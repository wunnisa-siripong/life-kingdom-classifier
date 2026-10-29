import json,datetime,subprocess
from pathlib import Path
base=Path('.')
sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
d=dict(url='https://life-kingdom-wunnisa.streamlit.app/',branch='main',deployed_code_commit=sha,push_status='confirmed',checked_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),live_status='verified',observed_catalog_count=417,checks=['Homepage displays 417 catalogue entries','Scientific-name search Pterocarpus macrocarpus returns new Thai-labelled entry','Selected profile shows unknown Photosynthesis and Chloroplast','Unknown profile displays prediction-withheld message','Live 319px-wide viewport visually checked; unknown feature text wraps inside cards after CSS fix'],mobile_scope='Narrow browser viewport 319px; not a physical-device test',limitations=['Legacy per-trait evidence not fully independently reverified','15 existing taxonomy records remain unresolved','No new Protista/Monera entries','Some source URLs remain inaccessible to automated link checking'])
(base/'evidence/catalog_audit/deployment.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
p=base/'CATALOG_AUDIT_TH.md';s=p.read_text(encoding='utf-8-sig');a=s.index('AppTest ตรวจ UI');b=s.index('\n## ไฟล์สำคัญ',a)
s=s[:a]+'''AppTest ตรวจ UI และโปรไฟล์ผ่าน 10 ชุด เพิ่ม regression test ที่เปลี่ยน CSV แล้วตรวจจำนวนบนหน้าจอ เพื่อป้องกันแคชเก่า แคชใช้ SHA-256 ของ CSV เป็นคีย์แล้ว

ตรวจเว็บจริงหลัง push: หน้าแรกแสดง 417 รายการ ค้น Pterocarpus macrocarpus พบรายการใหม่ เปิดโปรไฟล์ที่แสดง Photosynthesis/Chloroplast ว่าไม่ทราบ และแสดงข้อความงดทำนายได้จริง

ตรวจภาพจริงบน viewport กว้าง 319px พบข้อความ unknown ล้นการ์ดในครั้งแรก แก้เฉพาะ white-space/min-width/overflow-wrap ภายใน media query มือถือแล้ว ตรวจซ้ำเห็นข้อความตัดบรรทัดอยู่ในกรอบ เป็นการตรวจหน้าจอเบราว์เซอร์แคบ ไม่ใช่การทดสอบอุปกรณ์มือถือจริงทุกขนาด

เว็บทดสอบ localhost และไฟล์ HTML เคยติดข้อจำกัด จึงตรวจจากเว็บสาธารณะที่ deploy จริงแทน HTML ตัวอย่าง 390px ใน evidence/ui_preview ไม่ใช่หลักฐานภาพที่ผ่านการตรวจ สถานะเผยแพร่และขอบเขตการตรวจจริงอยู่ evidence/catalog_audit/deployment.json
''' + s[b:]
p.write_bytes(s.encode('utf8'))
p=base/'evidence/catalog_audit/test_verification.json';d=json.loads(p.read_text(encoding='utf8'));d['mobile_browser']='Live 319px viewport visually verified after unknown-label wrap fix; physical devices not tested';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
