"""Real database routes for one dealership. Run migrations before starting."""
import logging
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from backend import auth, schemas as s
from backend.database import build_engine, session_factory
from backend.models import User, LoginSession, Vehicle, Enquiry, Task, AuditEvent, now
from backend.contract import describe_api

logger = logging.getLogger('dealer')
ROOT = Path(__file__).resolve().parents[1]

def dealer_today():
    return datetime.now(ZoneInfo(os.environ.get('DEALER_TIMEZONE', 'Europe/London'))).date()

def record_dict(record):
    return {column.key: getattr(record, column.key) for column in record.__table__.columns}

def find(db, model, record_id):
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(404, 'Record not found.')
    return record

def audit(db, entity, record, action, actor):
    db.add(AuditEvent(entity=entity, entity_id=record.id, revision=record.revision,
                      action=action, actor_id=actor.id))

def save_new(db, model, data, entity, actor):
    record = model(**data)
    db.add(record)
    db.flush()
    audit(db, entity, record, 'created', actor)
    db.commit()
    return record_dict(record)

def save_edit(db, model, record_id, body, entity, actor):
    values = body.model_dump(exclude_unset=True)
    revision = values.pop('revision')
    values.update(revision=revision + 1, updated_at=now())
    result = db.execute(update(model).where(model.id == record_id, model.revision == revision)
                        .values(**values).execution_options(synchronize_session=False))
    if result.rowcount != 1:
        db.rollback()
        current = find(db, model, record_id)
        raise HTTPException(409, {'message': 'This record changed. Refresh before editing again.',
                                  'current_revision': current.revision})
    db.expire_all()
    record = find(db, model, record_id)
    audit(db, entity, record, 'updated', actor)
    db.commit()
    return record_dict(record)

def page(db, model, conditions, offset, limit):
    count = db.scalar(select(func.count()).select_from(model).where(*conditions))
    rows = db.scalars(select(model).where(*conditions).order_by(model.id.desc()).offset(offset).limit(limit))
    return {'items': [record_dict(row) for row in rows], 'total': count, 'offset': offset, 'limit': limit}

