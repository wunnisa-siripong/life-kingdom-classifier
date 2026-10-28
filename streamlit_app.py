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


from html import escape
import math
import streamlit.components.v1 as components
# Refresh presentation helpers retained by a running Streamlit Cloud process.
import importlib
import ui
importlib.reload(ui)
from ui import CSS, LABELS, QUESTIONS, KINGDOM_TH, KINGDOM_ICONS, BOOK_ICON, profile, prediction, evidence, manual_feature_label
st.markdown(CSS,unsafe_allow_html=True)
try:
    model,model_columns=load_model()
    catalog,training=load_data()
except Exception as error:
    st.error("โหลดข้อมูลหรือโมเดลไม่สำเร็จ กรุณาตรวจการติดตั้งและไฟล์บน GitHub")
    st.exception(error)
    st.stop()

def navigate(view):
    st.session_state['view']=view
    if view=='catalog':
        for key,default in [('catalog_query',''),('kingdom_filter','ทั้งหมด'),('catalog_page',1)]:
            st.session_state[key]=st.session_state.get('saved_'+key,default)

def open_profile(row_id):
    st.session_state['selected_id']=row_id
    st.session_state['view']='profile'

def reset_filters():
    st.session_state['catalog_query']=''
    st.session_state['kingdom_filter']='ทั้งหมด'
    st.session_state['catalog_page']=1

def reset_page():
    st.session_state['catalog_page']=1

def detail(row):
    profile(row)
    prediction(row,model,model_columns,row['Kingdom'])
    evidence(row,model_columns)

def about():
    with st.expander('เกี่ยวกับโมเดลและชุดข้อมูล'):
        st.write(f'Decision Tree เดิม · ข้อมูลฝึก {len(training)} แถว · แค็ตตาล็อกค้นหา {len(catalog)} รายการ')
        st.write('ใช้ระบบห้าอาณาจักรของโครงงาน: Monera, Protista, Fungi, Plantae และ Animalia ไม่ใช่การจัดอนุกรมวิธานสมัยใหม่จาก GBIF')
        st.write('ใช้คุณลักษณะ 6 ข้อและแสดงเส้นทางที่โมเดลใช้จริง คุณลักษณะเดียวกันอาจพบได้ต่างอาณาจักร จึงแยกสิ่งมีชีวิตไม่ได้ทุกกรณี เช่น Spirogyra')
        st.caption('ไม่ได้ฝึกโมเดลใหม่หรือแก้ข้อมูลฝึกเดิม · ยังไม่มีผลประเมินความแม่นยำกับแค็ตตาล็อกใหม่ จึงไม่แสดงคะแนนที่ตรวจสอบไม่ได้')
        st.caption('ค่าอ้างอิงใช้ระยะชีวิตและชนิดเซลล์ที่ระบุ ค่าที่ไม่ทราบไม่แทนด้วย 0 และไม่ส่งทำนาย คุณลักษณะของรายการใหม่บางส่วนเป็นการอนุมานระดับกลุ่มโดยมีแหล่งอ้างอิง')
        st.caption(f'Python {platform.python_version()} · scikit-learn {sklearn.__version__} · Streamlit {st.__version__}')

def catalog_link():
    with st.container(key='catalog_link'):
        st.markdown(f'<div class="lk-nav-card"><span>{BOOK_ICON}</span><div><strong>สำรวจสิ่งมีชีวิตทั้งหมด</strong><small>ดูข้อมูลทั้งหมด {len(catalog)} รายการ</small></div><b>↗</b></div>',unsafe_allow_html=True)
        st.button('สำรวจสิ่งมีชีวิตทั้งหมด',key='open_catalog',on_click=navigate,args=('catalog',),width='stretch')

def clear_manual():
    for i in range(6): st.session_state[f'feature_{i}']=None
    st.session_state.pop('manual_values',None)
    st.session_state.pop('manual_incomplete',None)

def changed_manual():
    st.session_state.pop('manual_values',None)
    st.session_state.pop('manual_incomplete',None)


