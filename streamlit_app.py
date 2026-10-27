from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Life Kingdom", page_icon="🌿", layout="centered")
BASE = Path(__file__).resolve().parent
LABELS = {
    "Ribosome": "Ribosome — มีไรโบโซม",
    "Photosynthesis": "Photosynthesis — สังเคราะห์แสงได้",
    "Nucleus": "Nucleus — มีนิวเคลียส",
    "Cell wall": "Cell Wall — มีผนังเซลล์",
    "Chloroplast": "Chloroplast — มีคลอโรพลาสต์",
    "Multicellular organisms": "Multicellular — มีหลายเซลล์",
}


@st.cache_resource
def load_model():
    package = joblib.load(BASE / "life_kingdom_model.joblib")
    model, columns = package["model"], list(package["features"])
    if len(columns) != 6 or set(columns) != set(LABELS):
        raise ValueError("คุณลักษณะในโมเดลไม่ตรงกับแบบฟอร์ม 6 ข้อ")
    return model, columns


@st.cache_data
def load_organisms():
    return pd.read_csv(BASE / "organisms.csv", encoding="utf-8-sig")


model, model_columns = load_model()
organisms = load_organisms()

st.markdown("""
<style>
.stApp { background-color: #191c1a; color: #f6f7f5; }
.block-container { max-width: 850px; padding-top: 2rem; }
div[data-testid="stFormSubmitButton"] button { border-radius: 28px; width: 100%; }
</style>
""", unsafe_allow_html=True)
st.title("🌿 Life Kingdom")
st.write("ทดลองจำแนกอาณาจักรสิ่งมีชีวิตด้วย Decision Tree")
st.caption("เลือกค้นหาจากข้อมูลเดิม หรือกำหนดคุณลักษณะทั้ง 6 ข้อ")


def show_prediction(values):
    X = pd.DataFrame([[int(values[col]) for col in model_columns]], columns=model_columns)
    result = model.predict(X)[0]
    st.success(f"ผลการทำนาย: {result}")
    st.session_state["last_input"] = X.to_dict(orient="records")[0]
    return result


tab1, tab2 = st.tabs(["ค้นหาสิ่งมีชีวิต", "กำหนดคุณลักษณะเอง"])
with tab1:
    st.caption("ค้นหาชื่อภาษาอังกฤษในชุดข้อมูล 50 ตัวอย่าง เช่น Fern, Amoeba, Spirogyra")
    with st.form("organism_form"):
        name = st.text_input("ชื่อสิ่งมีชีวิต", placeholder="เช่น Fern, Amoeba, Spirogyra")
        search = st.form_submit_button("ทำนายอาณาจักร", type="primary")
    if search:
        query = " ".join(name.split()).casefold()
        names = organisms["Common name"].astype(str).str.strip().str.casefold()
        if not query:
            st.warning("กรุณาพิมพ์ชื่อสิ่งมีชีวิต")
        else:
            matches = organisms.loc[names.eq(query)]
            if matches.empty:
                st.warning("ไม่พบชื่อนี้ในชุดข้อมูล กรุณาเลือกชื่อจากรายการด้านล่าง หรือใช้โหมดกำหนดคุณลักษณะเอง")
            else:
                row = matches.iloc[0]
                st.write(f"สิ่งมีชีวิต: {row['Common name']}")
                result = show_prediction(row)
                st.caption(f"อาณาจักรที่ระบุในชุดข้อมูล: {row['Kingdom']}")
                if result != row["Kingdom"]:
                    st.info("ผลโมเดลอาจต่างจากป้ายกำกับในข้อมูล เพราะบางอาณาจักรมีคุณลักษณะทั้ง 6 ข้อเหมือนกัน")
    with st.expander("รายชื่อสิ่งมีชีวิตในชุดข้อมูล"):
        st.dataframe(organisms[["Common name", "Kingdom"]], hide_index=True, use_container_width=True)

with tab2:
    with st.form("feature_form"):
        answers = {
            col: st.radio(label, ["ใช่", "ไม่ใช่"], index=None, horizontal=True, key=f"feature_{i}")
            for i, (col, label) in enumerate(LABELS.items())
        }
        predict = st.form_submit_button("ทำนายอาณาจักร", type="primary")
    if predict:
        if any(value is None for value in answers.values()):
            st.warning("กรุณาเลือกคุณลักษณะให้ครบทั้ง 6 ข้อ")
        else:
            show_prediction({col: int(value == "ใช่") for col, value in answers.items()})

with st.expander("ดูเหตุผลการทำนาย"):
    if "last_input" not in st.session_state:
        st.write("ทำนายก่อนเพื่อดูเส้นทางการตัดสินใจของโมเดลจริง")
    else:
        X = pd.DataFrame([st.session_state["last_input"]], columns=model_columns)
        tree = model.tree_
        leaf = model.apply(X)[0]
        for node in model.decision_path(X).indices:
            if node == leaf:
                continue
            col = model_columns[tree.feature[node]]
            value, threshold = int(X.iloc[0][col]), tree.threshold[node]
            operator = "≤" if value <= threshold else ">"
            st.write(f"{LABELS[col]}: {value} {operator} {threshold:g}")
        st.caption("เส้นทางนี้อธิบายการตัดสินใจของโมเดลจากข้อมูลฝึก ไม่ใช่กฎชีววิทยาที่ครอบคลุมทุกกรณี")

with st.expander("ข้อมูลโมเดลและแหล่งอ้างอิง"):
    st.write(f"Dataset: {len(organisms)} ตัวอย่าง · Features: {len(model_columns)} คุณลักษณะ")
    st.write("Traditional Five-Kingdom Classification")
    st.caption("ใช้โมเดลและชุดข้อมูลเดิมจากโครงการ Life Kingdom")
