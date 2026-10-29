"""Resumable exact-taxon photo/credit sourcing. Never alters model or traits.

GBIF occurrence/media assertions retain taxon, photographer and image-specific licence.
Broad catalogue groups use explicitly labelled representative taxa, not species guesses.
"""
import concurrent.futures, hashlib, html, io, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

BASE=Path(__file__).resolve().parent
OUT=BASE/'evidence/profile_sources'
ASSETS=BASE/'assets/species'
UA='LifeKingdomEducationalCatalogue/1.0 (source and licence review)'
GROUPS={
 'request-bamboo-shoots':('Bambusoideae','Bamboo shoot','หน่ออ่อนของไผ่ ภาพประกอบระดับกลุ่ม ไม่ระบุชนิด'),
 'request-het-lom':('Russula','Russula','ภาพตัวอย่างเห็ดในสกุล Russula ไม่ใช่การยืนยันชนิดของเห็ดหล่มทุกชนิด'),
 'request-suk-sun':('Scorias','Scorias spongiosa','ภาพตัวอย่าง Scorias ไม่ระบุซุกซุ่นทุกตัวอย่างเป็นชนิดเดียวกัน'),
 'request-worms':('Cestoda','Cestoda','ภาพตัวอย่างหนอนปรสิตในกลุ่มพยาธิตัวตืด ไม่ครอบคลุมพยาธิทุกกลุ่ม'),
 'request-jellyfish':('Scyphozoa','Jellyfish','ภาพตัวอย่างแมงกะพรุนในกลุ่ม Scyphozoa'),
 'request-corals':('Scleractinia','Coral','ภาพตัวอย่างปะการังหิน ไม่ครอบคลุมปะการังทุกกลุ่ม'),
 'request-hookworms':('Ancylostoma duodenale','Ancylostoma duodenale','ภาพตัวอย่างพยาธิปากขอชนิด Ancylostoma duodenale'),
 'request-shellfish':('Gastropoda','Gastropoda','ภาพตัวอย่างหอยฝาเดียว ไม่ครอบคลุมหอยทุกกลุ่ม'),
 'request-shrimps':('Caridea','Caridea','ภาพตัวอย่างกุ้งในกลุ่ม Caridea ไม่ครอบคลุมกุ้งทุกกลุ่ม'),
 'request-fishes':('Actinopterygii','Fish','ภาพตัวอย่างปลาครีบก้าน ไม่ครอบคลุมปลาทุกกลุ่ม'),
 'request-reptiles':('Reptilia','Reptile','ภาพประกอบกลุ่มสัตว์เลื้อยคลาน'),
 'request-molds':('Aspergillus','Mold','ภาพตัวอย่างราเส้นใยสกุล Aspergillus ไม่ใช่ราทุกชนิด'),
 'request-green-algae':('Chlorophyta','Green algae','ภาพตัวอย่างสาหร่ายสีเขียว ไม่ใช่ชนิดเดียวกันทั้งหมด'),
 'request-cyanobacteria':('Cyanobacteria','Cyanobacteria','ภาพตัวอย่างไซยาโนแบคทีเรีย ไม่ใช่ชนิดเดียวกันทั้งหมด'),
 'train-09':('Saccharomyces cerevisiae','Yeast','ภาพตัวอย่างยีสต์ Saccharomyces cerevisiae; รายการนี้เป็นรูปแบบการเจริญ ไม่ได้ระบุยีสต์ทุกชนิดเป็นชนิดนี้'),
 'train-11':('Polypodiopsida','Fern','ภาพตัวอย่างเฟิร์น ไม่ครอบคลุมทุกชนิด'),
 'train-48':('Alcyonacea','Sea fan','ภาพตัวอย่างกัลปังหาในกลุ่ม Alcyonacea'),
 'train-50':('Cirripedia','Barnacle','ภาพตัวอย่างเพรียงในกลุ่ม Cirripedia'),
}
COMMON={'Animalia':'สัตว์','Plantae':'พืช','Fungi':'รา','Protista':'โพรทิสตา','Monera':'มอเนอรา'}
SOURCES={'Animalia':'https://openstax.org/books/biology-2e/pages/27-1-features-of-the-animal-kingdom',
 'Plantae':'https://openstax.org/books/biology-2e/pages/25-1-early-plant-life',
 'Fungi':'https://openstax.org/books/biology-2e/pages/24-1-characteristics-of-fungi',
 'Protista':'https://openstax.org/books/biology-2e/pages/23-3-groups-of-protists',
 'Monera':'https://openstax.org/books/microbiology/pages/4-3-nonproteobacteria-gram-negative-bacteria-and-phototrophic-bacteria'}

def clean(v): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',str(v or '')))).strip()
def get(url):
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if p.exists(): return json.loads(p.read_text(encoding='utf8'))['data']
    for attempt in range(2):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA})
            with urllib.request.urlopen(req,timeout=22) as r: data=json.load(r)
            p.write_text(json.dumps(dict(url=url,retrieved_on='2026-10-29',data=data),ensure_ascii=False),encoding='utf8')
            return data
        except Exception:
            if attempt: raise
            time.sleep(0.5)

