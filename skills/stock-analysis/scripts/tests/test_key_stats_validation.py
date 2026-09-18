import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import fixture
from model import Invalid, validate

class KeyStatsValidationTests(unittest.TestCase):
    def test_concept_identifier_and_localized_label_are_valid(self):
        data = fixture()
        data['key_stats'] = [{'concept': 'revenue', 'evidence_ref': 'revenue',
                              'label': {'en': 'Sales', 'ro': 'Venituri'}}]
        validate(data)
        data['key_stats'][0]['label'].pop('ro')
        with self.assertRaises(Invalid):
            validate(data)

    def test_lesson_concept_still_requires_translation(self):
        data = fixture()
        data['sections'][0]['lesson']['concept'] = 'English only'
        with self.assertRaises(Invalid):
            validate(data)
