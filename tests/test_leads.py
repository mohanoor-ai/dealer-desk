from uuid import uuid4
from sqlalchemy import select
from backend.models import MarketingPreference
from conftest import sign_in

def enquiry(client,opt_in=False,email='alex@example.com'):
    return client.post('/api/catalogue/enquiries',json={'vehicle_id':None,'customer':'Alex',
        'email':email,'phone':'','message':'Looking for an SUV','request_type':'Other','source':'Website',
        'submission_key':str(uuid4()),'promotions_opt_in':opt_in})

def test_optional_choice_and_deduplicated_leads(client,app):
    assert enquiry(client).status_code==201
    assert client.get('/api/leads').status_code==401
    sign_in(client)
    lead=client.get('/api/leads').json()['items'][0]
    assert lead['promotions'] is False and lead['consent_at'] is None
    response=enquiry(client,True)
    assert response.status_code==201,response.text
    leads=client.get('/api/leads').json()
    assert leads['total']==1 and leads['items'][0]['enquiry_count']==2
    lead=leads['items'][0]
    assert lead['promotions'] is True and lead['consent_history'][0]['version']=='email-offers-v1'
    assert lead['consent_history'][0]['enquiry_id']==response.json()['reference']
    assert 'unsubscribe' in lead['consent_history'][0]['text']
    assert enquiry(client,False).status_code==201
    assert client.get('/api/leads').json()['items'][0]['promotions'] is True
    assert client.post('/api/leads/unsubscribe',json={'email':'alex@example.com'}).status_code==204
    assert client.get('/api/leads').json()['items'][0]['promotions'] is False
    with app.state.sessions() as db:
        pref=db.get(MarketingPreference,'alex@example.com')
        assert pref.withdrawn_at and len(pref.history)==2
    assert 'alex@example.com' not in str(client.get('/api/catalogue').json())

def test_unsubscribe_does_not_reveal_subscription_or_change_enquiry(client):
    result=enquiry(client,True)
    one=client.post('/api/catalogue/promotions/unsubscribe',json={'email':'alex@example.com'})
    two=client.post('/api/catalogue/promotions/unsubscribe',json={'email':'unknown@example.com'})
    assert one.status_code==two.status_code==200 and one.json()==two.json()
    sign_in(client)
    assert client.get(f"/api/enquiries/{result.json()['reference']}").json()['status']=='new'
    assert client.get('/api/leads').json()['items'][0]['promotions'] is False

def test_validation_and_permissions(client):
    for values in [{'email':''},{'customer':' '},{'message':' '},{'request_type':'Request a callback','phone':''}]:
        fields={'customer':'Alex','email':'alex@example.com','message':'Hello','submission_key':str(uuid4()),**values}
        assert client.post('/api/catalogue/enquiries',json=fields).status_code==422
    assert client.post('/api/catalogue/enquiries',json={'customer':'Alex','email':'alex@example.com','message':'Hello','submission_key':str(uuid4())}).status_code==422
    fields={'customer':'Alex','email':'alex@example.com','message':'Hello','request_type':'Other','submission_key':str(uuid4()),'promotions_opt_in':'yes'}
    assert client.post('/api/catalogue/enquiries',json=fields).status_code==422
    sign_in(client,'viewer')
    assert client.get('/api/leads').status_code==200
    assert client.post('/api/leads/unsubscribe',json={'email':'alex@example.com'}).status_code==403
    sign_in(client,'sales')
    assert client.post('/api/enquiries',json={'customer':'Alex','email':'alex@example.com','message':'Hello','promotions_opt_in':True}).status_code==403
