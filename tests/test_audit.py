from scripts import audit_release


def test_cached_history_scan_still_reports_each_affected_revision(tmp_path, monkeypatch, capsys):
    (tmp_path/'clean.txt').write_text('clean')
    monkeypatch.setattr(audit_release, 'ROOT', tmp_path)
    commits = ['a'*40, 'b'*40]
    reads = []
    secret = b'ghp_' + b'x'*40
    def git(*args):
        if args[0] == 'ls-files':
            return b'clean.txt\0'
        if args[0] == 'rev-list':
            return '\n'.join(commits).encode()
        if args[0] == 'ls-tree':
            return b'100644 blob abc\thistorical.txt\0'
        assert args == ('cat-file', 'blob', 'abc')
        reads.append(args)
        return secret
    monkeypatch.setattr(audit_release, 'git', git)
    assert audit_release.main() == 1
    output = capsys.readouterr().out
    assert len(reads) == 1
    assert all(commit[:12]+' historical.txt: github_token' in output for commit in commits)
    assert secret.decode() not in output
