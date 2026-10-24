"""Run the core checks from any directory; stop on the first failure."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm:
        print('Install Node.js and npm before running verification.', flush=True)
        return 1
    commands = [
        ([sys.executable, '-m', 'pytest', 'tests'], ROOT),
        ([npm, 'test'], ROOT / 'frontend'),
        ([npm, 'run', 'build'], ROOT / 'frontend'),
        ([sys.executable, '-m', 'scripts.audit_release'], ROOT),
    ]
    for command, directory in commands:
        print('\nChecking: ' + ' '.join(command[1:] if command[0] == sys.executable else command), flush=True)
        result = subprocess.run(command, cwd=directory, check=False)
        if result.returncode:
            return result.returncode
    print('Core verification passed. PostgreSQL, browsers and containers need separate checks.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
