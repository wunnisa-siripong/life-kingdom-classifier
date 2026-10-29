"""Reviewed names/groups requested 2026-10-29; offline replay, never training data.

Informal names are not fabricated scientific taxa. Empty traits remain unknown.
References describe groups, not six independent measurements of each species.
"""
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
BIO = 'https://openstax.org/books/biology-2e/pages/'
CELL = BIO+'4-3-eukaryotic-cells'
ANIMAL = BIO+'27-1-features-of-the-animal-kingdom'
FUNGI = BIO+'24-1-characteristics-of-fungi'
CNID = BIO+'28-2-phylum-cnidaria'
FLAT = BIO+'28-3-superphylum-lophotrochozoa-flatworms-rotifers-and-nemerteans'
MOLL = BIO+'28-4-superphylum-lophotrochozoa-mollusks-and-annelids'
ARTH = BIO+'28-6-superphylum-ecdysozoa-arthropods'
ECH = BIO+'28-7-superphylum-deuterostomia'
VERT = BIO+'29-chapter-summary'
PLANT = BIO+'25-1-early-plant-life'
ALGAE = 'https://openstax.org/books/microbiology/pages/5-4-algae'
CDC = 'https://www.cdc.gov/dpdx/'
F = ['Ribosome','Photosynthesis','Nucleus','Cell wall','Chloroplast','Multicellular organisms']

# slug, Thai name, English name, scientific group (blank when informal), rank, source, aliases
ANIMALS = [
 ('crabs','ปู (กลุ่มปูแท้)','True crabs','Brachyura','infraorder',ARTH,'ปู'),
 ('worms','พยาธิ (หนอนปรสิต)','Parasitic worms','','informal group',FLAT,'พยาธิ|หนอนปรสิต'),
 ('jellyfish','แมงกะพรุน (กลุ่มทั่วไป)','Jellyfish','','informal group',CNID,'แมงกะพรุน'),
 ('corals','ปะการัง (กลุ่มทั่วไป)','Corals','','informal group',CNID,'ปะการัง'),
 ('tapeworms','พยาธิตัวตืด','Tapeworms','Cestoda','class',FLAT,''),
 ('planarians','พลานาเรีย (กลุ่มทั่วไป)','Planarians','Tricladida','order',FLAT,'พลานาเรีย'),
 ('ascaris','พยาธิไส้เดือน','Human roundworm','Ascaris lumbricoides','species',CDC+'ascariasis/index.html','ยาธิไส้เดือน'),
 ('pinworm','พยาธิเส้นด้าย','Human pinworm','Enterobius vermicularis','species',CDC+'enterobiasis/index.html','พยาธิเข็มหมุด'),
 ('hookworms','พยาธิปากขอ (กลุ่มในลำไส้)','Intestinal hookworms','','informal group',CDC+'hookworm/index.html','พยาธิปากขอ'),
 ('shellfish','หอย (กลุ่มทั่วไป)','Shelled mollusks','','informal group',MOLL,'หอย'),
 ('cephalopods','หมึก (กลุ่มเซฟาโลพอด)','Cephalopods','Cephalopoda','class',MOLL,'หมึก|ปลาหมึก'),
 ('insects','แมลง','Insects','Insecta','class',ARTH,''),
 ('shrimps','กุ้ง (กลุ่มทั่วไป)','Shrimps and prawns','','informal group',ARTH,'กุ้ง'),
 ('spiders','แมงมุม','Spiders','Araneae','order',ARTH,''),
 ('centipedes','ตะขาบ','Centipedes','Chilopoda','class',ARTH,''),
 ('starfish','ปลาดาว','Sea stars','Asteroidea','class',ECH,'ลาดาว|ดาวทะเล'),
 ('urchins','เม่นทะเล','Sea urchins','Echinoidea','class',ECH,''),
 ('cucumbers','ปลิงทะเล','Sea cucumbers','Holothuroidea','class',ECH,'ปิงทะเล'),
 ('fishes','ปลา (กลุ่มทั่วไป)','Fishes','','informal group',VERT,'ปลา'),
 ('amphibians','สัตว์สะเทินน้ำสะเทินบก','Amphibians','Amphibia','class',VERT,''),
 ('frogs','กบ (กลุ่มกบและคางคก)','Frogs and toads','Anura','order',VERT,'กบ'),
 ('reptiles','สัตว์เลื้อยคลาน (กลุ่มดั้งเดิม)','Non-avian reptiles','','informal group',VERT,'สัตว์เลื้อยคลาน'),
 ('snakes','งู','Snakes','Serpentes','suborder',VERT,''),
 ('crocodilians','จระเข้ (กลุ่มคร็อกโคดิเลียน)','Crocodilians','Crocodylia','order',VERT,'จระเข้'),
 ('birds','สัตว์ปีก (นก)','Birds','Aves','class',VERT,'นก|สัตว์ปีก'),
 ('mammals','สัตว์เลี้ยงลูกด้วยน้ำนม','Mammals','Mammalia','class',VERT,'สัตว์เลี้ยงลูกด้วยน้ำนม (รวมถึงมนุษย์)'),
]

