from uuid import uuid4
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app import create_app, dealer_today
from backend.models import Enquiry, Task
from conftest import sign_in


def public_fields(vehicle_id=None):
    return {'vehicle_id':vehicle_id,'customer':'Alex Morgan','email':'alex@example.com',
            'phone':'','message':'Can I view the car on Saturday?',
            'request_type':'Arrange a viewing','source':'Website','submission_key':str(uuid4())}


def test_saved_website_to_staff_pipeline_and_restart(client,app):
    sign_in(client)
    car=client.post('/api/vehicles',json={'make':'Ford','model':'Puma (sample)','year':2026,'price_pence':2714500}).json()
    client.post('/api/auth/logout')
    fields=public_fields(car['id'])
    result=client.post('/api/catalogue/enquiries',json=fields)
    assert result.status_code==201,result.text
    receipt=result.json()
    assert set(receipt)=={'reference'}
    assert client.post('/api/catalogue/enquiries',json=fields).json()==receipt
    assert client.post('/api/catalogue/enquiries',json={**fields,'message':'Changed request'}).status_code==409
    assert client.get('/api/enquiries').status_code==401
    assert 'Alex' not in str(client.get('/api/catalogue').json())
    sign_in(client,'sales')
    path=f"/api/enquiries/{receipt['reference']}"
    saved=client.get(path).json()
    assert saved['source']=='Website' and saved['status']=='new'
    assert 'submission_key' not in saved
    assert saved['activity'][0]['actor']=='Customer website'
    reply={'revision':1,'subject':'Saturday viewing','body':'I will confirm the available time.','confirmed':True,
           'follow_up':{'due_date':dealer_today().isoformat(),'note':'Confirm Saturday viewing time'}}
    assert client.post(path+'/reply',json={**reply,'confirmed':False}).status_code==422
    result=client.post(path+'/reply',json=reply)
    assert result.status_code==200,result.text
    contacted=result.json()
    assert contacted['status']=='contacted'
    assert contacted['activity'][1]['actor']=='sales'
    assert contacted['activity'][1]['kind']=='Email marked as sent'
    assert client.post(path+'/reply',json=reply).status_code==409
    assert client.get('/api/tasks').json()['total']==1
    assert client.post(path+'/close',json={'revision':2,'outcome':'Agreed'}).status_code==409
    task=client.get('/api/tasks').json()['items'][0]
    client.patch(f"/api/tasks/{task['id']}",json={'revision':1,'completed':True})
    assert client.get(path).json()['status']=='contacted'
    assert client.post(path+'/close',json={'revision':2,'outcome':'Viewing agreed; no further action'}).status_code==200
    restarted=create_app(app.state.engine.url.render_as_string(hide_password=False))
    with TestClient(restarted,headers={'X-Requested-With':'DealerDesk'}) as second:
        sign_in(second)
        row=second.get(path).json()
        assert row['status']=='closed' and row['closure_reason']=='Viewing agreed; no further action'
        assert len(row['activity'])==3


def test_manual_source_and_optional_follow_up_are_atomic(signed_client):
    client=signed_client
    fields={k:v for k,v in public_fields().items() if k!='submission_key'}
    fields.update(source='Phone',request_type='Request a callback',email='',phone='020 0000 0000',
                  follow_up={'due_date':(dealer_today()-timedelta(days=1)).isoformat(),'note':'Call Alex'})
    assert client.post('/api/enquiries',json=fields).status_code==422
    assert client.get('/api/enquiries').json()['total']==0
    fields['follow_up']['due_date']=dealer_today().isoformat()
    result=client.post('/api/enquiries',json=fields)
    assert result.status_code==201,result.text
    enquiry=result.json()
    assert enquiry['source']=='Phone' and enquiry['vehicle_id'] is None
    assert client.get('/api/tasks').json()['total']==1
    response=client.post(f"/api/enquiries/{enquiry['id']}/contact",json={'revision':1,'outcome':'Called; customer will confirm a time'})
    assert response.status_code==200,response.text
    assert response.json()['status']=='contacted'
    assert response.json()['activity'][1]['kind']=='Contact recorded'


