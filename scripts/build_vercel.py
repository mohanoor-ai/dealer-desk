"""Build only public frontend files; never connect to or migrate a database."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    npm = shutil.which('npm')
    if not npm:
        raise SystemExit('Node.js and npm are required to build the frontend.')
    for args in (['ci'], ['run', 'build']):
        subprocess.run([npm, *args], cwd=ROOT / 'frontend', check=True)
    # Dedicated generated destination, never copy repository/docs/runtime files.
    shutil.copytree(ROOT / 'frontend/dist', ROOT / 'public', dirs_exist_ok=True)


if __name__ == '__main__':
    main()
