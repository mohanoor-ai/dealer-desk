"""Explicit hosted capability switch and a shared database write budget."""
import os
import time
from fastapi import HTTPException
from sqlalchemy import case,or_
from backend.config import hosted
from backend.models import PublicWriteWindow

def enquiries_enabled():
    return not hosted() or os.environ.get('PUBLIC_ENQUIRIES_ENABLED')=='true'

def public_budget(db,key,limit):
    # One bounded row per service, atomic across serverless instances.
    window=int(time.time())//900
    table=PublicWriteWindow.__table__
    dialect=db.bind.dialect.name
    if dialect=='postgresql':
        from sqlalchemy.dialects.postgresql import insert
    elif dialect=='sqlite':
        from sqlalchemy.dialects.sqlite import insert
    else:raise HTTPException(503,'Public request storage is unavailable.')
    statement=insert(table).values(service=key,window=window,count=1)
    statement=statement.on_conflict_do_update(index_elements=['service'],
        set_={'window':window,'count':case((table.c.window==window,table.c.count+1),else_=1)},
        where=or_(table.c.window!=window,table.c.count<limit)).returning(table.c.count)
    value=db.execute(statement).scalar()
    db.commit()
    if value is None:raise HTTPException(429,'Too many requests. Please try again later.')
