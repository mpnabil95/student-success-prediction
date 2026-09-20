"""Compare regenerated outputs with a preserved checkout; never overwrite evidence."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import nbformat
import pandas as pd
from scripts.check_release import compare_values, read_json, require


def compare_reproduction(reference, candidate=ROOT):
    reference, candidate = Path(reference), Path(candidate)
    for name in ['reports/metrics.json', 'reports/protocol.json', 'reports/data_quality.json',
                 'artifacts/feature_schema.json']:
        compare_values(read_json(candidate / name), read_json(reference / name), name)
    old, new = (read_json(p / 'artifacts/manifest.json') for p in [reference, candidate])
    # Serialized bytes / runtime patch versions may differ across platforms.
    # Each bundle must separately pass check_release, including its own checksum.
    for manifest in [old, new]:
        for key in ['model_sha256', 'environment']:
            manifest.pop(key)
    compare_values(new, old, 'manifest')
    tables = ['cv_folds', 'model_comparison', 'threshold_analysis', 'policy_validation_predictions',
              'historical_holdout_predictions', 'subgroup_metrics', 'permutation_importance',
              'split_assignments']
    for name in [f'reports/{table}.csv' for table in tables] + ['examples/students_template.csv']:
        old, new = (pd.read_csv(p / name) for p in [reference, candidate])
        if name == 'reports/cv_folds.csv':
            old, new = (frame.drop(columns=['seconds']) for frame in [old, new])
        pd.testing.assert_frame_equal(new, old, check_dtype=False, rtol=1e-7, atol=1e-9, obj=name)
    for name in ['README.md', 'docs/MODEL_CARD.md', 'docs/FEATURE_DICTIONARY.md', 'docs/PORTFOLIO_RELEASE.md']:
        require((candidate / name).read_text() == (reference / name).read_text(), name + ': stale generated documentation.')
    notebooks = [nbformat.read(p / 'notebook.ipynb', as_version=4) for p in [reference, candidate]]
    require([(c.cell_type, c.source) for c in notebooks[0].cells] ==
            [(c.cell_type, c.source) for c in notebooks[1].cells], 'Notebook source differs from builder.')
    return {'status': 'passed', 'tables_compared': len(tables) + 1,
            'excluded': ['fit timings', 'model serialization bytes', 'runtime patch versions',
                         'notebook output bytes', 'figure bytes', 'verification timestamps']}


if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(compare_reproduction(args.reference, args.candidate), indent=2))