def licence(value):
    s=clean(value).lower().replace('https:','http:')
    if 'by-nd' in s or 'no derivatives' in s: return None
    if '/publicdomain/zero/' in s or s=='cc0': return ('CC0 1.0','https://creativecommons.org/publicdomain/zero/1.0/')
    if 'public domain' in s or s=='pd': return ('Public domain','https://creativecommons.org/publicdomain/mark/1.0/')
    m=re.search(r'(?:licenses/|cc\s+)(by-nc-sa|by-nc|by-sa|by)[/\s-]*(\d\.\d)',s)
    if m: return ('CC '+m[1].upper()+' '+m[2],f'https://creativecommons.org/licenses/{m[1]}/{m[2]}/')
    return None

def download(row_id,url,preserve=False):
    ASSETS.mkdir(parents=True,exist_ok=True)
    p=ASSETS/(row_id+'.jpg')
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(20_000_001)
    if len(raw)>20_000_000: raise ValueError('Image too large')
    original=Image.open(io.BytesIO(raw))
    if preserve:
        if original.format not in ('JPEG','PNG','GIF','WEBP'):raise ValueError('Cannot display original ND image format')
        suffix={'JPEG':'.jpg','PNG':'.png','GIF':'.gif','WEBP':'.webp'}[original.format]
        p=ASSETS/(row_id+suffix);p.write_bytes(raw)
        return p.relative_to(BASE).as_posix(),list(original.size)
    im=ImageOps.exif_transpose(original)
    if min(im.size)<120: raise ValueError('Image too small')
    im.thumbnail((900,900))
    if im.mode!='RGB':
        if im.mode=='RGBA':
            bg=Image.new('RGB',im.size,'white');bg.paste(im,mask=im.getchannel('A'));im=bg
        else: im=im.convert('RGB')
    im.save(p,'JPEG',quality=87,optimize=True)
    return p.relative_to(BASE).as_posix(),list(im.size)

def commons_photo(title):
    summary=get('https://en.wikipedia.org/api/rest_v1/page/summary/'+urllib.parse.quote(title.replace(' ','_'),safe=''))
    image=summary.get('originalimage',{}).get('source')
    if not image or '/commons/' not in image: return []
    filename=urllib.parse.unquote(image.rsplit('/',1)[-1].split('?')[0])
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',format='json',titles='File:'+filename,prop='imageinfo',iiprop='url|extmetadata'))
    pages=get(url).get('query',{}).get('pages',{})
    result=[]
    for page in pages.values():
        for info in page.get('imageinfo',[]):
            md=info.get('extmetadata',{});val=lambda k:md.get(k,{}).get('value','')
            lic=licence(val('LicenseShortName'))
            if lic and clean(val('Artist')):
                result.append(dict(image=info['url'],image_source=info['descriptionurl'],credit=clean(val('Artist')),license=lic[0],license_url=val('LicenseUrl') or lic[1],image_taxon=title,source_api=url,
                    encyclopedia_url=summary.get('content_urls',{}).get('desktop',{}).get('page',''),encyclopedia_excerpt=' '.join(summary.get('extract','').split()[:120]),image_description=clean(val('ImageDescription'))[:1500]))
    return result

def taxon_for(row,audit):
    group=GROUPS.get(row['id'])
    query=group[0] if group else re.sub(r'\s+spp?\..*','',row['scientific_name']).strip()
    if audit.get('accepted_key') and not group:
        key=audit['accepted_key']
    else:
        m=get('https://api.gbif.org/v1/species/match?'+urllib.parse.urlencode({'name':query}))
        if m.get('matchType')!='EXACT' and m.get('canonicalName','').casefold()!=query.casefold():
            search=get('https://api.gbif.org/v1/species/search?'+urllib.parse.urlencode(dict(q=query,status='ACCEPTED',limit=30)))
            kingdoms={'Monera':{'Bacteria','Archaea'},'Protista':{'Protozoa','Chromista','Plantae'},'Fungi':{'Fungi'},'Plantae':{'Plantae'},'Animalia':{'Animalia'}}[row['Kingdom']]
            matches=[t for t in search.get('results',[]) if t.get('canonicalName','').casefold()==query.casefold() and t.get('kingdom') in kingdoms and t.get('taxonomicStatus')=='ACCEPTED']
            if not matches: return None,query,group
            # Prefer backbone usage over duplicate dataset usages.
            matches.sort(key=lambda t:t.get('datasetKey')!='d7dddbf4-2cf0-4f39-9b2a-bb099caae36c')
            key=matches[0]['key']
        else: key=m.get('acceptedUsageKey',m['usageKey'])
    return get(f'https://api.gbif.org/v1/species/{key}'),query,group

