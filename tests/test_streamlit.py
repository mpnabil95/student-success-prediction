"""UI regressions: navigation, validation, input state, and batch source changes."""
import json
import unittest
from pathlib import Path
import pandas as pd
from student_success.config import DATA_PATH
from student_success.inference import load_bundle, predict_frame
from student_success.schema import defaults
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None
ROOT = Path(__file__).resolve().parents[1]

@unittest.skipIf(AppTest is None, 'Streamlit not installed in this runtime')
class StreamlitIntegrationTests(unittest.TestCase):
    def app(self, page=None):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60).run()
        if page:
            app.sidebar.radio[0].set_value(page).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def click(self, app, label):
        next(b for b in app.button if b.label == label).click().run()
        self.assertEqual(len(app.exception), 0)

    def radio(self, app, label, value):
        next(r for r in app.radio if r.label == label).set_value(value).run()
        self.assertEqual(len(app.exception), 0)

    def test_pages_and_individual_prediction(self):
        app = self.app()
        for page in ['Prediksi Individu', 'Prediksi Batch', 'Kinerja Model']:
            app.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(app.exception), 0)
        app.sidebar.radio[0].set_value('Prediksi Individu').run()
        self.click(app, 'Lihat hasil peninjauan')
        self.assertTrue(any(m.label == 'Probabilitas Dropout' for m in app.metric))

    def test_chart_padding_is_compatible_with_streamlit_renderer(self):
        # AppTest does not run the browser renderer. Check its actual serialized
        # input: Streamlit 1.49.1 assigns spec.padding.bottom, so a scalar fails.
        app = self.app()
        for page in ['Gambaran Data', 'Prediksi Individu', 'Kinerja Model']:
            app.sidebar.radio[0].set_value(page).run()
            if page == 'Prediksi Individu':
                self.click(app, 'Lihat hasil peninjauan')
            self.assertEqual(len(app.exception), 0)
            charts = app.get('arrow_vega_lite_chart')
            self.assertGreater(len(charts), 0, page)
            for index, element in enumerate(charts):
                with self.subTest(page=page, chart=index):
                    spec = json.loads(element.proto.spec)
                    padding = spec.get('padding')
                    self.assertIsInstance(padding, dict)
                    self.assertTrue({'left', 'right', 'top', 'bottom'} <= padding.keys())
                    for side in ['left', 'right', 'top', 'bottom']:
                        self.assertIsInstance(padding[side], (int, float))
                        self.assertGreaterEqual(padding[side], 0)

    def test_chart_expressions_are_browser_safe(self):
        app = self.app('Kinerja Model')
        charts = app.get('arrow_vega_lite_chart')
        self.assertGreater(len(charts), 0)
        for index, element in enumerate(charts):
            with self.subTest(chart=index):
                serialized = element.proto.spec
                self.assertNotIn('np.', serialized)
                self.assertNotIn('numpy.', serialized)

    def test_overview_empty_filter_and_reset(self):
        app = self.app()
        data = pd.read_csv(DATA_PATH, sep=';')
        course = next(int(c) for c in data.Course.unique() if data.loc[data.Course.eq(c), 'Age_at_enrollment'].max() < 70)
        app.multiselect(key='overview_courses').set_value([course])
        app.slider(key='overview_age').set_value((70, 70)).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any('Belum ada data dalam pilihan ini' in m.value for m in app.markdown))
        self.click(app, 'Reset filter')
        self.assertEqual(app.multiselect(key='overview_courses').value, [])
        self.assertEqual(app.slider(key='overview_age').value, (17, 70))
        self.assertEqual(next(m.value for m in app.metric if m.label == 'Mahasiswa dalam filter'), '4.424')

    def test_individual_matches_shared_inference(self):
        app = self.app('Prediksi Individu')
        self.click(app, 'Lihat hasil peninjauan')
        model, manifest = load_bundle()
        expected = predict_frame(pd.DataFrame([defaults()]), model, manifest)
        pd.testing.assert_frame_equal(app.session_state['individual_result'], expected)

    def test_invalid_profile_clears_previous_result(self):
        app = self.app('Prediksi Individu')
        self.click(app, 'Lihat hasil peninjauan')
        app.number_input(key='input_Curricular_units_1st_sem_enrolled').set_value(1)
        app.number_input(key='input_Curricular_units_1st_sem_approved').set_value(2)
        self.click(app, 'Lihat hasil peninjauan')
        self.assertGreater(len(app.error), 0)
        self.assertNotIn('individual_result', app.session_state)
        self.assertFalse(any(m.label == 'Probabilitas Dropout' for m in app.metric))

    def test_preset_clears_old_result_and_updates_fields(self):
        app = self.app('Prediksi Individu')
        self.click(app, 'Lihat hasil peninjauan')
        app.selectbox(key='preset').set_value('Akademik kuat').run()
        self.click(app, 'Terapkan contoh')
        self.assertNotIn('individual_result', app.session_state)
        self.assertEqual(app.number_input(key='input_Curricular_units_1st_sem_grade').value,
                         defaults('Akademik kuat')['Curricular_units_1st_sem_grade'])
        self.click(app, 'Lihat hasil peninjauan')
        self.assertEqual(app.session_state['individual_result'].iloc[0]['Curricular_units_1st_sem_grade'],
                         defaults('Akademik kuat')['Curricular_units_1st_sem_grade'])

    def test_navigation_restores_submitted_profile(self):
        app = self.app('Prediksi Individu')
        app.number_input(key='input_Age_at_enrollment').set_value(31)
        self.click(app, 'Lihat hasil peninjauan')
        app.sidebar.radio[0].set_value('Gambaran Data').run()
        app.sidebar.radio[0].set_value('Prediksi Individu').run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.number_input(key='input_Age_at_enrollment').value, 31)
        self.assertEqual(app.session_state['individual_result'].iloc[0]['Age_at_enrollment'], 31)

    def test_batch_synthetic_results_and_action_filter(self):
        app = self.app('Prediksi Batch')
        self.assertTrue(next(b.disabled for b in app.button if b.label == 'Validasi dan prediksi'))
        self.radio(app, 'Sumber data', 'Contoh sintetis')
        self.click(app, 'Validasi dan prediksi')
        result = app.session_state['batch_result']
        model, manifest = load_bundle()
        expected = predict_frame(pd.DataFrame([defaults(n) for n in ['Contoh umum', 'Perlu dukungan akademik', 'Akademik kuat']]), model, manifest)
        pd.testing.assert_frame_equal(result, expected)
        self.assertEqual(list(result.source_row), [1, 2, 3])
        self.radio(app, 'Tampilkan profil', 'Perlu peninjauan')
        tables = [d.value for d in app.dataframe if 'action' in d.value.columns]
        self.assertTrue(tables)
        self.assertTrue(tables[-1].action.eq('Perlu peninjauan').all())
        self.assertTrue(tables[-1].prob_dropout.is_monotonic_decreasing)
        pd.testing.assert_frame_equal(app.session_state['batch_result'], expected)

    def test_batch_source_change_clears_previous_results(self):
        app = self.app('Prediksi Batch')
        self.radio(app, 'Sumber data', 'Contoh sintetis')
        self.click(app, 'Validasi dan prediksi')
        self.radio(app, 'Sumber data', 'Unggah CSV')
        self.assertNotIn('batch_result', app.session_state)
        self.assertTrue(next(b.disabled for b in app.button if b.label == 'Validasi dan prediksi'))
        self.assertFalse(any(m.label == 'Baris diproses' for m in app.metric))

if __name__ == '__main__':
    unittest.main()
