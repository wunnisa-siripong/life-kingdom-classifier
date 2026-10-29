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
            b=path.read_bytes(); b=b.replace(b'\r\n',b'\n') if path.suffix=='.csv' else b;return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        self.assertEqual(git_sha(BASE/'organisms.csv'),'53311374e7c0787131df5e81446564d0d1a5815a')
        self.assertEqual(git_sha(BASE/'life_kingdom_model.joblib'),'3aeef574a4c65a3de51a07b47fbd4ee4de15f2de')
    def test_scope_and_sources(self):
        summary=json.loads((BASE/'evidence/catalog_audit/summary.json').read_text(encoding='utf8'))
        self.assertEqual(len(self.data),summary['total'])
        self.assertGreaterEqual(summary['new'],300)
        self.assertEqual(set(self.data.Kingdom),KINGDOMS)
        self.assertEqual(len(set(self.data.apply(option_label,axis=1))),len(self.data))
        self.assertTrue(self.data[FEATURES].isna().any().any())
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
        X=self.data.dropna(subset=cols)[cols].astype(int)
        predicted=model.predict(X)
        self.assertEqual(len(predicted),len(X))
        sp=self.data.loc[self.data.english_name.eq('Spirogyra')].iloc[0]
        self.assertEqual(sp.Kingdom,'Protista')
        self.assertEqual(model.predict(prediction_input(sp,cols))[0],'Plantae')
        all_vectors=pd.DataFrame(itertools.product([0,1],repeat=6),columns=cols)
        self.assertEqual(len(model.predict(all_vectors)),64)
        with self.assertRaises(ValueError): prediction_input(dict.fromkeys(FEATURES,None),cols)
        with self.assertRaises(ValueError): prediction_input(dict.fromkeys(FEATURES,2),cols)

    def test_requested_names_and_group_scope(self):
        requested=['เห็ดหล่ม','ซุกซุ่น','หน่อ','หน่อไม้','ผักปลัง','ปู','คน','พยาธิ','ไฮดรา',
                   'เชื้อรา','ยูกลีนา','สาหร่ายสีเขียว','สาหร่ายสีเขียว น้ำเงิน','ยีสต์','รา','พืชดอก',
                   'แมงกะพรุน','ดอกไม้ทะเล','ปะการัง','พยาธิใบไม้','พยาธิตัวตืด','พลานาเรีย',
                   'พยาธิไส้เดือน','พยาธิเส้นด้าย','พยาธิปากขอ','หอย','หมึก','แมลง','กุ้ง','แมงมุม',
                   'ตะขาบ','ปลาดาว','เม่นทะเล','ปลิงทะเล','ปลา','สัตว์สะเทินน้ำสะเทินบก','กบ',
                   'สัตว์เลื้อยคลาน','งู','จระเข้','สัตว์ปีก','นก','สัตว์เลี้ยงลูกด้วยน้ำนม','มนุษย์']
        for q in requested:
            with self.subTest(query=q): self.assertFalse(search(self.data,q).empty)
        for q,expected in [('คน','Homo sapiens'),('ไฮดรา','Hydra spp.'),('ยูกลีนา','Euglena gracilis')]:
            self.assertEqual(search(self.data,q).iloc[0].scientific_name,expected)
        for q in ['หน่อไม้','ซุกซุ่น','เชื้อรา','รา','สาหร่ายสีเขียว','สาหร่ายสีเขียว น้ำเงิน','พืชดอก']:
            with self.subTest(unknown_group=q):
                row=search(self.data,q).iloc[0]
                self.assertTrue(row[FEATURES].isna().any())
                with self.assertRaises(ValueError): prediction_input(row,self.package['features'])
        self.assertEqual(search(self.data,'ซุกซุ่น').iloc[0].scientific_name,'')
        self.assertIn('ยังไม่มีหลักฐาน',search(self.data,'ซุกซุ่น').iloc[0].scope)
        from requested_catalog import apply_requested
        for _,row in self.data[self.data.id.str.startswith('request-')].iterrows():
            for f in FEATURES: self.assertNotIn('|https://',row[f+'_evidence'])
        rows=json.loads((BASE/'evidence/catalog_audit/curated_catalog.json').read_text(encoding='utf8'))
        report=json.loads((BASE/'evidence/catalog_audit/row_report.json').read_text(encoding='utf8'))
        before=json.dumps(rows,sort_keys=True)
        apply_requested(rows,report)
        self.assertEqual(before,json.dumps(rows,sort_keys=True))
    def test_ui(self):
        def app_for(view='home', **state):
            app=AppTest.from_file(str(BASE/'streamlit_app.py'),default_timeout=20)
            app.session_state['view']=view
            for key,value in state.items(): app.session_state[key]=value
            app.run()
            self.assertEqual(len(app.exception),0)
            return app
        app=app_for()
        next(b for b in app.button if b.label=='ทำนายอาณาจักร').click().run()
        self.assertTrue(any('ครบทั้ง 6' in w.value for w in app.warning))
        for radio in app.radio: radio.set_value('ใช่')
        next(b for b in app.button if b.label=='ทำนายอาณาจักร').click().run()
        self.assertTrue(any('section class="lk-result"' in m.value and 'Plantae' in m.value for m in app.markdown))
        self.assertTrue(any('6/6' in m.value for m in app.markdown))
        result=next(m.value for m in app.markdown if 'section class="lk-result"' in m.value)
        self.assertNotIn('สอดคล้อง',result)
        self.assertNotIn('ข้อมูลอ้างอิง',result)
        next(b for b in app.button if b.label=='ล้างคำตอบ').click().run()
        self.assertTrue(all(r.value is None for r in app.radio))
        self.assertFalse(any('section class="lk-result"' in m.value for m in app.markdown))
        for q,kingdom in [('มะม่วง','Plantae'),('แมว','Animalia'),('Spirogyra','Plantae')]:
            row=search(self.data,q).iloc[0]
            profile=app_for('profile',selected_id=row['id'])
            result=next(m.value for m in profile.markdown if 'section class="lk-result"' in m.value)
            self.assertIn(kingdom,result)
            if q=='Spirogyra':
                self.assertIn('Protista',result); self.assertIn('ผลต่างกัน',result)
            self.assertTrue(any('lk-profile' in m.value and '<img' in m.value for m in profile.markdown))
        for label,kingdom in [('พืช','Plantae'),('สัตว์','Animalia'),('เห็ดรา','Fungi'),('โพรทิสตา','Protista'),('มอเนอรา','Monera')]:
            listing=app_for('catalog',kingdom_filter=label,catalog_query='')
            self.assertTrue(any('รายการสิ่งมีชีวิต' in m.value and str(sum(self.data.Kingdom.eq(kingdom))) in m.value for m in listing.markdown))
        listing=app_for('catalog',kingdom_filter='สัตว์',catalog_query='cat')
        # Streamlit 1.50's AppTest exposes single-select pills as a ButtonGroup.
        listing.get('button_group')[0].set_value(['สัตว์'])
        target=next(b for b in listing.button if b.key and b.key.startswith('open_'))
        target.click().run()
        self.assertEqual(listing.session_state['view'],'profile')
        next(b for b in listing.button if b.label=='← กลับไปแค็ตตาล็อก').click().run()
        self.assertEqual(listing.session_state['kingdom_filter'],'สัตว์')
        self.assertEqual(listing.session_state['catalog_query'],'cat')
        empty=app_for('catalog',catalog_query='not-a-real-organism-999')
        self.assertTrue(any('ไม่พบรายการ' in m.value for m in empty.markdown))
        empty.get('button_group')[0].set_value(['ทั้งหมด'])
        next(b for b in empty.button if b.label=='ล้างตัวกรอง').click().run()
        self.assertEqual(empty.session_state['catalog_query'],'')
        self.assertEqual(empty.session_state['kingdom_filter'],'ทั้งหมด')
        second=app_for('catalog',catalog_page=2)
        self.assertEqual(len([b for b in second.button if b.key and b.key.startswith('open_')]),18)
        self.assertEqual(second.session_state['catalog_page'],2)
        from ui import feature_html
        unknown=self.data.iloc[0].copy()
        unknown['Cell wall']=pd.NA
        self.assertIn('ผนังเซลล์ · ไม่ทราบ',feature_html(unknown))

    def test_polish(self):
        from ui import feature_html,feature_text,scope_summary
        cat=search(self.data,'แมว').iloc[0]
        html=feature_html(cat)
        self.assertEqual(html.count('lk-present'),3)
        self.assertEqual(html.count('lk-absent'),3)
        self.assertIn('สังเคราะห์แสงไม่ได้',html)
        self.assertIn('ไม่มีคลอโรพลาสต์',html)
        unknown=cat.copy(); unknown['Cell wall']=pd.NA
        self.assertIn('lk-unknown',feature_html(unknown))
        self.assertEqual(feature_text(unknown,'Cell wall'),'ผนังเซลล์ · ไม่ทราบ')
        self.assertTrue(all(scope_summary(row) for _,row in self.data.iterrows()))
        app=AppTest.from_file(str(BASE/'streamlit_app.py'),default_timeout=20)
        app.session_state['view']='profile';app.session_state['selected_id']=cat['id']
        app.run()
        self.assertEqual(len(app.exception),0)
        expanders={e.proto.label:e for e in app.get('expander')}
        self.assertNotIn('ภาพและข้อมูลพร้อมแหล่งอ้างอิง',expanders)
        for label in ['ดูเส้นทางการตัดสินใจ','แหล่งอ้างอิงและเครดิตภาพ','เกี่ยวกับโมเดลและชุดข้อมูล','รายละเอียดทางเทคนิค','หลักฐานและขอบเขตคุณลักษณะ','รายละเอียดและข้อจำกัดของโมเดล']:
            self.assertIn(label,expanders)
            self.assertFalse(expanders[label].proto.expanded)
        self.assertEqual(len([e for e in app.get('expander') if e.proto.label=='แหล่งอ้างอิงและเครดิตภาพ']),1)
        facts=next(m.value for m in app.markdown if 'lk-model-facts' in m.value and '<div' in m.value)
        self.assertIn('50 รายการ',facts);self.assertIn(f'{len(self.data)} รายการ',facts)
        credits=next(m.value for m in app.markdown if '<div class="lk-references"' in m.value)
        self.assertIn('Clumsyninja',credits);self.assertIn('creativecommons.org/licenses/by-sa/4.0/',credits)

    def test_paths(self):
        from ui import decision_steps
        model,cols=self.package['model'],list(self.package['features'])
        for vector in itertools.product([0,1],repeat=6):
            X=pd.DataFrame([vector],columns=cols)
            steps,leaf=decision_steps(model,X,cols)
            self.assertEqual([s['node'] for s in steps]+[leaf],list(model.decision_path(X).indices))

    def test_unknown_profile_and_names(self):
        row=self.data.loc[self.data[FEATURES].isna().any(axis=1)].iloc[0]
        with self.assertRaises(ValueError): prediction_input(row,self.package['features'])
        app=AppTest.from_file(str(BASE/'streamlit_app.py'),default_timeout=20)
        app.session_state['view']='profile';app.session_state['selected_id']=row['id'];app.run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('ยังไม่ทำนาย' in w.value for w in app.warning))
        self.assertFalse(any('section class="lk-result"' in m.value for m in app.markdown))
        self.assertTrue(any('lk-unknown' in m.value for m in app.markdown))
        for _,r in self.data.iterrows():
            if r['scientific_name']: self.assertIn(r['id'],set(search(self.data,r['scientific_name'])['id']))
            if r['thai_name']: self.assertIn(r['id'],set(search(self.data,r['thai_name'])['id']))
        monarch=search(self.data,'Danaus plexippus').iloc[0]
        self.assertEqual(monarch['english_name'].casefold(),'monarch butterfly')

    def test_reject_invalid_feature(self):
        import tempfile
        raw=pd.read_csv(BASE/'organism_catalog.csv',keep_default_na=False)
        for bad in ['banana','2','-1','0.5']:
            raw.loc[0,FEATURES[0]]=bad
            with tempfile.TemporaryDirectory(dir=BASE) as folder:
                path=Path(folder)/'invalid.csv';raw.to_csv(path,index=False)
                with self.assertRaises(ValueError): read_catalog(path)

    def test_catalog_cache_refresh_after_csv_change(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory(dir=BASE) as folder:
            root=Path(folder)
            for name in ['streamlit_app.py','catalog.py','ui.py','species.py','organisms.csv','organism_catalog.csv','life_kingdom_model.joblib']:
                shutil.copyfile(BASE/name,root/name)
            shutil.copytree(BASE/'search_component',root/'search_component')
            app=AppTest.from_file(str(root/'streamlit_app.py'),default_timeout=20).run()
            self.assertEqual(len(app.exception),0)
            self.assertTrue(any(f'ดูข้อมูลทั้งหมด {len(self.data)} รายการ' in m.value for m in app.markdown))
            raw=pd.read_csv(root/'organism_catalog.csv',keep_default_na=False)
            raw.iloc[:-1].to_csv(root/'organism_catalog.csv',index=False,encoding='utf-8-sig')
            app.run()
            self.assertEqual(len(app.exception),0)
            self.assertTrue(any(f'ดูข้อมูลทั้งหมด {len(self.data)-1} รายการ' in m.value for m in app.markdown))

if __name__=='__main__': unittest.main(verbosity=2)
