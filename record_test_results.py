import json,re,sys,hashlib
from pathlib import Path
import pandas,streamlit,sklearn
base=Path('.')
log=(base/'test_results.txt').read_text(encoding='utf-8',errors='replace')
assert re.search(r'Ran 10 tests in [\d.]+s\s+OK',log)
report=dict(status='passed',tests=10,python=sys.version.split()[0],streamlit=streamlit.__version__,pandas=pandas.__version__,scikit_learn=sklearn.__version__,date='2026-10-29',checks=['all catalogue names and aliases','unknown-profile does not predict','invalid binary values rejected','unchanged original training and model hashes','all 64 binary decision paths','catalogue cache invalidates after CSV content changes','search and navigation','Spirogyra model/reference mismatch'],mobile_browser='not verified; localhost timeout and file URL policy rejection')
(base/'evidence/catalog_audit/test_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
p=base/'evidence/ui_preview/preview_status.json';d=json.loads(p.read_text(encoding='utf8'));d['render_verification']='not verified: browser file URL policy rejected';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
