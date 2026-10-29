"""Build the offline presentation overlay and photo-coverage report; no inference API."""
import hashlib,json
from pathlib import Path
from PIL import Image
from catalog import FEATURES
from enrich_profiles import BASE,OUT,SOURCES,COMMON
from species import PROFILES

ANIMAL_CLASS={
 'Aves':('นก','นกมีขนแบบขนนกและมีจะงอยปาก เป็นสัตว์มีกระดูกสันหลัง','29-5-birds'),
 'Mammalia':('สัตว์เลี้ยงลูกด้วยน้ำนม','สัตว์กลุ่มนี้มีต่อมน้ำนมสำหรับเลี้ยงลูก และมีขนในบางช่วงของชีวิต','29-6-mammals'),
 'Amphibia':('สัตว์สะเทินน้ำสะเทินบก','สัตว์กลุ่มนี้มีผิวหนังที่มีต่อมและใช้ผิวหนังช่วยแลกเปลี่ยนแก๊ส วงจรชีวิตแตกต่างตามชนิด','29-3-amphibians'),
 'Reptilia':('สัตว์เลื้อยคลาน','สัตว์กลุ่มนี้หายใจด้วยปอดและมีผิวหนังที่ช่วยลดการสูญเสียน้ำ','29-4-reptiles'),
 'Actinopterygii':('ปลาครีบก้าน','เป็นปลาที่มีก้านครีบช่วยพยุงครีบ หายใจด้วยเหงือกในระยะทั่วไป','29-2-fishes'),
 'Insecta':('แมลง','แมลงระยะตัวเต็มวัยมีขา 3 คู่ และแบ่งลำตัวเป็นหัว อก และท้อง','28-6-superphylum-ecdysozoa-arthropods'),
 'Arachnida':('สัตว์กลุ่มแมง','สัตว์กลุ่มแมงโดยทั่วไปมีขา 4 คู่ในระยะโตเต็มวัย และไม่มีหนวดแบบแมลง','28-6-superphylum-ecdysozoa-arthropods'),
 'Chilopoda':('ตะขาบ','ตะขาบมีลำตัวเป็นปล้อง โดยปล้องลำตัวที่มีขามีขา 1 คู่ต่อปล้อง','28-6-superphylum-ecdysozoa-arthropods'),
 'Cephalopoda':('หมึก','หมึกเป็นมอลลัสก์ที่มีแขนหรือหนวดอยู่รอบปาก และใช้กล้ามเนื้อแมนเทิลช่วยเคลื่อนที่','28-4-superphylum-lophotrochozoa-mollusks-and-annelids'),
 'Gastropoda':('หอยฝาเดียว','หอยฝาเดียวเป็นกลุ่มมอลลัสก์ที่รวมทั้งชนิดมีเปลือกและทากที่เปลือกลดรูป','28-4-superphylum-lophotrochozoa-mollusks-and-annelids'),
 'Asteroidea':('ดาวทะเล','ดาวทะเลเป็นเอไคโนเดิร์มที่มีระบบท่อน้ำและเท้าท่อ ใช้ในการเคลื่อนที่และดำรงชีวิต','28-7-superphylum-deuterostomia'),
 'Echinoidea':('เม่นทะเล','เม่นทะเลเป็นเอไคโนเดิร์มที่มีโครงแข็งและหนาม ไม่มีแขนแบบดาวทะเล','28-7-superphylum-deuterostomia'),
 'Holothuroidea':('ปลิงทะเล','ปลิงทะเลเป็นเอไคโนเดิร์มที่มีลำตัวอ่อนยาวและมีหนวดรอบปาก','28-7-superphylum-deuterostomia'),
}

def biological_text(row,tax):
    kingdom=row['Kingdom']; extra=[]
    if kingdom=='Animalia':
        cl=ANIMAL_CLASS.get(tax.get('class'))
        if cl:
            return cl[0],cl[1]+' เซลล์ของตัวสัตว์ไม่มีผนังเซลล์และไม่มีคลอโรพลาสต์ ไม่รวมสิ่งมีชีวิตร่วมอาศัย', ['https://openstax.org/books/biology-2e/pages/'+cl[2],SOURCES[kingdom]]
        return 'สัตว์','สัตว์เป็นยูคาริโอตหลายเซลล์ เซลล์ร่างกายไม่มีผนังเซลล์และไม่มีคลอโรพลาสต์ จึงรับสารอินทรีย์จากสิ่งแวดล้อมหรือสิ่งมีชีวิตอื่น ไม่รวมคุณลักษณะของสาหร่ายร่วมอาศัย',[SOURCES[kingdom]]
    if kingdom=='Fungi':
        group=tax.get('phylum','')
        detail={'Basidiomycota':'อยู่ในไฟลัม Basidiomycota ซึ่งมีระยะสืบพันธุ์แบบอาศัยเพศสร้างสปอร์บนเบซิเดีย',
                'Ascomycota':'อยู่ในไฟลัม Ascomycota ซึ่งมีระยะสืบพันธุ์แบบอาศัยเพศสร้างสปอร์ในถุงแอสคัส'}.get(group,'รามีทั้งรูปแบบยีสต์และเส้นใย ต้องแยกชนิดและระยะชีวิตเมื่อพิจารณาจำนวนเซลล์')
        return 'รา',detail+' ราไม่มีคลอโรพลาสต์และไม่สังเคราะห์แสง รับสารอาหารโดยดูดซึมสารอินทรีย์',[SOURCES[kingdom],'https://openstax.org/books/biology-2e/pages/24-2-classifications-of-fungi']
    if kingdom=='Plantae':
        detail='เซลล์พืชระยะเจริญมีนิวเคลียสและผนังเซลล์'
        if tax.get('class')=='Liliopsida': detail='เป็นพืชดอกกลุ่มใบเลี้ยงเดี่ยว '+detail
        elif tax.get('phylum')=='Tracheophyta': detail='เป็นพืชมีท่อลำเลียง '+detail
        detail+=' ใบหรือเนื้อเยื่อสีเขียวที่มีคลอโรพลาสต์ทำหน้าที่สังเคราะห์แสง แต่ไม่ใช่ทุกอวัยวะหรือทุกระยะชีวิต'
        return 'พืช',detail,[SOURCES[kingdom],'https://openstax.org/books/biology-2e/pages/4-3-eukaryotic-cells']
    if kingdom=='Monera':
        return 'แบคทีเรีย','เป็นโพรคาริโอต ไม่มีนิวเคลียสที่มีเยื่อหุ้มและไม่มีคลอโรพลาสต์ แบคทีเรียบางกลุ่ม เช่น ไซยาโนแบคทีเรีย สังเคราะห์แสงได้โดยไม่ใช้คลอโรพลาสต์',[SOURCES[kingdom]]
    return 'โพรทิสตา','เป็นยูคาริโอตในระบบ 5 อาณาจักรของโครงงาน โพรทิสตามีทั้งรูปแบบเซลล์เดียว โคโลนี และหลายเซลล์ ความสามารถสังเคราะห์แสงและโครงสร้างเซลล์จึงต้องดูข้อมูลเฉพาะรายการ',[SOURCES[kingdom]]

