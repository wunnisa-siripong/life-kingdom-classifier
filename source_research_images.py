"""Find organism figures in openly licensed primary research, never tree/graph substitutes.

Uses the current PMC Cloud metadata/media API, not retired OA package endpoints.
Raw XML is a local discovery cache. Selected figure/caption/licence evidence is tracked.
"""
import concurrent.futures,json,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
import enrich_profiles as e

REJECTED_PHOTOS={'gbif-8296805','gbif-2614118','gbif-7713104','gbif-2573550','gbif-8067271',
 'gbif-1653465','gbif-1650580','gbif-1650368','gbif-1650497'}

XL='{http://www.w3.org/1999/xlink}href'
def https(s):return s.replace('s3://pmc-oa-opendata/','https://pmc-oa-opendata.s3.amazonaws.com/')
def article(pmcid):
    md=e.get(f'https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.json')
    if md.get('is_retracted') or not md.get('media_urls') or not md.get('license_code','').startswith('CC '):return None
    url=https(md['xml_url']);path=e.OUT/(pmcid+'.xml')
    if path.exists(): raw=path.read_bytes()
    else:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':e.UA}),timeout=22) as r:raw=r.read()
        path.write_bytes(raw)
    root=ET.fromstring(raw)
    licences=root.findall('.//permissions/license')
    links=[l.get(XL,'') for l in licences]+[n.get(XL,'') for l in licences for n in l.iter()]
    # Modern JATS often stores the licence URL as ALI license_ref text, not xlink.
    links+=re.findall(r'https?://creativecommons\.org/(?:licenses|publicdomain)/[a-zA-Z0-9./-]+',' '.join(' '.join(l.itertext()) for l in licences))
    lic=next((e.licence(u) for u in links if e.licence(u)),None)
    if not lic:
        nd=next((u for u in links if '/licenses/by-nc-nd/' in u or '/licenses/by-nd/' in u),None)
        if nd:
            code,version=nd.rstrip('/').split('/')[-2:]
            lic=('CC '+code.upper()+' '+version,nd)
    if not lic:return None
    authors=[' '.join(a.itertext()).strip() for a in root.findall('.//article-meta/contrib-group/contrib/name')]
    return md,root,lic,('; '.join(authors[:5])+(' และคณะ' if len(authors)>5 else ''))

def run_one(row):
    rid=row['id'];p=e.OUT/(rid+'.json');record=json.loads(p.read_text(encoding='utf8'))
    name=row['scientific_name']; names=[name]
    tax=record.get('taxonomy',{})
    # The GBIF source can carry a previous combination; do not invent synonyms.
    name=re.sub(r'\s+spp?\..*','',name)
    if len(name.split())<2:return rid,'needs genus figure'
    search_names=[name]
    if tax.get('key'):
        try:
            syn=e.get(f'https://api.gbif.org/v1/species/{tax["key"]}/synonyms?limit=100')
            search_names+=list(dict.fromkeys(s['canonicalName'] for s in syn.get('results',[]) if s.get('canonicalName') and len(s['canonicalName'].split())==2))[:5]
        except Exception:pass
    query='('+' OR '.join('"'+n+'"' for n in search_names)+') AND OPEN_ACCESS:Y'
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=query,format='json',pageSize=40))
    try: results=e.get(url).get('resultList',{}).get('result',[])
    except Exception as exc:return rid,str(exc)
    aliases=[]
    for n in search_names:
        parts=n.split();aliases.extend([n.lower(),parts[0][0].lower()+'. '+parts[-1].lower()])
    for result in results:
        pmcid=result.get('pmcid')
        if not pmcid:continue
        try:
            data=article(pmcid)
            if not data:continue
            md,root,lic,authors=data
            captions=[e.clean(' '.join(f.find('caption').itertext())) for f in root.findall('.//fig') if f.find('caption') is not None]
            if len(captions)>2 and len(set(captions))<len(captions)/2:
                # Some publisher JATS repeats the wrong caption for every graphic.
                # A human must check the original PDF instead (e.g. Inocybe Figure 16).
                continue
            choices=[]
            for fig in root.findall('.//fig'):
                caption=' '.join(fig.find('caption').itertext()) if fig.find('caption') is not None else ''
                low=e.clean(caption).lower()
                if not any(a in low for a in aliases):continue
                photo_words=['morpholog','colonies','colony','conidia','conidiophore','hyphae','ascospore','basidioma','basidiocar','sporangi','micrograph','microscop','microbiological bait','fruiting bod','ascoma','conidioma','culture','cells','spores']
                if any(w in low for w in ['heatmap','heat map','expression profile','antioxidant activity','chemical structure','reproduced with permission','courtesy of','phylogenetic','maximum likelihood','phylogeny','screening flow','kinetics','purification steps','lc 50','lc50','quality metrics','gene expression','cultivation on']):continue
                if not any(w in low for w in photo_words):continue
                for graphic in fig.findall('.//graphic'):
                    file=graphic.get(XL,'')
                    urls=[https(u) for u in md['media_urls'] if urllib.parse.unquote(u.split('?')[0].rsplit('/',1)[-1])==file or Path(urllib.parse.unquote(u.split('?')[0].rsplit('/',1)[-1])).stem==file]
                    if urls:choices.append((len(low),fig,caption,urls[0]))
            for _,fig,caption,image in sorted(choices,key=lambda v:v[0]):
                try:local,size=e.download(rid,image,preserve='ND' in lic[0])
                except Exception:continue
                record.update(image=image,image_local=local,image_size=size,
                    image_source='https://pmc.ncbi.nlm.nih.gov/articles/'+pmcid+'/#'+fig.get('id',''),
                    credit=authors,license=lic[0],license_url=lic[1],image_taxon=name,
                    image_caption='ภาพโคโลนีหรือโครงสร้างของ '+name+' จากบทความวิจัย (ดูชื่อและแผงภาพในต้นฉบับ)',
                    alt='ภาพวิจัยของ '+name,source_api=https(md['xml_url']),paper_title=md['title'],paper_doi=md.get('doi'),paper_caption=e.clean(caption),
                    image_description=e.clean(caption),image_changes=('ไฟล์ภาพต้นฉบับ ไม่ดัดแปลงหรือครอป แสดงผลโดยรักษาสัดส่วน' if 'ND' in lic[0] else 'ย่อขนาดและแปลง JPEG โดยรักษาสัดส่วน แสดงทั้งภาพ ไม่ครอปแผงภาพ'),
                    image_mime={'.png':'image/png','.gif':'image/gif','.webp':'image/webp'}.get(Path(local).suffix,'image/jpeg'),
                    research_source='https://pmc.ncbi.nlm.nih.gov/articles/'+pmcid+'/',
                    searched_taxon_names=search_names,
                    review_status='exact species name and morphology figure matched; visual review pending')
                p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
                return rid,'ADDED '+pmcid
        except Exception:continue
    return rid,'no reusable species figure found'

def run():
    rows=json.loads((e.BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))
    todo=[r for r in rows if not json.loads((e.OUT/(r['id']+'.json')).read_text(encoding='utf8')).get('review_locked') and (not json.loads((e.OUT/(r['id']+'.json')).read_text(encoding='utf8')).get('image_local') or r['id'] in REJECTED_PHOTOS) and r['rank']=='species']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(run_one,todo):print(result,flush=True)
if __name__=='__main__':run()
