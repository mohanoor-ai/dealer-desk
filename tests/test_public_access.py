from uuid import uuid4
from fastapi.testclient import TestClient
from backend.app import create_app

def fields():
    return {'customer':'Public test','email':'public@example.com','message':'Availability?',
            'request_type':'Check availability','submission_key':str(uuid4())}

def test_hosted_switch_enables_enquiries_but_never_local_registration(client,monkeypatch):
    monkeypatch.setenv('APP_ENV','production')
    assert client.get('/api/catalogue/capabilities').json()=={'enquiries':False,'customer_registration':False}
    assert client.post('/api/catalogue/enquiries',json=fields()).status_code==403
    monkeypatch.setenv('PUBLIC_ENQUIRIES_ENABLED','true')
    assert client.get('/api/catalogue/capabilities').json()=={'enquiries':True,'customer_registration':False}
    assert client.post('/api/catalogue/enquiries',json=fields()).status_code==201
    assert client.post('/api/customer/register',json={'name':'Test','email':'public@example.com','password':'fictional-long-password'}).status_code==403
    assert client.post('/api/catalogue/enquiries',content='x'*8001).status_code==413

def test_public_budget_survives_application_restart_and_new_instances(client,app):
    for _ in range(30):assert client.post('/api/catalogue/enquiries',json=fields()).status_code==201
    restarted=create_app(app.state.engine.url.render_as_string(hide_password=False))
    with TestClient(restarted,headers={'X-Requested-With':'DealerDesk'}) as second:
        assert second.post('/api/catalogue/enquiries',json=fields()).status_code==429
