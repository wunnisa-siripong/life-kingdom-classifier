"""Reproducible GBIF sourcing. Cached responses are evidence, never invented names.

Occurrence selection establishes reported presence, NOT native status or identification
certainty. Taxonomy and vernaculars are GBIF assertions, not editorial certification.
Run --fetch once, then offline replay with python source_catalog.py.
"""
import argparse, concurrent.futures, csv, datetime, hashlib, json, re, time
import urllib.request, urllib.parse
from pathlib import Path

BASE = Path(__file__).resolve().parent
E = BASE / 'evidence' / 'catalog_audit'
F = ['Ribosome','Photosynthesis','Nucleus','Cell wall','Chloroplast','Multicellular organisms']
DATE = '2026-10-29'
API = 'https://api.gbif.org/v1/'
BIO = 'https://openstax.org/books/biology-2e/pages/'
SOURCES = {'Animalia': BIO+'27-1-features-of-the-animal-kingdom',
           'Plantae': BIO+'25-1-early-plant-life',
           'Fungi': BIO+'24-1-characteristics-of-fungi'}
CELL = BIO+'4-3-eukaryotic-cells'

def norm(s):
    import unicodedata
    return ' '.join(unicodedata.normalize('NFKC',s).split()).casefold()

def get(url, fetch):
    path = E/'responses'/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if path.exists(): return json.loads(path.read_text(encoding='utf8'))['data']
    if not fetch: raise RuntimeError('Uncached evidence: '+url)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as response: data=json.load(response)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps({'url':url,'retrieved_on':DATE,'data':data},ensure_ascii=False),encoding='utf8')
            return data
        except Exception:
            if attempt==2: raise
            time.sleep(attempt+1)

def names(key,fetch):
    url=API+f'species/{key}/vernacularNames?limit=1000'
    records=get(url,fetch).get('results',[])
    def select(language):
        return list(dict.fromkeys(n['vernacularName'].strip() for n in records
            if n.get('language')==language and n.get('vernacularName')
            and (language!='tha' or re.search('[ก-๙]',n['vernacularName']))))
    return select('tha'), select('eng'), url, records

