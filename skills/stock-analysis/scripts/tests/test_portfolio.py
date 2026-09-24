import copy
from decimal import Decimal as D
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'portfolio.py'
spec = importlib.util.spec_from_file_location('portfolio_calculations', SCRIPT)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def snapshot():
    return {
        'schema_version': '1.0', 'kind': 'portfolio_snapshot', 'synthetic': True,
        'as_of': '2026-09-24', 'scope': 'stock_sleeve', 'base_currency': 'EUR',
        'total_investable_value_base': '200',
        'positions': [
            {'security_id': 'DEMO:A', 'issuer_id': 'DEMO:ONE', 'label': 'A',
             'asset_type': 'company', 'value_base': '20', 'value_source': 'Synthetic',
             'themes': ['theme'], 'theme_source': 'Synthetic'},
            {'security_id': 'DEMO:B', 'issuer_id': 'DEMO:ONE', 'label': 'B',
             'asset_type': 'company', 'value_base': '30', 'value_source': 'Synthetic',
             'themes': ['theme'], 'theme_source': 'Synthetic'},
            {'security_id': 'CASH:EUR', 'label': 'Cash', 'asset_type': 'cash',
             'value_base': '50', 'value_source': 'Synthetic', 'themes': [], 'theme_source': 'Cash'}],
        'target_weights': {'DEMO:A': '.1', 'DEMO:B': '.2', 'CASH:EUR': '.7'},
        'target_basis': 'Invented comparison',
        'policy': {'max_issuer_weight': '.4', 'theme_caps': {'theme': '.4'}, 'basis': 'Invented limits'},
        'scenarios': [{'id': 'stress', 'label': 'Stress', 'horizon': 'One year',
                       'assumptions': 'Both shares lose 60%, cash unchanged',
                       'returns': {'DEMO:A': '-.6', 'DEMO:B': '-.6', 'CASH:EUR': '0'}}]}


class PortfolioTests(unittest.TestCase):
    def test_scope_targets_and_joint_losses(self):
        r = p.calculate(snapshot())
        self.assertEqual(r['portfolio_value_base'], 100)
        self.assertEqual(r['positions'][0]['current_weight_of_total'], D('.1'))
        self.assertEqual(r['scenarios'][0]['current']['change_base'], -30)
        self.assertEqual(r['scenarios'][0]['target']['change_base'], -18)
        self.assertEqual(sum(x['delta_value_base'] for x in r['positions']), 0)
        self.assertEqual(r['suitability'], 'not_assessed_by_calculator')

    def test_issuer_aggregates_share_classes(self):
        r = p.calculate(snapshot())
        self.assertEqual(r['current_exposure']['direct_issuer_weights']['DEMO:ONE'], D('.5'))
        self.assertEqual(len(r['current_exposure']['breaches']), 2)
        self.assertFalse(r['target_exposure']['breaches'])

    def test_missing_sleeve_denominator_stays_unknown(self):
        d = snapshot(); del d['total_investable_value_base']
        self.assertIsNone(p.calculate(d)['positions'][0]['current_weight_of_total'])

    def test_whole_portfolio_denominator(self):
        d = snapshot(); d['scope'] = 'whole_portfolio'
        with self.assertRaises(p.PortfolioError): p.validate(d)
        del d['total_investable_value_base']
        self.assertEqual(p.calculate(d)['positions'][0]['current_weight_of_total'], D('.2'))

    def test_missing_cash_not_silently_redistributed(self):
        for field in ('target_weights', 'scenario'):
            d = snapshot()
            mapping = d['target_weights'] if field == 'target_weights' else d['scenarios'][0]['returns']
            del mapping['CASH:EUR']
            with self.subTest(field=field), self.assertRaises(p.PortfolioError): p.calculate(d)

    def test_invalid_values(self):
        for value in ('NaN', 'Infinity', '-1', True, None, {}, []):
            d = snapshot(); d['positions'][0]['value_base'] = value
            with self.subTest(value=value), self.assertRaises(p.PortfolioError): p.validate(d)

    def test_percent_units_and_unfunded_targets(self):
        for value in ('10', '-.1', '.11'):
            d = snapshot(); d['target_weights']['DEMO:A'] = value
            with self.subTest(value=value), self.assertRaises(p.PortfolioError): p.validate(d)

    def test_total_loss_allowed_but_levered_loss_rejected(self):
        d = snapshot(); d['scenarios'][0]['returns']['DEMO:A'] = '-1'
        self.assertEqual(p.calculate(d)['scenarios'][0]['current']['change_base'], -38)
        d['scenarios'][0]['returns']['DEMO:A'] = '-1.01'
        with self.assertRaises(p.PortfolioError): p.validate(d)

    def test_unknown_theme_coverage_is_visible(self):
        d = snapshot(); d['positions'][0]['themes'] = None
        r = p.calculate(d)
        self.assertEqual(r['target_exposure']['unclassified_theme_weight'], D('.1'))
        self.assertEqual(r['target_exposure']['policy_status'], 'incomplete_theme_coverage')

    def test_overlap_is_not_normalized(self):
        d = snapshot(); d['positions'][0]['themes'].append('second')
        e = p.calculate(d)['current_exposure']
        self.assertEqual(e['tagged_theme_weights'], {'second': D('.2'), 'theme': D('.5')})

    def test_contribution_funds_new_total(self):
        d = snapshot(); d['contribution'] = {'amount_base': '100',
            'allocation_weights': {'DEMO:A': '0', 'DEMO:B': '0', 'CASH:EUR': '1'}}
        r = p.calculate(d)['after_contribution']
        self.assertEqual(r['weights'], {'DEMO:A': D('.1'), 'DEMO:B': D('.15'), 'CASH:EUR': D('.75')})
        self.assertEqual(sum(r['weights'].values()), 1)
        self.assertFalse(r['exposure']['breaches'])

    def test_duplicate_security_and_unknown_policy(self):
        d = snapshot(); d['positions'].append(copy.deepcopy(d['positions'][0]))
        with self.assertRaises(p.PortfolioError): p.validate(d)
        d = snapshot(); d['policy']['minimum_cash'] = '.1'
        with self.assertRaises(p.PortfolioError): p.validate(d)

    def test_unsupported_model_fields_do_not_silently_pass(self):
        for location, key in [('root', 'leverage'), ('position', 'currency'),
                              ('scenario', 'probability')]:
            d = snapshot()
            destination = d if location == 'root' else d['positions'][0] if location == 'position' else d['scenarios'][0]
            destination[key] = 2
            with self.subTest(location=location), self.assertRaises(p.PortfolioError): p.validate(d)

    def test_cli_rejects_duplicate_json_keys_and_nonfinite(self):
        for text in ('{"kind":"portfolio_snapshot","kind":"other"}', '{"x":NaN}'):
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'input.json'; path.write_text(text)
                r = subprocess.run([sys.executable, str(SCRIPT), 'calculate', str(path)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 2)
                self.assertFalse(r.stdout)

    def test_cli_example_from_documentation(self):
        doc = (SCRIPT.parent.parent / 'references/portfolio-data.md').read_text()
        example = doc.split('```json\n')[1].split('```')[0]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.json'; path.write_text(example)
            r = subprocess.run([sys.executable, str(SCRIPT), 'calculate', str(path)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            result = json.loads(r.stdout)
            self.assertEqual(D(result['scenarios'][0]['current']['change_base']), -3000)
            self.assertEqual(D(result['scenarios'][0]['target']['change_base']), -2250)


if __name__ == '__main__':
    unittest.main()
