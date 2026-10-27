"""Run with Python 3.12 and requirements.txt; never retrains the model."""
import hashlib, itertools, json, sys, unittest
from pathlib import Path
import joblib
import pandas as pd
from streamlit.testing.v1 import AppTest
from catalog import FEATURES,KINGDOMS,normalize,read_catalog,search,option_label,prediction_input
BASE=Path(__file__).resolve().parent

class CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read_catalog(BASE/'organism_catalog.csv')
        cls.package=joblib.load(BASE/'life_kingdom_model.joblib')
    def test_original_files(self):
        def git_sha(path):
            b=path.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        self.assertEqual(git_sha(BASE/'organisms.csv'),'53311374e7c0787131df5e81446564d0d1a5815a')
        self.assertEqual(git_sha(BASE/'life_kingdom_model.joblib'),'3aeef574a4c65a3de51a07b47fbd4ee4de15f2de')
    def test_scope_and_sources(self):
        self.assertEqual(len(self.data),117)
        self.assertEqual(set(self.data.Kingdom),KINGDOMS)
        self.assertEqual(len(set(self.data.apply(option_label,axis=1))),len(self.data))
        self.assertTrue(self.data[FEATURES].notna().all().all())
        for f in FEATURES: self.assertTrue(self.data[f+'_evidence'].str.len().gt(0).all())
    def test_names(self):
        for q in ['มะม่วง','MANGO','mAnGiFeRa   indica','มะม่วงสวน']:
            self.assertEqual(search(self.data,q).iloc[0].scientific_name,'Mangifera indica')
        for q in ['แมว','DOMESTIC CAT','Felis catus']:
            self.assertEqual(search(self.data,q).iloc[0].scientific_name,'Felis catus')
        self.assertTrue(search(self.data,'not-a-real-organism-999').empty)
        self.assertTrue(search(self.data,'   ').empty)
        self.assertGreater(len(search(self.data,'sativ')),1)
    def test_real_model(self):
        model,cols=self.package['model'],self.package['features']
        X=self.data[cols].astype(int)
        predicted=model.predict(X)
        self.assertEqual(len(predicted),117)
        sp=self.data.loc[self.data.english_name.eq('Spirogyra')].iloc[0]
        self.assertEqual(sp.Kingdom,'Protista')
        self.assertEqual(model.predict(prediction_input(sp,cols))[0],'Plantae')
        all_vectors=pd.DataFrame(itertools.product([0,1],repeat=6),columns=cols)
        self.assertEqual(len(model.predict(all_vectors)),64)
        with self.assertRaises(ValueError): prediction_input(dict.fromkeys(FEATURES,None),cols)
        with self.assertRaises(ValueError): prediction_input(dict.fromkeys(FEATURES,2),cols)
    def test_ui(self):
        app=AppTest.from_file(str(BASE/'streamlit_app.py'),default_timeout=20).run()
        self.assertEqual(len(app.exception),0)
        for q,kingdom in [('มะม่วง','Plantae'),('MANGO','Plantae'),('Felis catus','Animalia'),('อะมีบา','Protista')]:
            label=option_label(search(self.data,q).iloc[0])
            app.selectbox[0].select(label).run()
            self.assertEqual(len(app.exception),0)
            self.assertIn(kingdom,[m.value for m in app.metric])
        app.selectbox[0].select(option_label(search(self.data,'Spirogyra').iloc[0])).run()
        self.assertEqual([m.value for m in app.metric],['Protista','Plantae'])
        self.assertTrue(any('ผลต่างกัน' in w.value for w in app.warning))
        # AppTest 1.50 cannot submit new selectbox options. No-match is tested
        # by search() above and through the deployed browser UI.
        app.selectbox[0].set_value(None).run()
        self.assertEqual(len(app.metric),0)
        app.button[0].click().run()
        self.assertTrue(any('ครบทั้ง 6' in w.value for w in app.warning))
        for radio in app.radio: radio.set_value('ใช่')
        app.button[0].click().run()
        self.assertTrue(any('Plantae' in s.value for s in app.success))
        self.assertEqual(len(app.exception),0)

if __name__=='__main__': unittest.main(verbosity=2)
