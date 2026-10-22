from pathlib import Path
import yaml
from scripts.export_openapi import export

def test_committed_contract_matches_implementation():
    committed = yaml.safe_load(Path('openapi.yaml').read_text(encoding='utf-8'))
    assert committed == export(), 'Regenerate and review openapi.yaml after API changes.'
