"""Presentation helpers. Predictions and paths always come from the loaded model."""
from html import escape
from urllib.parse import urlparse, unquote
import pandas as pd
import streamlit as st
from catalog import FEATURES, prediction_input
from species import PROFILES

LABELS=dict(zip(FEATURES,['ไรโบโซม','การสังเคราะห์แสง','นิวเคลียส','ผนังเซลล์','คลอโรพลาสต์','หลายเซลล์']))
ICONS=dict(zip(FEATURES,['◉','☀','◎','▣','❋','◌']))
QUESTIONS=dict(zip(FEATURES,['มีไรโบโซม','สังเคราะห์แสงได้','มีนิวเคลียส','มีผนังเซลล์','มีคลอโรพลาสต์','เป็นสิ่งมีชีวิตหลายเซลล์']))
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
BOOK_ICON=vector_icon('<path d="M16 7C11 3 6 3 2 4v22c5-1 9 0 14 3 5-3 9-4 14-3V4c-4-1-9-1-14 3Zm0 0v22"/>', '#B7D7BA')

MANUAL_ICONS = dict(zip(FEATURES, [
    vector_icon('<circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="8"/>'),
    vector_icon('<circle cx="16" cy="16" r="6"/><path d="M16 2v4M16 26v4M2 16h4M26 16h4M6 6l3 3M23 23l3 3M6 26l3-3M23 9l3-3"/>'),
    vector_icon('<ellipse cx="16" cy="16" rx="6" ry="14" transform="rotate(45 16 16)"/><ellipse cx="16" cy="16" rx="6" ry="14" transform="rotate(-45 16 16)"/><circle cx="16" cy="16" r="1"/>'),
    vector_icon('<path d="M16 3c4 4 7 4 11 5v10c0 6-5 9-11 12C10 27 5 24 5 18V8c4-1 7-1 11-5Z"/>'),
    vector_icon('<path d="M26 5C13 3 5 9 7 19c9 6 21-1 19-14Z"/><path d="M5 28 23 9"/>'),
    vector_icon('<circle cx="16" cy="5" r="3"/><circle cx="6" cy="26" r="3"/><circle cx="26" cy="26" r="3"/><circle cx="16" cy="26" r="3"/><path d="M16 8v15M6 23v-7h20v7"/>'),
]))

def manual_feature_label(feature):
    st.markdown(f'<div class="lk-manual-label"><span>{MANUAL_ICONS[feature]}</span><span>{escape(QUESTIONS[feature])}</span></div>', unsafe_allow_html=True)

