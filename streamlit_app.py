
import streamlit as st
import pandas as pd
import joblib
st.set_page_config(
    page_title="Life Kingdom",
    page_icon="🌿",
    layout="centered"
)
@st.cache_resource
def load_model():
    package = joblib.load("life_kingdom_model.joblib")
    return package["model"], list(package["features"])

model, model_columns = load_model()

st.markdown("""
<style>
.stApp {
    background-color: #191c1a;
    color: #f6f7f5;
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
}
div[data-testid="stFormSubmitButton"] button {
    border-radius: 28px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("🌿 Life Kingdom")
st.write("ทดลองจำแนกอาณาจักรสิ่งมีชีวิตด้วย Decision Tree")
st.caption("ทดลองจำแนกสิ่งมีชีวิตด้วยโมเดล Decision Tree")

tab1, tab2 = st.tabs([
    "ค้นหาสิ่งมีชีวิต",
    "กำหนดคุณลักษณะเอง"
])

with tab1:
    with st.form("organism_form"):
        name = st.text_input(
            "ชื่อสิ่งมีชีวิต",
            placeholder="เช่น ต้นมะม่วง, Amoeba, Spirogyra"
        )
        search = st.form_submit_button(
            "ทำนายอาณาจักร",
            type="primary"
        )

    if search:
        if not name.strip():
            st.warning("กรุณาพิมพ์ชื่อสิ่งมีชีวิต")
        else:
            st.info(
                "รับชื่อแล้ว: " + name +
                " — ยังไม่ได้เชื่อมฐานข้อมูลและโมเดล"
            )


with tab2:
    features = [
        "Ribosome — มีไรโบโซม",
        "Photosynthesis — สังเคราะห์แสงได้",
        "Nucleus — มีนิวเคลียส",
        "Cell Wall — มีผนังเซลล์",
        "Chloroplast — มีคลอโรพลาสต์",
        "Multicellular — มีหลายเซลล์"
    ]

    with st.form("feature_form"):
        answers = {}

        for i, feature in enumerate(features):
            answers[feature] = st.radio(
                feature,
                options=["ใช่", "ไม่ใช่"],
                index=None,
                horizontal=True,
                key=f"feature_{i}"
            )

        predict = st.form_submit_button(
            "ทำนายอาณาจักร",
            type="primary"
        )

    if predict:
        if any(v is None for v in answers.values()):
            st.warning("กรุณาเลือกคุณลักษณะให้ครบทั้ง 6 ข้อ")
        else:
            form_columns = [
                "Ribosome",
                "Photosynthesis",
                "Nucleus",
                "Cell wall",
                "Chloroplast",
                "Multicellular organisms"
            ]

            values = {
                col: 1 if answer == "ใช่" else 0
                for col, answer in zip(
                    form_columns, answers.values()
                )
            }

            missing = [
                col for col in model_columns
                if col not in values
            ]

            if missing:
                st.error(
                    f"ชื่อคุณลักษณะไม่ตรงกับ Colab: {missing}"
                )
            else:
                X = pd.DataFrame(
                    [[values[col] for col in model_columns]],
                    columns=model_columns
                )

                result = model.predict(X)[0]
                st.success(f"ผลการทำนาย: {result}")

with st.expander("ดูเหตุผลการทำนาย"):
    st.write("จะแสดงเส้นทางการตัดสินใจของโมเดลจริง")

with st.expander("ข้อมูลโมเดลและแหล่งอ้างอิง"):
    st.write("Dataset: 50 ตัวอย่าง")
    st.write("Features: 6 คุณลักษณะ")
    st.write("Traditional Five-Kingdom Classification")
