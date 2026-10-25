"""Fail closed unless the exact Git revision has a successful trusted CI run."""
import json
import re
import time
from urllib.request import Request, urlopen

REPOSITORY = 'mohanoor-ai/dealer-desk'


def passed(runs, revision):
    eligible = [run for run in runs if run.get('head_sha') == revision
                and run.get('path') == '.github/workflows/ci.yml'
                and run.get('event') == 'push'
                and run.get('head_branch') == 'main'
                and run.get('head_repository', {}).get('full_name') == REPOSITORY]
    if not eligible:
        return False
    latest = max(eligible, key=lambda run: (run.get('run_number', 0), run.get('run_attempt', 0)))
    return latest.get('status') == 'completed' and latest.get('conclusion') == 'success'


def require_ci(revision, attempts=24):
    if not re.fullmatch('[0-9a-f]{40}', revision or ''):
        raise RuntimeError('Release requires a full Git revision.')
    url = f'https://api.github.com/repos/{REPOSITORY}/actions/workflows/ci.yml/runs?head_sha={revision}&event=push&per_page=20'
    for attempt in range(attempts):
        request = Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'dealer-desk-release'})
        with urlopen(request, timeout=15) as response:
            runs = json.load(response)['workflow_runs']
        if passed(runs, revision):
            print('Trusted CI passed for exact revision '+revision, flush=True)
            return
        if attempt+1 < attempts:
            time.sleep(15)
    raise RuntimeError('No successful CI run for this exact revision; deployment denied.')
