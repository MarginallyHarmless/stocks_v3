import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import timedelta

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('market_sweep', ROOT / 'scripts/prepare_market_sweep.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def entry(name, version=1, threshold=10, question_id='growth'):
    return {'status': 'ready', 'company': {'ticker': name}, 'report_id': name + '-report',
            'questions': [{'id': question_id, 'criterion_version': version,
                           'criterion': {'value': threshold}}]}


class MarketSweepTests(unittest.TestCase):
    def test_changed_questions_are_scoped_to_security(self):
        old = {'A': entry('A'), 'B': entry('B')}
        current = copy.deepcopy(old)
        current['A']['questions'][0]['criterion']['value'] = 20
        before = copy.deepcopy(old)
        result = m.diff_universe(current, {'run_id': 'old', 'companies': old})
        self.assertEqual(list(result['companies_changed']), ['A'])
        self.assertEqual(result['companies_changed']['A']['same_version_content_changes'], ['growth'])
        self.assertEqual(old, before)

    def test_additions_removals_and_ticker_change(self):
        old = {'issuer1|share1': entry('OLD'), 'removed': entry('R')}
        current = {'issuer1|share1': entry('NEW'), 'added': entry('A')}
        result = m.diff_universe(current, {'run_id': 'old', 'companies': old})
        self.assertEqual(result['companies_added'], ['added'])
        self.assertEqual(result['companies_removed'], ['removed'])
        self.assertTrue(result['companies_changed']['issuer1|share1']['identity_metadata_changed'])

    def test_question_version_and_retirement(self):
        old = {'A': entry('A')}
        old['A']['questions'].append({'id': 'retired', 'criterion_version': 1})
        now = {'A': entry('A', version=2, threshold=20)}
        result = m.diff_universe(now, {'run_id': 'old', 'companies': old})['companies_changed']['A']
        self.assertEqual(result['questions_removed'], ['retired'])
        self.assertEqual(result['questions_changed'], ['growth'])
        self.assertEqual(result['same_version_content_changes'], [])

    def test_loading_failure_is_not_question_retirement(self):
        old = {'A': entry('A')}
        now = {'A': {**entry('A'), 'status': 'blocked', 'questions': []}}
        result = m.diff_universe(now, {'run_id': 'old', 'companies': old})
        self.assertEqual(result['companies_changed']['A']['comparison_status'], 'unavailable')
        self.assertNotIn('questions_removed', result['companies_changed']['A'])

    def test_all_registry_companies_loaded_and_missing_archive_visible(self):
        registry = json.loads((ROOT / 'stock-analysis-registry.json').read_text())
        original = next(iter(registry['companies'].items()))
        key, value = original
        archived = json.loads((ROOT / value['archive_path']).read_text())
        cutoff = m.instant(archived['snapshots'][value['latest_report_id']]['research']['cutoff'])
        start = (cutoff - timedelta(days=7)).isoformat()
        cutoff = (cutoff + timedelta(seconds=1)).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = {'kind': 'company_registry', 'companies': {key: value}}
            (root / 'stock-analysis-registry.json').write_text(json.dumps(reg))
            missing = m.prepare(root, start, cutoff, 'test')
            self.assertEqual(missing['company_count'], 1)
            self.assertEqual(missing['companies'][key]['status'], 'blocked')
            archive = root / value['archive_path']
            archive.parent.mkdir(parents=True)
            archive.write_bytes((ROOT / value['archive_path']).read_bytes())
            loaded = m.prepare(root, start, cutoff, 'test')
            self.assertEqual(loaded['status'], 'ready')
            self.assertGreater(loaded['question_count'], 0)


if __name__ == '__main__':
    unittest.main()
