import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from labels import period, basis, cell
from model import format_number
from dashboard import fmt


class RomanianLabels(unittest.TestCase):
    def test_periods(self):
        self.assertEqual(period('Q2 2026', 'ro'), 'T2 2026')
        self.assertEqual(period('Q226', 'ro'), 'T2 2026')
        self.assertEqual(period('H1 2026', 'ro'), 'S1 2026')
        self.assertEqual(period('TTM to June 30, 2026', 'ro'), 'TTM până la 30 iunie 2026')
        self.assertEqual(period('Sep 23, 2026, 4:00 PM EDT', 'ro'), '23 sept. 2026, 16:00 EDT')
        self.assertEqual(period('Q2 2026', 'en'), 'Q2 2026')
        self.assertEqual(basis('operating', 'ro'), 'operațional')

    def test_cells_translate_only_whole_periods(self):
        self.assertEqual(cell('Q324', 'ro'), 'T3 2024')
        self.assertEqual(cell('APP-Q3-REVENUE', 'ro'), 'APP-Q3-REVENUE')

    def test_romanian_amounts(self):
        e = {'unit': 'currency', 'currency': 'USD', 'scale': 1, 'value': 2.89e9}
        self.assertEqual(format_number(e, 'ro'), '2,89 mld. USD')
        self.assertEqual(format_number(e, 'en'), 'USD 2.89B')
        self.assertEqual(format_number({'unit': 'shares', 'scale': 1, 'value': 357e6}, 'ro'), '357 mil.')
        self.assertEqual(format_number({'unit': 'currency_per_share', 'currency': 'USD', 'scale': 1, 'value': 8.73}, 'ro'), '8,73 USD')
        self.assertEqual(fmt(2.76e9, lang='ro'), '2,76 mld. USD')
        self.assertEqual(fmt(-308.7e6, lang='ro', digits=1, axis=True), '-308,7 mil.')
        self.assertEqual(fmt(None, lang='ro'), 'N/D')


if __name__ == '__main__':
    unittest.main()
