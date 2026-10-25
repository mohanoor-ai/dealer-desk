from scripts.release_gate import passed

SHA = 'a'*40


def run(**overrides):
    return {'head_sha': SHA, 'path': '.github/workflows/ci.yml', 'event': 'push',
            'head_branch': 'main',
            'head_repository': {'full_name': 'mohanoor-ai/dealer-desk'},
            'run_number': 1, 'run_attempt': 1, 'status': 'completed', 'conclusion': 'success', **overrides}


def test_gate_rejects_wrong_revision_workflow_origin_failure_and_rerun():
    assert passed([run()], SHA)
    for invalid in [run(head_sha='b'*40), run(path='untrusted.yml'), run(event='pull_request'), run(head_branch='untrusted'),
                    run(head_repository={'full_name': 'someone/fork'}), run(conclusion='failure'),
                    run(status='in_progress'), run(conclusion='cancelled')]:
        assert not passed([invalid], SHA)
    assert not passed([run(), run(run_attempt=2, conclusion='failure')], SHA)
    assert not passed([], SHA)
