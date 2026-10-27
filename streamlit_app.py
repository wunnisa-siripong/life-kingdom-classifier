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

st.markdown("""<style>
.stApp {background:#191c1a;color:#f6f7f5;}
.block-container {max-width:780px;padding-top:2rem;padding-bottom:2rem;}
[data-testid="stHeader"] {background:#191c1a;}
div[data-testid="stFormSubmitButton"] button {border-radius:24px;width:100%;}
[data-testid="stMetric"] {background:#232924;padding:12px;border-radius:12px;}
@media(max-width:600px){.block-container{padding:1.1rem;}h1{font-size:2rem!important;}
[data-baseweb="tab-list"]{gap:0.6rem;}[data-baseweb="tab"]{font-size:0.9rem;}}
</style>""",unsafe_allow_html=True)
st.title("🌿 Life Kingdom")
st.write("ค้นพบสิ่งมีชีวิต · เข้าใจการตัดสินใจของโมเดล")
try:
    model,model_columns=load_model()
    catalog,training=load_data()
except Exception as error:
    st.error("โหลดข้อมูลหรือโมเดลไม่สำเร็จ กรุณาตรวจการติดตั้งและไฟล์บน GitHub")
    st.exception(error)
    st.stop()

st.caption(f"{len(catalog)} รายการ · ระบบห้าอาณาจักรของโครงงาน · Decision Tree เดิมจาก Colab")
last_input=None

def show_prediction(values,reference=None):
    global last_input
    try: X=prediction_input(values,model_columns)
    except ValueError as error:
        st.warning(str(error));return
    result=str(model.predict(X)[0])
    last_input=X
    if reference:
        left,right=st.columns(2)
        left.metric("ตามข้อมูลอ้างอิง",reference)
        right.metric("โมเดลทำนาย",result)
        if result!=reference:
            st.warning(f"ผลต่างกัน: ข้อมูลอ้างอิงระบุ {reference} แต่โมเดลทำนาย {result} คุณลักษณะทั้ง 6 อาจเหมือนกันในต่างอาณาจักร โมเดลนี้จึงแยกไม่ได้ทุกกรณี")
    else: st.success(f"ผลการทำนาย: {result}")
    return result

tab1,tab2=st.tabs(["ค้นหาสิ่งมีชีวิต","กำหนดคุณลักษณะเอง"])
with tab1:
    st.caption("พิมพ์ชื่อไทย อังกฤษ วิทยาศาสตร์ หรือชื่อเรียกอื่น แล้วเลือกจากคำแนะนำ ไม่สนตัวพิมพ์ใหญ่เล็ก")
    options={option_label(row):row["id"] for _,row in catalog.iterrows()}
    chosen=st.selectbox("ชื่อสิ่งมีชีวิต",list(options),index=None,
        placeholder="เช่น มะม่วง, Rice, Felis catus, Spirogyra",accept_new_options=True)
    row=None
    if chosen:
        if chosen in options:
            row=catalog.loc[catalog["id"].eq(options[chosen])].iloc[0]
        else:
            matches=search(catalog,chosen)
            if len(matches)==1: row=matches.iloc[0]
            elif len(matches)>1:
                st.info("ชื่อนี้ตรงกับหลายรายการ โปรดเลือกชื่อวิทยาศาสตร์เพื่อระบุให้ชัดเจน")
                choice=st.selectbox("เลือกรายการที่ต้องการ",[option_label(r) for _,r in matches.iterrows()],index=None)
                if choice: row=catalog.loc[catalog["id"].eq(options[choice])].iloc[0]
            else: st.warning("ไม่พบชื่อนี้ในแค็ตตาล็อก ลองชื่ออื่น หรือใช้โหมดกำหนดคุณลักษณะเอง")
    if row is not None:
        st.subheader(row["thai_name"] or row["english_name"] or row["scientific_name"])
        st.write(row["scientific_name"])
        if row["english_name"]: st.caption(row["english_name"]+" · ระดับ: "+row["rank"])
        st.caption("ขอบเขต: "+row["scope"])
        st.dataframe(pd.DataFrame({"คุณลักษณะ":[LABELS[f] for f in model_columns],
            "ค่า (1=ใช่, 0=ไม่ใช่)":[str(row[f]) if pd.notna(row[f]) else "ไม่ทราบ" for f in model_columns]}),
            hide_index=True,use_container_width=True)
        show_prediction(row,row["Kingdom"])
        with st.expander("หลักฐานและข้อจำกัดของรายการนี้"):
            st.write(row["uncertainty"])
            st.caption(row["evidence_basis"]+" · วันที่ตรวจหลักฐาน: "+row["verified_on"])
            for f in model_columns: st.write(f"• {LABELS[f]}: {row[f+'_evidence']}")
            for title,key in [("แหล่งชื่อและอนุกรมวิธาน","name_sources"),("แหล่งคุณลักษณะ","feature_sources")]:
                st.write(title)
                for i,url in enumerate(dict.fromkeys(row[key].split("|")),1):
                    if url.startswith("https://"): st.link_button(f"{title} {i}",url)
            st.caption("Protista และ Monera เป็นป้ายตามระบบห้าอาณาจักรของโครงงาน ไม่ใช่อาณาจักรสมัยใหม่จาก GBIF; ชื่ออ้างอิงไม่ใช่การพิสูจน์ชนิดตัวอย่างจริง")
    with st.expander("ดูรายชื่อทั้งหมด / ดาวน์โหลดแค็ตตาล็อก"):
        st.dataframe(catalog[["thai_name","english_name","scientific_name","Kingdom"]],hide_index=True,use_container_width=True)
        st.download_button("ดาวน์โหลด CSV พร้อมแหล่งอ้างอิง",(BASE/"organism_catalog.csv").read_bytes(),file_name="organism_catalog.csv",mime="text/csv")