CSS='''<style>
@import url('https://fonts.googleapis.com/css2?family=Anuphan:wght@400;500;600;700&display=swap');
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

/* Remaining approved presentation work; manual row geometry stays intact. */
.stApp,.stApp input,.stApp button,.stApp textarea{font-family:'Anuphan','Noto Sans Thai',Tahoma,sans-serif}
.stApp h1,.stApp h2,.stApp h3{font-family:'Anuphan','Noto Sans Thai',Tahoma,sans-serif;line-height:1.35;letter-spacing:-.015em}
.stApp h1{font-size:clamp(2.8rem,7vw,3.7rem);font-weight:700}
.lk-profile{position:relative;align-items:flex-start;padding-right:76px}
.lk-profile>div{min-width:0}.lk-profile h2{font-size:clamp(2rem,5vw,2.7rem);overflow-wrap:anywhere}.lk-profile i{overflow-wrap:anywhere}
.lk-profile-icon{position:absolute;top:24px;right:24px;width:34px;height:34px}.lk-profile-icon svg{width:100%;height:100%}
.lk-photo{flex:0 0 150px;width:150px;height:160px;background:#344236;border-radius:16px;overflow:hidden;display:flex;align-items:center;justify-content:center}.lk-photo img{width:100%;height:100%;object-fit:contain}
.lk-bio{color:#d8e2d4;line-height:1.85;margin:0 0 14px}.lk-bio p{margin:0 0 6px}.lk-bio ul{margin:0;padding-left:22px}
.lk-placeholder svg{width:40px;height:40px}.lk-placeholder span{display:flex}
.lk-feature .lk-icon{display:flex;flex:0 0 26px;width:26px;height:26px}.lk-feature svg{width:26px;height:26px}
.lk-feature{gap:14px;line-height:1.6}.lk-feature small{font-size:.88rem;color:#c5d0c2}.lk-feature strong{font-size:1.05rem}
.lk-result h2{font-size:clamp(2rem,5vw,2.8rem)}
[data-baseweb="tab"][aria-selected="true"]{color:#B7D7BA;font-weight:600}
.lk-feature{transition:background-color .16s ease,transform .16s ease}
@media(hover:hover){.lk-feature:hover{background:#344236;transform:translateY(-2px)}}
@media(prefers-reduced-motion:reduce){.lk-feature{transition:none;transform:none!important}}
@media(max-width:600px){.lk-profile{padding:18px;gap:14px;padding-top:62px}.lk-profile-icon{top:18px;right:18px;width:32px;height:32px}.lk-photo{flex-basis:94px;width:94px;height:126px}.lk-profile h2{font-size:1.9rem}.lk-feature{gap:12px}.lk-feature small{font-size:.8rem}}

/* Approved final layouts; retain existing header clearance and native radio styling. */
.lk-hero-icons{display:flex;gap:22px;margin:6px 0 26px}.lk-hero-icons span{width:26px;height:26px}.lk-hero-icons svg{width:100%;height:100%}
.stApp .lk-slogan{font-size:clamp(1.4rem,3.5vw,2rem);font-weight:600;line-height:1.65;margin:16px 0 10px}.lk-intro{font-size:1rem;color:#c1cebf}
.lk-profile{display:block;padding:24px}.lk-profile-top{display:flex;gap:24px;justify-content:space-between;align-items:flex-start}.lk-profile-names{flex:1;min-width:0}.lk-photo{flex:0 0 180px;width:180px;height:180px}.lk-photo img{object-fit:cover}.lk-profile h3{font-size:1.15rem;margin:22px 0 16px;padding:0}.lk-profile-bio{border-top:1px solid #4b604e;margin-top:24px;padding-top:2px;line-height:1.85}.lk-profile-bio p{color:#c6d2c3}.lk-tags{display:flex;gap:8px;flex-wrap:wrap}.lk-tag{margin:0}.lk-grid{margin-bottom:0}.lk-feature{padding:18px 14px;min-height:72px;background:#354638}.lk-feature strong{font-size:1rem;line-height:1.5}.lk-absent .lk-icon{opacity:.65}.lk-result h2{font-size:clamp(2.4rem,6vw,3.3rem)}
.lk-flow{margin:0}.lk-flow li{display:flex;gap:20px;border:0;margin:0;padding:8px 0 38px}.lk-flow li:before{content:'↓';background:none;top:auto;bottom:6px;left:23px;width:auto;height:auto;color:#94b197;font-size:24px}.lk-flow li:last-child{padding-bottom:30px}.lk-step-number{flex:0 0 54px;height:54px;display:flex;align-items:center;justify-content:center;background:#344d3a;border-radius:18px;color:#B7D7BA;font-weight:600}.lk-flow p{margin:8px 0 0;color:#B7D7BA}.lk-path{border:1px solid #415747;border-radius:22px;padding:20px}.lk-path-heading{display:flex;justify-content:space-between;gap:12px;font-size:.84rem;color:#bdceba;margin:0 0 16px}.lk-path-result{position:relative;background:#2d4b35;padding:20px;border-radius:18px}.lk-path-result h2{padding:6px 0;font-size:2rem}.lk-path-result p{margin:0}.lk-path-result .lk-result-icon{top:24px;right:20px}
.lk-nav-card,.lk-catalog-row{display:flex;align-items:center;gap:18px;background:#24352a;border:1px solid #405846;border-radius:22px;padding:18px 20px}.lk-nav-card>span{flex:0 0 28px;height:28px}.lk-nav-card svg{width:100%;height:100%}.lk-nav-card>div,.lk-catalog-row>div{flex:1;min-width:0}.lk-nav-card strong,.lk-catalog-row strong{display:block;font-size:1.08rem}.lk-nav-card small,.lk-catalog-row small{display:block;color:#bdceba;margin-top:7px;font-size:.95rem;overflow-wrap:anywhere}.lk-nav-card b,.lk-catalog-row b{color:#B7D7BA}.st-key-catalog_link,[class*="st-key-catalog_item_"]{position:relative;gap:0!important}.st-key-catalog_link [data-testid="stButton"],[class*="st-key-catalog_item_"] [data-testid="stButton"]{position:absolute;inset:0;width:100%;height:100%}.st-key-catalog_link [data-testid="stButton"] button,[class*="st-key-catalog_item_"] [data-testid="stButton"] button{height:100%;border-radius:22px;background:transparent;border:1px solid transparent;color:transparent}.st-key-catalog_link [data-testid="stButton"] button:hover,[class*="st-key-catalog_item_"] [data-testid="stButton"] button:hover{border-color:#B7D7BA;background:#b7d7ba08}.st-key-catalog_link [data-testid="stButton"] button:focus-visible,[class*="st-key-catalog_item_"] button:focus-visible{outline:2px solid #B7D7BA}
.lk-catalog-heading{position:relative;padding-right:50px}.lk-catalog-heading h1{font-size:clamp(2rem,5vw,2.8rem)}.lk-catalog-heading>span{position:absolute;right:0;top:45px;width:34px;height:34px}.lk-catalog-heading svg{width:100%;height:100%}.lk-catalog-heading p{color:#bfcebb}.st-key-catalog_search [data-baseweb="input"]{border-radius:40px;border:1px solid #536756;padding:6px 12px;background:transparent}.st-key-catalog_search input{background:#202722;border-radius:32px}.lk-list-heading{display:flex;justify-content:space-between;border-top:1px solid #465d4b;padding-top:24px;margin:12px 0 12px}.lk-list-heading span{color:#b9cab7}.lk-catalog-symbol{display:flex;align-items:center;justify-content:center;flex:0 0 64px;width:64px;height:64px;background:#354e3e;border-radius:18px}.lk-catalog-symbol svg{width:34px;height:34px}.lk-empty{padding:28px;text-align:center;background:#24352a;border-radius:20px;color:#c4d3bf}
[data-testid="stBaseButton-pills"],[data-testid="stBaseButton-pillsActive"]{border-radius:30px;padding:10px 16px;border:1px solid #506754;background:#202d24;color:#cbd7c6}
[data-testid="stBaseButton-pillsActive"]{background:#e5ede2;color:#223428;border-color:#e5ede2}
[class*="st-key-catalog_item_"]{margin-bottom:12px}
/* Position the widget wrapper over the card, not inside its zero-height slot. */
.st-key-catalog_link>[data-testid="stElementContainer"]:has(>[data-testid="stButton"]),[class*="st-key-catalog_item_"]>[data-testid="stElementContainer"]:has(>[data-testid="stButton"]){position:absolute;inset:0;height:100%;z-index:1}
@media(max-width:600px){.lk-profile{padding:18px}.lk-profile-top{gap:14px}.lk-photo{flex-basis:100px;width:100px;height:112px}.lk-profile h2{font-size:1.9rem}.lk-profile .lk-placeholder{flex-basis:86px;height:112px}.lk-feature{padding:14px 10px;gap:12px}.lk-feature strong{font-size:.86rem}.lk-profile .lk-grid{gap:10px}.lk-catalog-row{padding:14px;gap:14px}.lk-catalog-symbol{flex-basis:50px;width:50px;height:50px;border-radius:14px}.lk-catalog-symbol svg{width:28px;height:28px}.lk-catalog-row strong{font-size:1rem}.lk-catalog-row small{font-size:.82rem}.lk-flow li{gap:14px}.lk-path{padding:16px}.lk-nav-card{padding:16px}.lk-nav-card strong{font-size:1rem}.lk-path-heading{font-size:.72rem}.lk-manual-label{font-size:.9rem}.lk-manual-label>span:last-child{overflow-wrap:anywhere}}

/* Final polish is scoped to biological states and result details. */
.lk-feature.lk-present{background:#34483A;color:#F1F7F0}.lk-present .lk-icon{color:#B9E0C0;opacity:1}
.lk-feature.lk-absent{background:#2C3730;color:#D0D9D1}.lk-absent .lk-icon{color:#94A89A;opacity:1}
.lk-feature.lk-unknown{background:#303A35;color:#D9E1D9}.lk-unknown .lk-icon{color:#ABB9AF;opacity:1}
.lk-feature strong{color:inherit;white-space:nowrap}
.lk-path-result{padding:12px 64px 12px 16px;border-radius:14px}.lk-path-result h2{font-size:1.55rem;line-height:1.2;padding:3px 0}.lk-path-result small{font-size:.78rem}.lk-path-result p{font-size:.88rem}.lk-path-result .lk-result-icon{width:28px;height:28px;top:50%;right:18px;transform:translateY(-50%)}
.lk-references{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:12px}.lk-reference{display:flex;align-items:flex-start;gap:10px;padding:14px 12px;border:1px solid #405346;border-radius:14px;background:#26332b;min-width:0}.lk-reference-icon{display:flex;flex:0 0 24px;width:24px;height:24px;color:#B7D7BA}.lk-reference-icon svg{width:100%;height:100%}.lk-reference>div{min-width:0}.lk-reference strong{display:block;font-size:.9rem;margin-bottom:7px}.lk-reference a{display:block;font-size:.8rem;line-height:1.6;overflow-wrap:anywhere;margin:4px 0}.lk-reference small{display:block;color:#c2cec1;font-size:.76rem;line-height:1.6}
.lk-model-facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}.lk-model-fact{display:flex;gap:10px;align-items:center;background:#2c3c30;border:1px solid #405346;border-radius:14px;padding:12px 10px;min-width:0}.lk-model-fact>span{display:flex;flex:0 0 24px;width:24px;height:24px;color:#B7D7BA}.lk-model-fact svg{width:100%;height:100%}.lk-model-fact>div{min-width:0}.lk-model-fact small{display:block;color:#bacbb9;font-size:.74rem}.lk-model-fact strong{display:block;font-size:.86rem;margin-top:4px;overflow-wrap:anywhere}
@media(max-width:600px){.lk-references{grid-template-columns:1fr}.lk-model-facts{grid-template-columns:repeat(2,minmax(0,1fr))}.lk-reference{padding:12px}.lk-feature{padding:14px 6px;gap:6px}.lk-feature .lk-icon{flex-basis:20px;width:20px;height:20px}.lk-feature svg{width:20px;height:20px}.lk-feature strong{font-size:.75rem;letter-spacing:-.015em;white-space:normal;min-width:0;overflow-wrap:anywhere}}
</style>'''

