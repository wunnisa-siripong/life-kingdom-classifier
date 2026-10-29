"""Audit constraints and produce honest warnings separately from structural failures."""
import argparse, collections, concurrent.futures, csv, hashlib, json, urllib.parse, urllib.request
from pathlib import Path
from catalog import FEATURES, normalize, read_catalog, search
BASE=Path(__file__).resolve().parent
E=BASE/'evidence/catalog_audit'

def validate(check_links=False):
    data=read_catalog(BASE/'organism_catalog.csv')
    raw=list(csv.DictReader((BASE/'organism_catalog.csv').open(encoding='utf-8-sig')))
    report=json.loads((E/'row_report.json').read_text(encoding='utf8'))
    summary=json.loads((E/'summary.json').read_text(encoding='utf8'))
    assert len(data)==len(report)==summary['total']
    assert len(raw)-117==summary['new']
    assert len(set(a.get('accepted_key') for a in report if a.get('accepted_key')))==sum(bool(a.get('accepted_key')) for a in report), 'Duplicate accepted taxon'
    assert len(set(a['id'] for a in report))==len(raw)
    assert list(data['id'])==[a['id'] for a in report]
    cache={json.loads(p.read_text(encoding='utf8'))['url']:json.loads(p.read_text(encoding='utf8'))['data'] for p in (E/'responses').glob('*.json')}
    mismatches=[]; alias_index=collections.defaultdict(set); warnings=[]; urls=set()
    for row,audit in zip(raw,report):
        assert row=={k:str(v) for k,v in audit['after'].items()}
        if audit.get('accepted_key'):
            tax=cache[f'https://api.gbif.org/v1/species/{audit["accepted_key"]}']
            assert tax['taxonomicStatus']=='ACCEPTED'
            assert row['rank']==tax['rank'].lower()
            if row['rank']=='species': assert row['scientific_name']==tax['canonicalName']
        if audit['before'] is None:
            assert row['rank']=='species' and audit.get('occurrence_count',0)>0
            assert cache[audit['occurrence_query']]['facets']
            if row['thai_name']:
                override=audit.get('thai_name_evidence')
                assert override or any(n.get('language')=='tha' and n['vernacularName']==row['thai_name'] for n in audit['vernacular_records'])
        if audit.get('reference_kingdom') and row['Kingdom']!=audit['reference_kingdom']:
            mismatches.append({'id':row['id'],'project':row['Kingdom'],'reference':audit['reference_kingdom']})
        for f in FEATURES:
            assert row[f] in ('0','1','') and row[f+'_evidence'].strip()
            if row[f]=='': assert 'unknown' in row[f+'_evidence'].lower()
        assert row['Ribosome']=='1'
        if row['Kingdom']=='Animalia': assert [row[f] for f in FEATURES]==['1','0','1','0','0','1']
        if row['Kingdom']=='Monera': assert row['Nucleus']==row['Chloroplast']=='0'
        if row['Kingdom']=='Fungi': assert row['Photosynthesis']==row['Chloroplast']=='0'
        for n in [row['scientific_name'],row['thai_name'],row['english_name']]+row['aliases'].split('|'):
            if n:
                alias_index[normalize(n)].add(row['id'])
                assert row['id'] in set(search(data,n)['id'])
        for column in ['name_sources','feature_sources']:
            for url in row[column].split('|'):
                parsed=urllib.parse.urlparse(url.strip())
                assert parsed.scheme in ('http','https') and parsed.netloc, (row['id'],url)
                urls.add(url.strip())
        if any('\ufffd' in str(v) for v in row.values()): warnings.append({'id':row['id'],'issue':'Legacy replacement characters in text; cannot reconstruct lost wording without source review'})
    # Canonical export must regenerate byte-identically.
    before=(BASE/'organism_catalog.csv').read_bytes()
    from build_catalog import build
    build()
    assert before==(BASE/'organism_catalog.csv').read_bytes()
    protected={}
    for filename,expected in [('organisms.csv','53311374e7c0787131df5e81446564d0d1a5815a'),('life_kingdom_model.joblib','3aeef574a4c65a3de51a07b47fbd4ee4de15f2de')]:
        b=(BASE/filename).read_bytes()
        if filename.endswith('.csv'): b=b.replace(b'\r\n',b'\n')
        sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        assert sha==expected;protected[filename]=sha
    result=dict(structural_validation='passed',total=len(data),new=summary['new'],protected_files=protected,
                framework_differences=mismatches,shared_names={n:sorted(ids) for n,ids in alias_index.items() if len(ids)>1},
                text_warnings=warnings,unresolved_taxonomy=[a['id'] for a in report if a['status']=='unresolved'],
                biological_verification='Partial: legacy traits not independently reverified; new traits explicitly group-inferred or unknown',
                source_url_count=len(urls),live_link_check='not run')
    if check_links:
        def check(url):
            if url in cache: return dict(url=url,status=200,basis='retrieved source response cached')
            try:
                # Percent-encode Thai paths without altering existing escapes.
                safe=urllib.parse.quote(url,safe=':/?&=%#,+;@')
                req=urllib.request.Request(safe,headers={'User-Agent':'LifeKingdomEvidenceAudit/1.0'})
                with urllib.request.urlopen(req,timeout=18) as response:
                    return dict(url=url,status=response.status,final_url=response.url)
            except Exception as exc: return dict(url=url,status='unresolved',error=str(exc))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: links=list(pool.map(check,sorted(urls)))
        (E/'link_checks.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf8')
        result['live_link_check']={'retrievable':sum(x['status']==200 for x in links),'unresolved':sum(x['status']!=200 for x in links),'note':'HTTP availability does not certify that a source supports every biological claim'}
    elif (E/'link_checks.json').exists():
        recorded=json.loads((E/'link_checks.json').read_text(encoding='utf8'))
        if {x['url'] for x in recorded}==urls:
            result['live_link_check']={'retrievable':sum(x['status']==200 for x in recorded),'unresolved':sum(x['status']!=200 for x in recorded),'note':'Previously recorded link checks retained; not rerun by this offline validation. HTTP availability does not certify biological claims.'}
    (E/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    with (E/'row_report.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['id','status','scientific_name','thai_before','thai_after','rank','project_kingdom','reference_kingdom','unknown_traits','issues','sources']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row,a in zip(raw,report): writer.writerow(dict(id=row['id'],status=a['status'],scientific_name=row['scientific_name'],thai_before=(a['before'] or {}).get('thai_name',''),thai_after=row['thai_name'],rank=row['rank'],project_kingdom=row['Kingdom'],reference_kingdom=a.get('reference_kingdom',''),unknown_traits='|'.join(f for f in FEATURES if row[f]==''),issues='; '.join(a['issues']),sources=row['name_sources']+'|'+row['feature_sources']))
    print(json.dumps({k:v for k,v in result.items() if k not in ('shared_names','text_warnings')},ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check-links',action='store_true');args=p.parse_args();validate(args.check_links)
