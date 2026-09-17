"""Student Success interface. Run from the repository root: python -m streamlit run app.py."""
from __future__ import annotations

import hashlib
import json
from html import escape
from itertools import count
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve

from student_success.config import DATA_PATH, REPORT_DIR, CLASS_NAMES
from student_success.schema import FIELDS, FEATURES, COURSES, defaults, parse_csv, ValidationError
from student_success.inference import (
    load_bundle, predict_frame, recommendations, reference_warnings,
)

ROOT = Path(__file__).resolve().parent
PAGES = ['Gambaran Data', 'Prediksi Individu', 'Prediksi Batch', 'Kinerja Model']
PRESETS = ['Contoh umum', 'Perlu dukungan akademik', 'Akademik kuat']
COLORS = {'Dropout': '#c76b4c', 'Enrolled': '#b38a35', 'Graduate': '#168477'}
COLOR_SCALE = alt.Scale(domain=CLASS_NAMES, range=[COLORS[c] for c in CLASS_NAMES])
REPO = 'https://github.com/mpnabil95/student-success-prediction'
PANEL_IDS = count()
METRIC_IDS = count()

st.set_page_config(page_title='Student Success · Academic Insights', page_icon='🎓', layout='wide')


@st.cache_resource
def resources():
    return load_bundle()


@st.cache_data
def historical_data():
    return pd.read_csv(DATA_PATH, sep=';')


@st.cache_data
def evaluation():
    return json.loads((REPORT_DIR / 'metrics.json').read_text(encoding='utf-8'))


@st.cache_data
def report_table(name):
    return pd.read_csv(REPORT_DIR / name)


def number(value):
    return f'{int(value):,}'.replace(',', '.')


def percent(value):
    return f'{float(value):.1%}'.replace('.', ',')


def html(content):
    """Only developer templates and escaped scalar values are rendered as HTML."""
    st.markdown(content, unsafe_allow_html=True)


def section(kicker, title, description=''):
    html(f'<div class="section-heading"><span class="eyebrow">{escape(kicker)}</span>'
         f'<h3>{escape(title)}</h3><p>{escape(description)}</p></div>')


def note(title, body, tone='teal'):
    html(f'<div class="insight {escape(tone)}"><strong>{escape(title)}</strong>'
         f'<p>{escape(body)}</p></div>')


def chart(spec, height=280):
    # Streamlit 1.49 adjusts spec.padding.bottom in its JavaScript renderer.
    # A scalar is valid Vega-Lite but incompatible with that renderer path.
    styled = (spec.properties(
                  height=height,
                  padding={"left": 12, "right": 12, "top": 12, "bottom": 12},
              )
              .configure_view(strokeWidth=0)
              .configure_axis(gridColor='#edf1f4', domain=False, tickSize=0,
                              labelColor='#5d6b7a', titleColor='#5d6b7a', labelPadding=8,
                              titlePadding=14, labelFontSize=12, titleFontSize=12)
              .configure_legend(labelColor='#526474', title=None, labelFontSize=12,
                                orient='bottom', symbolType='circle', padding=12)
              .configure(background='transparent', font='sans-serif'))
    st.altair_chart(styled, use_container_width=True, theme=None)


def panel():
    """Public Streamlit container keys provide stable hooks for card styling."""
    return st.container(border=True, key=f'ss_panel_{next(PANEL_IDS)}')


def metric_row(items):
    for col, (label, value, detail) in zip(st.columns(len(items)), items):
        with col:
            with st.container(border=True, key=f'ss_metric_{next(METRIC_IDS)}'):
                st.metric(label, value, help=detail)
                st.caption(detail)


def show_validation(err):
    st.error('Data belum dapat diprediksi. Perbaiki nilai berikut terlebih dahulu.')
    st.dataframe(err.issues.rename(columns={'row': 'Baris data', 'column': 'Kolom', 'message': 'Keterangan'}),
                 hide_index=True, width='stretch')
    st.caption('Baris data dimulai dari 1 setelah header; baris 0 berarti masalah file atau struktur kolom.')


def show_reference_warnings(issues):
    if issues is not None and not issues.empty:
        st.warning(f'{issues.row.nunique()} profil memuat nilai di luar rentang data pengembangan.')
        with st.expander('Lihat nilai yang perlu diperhatikan'):
            st.dataframe(issues.rename(columns={'row': 'Baris data', 'column': 'Kolom', 'message': 'Keterangan'}),
                         hide_index=True, width='stretch')