def feature_text(row, feature):
    value=row[feature]
    if pd.isna(value): return LABELS[feature]+' · ไม่ทราบ'
    if feature=='Photosynthesis': return 'สังเคราะห์แสงได้' if value else 'สังเคราะห์แสงไม่ได้'
    if feature=='Multicellular organisms': return 'มีหลายเซลล์' if value else 'ไม่มีหลายเซลล์'
    return ('มี' if value else 'ไม่มี')+LABELS[feature]

def feature_html(row):
    cards=[]
    for f in FEATURES:
        state='unknown' if pd.isna(row[f]) else ('present' if row[f] else 'absent')
        cards.append(f'<div class="lk-feature lk-{state}"><span class="lk-icon" aria-hidden="true">{MANUAL_ICONS[f]}</span><strong>{escape(feature_text(row,f))}</strong></div>')
    return '<div class="lk-grid">'+''.join(cards)+'</div>'

def profile(row):
    e=lambda key:escape(str(row[key]))
    info=PROFILES.get(str(row['scientific_name']))
    visual=(f'<div class="lk-photo"><img src="{escape(info["image"],quote=True)}" alt="{escape(info["alt"],quote=True)}" loading="lazy" /></div>' if info else f'<div class="lk-placeholder" role="img" aria-label="ยังไม่มีภาพที่ตรวจสอบสิทธิ์"><span aria-hidden="true">{KINGDOM_ICONS.get(row["Kingdom"], "")}</span>ยังไม่มีภาพที่ตรวจสอบสิทธิ์</div>')
    bio=''
    if info:
        tags=''.join(f'<span class="lk-tag">{escape(f)}</span>' for f in info['facts'])
        bio=f'<div class="lk-profile-bio"><h3>รู้จักสิ่งมีชีวิตชนิดนี้</h3><p>{escape(info["description"])}</p><div class="lk-tags">{tags}</div></div>'
    st.markdown(f"""<section class="lk-profile" aria-label="Species Profile"><div class="lk-profile-top"><div class="lk-profile-names"><div class="lk-kicker">SPECIES PROFILE</div><h2>{escape(row['thai_name'] or row['english_name'] or row['scientific_name'])}</h2><p><i>{e('scientific_name')}</i></p><p>{e('english_name')} · อาณาจักร{escape(KINGDOM_TH[row['Kingdom']])}</p></div>{visual}</div>{bio}<h3>ลักษณะทางชีววิทยา</h3>{feature_html(row)}</section>""",unsafe_allow_html=True)

