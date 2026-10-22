"""Run from the project directory after dependencies and frontend build are prepared."""
import argparse
import os
from pathlib import Path
from alembic.config import Config
from alembic import command
import uvicorn

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    command.upgrade(Config('alembic.ini'), 'head')
    print(f'Open http://127.0.0.1:{args.port}. This address is local to this computer.', flush=True)
    uvicorn.run('backend.app:app', host=args.host, port=args.port, access_log=False)
