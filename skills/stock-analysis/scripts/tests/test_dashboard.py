import copy
import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard import chart, chart_data, consensus_card, financial_card, price_card, validate_dashboard


def fixture():
    return {'kind':'visual_research_supplement','identity':'test|test','retrieved_at':'2026-09-24','sources':{'s':{'url':'https://example.com','status':'read','retrieved_at':'2026-09-24'}},'series':{},'market':{},'consensus':{}}


def series(points, scale=1):
    return {'unit':'currency','currency':'USD','scale':scale,'basis':'GAAP','period_kind':'quarter','source_id':'s','source_row':'test','points':[{'period':label,'value':value} for label,value in points]}


class Charts(unittest.TestCase):
    def test_period_focus_contract_preserves_missing_points(self):
        d=fixture();d['series']={'cfo':series([('Q1 2025',10),('Q3 2025',30)]),'fcf':series([('Q1 2025',5),('Q3 2025',20)])}
        for style in ('bar','line'):
            rendered=chart(d,['cfo','fcf'],'en',style)
            tags=[]
            parser=HTMLParser()
            parser.handle_starttag=lambda tag,attrs: tags.append((tag,dict(attrs)))
            parser.feed(rendered)
            points=[a for _,a in tags if 'data-viz-point' in a]
            self.assertEqual(len(points),4)
            self.assertFalse(any(a['data-viz-point']=='1' for a in points))
            self.assertEqual(sum(a['data-selected']=='true' for a in points),2)
            self.assertEqual(len([a for _,a in tags if 'data-viz-focus' in a]),1)
            self.assertEqual(len([a for _,a in tags if 'data-viz-row' in a]),3)
            self.assertIn('data-viz-period-label>Q3 2025</strong>',rendered)
            self.assertEqual(len([a for _,a in tags if 'data-viz-hit' in a]),3)
            slider=[a for _,a in tags if a.get('role')=='slider'][0]
            self.assertEqual(slider['tabindex'],'0')
            self.assertEqual(slider['aria-valuemax'],'2')
            self.assertIn('Q3 2025',slider['aria-valuetext'])
            self.assertNotIn('<select',rendered)

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
        self.assertIn('-$10',rendered);self.assertIn('-$20',rendered)
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


class DataDrivenText(unittest.TestCase):
    def market(self):
        d=fixture()
        d['market']={'overview_quote':{'price':50,'observed_at':'2026-09-23','session':'after_hours','source_id':'s'},
                     'range':{'low':40,'high':60,'low_date':'2026-01-05','high_date':None,'method':'m','source_id':'s'}}
        d['consensus']={'targets':{'low':40,'mean':55,'median':55,'high':70,'horizon_months':6,'source_id':'s'}}
        return validate_dashboard(d)

    def test_quote_session_and_extrema_dates_come_from_data(self):
        out=price_card(self.market(),'en')
        self.assertIn('After hours',out)
        self.assertNotIn('Regular close',out)
        self.assertIn('2026-01-05 / Not supplied',out)

    def test_target_horizon_comes_from_data(self):
        d=self.market()
        self.assertIn('6-month price targets',consensus_card(d,'en'))
        del d['consensus']['targets']['horizon_months']
        self.assertIn('horizon not supplied',consensus_card(d,'en'))

    def test_series_note_and_caveats_need_both_languages(self):
        d=fixture();d['series']={'debt':series([('Q1 2025',10),('Q2 2025',12)])}
        d['series']['debt']['note']={'en':'Includes brokerage funding.','ro':'Include finanțarea brokerajului.'}
        validate_dashboard(d)
        self.assertIn('Include finanțarea brokerajului.',financial_card(d,'Debt',['cash','investments','debt'],'ro',('a','b')))
        d['series']['debt']['note']={'en':'Only English'}
        with self.assertRaises(ValueError):validate_dashboard(d)
        d['series']['debt'].pop('note');d['caveats']=[{'en':'Only English'}]
        with self.assertRaises(ValueError):validate_dashboard(d)


if __name__=='__main__':unittest.main()
