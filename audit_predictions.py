"""Compare reference labels with the unchanged model; never score them as accuracy."""
import json
from pathlib import Path
import joblib
from catalog import read_catalog, prediction_input, FEATURES
BASE=Path(__file__).resolve().parent

def run():
    data=read_catalog(BASE/'organism_catalog.csv')
    package=joblib.load(BASE/'life_kingdom_model.joblib')
    results=[]
    for _,r in data.iterrows():
        item=dict(id=r['id'],scientific_name=r['scientific_name'],reference=r['Kingdom'])
        try:
            X=prediction_input(r,package['features'])
            item['prediction']=str(package['model'].predict(X)[0])
            item['status']='match' if item['prediction']==r['Kingdom'] else 'mismatch'
            item['path_nodes']=[int(n) for n in package['model'].decision_path(X).indices]
        except ValueError:
            item.update(status='not_predicted_unknown',unknown_traits=[f for f in FEATURES if r[f] is None or __import__('pandas').isna(r[f])])
        results.append(item)
    report=dict(counts={s:sum(r['status']==s for r in results) for s in ['match','mismatch','not_predicted_unknown']},
                interpretation='Reference comparison only; shared six-trait combinations are not biological identification or an independent accuracy evaluation.',rows=results)
    (BASE/'evidence/catalog_audit/prediction_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(report['counts'])

if __name__=='__main__':run()
