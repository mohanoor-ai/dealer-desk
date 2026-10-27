"""Customer-owned conversations. Local verification previews never claim email delivery."""
from collections import deque
from datetime import datetime, timedelta, timezone
import secrets
from threading import Lock
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import Field, field_validator
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from backend import auth, schemas as s
from backend.config import hosted, secure_cookies
from backend.models import CustomerAccount,CustomerSession,CustomerToken,Enquiry,EnquiryMessage,AuditEvent,now

from backend.public_access import unverified_registration_enabled, public_budget

COOKIE='dealer_customer_session'

class Email(s.Input):
    email:str=Field(min_length=3,max_length=254)
    @field_validator('email')
    @classmethod
    def check_email(cls,value):
        return s.EnquiryCreate.valid_email(value.strip().lower())

class Credentials(Email):
    password:str=Field(min_length=12,max_length=128)
    model_config={'extra':'forbid','str_strip_whitespace':False}

class Registration(Credentials):
    name:str=Field(min_length=1,max_length=80)
    @field_validator('name')
    @classmethod
    def check_name(cls,value):
        if not value.strip():raise ValueError('Enter your name.')
        return value.strip()

class Token(s.Input):
    token:str=Field(min_length=30,max_length=100)
    purpose:Literal['verify','reset']='verify'

class Reset(Token):
    password:str=Field(min_length=12,max_length=128)
    purpose:Literal['reset']='reset'
    model_config={'extra':'forbid','str_strip_whitespace':False}

class Message(s.Input):
    follow_up:s.FollowUpPlan|None=None
    body:str=Field(min_length=1,max_length=2000)

def optional_customer(request,db):
    token=request.cookies.get(COOKIE,'')
    session=db.get(CustomerSession,auth.token_hash(token)) if token else None
    if not session or session.expires_at.replace(tzinfo=timezone.utc)<=now():return None
    customer=db.get(CustomerAccount,session.customer_id)
    return customer if customer and (customer.verified or unverified_registration_enabled()) else None

def claim_enquiries(db,customer):
    if not customer.verified:return
    db.execute(update(Enquiry).where(Enquiry.customer_account_id.is_(None),
        func.lower(Enquiry.email)==customer.email).values(customer_account_id=customer.id))