def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def run(fetch=False,promote=False):
    E.mkdir(parents=True,exist_ok=True)
    baseline=E/'baseline_117.csv'
    if not baseline.exists(): baseline.write_bytes((BASE/'organism_catalog.csv').read_bytes())
    rows=list(csv.DictReader(baseline.open(encoding='utf-8-sig')))
    assert len(rows)==117
    fields=list(rows[0])
    report=[]; used=set(); keys=set()
    def audit(row):
        before=dict(row); issues=[]
        if row['id']=='train-09':
            row['scientific_name']=''
            row['uncertainty']='Yeast is a growth form spanning multiple fungal taxa, not an accepted scientific name. Species unresolved; legacy traits describe the scoped yeast cell.'
            return row,dict(id=row['id'],status='unresolved',issues=['Scientific name genuinely unknown for this growth-form entry; blank instead of corrupted non-taxonomic text'],before=before,after=dict(row))
        if row['id']=='train-21': row['scientific_name']='Amoeba spp.'
        if row['id']=='train-43': row['scientific_name']='Bacillus sp.'
        query=re.sub(r'\s+spp?\..*$','',row['scientific_name'])
        query=re.sub(r'\s+\(.*$','',query)
        url=API+'species/match?name='+urllib.parse.quote(query)
        try:
            match=get(url,fetch)
            rank=row['rank'].lower()
            expected=('SPECIES' if rank.startswith('species') and 'unspecified' not in rank else
                      'GENUS' if rank.startswith('genus') else
                      'PHYLUM' if rank.startswith(('division','phylum')) else
                      'ORDER' if rank.startswith('order') else rank.upper())
            same_identity=norm(match.get('canonicalName',''))==norm(query) and match.get('rank')==expected
            if (match.get('matchType')!='EXACT' and not same_identity) or match.get('rank')!=expected:
                issues.append('Taxon/rank requires manual source review; original retained')
                return row,dict(id=row['id'],status='unresolved',issues=issues,before=before,after=dict(row),match_url=url)
            key=match.get('acceptedUsageKey',match['usageKey'])
            accepted=get(API+f'species/{key}',fetch)
            if accepted.get('taxonomicStatus')!='ACCEPTED':
                raise ValueError('Accepted taxon not established')
            th,en,nurl,records=names(key,fetch)
            canonical=accepted['canonicalName']
            row['rank']=accepted['rank'].lower()
            row['scientific_name']=canonical+(' spp.' if expected=='GENUS' else '')
            if not row['thai_name'] and th: row['thai_name']=th[0]
            aliases=row['aliases'].split('|')+th
            if row['scientific_name']!=before['scientific_name']: aliases.append(before['scientific_name'])
            if canonical=='Danaus plexippus':
                monarch=next((n for n in en if n.casefold()=='monarch butterfly'),None)
                if monarch: row['english_name']=monarch
                aliases=[n for n in aliases if n.casefold() not in ('milkweed','milkweed butterfly')]
            row['aliases']='|'.join(dict.fromkeys(n for n in aliases if n and n not in (row['thai_name'],row['scientific_name'],row['english_name'])))
            row['name_sources']+='|'+url+'|'+nurl
            row['verified_on']=DATE
            if row['Kingdom']!=accepted.get('kingdom'): issues.append('Project five-kingdom label differs from GBIF; intentional framework distinction, not automatically changed')
            if canonical=='Spirogyra':
                row['uncertainty']+='; Six traits overlap Plantae; project Protista label is pedagogical, not a six-trait biological discriminator.'
            issues.append('Legacy six-trait evidence retained: not independently reverified in this run')
            return row,dict(id=row['id'],status='taxonomy_checked_traits_legacy',issues=issues,before=before,after=dict(row),accepted_key=key,accepted_name=canonical,reference_kingdom=accepted.get('kingdom'),match_url=url,vernacular_records=records)
        except Exception as exc:
            return row,dict(id=row['id'],status='unresolved',issues=[str(exc)],before=before,after=dict(row),match_url=url)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        audited=list(pool.map(audit,rows))
    rows=[r for r,a in audited]; report=[a for r,a in audited]
    for r,a in audited:
        used.add(norm(r['scientific_name'])); used.add(norm(a.get('accepted_name',r['scientific_name'])))
        if a.get('accepted_key'): keys.add(a['accepted_key'])
    candidates=[]; bucket_limits={}; bucket_counts={}
    for kingdom,key,target in [('Plantae',6,120),('Animalia',1,120),('Fungi',5,60)]:
        # Bounding box prioritises northern Thailand reports; not a native checklist.
        strata=[(key,target)]
        if kingdom=='Animalia':
            strata=[]
            # Derive legacy occurrence-backbone class keys from accepted anchor
            # species, avoiding homonymous higher names in the matching service.
            for anchor,quota in [('Gallus gallus',40),('Elephas maximus',20),('Varanus salvator',15),('Xenopus laevis',15),('Apis mellifera',20),('Danio rerio',10)]:
                match=get(API+'species/match?name='+urllib.parse.quote(anchor),fetch)
                assert match['matchType']=='EXACT' and match['rank']=='SPECIES'
                tax=get(API+f'species/{match.get("acceptedUsageKey",match["usageKey"])}',fetch)
                assert tax['taxonomicStatus']=='ACCEPTED' and tax['kingdom']=='Animalia'
                group_key=tax.get('classKey',tax.get('orderKey'))
                class_tax=get(API+f'species/{group_key}',fetch)
                assert class_tax['rank'] in ('CLASS','ORDER') and class_tax['kingdom']=='Animalia'
                strata.append((group_key,quota))
        for stratum_key,quota in strata:
            url=API+f'occurrence/search?country=TH&taxon_key={stratum_key}&decimalLatitude=17,21&decimalLongitude=97,101.5&limit=0&facet=speciesKey&facetLimit=350'
            counts=get(url,fetch)['facets'][0]['counts']
            bucket_limits[url]=quota;bucket_counts[url]=0
            candidates.extend((kingdom,int(c['name']),url,c['count'],target) for c in counts)
    def source(c):
        kingdom,key,url,count,target=c
        if bucket_counts[url]>=bucket_limits[url]: return None
        try:
            tax=get(API+f'species/{key}',fetch)
            if tax.get('taxonomicStatus')!='ACCEPTED' or tax.get('rank')!='SPECIES' or tax.get('kingdom')!=kingdom: return None
            if kingdom=='Plantae' and tax.get('phylum')!='Tracheophyta': return None
            th,en,nurl,records=names(key,fetch)
            return (c,tax,th,en,nurl,records)
        except Exception as exc: return {'key':key,'error':str(exc)}
    added={k:0 for k in SOURCES}; failures=[]
    # Fetch in bounded batches; stop each group once quota is reached.
    for kingdom in SOURCES:
        group=[c for c in candidates if c[0]==kingdom]
        for start in range(0,len(group),20):
            if added[kingdom]>=group[0][4]: break
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(source,group[start:start+20]))
            for result in results:
                if result is None: continue
                if isinstance(result,dict): failures.append(result); continue
                c,tax,th,en,nurl,records=result
                kingdom,key,url,count,target=c
                canonical=tax['canonicalName']
                if key in keys or norm(canonical) in used or added[kingdom]>=target or bucket_counts[url]>=bucket_limits[url]: continue
                # No assertion of green tissue from a vascular-plant taxon alone:
                # parasitic/mycoheterotrophic exceptions require species evidence.
                vector={'Animalia':[1,0,1,0,0,1],'Plantae':[1,'',1,1,'',1],'Fungi':[1,0,1,1,0,'']}[kingdom]
                notes=['Representative living host cell contains ribosomes',
                       'Host is heterotrophic; excludes symbionts' if kingdom!='Plantae' else 'Unknown: species-level photosynthesis not checked; parasitic exceptions prevent automatic inference',
                       'Representative nucleated eukaryotic host cell; excludes specialised anucleate cells',
                       'Animal host cells lack a cell wall' if kingdom=='Animalia' else 'Cell wall of representative vegetative cell (group inference)',
                       'Host cells lack chloroplasts' if kingdom!='Plantae' else 'Unknown: species-level green tissue not checked',
                       'Adult body is multicellular' if kingdom!='Fungi' else 'Unknown: species growth form and life stage not independently checked']
                row=dict.fromkeys(fields,'')
                row.update(id='gbif-'+str(key),thai_name=th[0] if th else '',english_name=en[0] if en else '',scientific_name=canonical,
                           aliases='|'.join(dict.fromkeys(th[1:]+en[1:4])),rank='species',Kingdom=kingdom,
                           scope='Representative living nucleated host cell; adult body for multicellularity; excludes symbionts, spores, gametes, dormant and specialised anucleate cells.',
                           uncertainty='Traits are group-level inference with explicit unknown blanks, not species measurements. GBIF common names are source assertions and may be shared. Northern bounding-box occurrence is not proof of native status.',
                           name_sources=API+f'species/{key}'+'|'+nurl+'|'+url,
                           feature_sources=CELL+'|'+SOURCES[kingdom],evidence_basis='GBIF accepted species and reported northern-Thai occurrence; OpenStax group inference, species exceptions left unknown',verified_on=DATE)
                for f,v,note in zip(F,vector,notes): row[f]=v;row[f+'_evidence']=note+'; '+CELL+' ; '+SOURCES[kingdom]
                rows.append(row);keys.add(key);used.add(norm(canonical));added[kingdom]+=1;bucket_counts[url]+=1
                report.append(dict(id=row['id'],status='accepted_species_group_inference_partial_unknown' if '' in vector else 'accepted_species_group_inference',issues=[row['uncertainty']],before=None,after=dict(row),accepted_key=key,accepted_name=canonical,reference_kingdom=tax['kingdom'],occurrence_count=count,occurrence_query=url,vernacular_records=records))
    overrides=json.loads((BASE/'evidence/thai_name_overrides.json').read_text(encoding='utf8'))
    for row in rows:
        for override in overrides:
            # Scientific synonyms remain auditable in the before snapshot.
            audit_record=next(a for a in report if a['id']==row['id'])
            previous=(audit_record.get('before') or {}).get('scientific_name','')
            if override['scientific_name'] not in (row['scientific_name'],previous): continue
            if row['thai_name'] and row['thai_name']!=override['thai_name']:
                row['aliases']+='|'+row['thai_name']
            row['thai_name']=override['thai_name']
            row['aliases']='|'.join(dict.fromkeys(n for n in row['aliases'].split('|')+override['aliases'] if n and n!=row['thai_name']))
            row['name_sources']+='|'+override['source']
            audit_record['thai_name_evidence']=override
            audit_record['after']=dict(row)
    # Apply separately reviewed user-requested groups and names on offline replay.
    from requested_catalog import apply_requested
    apply_requested(rows, report)
    from catalog_updates import apply_updates
    apply_updates(rows, report)
    added = {k: sum(a['before'] is None and a['after']['Kingdom']==k for a in report)
             for k in sorted({r['Kingdom'] for r in rows})}
    # This is the single source of truth. build_catalog replays this snapshot only.
    snapshot=E/'curated_catalog.json'
    if snapshot.exists() and json.loads(snapshot.read_text(encoding='utf8'))!=rows and not promote:
        dump(E/'proposed_catalog.json',rows)
        raise RuntimeError('Source refresh differs from reviewed snapshot. Proposal saved; existing catalogue and row report preserved. Review diff before explicitly using --promote.')
    dump(E/'curated_catalog.json',rows)
    dump(E/'row_report.json',report)
    dump(E/'source_failures.json',failures)
    summary=dict(date=DATE,baseline=117,total=len(rows),new=len(rows)-117,added_by_kingdom=added,
                 thai_filled_existing=sum(not a['before']['thai_name'] and bool(a['after']['thai_name']) for a in report if a['before']),
                 thai_total=sum(bool(r['thai_name']) for r in rows),thai_blank=sum(not r['thai_name'] for r in rows),
                 existing_unresolved=sum(a['status']=='unresolved' for a in report),
                 unknown_cells=sum(r[f]=='' for r in rows for f in F),
                 legacy_traits_not_independently_reverified=117,
                 limitations=['GBIF occurrence reports are not a native checklist or province-level confirmation.',
                              'GBIF accepted taxonomy is a reference backbone assertion, not universal taxonomic consensus.',
                              'No new photographs; existing licensed profiles and kingdom icons retained.',
                              'Legacy trait evidence preserved and flagged for further independent review.',
                              'Requested broad groups are not species or northern-Thai occurrence claims; variable traits remain unknown.',
                              'Suk sun is Scorias sp. following CMU thesis p.77; septate vegetative mycelium is multicellular, conidia are not the scoped stage.'])
    dump(E/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fetch',action='store_true');parser.add_argument('--promote',action='store_true');args=parser.parse_args();run(args.fetch,args.promote)