def test_public_boundaries_validation_and_limits(client,app,monkeypatch):
    fields=public_fields()
    for extra in [{'source':'Phone'},{'email':'bad'},{'email':'a@example.com\r\nBcc:b@example.com'},
                  {'request_type':'Unknown'},{'request_type':'Request a callback'},
                  {'customer':' '},{'vehicle_id':999},
                  {'follow_up':{'due_date':dealer_today().isoformat(),'note':'Injected'}}]:
        assert client.post('/api/catalogue/enquiries',json={**fields,**extra}).status_code in (404,422)
    assert client.post('/api/catalogue/enquiries',json=fields,headers={'Sec-Fetch-Site':'cross-site'}).status_code==403
    sign_in(client)
    hidden=client.post('/api/vehicles',json={'make':'Private','model':'Operational','year':2026,'price_pence':1}).json()
    assert client.post('/api/catalogue/enquiries',json={**fields,'vehicle_id':hidden['id']}).status_code==404
    sign_in(client,'viewer')
    assert client.post('/api/enquiries',json={k:v for k,v in fields.items() if k!='submission_key'}).status_code==403
    assert client.post('/api/enquiries/1/reply',json={'revision':1,'subject':'Hi','body':'Reply','confirmed':True}).status_code==403
    assert client.post('/api/enquiries/1/contact',json={'revision':1,'outcome':'Call'}).status_code==403
    assert client.post('/api/enquiries/1/close',json={'revision':1,'outcome':'Done'}).status_code==403
    monkeypatch.setenv('APP_ENV','production')
    assert client.post('/api/catalogue/enquiries',json=fields).status_code==403


def test_public_limiter_is_bounded_and_general_enquiries_persist(client):
    responses=[client.post('/api/catalogue/enquiries',json=public_fields()).status_code for _ in range(31)]
    assert responses[:30]==[201]*30 and responses[30]==429


def test_reply_follow_up_validation_does_not_save_partial_action(signed_client):
    client=signed_client
    fields={k:v for k,v in public_fields().items() if k!='submission_key'}
    fields['source']='Email'
    enquiry=client.post('/api/enquiries',json=fields).json()
    path=f"/api/enquiries/{enquiry['id']}"
    reply={'revision':1,'subject':'Hello','body':'Reply','confirmed':True,
           'follow_up':{'due_date':(dealer_today()-timedelta(days=1)).isoformat(),'note':'Call'}}
    assert client.post(path+'/reply',json=reply).status_code==422
    row=client.get(path).json()
    assert row['revision']==1 and row['status']=='new' and len(row['activity'])==1
    assert client.get('/api/tasks').json()['total']==0
    assert client.patch(path,json={'revision':1,'status':'closed'}).status_code==422


def test_competing_replies_cannot_create_duplicate_follow_ups(signed_client,app):
    from concurrent.futures import ThreadPoolExecutor
    fields={k:v for k,v in public_fields().items() if k!='submission_key'}
    row=signed_client.post('/api/enquiries',json=fields).json()
    token=signed_client.cookies.get('dealer_session')
    def respond(number):
        with TestClient(app,headers={'X-Requested-With':'DealerDesk'}) as client:
            client.cookies.set('dealer_session',token)
            return client.post(f"/api/enquiries/{row['id']}/reply",json={
                'revision':1,'subject':'Viewing','body':f'Checked time {number}',
                'confirmed':True,'follow_up':{'note':'Confirm viewing','due_date':dealer_today().isoformat()}
            }).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(respond,[1,2]))==[200,409]
    assert signed_client.get('/api/tasks').json()['total']==1
    saved=signed_client.get(f"/api/enquiries/{row['id']}").json()
    assert saved['revision']==2 and len(saved['activity'])==2