with tab2:
    st.caption("1 = ใช่ · 0 = ไม่ใช่ · เลือกให้ครบทั้ง 6 ข้อ โมเดลไม่ได้ตรวจความเป็นไปได้ทางชีววิทยาของชุดคำตอบ")
    with st.form("feature_form"):
        answers={f:st.radio(LABELS[f],["ใช่","ไม่ใช่"],index=None,horizontal=True,key=f"feature_{i}") for i,f in enumerate(FEATURES)}
        predict=st.form_submit_button("ทำนายอาณาจักร",type="primary")
    if predict:
        if any(v is None for v in answers.values()): st.warning("กรุณาเลือกคุณลักษณะให้ครบทั้ง 6 ข้อ")
        else: show_prediction({f:int(v=="ใช่") for f,v in answers.items()})

with st.expander("ดูเส้นทาง Decision Tree จริง"):
    if last_input is None: st.write("เลือกสิ่งมีชีวิตหรือทำนายจากคุณลักษณะก่อน")
    else:
        tree=model.tree_
        leaf=model.apply(last_input)[0]
        for node in model.decision_path(last_input).indices:
            if node==leaf: continue
            col=model_columns[tree.feature[node]]
            value=int(last_input.iloc[0][col]);threshold=tree.threshold[node]
            operator="≤" if value<=threshold else ">"
            st.write(f"{LABELS[col]}: {value} {operator} {threshold:g}")
        st.caption(f"ปลายทาง node {leaf} · เส้นทางจากโมเดลจริง ไม่ใช่กฎชีววิทยาครบทุกกรณี")

with st.expander("เกี่ยวกับข้อมูลและโมเดล"):
    st.write(f"แค็ตตาล็อกค้นหา {len(catalog)} รายการ แยกจากข้อมูลฝึกเดิม {len(training)} แถว")
    st.write("ค่าอ้างอิงใช้ระยะชีวิต/ชนิดเซลล์ที่ระบุ ไม่ใช่ทุกเซลล์ทุกสภาวะ; ค่าที่ไม่ทราบจะไม่แทนด้วย 0 และไม่ส่งทำนาย")
    st.caption("ชื่อไทยมีเฉพาะที่พบหลักฐาน ไม่ได้แปลหรือเดาให้ครบทุกชนิด คุณลักษณะของรายการพืช/สัตว์ใหม่เป็นการอนุมานระดับกลุ่มโดยเปิดเผยแหล่งข้อมูล")
    st.caption("ยังไม่รวม Rhizopus, Slime mold และ Red tube coral ในแค็ตตาล็อก เพราะนิยามหลายเซลล์/ชื่อกำกวม แต่คงอยู่ในข้อมูลฝึกเดิม")
    st.caption("ไม่ได้ฝึกโมเดลใหม่หรือแก้ไฟล์โมเดลเดิม · ยังไม่มีผลประเมินความแม่นยำกับรายการใหม่")
    st.caption(f"Python {platform.python_version()} · scikit-learn {sklearn.__version__} · Streamlit {st.__version__} · catalog 2026-10-27")
