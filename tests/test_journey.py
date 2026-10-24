from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from backend.app import create_app, dealer_today
from conftest import sign_in

VEHICLE = {'make':'Fictional Motors','model':'City','year':2021,'price_pence':1250050}

def add_vehicle(client):
    result = client.post('/api/vehicles', json=VEHICLE)
    assert result.status_code == 201, result.text
    return result.json()

def test_complete_journey_survives_new_app(signed_client, app):
    client = signed_client
    vehicle = add_vehicle(client)
    response = client.post('/api/enquiries', json={'vehicle_id':vehicle['id'],'customer':'Demo Buyer','message':'Arrange a viewing'})
    assert response.status_code == 201, response.text
    enquiry = response.json()
    response = client.post('/api/tasks', json={'enquiry_id':enquiry['id'],'due_date':dealer_today().isoformat(),'note':'Call about viewing'})
    assert response.status_code == 201, response.text
    task = response.json()
    assert client.get('/api/dashboard').json()['open_tasks'] == 1
    assert client.patch(f"/api/tasks/{task['id']}", json={'revision':1,'completed':True}).status_code == 200
    assert client.get('/api/dashboard').json()['open_tasks'] == 0
    # A new engine/app proves data does not live in the old process's Python objects.
    restarted = create_app(app.state.engine.url.render_as_string(hide_password=False))
    with TestClient(restarted, headers={'X-Requested-With':'DealerDesk'}) as second:
        sign_in(second)
        assert second.get('/api/vehicles').json()['items'][0]['price_pence'] == 1250050
        assert second.get('/api/tasks').json()['items'][0]['completed'] is True
        history = second.get('/api/audit').json()['items']
        assert len(history) == 4
        assert all(row['actor_id'] is not None for row in history)
        assert 'Demo Buyer' not in str(history)

def test_atomic_competing_edits(signed_client, app):
    vehicle = add_vehicle(signed_client)
    token = signed_client.cookies.get('dealer_session')
    def edit(price):
        with TestClient(app, headers={'X-Requested-With':'DealerDesk'}) as other:
            other.cookies.set('dealer_session', token)
            return other.patch(f"/api/vehicles/{vehicle['id']}", json={'revision':1,'price_pence':price}).status_code
    with ThreadPoolExecutor(max_workers=2) as workers:
        outcomes = list(workers.map(edit, [100, 200]))
    assert sorted(outcomes) == [200,409]
    saved = signed_client.get(f"/api/vehicles/{vehicle['id']}").json()
    assert saved['revision'] == 2
    assert saved['price_pence'] in [100,200]
    assert len(signed_client.get('/api/audit').json()['items']) == 2

def test_validation_and_workflow_guards(signed_client):
    client = signed_client
    for fields in [{'make':'  '},{'price_pence':-1},{'price_pence':2.5},{'year':True},{'unexpected':'x'}]:
        assert client.post('/api/vehicles', json={**VEHICLE,**fields}).status_code == 422
    vehicle = add_vehicle(client)
    path = f"/api/vehicles/{vehicle['id']}"
    assert client.patch(path, json={'revision':1}).status_code == 422
    assert client.patch(path, json={'revision':1,'make':None}).status_code == 422
    assert client.patch(path, json={'revision':1,'status':'sold'}).status_code == 200
    assert client.patch(path, json={'revision':2,'status':'reserved'}).status_code == 409
    assert client.patch(path, json={'revision':2,'archived':True}).status_code == 200
    assert client.get('/api/vehicles').json()['total'] == 0
    assert client.get('/api/vehicles?include_archived=true').json()['total'] == 1
    assert client.post('/api/enquiries', json={'vehicle_id':vehicle['id'],'customer':'Demo','message':'Hello'}).status_code == 409

def test_closed_enquiry_and_date_rules(signed_client):
    client = signed_client
    vehicle = add_vehicle(client)
    enquiry = client.post('/api/enquiries', json={'vehicle_id':vehicle['id'],'customer':'Demo','message':'Hello'}).json()
    fields = {'enquiry_id':enquiry['id'],'due_date':(dealer_today()-timedelta(days=1)).isoformat()}
    assert client.post('/api/tasks', json=fields).status_code == 422
    assert client.post('/api/tasks', json={**fields,'due_date':'not-a-date'}).status_code == 422
    assert client.patch(f"/api/enquiries/{enquiry['id']}", json={'revision':1,'status':'closed'}).status_code == 200
    assert client.post('/api/tasks', json={**fields,'due_date':dealer_today().isoformat()}).status_code == 409
    assert client.get('/api/dashboard').json()['open_enquiries'] == 0

def test_search_pagination_and_change_feed(signed_client):
    client = signed_client
    add_vehicle(client)
    client.post('/api/vehicles', json={**VEHICLE,'model':'100% electric'})
    assert client.get('/api/vehicles?q=%25').json()['total'] == 1
    assert client.get('/api/vehicles?q=FICTIONAL&limit=1').json()['total'] == 2
    assert len(client.get('/api/vehicles?offset=1&limit=1').json()['items']) == 1
    assert client.get('/api/vehicles?limit=101').status_code == 422
    feed = client.get('/api/changes?limit=1').json()
    assert feed['has_more'] is True
    assert client.get(f"/api/changes?after={feed['next_sequence']}").json()['items'][0]['sequence'] == 2

def test_sales_role_and_missing_records(client):
    sign_in(client,'sales')
    add_vehicle(client)
    assert client.get('/api/audit').status_code == 403
    assert client.get('/api/vehicles/99999').status_code == 404
