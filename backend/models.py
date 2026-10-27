from datetime import datetime, date, timezone
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, String, LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, deferred

def now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class Record:
    id: Mapped[int] = mapped_column(primary_key=True)
    revision: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)

class Vehicle(Record, Base):
    __tablename__ = 'vehicles_v2'
    make: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price_pence: Mapped[int] = mapped_column(Integer, nullable=False)
    approved_facts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(12), default='available', nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photos: Mapped[list['VehiclePhoto']] = relationship(lazy='selectin', order_by='VehiclePhoto.id')
    __table_args__ = (CheckConstraint('price_pence >= 0 AND price_pence <= 100000000'),CheckConstraint('year >= 1900 AND year <= 2100'),CheckConstraint("status IN ('available','reserved','sold')"),CheckConstraint('revision >= 1'))

class Enquiry(Record, Base):
    __tablename__ = 'enquiries_v2'
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey('vehicles_v2.id'), nullable=True, index=True)
    customer_account_id: Mapped[int | None] = mapped_column(ForeignKey('customer_accounts.id'),nullable=True,index=True)
    source: Mapped[str] = mapped_column(String(20), default='Other', nullable=False)
    request_type: Mapped[str] = mapped_column(String(30), default='Other', nullable=False)
    email: Mapped[str] = mapped_column(String(254), default='', nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default='', nullable=False)
    activity: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    closure_reason: Mapped[str] = mapped_column(String(300), default='', nullable=False)
    submission_key: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True)
    customer: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(12), default='new', nullable=False)
    __table_args__ = (CheckConstraint("status IN ('new','contacted','closed')"),CheckConstraint('revision >= 1'))

class Task(Record, Base):
    __tablename__ = 'tasks_v2'
    enquiry_id: Mapped[int] = mapped_column(ForeignKey('enquiries_v2.id'), nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str] = mapped_column(String(300), default='', nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    __table_args__ = (CheckConstraint('revision >= 1'),)

class AuditEvent(Base):
    __tablename__ = 'audit_events_v2'
    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    # IDs/state only. Never store customer messages or credentials here.

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(12), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    __table_args__ = (CheckConstraint("role IN ('viewer','sales','manager')"),)

class LoginSession(Base):
    __tablename__ = 'login_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class VehiclePhoto(Base):
    __tablename__ = 'vehicle_photos'
    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicles_v2.id'), nullable=False, index=True)
    caption: Mapped[str] = mapped_column(String(160), nullable=False)
    credit: Mapped[str] = mapped_column(String(200), default='', nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), default='', nullable=False)
    license: Mapped[str] = mapped_column(String(100), default='', nullable=False)
    license_url: Mapped[str] = mapped_column(String(1000), default='', nullable=False)
    illustrative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes] = deferred(mapped_column(LargeBinary, nullable=False))
    thumbnail: Mapped[bytes] = deferred(mapped_column(LargeBinary, nullable=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)

class CustomerAccount(Base):
    __tablename__='customer_accounts'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254),unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(80),nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256),nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)

class CustomerSession(Base):
    __tablename__='customer_sessions'
    token_hash: Mapped[str] = mapped_column(String(64),primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer_accounts.id'),nullable=False,index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

class CustomerToken(Base):
    __tablename__='customer_tokens'
    token_hash: Mapped[str] = mapped_column(String(64),primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer_accounts.id'),nullable=False)
    purpose: Mapped[str] = mapped_column(String(12),nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

class EnquiryMessage(Base):
    __tablename__='enquiry_messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    enquiry_id: Mapped[int] = mapped_column(ForeignKey('enquiries_v2.id'),nullable=False,index=True)
    author_role: Mapped[str] = mapped_column(String(12),nullable=False)
    body: Mapped[str] = mapped_column(String(2000),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=now,nullable=False)
