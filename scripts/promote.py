"""Operator-invoked production branch promotion after exact-revision CI verification."""
import argparse
import os
import subprocess
from scripts.release_gate import require_ci


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('revision', help='Full, reviewed Git SHA whose CI passed')
    args = parser.parse_args()
    if os.environ.get('VERCEL'):
        raise SystemExit('Promotion must be explicitly invoked by an operator, not a hosted build.')
    require_ci(args.revision)
    subprocess.run(['git', 'cat-file', '-e', args.revision+'^{commit}'], check=True)
    # No force push: incompatible branch history requires deliberate operator review.
    subprocess.run(['git', '-c', 'credential.interactive=false', 'push', 'origin',
                    args.revision+':refs/heads/production-release'],
                   env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}, check=True)
    print('Production branch advanced to verified revision '+args.revision+'. Check deployment and smoke results.')


if __name__ == '__main__':
    main()
