import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from financial_terms import annotate

class FinancialTermsTests(unittest.TestCase):
    def test_bilingual_key_stat_uses_machine_concept_and_translated_label(self):
        from demo import fixture
        from model import validate, Invalid
        data = fixture()
        data['key_stats'] = [{'concept': 'revenue', 'evidence_ref': 'revenue',
                              'label': {'en': 'Revenue', 'ro': 'Venituri'}}]
        validate(data)
        data['key_stats'][0]['label'] = {'en': 'Revenue'}
        with self.assertRaises(Invalid):
            validate(data)

    def test_longest_match_and_boundaries(self):
        out = annotate('<p>non-GAAP GAAP P/E forward P/E EPS PEPSICO</p>', 'x')
        self.assertEqual(out.count('class="finance-term"'), 5)
        self.assertIn('>non-GAAP</button>', out)
        self.assertIn('>forward P/E</button>', out)
        self.assertIn(' PEPSICO</p>', out)
    def test_controls_attributes_and_export_unchanged(self):
        source = '<a href="/GAAP">GAAP</a><button data-evidence="EPS">EPS</button><script type="application/json">{"EPS":2}</script><textarea>GAAP</textarea><svg><text>EPS</text></svg>'
        self.assertEqual(annotate(source, 'x'), source)
    def test_locale_and_unique_accessible_references(self):
        out = annotate('<div data-lang="ro"><p>GAAP EPS</p></div><p>EPS</p>', 'x')
        self.assertIn('Reguli contabile', out)
        self.assertIn('Earnings per share:', out)
        for i in range(1,4):
            self.assertEqual(out.count(f'id="x-term-{i}"'), 1)
            self.assertEqual(out.count(f'aria-describedby="x-term-{i}"'), 1)
    def test_entities_preserved(self):
        out = annotate('<p>GAAP &amp; &lt;EPS&gt;</p>', 'x')
        self.assertIn('&amp;', out)
        self.assertIn('&lt;', out)
        self.assertIn('&gt;', out)

if __name__ == '__main__': unittest.main()
