"""Operator-only user creation. Password never appears in shell arguments."""
import argparse
import getpass
from sqlalchemy import select
from backend.models import User
from backend.auth import create_user
from backend.database import build_engine, session_factory

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('username')
    parser.add_argument('--role', choices=['viewer', 'sales', 'manager'], default='sales')
    parser.add_argument('--if-empty', action='store_true', help='Only bootstrap when no accounts exist.')
    args = parser.parse_args()
    engine = build_engine()
    with session_factory(engine)() as db:
        if args.if_empty and db.scalar(select(User.id).limit(1)):
            print('Existing accounts preserved.')
            engine.dispose()
            return
    password = getpass.getpass('New password (12+ characters): ')
    if password != getpass.getpass('Repeat password: '):
        raise SystemExit('Passwords differ; nothing changed.')
    try:
        with session_factory(engine)() as db:
            user = create_user(db, args.username, password, args.role)
            print(f'Created {user.username} ({user.role}).')
    except ValueError as error:
        raise SystemExit(str(error))
    finally:
        engine.dispose()

if __name__ == '__main__':
    main()
