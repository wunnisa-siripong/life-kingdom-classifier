"""Offline deterministic export from the reviewed single source of truth.

Legacy GBIF/training builders are archived and cannot overwrite the curated data.
To refresh sources explicitly: python source_catalog.py --fetch
"""
import csv, json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def build():
    rows=json.loads((BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))
    with (BASE/'organism_catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    from catalog import read_catalog
    read_catalog(BASE/'organism_catalog.csv')
    print('Exported',len(rows),'catalogue rows; training/model unchanged')

if __name__=='__main__': build()
