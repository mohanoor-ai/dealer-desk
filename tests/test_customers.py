from urllib.parse import parse_qs
from uuid import uuid4
from datetime import timedelta
from sqlalchemy import select
from backend.models import CustomerAccount,CustomerToken,CustomerSession,now
from conftest import sign_in

PASSWORD='fictional-customer-password'

def register(client,email='alex@example.com'):
    result=client.post('/api/customer/register',json={'name':'Alex Morgan','email':email,'password':PASSWORD})
    assert result.status_code==201,result.text
    assert 'No email has been sent' in result.json()['message']
    return parse_qs(result.json()['local_email_url'].split('?')[1])['token'][0]

def verify_login(client,email='alex@example.com'):
    token=register(client,email)
    assert client.post('/api/customer/login',json={'email':email,'password':PASSWORD}).status_code==403
    assert client.post('/api/customer/verify',json={'token':token}).status_code==200
    assert client.post('/api/customer/verify',json={'token':token}).status_code==400
    response=client.post('/api/customer/login',json={'email':email,'password':PASSWORD})
    assert response.status_code==200,response.text
    assert 'HttpOnly' in response.headers['set-cookie']
    return response

def guest(client,email='alex@example.com'):
    response=client.post('/api/catalogue/enquiries',json={'vehicle_id':None,'source':'Website',
        'customer':'Alex','email':email,'phone':'','message':'Viewing request',
        'request_type':'Arrange a viewing','submission_key':str(uuid4())})
    assert response.status_code==201,response.text
    return response.json()['reference']

def test_verified_customer_claim_and_private_staff_customer_conversation(client):
    ident=guest(client)
    other=guest(client,'other@example.com')
    assert client.get('/api/customer/enquiries').status_code==401
    verify_login(client)
    items=client.get('/api/customer/enquiries').json()['items']
    assert [e['id'] for e in items]==[ident]
    assert all(field not in items[0] for field in ['activity','phone','email','submission_key','customer_account_id'])
    path=f'/api/customer/enquiries/{ident}/messages'
    assert client.get(f'/api/customer/enquiries/{other}/messages').status_code==404
    assert client.post(f'/api/customer/enquiries/{other}/messages',json={'body':'Denied'}).status_code==404
    assert client.post(path,json={'body':'Is Saturday morning possible?'}).status_code==201
    assert client.get('/api/enquiries').status_code==401
    sign_in(client,'sales')
    assert client.post(f'/api/enquiries/{ident}/contact',json={'revision':2,'outcome':'Internal scheduling check'}).status_code==200
    assert client.post(f'/api/enquiries/{ident}/messages',json={'body':'We will confirm a time here.'}).status_code==201
    messages=client.get(path).json()['items']
    assert [m['author_role'] for m in messages]==['customer','staff']
    assert 'Internal scheduling check' not in str(messages)
    assert client.get(f'/api/enquiries/{ident}').json()['status']=='contacted'
    assert client.post(path,json={'body':'Thank you, please confirm.'}).status_code==201
    assert client.get(f'/api/enquiries/{ident}').json()['status']=='new'
    assert client.get(f'/api/enquiries/{ident}').json()['customer_linked'] is True

def test_verification_tokens_expire_and_credentials_are_hashed(client,app):
    raw=register(client)
    with app.state.sessions() as db:
        account=db.scalar(select(CustomerAccount))
        assert account.password_hash!=PASSWORD and account.password_hash.startswith('scrypt$')
        token=db.scalar(select(CustomerToken))
        assert token.token_hash!=raw
        token.expires_at=now()-timedelta(seconds=1);db.commit()
    assert client.post('/api/customer/verify',json={'token':raw}).status_code==400
    assert client.get('/api/customer/enquiries').status_code==401
    assert client.post('/api/customer/register',json={'name':'Alex','email':'ALEX@example.com','password':PASSWORD}).status_code==409

def test_recovery_revokes_existing_sessions_and_token_is_single_use(client):
    verify_login(client)
    assert client.get('/api/customer/me').status_code==200
    response=client.post('/api/customer/recovery',json={'email':'alex@example.com'}).json()
    raw=parse_qs(response['local_email_url'].split('?')[1])['token'][0]
    assert client.post('/api/customer/reset',json={'token':raw,'password':'new-fictional-password','purpose':'reset'}).status_code==200
    assert client.get('/api/customer/me').status_code==401
    assert client.post('/api/customer/reset',json={'token':raw,'password':'another-test-password'}).status_code==400
    assert client.post('/api/customer/login',json={'email':'alex@example.com','password':PASSWORD}).status_code==401
    assert client.post('/api/customer/login',json={'email':'alex@example.com','password':'new-fictional-password'}).status_code==200
    client.post('/api/customer/logout')
    assert client.get('/api/customer/me').status_code==401

def test_customer_staff_boundaries_and_local_only_registration(client,monkeypatch):
    assert client.post('/api/customer/register',json={'email':'bad','name':'Alex','password':PASSWORD}).status_code==422
    assert client.post('/api/customer/register',json={'email':'alex@example.com','name':'Alex','password':PASSWORD,'role':'manager'}).status_code==422
    ident=guest(client)
    verify_login(client)
    assert client.post(f'/api/enquiries/{ident}/messages',json={'body':'Cannot impersonate staff'}).status_code==401
    assert client.post(f'/api/customer/enquiries/{ident}/messages',json={'body':' '}).status_code==422
    assert client.post(f'/api/customer/enquiries/{ident}/messages',json={'body':'Hello'},headers={'Sec-Fetch-Site':'cross-site'}).status_code==403
    sign_in(client,'viewer')
    assert client.post(f'/api/enquiries/{ident}/messages',json={'body':'No viewer edits'}).status_code==403
    monkeypatch.setenv('APP_ENV','production')
    assert client.post('/api/customer/register',json={'email':'new@example.com','name':'New','password':PASSWORD}).status_code==403
    assert client.post('/api/customer/recovery',json={'email':'alex@example.com'}).status_code==403