view=st.session_state.get('view','home')
if view=='catalog':
    st.button('← กลับหน้า Life Kingdom',on_click=navigate,args=('home',))
    st.markdown(f'<div class="lk-catalog-heading"><div class="lk-kicker">EXPLORE CATALOG</div><h1>สำรวจสิ่งมีชีวิตทั้งหมด</h1><p>แค็ตตาล็อกปัจจุบัน {len(catalog)} รายการ</p><span>{BOOK_ICON}</span></div>',unsafe_allow_html=True)
    with st.container(key='catalog_search'):
        query=st.text_input('ค้นหาในแค็ตตาล็อก',key='catalog_query',placeholder='ค้นหาชื่อไทย อังกฤษ หรือวิทยาศาสตร์',label_visibility='collapsed',on_change=reset_page)
    labels={'ทั้งหมด':None,'พืช':'Plantae','สัตว์':'Animalia','เห็ดรา':'Fungi','โพรทิสตา':'Protista','มอเนอรา':'Monera'}
    chosen=st.pills('กรองตามอาณาจักร',list(labels),default='ทั้งหมด' if 'kingdom_filter' not in st.session_state else None,key='kingdom_filter',on_change=reset_page)
    matches=search(catalog,query) if query.strip() else catalog
    if labels.get(chosen): matches=matches.loc[matches.Kingdom.eq(labels[chosen])]
    st.markdown(f'<div class="lk-list-heading"><strong>รายการสิ่งมีชีวิต</strong><span>{len(matches)} รายการ</span></div>',unsafe_allow_html=True)
    page_count=max(1,math.ceil(len(matches)/18))
    if st.session_state.get('catalog_page',1)>page_count: st.session_state['catalog_page']=1
    page=st.session_state.get('catalog_page',1)
    st.session_state['saved_catalog_query']=query
    st.session_state['saved_kingdom_filter']=chosen
    st.session_state['saved_catalog_page']=page
    if matches.empty:
        st.markdown('<div class="lk-empty">ไม่พบรายการที่ตรงกับคำค้นหาและตัวกรอง</div>',unsafe_allow_html=True)
        st.button('ล้างตัวกรอง',on_click=reset_filters)
    else:
        for _,r in matches.iloc[(page-1)*18:page*18].iterrows():
            name=r['thai_name'] or r['english_name'] or r['scientific_name']
            sub=' · '.join(dict.fromkeys(x for x in [r['scientific_name'],r['english_name']] if x))
            with st.container(key=f'catalog_item_{r["id"]}'):
                st.markdown(f'<div class="lk-catalog-row"><span class="lk-catalog-symbol">{KINGDOM_ICONS[r["Kingdom"]]}</span><div><strong>{escape(name)}</strong><small>{escape(sub)}</small></div><b>↗</b></div>',unsafe_allow_html=True)
                st.button(f'เปิดข้อมูล {name}',key=f'open_{r["id"]}',on_click=open_profile,args=(r['id'],),width='stretch')
        if page_count>1:
            st.selectbox('หน้า',range(1,page_count+1),key='catalog_page',format_func=lambda n:f'{n} / {page_count}')
    st.download_button('ดาวน์โหลด CSV พร้อมแหล่งอ้างอิง',(BASE/'organism_catalog.csv').read_bytes(),file_name='organism_catalog.csv',mime='text/csv')
    about()
elif view=='profile':
    st.button('← กลับไปแค็ตตาล็อก',on_click=navigate,args=('catalog',))
    selected=catalog.loc[catalog.id.eq(st.session_state.get('selected_id'))]
    if not selected.empty: detail(selected.iloc[0])
    else: st.info('ไม่พบรายการนี้ในแค็ตตาล็อก')
    about()
else:
    st.markdown('<div class="lk-kicker">EXPLORE THE LIVING WORLD</div>',unsafe_allow_html=True)
    st.title('Life Kingdom')
    st.markdown('<div class="lk-hero-icons" aria-label="อาณาจักรทั้งห้า">'+''.join(f'<span>{KINGDOM_ICONS[k]}</span>' for k in ['Plantae','Animalia','Fungi','Protista','Monera'])+'</div><p class="lk-slogan">“โลกของสิ่งมีชีวิต เริ่มจากความสงสัยเล็ก ๆ”</p><p class="lk-intro">ค้นหาสิ่งมีชีวิต สำรวจข้อมูลทางชีววิทยา และเรียนรู้การจำแนกอาณาจักรด้วย Decision Tree</p>',unsafe_allow_html=True)
    tab1,tab2=st.tabs(['ค้นหาสิ่งมีชีวิต','กำหนดคุณลักษณะเอง'])
    with tab1:
        search_box=components.declare_component('living_search',path=str(BASE/'search_component'))
        rows=[dict(id=r['id'],name=r['thai_name'] or r['english_name'] or r['scientific_name'],scientific=r['scientific_name'],english=r['english_name'],names=[r['thai_name'],r['english_name'],r['scientific_name'],*r['aliases'].split('|')],icon=KINGDOM_ICONS[r['Kingdom']]) for _,r in catalog.iterrows()]
        selected_id=search_box(rows=rows,key='main_search',default=None)
        selected=catalog.loc[catalog.id.eq(selected_id)]
        catalog_link()
        if not selected.empty: detail(selected.iloc[0])
    with tab2:

        st.caption("เลือกคำตอบทั้ง 6 ข้อ แล้วให้โมเดลช่วยจำแนกอาณาจักร")
        complete=sum(st.session_state.get(f'feature_{i}') is not None for i in range(6))
        st.markdown(f'**เลือกแล้ว {complete}/6 ข้อ**')
        answers={}
        for i,f in enumerate(FEATURES):
            with st.container(key=f'manual_feature_{i}'):
                manual_feature_label(f)
                answers[f]=st.radio(QUESTIONS[f],["ใช่","ไม่ใช่"],index=None,horizontal=True,key=f'feature_{i}',on_change=changed_manual,width='stretch',label_visibility='collapsed')
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

    about()
