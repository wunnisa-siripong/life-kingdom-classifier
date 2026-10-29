"""Small, sourced profile overlay; never modifies catalogue traits or predictions.

Image/taxon/license pages checked 2026-10-28. Images are displayed unedited
(scaled to fit); Wikimedia hosts the originals. Spirogyra is genus-level.
"""
PROFILES = {
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
