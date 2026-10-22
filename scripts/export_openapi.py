"""Export the implemented API and annotate its enforced cookie/CSRF boundary."""
from pathlib import Path
import yaml
from backend.app import create_app

def export():
    app = create_app('sqlite:///:memory:')
    schema = app.openapi()
    app.state.engine.dispose()
    return schema

if __name__ == '__main__':
    Path('openapi.yaml').write_text(yaml.safe_dump(export(),sort_keys=False),encoding='utf-8')
