"""Password hashing and server-side session helpers; no model makes access decisions."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from backend.models import User, LoginSession

COOKIE = 'dealer_session'

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
    return f'scrypt${salt}${digest.hex()}'

def verify_password(password, encoded):
    _, salt, expected = encoded.split('$')
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
    return hmac.compare_digest(digest.hex(), expected)

def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

def create_user(db, username, password, role):
    username = username.strip().lower()
    if not 3 <= len(username) <= 80 or not username.isascii() or not all(c.isalnum() or c in '._-' for c in username):
        raise ValueError('Username must have 3–80 letters, numbers, dots, underscores or hyphens.')
    if not 12 <= len(password) <= 128:
        raise ValueError('Use a password of 12–128 characters.')
    if role not in ('viewer', 'sales', 'manager'):
        raise ValueError('Unknown role.')
    if db.scalar(select(User).where(User.username == username)):
        raise ValueError('Username already exists; existing account was not changed.')
    user = User(username=username, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    return user

def issue_session(db, user):
    token = secrets.token_urlsafe(32)
    db.add(LoginSession(token_hash=token_hash(token), user_id=user.id,
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=8)))
    db.commit()
    return token
