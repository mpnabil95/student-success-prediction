"""Read-only integrity check of the shipped package, before any regeneration."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import nbformat
import numpy as np
import pandas as pd
from student_success.config import CLASS_NAMES, PROTOCOL
from student_success.inference import load_bundle, sha256_file
from student_success.modeling import align_probabilities, evaluate, policy_metrics
from student_success.schema import NUMERICAL, schema_records, validate_features
from student_success.train import EXPECTED_DATA_SHA256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def compare_values(actual, expected, label):
    """Compare JSON values with tolerance for floating-point serialization."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), label)
        for key, value in expected.items():
            compare_values(actual[key], value, f'{label}.{key}')
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), label)
        for index, value in enumerate(expected):
            compare_values(actual[index], value, f'{label}[{index}]')
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        require(np.isclose(actual, expected, rtol=1e-9, atol=1e-12), label)
    else:
        require(actual == expected, label)


def check_release(root=ROOT):
    root = Path(root)
    require(sys.version_info[:2] == (3, 12), 'Use Python 3.12.')
    sources = [root / 'app.py']
    for directory in ['student_success', 'scripts', 'tests']:
        sources.extend((root / directory).glob('*.py'))
    for path in sources:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

    nb = nbformat.read(root / 'notebook.ipynb', as_version=4)
    nbformat.validate(nb)
    code = [cell for cell in nb.cells if cell.cell_type == 'code']
    require(bool(code), 'Notebook contains no code.')
    require([cell.execution_count for cell in code] == list(range(1, len(code) + 1)),
            'Notebook execution counts are incomplete or out of order.')
    for cell in code:
        ast.parse(cell.source)
        require(not any(output.output_type == 'error' for output in cell.outputs),
                'Notebook contains an error output.')

    manifest = read_json(root / 'artifacts/manifest.json')
    metrics = read_json(root / 'reports/metrics.json')
    hashes = {p.name: sha256_file(p) for p in sorted((root / 'student_success').glob('*.py'))}
    require(hashes == manifest['code_sha256'], 'Source changed since training; rebuild the bundle.')
    compare_values(read_json(root / 'artifacts/feature_schema.json'),
                   json.loads(json.dumps(schema_records())), 'feature_schema')
    for label, protocol in [('manifest', manifest['protocol']), ('metrics', metrics['protocol']),
                            ('report', read_json(root / 'reports/protocol.json'))]:
        compare_values(protocol, PROTOCOL, label + '.protocol')
    data_path = root / 'data/raw/students.csv'
    require(sha256_file(data_path) == manifest['data_sha256'] == EXPECTED_DATA_SHA256,
            'Dataset checksum mismatch.')
    data = pd.read_csv(data_path, sep=';')
    features = validate_features(data)
    model, _ = load_bundle(root / 'artifacts')
    require(manifest['classes'] == CLASS_NAMES, 'Manifest classes mismatch.')
    for key in ['threshold', 'counts']:
        compare_values(metrics[key], manifest[key], key)
    require(metrics['selected_candidate'] == manifest['candidate'], 'Candidate mismatch.')

    splits = pd.read_csv(root / 'reports/split_assignments.csv')
    require(splits.source_row.tolist() == list(range(1, len(data) + 1)), 'Invalid split row IDs.')
    require(splits.target.tolist() == data.Status.tolist(), 'Split targets mismatch.')
    compare_values(splits['split'].value_counts().to_dict(), manifest['counts'], 'split.counts')
    development = data.loc[splits['split'].eq('model_development')]
    ranges = {c: {'min': float(development[c].min()), 'max': float(development[c].max())}
              for c in NUMERICAL}
    compare_values(ranges, manifest['training_ranges'], 'training_ranges')

    verified_rows = 0
    for partition in ['policy_validation', 'historical_holdout']:
        saved = pd.read_csv(root / f'reports/{partition}_predictions.csv')
        expected_ids = splits.loc[splits['split'].eq(partition), 'source_row']
        require(saved.source_row.is_unique and sorted(saved.source_row) == expected_ids.tolist(),
                partition + ': missing or duplicate prediction rows.')
        indices = saved.source_row.to_numpy() - 1
        actual = data.iloc[indices].Status.to_numpy()
        probabilities = align_probabilities(model, features.iloc[indices])
        require(saved.actual.tolist() == actual.tolist(), partition + ': targets mismatch.')
        np.testing.assert_allclose(saved[['prob_' + c.lower() for c in CLASS_NAMES]],
                                   probabilities, rtol=1e-7, atol=1e-8)
        require(saved.predicted.tolist() == np.asarray(CLASS_NAMES)[probabilities.argmax(axis=1)].tolist(),
                partition + ': predicted labels mismatch.')
        require(saved.review.tolist() == (probabilities[:, 0] >= manifest['threshold']).tolist(),
                partition + ': review flags mismatch.')
        compare_values(metrics[partition], evaluate(actual, probabilities, manifest['threshold']), partition)
        verified_rows += len(saved)
        if partition == 'policy_validation':
            expected_thresholds = [policy_metrics(actual, probabilities[:, 0], t)
                                   for t in np.round(np.arange(.05, .951, .01), 2)]

    thresholds = pd.read_csv(root / 'reports/threshold_analysis.csv')
    compare_values(thresholds.to_dict('records'), expected_thresholds, 'threshold_analysis')
    best = max(expected_thresholds, key=lambda row: (row['f2'], row['threshold']))
    require(best['threshold'] == manifest['threshold'], 'Policy threshold is not the validation winner.')
    comparison = pd.read_csv(root / 'reports/model_comparison.csv')
    compare_values(comparison.to_dict('records'), metrics['model_selection'], 'model_selection')
    candidates = comparison.loc[comparison.candidate.ne('dummy')]
    require(candidates.loc[candidates.macro_f1_mean.idxmax(), 'candidate'] == manifest['candidate'],
            'Selected candidate is not the CV winner.')
    return {'notebook_cells': len(nb.cells), 'executed_code_cells': len(code),
            'source_hashes_match_manifest': True, 'verified_prediction_rows': verified_rows,
            'verified_thresholds': len(thresholds), 'model_sha256': manifest['model_sha256']}


if __name__ == '__main__':
    print(json.dumps(check_release(), indent=2))
