from pathlib import Path
import platform
import joblib
import pandas as pd
import sklearn
import streamlit as st
from catalog import FEATURES, read_catalog, search, option_label, prediction_input

st.set_page_config(page_title="Life Kingdom",page_icon="🌿",layout="centered")
BASE=Path(__file__).resolve().parent
LABELS=dict(zip(FEATURES,["มีไรโบโซม","สังเคราะห์แสงได้","มีนิวเคลียส","มีผนังเซลล์","มีคลอโรพลาสต์","มีหลายเซลล์"]))

@st.cache_resource
def load_model():
    package=joblib.load(BASE/"life_kingdom_model.joblib")
    model,columns=package["model"],list(package["features"])
    prediction_input(dict.fromkeys(FEATURES,1),columns)
    if not hasattr(model,"tree_"): raise ValueError("โมเดลต้องเป็น Decision Tree")
    return model,columns

@st.cache_data
def load_data():
    return read_catalog(BASE/"organism_catalog.csv"),pd.read_csv(BASE/"organisms.csv",encoding="utf-8-sig")

from ui import CSS, LABELS, ICONS, profile, feature_cards, prediction, evidence
st.markdown(CSS,unsafe_allow_html=True)
st.markdown('<div class="lk-kicker">EXPLORE THE LIVING WORLD</div>',unsafe_allow_html=True)
st.title("Life Kingdom")
st.markdown('<p class="lk-intro">โลกของสิ่งมีชีวิต เริ่มจากความสงสัยเล็ก ๆ<br>ค้นหาชื่อ หรือสำรวจผ่านคุณลักษณะทั้ง 6</p>',unsafe_allow_html=True)
try:
    model,model_columns=load_model()
    catalog,training=load_data()
except Exception as error:
    st.error("โหลดข้อมูลหรือโมเดลไม่สำเร็จ กรุณาตรวจการติดตั้งและไฟล์บน GitHub")
    st.exception(error)
    st.stop()

tab1,tab2=st.tabs(["ค้นหาสิ่งมีชีวิต","กำหนดคุณลักษณะเอง"])
with tab1:
    st.caption("ค้นด้วยชื่อไทย อังกฤษ วิทยาศาสตร์ หรือชื่อเรียกอื่น")
    # Keep aliases searchable without appending them to every suggestion.
    query=st.text_input("ค้นหาชื่อสิ่งมีชีวิต",placeholder="เช่น มะม่วง, cat, Spirogyra")
    matches=search(catalog,query) if query.strip() else catalog
    options={option_label(r):r['id'] for _,r in matches.iterrows()}
    row=None
    if query.strip() and not options:
        st.info("ไม่พบชื่อนี้ในแค็ตตาล็อก ลองชื่ออื่น หรือใช้แท็บกำหนดคุณลักษณะเอง")
    elif query.strip() and len(options)==1:
        row=matches.iloc[0]
    else:
        chosen=st.selectbox("เลือกรายการ",list(options),index=None,placeholder="เลือกสิ่งมีชีวิตเพื่อเริ่มสำรวจ")
        if chosen: row=catalog.loc[catalog['id'].eq(options[chosen])].iloc[0]
    if row is not None:
        profile(row)
        feature_cards(row)
        prediction(row,model,model_columns,row['Kingdom'])
        evidence(row,model_columns)
    else:
        st.caption("117 รายการในแค็ตตาล็อก · เลือกชื่อเพื่อดูโปรไฟล์และผลทำนาย")
    with st.expander("ดูรายชื่อทั้งหมด / ดาวน์โหลดแค็ตตาล็อก"):
        st.dataframe(catalog[["thai_name","english_name","scientific_name","Kingdom"]],hide_index=True,use_container_width=True)
        st.download_button("ดาวน์โหลด CSV พร้อมแหล่งอ้างอิง",(BASE/"organism_catalog.csv").read_bytes(),file_name="organism_catalog.csv",mime="text/csv")

def clear_manual():
    for i in range(6): st.session_state[f'feature_{i}']=None
    st.session_state.pop('manual_values',None)
    st.session_state.pop('manual_incomplete',None)

def changed_manual():
    st.session_state.pop('manual_values',None)
    st.session_state.pop('manual_incomplete',None)

with tab2:
    st.caption("เลือกคำตอบทั้ง 6 ข้อ แล้วให้โมเดลช่วยจำแนกอาณาจักร")
    complete=sum(st.session_state.get(f'feature_{i}') is not None for i in range(6))
    st.markdown(f'**เลือกแล้ว {complete}/6 ข้อ**')
    answers={f:st.radio(f'{ICONS[f]}  {LABELS[f]}',["ใช่","ไม่ใช่"],index=None,horizontal=True,key=f'feature_{i}',on_change=changed_manual,width='stretch') for i,f in enumerate(FEATURES)}
    left,right=st.columns([2,1])
    predict=left.button("ทำนายอาณาจักร",type="primary",use_container_width=True)
    right.button("ล้างคำตอบ",on_click=clear_manual,use_container_width=True)
    if predict:
        if any(v is None for v in answers.values()): st.session_state['manual_incomplete']=True
        else: st.session_state['manual_values']={f:int(v=="ใช่") for f,v in answers.items()}
    if st.session_state.get('manual_incomplete'): st.warning("กรุณาเลือกคุณลักษณะให้ครบทั้ง 6 ข้อ")
    if answers['Ribosome']=='ไม่ใช่':
        st.info("สิ่งมีชีวิตที่เป็นเซลล์ต้องมีไรโบโซม ชุดคำตอบนี้อาจไม่สอดคล้องทางชีววิทยา แต่ยังทดลองทำนายได้")
    if 'manual_values' in st.session_state:
        prediction(st.session_state['manual_values'],model,model_columns)
    st.caption("ผลขึ้นอยู่กับคุณลักษณะที่เลือก โมเดลไม่ได้ตรวจความเป็นไปได้ทางชีววิทยาของทุกชุดคำตอบ")

with st.expander("เกี่ยวกับข้อมูลและโมเดล"):
    st.write(f"แค็ตตาล็อกค้นหา {len(catalog)} รายการ แยกจากข้อมูลฝึกเดิม {len(training)} แถว")
    st.write("ค่าอ้างอิงใช้ระยะชีวิต/ชนิดเซลล์ที่ระบุ ไม่ใช่ทุกเซลล์ทุกสภาวะ; ค่าที่ไม่ทราบจะไม่แทนด้วย 0 และไม่ส่งทำนาย")
    st.caption("ชื่อไทยมีเฉพาะที่พบหลักฐาน ไม่ได้แปลหรือเดาให้ครบทุกชนิด คุณลักษณะของรายการพืช/สัตว์ใหม่เป็นการอนุมานระดับกลุ่มโดยเปิดเผยแหล่งข้อมูล")
    st.caption("ยังไม่รวม Rhizopus, Slime mold และ Red tube coral ในแค็ตตาล็อก เพราะนิยามหลายเซลล์/ชื่อกำกวม แต่คงอยู่ในข้อมูลฝึกเดิม")
    st.caption("ไม่ได้ฝึกโมเดลใหม่หรือแก้ไฟล์โมเดลเดิม · ยังไม่มีผลประเมินความแม่นยำกับรายการใหม่")
    st.caption(f"Python {platform.python_version()} · scikit-learn {sklearn.__version__} · Streamlit {st.__version__} · catalog 2026-10-27")