def feature_cards(row):
    st.markdown(feature_html(row),unsafe_allow_html=True)

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
    st.markdown(f'<section class="lk-result" aria-label="ผลการทำนาย"><span class="lk-result-icon">{KINGDOM_ICONS.get(result, "")}</span><div class="lk-kicker">MODEL PREDICTION</div><h2>{escape(result)}</h2><div class="lk-en">อาณาจักร{escape(KINGDOM_TH.get(result,result))}</div>{compare}</section>',unsafe_allow_html=True)
    with st.expander('ดูเส้นทางการตัดสินใจ',expanded=False):
        steps,leaf=decision_steps(model,X,columns)
        st.markdown(f'<div class="lk-path-heading"><span>DECISION TREE EXPLANATION</span><span>{len(steps)} ขั้นตอน</span></div>',unsafe_allow_html=True)
        items=''.join(f'<li><span class="lk-step-number">{i:02d}</span><div><strong>{QUESTIONS[s["feature"]]}หรือไม่?</strong><p> {"✓ ใช่" if s["value"] else "− ไม่ใช่"}</p></div></li>' for i,s in enumerate(steps,1))
        terminal=f'<div class="lk-path-result"><small>ผลทำนายจากเส้นทางนี้</small><h2>{escape(result)}</h2><span class="lk-result-icon">{KINGDOM_ICONS.get(result, "")}</span><p>อาณาจักร{escape(KINGDOM_TH.get(result,result))}</p></div>'
        st.markdown(f'<div class="lk-path"><ol class="lk-flow" aria-label="เส้นทางการตัดสินใจ">{items}</ol>{terminal}</div>',unsafe_allow_html=True)
        st.caption('แสดงเฉพาะคำถามที่โมเดลใช้จริง ไม่ใช่กฎชีววิทยาครบทุกกรณี')
        with st.expander('รายละเอียดทางเทคนิค',expanded=False):
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