def make(slug, thai, english, scientific, rank, kingdom, vector, source, scope, aliases='', uncertainty=''):
    row=dict.fromkeys(json.loads((BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))[0], '')
    row.update(id='request-'+slug,thai_name=thai,english_name=english,scientific_name=scientific,
               rank=rank,Kingdom=kingdom,aliases=aliases,scope='ขอบเขต: '+scope,
               uncertainty=uncertainty or 'รายการระดับกลุ่มหรือขอบเขตที่ระบุ ไม่ใช่การระบุชนิดของตัวอย่างจริง',
               name_sources=source,feature_sources='|'.join(dict.fromkeys([CELL, {'Animalia':ANIMAL,'Fungi':FUNGI,'Plantae':PLANT,'Protista':ALGAE,'Monera':ALGAE}[kingdom],source])),
               evidence_basis='Reviewed requested catalogue; group-level inference with explicit scope and unknowns; no specimen measurement or occurrence claim',verified_on='2026-10-29')
    notes={
        'Animalia':['เซลล์ร่างกายตัวแทนที่มีชีวิตมีไรโบโซม','เซลล์เจ้าบ้านไม่สังเคราะห์แสง ไม่รวมสิ่งมีชีวิตร่วมอาศัย','เซลล์ร่างกายตัวแทนมีนิวเคลียส','เซลล์สัตว์ไม่มีผนังเซลล์ เปลือกหรือคิวติเคิลไม่ใช่ผนังเซลล์','เซลล์เจ้าบ้านไม่มีคลอโรพลาสต์','ตัวสัตว์ระยะวัยอ่อนหรือโตเต็มวัยมีหลายเซลล์'],
        'Fungi':['เซลล์ราระยะเจริญมีไรโบโซม','ราไม่สังเคราะห์แสง ไม่รวมคู่ร่วมอาศัย','เซลล์ราระยะเจริญมีนิวเคลียส','เซลล์ราระยะเจริญมีผนังเซลล์','เซลล์ราไม่มีคลอโรพลาสต์','เส้นใยหรือดอกเห็ดหลายเซลล์ตามขอบเขตที่ระบุ'],
        'Plantae':['เซลล์พืชที่มีชีวิตมีไรโบโซม','ประเมินความสามารถของใบสีเขียวเมื่อรับแสง','เซลล์พืชตัวแทนมีนิวเคลียส','เซลล์พืชตัวแทนมีผนังเซลล์','ประเมินคลอโรพลาสต์ในใบสีเขียว ไม่ใช่ทุกอวัยวะ','ต้นพืชประกอบด้วยหลายเซลล์'],
        'Protista':['เซลล์มีไรโบโซม','ประเมินสาหร่ายสีเขียวที่สังเคราะห์แสง','เซลล์ยูคาริโอตมีนิวเคลียส','ผนังเซลล์แปรตามกลุ่มและระยะ','เซลล์สีเขียวมีคลอโรพลาสต์','มีทั้งเซลล์เดียว โคโลนี และหลายเซลล์'],
        'Monera':['เซลล์แบคทีเรียมีไรโบโซม','ไซยาโนแบคทีเรียสังเคราะห์แสง','โพรคาริโอตไม่มีนิวเคลียสที่มีเยื่อหุ้ม','เซลล์ตัวแทนมีผนังเซลล์','การสังเคราะห์แสงไม่ใช้คลอโรพลาสต์','มีทั้งเซลล์เดี่ยวและเส้นสาย ขึ้นกับนิยามจำนวนเซลล์'],
    }[kingdom]
    for f,v,n in zip(F,vector,notes):
        row[f]=str(v)
        row[f+'_evidence']=('Unknown: ไม่สรุปรวมทั้งกลุ่มหรือยังไม่มีหลักฐานในขอบเขตนี้; ' if v=='' else 'อนุมานระดับกลุ่ม: ')+n+'; '+row['feature_sources'].replace('|',' ; ')
    return row

