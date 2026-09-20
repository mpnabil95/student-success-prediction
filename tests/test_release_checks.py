"""The pre-build gate must reject broken committed reports and notebook outputs."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import pandas as pd
from scripts.check_release import ROOT, check_release


class ReleaseChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repository'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__', '.git', '.venv'))

    def test_inconsistent_committed_metric_is_rejected_before_rebuild(self):
        path = self.root / 'reports/metrics.json'
        metrics = json.loads(path.read_text())
        metrics['historical_holdout']['accuracy'] = 1.0
        path.write_text(json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, 'historical_holdout.accuracy'):
            check_release(self.root)

    def test_shifted_prediction_probabilities_are_rejected(self):
        path = self.root / 'reports/policy_validation_predictions.csv'
        predictions = pd.read_csv(path)
        predictions.loc[0, 'prob_dropout'] += .1
        predictions.to_csv(path, index=False)
        with self.assertRaises(AssertionError):
            check_release(self.root)

    def test_unexecuted_notebook_is_rejected(self):
        path = self.root / 'notebook.ipynb'
        notebook = json.loads(path.read_text())
        next(cell for cell in notebook['cells'] if cell['cell_type'] == 'code')['execution_count'] = None
        path.write_text(json.dumps(notebook))
        with self.assertRaisesRegex(ValueError, 'execution counts'):
            check_release(self.root)


if __name__ == '__main__':
    unittest.main()