def scope_summary(row):
    scope=str(row['scope'])
    if scope.startswith('ขอบเขต: '):
        return scope.removeprefix('ขอบเขต: ')
    if scope.startswith('Representative living nucleated host cell;'):
        return 'ใช้เซลล์เจ้าบ้านที่มีชีวิตและมีนิวเคลียสเป็นตัวแทน และร่างกายโตเต็มวัยสำหรับจำนวนเซลล์ ไม่รวมสิ่งมีชีวิตร่วมอาศัย สปอร์ เซลล์สืบพันธุ์ ระยะพักตัว และเซลล์พิเศษที่ไม่มีนิวเคลียส ค่าที่ยังไม่มีหลักฐานเฉพาะชนิดแสดงว่าไม่ทราบ'
    if scope.startswith('Mature green plant;'):
        return 'ใช้พืชสีเขียวโตเต็มวัยและเนื้อเยื่อใบที่รับแสง ไม่ครอบคลุมทุกเซลล์ เมล็ด หรือระยะพักตัว'
    if scope.startswith('Juvenile/adult host body'):
        return 'ใช้ร่างกายสัตว์วัยอ่อนหรือโตเต็มวัยและเซลล์ร่างกายที่มีนิวเคลียส ไม่รวมสิ่งมีชีวิตร่วมอาศัย เซลล์สืบพันธุ์ และเม็ดเลือดแดงโตเต็มวัยของสัตว์เลี้ยงลูกด้วยนม'
    scopes={
        'Feeding amoeboid cell; excludes cyst':'ใช้เซลล์อะมีบาระยะกินอาหาร ไม่รวมระยะซีสต์',
        'Green photosynthetic gametophyte':'ใช้ระยะแกมีโทไฟต์สีเขียวที่สังเคราะห์แสง',
        'Green photosynthetic multicellular gametophyte':'ใช้ระยะแกมีโทไฟต์หลายเซลล์สีเขียวที่สังเคราะห์แสง',
        'Green photosynthetic sporophyte':'ใช้ระยะสปอโรไฟต์สีเขียวที่สังเคราะห์แสง',
        'Green photosynthetic sporophyte representative':'ใช้ตัวแทนระยะสปอโรไฟต์สีเขียวที่สังเคราะห์แสง',
        'Green photosynthetic sporophyte tissue':'ใช้เนื้อเยื่อระยะสปอโรไฟต์สีเขียวที่สังเคราะห์แสง',
        'Multicellular photosynthetic thallus':'ใช้ทัลลัสหลายเซลล์ที่สังเคราะห์แสง',
        'Multicellular photosynthetic thallus/blade representative':'ใช้ตัวแทนทัลลัสหรือแผ่นสาหร่ายหลายเซลล์ที่สังเคราะห์แสง',
        'Multicellular photosynthetic thallus; excludes gametes':'ใช้ทัลลัสหลายเซลล์ที่สังเคราะห์แสง ไม่รวมเซลล์สืบพันธุ์',
        'Representative animal body; cell traits inferred if referring to extinct non-avian dinosaurs':'ใช้ตัวแทนร่างกายสัตว์ หากหมายถึงไดโนเสาร์ที่สูญพันธุ์และไม่ใช่นก คุณลักษณะระดับเซลล์เป็นการอนุมาน',
        'Representative juvenile/adult host body and normal somatic cell; excludes symbiont traits':'ใช้ตัวแทนร่างกายสัตว์วัยอ่อนหรือโตเต็มวัยและเซลล์ร่างกายปกติ ไม่รวมคุณลักษณะของสิ่งมีชีวิตร่วมอาศัย',
        'Single-celled vegetative yeast form; excludes hyphal/pseudohyphal forms':'ใช้ยีสต์เซลล์เดียวระยะเจริญ ไม่รวมรูปแบบเส้นใยหรือเส้นใยเทียม',
        'Trophozoite':'ใช้ระยะโทรโฟซอยต์ที่กำลังกินอาหารและเจริญ',
        'Trophozoite only; excludes cyst':'ใช้เฉพาะระยะโทรโฟซอยต์ ไม่รวมซีสต์',
        'Vegetative bacterial cell':'ใช้เซลล์แบคทีเรียระยะเจริญ',
        'Vegetative bacterial cell; not an endospore representation':'ใช้เซลล์แบคทีเรียระยะเจริญ ไม่ใช้เอนโดสปอร์เป็นตัวแทน',
        'Vegetative ciliate host cell; excludes algal symbiont traits':'ใช้เซลล์ซิลิเอตระยะเจริญ ไม่รวมคุณลักษณะของสาหร่ายร่วมอาศัย',
        'Vegetative cyanobacterial filament/colony; not every specialized cell':'ใช้เส้นสายหรือโคโลนีไซยาโนแบคทีเรียระยะเจริญ ไม่ครอบคลุมเซลล์เฉพาะทางทุกเซลล์',
        'Vegetative cyanobacterial filament; photosynthetic capability of filament, not every specialized cell':'ใช้เส้นสายไซยาโนแบคทีเรียระยะเจริญ ประเมินการสังเคราะห์แสงระดับเส้นสาย ไม่ใช่ทุกเซลล์เฉพาะทาง',
        'Vegetative mycelium / fruiting body fungal convention':'ใช้เส้นใยระยะเจริญหรือดอกเห็ดตามขอบเขตของกลุ่มรา',
        'Vegetative mycelium / fruiting body of shiitake; not a single spore':'ใช้เส้นใยระยะเจริญหรือดอกเห็ดหอม ไม่ใช้สปอร์เดี่ยวเป็นตัวแทน',
        'Vegetative photosynthetic cell under light':'ใช้เซลล์ระยะเจริญที่สังเคราะห์แสงเมื่อได้รับแสง',
        'Vegetative photosynthetic cyanobacterial filament':'ใช้เส้นสายไซยาโนแบคทีเรียระยะเจริญที่สังเคราะห์แสง',
        'Vegetative photosynthetic diatom cell with silica frustule':'ใช้เซลล์ไดอะตอมระยะเจริญที่สังเคราะห์แสงและมีเปลือกซิลิกา',
        'Vegetative photosynthetic filament':'ใช้เส้นสายระยะเจริญที่สังเคราะห์แสง',
        'Vegetative photosynthetic haploid 10D culture; excludes cell-walled diploid':'ใช้เซลล์เพาะเลี้ยงแฮพลอยด์สายพันธุ์ 10D ระยะเจริญที่สังเคราะห์แสง ไม่รวมระยะดิพลอยด์ที่มีผนังเซลล์',
        'Vegetative photosynthetic wild-type cell under light':'ใช้เซลล์สายพันธุ์ปกติระยะเจริญที่สังเคราะห์แสงเมื่อได้รับแสง',
        'Vegetative unicellular ciliate':'ใช้ซิลิเอตเซลล์เดียวระยะเจริญ',
        'Vegetative unicellular photosynthetic cell':'ใช้เซลล์เดียวระยะเจริญที่สังเคราะห์แสง',
    }
    return scopes.get(scope,'ใช้ขอบเขตระยะชีวิตและชนิดเซลล์ที่ระบุในข้อมูลอ้างอิงของรายการนี้')