def sidebar():
    with st.sidebar:
        html('<div class="brand"><div class="brand-mark">s<span>+</span></div>'
             '<div><strong>Student Success</strong><small>ACADEMIC INSIGHTS</small></div></div>')
        html('<div class="nav-label">RUANG ANALISIS</div>')
        page = st.radio('Jelajahi', PAGES, key='navigation', label_visibility='collapsed')
        st.markdown('---')
        html('<div class="sidebar-context"><span class="eyebrow">TENTANG STUDI</span>'
             '<h4>Data awal.<br>Pemahaman lebih baik.</h4>'
             '<p>Data pendaftaran dan semester pertama untuk mempelajari tiga kemungkinan status studi.</p>'
             '<div class="pill-row"><span>14 fitur</span><span>3 status</span></div></div>')
        st.caption('Studi kasus portofolio · Data historis Portugal. Jaya Jaya Institut adalah konteks fiktif.')
        st.markdown(f'[Panduan penggunaan ↗]({REPO}/blob/main/docs/APP_GUIDE.md)')
        st.markdown('[Sumber dataset ↗](https://doi.org/10.24432/C5MC89)')
        html('<div class="sidebar-author"><span>DIKEMBANGKAN OLEH</span>'
             '<strong>Muhammad Pangeran Nabil</strong><small>Data Science Portfolio</small></div>')
    return page


def page_header(page):
    titles = {
        PAGES[0]: ('01', 'Eksplorasi perjalanan akademik',
                   'Kenali pola historis sebelum melihat prediksi.',
                   ['4.424 profil', '17 program studi', 'Snapshot historis']),
        PAGES[1]: ('02', 'Satu profil, pemahaman lebih utuh',
                   'Tinjau kemungkinan status studi dari data semester pertama.',
                   ['14 fitur', '3 kemungkinan status', 'Tinjauan oleh manusia']),
        PAGES[2]: ('03', 'Tinjau banyak profil sekaligus',
                   'Dari CSV menjadi daftar peninjauan yang dapat ditelusuri.',
                   ['Alur kerja CSV', 'Validasi per baris', 'Hasil dapat diunduh']),
        PAGES[3]: ('04', 'Kenali kemampuan dan batas model',
                   'Evaluasi yang transparan untuk interpretasi yang bertanggung jawab.',
                   ['Historical holdout', 'Kebijakan recall-first', 'Model card tersedia']),
    }
    index, title, subtitle, metadata = titles[page]
    meta = ''.join(f'<span>{escape(item)}</span>' for item in metadata)
    html(f'<div class="topline"><span><b>{index}</b> STUDENT SUCCESS <i>/</i> {escape(page.upper())}</span>'
         '<span class="context-badge">STUDI RETROSPEKTIF</span></div>'
         f'<div class="page-heading"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p>'
         f'<div class="page-meta">{meta}</div></div>')


def reset_filters():
    st.session_state['overview_courses'] = []
    st.session_state['overview_age'] = (17, 70)


