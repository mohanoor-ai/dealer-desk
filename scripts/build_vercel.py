"""Build only public frontend files; never connect to or migrate a database."""
from pathlib import Path
import shutil
import subprocess
import os
from scripts.release_gate import require_ci

ROOT = Path(__file__).resolve().parents[1]


def main():
    if os.environ.get('VERCEL'):
        require_ci(os.environ.get('VERCEL_GIT_COMMIT_SHA'))
    npm = shutil.which('npm')
    if not npm:
        raise SystemExit('Node.js and npm are required to build the frontend.')
    for args in (['ci'], ['run', 'build']):
        subprocess.run([npm, *args], cwd=ROOT / 'frontend', check=True)
    # Only generated assets are copied; approved public article sources/images are bundled by Vite.
    shutil.copytree(ROOT / 'frontend/dist', ROOT / 'public', dirs_exist_ok=True)


if __name__ == '__main__':
    main()
