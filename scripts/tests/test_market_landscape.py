"""Protect scope, immutable criteria and irregular manual research windows."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect_market_sources import select_filings
from prepare_market_sweep import instant
from render_market_sweep import validate
from start_market_sweep import select_window


class LandscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run = ROOT / 'research/market-sweeps/2026-09-27-r1'
        cls.data = json.loads((run / 'report.json').read_text())
        cls.manifest = json.loads((run / 'manifest.json').read_text())

    def test_complete_frozen_report_is_valid(self):
        validate(self.data, self.manifest)

    def test_omitted_company_is_rejected(self):
        data = copy.deepcopy(self.data)
        data['companies'].pop()
        with self.assertRaises(AssertionError):
            validate(data, self.manifest)

    def test_changed_criterion_and_earnings_verdict_are_rejected(self):
        for mutation in ('criterion', 'outcome'):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                question = data['companies'][0]['questions'][0]
                if mutation == 'criterion':
                    question['question']['criterion']['value'] += 1
                else:
                    question['criterion_outcome'] = 'met'
                with self.assertRaises(AssertionError):
                    validate(data, self.manifest)

    def test_unknown_source_and_future_observation_are_rejected(self):
        for mutation in ('source', 'future'):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                if mutation == 'source':
                    data['events'][0]['source_ids'].append('missing')
                else:
                    data['series']['DGS10']['observations'][-1]['date'] = '2099-01-01'
                with self.assertRaises(AssertionError):
                    validate(data, self.manifest)

    def test_irregular_gap_is_not_shortened_and_future_run_is_ignored(self):
        reports = [{'cutoff': '2026-09-01T12:00:00+03:00'},
                   {'cutoff': '2026-11-01T12:00:00+03:00'},
                   {'cutoff': '2026-09-10T12:00:00+03:00'}]
        prior, start = select_window(reports, '2026-10-15T12:00:00+03:00')
        self.assertEqual(prior['cutoff'], reports[2]['cutoff'])
        self.assertEqual(instant(start), instant('2026-09-08T12:00:00+03:00'))
        _, first = select_window([], '2026-10-15T12:00:00+03:00')
        self.assertEqual(instant(first), instant('2026-10-08T12:00:00+03:00'))
        _, explicit = select_window(reports, '2026-10-15T12:00:00+03:00', '2026-09-01T00:00:00Z')
        self.assertEqual(explicit, '2026-09-01T00:00:00Z')

    def test_sec_acceptance_cutoff_and_missing_timestamp(self):
        table = {'filingDate': ['2026-09-27'] * 3,
                 'acceptanceDateTime': ['2026-09-27T20:00:00Z', '2026-09-27T22:00:00Z'],
                 'accessionNumber': ['0001-01', '0001-02', '0001-03'],
                 'form': ['8-K'] * 3, 'primaryDocument': ['a.htm'] * 3}
        result = select_filings(table, '0000123', instant('2026-09-27T00:00:00+03:00'),
                                instant('2026-09-27T23:00:00+03:00'))
        self.assertEqual([r['accession'] for r in result], ['0001-01', '0001-03'])
        self.assertFalse(result[0]['boundary_review_required'])
        self.assertTrue(result[1]['boundary_review_required'])
        self.assertEqual(result[1]['review_status'], 'discovered_not_read')


if __name__ == '__main__':
    unittest.main()