def register_customers(app,database,signed_in,can_write):
    router=APIRouter()
    attempts=deque()
    lock=Lock()
    dummy=auth.hash_password('unused-customer-dummy-password')

    def limited():
        current=time.monotonic()
        with lock:
            while attempts and attempts[0]<current-900:attempts.popleft()
            if len(attempts)>=40:raise HTTPException(429,'Too many attempts. Try again later.')
            attempts.append(current)

    def local_registration(request):
        if hosted() or request.url.hostname not in ('localhost','127.0.0.1','testserver'):
            raise HTTPException(403,'Customer registration requires a configured verification email service before hosting.')

    def customer(request:Request,db=Depends(database)):
        value=optional_customer(request,db)
        if value is None:raise HTTPException(401,'Sign in to your customer account.')
        return value

    def preview(db,row,purpose):
        raw=secrets.token_urlsafe(32)
        db.execute(delete(CustomerToken).where(CustomerToken.customer_id==row.id,CustomerToken.purpose==purpose))
        db.add(CustomerToken(token_hash=auth.token_hash(raw),customer_id=row.id,purpose=purpose,expires_at=now()+timedelta(minutes=30)))
        db.commit()
        return {'message':'Local verification email preview. No email has been sent.',
                'local_email_url':f'#/account?purpose={purpose}&token={raw}'}

    @router.post('/api/customer/register',status_code=201)
    def register(body:Registration,request:Request,db=Depends(database)):
        if unverified_registration_enabled():public_budget(db,'customer_registration',20)
        else:local_registration(request)
        limited()
        row=db.scalar(select(CustomerAccount).where(CustomerAccount.email==body.email))
        if row:
            raise HTTPException(409,'Use sign in or password recovery for this email address.')
        row=CustomerAccount(email=body.email,name=body.name,password_hash=auth.hash_password(body.password),verified=False)
        db.add(row)
        try:db.flush()
        except IntegrityError:
            db.rollback();raise HTTPException(409,'Use sign in or password recovery.') from None
        if unverified_registration_enabled():
            db.commit()
            return {'message':'Account created. Sign in to send and follow up new enquiries. Earlier guest enquiries are not linked to this account.'}
        return preview(db,row,'verify')

    @router.post('/api/customer/recovery')
    def recovery(body:Email,request:Request,db=Depends(database)):
        local_registration(request);limited()
        row=db.scalar(select(CustomerAccount).where(CustomerAccount.email==body.email))
        if row:return preview(db,row,'reset')
        return {'message':'If this account exists, recovery instructions are available.'}

    def consume(db,raw,purpose):
        hashed=auth.token_hash(raw)
        # DELETE ... RETURNING makes the token single-use under competing requests.
        ident=db.execute(delete(CustomerToken).where(CustomerToken.token_hash==hashed,
            CustomerToken.purpose==purpose,CustomerToken.expires_at>now()).returning(CustomerToken.customer_id)).scalar()
        if ident is None:raise HTTPException(400,'This link has expired or was already used.')
        return db.get(CustomerAccount,ident)

    @router.post('/api/customer/verify')
    def verify(body:Token,db=Depends(database)):
        if hosted():raise HTTPException(403,'Email verification is not configured.')
        if body.purpose!='verify':raise HTTPException(422,'Use a verification link.')
        row=consume(db,body.token,'verify');row.verified=True;claim_enquiries(db,row);db.commit()
        return {'message':'Account verified locally. You can now sign in.'}

    @router.post('/api/customer/reset')
    def reset(body:Reset,db=Depends(database)):
        if hosted():raise HTTPException(403,'Password recovery is not configured.')
        row=consume(db,body.token,'reset');row.password_hash=auth.hash_password(body.password);row.verified=True;claim_enquiries(db,row)
        db.execute(delete(CustomerToken).where(CustomerToken.customer_id==row.id))
        db.execute(delete(CustomerSession).where(CustomerSession.customer_id==row.id));db.commit()
        return {'message':'Password changed. Sign in again.'}

    @router.post('/api/customer/login')
    def login(body:Credentials,response:Response,db=Depends(database)):
        public_budget(db,'customer_login',40)
        limited();row=db.scalar(select(CustomerAccount).where(CustomerAccount.email==body.email))
        valid=auth.verify_password(body.password,row.password_hash if row else dummy)
        if not row or not valid:raise HTTPException(401,'Email or password is incorrect.')
        if not row.verified and not unverified_registration_enabled():raise HTTPException(403,'Verify your account before signing in; use account recovery if the link expired.')
        raw=secrets.token_urlsafe(32)
        db.add(CustomerSession(token_hash=auth.token_hash(raw),customer_id=row.id,expires_at=now()+timedelta(hours=8)))
        claim_enquiries(db,row);db.commit()
        response.set_cookie(COOKIE,raw,max_age=8*3600,httponly=True,secure=secure_cookies(),samesite='lax')
        return {'name':row.name,'email':row.email}

    @router.get('/api/customer/me')
    def me(row=Depends(customer)):
        return {'name':row.name,'email':row.email}

    @router.post('/api/customer/logout',status_code=204)
    def logout(request:Request,response:Response,db=Depends(database)):
        db.execute(delete(CustomerSession).where(CustomerSession.token_hash==auth.token_hash(request.cookies.get(COOKIE,''))))
        db.commit();response.delete_cookie(COOKIE)

    @router.get('/api/customer/enquiries')
    def enquiries(row=Depends(customer),db=Depends(database)):
        claim_enquiries(db,row);db.commit()
        records=db.scalars(select(Enquiry).where(Enquiry.customer_account_id==row.id).order_by(Enquiry.id.desc()).limit(100))
        return {'items':[{'id':e.id,'vehicle_id':e.vehicle_id,'message':e.message,'status':e.status,
                         'request_type':e.request_type,'created_at':e.created_at,'revision':e.revision} for e in records]}

    def owned(db,ident,row):
        e=db.get(Enquiry,ident)
        if not e or e.customer_account_id!=row.id:raise HTTPException(404,'Enquiry not found.')
        return e

    def messages(db,ident):
        values=list(db.scalars(select(EnquiryMessage).where(EnquiryMessage.enquiry_id==ident).order_by(EnquiryMessage.id.desc()).limit(100)))
        return {'items':[{'id':m.id,'author_role':m.author_role,'body':m.body,'created_at':m.created_at} for m in reversed(values)]}

    def add_message(db,ident,body,role,actor=None):
        db.execute(update(Enquiry).where(Enquiry.id==ident).values(updated_at=Enquiry.updated_at));db.expire_all()
        e=db.get(Enquiry,ident)
        if db.scalar(select(func.count()).select_from(EnquiryMessage).where(EnquiryMessage.enquiry_id==ident))>=100:
            raise HTTPException(409,'Conversation limit reached.')
        if role=='staff' and e.customer_account_id is None:raise HTTPException(409,'Customer must verify and link this enquiry first.')
        if body.follow_up is not None:
            if role!='staff':raise HTTPException(403,'Only staff can schedule follow-ups.')
            from backend.enquiry_workflow import plan_task
            from backend.app import dealer_today
            plan_task(db,e,body.follow_up,actor,dealer_today())
        db.add(EnquiryMessage(enquiry_id=ident,author_role=role,body=body.body))
        e.status='new' if role=='customer' else 'contacted';e.closure_reason='';e.revision+=1;e.updated_at=now()
        db.add(AuditEvent(entity='enquiry',entity_id=e.id,revision=e.revision,action='message_added',actor_id=actor.id if actor else None))
        db.commit();return messages(db,ident)

    @router.get('/api/customer/enquiries/{ident}/messages')
    def customer_messages(ident:int,row=Depends(customer),db=Depends(database)):
        owned(db,ident,row);return messages(db,ident)

    @router.post('/api/customer/enquiries/{ident}/messages',status_code=201)
    def customer_message(ident:int,body:Message,row=Depends(customer),db=Depends(database)):
        owned(db,ident,row);return add_message(db,ident,body,'customer')

    @router.get('/api/enquiries/{ident}/messages')
    def staff_messages(ident:int,user=Depends(signed_in),db=Depends(database)):
        if db.get(Enquiry,ident) is None:raise HTTPException(404,'Enquiry not found.')
        return messages(db,ident)

    @router.post('/api/enquiries/{ident}/messages',status_code=201)
    def staff_message(ident:int,body:Message,user=Depends(can_write),db=Depends(database)):
        if db.get(Enquiry,ident) is None:raise HTTPException(404,'Enquiry not found.')
        return add_message(db,ident,body,'staff',user)

    app.include_router(router)
