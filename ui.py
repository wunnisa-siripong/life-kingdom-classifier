"""Presentation helpers. Predictions and paths always come from the loaded model."""
from html import escape
from urllib.parse import urlparse, unquote
import pandas as pd
import streamlit as st
from catalog import FEATURES, prediction_input

LABELS=dict(zip(FEATURES,['ไรโบโซม','การสังเคราะห์แสง','นิวเคลียส','ผนังเซลล์','คลอโรพลาสต์','หลายเซลล์']))
ICONS=dict(zip(FEATURES,['◉','☀','◎','▣','❋','◌']))
KINGDOM_TH={'Monera':'มอเนอรา','Protista':'โพรทิสตา','Fungi':'ฟังไจ','Plantae':'พืช','Animalia':'สัตว์'}


def vector_icon(paths, color="currentColor"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'

KINGDOM_ICONS = {
    "Plantae": vector_icon('<path d="M26 5C13 3 5 9 7 19c9 6 21-1 19-14Z" fill="#B7D7BA" fill-opacity=".18"/><path d="M5 28 23 9M12 21l-1-8M17 16l7 1"/>', "#B7D7BA"),
    "Animalia": vector_icon('<ellipse cx="10" cy="10" rx="3" ry="4"/><ellipse cx="22" cy="10" rx="3" ry="4"/><ellipse cx="4.5" cy="16" rx="2.5" ry="3.5"/><ellipse cx="27.5" cy="16" rx="2.5" ry="3.5"/><path d="M8 25c0-4 5-10 8-10s8 6 8 10c0 5-5 3-8 2-3 1-8 3-8-2Z" fill="#E8BC7D" fill-opacity=".2"/>', "#E8BC7D"),
    "Fungi": vector_icon('<path d="M3 18a13 13 0 0 1 26 0Z" fill="#E6A9BD" fill-opacity=".2"/><path d="m13 18-2 10h10l-2-10M9 12h.01M17 8h.01M23 13h.01"/>', "#E6A9BD"),
    "Protista": vector_icon('<path d="m15 4 7 4-6 11-7-4ZM13 3l11 6M11 20H5M20 15a7 7 0 0 1 1 13M6 28h21M13 23v5"/><circle cx="21" cy="16" r="2"/>', "#C9B8EB"),
    "Monera": vector_icon('<rect x="8" y="5" width="16" height="22" rx="8" transform="rotate(35 16 16)" fill="#93D8DC" fill-opacity=".2"/><path d="m9 4 2 3M21 3l-1 4M28 10l-4 1M28 22l-4-2M21 29l-1-4M6 28l3-4M3 17l4 1M4 8l4 3M13 12h.01M19 16h.01M13 21h.01"/>', "#93D8DC"),
}
MANUAL_ICONS = dict(zip(FEATURES, [
    vector_icon('<circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="8"/>'),
    vector_icon('<circle cx="16" cy="16" r="6"/><path d="M16 2v4M16 26v4M2 16h4M26 16h4M6 6l3 3M23 23l3 3M6 26l3-3M23 9l3-3"/>'),
    vector_icon('<ellipse cx="16" cy="16" rx="6" ry="14" transform="rotate(45 16 16)"/><ellipse cx="16" cy="16" rx="6" ry="14" transform="rotate(-45 16 16)"/><circle cx="16" cy="16" r="1"/>'),
    vector_icon('<path d="M16 3c4 4 7 4 11 5v10c0 6-5 9-11 12C10 27 5 24 5 18V8c4-1 7-1 11-5Z"/>'),
    vector_icon('<path d="M26 5C13 3 5 9 7 19c9 6 21-1 19-14Z"/><path d="M5 28 23 9"/>'),
    vector_icon('<circle cx="16" cy="5" r="3"/><circle cx="6" cy="26" r="3"/><circle cx="26" cy="26" r="3"/><circle cx="16" cy="26" r="3"/><path d="M16 8v15M6 23v-7h20v7"/>'),
]))

def manual_feature_label(feature):
    st.markdown(f'<div class="lk-manual-label"><span>{MANUAL_ICONS[feature]}</span><span>{escape(LABELS[feature])}</span></div>', unsafe_allow_html=True)

CSS='''<style>
.stApp{background:#191D1A;color:#F2F5F0}
[data-testid="stHeader"]{background:#191D1A}
.block-container{max-width:860px;padding-top:2.2rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em} .lk-kicker{font-size:.7rem;letter-spacing:.18em;color:#B7D7BA;font-weight:650;margin-bottom:10px}
.lk-intro{color:#bec9bd;margin:0 0 22px;line-height:1.7}
.lk-profile{display:flex;gap:22px;align-items:center;background:#292F2A;border:1px solid #3b493d;border-radius:22px;padding:24px;margin:18px 0}
.lk-placeholder{display:flex;flex:0 0 112px;height:126px;align-items:center;justify-content:center;flex-direction:column;background:#344236;border-radius:15px;color:#c6d7c4;font-size:11px;text-align:center;padding:10px}
.lk-placeholder span{font-size:36px;margin-bottom:9px}.lk-profile h2{font-size:2rem;margin:0;padding:0;color:#F2F5F0}.lk-profile p{margin:5px 0;color:#cad4c7}.lk-profile i{font-size:1.05rem}.lk-tag{display:inline-block;font-size:.75rem;background:#344236;padding:5px 10px;border-radius:30px;color:#d5e5d2;margin-top:7px}
.lk-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:10px 0 22px}
.lk-feature{display:flex;gap:12px;align-items:center;padding:14px;background:#292F2A;border-radius:14px;min-width:0}.lk-icon{color:#B7D7BA;font-size:22px;flex-shrink:0}.lk-feature small{display:block;color:#b8c4b7;font-size:.8rem}.lk-feature strong{font-size:.95rem;font-weight:550}
.lk-result{background:#344B39;border:1px solid #6f9475;border-radius:22px;padding:24px;margin:10px 0 16px}.lk-result h2{padding:0;margin:0;color:#F2F5F0;font-size:2.2rem}.lk-result .lk-en{color:#c6dfc6;margin-top:4px}.lk-compare{border-top:1px solid #68826b;margin-top:20px;padding-top:14px;font-size:.88rem;line-height:1.8;color:#e4eee0}.lk-note{background:#293b2d;border-radius:10px;padding:12px 14px;margin-top:10px;line-height:1.7;font-size:.85rem;color:#e2e9d8}
.lk-flow{list-style:none;padding:0;margin:6px 0 16px}.lk-flow li{position:relative;border-left:2px solid #719777;padding:0 0 20px 22px;margin-left:8px;line-height:1.7}.lk-flow li:before{content:'';position:absolute;left:-6px;top:7px;width:10px;height:10px;border-radius:50%;background:#B7D7BA}.lk-flow li:last-child{padding-bottom:0;border-left-color:transparent}.lk-flow small{display:block;color:#b5c4b2}
[data-testid="stExpander"]{border:1px solid #3b493d;border-radius:14px;background:transparent}
[data-testid="stRadio"]{background:#292F2A;border-radius:12px;padding:12px 15px;display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
[data-testid="stRadio"]>label{font-weight:550;margin:0;width:auto!important;flex:1}
[data-testid="stRadio"]>[role="radiogroup"]{width:auto!important;flex:0 0 auto}
div.stButton>button{border-radius:24px;min-height:44px} [data-baseweb="tab-list"]{gap:22px;border-bottom:1px solid #3b493d} [data-baseweb="tab"]{padding:12px 0}
a{color:#B7D7BA!important} [data-testid="stCaptionContainer"]{color:#b5c4b2}
@media(max-width:600px){.block-container{padding:1.2rem 1rem 2rem}.lk-profile{padding:18px;gap:14px}.lk-placeholder{flex-basis:74px;height:108px;font-size:10px}.lk-profile h2{font-size:1.6rem}.lk-profile i{font-size:.9rem}.lk-feature{padding:12px 10px;gap:9px}.lk-feature small{font-size:.73rem}.lk-result{padding:20px}.lk-result h2{font-size:1.9rem}[data-baseweb="tab-list"]{gap:18px}[data-baseweb="tab"]{font-size:.86rem}}

/* เพิ่มระยะด้านบน ไม่ให้หัวเว็บถูกบัง */
[data-testid="stMainBlockContainer"] {
    padding-top: 5rem !important;
}

/* Compact manual feature controls */
[data-testid="stRadio"] {
    padding: 8px 14px !important;
    min-height: 58px;
    border-radius: 12px !important;
    gap: 6px !important;
}

[data-testid="stRadio"] > label {
    font-size: 0.95rem;
}

@media (max-width: 600px) {
    [data-testid="stRadio"] {
        padding: 10px 12px !important;
    }
}


/* Only the prediction card and six keyed manual rows. */
.lk-result{position:relative}
.lk-result>.lk-kicker{padding-right:52px;min-height:32px;display:flex;align-items:center}
.lk-result-icon{position:absolute;top:24px;right:24px;width:34px;height:34px}
.lk-result-icon svg{display:block;width:100%;height:100%}
[class*="st-key-manual_feature_"][data-testid="stVerticalBlock"]{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:8px;background:#292F2A;border-radius:12px;padding:8px 14px;min-height:58px}
.lk-manual-label{display:flex;align-items:center;gap:14px;font-weight:550;line-height:1.4}
.lk-manual-label>span:first-child{display:flex;flex:0 0 26px;width:26px;height:26px;color:#B7D7BA}
.lk-manual-label svg{width:26px;height:26px;display:block}
[class*="st-key-manual_feature_"] [data-testid="stRadio"]{padding:0!important;min-height:0;background:transparent;gap:0!important}
[class*="st-key-manual_feature_"] [role="radiogroup"]{gap:10px;flex-wrap:nowrap}
@media(max-width:600px){.lk-result-icon{top:20px;right:20px;width:32px;height:32px}[class*="st-key-manual_feature_"][data-testid="stVerticalBlock"]{padding:8px 10px}.lk-manual-label{font-size:.95rem}}
</style>'''

def profile(row):
    e=lambda key:escape(str(row[key]))
    st.markdown(f'''<section class="lk-profile" aria-label="Species Profile">
<div class="lk-placeholder" role="img" aria-label="ภาพแทน ยังไม่มีภาพที่ตรวจสอบสิทธิ์"><span aria-hidden="true">❋</span>ภาพแทน<br>รอภาพยืนยันสิทธิ์</div>
<div><div class="lk-kicker">SPECIES PROFILE</div><h2>{escape(row['thai_name'] or row['english_name'] or row['scientific_name'])}</h2><p><i>{e('scientific_name')}</i></p><p>{e('english_name')}</p><span class="lk-tag">อ้างอิง · {escape(KINGDOM_TH[row['Kingdom']])} / {e('Kingdom')}</span></div></section>''',unsafe_allow_html=True)

def feature_cards(row):
    cards=[]
    for f in FEATURES:
        if pd.isna(row[f]):
            value = "ไม่ทราบ"
        elif f == "Photosynthesis":
            value = "ได้" if row[f] == 1 else "ไม่ได้"
        else:
            value = "มี" if row[f] == 1 else "ไม่มี"
        cards.append(f'<div class="lk-feature"><span class="lk-icon" aria-hidden="true">{ICONS[f]}</span><div><small>{LABELS[f]}</small><strong>{value}</strong></div></div>')
    st.markdown('<div class="lk-kicker">ลักษณะสำคัญทั้ง 6</div><div class="lk-grid">'+''.join(cards)+'</div>',unsafe_allow_html=True)

def decision_steps(model,X,columns):
    tree=model.tree_
    leaf=int(model.apply(X)[0])
    steps=[]
    for node in model.decision_path(X).indices:
        if node==leaf: continue
        f=columns[tree.feature[node]]
        value=int(X.iloc[0][f]); threshold=float(tree.threshold[node])
        steps.append(dict(node=int(node),feature=f,value=value,threshold=threshold,operator='≤' if value<=threshold else '>'))
    return steps,leaf

def prediction(values,model,columns,reference=None):
    try: X=prediction_input(values,columns)
    except ValueError as error:
        st.warning(str(error));return
    result=str(model.predict(X)[0])
    compare=''
    if reference:
        match=result==reference
        compare=f'<div class="lk-compare">ข้อมูลอ้างอิง · <strong>{escape(KINGDOM_TH[reference])} / {escape(reference)}</strong><br>{"✓ สอดคล้องกับผลโมเดล" if match else "ผลต่างกัน · ผลโมเดลกับข้อมูลอ้างอิงไม่ตรงกัน"}</div>'
        if not match:
            compare+='<div class="lk-note">คุณลักษณะ 6 ข้อนี้อาจเหมือนกันในต่างอาณาจักร โมเดลจึงแยกไม่ได้ทุกกรณี ผลนี้เป็นการทำนายจากโมเดล ไม่ได้เปลี่ยนข้อมูลอ้างอิงของสิ่งมีชีวิต</div>'
    st.markdown(f'<section class="lk-result" aria-label="ผลการทำนาย"><span class="lk-result-icon">{KINGDOM_ICONS.get(result, "")}</span><div class="lk-kicker">MODEL PREDICTION</div><h2>อาณาจักร{escape(KINGDOM_TH.get(result,result))}</h2><div class="lk-en">{escape(result)}</div>{compare}</section>',unsafe_allow_html=True)
    with st.expander('ดูเหตุผลการทำนาย'):
        steps,leaf=decision_steps(model,X,columns)
        items=''.join(f'<li><strong>{LABELS[s["feature"]]}</strong><small>คำตอบ: {"ใช่" if s["value"] else "ไม่ใช่"} → ไปยังขั้นถัดไป</small></li>' for s in steps)
        st.markdown(f'<ol class="lk-flow" aria-label="เส้นทางการตัดสินใจ">{items}<li><strong>ผลทำนาย · {escape(result)}</strong><small>อาณาจักร{escape(KINGDOM_TH.get(result,result))}</small></li></ol>',unsafe_allow_html=True)
        st.caption('แสดงเฉพาะคำถามที่โมเดลใช้จริงในเส้นทางนี้ ไม่ใช่กฎชีววิทยาครบทุกกรณี')
        with st.expander('รายละเอียดทางเทคนิค'):
            for s in steps: st.text(f'node {s["node"]} · {s["feature"]}: {s["value"]} {s["operator"]} {s["threshold"]:g}')
            st.caption(f'ปลายทาง node {leaf} · model.decision_path')
    return result

def source_label(url):
    parsed=urlparse(url)
    host=parsed.netloc.removeprefix('www.')
    path=unquote(parsed.path).strip('/').split('/')
    title=path[-1].replace('-',' ').replace('_',' ') if path and path[-1] else 'หน้าข้อมูล'
    if host=='scimath.org': return 'Scimath · บทเรียนชีววิทยา'
    if host=='gbif.org': return 'GBIF · ข้อมูลชื่อและอนุกรมวิธาน'
    for slug,label in {'eukaryotic-cells':'เซลล์ยูแคริโอต','prokaryotic-cells':'เซลล์โพรแคริโอต','groups-of-protists':'กลุ่มโพรทิสต์','characteristics-of-the-animal-kingdom':'ลักษณะของอาณาจักรสัตว์','early-plant-life':'พืชบกและวิวัฒนาการระยะแรก'}.items():
        if slug in parsed.path: title=label;break
    return escape(host+' · '+title[:75])

def thai_evidence(text):
    translations={
        'All living cells contain ribosomes':'เซลล์ที่มีชีวิตมีไรโบโซม',
        'Green leaf photosynthetic capability under light':'เนื้อเยื่อใบสีเขียวสังเคราะห์แสงได้เมื่อได้รับแสง',
        'Host animal is heterotrophic; excludes symbionts':'ตัวสัตว์รับสารอาหารจากภายนอก ไม่รวมคุณลักษณะของสิ่งมีชีวิตร่วมอาศัย',
        'Representative eukaryotic cell has a nucleus':'เซลล์ยูแคริโอตตัวแทนมีนิวเคลียส',
        'Representative nucleated somatic cell':'ใช้เซลล์ร่างกายตัวแทนที่มีนิวเคลียส',
        'Plant cell wall':'เซลล์พืชมีผนังเซลล์',
        'Animal cell membrane is not a cell wall':'เยื่อหุ้มเซลล์สัตว์ไม่ใช่ผนังเซลล์',
        'Green leaf cell chloroplast':'เซลล์ใบสีเขียวมีคลอโรพลาสต์',
        'Host animal cell lacks chloroplasts':'เซลล์ของตัวสัตว์ไม่มีคลอโรพลาสต์',
        'Mature land plant body is multicellular':'ร่างกายพืชบกโตเต็มวัยประกอบด้วยหลายเซลล์',
        'Animal body is multicellular':'ร่างกายสัตว์ประกอบด้วยหลายเซลล์',
    }
    prefix='Group-level inference: '
    if text.startswith(prefix): return 'อนุมานระดับกลุ่ม: '+translations.get(text[len(prefix):],text[len(prefix):])
    return text

def evidence(row,columns):
    with st.expander('หลักฐาน แหล่งอ้างอิง และข้อจำกัด'):
        st.markdown('**ขอบเขตที่ใช้ประเมิน**')
        scope=row['scope']
        if scope.startswith('Mature green plant;'):
            scope='พืชสีเขียวโตเต็มวัย ใช้เนื้อเยื่อใบที่รับแสงและสังเคราะห์แสง ไม่ได้หมายถึงทุกเซลล์ เมล็ด หรือระยะพักตัว'
        elif scope.startswith('Juvenile/adult host body'):
            scope='ร่างกายสัตว์วัยอ่อนหรือโตเต็มวัย และเซลล์ร่างกายที่มีนิวเคลียส ไม่รวมสิ่งมีชีวิตร่วมอาศัย เซลล์สืบพันธุ์ และเม็ดเลือดแดงโตเต็มวัยของสัตว์เลี้ยงลูกด้วยนม'
        elif scope=='Vegetative photosynthetic filament':
            scope='ระยะเส้นสายที่กำลังเจริญและสังเคราะห์แสง'
        st.write(scope);st.write(row['uncertainty'])
        inferred='group' in row['evidence_basis'].lower()
        st.caption(('คุณลักษณะอนุมานระดับกลุ่มตามขอบเขตที่ระบุ ไม่ใช่ผลวัดตัวอย่างรายชนิด' if inferred else 'คุณลักษณะอ้างอิงจากการตรวจข้อมูลเดิมของโครงงาน ตามระยะชีวิตและชนิดเซลล์ที่ระบุ')+' · ตรวจหลักฐาน: '+row['verified_on'])
        st.markdown('**หลักฐานคุณลักษณะ**')
        for f in columns:
            state='ไม่ทราบ' if pd.isna(row[f]) else ('มี / ทำได้' if row[f] else 'ไม่มี / ทำไม่ได้')
            st.markdown(f'**{LABELS[f]} · {state}**')
            st.caption(thai_evidence(row[f+'_evidence']))
        with st.expander('ข้อความขอบเขตและหลักฐานต้นฉบับ'):
            st.write(row['scope']);st.write(row['evidence_basis'])
            for f in columns: st.caption(f+': '+row[f+'_evidence'])
        for title,key in [('ชื่อและอนุกรมวิธาน','name_sources'),('คุณลักษณะและชีววิทยา','feature_sources')]:
            st.markdown('**'+title+'**')
            for url in dict.fromkeys(row[key].split('|')):
                if url.startswith('https://'):
                    st.markdown(f'<p><a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{source_label(url)} ↗</a></p>',unsafe_allow_html=True)
        st.caption('Protista และ Monera เป็นป้ายตามระบบห้าอาณาจักรของโครงงาน ไม่ใช่อาณาจักรสมัยใหม่จาก GBIF; ชื่ออ้างอิงไม่ใช่การพิสูจน์ชนิดตัวอย่างจริง')
