"""Bounded source/history checks. Report paths/rules only, never matched values."""
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    'aws_access_id': re.compile(rb'AKIA[A-Z0-9]{16}'),
    'hosted_database_credential': re.compile(
        rb'postgres(?:ql)?(?:\+psycopg)?://[^\s:/]+:[^\s@]+@'
        rb'(?!localhost[:/]|127\.0\.0\.1[:/]|host[:/]|db[:/]|example\.)[^\s/]+'),
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def forbidden(path):
    parts = PurePosixPath(path).parts
    name = parts[-1]
    return (any(part in ('.venv', 'node_modules', 'backups', 'data', '.vercel') for part in parts)
            or (name.startswith('.env') and name != '.env.example')
            or name.endswith(('.sqlite3', '.sqlite', '.db', '.log', '.pem', '.key')))


def findings(path, content):
    result = ['private_runtime_file'] if forbidden(path) else []
    if b'\x00' not in content:
        # Reviewed Compose variable reference, not a stored password. Keep this
        # exception exact; a literal credential in this file must still fail.
        if path == 'docker-compose.yml':
            content = content.replace(
                b'postgresql+psycopg://' + b'dealer:${POSTGRES_PASSWORD}@database:5432/dealer', b'')
        result.extend(rule for rule, pattern in PATTERNS.items() if pattern.search(content))
    return result


def main():
    hits = set()
    paths = git('ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0')
    count = 0
    for raw in filter(None, paths):
        path = raw.decode('utf-8')
        count += 1
        for rule in findings(path, (ROOT / path).read_bytes()):
            hits.add(('working-tree', path, rule))
    commits = git('rev-list', '--all').decode().splitlines()
    for commit in commits:
        rows = git('ls-tree', '-rz', '--full-tree', commit).split(b'\0')
        for row in filter(None, rows):
            metadata, raw = row.split(b'\t', 1)
            mode, kind, blob = metadata.split()
            if kind != b'blob':
                continue
            path = raw.decode('utf-8')
            content = git('cat-file', 'blob', blob.decode())
            for rule in findings(path, content):
                hits.add((commit[:12], path, rule))
    print(f'Checked {count} source files and {len(commits)} reachable commits.')
    for revision, path, rule in sorted(hits):
        print(f'REVIEW {revision} {path}: {rule}')
    print(f'{len(hits)} findings. This limited scan does not prove absence of secrets.')
    return 1 if hits else 0


if __name__ == '__main__':
    raise SystemExit(main())