def overview():
    data = historical_data()
    html('<div class="hero"><div class="hero-copy"><span class="hero-label">MEMAHAMI PROGRES · MENDUKUNG POTENSI</span>'
         '<h2>Di balik setiap angka,<br>ada perjalanan studi.</h2>'
         '<p>Jelajahi pola capaian akademik untuk memahami mahasiswa yang mungkin membutuhkan dukungan.</p>'
         '<div class="hero-tags"><span>Data pendaftaran</span><span>Semester pertama</span></div></div>'
         f'<div class="hero-fact"><span>CAKUPAN DATA HISTORIS</span><strong>{number(len(data))}</strong>'
         '<p>profil mahasiswa<br>pendidikan tinggi di Portugal</p><small>UCI · Dataset publik</small></div></div>')
    with st.container(border=True, key='overview_filters'):
        left, middle, right = st.columns([2.1, 1.5, .7], vertical_alignment='bottom')
        chosen = left.multiselect('Program studi', options=sorted(COURSES), format_func=lambda k: COURSES[k],
                                  key='overview_courses', placeholder='Semua program studi')
        age = middle.slider('Usia saat masuk', 17, 70, (17, 70), key='overview_age')
        right.button('Reset filter', on_click=reset_filters, width='stretch')
    subset = data.loc[data.Age_at_enrollment.between(*age)]
    if chosen:
        subset = subset.loc[subset.Course.isin(chosen)]
    if subset.empty:
        note('Belum ada data dalam pilihan ini', 'Ubah program studi atau rentang usia, atau gunakan Reset filter.', 'amber')
        return
    counts = subset.Status.value_counts().reindex(CLASS_NAMES, fill_value=0)
    metric_row([
        ('Mahasiswa dalam filter', number(len(subset)), f'{percent(len(subset) / len(data))} dari seluruh snapshot'),
        ('Graduate', number(counts.Graduate), f'{percent(counts.Graduate / len(subset))} telah lulus pada titik pelabelan'),
        ('Enrolled', number(counts.Enrolled), f'{percent(counts.Enrolled / len(subset))} masih terdaftar pada titik pelabelan'),
        ('Dropout', number(counts.Dropout), f'{percent(counts.Dropout / len(subset))} keluar pada titik pelabelan'),
    ])
    left, right = st.columns([1, 1.4], gap='medium')
    with left, panel():
        section('01 / KOMPOSISI', 'Tiga kemungkinan status', 'Distribusi mahasiswa setelah filter.')
        comp = pd.DataFrame({'Status': CLASS_NAMES, 'Jumlah': counts.to_numpy()})
        comp['Proporsi'] = comp.Jumlah / len(subset)
        base = alt.Chart(comp)
        donut = base.mark_arc(innerRadius=76, outerRadius=109, cornerRadius=5, padAngle=.025).encode(
            theta=alt.Theta('Jumlah:Q'), color=alt.Color('Status:N', scale=COLOR_SCALE),
            tooltip=['Status:N', alt.Tooltip('Jumlah:Q', format=','), alt.Tooltip('Proporsi:Q', format='.1%')])
        center = alt.Chart(pd.DataFrame({'label': [number(len(subset))]})).mark_text(
            fontSize=28, fontWeight=700, color='#203d4b', dy=-4).encode(text='label:N')
        label = alt.Chart(pd.DataFrame({'label': ['mahasiswa']})).mark_text(
            fontSize=12, color='#72808e', dy=24).encode(text='label:N')
        chart(donut + center + label, 260)
        st.caption('Enrolled berarti belum selesai, bukan jaminan lulus atau bebas risiko.')
    with right, panel():
        section('02 / CAPAIAN AKADEMIK', 'Bagaimana pola semester pertama?', 'Rata-rata capaian menurut status historis.')
        measure = st.radio('Ukuran akademik', ['Unit lulus', 'Rata-rata nilai'], horizontal=True,
                           label_visibility='collapsed')
        field = 'Curricular_units_1st_sem_approved' if measure == 'Unit lulus' else 'Curricular_units_1st_sem_grade'
        means = subset.groupby('Status')[field].mean().reindex(CLASS_NAMES).dropna().rename('Rata-rata').reset_index()
        bars = alt.Chart(means).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=62).encode(
            x=alt.X('Status:N', sort=CLASS_NAMES, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Rata-rata:Q', title=measure, scale=alt.Scale(zero=True)),
            color=alt.Color('Status:N', scale=COLOR_SCALE, legend=None),
            tooltip=['Status:N', alt.Tooltip('Rata-rata:Q', format='.2f')])
        chart(bars, 250)
        st.caption('Pola antarstatus bersifat deskriptif dan tidak menunjukkan sebab-akibat.')
    with panel():
        section('03 / PROGRAM STUDI', 'Melihat konteks di setiap program',
                'Bandingkan proporsi dropout bersama ukuran kelompoknya.')
        groups = subset.groupby('Course').agg(jumlah=('Status', 'size'), dropout=('Status', lambda s: s.eq('Dropout').sum()))
        groups['proporsi_dropout'] = groups.dropout / groups.jumlah
        groups['Program studi'] = [COURSES[c] for c in groups.index]
        min_n = st.select_slider('Minimal mahasiswa per program', options=[1, 10, 30, 50, 100], value=1)
        show = groups.loc[groups.jumlah >= min_n].sort_values('proporsi_dropout', ascending=False)
        st.caption(f'{len(show)} program ditampilkan · Penyebut proporsi: mahasiswa program tersebut setelah filter.')
        if show.empty:
            st.info('Tidak ada program yang memenuhi ukuran kelompok ini. Turunkan minimum mahasiswa.')
        else:
            st.dataframe(show[['Program studi', 'jumlah', 'dropout', 'proporsi_dropout']], hide_index=True,
                         width='stretch', height=min(430, 36 * len(show) + 40), column_config={
                             'jumlah': st.column_config.NumberColumn('Mahasiswa', format='%d'),
                             'dropout': st.column_config.NumberColumn('Dropout', format='%d'),
                             'proporsi_dropout': st.column_config.ProgressColumn('Proporsi dropout', min_value=0, max_value=1, format='percent'),
                         })
            st.download_button('Unduh ringkasan program', show[['Program studi', 'jumlah', 'dropout', 'proporsi_dropout']].to_csv(index=False).encode('utf-8'),
                               'program_summary.csv', 'text/csv', key='program_summary_download')
    note('Mulai dari pola, lanjutkan dengan peninjauan',
         'Dashboard ini membaca data historis. Untuk mencoba prediksi, pilih Prediksi Individu atau Prediksi Batch di sidebar.')


def apply_preset():
    profile = defaults(st.session_state['preset'])
    st.session_state['saved_profile'] = profile
    for field, value in profile.items():
        st.session_state['input_' + field] = float(value) if FIELDS[field].kind == 'continuous' else int(value)
    st.session_state.pop('individual_result', None)
    st.session_state.pop('individual_warnings', None)


def probability_chart(row):
    frame = pd.DataFrame({'Status': CLASS_NAMES, 'Probabilitas': [row['prob_' + c.lower()] for c in CLASS_NAMES]})
    bars = alt.Chart(frame).mark_bar(cornerRadiusEnd=5, size=25).encode(
        y=alt.Y('Status:N', sort=CLASS_NAMES, title=None),
        x=alt.X('Probabilitas:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%'), title=None),
        color=alt.Color('Status:N', scale=COLOR_SCALE, legend=None),
        tooltip=['Status:N', alt.Tooltip('Probabilitas:Q', format='.1%')])
    chart(bars, 160)