def reviewed_records():
    result=[]
    for slug,th,en,sci,rank,src,aliases in ANIMALS:
        scope='รายการระดับ'+('ชนิด' if rank=='species' else 'กลุ่ม')+' '+th+'; ใช้ตัวสัตว์วัยอ่อนหรือโตเต็มวัยและเซลล์ร่างกายที่มีนิวเคลียส ไม่รวมเซลล์สืบพันธุ์ เซลล์พิเศษ และสาหร่ายหรือจุลชีพร่วมอาศัย'
        if slug=='worms': scope+='; คำว่าพยาธิในรายการนี้หมายถึงหนอนปรสิต ไม่รวมโพรโทซัว'
        if slug=='corals': scope+='; รวมปะการังหลายกลุ่ม ไม่ได้หมายถึงชนิดเดียว'
        if slug=='shellfish': scope+='; หมายถึงหอยฝาเดียว หอยสองฝา และกลุ่มมีเปลือก ไม่เหมารวมว่าหอยทุกชนิดมีเปลือก'
        result.append(make(slug,th,en,sci,rank,'Animalia',[1,0,1,0,0,1],src,scope,aliases))
    result.extend([
      make('basella','ผักปลัง','Ceylon spinach','Basella alba','species','Plantae',[1,1,1,1,1,1],
           'https://qsds.go.th/newqssccpn/wp-content/uploads/sites/99/2018/12/120.Ceylon-spinach.pdf','ต้นผักปลังและเซลล์ใบสีเขียวระยะเจริญเมื่อได้รับแสง ไม่ใช่ทุกเซลล์หรือเมล็ด','ผักปั๋ง|ผักปัง|ผักปลังขาว|ผักปลังแดง'),
      make('bamboo-shoots','หน่อไม้ (หน่ออ่อนของไผ่)','Bamboo shoots','','informal group','Plantae',[1,'',1,1,'',1],
           'https://www.hkzbg.gov.hk/en/plants/thematic/bamboo.html','หน่ออ่อนของไผ่หลายชนิด ไม่ใช่สิ่งมีชีวิตคนละชนิดกับต้นไผ่; ยังไม่สรุปการสังเคราะห์แสงหรือคลอโรพลาสต์ของหน่อที่อาจอยู่ใต้ดิน','หน่อ|หน่อไม้|ไผ่ (หน่ออ่อน)'),
      make('flowering-plants','พืชดอก (กลุ่มทั่วไป)','Flowering plants','Angiosperms','clade','Plantae',[1,'',1,1,'',1],BIO+'26-3-angiosperms','กลุ่มพืชดอกโดยรวม รวมชนิดปรสิตที่อาจไม่สังเคราะห์แสง จึงไม่ใส่ค่าการสังเคราะห์แสงและคลอโรพลาสต์เหมารวม','พืชดอก'),
      make('fungi','เชื้อรา (กลุ่มทั่วไป)','Fungi','Fungi','kingdom','Fungi',[1,0,1,1,0,''],FUNGI,'กลุ่มราโดยรวม มีทั้งยีสต์เซลล์เดียวและราเส้นใยหลายเซลล์ ไม่รวมสิ่งมีชีวิตที่เพียงมีชื่อเรียกว่าราแต่ไม่ใช่ Fungi','เชื้อรา'),
      make('molds','รา (รูปแบบเส้นใย)','Filamentous molds','','growth form','Fungi',[1,0,1,1,0,''],FUNGI,'รูปแบบราเส้นใยระยะเจริญ มีทั้งเส้นใยมีผนังกั้นและเส้นใยร่วมไซโทพลาซึม จึงไม่สรุปจำนวนเซลล์ค่าเดียว ไม่ครอบคลุมราน้ำและราเมือกที่ไม่ใช่ Fungi','รา|ราเส้นใย'),
      make('het-lom','เห็ดหล่ม (กลุ่มชื่อท้องถิ่น)','Het lom mushrooms','Russula spp.','genus (species unresolved)','Fungi',[1,0,1,1,0,1],
           'https://www.cmu.ac.th/th/article/0ca5b227-e1e2-448c-88f4-cdd6cf1b5f0b','ชื่อท้องถิ่นครอบคลุมเห็ด Russula หลายชนิด เช่น เห็ดหล่มหลังขาวและหลังเขียว ไม่ระบุเป็น Russula virescens โดยไม่มีตัวอย่าง; ใช้ระยะเส้นใยและดอกเห็ด','เห็ดหล่ม|เห็ดไคล|เห็ดตะไคล'),
      make('suk-sun','ซุกซุ่น','Suk sun fungus','Scorias sp.','genus (species unresolved)','Fungi',[1,0,1,1,0,1],
           'https://archive.lib.cmu.ac.th/full/T/2558/micro71058sst_ch5.pdf',
           'รา Scorias sp. ตามงานวิจัยเห็ดซุกซุ่นของมหาวิทยาลัยเชียงใหม่ หน้า 77; ประเมินระยะเส้นใยที่มีผนังกั้นตามขวาง จึงมีหลายเซลล์ ไม่ใช้ conidium ซึ่งเป็นสปอร์เซลล์เดียวเป็นตัวแทน ไม่ระบุเป็น Scorias spongiosa เพราะงานวิจัยยังแยกไว้เพียงระดับสกุล','ยุกยุ่น|อีหยุ่น|ซุกซุ่น|เห็ดซุกซุ่น|เห็ดเพลี้ยไม้ไผ่',
           'CMU thesis identifies local suk sun as Scorias sp. and documents septate hyphae (p.77). Species not resolved; six traits describe vegetative mycelium, not unicellular conidia.'),
      make('green-algae','สาหร่ายสีเขียว (กลุ่มทั่วไป)','Green algae','','informal group','Protista',[1,1,1,'',1,''],ALGAE,'กลุ่มสาหร่ายสีเขียวตามระบบ 5 อาณาจักรของโครงงาน ไม่รวมพืชบก; มีเซลล์เดียว โคโลนี และหลายเซลล์ ผนังเซลล์และจำนวนเซลล์จึงไม่สรุปเป็นค่าเดียว','สาหร่ายสีเขียว'),
      make('cyanobacteria','สาหร่ายสีเขียวแกมน้ำเงิน','Cyanobacteria','Cyanobacteria','phylum','Monera',[1,1,0,1,0,''],
           'https://naturalhistory.si.edu/research/botany/research/algae/algae-classification','ไซยาโนแบคทีเรียตามระบบ Monera ของโครงงาน เป็นแบคทีเรียสังเคราะห์แสง ไม่ใช่สาหร่ายยูคาริโอต; มีทั้งเซลล์เดี่ยวและเส้นสาย ไม่สรุปจำนวนเซลล์ค่าเดียว','สาหร่ายสีเขียวน้ำเงิน|สาหร่ายสีเขียว น้ำเงิน|สาหร่ายสีน้ำเงินแกมเขียว|ไซยาโนแบคทีเรีย'),
    ])
    return {r['id']:r for r in result}

