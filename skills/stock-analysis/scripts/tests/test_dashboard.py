import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard import chart, chart_data, validate_dashboard


def fixture():
    return {'kind':'visual_research_supplement','identity':'test|test','retrieved_at':'2026-09-24','sources':{'s':{'url':'https://example.com','status':'read','retrieved_at':'2026-09-24'}},'series':{},'market':{},'consensus':{}}


def series(points, scale=1):
    return {'unit':'currency','currency':'USD','scale':scale,'basis':'GAAP','period_kind':'quarter','source_id':'s','source_row':'test','points':[{'period':label,'value':value} for label,value in points]}


class Charts(unittest.TestCase):
    def test_period_alignment_and_missing_quarter(self):
        d=fixture();d['series']={'cfo':series([('Q1 2025',10),('Q3 2025',30)]),'fcf':series([('Q1 2025',5),('Q3 2025',20)])}
        _,labels,values=chart_data(d,['cfo','fcf'])
        self.assertEqual(labels,['Q1 2025','Q2 2025','Q3 2025'])
        self.assertEqual(values,[[10,None,30],[5,None,20]])
        # A line must not bridge the absent middle quarter.
        self.assertNotIn('<polyline',chart(d,['cfo'], 'en','line'))

    def test_shared_axis_normalizes_scales(self):
        d=fixture();d['series']={'cash':series([('Q1 2025',1)],1e9),'debt':series([('Q1 2025',500)],1e6)}
        self.assertEqual(chart_data(d,['cash','debt'])[2],[[1e9],[5e8]])
        d['series']['debt']['period_kind']='annual'
        with self.assertRaises(ValueError):chart_data(d,['cash','debt'])

    def test_negative_values_preserve_series_and_zero_baseline(self):
        d=fixture();d['series']={'cfo':series([('Q1 2025',-10)]),'fcf':series([('Q1 2025',-20)])}
        rendered=chart(d,['cfo','fcf'],'en')
        self.assertIn('$-10',rendered);self.assertIn('$-20',rendered)
        self.assertIn('fill="var(--plot-violet)"',rendered)
        self.assertIn('fill="var(--plot-mint)"',rendered)
        self.assertNotIn('fill="var(--plot-loss)"',rendered)

    def test_identity_rating_counts_and_nonpositive_pe(self):
        d=fixture();validate_dashboard(d,'test|test')
        with self.assertRaises(ValueError):validate_dashboard(d,'wrong')
        d['series']['pe']=dict(series([('Q1 2025',-2)]),unit='ratio',currency=None)
        with self.assertRaises(ValueError):validate_dashboard(d)
        d['series']={};d['consensus']['ratings']={'counts':{'Strong Buy':1,'Buy':1,'Hold':1,'Sell':0,'Strong Sell':0},'total':2,'source_id':'s','score':2}
        with self.assertRaises(ValueError):validate_dashboard(d)

    def test_median_requires_eight_usable_points(self):
        d=fixture();d['series']['pe']=dict(series([(f'Q{i%4+1} {2023+i//4}',i+1) for i in range(8)]),unit='ratio',currency=None)
        self.assertIn('viz-median',chart(d,['pe'],'en','line',True))
        d['series']['pe']['points'][2]['value']=None
        self.assertNotIn('class="viz-median"',chart(d,['pe'],'en','line',True))


if __name__=='__main__':unittest.main()
