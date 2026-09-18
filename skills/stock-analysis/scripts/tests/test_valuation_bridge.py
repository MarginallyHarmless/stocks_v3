import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import calculate, Invalid
from render import evidence_table_html
from render import metrics_html
from html.parser import HTMLParser

class ValuationBridgeTests(unittest.TestCase):
    def setUp(self):
        self.p = dict(kind='instant', end='2026-09-17', label='Quote', forecast=False)
        self.price = dict(value=10, scale=1, unit='currency_per_share', currency='USD', basis='market', period=self.p)
        self.shares = dict(value=20, scale=1000000, unit='shares', basis='GAAP', period=dict(self.p, end='2026-09-14'))
        self.out = dict(operation='equity_value', scale=1000000, unit='currency', currency='USD', basis='model', period=self.p, model_assumptions='Latest filed basic count, no later issuance assumed.')
    def test_scale_and_dated_share_count(self):
        self.assertEqual(calculate(self.out, [self.price, self.shares]), 200)
    def test_future_shares_rejected(self):
        s=copy.deepcopy(self.shares); s['period']['end']='2026-09-18'
        with self.assertRaises(Invalid): calculate(self.out,[self.price,s])
    def test_currency_mismatch_rejected(self):
        out=dict(self.out,operation='valuation_multiple',unit='ratio',scale=1);out.pop('currency')
        sales=dict(value=25,scale=1000000,unit='currency',currency='EUR',basis='GAAP',period=dict(kind='duration',start='2026-01-01',end='2026-12-31',label='FY',forecast=True))
        with self.assertRaises(Invalid):calculate(out,[dict(self.out,value=200),sales])
        sales['currency']='USD'
        self.assertEqual(calculate(out,[dict(self.out,value=200),sales]),8)
    def test_table_escapes_and_uses_ledger(self):
        e=dict(id='a',value=25,scale=1,unit='percent',precision=1,kind='fact',label='Margin',state='Unused')
        table=dict(title={'en':'A < B','ro':'A > B'},columns=['Metric','Company'],rows=[dict(label='Margin',cells=[dict(evidence_ref='a')])])
        out=evidence_table_html(table,{'a':e},'en')
        self.assertIn('25.0%',out);self.assertIn('A &lt; B',out);self.assertIn('data-evidence="a"',out)

    def test_shared_model_assumptions_do_not_become_metric_columns(self):
        evidence={key:dict(id=key,value=3,scale=1,unit='currency_per_share',currency='USD',basis='model',period=self.p,kind='calculation',label=key,model_assumptions='Shared conditional model.') for key in ['bear','base','bull']}
        rendered=metrics_html(list(evidence),evidence,'en')
        class Children(HTMLParser):
            def __init__(self): super().__init__();self.stack=[];self.columns=[]
            def handle_starttag(self,tag,attrs):
                cls=dict(attrs).get('class','')
                if self.stack and self.stack[-1]=='metrics': self.columns.append(cls)
                self.stack.append(cls)
            def handle_endtag(self,tag):
                if self.stack:self.stack.pop()
        parser=Children();parser.feed(rendered)
        self.assertEqual(parser.columns,['metric','metric','metric'])
        self.assertEqual(rendered.count('Shared conditional model.'),1)

if __name__=='__main__': unittest.main()
