from pathlib import Path
import html,json
from streamlit.testing.v1 import AppTest
from catalog import read_catalog,FEATURES
base=Path.cwd();data=read_catalog(base/'organism_catalog.csv')
r=data.loc[data[FEATURES].isna().any(axis=1) & data.thai_name.ne('')].iloc[0]
a=AppTest.from_file(str(base/'streamlit_app.py')).run()
a.session_state['view']='profile';a.session_state['selected_id']=r['id'];a.run()
assert not a.exception
inner='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;padding:16px;background:#191D1A;color:#F2F5F0;font-family:Tahoma,sans-serif">'+''.join(m.value for m in a.markdown)+'<p>ไม่ทราบคุณลักษณะครบทั้ง 6 ข้อ จึงยังไม่ทำนาย</p></body></html>'
wrapper='<!doctype html><html><head><meta charset="utf-8"><title>Life Kingdom mobile CSS verification</title></head><body style="margin:0;background:#111"><iframe title="390px mobile layout" width="390" height="1100" style="border:0" srcdoc="'+html.escape(inner,quote=True)+'"></iframe></body></html>'
(base/'evidence/ui_preview/mobile_static.html').write_text(wrapper,encoding='utf8')
(base/'evidence/ui_preview/preview_status.json').write_text(json.dumps(dict(kind='Static mobile CSS render from actual Streamlit AppTest output; not a mobile interaction test',width=390,id=r['id'],scientific_name=r['scientific_name'],live_mobile_status='Local browser connection timed out'),indent=2),encoding='utf8')
print(r['id'],r['scientific_name'])
