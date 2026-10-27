"""Enquiry leads and recorded preferences, without a campaign delivery service."""
from fastapi import Depends,HTTPException,Query
from sqlalchemy import select,func,String,cast
from backend import schemas as s
from backend.models import Enquiry,MarketingPreference,now
from backend.public_access import enquiries_enabled,public_budget

CONSENT_VERSION='email-offers-v1'
CONSENT_TEXT='Email me Dealer Desk vehicle updates and offers. Optional; unsubscribe at any time.'

class Unsubscribe(s.Input):
    email:str
    @s.field_validator('email')
    @classmethod
    def valid_email(cls,value):
        if not value or len(value)>254:raise ValueError('Enter an email address.')
        return s.EnquiryCreate.valid_email(value.strip().lower())

def record_opt_in(db,enquiry):
    if not enquiry.promotions_opt_in:return
    email=enquiry.email.strip().lower()
    pref=db.get(MarketingPreference,email)
    if pref is None:
        pref=MarketingPreference(email=email,opted_in=False,history=[]);db.add(pref)
    timestamp=now();pref.opted_in=True;pref.consent_at=timestamp;pref.withdrawn_at=None
    pref.history=(pref.history+[{ 'action':'opt_in','at':timestamp.isoformat(),'source':'Website enquiry',
        'enquiry_id':enquiry.id,'version':CONSENT_VERSION,'text':CONSENT_TEXT}])[-100:]

def withdraw(db,email,source):
    pref=db.get(MarketingPreference,email)
    if pref and pref.opted_in:
        pref.opted_in=False;pref.withdrawn_at=now()
        pref.history=(pref.history+[{'action':'withdraw','at':pref.withdrawn_at.isoformat(),'source':source}])[-100:]
    db.commit()

def register_leads(app,database,signed_in,can_write):
    @app.get('/api/leads')
    def leads(offset:int=Query(0,ge=0),limit:int=Query(25,ge=1,le=100),user=Depends(signed_in),db=Depends(database)):
        # SQLite's portable concatenation is rendered by SQLAlchemy's string operator.
        key=func.coalesce(func.nullif(func.lower(Enquiry.email),''),'enquiry-'+cast(Enquiry.id,String))
        grouped=select(func.max(Enquiry.id).label('latest'),func.count().label('count')).group_by(key).subquery()
        total=db.scalar(select(func.count()).select_from(grouped))
        rows=db.execute(select(Enquiry,grouped.c.count).join(grouped,Enquiry.id==grouped.c.latest)
                        .order_by(Enquiry.id.desc()).offset(offset).limit(limit))
        items=[]
        for e,count in rows:
            pref=db.get(MarketingPreference,e.email.lower()) if e.email else None
            items.append({'id':e.id,'customer':e.customer,'email':e.email,'phone':e.phone,'source':e.source,
                'request_type':e.request_type,'interest':e.message,'status':e.status,'vehicle_id':e.vehicle_id,
                'enquiry_count':count,'promotions':bool(pref and pref.opted_in),
                'consent_at':pref.consent_at if pref else None,'withdrawn_at':pref.withdrawn_at if pref else None,
                'consent_history':pref.history if pref else []})
        return {'items':items,'total':total,'offset':offset,'limit':limit}

    @app.post('/api/leads/unsubscribe',status_code=204)
    def staff_unsubscribe(body:Unsubscribe,user=Depends(can_write),db=Depends(database)):
        withdraw(db,body.email,'Staff recorded withdrawal')

    @app.post('/api/catalogue/promotions/unsubscribe')
    def public_unsubscribe(body:Unsubscribe,db=Depends(database)):
        if not enquiries_enabled():raise HTTPException(403,'Email preferences are not enabled on this deployment.')
        public_budget(db,'unsubscribe',60)
        # Only revokes a preference; never reveals whether an address was subscribed.
        withdraw(db,body.email,'Self-service withdrawal')
        return {'message':'Email promotions have been stopped for this address if it was subscribed.'}
