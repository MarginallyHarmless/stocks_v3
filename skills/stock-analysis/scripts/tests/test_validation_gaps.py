"""Inputs the contract rejects must fail validation, not rendering."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import fixture, bi
from model import Invalid, validate


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


if __name__ == '__main__':
    unittest.main()
