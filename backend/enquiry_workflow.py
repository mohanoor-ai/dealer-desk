"""Saved enquiry workflow; email actions record staff confirmation, not delivery."""
from collections import deque
from threading import Lock
import json
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from backend import schemas as s
from backend.config import hosted
from backend.models import Enquiry, Vehicle, Task, AuditEvent, now


def event(kind, actor, **details):
    return {'kind':kind,'actor':actor,'at':now().isoformat(),**details}


def plan_task(db, enquiry, plan, actor, today):
    if plan is None:
        return
    if plan.due_date < today:
        raise HTTPException(422,'Choose today or a future date.')
    task = Task(enquiry_id=enquiry.id,**plan.model_dump())
    db.add(task)
    db.flush()
    db.add(AuditEvent(entity='task',entity_id=task.id,revision=task.revision,
                      action='created',actor_id=actor.id))


def create_enquiry(db, body, actor, today, public=False,customer=None):
    if body.vehicle_id is not None:
        vehicle = db.get(Vehicle,body.vehicle_id)
        if vehicle is None:
            raise HTTPException(404,'Vehicle not found.')
        if vehicle.archived:
            raise HTTPException(409,'Restore this vehicle before recording an enquiry.')
        if public and (not vehicle.model.endswith('(sample)') or vehicle.make in ('Deployment','Demo Motors')):
            raise HTTPException(404,'Vehicle not found.')
    if body.promotions_opt_in and not public:
        raise HTTPException(403,'Promotions consent must be given by the customer.')
    fields = body.model_dump(exclude={'follow_up'})
    fields['activity'] = [event('Enquiry received','Customer website' if public else actor.username)]
    if customer:fields['customer_account_id']=customer.id
    record = Enquiry(**fields)
    db.add(record)
    db.flush()
    db.add(AuditEvent(entity='enquiry',entity_id=record.id,revision=record.revision,
                      action='created',actor_id=None if public else actor.id))
    from backend.leads import record_opt_in
    record_opt_in(db,record)
    plan_task(db,record,body.follow_up,actor,today)
    db.commit()
    return record


def register_workflow(app, database, can_write, today, serialize):
    router = APIRouter()
    submissions = deque()
    lock = Lock()

    @router.post('/api/catalogue/enquiries',status_code=201,response_model=s.EnquiryReceipt)
    def website_enquiry(body:s.PublicEnquiry,request:Request,db=Depends(database)):
        # This locally reviewed write path is not enabled for hosted deployments.
        # Shared abuse controls and release approval are needed before hosting it.
        if hosted():
            raise HTTPException(403,'Website enquiries are not enabled on this deployment.')
        if len(json.dumps(body.model_dump(mode='json'))) > 6000:
            raise HTTPException(413,'Enquiry is too large.')
        current = time.monotonic()
        with lock:
            while submissions and submissions[0] < current-900:
                submissions.popleft()
            if len(submissions) >= 30:
                raise HTTPException(429,'Too many enquiries. Try again later.')
            submissions.append(current)
        existing = db.scalar(select(Enquiry).where(Enquiry.submission_key==body.submission_key))
        if existing:
            fields=body.model_dump(exclude={'follow_up','submission_key'})
            if any(getattr(existing,k)!=v for k,v in fields.items()):
                raise HTTPException(409,'This submission has already been used. Start a new enquiry.')
            return {'reference':existing.id}
        try:
            from backend.customer_portal import optional_customer
            account=optional_customer(request,db)
            if account and body.email.lower()!=account.email:
                raise HTTPException(422,'Use the email address of your signed-in account.')
            row=create_enquiry(db,body,None,today(),public=True,customer=account)
        except IntegrityError:
            db.rollback()
            raise HTTPException(409,'Submission already saved. Check before trying again.') from None
        return {'reference':row.id}

    def apply_action(db, enquiry_id, body, user, kind):
        # Serialize closure/replies with task creation or reopening.
        db.execute(update(Enquiry).where(Enquiry.id==enquiry_id).values(updated_at=Enquiry.updated_at))
        db.expire_all()
        row=db.get(Enquiry,enquiry_id)
        if row is None:
            raise HTTPException(404,'Enquiry not found.')
        if row.status=='closed':
            raise HTTPException(409,'This enquiry is closed.')
        if len(row.activity)>=100:
            raise HTTPException(409,'Activity limit reached for this enquiry.')
        if kind=='reply':
            if not row.email:
                raise HTTPException(422,'No email address recorded.')
            details=event('Email marked as sent',user.username,subject=body.subject,body=body.body)
            status='contacted'
        elif kind=='contact':
            details=event('Contact recorded',user.username,outcome=body.outcome)
            status='contacted'
        else:
            if db.scalar(select(Task.id).where(Task.enquiry_id==row.id,Task.completed.is_(False)).limit(1)):
                raise HTTPException(409,'Complete pending follow-ups before closing this enquiry.')
            details=event('Enquiry closed',user.username,outcome=body.outcome)
            status='closed'
        values={'status':status,'activity':row.activity+[details],
                'revision':body.revision+1,'updated_at':now()}
        if kind=='close':
            values['closure_reason']=body.outcome
        result=db.execute(update(Enquiry).where(Enquiry.id==row.id,Enquiry.revision==body.revision)
                          .values(**values).execution_options(synchronize_session=False))
        if result.rowcount!=1:
            db.rollback()
            raise HTTPException(409,'Record changed. Refresh before recording the action.')
        plan_task(db,row,body.follow_up,user,today())
        db.add(AuditEvent(entity='enquiry',entity_id=row.id,revision=body.revision+1,
                          action=kind+'_recorded',actor_id=user.id))
        db.commit()
        db.expire_all()
        return serialize(db.get(Enquiry,enquiry_id))

    @router.post('/api/enquiries/{enquiry_id}/reply',response_model=s.EnquiryOutput)
    def reply(enquiry_id:int,body:s.ReplyConfirmation,user=Depends(can_write),db=Depends(database)):
        return apply_action(db,enquiry_id,body,user,'reply')

    @router.post('/api/enquiries/{enquiry_id}/contact',response_model=s.EnquiryOutput)
    def contact(enquiry_id:int,body:s.ContactOutcome,user=Depends(can_write),db=Depends(database)):
        return apply_action(db,enquiry_id,body,user,'contact')

    @router.post('/api/enquiries/{enquiry_id}/close',response_model=s.EnquiryOutput)
    def close(enquiry_id:int,body:s.ContactOutcome,user=Depends(can_write),db=Depends(database)):
        if body.follow_up is not None:
            raise HTTPException(422,'A closed enquiry cannot have a new follow-up.')
        return apply_action(db,enquiry_id,body,user,'close')

    app.include_router(router)