def individual(model, manifest):
    left, right = st.columns([1.25, 1], gap='medium')
    with left:
        with panel():
            section('01 / PROFIL MAHASISWA', 'Lengkapi informasi awal', 'Gunakan data pendaftaran dan hasil semester pertama.')
            a, b = st.columns([2, 1], vertical_alignment='bottom')
            a.selectbox('Contoh input sintetis', PRESETS, key='preset')
            b.button('Terapkan contoh', on_click=apply_preset, width='stretch')
            profile = st.session_state.get('saved_profile', defaults())
            for field, spec in FIELDS.items():
                value = profile[field]
                st.session_state.setdefault('input_' + field, float(value) if spec.kind == 'continuous' else int(value))
            with st.form('student_form', border=False):
                values = {}
                for tab, group in zip(st.tabs(['Pendaftaran', 'Semester 1']), ['Pendaftaran', 'Semester 1']):
                    with tab:
                        if group == 'Pendaftaran':
                            st.caption('Nilai masuk dan kualifikasi memakai skala 0–200 sesuai sumber.')
                        else:
                            st.caption('Nilai semester: 0–20. Unit kurikulum tidak otomatis setara SKS Indonesia.')
                        columns = st.columns(2)
                        for i, (field, spec) in enumerate((k, v) for k, v in FIELDS.items() if v.group == group):
                            with columns[i % 2]:
                                if spec.options:
                                    values[field] = st.selectbox(spec.label, list(spec.options), format_func=lambda x, m=spec.options: m[x],
                                                                 key='input_' + field, help=spec.description)
                                else:
                                    kwargs = {'min_value': int(spec.low), 'max_value': int(spec.high), 'step': 1} if spec.kind == 'integer' else {
                                        'min_value': float(spec.low), 'max_value': float(spec.high), 'step': .1}
                                    values[field] = st.number_input(spec.label, key='input_' + field, help=spec.description, **kwargs)
                submitted = st.form_submit_button('Lihat hasil peninjauan', type='primary', width='stretch',
                                                   key='individual_submit')
            st.caption('Kirim kembali formulir setiap kali mengubah input. Hasil di samping berasal dari pengiriman terakhir.')
            if submitted:
                st.session_state.pop('individual_result', None)
                st.session_state.pop('individual_warnings', None)
                st.session_state['saved_profile'] = values
                try:
                    frame = pd.DataFrame([values])
                    result = predict_frame(frame, model, manifest)
                    st.session_state['individual_warnings'] = reference_warnings(frame, manifest)
                    st.session_state['individual_result'] = result
                except ValidationError as err:
                    show_validation(err)
                except Exception:
                    st.error('Prediksi belum dapat diproses. Periksa kesesuaian artefak dan versi dependensi aplikasi.')
        with st.expander('Apa yang perlu diperhatikan saat mengisi?'):
            st.markdown('Unit lulus dan unit tanpa evaluasi masing-masing tidak boleh melebihi unit terdaftar. '
                        'Jumlah evaluasi boleh lebih besar karena penilaian dapat berulang. '
                        'Kategori mengikuti data sumber Portugal.')
            st.markdown(f'[Buka kamus 14 fitur]({REPO}/blob/main/docs/FEATURE_DICTIONARY.md)')
    with right:
        with panel():
            section('02 / HASIL PENINJAUAN', 'Dari profil menjadi pemahaman', 'Probabilitas membantu diskusi, bukan menentukan keputusan akademik.')
            result = st.session_state.get('individual_result')
            if result is None:
                html('<div class="empty-result"><div class="empty-symbol">◎</div>'
                     '<h3>Hasil akan muncul di sini</h3><p>Lengkapi profil atau terapkan contoh sintetis, '
                     'lalu pilih <b>Lihat hasil peninjauan</b>.</p>'
                     '<div class="empty-steps"><span>01 · Isi profil</span><span>02 · Lihat peluang</span><span>03 · Tinjau bersama</span></div></div>')
            else:
                row = result.iloc[0]
                review = row.action == 'Perlu peninjauan'
                note('Perlu peninjauan oleh dosen wali' if review else 'Lanjutkan pemantauan rutin',
                     'Konfirmasi kebutuhan mahasiswa sebelum menawarkan pendampingan.' if review else
                     'Tetap perhatikan perkembangan mahasiswa; hasil ini tidak menjamin bebas risiko.', 'amber' if review else 'teal')
                a, b = st.columns(2)
                a.metric('Probabilitas Dropout', percent(row.prob_dropout))
                b.metric('Ambang peninjauan', percent(manifest['threshold']))
                st.caption(f'Status paling mungkin: **{row.predicted_status}** · Model {manifest["model_version"]}')
                probability_chart(row)
                st.caption('Status memilih peluang terbesar. Tindakan mengikuti ambang Dropout; keduanya dapat berbeda.')
                show_reference_warnings(st.session_state.get('individual_warnings'))
                st.markdown('**Langkah pendampingan**')
                for i, suggestion in enumerate(recommendations(row), 1):
                    html(f'<div class="action-item"><span>{i:02}</span><p>{escape(suggestion)}</p></div>')
                st.caption('Saran berbasis aturan transparan; bukan penjelasan sebab-akibat dari model.')
                with st.expander('Input pada hasil ini'):
                    display = result[FEATURES].T.reset_index()
                    display.columns = ['Fitur', 'Nilai']
                    display['Fitur'] = display.Fitur.map(lambda c: FIELDS[c].label)
                    st.dataframe(display, hide_index=True, width='stretch')
                st.download_button('Unduh hasil individu', result.to_csv(index=False).encode('utf-8'),
                                   'student_prediction.csv', 'text/csv', width='stretch',
                                   key='individual_download')


