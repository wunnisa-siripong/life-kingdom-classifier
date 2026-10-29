"""Sourced profiles; image rights and taxonomy remain auditable per catalogue ID.

Image/taxon/license pages checked 2026-10-28. Images are displayed unedited
(scaled to fit); Wikimedia hosts the originals. Spirogyra is genus-level.
"""
PROFILES = {
    'catalog:request-bamboo-shoots': {
        'description':'หน่อไม้คือหน่ออ่อนของไผ่ ซึ่งเป็นพืชในวงศ์หญ้า (Poaceae) ไม่ใช่สิ่งมีชีวิตคนละชนิดกับต้นไผ่ หน่อที่กำลังยืดตัวได้รับสารอาหารจากต้นแม่ผ่านเหง้า ส่วนใบสีเขียวของต้นไผ่มีคลอโรพลาสต์และสังเคราะห์แสงได้ ค่าทั้ง 6 ข้อในหน้านี้ใช้ต้นไผ่ระยะมีใบสีเขียวเป็นตัวแทน จึงไม่หมายความว่าหน่อใต้ดินทุกเซลล์สังเคราะห์แสงได้',
        'facts':['วงศ์ Poaceae','หน่ออ่อนของต้นไผ่','ประเมินต้นไผ่ระยะมีใบสีเขียว'],
        'source':'https://www.nature.com/articles/srep25908',
        'source_label':'Scientific Reports · การส่งคาร์โบไฮเดรตจากต้นแม่สู่หน่อไผ่',
    },
    'Russula spp.': {
        'description':'เห็ดหล่มเป็นชื่อท้องถิ่นที่ใช้กับเห็ดหลายชนิดในสกุล Russula ไม่ใช่ชื่อของชนิดเดียว งานวิจัยมหาวิทยาลัยเชียงใหม่แยกเห็ดหล่มหลังขาวและหลังเขียวเป็นคนละชนิดด้วยข้อมูลสัณฐานวิทยาและดีเอ็นเอ เห็ดกลุ่มนี้อยู่ในอาณาจักร Fungi ไม่มีคลอโรพลาสต์ และไม่สังเคราะห์แสง ค่าหลายเซลล์ในหน้านี้หมายถึงระยะเส้นใยและดอกเห็ด',
        'facts':['สกุล Russula','ชื่อท้องถิ่นครอบคลุมหลายชนิด','ระยะเส้นใยและดอกเห็ดหลายเซลล์'],
        'source':'https://www.cmu.ac.th/th/article/0ca5b227-e1e2-448c-88f4-cdd6cf1b5f0b',
        'source_label':'มหาวิทยาลัยเชียงใหม่ · งานวิจัยเห็ดหล่มหลังขาวและหลังเขียว',
    },
    'Scorias sp.': {
        'description':'ซุกซุ่นเป็นชื่อท้องถิ่นของรา Scorias sp. งานวิจัยของมหาวิทยาลัยเชียงใหม่รายงานว่าเป็นราในไฟลัม Ascomycota มีเส้นใยหนา เนื้อเหนียว และมีผนังกั้นตามขวาง โคโลนีอ่อนสีเขียวอ่อนและเข้มขึ้นเมื่อแก่ ไม่ใช่พืชและไม่สังเคราะห์แสง',
        'facts':['อาณาจักร Fungi','ระยะเส้นใยมีหลายเซลล์','ระบุระดับสกุล Scorias'],
        'source':'https://archive.lib.cmu.ac.th/full/T/2558/micro71058sst_ch5.pdf',
        'source_label':'คลังวิทยานิพนธ์ มหาวิทยาลัยเชียงใหม่ · บทที่ 5 หน้า 77',
    },
    'Mangifera indica': {
        'image':'https://upload.wikimedia.org/wikipedia/commons/9/9c/Starr_071024-0216_Mangifera_indica.jpg',
        'alt':'ผลมะม่วง Mangifera indica บนต้น',
        'credit':'Forest & Kim Starr',
        'license':'CC BY 3.0',
        'license_url':'https://creativecommons.org/licenses/by/3.0/',
        'image_source':'https://commons.wikimedia.org/wiki/File:Starr_071024-0216_Mangifera_indica.jpg',
        'description':'มะม่วงเป็นไม้ยืนต้นเขตร้อน มีทรงพุ่มกว้าง ใบเรียวยาว และผลที่รับประทานได้',
        'facts':['วงศ์ Anacardiaceae','ใบเรียงสลับ มักกระจุกบริเวณปลายกิ่ง'],
        'source':'https://ntbg.org/database/plants/detail/mangifera-indica',
        'source_label':'National Tropical Botanical Garden',
    },
    'Felis catus': {
        'image':'https://upload.wikimedia.org/wikipedia/commons/9/90/Felis_catus_%28cat%29.jpg',
        'alt':'แมวบ้าน Felis catus',
        'credit':'Clumsyninja',
        'license':'CC BY-SA 4.0',
        'license_url':'https://creativecommons.org/licenses/by-sa/4.0/',
        'image_source':'https://commons.wikimedia.org/wiki/File:Felis_catus_(cat).jpg',
        'description':'แมวบ้านเป็นสัตว์เลี้ยงลูกด้วยนมในวงศ์แมว เป็นผู้ล่าที่กินอาหารจากสัตว์เป็นหลัก',
        'facts':['วงศ์ Felidae','ออกลูกเป็นตัวและเลี้ยงลูกด้วยน้ำนม'],
        'source':'https://animaldiversity.org/accounts/Felis_catus/',
        'source_label':'Animal Diversity Web · University of Michigan',
    },
    'Spirogyra spp.': {
        'image':'https://upload.wikimedia.org/wikipedia/commons/9/92/Single_strand_chloroplast_in_Spirogyra.jpg',
        'alt':'ภาพจุลทรรศน์ Spirogyra เห็นคลอโรพลาสต์เป็นเกลียว',
        'credit':'Krishna satya 333',
        'license':'CC0 1.0',
        'license_url':'https://creativecommons.org/publicdomain/zero/1.0/',
        'image_source':'https://commons.wikimedia.org/wiki/File:Single_strand_chloroplast_in_Spirogyra.jpg',
        'description':'สไปโรไจราเป็นสาหร่ายสีเขียวแบบเส้นสาย มีคลอโรพลาสต์เรียงเป็นเกลียวซึ่งสังเกตได้ด้วยกล้องจุลทรรศน์',
        'facts':['ข้อมูลระดับสกุล ไม่ระบุชนิด','คลอโรพลาสต์เป็นเกลียวอยู่ภายในแต่ละเซลล์'],
        'source':'https://www.jircas.go.jp/project/aquacult_Thailand/data/spirogyra_sp1.html',
        'source_label':'JIRCAS · สาหร่ายน้ำจืดในประเทศไทย',
    },
}

# Generated source-matched photos/basic profiles, supplemented by reviewed Thai text.
import json
from pathlib import Path
_profile_path=Path(__file__).resolve().parent/'organism_profiles.json'
PROFILE_BY_ID=json.loads(_profile_path.read_text(encoding='utf8')) if _profile_path.exists() else {}

def profile_for(row):
    generated=dict(PROFILE_BY_ID.get(str(row['id']),{}))
    reviewed=PROFILES.get('catalog:'+str(row['id'])) or PROFILES.get(str(row['scientific_name'])) or {}
    if reviewed.get('image') and not (generated.get('reviewed_image_cached') and generated.get('image_original')==reviewed['image']):
        # Preserve approved existing images together with their own matching credits.
        for key in ['image_local','image_caption','image_changes','image_taxon']:
            generated.pop(key,None)
    generated.update(reviewed)
    return generated or None
