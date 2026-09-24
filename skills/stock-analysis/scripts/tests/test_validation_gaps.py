"""Inputs the contract rejects must fail validation, not rendering."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tempfile
from archive import register, verify_archive
from dashboard import validate_dashboard
from demo import fixture, update_fixture, bi
from model import Invalid, digest, load, validate


class ValidationGaps(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def test_period_labels_are_plain_strings(self):
        self.data['evidence'][0]['period']['label'] = bi('Q1 2026', 'T1 2026')
        with self.assertRaisesRegex(Invalid, 'plain string'):
            validate(self.data)

    def test_watch_due_period_is_a_plain_string(self):
        self.data['watchlist'][0]['due_period'] = bi('Q2 2026', 'T2 2026')
        with self.assertRaisesRegex(Invalid, 'plain string'):
            validate(self.data)

    def test_compact_iso_dates_are_rejected(self):
        e = self.data['evidence'][0]
        e['period']['end'] = e['period']['end'].replace('-', '')
        with self.assertRaisesRegex(Invalid, 'Invalid ISO date'):
            validate(self.data)

    def test_trend_series_is_checked_before_rendering(self):
        section = self.data['sections'][0]
        section['series'] = {'title': bi('Shares', 'Acțiuni'), 'evidence_refs': ['shares-old', 'shares']}
        validate(self.data)
        section['series']['evidence_refs'] = ['shares', 'shares-old']
        with self.assertRaisesRegex(Invalid, 'chronological'):
            validate(self.data)
        section['series']['evidence_refs'] = ['shares-old', 'missing']
        with self.assertRaises(Invalid):
            validate(self.data)

    def test_key_stats_are_checked_before_rendering(self):
        self.data['key_stats'] = [{'concept': 'not-a-term', 'evidence_ref': 'revenue'}]
        with self.assertRaisesRegex(Invalid, 'concept'):
            validate(self.data)
        self.data['key_stats'] = [{'concept': 'revenue', 'evidence_ref': 'missing'}]
        with self.assertRaisesRegex(Invalid, 'evidence'):
            validate(self.data)

    def test_evidence_table_may_show_unavailable_values(self):
        self.data['evidence'].append({'id': 'peer-margin', 'kind': 'unavailable', 'label': bi('Peer margin', 'Marja companiei comparabile'),
                                      'definition': 'Peer operating margin', 'state': bi('Not disclosed.', 'Neraportată.')})
        self.data['sections'][0]['evidence_table'] = {
            'title': bi('Peers', 'Comparabile'), 'columns': [bi('Measure', 'Indicator'), bi('Us', 'Noi'), bi('Peer', 'Comparabilă')],
            'rows': [{'label': bi('Margin', 'Marjă'), 'cells': [{'evidence_ref': 'op-margin'}, {'evidence_ref': 'peer-margin'}]}]}
        validate(self.data)


class ArchiveReviewRules(unittest.TestCase):
    def setUp(self):
        self.base = fixture()
        self.review = update_fixture(self.base)

    def test_first_review_cannot_claim_to_supersede(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'archive.json'
            register(path, self.base)
            dangling = copy.deepcopy(self.review)
            dangling['supersedes_report_id'] = 'does-not-exist'
            with self.assertRaisesRegex(Invalid, 'supersedes'):
                register(path, dangling)

    def test_hand_merged_duplicate_review_fails_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'archive.json'
            register(path, self.base)
            register(path, self.review)
            archive = load(path)
            twin = copy.deepcopy(self.review)
            twin.update(report_id='second-review', cutoff='2026-08-09T12:00:00Z', prepared_at='2026-08-09T12:00:00Z')
            archive['snapshots'][twin['report_id']] = {'sha256': digest(twin), 'research': twin}
            with self.assertRaisesRegex(Invalid, 'reviewed twice'):
                verify_archive(archive)


class ChartPeriods(unittest.TestCase):
    def supplement(self, labels):
        return {'kind': 'visual_research_supplement', 'identity': 'x|y', 'retrieved_at': '2026-09-24',
                'sources': {'s': {'url': 'https://example.com', 'status': 'read', 'retrieved_at': '2026-09-24'}},
                'series': {'revenue': {'unit': 'currency', 'currency': 'USD', 'scale': 1, 'basis': 'GAAP', 'period_kind': 'quarter',
                                       'source_id': 's', 'source_row': 'r', 'points': [{'period': x, 'value': 1} for x in labels]}},
                'market': {}, 'consensus': {}}

    def test_labels_match_cadence_and_order(self):
        validate_dashboard(self.supplement(['Q4 2025', 'Q1 2026']))
        for labels in (['FY 2024', 'FY 2025'], ['Q5 2026'], ['Q2 2026', 'Q1 2026']):
            with self.assertRaises(ValueError, msg=labels):
                validate_dashboard(self.supplement(labels))


if __name__ == '__main__':
    unittest.main()


class NumbersAndMultiples(unittest.TestCase):
    def quote(self, end='2026-09-17'):
        return {'id': 'price', 'unit': 'currency_per_share', 'currency': 'USD', 'scale': 1, 'basis': 'market', 'value': 100,
                'period': {'kind': 'instant', 'end': end, 'label': end, 'forecast': False}}

    def eps(self, start, end, forecast=False):
        return {'id': 'eps', 'unit': 'currency_per_share', 'currency': 'USD', 'scale': 1, 'basis': 'GAAP', 'value': 2,
                'period': {'kind': 'duration', 'start': start, 'end': end, 'label': 'EPS', 'forecast': forecast}}

    def pe(self, eps):
        return {'operation': 'pe', 'unit': 'ratio', 'scale': 1, 'basis': eps['basis'], 'period': eps['period']}

    def test_pe_needs_one_year_of_known_earnings(self):
        from model import calculate
        ttm = self.eps('2025-07-01', '2026-06-30')
        self.assertEqual(calculate(self.pe(ttm), [self.quote(), ttm]), 50)
        quarter = self.eps('2026-04-01', '2026-06-30')
        with self.assertRaisesRegex(Invalid, 'twelve-month'):
            calculate(self.pe(quarter), [self.quote(), quarter])
        later = self.eps('2025-10-01', '2026-09-30')
        with self.assertRaisesRegex(Invalid, 'after the quote'):
            calculate(self.pe(later), [self.quote(), later])
        forward = self.eps('2027-01-01', '2027-12-31', forecast=True)
        self.assertEqual(calculate(self.pe(forward), [self.quote(), forward]), 50)

    def test_rounding_moves_to_the_next_unit(self):
        from model import format_number
        from dashboard import fmt
        e = {'unit': 'currency', 'currency': 'USD', 'scale': 1, 'value': 999_999}
        self.assertEqual(format_number(e), 'USD 1M')
        self.assertEqual(fmt(999_999), '$1M')
        self.assertEqual(fmt(-10), '-$10')

    def test_values_below_the_boundary_keep_their_precision(self):
        from model import format_number
        from dashboard import fmt
        self.assertEqual(fmt(999.49e6), '$999.49M')
        self.assertEqual(format_number({'unit': 'currency', 'currency': 'USD', 'scale': 1, 'value': 999.49e6}), 'USD 999.49M')
