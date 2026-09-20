"""Verify shipped files and required tests; optionally save a dated local report."""
import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS']:
    os.environ.setdefault(key, '1')

from scripts.check_release import check_release


def verify(read_only=False):
    # These dependencies are mandatory here; a skipped AppTest is not a release pass.
    import streamlit  # noqa: F401
    import nbformat  # noqa: F401
    integrity = check_release()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    print(log.getvalue())
    if not result.wasSuccessful() or result.skipped:
        raise SystemExit('Verification failed: failures, errors, or skipped tests.')
    report = {
        'verified_at_utc': datetime.now(timezone.utc).isoformat(),
        'integrity': integrity,
        'tests_run': result.testsRun, 'passed': result.testsRun,
        'skipped': 0, 'failures': 0, 'errors': 0,
        'training': 'not rerun by this verifier',
        'notebook': 'nbformat, syntax, execution counts and saved outputs inspected; no kernel launched',
        'deployment': 'not changed or tested by this verifier',
        'github_actions': 'check the run for the committed revision separately',
    }
    if not read_only:
        (ROOT / 'reports/verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        (ROOT / 'docs/VALIDATION.md').write_text(f'''# Catatan verifikasi paket

Pemeriksaan lokal terakhir: **{report['verified_at_utc']}**.

## Hasil yang diperiksa

- **{result.testsRun} tes lulus**, tanpa skip, failure, atau error; termasuk Streamlit AppTest.
- Notebook: {integrity['notebook_cells']} sel, {integrity['executed_code_cells']} sel kode dengan urutan eksekusi lengkap; nbformat dan sintaks valid, tanpa output error tersimpan.
- Hash seluruh modul inti, checksum data/model, schema, protokol, dan rentang training sesuai manifest.
- {integrity['verified_prediction_rows']} baris prediksi policy/holdout sesuai inference model yang disimpan; label, tindakan dan metrik diperiksa kembali.
- {integrity['verified_thresholds']} kandidat threshold dihitung ulang dari policy validation; pilihan threshold sesuai aturan F2.

## Batas bukti

Verifier tidak menjalankan training, kernel Jupyter, browser, deployment, atau build container. Pemeriksaan notebook membaca output tersimpan. Builder terpisah menjalankan kode notebook melalui Python biasa; hasil reproduksi dicatat di [kesiapan release](RELEASE_READINESS.md).

AppTest tidak menggantikan pengujian unduh/unggah lewat browser, tampilan pada semua ukuran layar, atau validasi institusi eksternal. Keberhasilan lokal ini tidak membuktikan bahwa workflow baru sudah berhasil di GitHub Actions.

## Mengulang

```bash
python -m pip install -r requirements-notebook.txt
python scripts/verify_package.py --read-only
```

Tanpa `--read-only`, perintah memperbarui file ini dan `reports/verification.json`. Mode read-only tidak menulis laporan. Rincian tes ada di [tests](../tests/README.md); alur dua job ada di [workflow](../.github/workflows/README.md).
''', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-only', action='store_true', help='Check without rewriting reports or documentation.')
    args = parser.parse_args()
    os.chdir(ROOT)
    verify(args.read_only)
