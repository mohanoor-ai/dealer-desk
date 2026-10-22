"""Describe the same cookie and middleware rules that the server enforces."""
from fastapi.openapi.utils import get_openapi

def describe_api(app):
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    components = schema.setdefault('components', {})
    components['securitySchemes'] = {
        'sessionCookie': {'type':'apiKey','in':'cookie','name':'dealer_session',
                          'description':'HttpOnly eight-hour session issued by login; logout revokes.'}}
    components.setdefault('schemas', {})['ApiError'] = {
        'type':'object', 'required':['error'], 'additionalProperties':False,
        'properties':{'error':{'type':'object','required':['code','message','request_id'],
            'properties':{'code':{'type':'string'},'message':{'type':'string'},
                          'request_id':{'type':'string'},'current_revision':{'type':'integer','minimum':1}}}}}
    for path, operations in schema['paths'].items():
        for method, operation in operations.items():
            if method not in ('get','post','patch','put','delete'):
                continue
            if path.startswith('/api/') and path not in ('/api/auth/login','/api/auth/logout'):
                operation['security'] = [{'sessionCookie':[]}]
            if method in ('post','patch','put','delete'):
                operation.setdefault('parameters', []).append({
                    'name':'X-Requested-With','in':'header','required':True,
                    'schema':{'type':'string','const':'DealerDesk'},
                    'description':'Same-origin mutation guard; cross-site requests are rejected.'})
            for code, description in [('401','Sign-in required or invalid credentials'),
                ('403','Permission or same-origin check failed'),('404','Record not found'),
                ('409','Stale revision or workflow conflict'),('422','Invalid input'),
                ('429','Rate limit exceeded'),('503','Storage unavailable')]:
                operation['responses'][code] = {'description':description,'content':{
                    'application/json':{'schema':{'$ref':'#/components/schemas/ApiError'}}}}
    return schema
