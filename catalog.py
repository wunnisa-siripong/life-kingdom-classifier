"""Search catalogue: no training and no imputation of unknown features."""
import unicodedata
import pandas as pd
FEATURES = ['Ribosome','Photosynthesis','Nucleus','Cell wall','Chloroplast','Multicellular organisms']
KINGDOMS = {'Monera','Protista','Fungi','Plantae','Animalia'}
def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC',str(value)).split()).casefold()
def names(row):
    return [str(row[k]) for k in ['thai_name','english_name','scientific_name'] if row[k]]+str(row['aliases']).split('|')
def search(catalog,query):
    q=normalize(query)
    if not q: return catalog.iloc[0:0]
    exact=catalog.apply(lambda r:any(normalize(n)==q for n in names(r) if n),axis=1)
    if exact.any(): return catalog.loc[exact]
    return catalog.loc[catalog.apply(lambda r:any(q in normalize(n) for n in names(r) if n),axis=1)]
def read_catalog(path):
    data=pd.read_csv(path,encoding='utf-8-sig',keep_default_na=False)
    required={'id','thai_name','english_name','scientific_name','aliases','Kingdom','rank','scope','uncertainty','name_sources','feature_sources','evidence_basis','verified_on',*FEATURES}
    if not required.issubset(data.columns): raise ValueError('Missing catalogue columns')
    if data['id'].duplicated().any(): raise ValueError('Duplicate IDs')
    if data['id'].eq('').any(): raise ValueError('Empty ID')
    unknown_name=data['scientific_name'].eq('')
    if (unknown_name & (~data['rank'].str.contains('growth form',case=False) | data['english_name'].eq(''))).any():
        raise ValueError('Unexplained missing scientific name')
    if data.loc[~unknown_name,'scientific_name'].map(normalize).duplicated().any(): raise ValueError('Duplicate scientific names')
    if not set(data['Kingdom']).issubset(KINGDOMS): raise ValueError('Unexpected kingdom')
    for col in FEATURES:
        # Only an empty cell means unknown. Never silently turn bad input into null.
        if not data[col].astype(str).isin(['','0','1']).all(): raise ValueError('Invalid binary feature: '+col)
        data[col]=pd.to_numeric(data[col],errors='coerce').astype('Int64')
        if col+'_evidence' not in data: raise ValueError('Missing feature evidence')
        if data[col+'_evidence'].str.strip().eq('').any(): raise ValueError('Empty feature evidence')
    if (data[['scope','feature_sources','name_sources']]=='').any().any(): raise ValueError('Missing scope/sources')
    return data
def option_label(row):
    primary=row['thai_name'] or row['english_name'] or row['scientific_name']
    return primary+(' · '+row['scientific_name'] if row['scientific_name'] and row['scientific_name']!=primary else '')
def prediction_input(values,columns):
    if len(columns)!=6 or set(columns)!=set(FEATURES): raise ValueError('Unexpected model features')
    if any(pd.isna(values[c]) or values[c] not in (0,1) for c in columns):
        raise ValueError('ไม่ทราบคุณลักษณะครบทั้ง 6 ข้อ จึงยังไม่ทำนาย')
    return pd.DataFrame([[int(values[c]) for c in columns]],columns=columns)