def create_app(database_url=None):
    engine = build_engine(database_url)
    factory = session_factory(engine)

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(title='Dealer Desk API', version='0.3.0', lifespan=lifespan)
    app.state.engine = engine
    app.state.sessions = factory
    # Local milestone guard only. Distributed public deployment requires a shared limiter.
    attempts = defaultdict(deque)
    attempt_lock = Lock()
    dummy_password = auth.hash_password('unused-dummy-password')

    def database():
        with factory() as db:
            yield db

    def signed_in(request: Request, db=Depends(database)):
        token = request.cookies.get(auth.COOKIE, '')
        session = db.get(LoginSession, auth.token_hash(token)) if token else None
        if session is None:
            raise HTTPException(401, 'Please sign in.')
        expiry = session.expires_at.replace(tzinfo=timezone.utc)
        user = db.get(User, session.user_id)
        if expiry <= datetime.now(timezone.utc) or user is None or not user.active:
            raise HTTPException(401, 'Your session expired. Please sign in again.')
        return user

    def can_write(user=Depends(signed_in)):
        if user.role not in ('sales', 'manager'):
            raise HTTPException(403, 'Your account has read-only access.')
        return user

    def manager(user=Depends(signed_in)):
        if user.role != 'manager':
            raise HTTPException(403, 'Manager access is required.')
        return user

    @app.middleware('http')
    async def request_boundary(request: Request, call_next):
        request.state.request_id = uuid4().hex
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            # HTML cross-origin forms cannot set this header. No CORS middleware permits preflight.
            if request.headers.get('x-requested-with') != 'DealerDesk' or request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'error': {'code': 'forbidden', 'message': 'Use the same-origin application.',
                                               'request_id': request.state.request_id}}, status_code=403)
        started = time.monotonic()
        response = await call_next(request)
        response.headers['X-Request-ID'] = request.state.request_id
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        if request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        # Route template avoids logging record IDs, query strings, submitted fields or secrets.
        route = request.scope.get('route')
        logger.info('request id=%s route=%s method=%s status=%s duration_ms=%.1f',
                    request.state.request_id, getattr(route, 'path', 'static'), request.method,
                    response.status_code, (time.monotonic() - started) * 1000)
        return response

    @app.exception_handler(HTTPException)
    async def api_error(request, exc):
        detail = exc.detail if isinstance(exc.detail, dict) else {'message': str(exc.detail)}
        error = {'code': {401: 'unauthorized', 403: 'forbidden', 404: 'not_found', 409: 'conflict',
                          422: 'validation', 429: 'rate_limit'}.get(exc.status_code, 'request_failed'),
                 'message': detail['message'], 'request_id': request.state.request_id}
        if 'current_revision' in detail:
            error['current_revision'] = detail['current_revision']
        return JSONResponse({'error': error}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        # Never return raw input (which may contain a password).
        fields = sorted({str(error['loc'][-1]) for error in exc.errors()})
        return JSONResponse({'error': {'code': 'validation', 'message': 'Check these fields: ' + ', '.join(fields)[:220],
                                      'request_id': request.state.request_id}}, status_code=422)

    @app.exception_handler(SQLAlchemyError)
    async def database_failure(request, exc):
        logger.error('database_unavailable request_id=%s', request.state.request_id)
        return JSONResponse({'error': {'code': 'unavailable', 'message': 'Storage is temporarily unavailable. Try again.',
                                      'request_id': request.state.request_id}}, status_code=503)

    @app.get('/health')
    def health(db=Depends(database)):
        db.execute(select(Vehicle.id).limit(1))
        return {'status': 'ok', 'version': app.version}

    @app.post('/api/auth/login', response_model=s.UserOutput)
    def login(body: s.Login, request: Request, response: Response, db=Depends(database)):
        username = body.username.strip().lower()
        key = (request.client.host if request.client else 'unknown', username)
        current = time.monotonic()
        with attempt_lock:
            # Bound memory and reject saturated limiter rather than evicting active lockouts.
            for old_key in list(attempts):
                while attempts[old_key] and attempts[old_key][0] < current - 900:
                    attempts[old_key].popleft()
                if not attempts[old_key]:
                    del attempts[old_key]
            if len(attempts) >= 1000 or len(attempts[key]) >= 10:
                raise HTTPException(429, 'Too many sign-in attempts. Wait 15 minutes.')
            attempts[key].append(current)
        user = db.scalar(select(User).where(User.username == username))
        valid = auth.verify_password(body.password, user.password_hash if user else dummy_password)
        if not valid or user is None or not user.active:
            raise HTTPException(401, 'Username or password is incorrect.')
        token = auth.issue_session(db, user)
        response.set_cookie(auth.COOKIE, token, httponly=True, samesite='strict', max_age=8 * 3600,
                            secure=os.environ.get('COOKIE_SECURE', 'false').lower() == 'true', path='/')
        return {'id': user.id, 'username': user.username, 'role': user.role}

    @app.get('/api/auth/me', response_model=s.UserOutput)
    def me(user=Depends(signed_in)):
        return {'id': user.id, 'username': user.username, 'role': user.role}

    @app.post('/api/auth/logout', status_code=204)
    def logout(request: Request, response: Response, db=Depends(database)):
        token = request.cookies.get(auth.COOKIE, '')
        session = db.get(LoginSession, auth.token_hash(token)) if token else None
        if session:
            db.delete(session)
            db.commit()
        response.delete_cookie(auth.COOKIE, path='/')

    @app.get('/api/vehicles', response_model=s.Page[s.VehicleOutput])
    def vehicles(q: str = Query('', max_length=100), status: s.Status | None = None,
                 include_archived: bool = False, offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
                 user=Depends(signed_in), db=Depends(database)):
        conditions = []
        if not include_archived:
            conditions.append(Vehicle.archived.is_(False))
        if status:
            conditions.append(Vehicle.status == status)
        if q:
            conditions.append(func.lower(Vehicle.make + ' ' + Vehicle.model).contains(q.lower(), autoescape=True))
        return page(db, Vehicle, conditions, offset, limit)

    @app.get('/api/vehicles/{vehicle_id}', response_model=s.VehicleOutput)
    def vehicle(vehicle_id: int, user=Depends(signed_in), db=Depends(database)):
        return record_dict(find(db, Vehicle, vehicle_id))

    @app.post('/api/vehicles', status_code=201, response_model=s.VehicleOutput)
    def add_vehicle(body: s.VehicleCreate, user=Depends(can_write), db=Depends(database)):
        return save_new(db, Vehicle, body.model_dump(), 'vehicle', user)

    @app.patch('/api/vehicles/{vehicle_id}', response_model=s.VehicleOutput)
    def edit_vehicle(vehicle_id: int, body: s.VehicleEdit, user=Depends(can_write), db=Depends(database)):
        record = find(db, Vehicle, vehicle_id)
        if record.status == 'sold' and body.status == 'reserved':
            raise HTTPException(409, 'Return sold stock to available before reserving it.')
        return save_edit(db, Vehicle, vehicle_id, body, 'vehicle', user)

    @app.get('/api/enquiries', response_model=s.Page[s.EnquiryOutput])
    def enquiries(vehicle_id: int | None = Query(None, ge=1), status: str | None = Query(None, pattern='^(new|contacted|closed)$'),
                  offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), user=Depends(signed_in), db=Depends(database)):
        conditions = []
        if vehicle_id:
            conditions.append(Enquiry.vehicle_id == vehicle_id)
        if status:
            conditions.append(Enquiry.status == status)
        return page(db, Enquiry, conditions, offset, limit)

    @app.get('/api/enquiries/{enquiry_id}', response_model=s.EnquiryOutput)
    def enquiry(enquiry_id: int, user=Depends(signed_in), db=Depends(database)):
        return record_dict(find(db, Enquiry, enquiry_id))

    @app.post('/api/enquiries', status_code=201, response_model=s.EnquiryOutput)
    def add_enquiry(body: s.EnquiryCreate, user=Depends(can_write), db=Depends(database)):
        vehicle = find(db, Vehicle, body.vehicle_id)
        if vehicle.archived:
            raise HTTPException(409, 'Restore this vehicle before recording an enquiry.')
        return save_new(db, Enquiry, body.model_dump(), 'enquiry', user)

    @app.patch('/api/enquiries/{enquiry_id}', response_model=s.EnquiryOutput)
    def edit_enquiry(enquiry_id: int, body: s.EnquiryEdit, user=Depends(can_write), db=Depends(database)):
        record = find(db, Enquiry, enquiry_id)
        if record.status == 'closed' and body.status == 'new':
            raise HTTPException(409, 'Reopen a closed enquiry as contacted first.')
        return save_edit(db, Enquiry, enquiry_id, body, 'enquiry', user)

    @app.get('/api/tasks', response_model=s.Page[s.TaskOutput])
    def tasks(enquiry_id: int | None = Query(None, ge=1), completed: bool | None = None, overdue: bool | None = None,
              offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), user=Depends(signed_in), db=Depends(database)):
        conditions = []
        if enquiry_id:
            conditions.append(Task.enquiry_id == enquiry_id)
        if completed is not None:
            conditions.append(Task.completed == completed)
        if overdue is not None:
            overdue_condition = (Task.completed.is_(False)) & (Task.due_date < dealer_today())
            conditions.append(overdue_condition if overdue else ~overdue_condition)
        return page(db, Task, conditions, offset, limit)

    @app.get('/api/tasks/{task_id}', response_model=s.TaskOutput)
    def task(task_id: int, user=Depends(signed_in), db=Depends(database)):
        return record_dict(find(db, Task, task_id))

    @app.post('/api/tasks', status_code=201, response_model=s.TaskOutput)
    def add_task(body: s.TaskCreate, user=Depends(can_write), db=Depends(database)):
        enquiry = find(db, Enquiry, body.enquiry_id)
        if enquiry.status == 'closed':
            raise HTTPException(409, 'Reopen this enquiry before scheduling a follow-up.')
        if body.due_date < dealer_today():
            raise HTTPException(422, 'Choose today or a future date.')
        return save_new(db, Task, body.model_dump(), 'task', user)

    @app.patch('/api/tasks/{task_id}', response_model=s.TaskOutput)
    def edit_task(task_id: int, body: s.TaskEdit, user=Depends(can_write), db=Depends(database)):
        record = find(db, Task, task_id)
        enquiry = find(db, Enquiry, record.enquiry_id)
        if body.due_date is not None and body.due_date < dealer_today():
            raise HTTPException(422, 'Choose today or a future date.')
        if body.completed is False and enquiry.status == 'closed':
            raise HTTPException(409, 'Reopen the enquiry before reopening its follow-up.')
        return save_edit(db, Task, task_id, body, 'task', user)

    @app.get('/api/dashboard', response_model=s.Dashboard)
    def dashboard(user=Depends(signed_in), db=Depends(database)):
        vehicles = list(db.scalars(select(Vehicle).where(Vehicle.archived.is_(False))))
        open_ids = select(Enquiry.id).where(Enquiry.status != 'closed')
        tasks = list(db.scalars(select(Task).where(Task.completed.is_(False), Task.enquiry_id.in_(open_ids))))
        return {'available': sum(v.status == 'available' for v in vehicles),
                'reserved': sum(v.status == 'reserved' for v in vehicles),
                'sold': sum(v.status == 'sold' for v in vehicles),
                'stock_value_pence': sum(v.price_pence for v in vehicles if v.status != 'sold'),
                'open_enquiries': db.scalar(select(func.count()).select_from(Enquiry).where(Enquiry.status != 'closed')),
                'open_tasks': len(tasks), 'overdue_tasks': sum(t.due_date < dealer_today() for t in tasks)}

    @app.get('/api/changes')
    def changes(after: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100), user=Depends(signed_in), db=Depends(database)):
        events = list(db.scalars(select(AuditEvent).where(AuditEvent.id > after).order_by(AuditEvent.id).limit(limit + 1)))
        selected = events[:limit]
        return {'items': [{'sequence': e.id, 'entity': e.entity, 'entity_id': e.entity_id,
                           'revision': e.revision, 'occurred_at': e.occurred_at} for e in selected],
                'next_sequence': selected[-1].id if selected else after, 'has_more': len(events) > limit}

    @app.get('/api/audit')
    def audit_history(offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), user=Depends(manager), db=Depends(database)):
        return page(db, AuditEvent, [], offset, limit)

    built_frontend = ROOT / 'frontend' / 'dist'
    if built_frontend.exists():
        app.mount('/', StaticFiles(directory=built_frontend, html=True), name='frontend')
    app.openapi = lambda: describe_api(app)
    return app

app = create_app()
