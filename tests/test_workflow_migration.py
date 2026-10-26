from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import IntegrityError
import pytest


def test_upgrade_preserves_existing_enquiry_and_task(tmp_path,monkeypatch):
    url='sqlite:///'+(tmp_path/'existing.sqlite3').as_posix()
    monkeypatch.setenv('DATABASE_URL',url)
    cfg=Config('alembic.ini')
    command.upgrade(cfg,'20261022_photos')
    engine=create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO vehicles_v2 (id,make,model,year,price_pence,approved_facts,status,archived,revision,created_at,updated_at) VALUES (1,'Ford','Puma',2026,100,'[]','available',0,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"))
        db.execute(text("INSERT INTO enquiries_v2 (id,vehicle_id,customer,message,status,revision,created_at,updated_at) VALUES (1,1,'Alex','Viewing','new',1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"))
        db.execute(text("INSERT INTO tasks_v2 (id,enquiry_id,due_date,note,completed,revision,created_at,updated_at) VALUES (1,1,'2026-12-01','Confirm viewing',0,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"))
    command.upgrade(cfg,'head')
    with engine.connect() as db:
        row=db.execute(text('SELECT customer,source,request_type,activity FROM enquiries_v2 WHERE id=1')).one()
        assert tuple(row)==('Alex','Other','Other','[]')
        assert db.execute(text('SELECT enquiry_id FROM tasks_v2 WHERE id=1')).scalar()==1
        assert not db.execute(text('PRAGMA foreign_key_check')).fetchall()
    checks={c['name'] for c in inspect(engine).get_check_constraints('enquiries_v2')}
    assert {'ck_enquiry_status','ck_enquiry_revision'} <= checks
    with pytest.raises(IntegrityError),engine.begin() as db:
        db.execute(text("UPDATE enquiries_v2 SET status='unknown' WHERE id=1"))
    engine.dispose()
