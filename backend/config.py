"""Explicit hosted-runtime configuration; values never appear in error messages."""
import os
from sqlalchemy.engine import make_url


def hosted():
    return bool(os.environ.get('VERCEL')) or os.environ.get('APP_ENV') in ('production', 'staging')


def database_url(explicit=None):
    value = explicit or os.environ.get('DATABASE_URL')
    if not value:
        if hosted():
            raise RuntimeError('Hosted runtime requires DATABASE_URL.')
        return 'sqlite:///data/dealer-v2.sqlite3'
    try:
        parsed = make_url(value)
    except Exception:
        raise RuntimeError('DATABASE_URL is invalid.') from None
    if hosted():
        if parsed.get_backend_name() not in ('postgres', 'postgresql'):
            raise RuntimeError('Hosted runtime requires PostgreSQL.')
        if parsed.query.get('sslmode') not in ('require', 'verify-ca', 'verify-full'):
            raise RuntimeError('Hosted PostgreSQL requires TLS via sslmode.')
    if parsed.drivername in ('postgres', 'postgresql'):
        parsed = parsed.set(drivername='postgresql+psycopg')
    return parsed.render_as_string(hide_password=False)


def secure_cookies():
    return hosted() or os.environ.get('COOKIE_SECURE', '').lower() == 'true'