def batch(model, manifest):
    template = pd.DataFrame([defaults(n) for n in PRESETS])
    left, right = st.columns([1.55, 1], gap='medium')
    with left, panel():
        section('01 / SUMBER INPUT', 'Siapkan profil yang ingin ditinjau', 'Pilih file sendiri atau coba tiga profil sintetis.')
        source = st.radio('Sumber data', ['Unggah CSV', 'Contoh sintetis'], horizontal=True, key='batch_source')
        content = None
        if source == 'Unggah CSV':
            upload = st.file_uploader('CSV mahasiswa', type=['csv'], help='UTF-8 · koma atau titik koma · maksimum 10 MB dan 10.000 baris')
            if upload is not None:
                content = upload.getvalue()
        else:
            content = template.to_csv(index=False).encode('utf-8')
            st.info('Tiga profil ini dibuat secara sintetis untuk demonstrasi, bukan data mahasiswa nyata.')
        fingerprint = (source, hashlib.sha256(content).hexdigest() if content is not None else None)
        if st.session_state.get('batch_fingerprint') != fingerprint:
            for key in ['batch_result', 'batch_warnings', 'batch_action_filter']:
                st.session_state.pop(key, None)
            st.session_state['batch_fingerprint'] = fingerprint
        if st.button('Validasi dan prediksi', type='primary', disabled=content is None, width='stretch',
                     key='batch_submit'):
            st.session_state.pop('batch_result', None)
            st.session_state.pop('batch_warnings', None)
            try:
                with st.spinner('Memvalidasi profil dan menyiapkan hasil…'):
                    frame = parse_csv(content)
                    result = predict_frame(frame, model, manifest)
                    warnings = reference_warnings(frame, manifest)
                st.session_state['batch_result'] = result
                st.session_state['batch_warnings'] = warnings
            except ValidationError as err:
                show_validation(err)
            except Exception:
                st.error('File belum dapat diproses. Pastikan struktur CSV valid dan artefak sesuai versi aplikasi.')
    with right, panel():
        section('PANDUAN SINGKAT', 'Mulai dengan format yang tepat')
        for n, title, body in [
            ('01', 'Gunakan 14 kolom fitur', 'Nama kolom mengikuti template. Nilai kategori memakai kode sumber.'),
            ('02', 'Periksa seluruh baris', 'Satu baris tidak valid menghentikan batch agar tidak ada profil terlewat diam-diam.'),
            ('03', 'Simpan pemetaan baris', 'source_row menjaga urutan input. Kolom tambahan tidak ikut diekspor.'),
        ]:
            html(f'<div class="action-item"><span>{n}</span><p><b>{title}</b><br>{body}</p></div>')
        st.download_button('Unduh template dan 3 contoh sintetis', template.to_csv(index=False).encode('utf-8'),
                           'students_template.csv', 'text/csv', width='stretch', key='template_download')
        st.caption('Unggahan diproses dalam sesi dan tidak ditulis ke file project. Batas: 10 MB · 10.000 baris.')
    result = st.session_state.get('batch_result')
    if result is None:
        note('Daftar peninjauan akan muncul setelah prediksi', 'Setiap hasil menyertakan peluang tiga status, kategori tindakan, dan nomor baris input.')
        return
    section('02 / HASIL BATCH', 'Prioritas yang dapat ditelusuri', 'Hasil berasal dari sumber input yang dipilih di atas.')
    n_review = int(result.action.eq('Perlu peninjauan').sum())
    metric_row([
        ('Baris diproses', number(len(result)), 'Seluruh baris lolos validasi'),
        ('Perlu peninjauan', number(n_review), f'{percent(n_review / len(result))} dari profil yang diproses'),
        ('Pemantauan rutin', number(len(result) - n_review), 'Tetap pantau perkembangan berikutnya'),
        ('Ambang peninjauan', percent(manifest['threshold']), 'Mengikuti kebijakan model tersimpan'),
    ])
    show_reference_warnings(st.session_state.get('batch_warnings'))
    with panel():
        action_filter = st.radio('Tampilkan profil', ['Semua', 'Perlu peninjauan', 'Pemantauan rutin'],
                                 horizontal=True, key='batch_action_filter')
        view = result if action_filter == 'Semua' else result.loc[result.action.eq(action_filter)]
        view = view.sort_values(['prob_dropout', 'source_row'], ascending=[False, True])
        st.caption(f'{len(view)} dari {len(result)} profil · Diurutkan berdasarkan probabilitas Dropout tertinggi. source_row tetap merujuk urutan input.')
        if view.empty:
            st.info('Tidak ada profil dalam kategori ini. Pilih kategori lainnya atau Semua.')
        else:
            st.dataframe(view[['source_row', 'predicted_status', 'prob_dropout', 'prob_enrolled', 'prob_graduate', 'action']],
                         hide_index=True, width='stretch', column_config={
                             'source_row': st.column_config.NumberColumn('Baris input', format='%d'),
                             'predicted_status': 'Status paling mungkin', 'action': 'Tindakan',
                             **{f'prob_{c.lower()}': st.column_config.ProgressColumn(f'P({c})', min_value=0, max_value=1, format='percent') for c in CLASS_NAMES},
                         })
        a, b = st.columns(2)
        a.download_button('Unduh seluruh hasil', result.to_csv(index=False).encode('utf-8'),
                          'batch_predictions.csv', 'text/csv', width='stretch', key='batch_download_all')
        b.download_button('Unduh tampilan terfilter', view.to_csv(index=False).encode('utf-8'),
                          'batch_predictions_filtered.csv', 'text/csv', width='stretch',
                          disabled=view.empty, key='batch_download_filtered')
        st.caption('Seluruh hasil mengikuti urutan input. Unduhan terfilter mengikuti kategori dan urutan tabel saat ini.')