def reference_links(urls, label=None):
    labels={'gbif.org':'GBIF','api.gbif.org':'GBIF','animaldiversity.org':'Animal Diversity Web · University of Michigan','ntbg.org':'National Tropical Botanical Garden','openstax.org':'OpenStax','jircas.go.jp':'JIRCAS','scimath.org':'Scimath'}
    links=[]
    for url in dict.fromkeys(urls):
        if not url.startswith('https://'): continue
        host=urlparse(url).netloc.removeprefix('www.')
        title=escape(label or labels.get(host,host))
        links.append(f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{title} ↗</a>')
    return ''.join(links)

def evidence(row,columns):
    with st.expander('แหล่งอ้างอิงและเครดิตภาพ',expanded=False):
        info=PROFILES.get(str(row['scientific_name']))
        names=reference_links(row['name_sources'].split('|'))
        biology=reference_links(row['feature_sources'].split('|')+([info['source']] if info else []))
        photo=(reference_links([info['image_source']],info['credit'])+reference_links([info['license_url']],info['license'])+'<small>ครอปภาพเพื่อจัดวาง</small>') if info else '<small>ยังไม่มีภาพถ่ายที่ตรวจสอบสิทธิ์ ใช้ไอคอนอาณาจักรแทน</small>'
        sections=[('ชื่อและอนุกรมวิธาน',names,BOOK_ICON),('ข้อมูลชีววิทยา',biology,MANUAL_ICONS['Nucleus']),('เครดิตภาพ',photo,MANUAL_ICONS['Cell wall'])]
        st.markdown('<div class="lk-references">'+''.join(f'<section class="lk-reference"><span class="lk-reference-icon" aria-hidden="true">{icon}</span><div><strong>{title}</strong>{links}</div></section>' for title,links,icon in sections)+'</div>',unsafe_allow_html=True)
        with st.expander('หลักฐานและขอบเขตคุณลักษณะ',expanded=False):
            inferred='group' in str(row['evidence_basis']).lower()
            st.write(('คุณลักษณะเป็นการอนุมานระดับกลุ่ม ไม่ใช่ผลวัดแยกรายชนิดทั้ง 6 ข้อ ' if inferred else 'คุณลักษณะอ้างอิงตามระยะชีวิตและชนิดเซลล์ที่ระบุ ')+scope_summary(row))
            if str(row['id']).startswith('train-'):
                st.caption('รายการเดิมใช้หลักฐาน audit ของโครงงาน การตรวจชื่อรอบนี้ไม่ได้ยืนยันหลักฐานคุณลักษณะรายข้อใหม่ทั้งหมด')
            if 'Northern bounding-box occurrence' in str(row['uncertainty']):
                st.caption('มีรายงานพบในกรอบพิกัดภาคเหนือจาก GBIF ไม่ใช่การยืนยันว่าเป็นชนิดพื้นเมือง ชื่อสามัญอาจใช้ร่วมกับชนิดอื่นได้')
            for f in columns:
                st.markdown('**'+feature_text(row,f)+'**')
                reason=thai_evidence(str(row[f+'_evidence'])).removeprefix('อนุมานระดับกลุ่ม: ')
                if '�' in reason:
                    st.caption('ตรวจรายละเอียดคุณลักษณะข้อนี้จากแหล่งข้อมูลชีววิทยาของรายการ หลักฐานต้นฉบับคงอยู่ใน CSV')
                else:
                    st.caption(reason)
            st.caption('ตรวจหลักฐาน: '+str(row['verified_on'])+' · ขอบเขตและหลักฐานต้นฉบับคงอยู่ในข้อมูล CSV พร้อมแหล่งอ้างอิง')
            if '�' in str(row['uncertainty']):
                st.caption('ข้อความต้นฉบับบางส่วนมีอักขระผิดรูป จึงแสดงลิงก์แหล่งข้อมูลแทนโดยไม่แก้ไขต้นฉบับ')

def about_model(training_count,catalog_count,python_version,sklearn_version,streamlit_version):
    with st.expander('เกี่ยวกับโมเดลและชุดข้อมูล',expanded=False):
        cards=[('โมเดล','Decision Tree',BOOK_ICON),('ระบบจำแนก','5 อาณาจักร',MANUAL_ICONS['Nucleus']),('ข้อมูลต้นฉบับ',f'{training_count} รายการ',MANUAL_ICONS['Multicellular organisms']),('แค็ตตาล็อกค้นหา',f'{catalog_count} รายการ',MANUAL_ICONS['Ribosome'])]
        st.markdown('<div class="lk-model-facts">'+''.join(f'<div class="lk-model-fact"><span aria-hidden="true">{icon}</span><div><small>{label}</small><strong>{value}</strong></div></div>' for label,value,icon in cards)+'</div>',unsafe_allow_html=True)
        st.write('โมเดลใช้คุณลักษณะทางชีววิทยา 6 ข้อเพื่อจำแนกสิ่งมีชีวิตตามระบบ 5 อาณาจักรของโครงงาน')
        st.write('ผลทำนายอาจแตกต่างจากข้อมูลอ้างอิง และการเพิ่มรายการในแค็ตตาล็อกไม่ได้หมายถึงการฝึกโมเดลใหม่')
        with st.expander('รายละเอียดและข้อจำกัดของโมเดล',expanded=False):
            st.write('ระบบ 5 อาณาจักรเป็นกรอบของโครงงาน ไม่เท่ากับการจัดอนุกรมวิธานสมัยใหม่ในทุกกรณี คุณลักษณะเดียวกันอาจพบได้ต่างอาณาจักร เช่น Spirogyra')
            st.write('ยังไม่มีผลประเมินความแม่นยำกับแค็ตตาล็อกใหม่ จึงไม่แสดงคะแนนที่ตรวจสอบไม่ได้ ไม่ได้ฝึกโมเดลใหม่หรือแก้ข้อมูลฝึกเดิม')
            st.write('ค่าอ้างอิงใช้ระยะชีวิตและชนิดเซลล์ที่ระบุ ค่าที่ไม่ทราบไม่แทนด้วย 0 และไม่ส่งทำนาย คุณลักษณะของรายการใหม่บางส่วนเป็นการอนุมานระดับกลุ่มโดยมีแหล่งอ้างอิง')
            st.caption(f'Python {python_version} · scikit-learn {sklearn_version} · Streamlit {streamlit_version}')
