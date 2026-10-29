"""Replay reviewed catalogue substitutions/additions; never changes training data."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def reviewed_updates():
    return json.loads((BASE/'evidence/thai_catalog_updates.json').read_text(encoding='utf8'))

def apply_updates(rows, report):
    for change in reviewed_updates():
        row=dict(change['row'])
        index=next((i for i,r in enumerate(rows) if r['id']==row['id']),None)
        if index is None and change.get('replaces_id'):
            index=next((i for i,r in enumerate(rows) if r['id']==change['replaces_id']),None)
        audit=dict(id=row['id'],status='reviewed_user_catalog_update',before=change['before'],after=row,
                   review_basis='thai_catalog_update',review_sources=row['name_sources'].split('|'),
                   reference_kingdom=change.get('reference_kingdom'),
                   issues=['Scoped teaching example; image source identification is retained, not a specimen diagnosis.'])
        if change.get('accepted_key'):audit['accepted_key']=change['accepted_key']
        if index is None:rows.append(row);report.append(audit)
        else:rows[index]=row;report[index]=audit

if __name__=='__main__':
    e=BASE/'evidence/catalog_audit'
    rows=json.loads((e/'curated_catalog.json').read_text(encoding='utf8'))
    report=json.loads((e/'row_report.json').read_text(encoding='utf8'))
    apply_updates(rows,report)
    for name,data in [('curated_catalog',rows),('row_report',report)]:
        (e/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    summary=json.loads((e/'summary.json').read_text(encoding='utf8'))
    from catalog import FEATURES
    summary.update(date='2026-10-30',total=len(rows),new=len(rows)-117,
                   thai_total=sum(bool(r['thai_name']) for r in rows),thai_blank=sum(not r['thai_name'] for r in rows),
                   unknown_cells=sum(r[f]=='' for r in rows for f in FEATURES),
                   catalogue_changes='18 missing-photo records replaced with Thai-named examples; requested taxa deduplicated. No model retraining.')
    summary['added_by_kingdom']={k:sum(a['before'] is None and a['after']['Kingdom']==k for a in report) for k in sorted({r['Kingdom'] for r in rows})}
    summary['limitations']=[s for s in summary['limitations'] if not s.startswith('No new photographs')]
    (e/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print('Updated',len(reviewed_updates()),'reviewed records;',len(rows),'total')