NAME_UPDATES = {
 'train-04': ('ดอกไม้ทะเล',['ดอกไม้ทะเล']),
 'train-05': ('พยาธิใบไม้',['พยาธิใบไม้']),
 'train-09': ('ยีสต์',['ยีสต์']),
 'train-23': ('ยูกลีนา',['ยูกลีนา','ยูกลีนา กราซิลิส']),
 'train-27': ('ไฮดรา',['ไฮดรา']),
 'gbif-2436436': ('มนุษย์',['คน']),
}

def apply_requested(rows, report):
    for row in rows:
        if row['id'] in NAME_UPDATES:
            th,aliases=NAME_UPDATES[row['id']]
            row['thai_name']=th
            row['aliases']='|'.join(dict.fromkeys(n for n in row['aliases'].split('|')+aliases if n and n!=th))
            audit=next(a for a in report if a['id']==row['id'])
            audit['requested_name_review']={'date':'2026-10-29','basis':'Thai search labels for existing named taxon; identity and features unchanged','aliases':aliases}
            audit['after']=dict(row)
    ids={r['id'] for r in rows}
    scientific={r['scientific_name'].casefold() for r in rows if r['scientific_name']}
    for row in reviewed_records().values():
        if row['id'] in ids: continue
        if row['scientific_name'] and row['scientific_name'].casefold() in scientific:
            raise ValueError('Requested taxon already exists: '+row['scientific_name'])
        rows.append(row)
        report.append(dict(id=row['id'],status='reviewed_group_or_scoped_reference',issues=[row['uncertainty']],
                           before=None,after=dict(row),review_basis='requested_catalog',review_sources=row['name_sources'].split('|')))
        ids.add(row['id'])
        if row['scientific_name']: scientific.add(row['scientific_name'].casefold())

if __name__=='__main__':
    raise SystemExit('Review records here; apply with source_catalog.py --promote, then build_catalog.py')