def build():
    rows=json.loads((BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))
    profiles={};missing=[]
    for row in rows:
        p=OUT/(row['id']+'.json')
        if not p.exists(): missing.append(row['id']);continue
        info=json.loads(p.read_text(encoding='utf8'))
        tax=info.get('taxonomy',{})
        kind,body,refs=biological_text(row,tax)
        name=row['thai_name'] or row['english_name'] or row['scientific_name']
        identity=row['scientific_name']
        heading=name+' เป็น'+kind+'ในระบบ 5 อาณาจักรของโครงงาน'
        if identity: heading+=' ใช้ชื่อ '+identity
        if tax.get('family'): heading+=' อยู่ในวงศ์ '+tax['family']
        info['description']=info.get('species_description_th') or heading+' '+body
        if tax.get('key'):
            info['source']=f'https://www.gbif.org/species/{tax["key"]}'
            info['source_label']='GBIF · อนุกรมวิธานอ้างอิง'
        info['biology_sources']=list(dict.fromkeys(info.get('biology_sources',[])+refs+([info['research_source']] if info.get('research_source') else [])+(['https://doi.org/'+info['paper_doi']] if info.get('paper_doi') else [])))
        if info.get('image_local'):
            image=BASE/info['image_local']
            with Image.open(image) as im: im.verify()
            info['image_sha256']=hashlib.sha256(image.read_bytes()).hexdigest()
            if row['rank']!='species' and info.get('image_taxon'):
                info['image_caption']=info.get('image_caption','ภาพตัวแทนของกลุ่ม')+' · ชื่อในแหล่งภาพ: '+info['image_taxon']
        else: missing.append(row['id'])
        # Complete raw chosen-source evidence remains separate from the compact UI overlay.
        info.pop('taxonomy',None);info.pop('errors',None)
        reviewed=PROFILES.get('catalog:'+row['id']) or PROFILES.get(row['scientific_name']) or {}
        if reviewed.get('image') and not (info.get('reviewed_image_cached') and info.get('image_original')==reviewed['image']):
            for key in ['image_local','image_caption','image_changes','image_taxon','image_sha256']:
                info.pop(key,None)
        info.update(reviewed)
        if info.get('license_url','').startswith('http://creativecommons.org/'):
            info['license_url']='https://'+info['license_url'][7:]
        profiles[row['id']]=info
    (BASE/'organism_profiles.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2),encoding='utf8')
    report=dict(total=len(rows),profiles=len(profiles),images=sum(bool(p.get('image_local') or p.get('image')) for p in profiles.values()),missing_images=missing,
                biological_detail='Taxonomic identity from source records plus sourced group biology; not an independent species diagnosis.',
                photo_identity='Species images matched to source taxon; broad-group images explicitly labelled representative; occurrence identifications are source assertions.',
                licences='Image-specific CC licences and credits retained. NC assets are for this noncommercial educational project; image modifications stated.',
                model_and_training='Not modified')
    (BASE/'evidence/profile_coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# เครดิตภาพรายรายการ','', 'ภาพใช้เพื่อโครงงานการศึกษาที่ไม่ใช่เชิงพาณิชย์ ภาพแต่ละไฟล์คงเงื่อนไขใบอนุญาตของตน รวมถึง NC/SA/ND เมื่อระบุ ภาพ ND เก็บไฟล์ภาพต้นฉบับ ส่วนการย่อขนาด แปลงรูปแบบ หรือครอปภาพอื่นระบุไว้รายภาพในข้อมูลเครดิต ไม่ได้เปลี่ยนสิทธิ์ภาพเป็นสิทธิ์ของโค้ดโครงงาน', '', '| รายการ | ผู้ถ่าย/ผู้สร้าง | สิทธิ์ | แหล่งต้นฉบับ |','|---|---|---|---|']
    for rid,p in profiles.items():
        if p.get('image_local') or p.get('image'):
            lines.append(f'| {rid} | {p["credit"].replace("|", "/")} | [{p["license"]}]({p["license_url"]}) | [ต้นฉบับ]({p["image_source"]}) |')
    (BASE/'IMAGE_CREDITS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': build()