def performance(manifest):
    metrics = evaluation()
    m, policy = metrics['historical_holdout'], metrics['historical_holdout']['policy']
    note('Evaluasi pada holdout historis',
         f'{number(metrics["counts"]["historical_holdout"])} profil evaluasi pernah diperiksa pada submission lama. '
         'Ini belum merupakan validasi independen pada kampus atau cohort baru.', 'amber')
    metric_row([
        ('Macro F1', f'{m["macro_f1"]:.3f}', 'Tiga kelas diberi bobot sama'),
        ('Recall peninjauan Dropout', percent(policy['recall']), 'Kasus Dropout aktual yang ditandai'),
        ('Precision peninjauan', percent(policy['precision']), 'Ketepatan di antara profil yang ditandai'),
        ('Profil yang ditandai', percent(policy['review_rate']), 'Beban peninjauan pada holdout'),
    ])
    tabs = st.tabs(['Hasil evaluasi', 'Pemilihan model', 'Diagnostik', 'Batas penggunaan'])
    with tabs[0]:
        left, right = st.columns(2, gap='medium')
        with left, panel():
            section('KLASIFIKASI TIGA KELAS', 'Di mana prediksi tepat atau keliru?', 'Baris: status aktual · Kolom: prediksi model.')
            cm = pd.DataFrame(m['confusion_matrix'], index=CLASS_NAMES, columns=CLASS_NAMES).reset_index().melt('index')
            cm.columns = ['Aktual', 'Prediksi', 'Jumlah']
            base = alt.Chart(cm).encode(x=alt.X('Prediksi:N', sort=CLASS_NAMES, title=None, axis=alt.Axis(labelAngle=0)),
                                        y=alt.Y('Aktual:N', sort=CLASS_NAMES, title=None), tooltip=['Aktual', 'Prediksi', 'Jumlah'])
            tiles = base.mark_rect(cornerRadius=5).encode(color=alt.Color('Jumlah:Q', scale=alt.Scale(range=['#edf6f3', '#117367']), legend=None))
            # Altair preserves NumPy scalar constructors inside expression strings
            # (for example ``np.float64(199.0)``). Vega cannot execute that Python
            # syntax in the browser, so normalize the threshold to a plain float.
            label_contrast_threshold = float(cm['Jumlah'].max()) * .5
            labels = base.mark_text(fontSize=20, fontWeight=600).encode(text='Jumlah:Q', color=alt.condition(
                alt.datum.Jumlah > label_contrast_threshold, alt.value('white'), alt.value('#26483f')))
            chart(tiles + labels, 265)
            st.caption(f'Accuracy: {percent(m["accuracy"])} · Diagonal menunjukkan prediksi status yang benar.')
        with right, panel():
            section('KEBIJAKAN PENINJAUAN', 'Recall tinggi memiliki konsekuensi', 'Keputusan tindakan menggunakan probabilitas Dropout.')
            pred = report_table('historical_holdout_predictions.csv')
            actual = pred.actual.eq('Dropout').to_numpy()
            precision, recall, _ = precision_recall_curve(actual, pred.prob_dropout)
            curve = pd.DataFrame({'Recall': recall, 'Precision': precision, 'order': np.arange(len(recall))})
            line = alt.Chart(curve).mark_line(color='#168477', strokeWidth=3).encode(
                x=alt.X('Recall:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
                y=alt.Y('Precision:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
                order='order:Q', tooltip=[alt.Tooltip('Recall', format='.1%'), alt.Tooltip('Precision', format='.1%')])
            point = alt.Chart(pd.DataFrame({'Recall': [policy['recall']], 'Precision': [policy['precision']]})).mark_point(
                filled=True, color='#c76b4c', size=120).encode(x='Recall:Q', y='Precision:Q')
            chart(line + point, 265)
            st.caption(f'Titik oranye: ambang {percent(manifest["threshold"])} yang dipilih pada policy validation.')
        with panel():
            section('KONSEKUENSI PRAKTIS', 'Apa arti angka ini bagi tim pendampingan?')
            metric_row([
                ('Dropout teridentifikasi', number(policy['tp']), 'Dropout aktual yang ditandai'),
                ('Dropout terlewat', number(policy['fn']), 'Dropout aktual yang tidak ditandai'),
                ('Penandaan keliru', number(policy['fp']), 'Selain Dropout yang ikut ditandai'),
                ('Total perlu ditinjau', number(policy['review_count']), 'Kapasitas tim nyata belum ditetapkan'),
            ])
    with tabs[1], panel():
        section('PROSES PEMILIHAN', 'Model dipilih sebelum evaluasi holdout',
                'Rata-rata macro F1 pada lima fold data development.')
        comparison = report_table('model_comparison.csv')
        bars = alt.Chart(comparison).mark_bar(cornerRadiusEnd=5, size=28).encode(
            y=alt.Y('candidate:N', sort='-x', title=None), x=alt.X('macro_f1_mean:Q', title='Macro F1', scale=alt.Scale(domain=[0, 1])),
            color=alt.condition(alt.datum.candidate == manifest['candidate'], alt.value('#168477'), alt.value('#adc6cf')),
            tooltip=['candidate:N', alt.Tooltip('macro_f1_mean:Q', format='.4f'), alt.Tooltip('macro_f1_std:Q', format='.4f')])
        chart(bars, 235)
        st.caption('Hover pada batang untuk melihat rata-rata dan simpangan baku antar-fold.')
        splits = metrics['counts']
        metric_row([('Development', number(splits['model_development']), 'Seleksi dan fit model'),
                    ('Policy validation', number(splits['policy_validation']), 'Pemilihan ambang dengan F2'),
                    ('Historical holdout', number(splits['historical_holdout']), 'Evaluasi setelah pilihan dikunci')])
        st.markdown(f'Model terpilih: **{manifest["candidate"]}** dengan kalibrasi sigmoid. Model tidak dilatih ulang '
                    'pada seluruh data setelah evaluasi. Ambang tersimpan dipilih untuk mengutamakan recall melalui F2.')
        with st.expander('Lihat seluruh skor per kandidat'):
            st.dataframe(comparison, hide_index=True, width='stretch')
    with tabs[2]:
        left, right = st.columns(2, gap='medium')
        with left, panel():
            section('KALIBRASI', 'Apakah peluang sesuai kejadian?', 'Kelompok probabilitas pada holdout historis.')
            pred = report_table('historical_holdout_predictions.csv')
            true, mean = calibration_curve(pred.actual.eq('Dropout'), pred.prob_dropout, n_bins=8, strategy='quantile')
            cal = alt.Chart(pd.DataFrame({'Prediksi': mean, 'Aktual': true})).mark_line(point=True, color='#168477', strokeWidth=2.5).encode(
                x=alt.X('Prediksi:Q', title='Rata-rata probabilitas', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
                y=alt.Y('Aktual:Q', title='Proporsi Dropout aktual', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
                tooltip=[alt.Tooltip('Prediksi:Q', format='.1%'), alt.Tooltip('Aktual:Q', format='.1%')])
            ideal = alt.Chart(pd.DataFrame({'Prediksi': [0, 1], 'Aktual': [0, 1]})).mark_line(color='#adb9bf', strokeDash=[5, 5]).encode(x='Prediksi:Q', y='Aktual:Q')
            chart(cal + ideal, 250)
            st.caption('Garis putus-putus: kalibrasi ideal. Kedekatan pada garis tidak menjamin akurasi di populasi baru.')
        with right, panel():
            section('KEBIJAKAN', 'Menyeimbangkan jangkauan dan beban', 'Semua kurva berikut dihitung pada policy validation.')
            thresholds = report_table('threshold_analysis.csv')
            long = thresholds.melt('threshold', value_vars=['precision', 'recall', 'review_rate', 'f2'], var_name='Ukuran', value_name='Nilai')
            lines = alt.Chart(long).mark_line(strokeWidth=2).encode(
                x=alt.X('threshold:Q', title='Ambang probabilitas', axis=alt.Axis(format='%')),
                y=alt.Y('Nilai:Q', scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format='%')),
                color=alt.Color('Ukuran:N', scale=alt.Scale(range=['#c76b4c', '#458499', '#168477', '#b38a35'])),
                tooltip=['Ukuran:N', alt.Tooltip('threshold:Q', format='.0%'), alt.Tooltip('Nilai:Q', format='.1%')])
            rule = alt.Chart(pd.DataFrame({'threshold': [manifest['threshold']]})).mark_rule(color='#344054', strokeDash=[5, 5]).encode(x='threshold:Q')
            chart(lines + rule, 250)
            st.caption('Garis vertikal: ambang tersimpan. Halaman ini tidak mengubah kebijakan prediksi.')
        with st.expander('Performa per kelas dan perbedaan error kelompok'):
            per_class = pd.DataFrame({c: m['classification_report'][c] for c in CLASS_NAMES}).T
            st.dataframe(per_class, width='stretch')
            st.dataframe(report_table('subgroup_metrics.csv'), hide_index=True, width='stretch')
            st.caption('Ukuran kelompok kecil membuat metrik lebih tidak stabil. Diagnosis ini bukan bukti bahwa model bebas bias.')
    with tabs[3], panel():
        section('INTERPRETASI YANG BERTANGGUNG JAWAB', 'Gunakan hasil sebagai awal percakapan')
        for title, body in [
            ('Waktu kejadian tidak tersedia', 'Dataset tidak memiliki tanggal dropout per mahasiswa. Sebagian kejadian mungkin sudah terjadi sebelum akhir semester pertama.'),
            ('Enrolled belum menjadi hasil akhir', 'Masih terdaftar pada titik pelabelan bukan jaminan lulus atau bebas risiko.'),
            ('Generalisasi perlu dibuktikan', 'Data Portugal tidak otomatis mewakili kampus Indonesia. Pemetaan kategori, data cohort baru, dan validasi tambahan diperlukan.'),
            ('Kapasitas tim perlu ditetapkan', 'Banyak profil dapat ditandai pada ambang yang mengutamakan recall. Manfaat intervensi dan beban operasional belum diuji melalui pilot.'),
            ('Dukungan selalu melibatkan manusia', 'Jangan gunakan prediksi untuk sanksi, penolakan beasiswa, atau keputusan akademik otomatis. Eksklusi fitur demografis tidak menjamin fairness.'),
        ]:
            note(title, body)
        st.markdown(f'[Baca model card lengkap ↗]({REPO}/blob/main/docs/MODEL_CARD.md)')


def main():
    css_path = ROOT / '.streamlit' / 'styles.css'
    if css_path.exists():
        html('<style>' + css_path.read_text(encoding='utf-8') + '</style>')
    page = sidebar()
    page_header(page)
    if page == 'Gambaran Data':
        try:
            overview()
        except (OSError, ValueError, KeyError):
            st.error('Data historis belum dapat ditampilkan. Pastikan snapshot dataset lengkap dan sesuai versi project.')
    else:
        try:
            model, manifest = resources()
        except Exception as err:
            st.error('Model belum siap digunakan. Instal dependensi project dan pastikan artefak model lengkap.')
            with st.expander('Rincian untuk menjalankan aplikasi'):
                st.code(str(err))
            st.stop()
        if page == 'Prediksi Individu':
            individual(model, manifest)
        elif page == 'Prediksi Batch':
            batch(model, manifest)
        else:
            performance(manifest)
    html('<div class="page-footer"><span>STUDENT SUCCESS <b>·</b> Data Science Portfolio</span>'
         '<span>Prediksi retrospektif · Pendampingan oleh manusia</span></div>')


if __name__ == '__main__':
    main()
