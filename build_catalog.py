"""Curate a search catalogue separately from the immutable training CSV."""
import csv, json, re, shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
FEATURES = ['Ribosome','Photosynthesis','Nucleus','Cell wall','Chloroplast','Multicellular organisms']
CELL = 'https://openstax.org/books/biology-2e/pages/4-3-eukaryotic-cells'
PLANT = 'https://openstax.org/books/biology-2e/pages/25-1-early-plant-life'
ANIMAL = 'https://openstax.org/books/biology-2e/pages/27-1-features-of-the-animal-kingdom'
IPST = 'https://www.scimath.org/lesson-biology/item/11306-2020-02-17-06-56-12'
def read(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig')))
def unique(values):
    return list(dict.fromkeys(x.strip() for x in values if x and x.strip()))

EVIDENCE = BASE/'evidence' if (BASE/'evidence/Data_Audit_50_final_v3.csv').exists() else ROOT/'outputs/Evidence_Package'
audit = read(EVIDENCE/'Data_Audit_50_final_v3.csv')
metadata = read(EVIDENCE/'Kingdom_metadata_final.csv')
training = read(BASE/'organisms.csv')
rows = []
excluded = {'Rhizopus':'Coenocytic hyphae: multicellular encoding needs an explicit modelling convention.',
            'Slime mold':'Unresolved lineage and life stage: multicellularity is not a single verified value.',
            'Red tube coral':'Common name cannot be resolved to one taxon.'}
for i,(row,a,m) in enumerate(zip(training,audit,metadata),1):
    assert row['Common name'] == a['Name_in_v3'] == m['Common name']
    if row['Common name'] in excluded: continue
    r = {'id':f'train-{i:02}', 'thai_name':'','english_name':row['Common name'],
         'scientific_name':m['Scientific Name'] or m['Taxon Name / Interpretation'],
         'aliases':m['Alias'], 'rank':m['Taxonomic Rank'], 'Kingdom':row['Kingdom'],
         'scope':m['Life Stage'], 'uncertainty':m['Notes'],
         'name_sources':m['Data Source'].replace(' ; ','|'),
         'feature_sources':a['Evidence_URLs'].replace(' ; ','|'),
         'evidence_basis':'Project v3 row audit (2026-10-17); scoped reference encoding, not a specimen measurement',
         'verified_on':'2026-10-17', 'training_name':row['Common name']}
    for f in FEATURES:
        r[f] = row[f]
        r[f+'_evidence'] = a['Check_'+f]
    if row['Common name']=='Amoeba':
        r['thai_name']='อะมีบา'; r['name_sources']+='|'+IPST
    if row['Common name']=='Paramecium':
        r['thai_name']='พารามีเซียม'; r['name_sources']+='|'+IPST
    if row['Common name']=='Asian elephant':
        r['thai_name']='ช้าง'; r['name_sources']+='|https://www.dft.go.th/th-th/แสดงเนื้อหา/ArticleId/1943'
    rows.append(r)

# Only names returned by GBIF are added; no translations are generated.
preferred = {'Mangifera indica':'Mango','Oryza sativa':'Rice','Zea mays':'Maize',
             'Solanum lycopersicum':'Tomato','Solanum tuberosum':'Potato',
             'Cucumis sativus':'Cucumber','Homo sapiens':'Human','Felis catus':'Domestic cat',
             'Panthera tigris':'Tiger','Panthera leo':'Lion','Aedes aegypti':'Yellow fever mosquito'}
name_evidence = []
taxa_path = BASE/'taxon_verification.json'
if not taxa_path.exists(): taxa_path=BASE/'evidence/gbif_taxa_2026-10-27.json'
for item in json.loads(taxa_path.read_text(encoding='utf8')):
    if item.get('excluded'): continue
    match = item['match']
    canonical = match['canonicalName']
    names = item['vernaculars']['results']
    en = unique(n['vernacularName'] for n in names if n.get('language')=='eng' and ',' not in n['vernacularName'])
    th = unique(n['vernacularName'] for n in names if n.get('language')=='tha' and re.search('[ก-๙]',n['vernacularName']) and 'ฯ' not in n['vernacularName'])
    desired = preferred.get(item['requested'],'')
    english = next((n for n in en if n.casefold()==desired.casefold()),en[0] if en else '')
    # Keep at most 4 English aliases. Full source records are retained in evidence/.
    aliases = unique([n for n in en if n!=english][:4]+th[1:])
    plant = item['kingdom']=='Plantae'
    vector = [1,1,1,1,1,1] if plant else [1,0,1,0,0,1]
    scope = ('Mature green plant; photosynthetic leaf tissue under light, not every cell, seed or dormant stage'
             if plant else 'Juvenile/adult host body and representative nucleated somatic cell; excludes symbionts, gametes and mature mammalian red blood cells')
    r = {'id':'gbif-'+str(match.get('acceptedUsageKey',match['usageKey'])),
         'thai_name':th[0] if th else '', 'english_name':english,
         'scientific_name':canonical, 'aliases':'|'.join(aliases), 'rank':match['rank'].lower(),
         'Kingdom':item['kingdom'], 'scope':scope,
         'uncertainty':'Feature values are explicit group-level biological inferences for the stated scope, not six species-specific laboratory measurements. Common names may be shared by other taxa; select the scientific name.',
         'name_sources':item['match_url']+'|'+item['names_url'],
         'feature_sources':CELL+'|'+(PLANT if plant else ANIMAL),
         'evidence_basis':'GBIF exact taxon match + documented plant/animal cell biology; group-level inference',
         'verified_on':'2026-10-27','training_name':''}
    notes = (['All living cells contain ribosomes','Green leaf photosynthetic capability under light',
              'Representative eukaryotic cell has a nucleus','Plant cell wall',
              'Green leaf cell chloroplast','Mature land plant body is multicellular'] if plant else
             ['All living cells contain ribosomes','Host animal is heterotrophic; excludes symbionts',
              'Representative nucleated somatic cell','Animal cell membrane is not a cell wall',
              'Host animal cell lacks chloroplasts','Animal body is multicellular'])
    for f,v,note in zip(FEATURES,vector,notes):
        r[f]=v; r[f+'_evidence']='Group-level inference: '+note
    if item['requested']=='Mangifera indica':
        r['thai_name']='มะม่วง';r['aliases']+='|มะม่วงบ้าน|มะม่วงสวน'
        r['name_sources']+='|https://rspg.mfu.ac.th/plant-genetic-conservation/botany/detail/490|https://www.clgc.agri.kps.ku.ac.th/resources/fruit/manaifera.html'
    rows.append(r)
    for n in names:
        if n.get('vernacularName') in [r['thai_name'],english]+aliases:
            name_evidence.append({'id':r['id'],'name':n['vernacularName'],'language':n.get('language',''),
                                  'source':n.get('source',''),'url':item['names_url']})

columns = list(rows[0])
with (BASE/'organism_catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
(BASE/'evidence').mkdir(exist_ok=True)
for name in ['Data_Audit_50_final_v3.csv','Kingdom_metadata_final.csv']:
    if (EVIDENCE/name).resolve() != (BASE/'evidence'/name).resolve():
        shutil.copyfile(EVIDENCE/name,BASE/'evidence'/name)
if taxa_path.resolve() != (BASE/'evidence'/'gbif_taxa_2026-10-27.json').resolve():
    shutil.copyfile(taxa_path,BASE/'evidence'/'gbif_taxa_2026-10-27.json')
(BASE/'evidence'/'name_evidence.json').write_text(json.dumps(name_evidence,ensure_ascii=False,indent=2),encoding='utf8')
(BASE/'evidence'/'excluded.json').write_text(json.dumps(excluded,indent=2),encoding='utf8')
print('Catalogue:',len(rows),'entries;',sum(bool(r['thai_name']) for r in rows),'with verified Thai names')
print({k:sum(r['Kingdom']==k for r in rows) for k in sorted(set(r['Kingdom'] for r in rows))})
