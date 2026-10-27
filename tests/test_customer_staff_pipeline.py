"""Current unverified-account journey, isolated by the shared DB fixture."""
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app import dealer_today
from conftest import sign_in

PASSWORD='fictional-pipeline-password'


def test_complete_customer_staff_pipeline_and_denials(app,client,monkeypatch):
    monkeypatch.setenv('CUSTOMER_REGISTRATION_UNVERIFIED','true')
    sign_in(client)
    car=client.post('/api/vehicles',json={'make':'Ford','model':'Puma (sample)','year':2026,'price_pence':2714500}).json()
    client.post('/api/auth/logout')
    fields={'vehicle_id':car['id'],'customer':'Alex Morgan','email':'alex@example.com',
            'message':'Can I view this car on Saturday?','request_type':'Arrange a viewing',
            'submission_key':str(uuid4()),'promotions_opt_in':True}
    earlier=client.post('/api/catalogue/enquiries',json=fields).json()['reference']
    assert client.post('/api/customer/register',json={'name':'Alex Morgan','email':fields['email'],'password':PASSWORD}).status_code==201
    assert client.post('/api/customer/login',json={'email':fields['email'],'password':PASSWORD}).status_code==200
    assert client.get('/api/customer/enquiries').json()['items']==[]
    response=client.post('/api/catalogue/enquiries',json={**fields,'submission_key':str(uuid4())})
    assert response.status_code==201
    ident=response.json()['reference'];path=f'/api/enquiries/{ident}'
    messages=f'/api/customer/enquiries/{ident}/messages'
    assert client.get(f'/api/customer/enquiries/{earlier}/messages').status_code==404
    assert client.get('/api/leads').status_code==401
    with TestClient(app,headers={'X-Requested-With':'DealerDesk'}) as other:
        assert other.post('/api/customer/register',json={'name':'Casey Taylor','email':'casey@example.com','password':PASSWORD}).status_code==201
        assert other.post('/api/customer/login',json={'email':'casey@example.com','password':PASSWORD}).status_code==200
        assert other.get(messages).status_code==404
        assert other.post(messages,json={'body':'Cannot read or add to this enquiry'}).status_code==404
    sign_in(client,'viewer')
    assert client.post(path+'/messages',json={'body':'Viewer must not reply'}).status_code==403
    assert client.post('/api/tasks',json={'enquiry_id':ident,'due_date':dealer_today().isoformat(),'note':'Denied'}).status_code==403
    assert client.post(path+'/close',json={'revision':1,'outcome':'Denied'}).status_code==403
    sign_in(client,'sales')
    assert client.post(path+'/contact',json={'revision':1,'outcome':'INTERNAL: check diary before confirming'}).status_code==200
    assert client.post(path+'/messages',json={'body':'Saturday morning is available.'}).status_code==201
    assert client.get(path).json()['status']=='contacted'
    assert client.post(messages,json={'body':'Please book 10 am.'}).status_code==201
    enquiry=client.get(path).json();assert enquiry['status']=='new'
    task=client.post('/api/tasks',json={'enquiry_id':ident,'due_date':dealer_today().isoformat(),'note':'INTERNAL: reserve viewing slot'}).json()
    assert client.post(path+'/close',json={'revision':enquiry['revision'],'outcome':'Too early'}).status_code==409
    assert client.patch(f"/api/tasks/{task['id']}",json={'revision':task['revision'],'completed':True}).status_code==200
    enquiry=client.get(path).json()
    assert client.post(path+'/close',json={'revision':enquiry['revision'],'outcome':'Viewing confirmed; follow-up completed'}).status_code==200
    public=client.get('/api/catalogue').json();assert 'alex@example.com' not in str(public)
    assert client.get('/api/leads').json()['items'][0]['promotions'] is True
    client.post('/api/auth/logout')
    owned=client.get('/api/customer/enquiries').json()['items'];assert [e['id'] for e in owned]==[ident] and owned[0]['status']=='closed'
    assert 'INTERNAL:' not in str(owned)+str(client.get(messages).json())
    assert [m['author_role'] for m in client.get(messages).json()['items']]==['staff','customer']
    assert client.get('/api/leads').status_code==401
