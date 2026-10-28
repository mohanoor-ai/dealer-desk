"""Synthetic API journey for disposable CI containers only. Never use on hosted data."""
import argparse
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import hashlib
from sqlalchemy import text
from uuid import uuid4
from backend.auth import create_user, issue_session
from backend.database import build_engine, session_factory

STATE = Path('/tmp/dealer-ci-journey.json')
BASE_URL = 'http://127.0.0.1:8090'


class Client:
    def __init__(self, token, cookie="dealer_session"):
        self.token = token
        self.cookie = cookie

    def send(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {'X-Requested-With': 'DealerDesk', 'Cookie': self.cookie+'='+self.token,
                   'Content-Type': 'application/json'}
        with urlopen(Request(BASE_URL+path, data=data, headers=headers, method=method), timeout=5) as response:
            data=response.read()
            return json.loads(data) if data else None




def rehearsal_engine():
    engine=build_engine()
    url=engine.url
    allowed=(url.get_backend_name()=='postgresql' and url.host=='database' and url.database=='dealer') or (
        url.get_backend_name()=='sqlite' and Path(url.database or '').name=='journey.sqlite3')
    if not allowed:
        engine.dispose()
        raise SystemExit('Only the disposable Compose database or isolated journey.sqlite3 fixture is permitted.')
    return engine


def new_data_fingerprint():
    """Read only: permits checking newer records while the prior API runs."""
    engine=rehearsal_engine()
    snapshots=[]
    # This helper is copied by CI; it does not replace the previous application.
    tables=['customer_accounts','customer_sessions','enquiry_messages','marketing_preferences']
    with engine.connect() as db:
        for table in tables:
            rows=db.execute(text('SELECT * FROM '+table+' ORDER BY 1')).all()
            snapshots.append([table,[tuple(row) for row in rows]])
        rows=db.execute(text('SELECT id,customer_account_id,promotions_opt_in,source,request_type,email,phone,activity,closure_reason,submission_key FROM enquiries_v2 ORDER BY id')).all()
        snapshots.append(['enquiry_extensions',[tuple(row) for row in rows]])
    engine.dispose()
    return hashlib.sha256(json.dumps(snapshots,default=str,sort_keys=True).encode()).hexdigest()


def create_customer_conversation(staff):
    # Real customer registration/login; cookie kept only in the private state file.
    from urllib.request import build_opener,HTTPCookieProcessor
    from http.cookiejar import CookieJar
    jar=CookieJar();browser=build_opener(HTTPCookieProcessor(jar))
    email='ci-'+secrets.token_hex(6)+'@example.com';password=secrets.token_urlsafe(24)
    for path,body in [('/api/customer/register',{'name':'Fictional CI customer','email':email,'password':password}),
                      ('/api/customer/login',{'email':email,'password':password})]:
        request=Request(BASE_URL+path,data=json.dumps(body).encode(),
            headers={'X-Requested-With':'DealerDesk','Content-Type':'application/json'})
        with browser.open(request,timeout=5) as response:assert response.status in (200,201)
    customer_token=next(c.value for c in jar if c.name=='dealer_customer_session')
    customer=Client(customer_token,'dealer_customer_session')
    conversation=customer.send('POST','/api/catalogue/enquiries',{
        'vehicle_id':None,'customer':'Fictional CI customer','email':email,
        'message':'Synthetic persistence request','request_type':'Other',
        'submission_key':str(uuid4()),'promotions_opt_in':True})['reference']
    staff.send('POST',f'/api/enquiries/{conversation}/messages',{'body':'Synthetic staff response'})
    customer.send('POST',f'/api/customer/enquiries/{conversation}/messages',{'body':'Synthetic customer response'})
    return customer_token,conversation


def verify_customer_records(state,client):
    customer=Client(state['customer_token'],'dealer_customer_session')
    records=customer.send('GET','/api/customer/enquiries')['items']
    assert [r['id'] for r in records]==[state['conversation']]
    messages=customer.send('GET',f"/api/customer/enquiries/{state['conversation']}/messages")['items']
    assert [m['author_role'] for m in messages]==['staff','customer']
    leads=client.send('GET','/api/leads')['items']
    assert any(r['id']==state['conversation'] and r['promotions'] and r['consent_history'] for r in leads)
    anonymous=Client('')
    for path in ['/api/leads',f"/api/customer/enquiries/{state['conversation']}/messages"]:
        try:anonymous.send('GET',path)
        except HTTPError as error:assert error.code==401
        else:raise AssertionError('Private endpoint accepted anonymous read')
    public=anonymous.send('GET','/api/catalogue')
    assert 'Fictional CI customer' not in str(public) and '@example.com' not in str(public)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['create', 'verify', 'verify-legacy'])
    args = parser.parse_args()
    if os.environ.get('DEALER_CI_REHEARSAL') != '1' or os.environ.get('VERCEL') or os.environ.get('APP_ENV') in ('production','staging'):
        raise SystemExit('Only explicitly marked disposable CI containers are permitted.')
    checked=rehearsal_engine();checked.dispose()
    if args.stage == 'create':
        engine = rehearsal_engine()
        with session_factory(engine)() as db:
            user = create_user(db, 'ci-'+secrets.token_hex(6), secrets.token_urlsafe(24), 'manager')
            token = issue_session(db, user)
        engine.dispose()
        client = Client(token)
        vehicle = client.send('POST', '/api/vehicles',
                              {'make': 'Synthetic', 'model': 'Container persistence', 'year': 2026, 'price_pence': 10000})
        enquiry = client.send('POST', '/api/enquiries',
                              {'vehicle_id': vehicle['id'], 'customer': 'Fictional CI buyer', 'message': 'Test only'})
        task = client.send('POST', '/api/tasks',
                           {'enquiry_id': enquiry['id'],
                            'due_date': datetime.now(ZoneInfo('Europe/London')).date().isoformat(), 'note': 'Synthetic check'})
        client.send('PATCH', f"/api/tasks/{task['id']}", {'revision': 1, 'completed': True})
        customer_token,conversation=create_customer_conversation(client)
        state = {'token': token, 'vehicle': vehicle['id'], 'task': task['id'], 'enquiry':enquiry['id'],
                 'customer_token':customer_token,'conversation':conversation,
                 'new_data_sha256':new_data_fingerprint()}
        print(json.dumps({'stage': 'create', 'vehicle': state['vehicle'], 'task_completed': True}))
        # Printed state deliberately excludes the private cookie.
        print('JOURNEY_STATE='+json.dumps({'vehicle': state['vehicle'], 'task': state['task']}))
    else:
        # CI privately copies this cookie file across container replacement.
        state = json.loads(STATE.read_text())
        client = Client(state['token'])
        client.send('GET', f"/api/vehicles/{state['vehicle']}")
        tasks = client.send('GET', '/api/tasks')
        assert any(row['id'] == state['task'] and row['completed'] for row in tasks['items'])
        if args.stage=='verify-legacy':
            # Only supported legacy operations; no attempt to use new signup semantics.
            legacy=client.send('GET',f"/api/enquiries/{state['enquiry']}")
            assert legacy['vehicle_id']==state['vehicle']
            vehicle=client.send('GET',f"/api/vehicles/{state['vehicle']}")
            client.send('PATCH',f"/api/vehicles/{state['vehicle']}",
                        {'revision':vehicle['revision'],'price_pence':10001})
        assert new_data_fingerprint()==state['new_data_sha256']
        if args.stage=='verify':
            verify_customer_records(state,client)
        print(json.dumps({'stage':args.stage,'records_preserved':True,'task_completed':True,
                          'new_data_preserved':True,'customer_api_checked':args.stage=='verify'}))
    STATE.write_text(json.dumps(state))
    STATE.chmod(0o600)


if __name__ == '__main__':
    main()