def gbif_photos(tax):
    key=tax['key']; result=[]
    url=f'https://api.gbif.org/v1/occurrence/search?taxon_key={key}&media_type=StillImage&occurrence_status=PRESENT&limit=30'
    records=get(url).get('results',[])
    records.sort(key=lambda r: (r.get('basisOfRecord')!='HUMAN_OBSERVATION',r.get('basisOfRecord')=='PRESERVED_SPECIMEN'))
    for r in records:
        if tax['rank']=='SPECIES' and r.get('speciesKey')!=key and r.get('acceptedTaxonKey')!=key: continue
        for media in r.get('media',[]):
            lic=licence(media.get('license',''))
            credit=clean(media.get('creator') or media.get('rightsHolder'))
            image=media.get('identifier','')
            if media.get('type')=='StillImage' and lic and credit and image.startswith('https://'):
                result.append(dict(image=image,image_source=f'https://www.gbif.org/occurrence/{r["key"]}',credit=credit,license=lic[0],license_url=lic[1],image_taxon=r.get('acceptedScientificName') or r.get('scientificName',''),source_api=url,occurrence_id=r['key'],image_description=clean(media.get('description') or media.get('title'))))
    return result

def enrich(row,audit):
    rid=row['id']; dest=OUT/(rid+'.json')
    if dest.exists():
        prev=json.loads(dest.read_text(encoding='utf8'))
        if prev.get('review_locked'): return rid,'review retained'
        if prev.get('image_local') and (BASE/prev['image_local']).exists(): return rid,'cached'
    tax=None; errors=[]; group=GROUPS.get(rid)
    try: tax,query,group=taxon_for(row,audit)
    except Exception as e: errors.append('taxonomy: '+str(e))
    title=group[1] if group else re.sub(r'\s+spp?\..*','',row['scientific_name']).strip()
    candidates=[]
    if tax:
        try: candidates+=gbif_photos(tax)
        except Exception as e: errors.append('gbif: '+str(e))
    if not candidates:
        try: candidates+=commons_photo(title)
        except Exception as e: errors.append('commons: '+str(e))
    photo=None
    for candidate in candidates[:8]:
        try:
            path,size=download(rid,candidate['image'])
            photo=dict(candidate,image_local=path,image_size=size);break
        except Exception as e: errors.append('image: '+str(e))
    if not photo and tax and candidates:
        try:
            for candidate in gbif_photos(tax)[:6]:
                try:
                    path,size=download(rid,candidate['image']);photo=dict(candidate,image_local=path,image_size=size);break
                except Exception: pass
        except Exception: pass
    th=row['thai_name'] or row['english_name'] or row['scientific_name']
    identity=row['scientific_name'] or 'กลุ่มชื่อสามัญ ไม่ใช่ชื่อชนิดทางวิทยาศาสตร์'
    taxonomy=tax or {}
    parts=[f'{th} เป็น{COMMON[row["Kingdom"]]}ตามระบบ 5 อาณาจักรของโครงงาน']
    if row['scientific_name']: parts.append('ใช้ชื่อ '+identity)
    for field,label in [('family','วงศ์'),('order','อันดับ'),('class','ชั้น')]:
        if taxonomy.get(field): parts.append(label+' '+taxonomy[field])
    description=' '.join(parts)+ ' ข้อมูลลักษณะทั้ง 6 ข้อด้านล่างใช้ระยะชีวิตและชนิดเซลล์ตามขอบเขตของรายการ'
    profile=dict(id=rid,description=description,facts=[('ข้อมูลระดับกลุ่ม' if row['rank']!='species' else 'ข้อมูลระดับชนิด'),*([f'วงศ์ {taxonomy["family"]}'] if taxonomy.get('family') else []),f'อาณาจักร {row["Kingdom"]}'],
        source=row['name_sources'].split('|')[0],source_label='แหล่งอ้างอิงชื่อและชีววิทยาของรายการ',
        taxonomy=taxonomy,image_caption=group[2] if group else ('ภาพตัวอย่างในกลุ่ม '+identity if row['rank']!='species' else 'ภาพ '+identity),
        errors=errors,review_status='source-matched image; visual review pending' if photo else 'image missing',verified_on='2026-10-29')
    if photo: profile.update(photo,alt=profile['image_caption'],image_changes='ย่อขนาดและแปลงเป็น JPEG โดยรักษาสัดส่วน ไม่ครอป')
    dest.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf8')
    return rid,'photo' if photo else 'MISSING'

def run():
    rows=json.loads((BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))
    audits={r['id']:r for r in json.loads((BASE/'evidence/catalog_audit/row_report.json').read_text(encoding='utf8'))}
    counts={};completed=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(enrich,r,audits[r['id']]):r['id'] for r in rows}
        for future in concurrent.futures.as_completed(futures):
            rid=futures[future]
            try: _,status=future.result()
            except Exception as exc: status='ERROR';print(rid,str(exc),flush=True)
            counts[status]=counts.get(status,0)+1;completed+=1
            if completed%20==0 or status in ('MISSING','ERROR'): print(completed,rid,status,counts,flush=True)
    print('FINISHED',counts,flush=True)

if __name__=='__main__': run()
