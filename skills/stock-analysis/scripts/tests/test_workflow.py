import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from archive import baseline, catalog, register, verify_archive, write_json
from demo import fixture, update_fixture, period, bi
from model import Invalid, calculate, digest, format_number, identity, load, recompute, validate
from render import render, compare


class Workflow(unittest.TestCase):
    def setUp(self):
        self.base=fixture()
        self.new=update_fixture(self.base)
        self.ev={e['id']:e for e in self.base['evidence']}

    def test_consecutive_reports_and_export(self):
        validate(self.base);validate(self.new,self.base)
        html=render(self.new,self.base)
        package=json.loads(re.search(r'id="research-package">(.*?)</script>',html,re.S).group(1))
        verify_archive(package)
        self.assertEqual(len(package['snapshots']),2)
        self.assertEqual([x['outcome'] for x in self.new['review']['outcomes']],['Met','Missed','Not disclosed'])

    def test_wrong_currency_rejected(self):
        self.ev['capex']['currency']='EUR'
        with self.assertRaisesRegex(Invalid,'currenc'):validate(self.base)

    def test_wrong_fiscal_period_rejected(self):
        self.ev['capex']['period']=period('Q2 2026','2026-04-01','2026-06-30')
        with self.assertRaisesRegex(Invalid,'period'):validate(self.base)

    def test_wrong_accounting_basis_rejected(self):
        self.ev['capex']['basis']='adjusted'
        with self.assertRaisesRegex(Invalid,'bases'):validate(self.base)

    def test_scales_are_normalized(self):
        self.ev['capex'].update(value=6000000,scale=1)
        validate(self.base)
        self.assertEqual(format_number(self.ev['capex']),'USD 6M')

    def test_numeric_display_override_rejected(self):
        self.ev['revenue']['display']='USD 999M'
        with self.assertRaisesRegex(Invalid,'display'):validate(self.base)

    def test_summary_missing_provenance_rejected(self):
        self.base['summary'][0]['evidence_refs']=[]
        with self.assertRaisesRegex(Invalid,'supporting evidence'):validate(self.base)

    def test_fact_claim_cannot_hide_assumption_in_calculation(self):
        self.ev['capex']['kind']='assumption';self.ev['capex']['rationale']='Test assumption'
        self.base['summary'][0].update(type='fact',evidence_refs=['fcf'])
        with self.assertRaisesRegex(Invalid,'assumption'):validate(self.base)

    def test_unread_source_cannot_support_fact(self):
        self.base['sources'][0]['status']='pending'
        with self.assertRaisesRegex(Invalid,'Unread'):validate(self.base)

    def test_source_cannot_postdate_cutoff(self):
        self.base['sources'][0]['published_at']='2027-01-01T00:00:00Z'
        with self.assertRaisesRegex(Invalid,'after'):validate(self.base)

    def test_negative_fcf_is_valid(self):
        self.ev['capex']['value']=30
        d=recompute(self.base);validate(d)
        e={x['id']:x for x in d['evidence']}
        self.assertEqual(e['fcf-margin']['value'],-12)

    def test_nonpositive_ratio_denominator_rejected(self):
        self.ev['revenue']['value']=0
        with self.assertRaisesRegex(Invalid,'denominator'):recompute(self.base)

    def test_calculation_cycle_rejected(self):
        self.ev['fcf']['inputs']=['fcf','capex']
        with self.assertRaisesRegex(Invalid,'cycle'):validate(self.base)

    def test_cagr_uses_elapsed_endpoints(self):
        old=copy.deepcopy(self.ev['revenue']);new=copy.deepcopy(old)
        old['period']=period('FY2020','2020-01-01','2020-12-31')
        new['period']=period('FY2025','2025-01-01','2025-12-31');new['value']=200
        output=copy.deepcopy(self.ev['dilution']);output.update(period=new['period'],parameters={'years':5})
        output['operation']='cagr'
        self.assertAlmostEqual(calculate(output,[new,old]),14.8698354997)
        output['parameters']['years']=4
        with self.assertRaisesRegex(Invalid,'years'):calculate(output,[new,old])

    def test_ttm_respects_periods(self):
        fy=copy.deepcopy(self.ev['revenue']);fy.update(value=400,period=period('FY2025','2025-01-01','2025-12-31'))
        cur=copy.deepcopy(fy);cur.update(value=120,period=period('Q1 2026','2026-01-01','2026-03-31'))
        prev=copy.deepcopy(fy);prev.update(value=100,period=period('Q1 2025','2025-01-01','2025-03-31'))
        out=copy.deepcopy(fy);out.update(operation='ttm',period=period('TTM Q1 2026','2025-04-01','2026-03-31'))
        self.assertEqual(calculate(out,[fy,cur,prev]),420)
        prev['period']['start']='2025-02-01'
        with self.assertRaisesRegex(Invalid,'YTD'):calculate(out,[fy,cur,prev])

    def test_conditional_price_and_discount_horizon(self):
        eps=copy.deepcopy(self.ev['revenue']);eps.update(value=5,scale=1,unit='currency_per_share',kind='assumption',basis='model',period={**period('FY2029','2029-01-01','2029-12-31'),'forecast':True})
        multiple=copy.deepcopy(eps);multiple.update(value=20,unit='ratio');multiple.pop('currency')
        output=copy.deepcopy(eps);output.update(operation='eps_multiple',model_assumptions='Terminal EPS times selected P/E')
        self.assertEqual(calculate(output,[eps,multiple]),100)
        future=copy.deepcopy(output);future['value']=100
        rate=copy.deepcopy(multiple);rate['value']=.1
        present=copy.deepcopy(output);present.update(operation='discounted_value',parameters={'years':3},period={'kind':'instant','end':'2026-12-31','label':'2026-12-31','forecast':False})
        self.assertAlmostEqual(calculate(present,[future,rate]),75.1314800902)
        present['parameters']['years']=4
        with self.assertRaisesRegex(Invalid,'Discount'):calculate(present,[future,rate])

    def test_required_revenue_depends_on_assumed_multiple(self):
        equity=copy.deepcopy(self.ev['revenue']);equity['value']=1000
        mult=copy.deepcopy(self.ev['dilution']);mult.update(value=5,unit='ratio',scale=1)
        output=copy.deepcopy(equity);output.update(operation='required_revenue',basis='model',model_assumptions='Fixed equity value and chosen P/S anchor')
        self.assertEqual(calculate(output,[equity,mult]),200)
        mult['value']=4
        self.assertEqual(calculate(output,[equity,mult]),250)

    def test_return_horizons_can_reverse(self):
        self.assertEqual((200/100-1)*100,100)
        self.assertEqual((200/50-1)*100,300)

    def test_complete_original_checklist_required(self):
        self.base['checklist'].pop('C10.1')
        with self.assertRaisesRegex(Invalid,'original'):validate(self.base)

    def test_missing_translation_rejected(self):
        self.base['sections'][0]['question']={'en':'What is this?'}
        with self.assertRaisesRegex(Invalid,'translation'):validate(self.base)

    def test_confirmed_event_needs_issuer(self):
        self.base['next_event']['confidence']='Confirmed'
        with self.assertRaisesRegex(Invalid,'issuer'):validate(self.base)

    def test_unannounced_event_has_no_date(self):
        self.base['next_event']['confidence']='Not announced'
        with self.assertRaisesRegex(Invalid,'null date'):validate(self.base)

    def test_schedule_change_preserves_watchlist(self):
        d=copy.deepcopy(self.base);d['next_event']['date']='2026-08-12'
        validate(d)
        self.assertEqual(d['watchlist'],self.base['watchlist'])

    def test_security_identity_rejects_other_share_class(self):
        self.new['company']['security_id']='another-share-class'
        with self.assertRaisesRegex(Invalid,'security'):validate(self.new,self.base)

    def test_ticker_change_preserves_security(self):
        self.new['company']['ticker']='NEW-DEMO'
        validate(self.new,self.base)

    def test_every_original_item_has_one_outcome(self):
        self.new['review']['outcomes'].pop()
        with self.assertRaisesRegex(Invalid,'exactly one'):validate(self.new,self.base)

    def test_threshold_cannot_be_rewritten(self):
        self.base['watchlist'][0]['criterion']['value']=6
        with self.assertRaisesRegex(Invalid,'hash mismatch'):validate(self.new,self.base)

    def test_numeric_miss_cannot_be_called_met(self):
        self.new['review']['outcomes'][1]['outcome']='Met'
        with self.assertRaisesRegex(Invalid,'contradicts'):validate(self.new,self.base)

    def test_numeric_miss_cannot_be_called_mixed(self):
        self.new['review']['outcomes'][1]['outcome']='Mixed'
        with self.assertRaisesRegex(Invalid,'Mixed'):validate(self.new,self.base)

    def test_definition_change_requires_not_comparable(self):
        e={x['id']:x for x in self.new['evidence']};e['op-margin']['basis']='adjusted'
        with self.assertRaisesRegex(Invalid,'not comparable'):validate(self.new,self.base)
        o=self.new['review']['outcomes'][1];o.update(outcome='Not comparable',comparability_reason=bi('Adjusted definition differs.','Definiția ajustată diferă.'))
        validate(self.new,self.base)

    def test_not_disclosed_requires_read_sources(self):
        self.new['review']['outcomes'][2]['checked_source_ids']=[]
        with self.assertRaisesRegex(Invalid,'sources actually checked'):validate(self.new,self.base)

    def test_pending_release_does_not_resolve_any_item(self):
        self.new['review']['release']['status']='pending'
        self.new['watchlist']=copy.deepcopy(self.base['watchlist'])
        with self.assertRaisesRegex(Invalid,'Unpublished'):validate(self.new,self.base)
        for o in self.new['review']['outcomes']:o['outcome']='Not yet due'
        validate(self.new,self.base)

    def test_later_milestone_not_missed_early(self):
        self.base['watchlist'][1]['due_period']='FY2026'
        self.new['review']['baseline_sha256']=digest(self.base)
        self.new['review']['outcomes'][1]['criterion_sha256']=digest(self.base['watchlist'][1])
        with self.assertRaisesRegex(Invalid,'intervening'):validate(self.new,self.base)
        self.new['review']['outcomes'][1]['outcome']='Not yet due'
        validate(self.new,self.base)

    def test_future_criterion_change_needs_version(self):
        self.new['watchlist'][0]['criterion_version']=1
        with self.assertRaisesRegex(Invalid,'new version'):validate(self.new,self.base)

    def test_restatement_preserves_original(self):
        original=digest(self.base)
        e=copy.deepcopy(self.ev['op-margin']);e.update(id='restated-op',value=10)
        self.new['evidence'].append(e)
        self.new['review']['outcomes'][1].update(restated_baseline_ref='restated-op',restatement_note=bi('Original 12%, later restated 10%.','Inițial 12%, ulterior retratat la 10%.'))
        validate(self.new,self.base)
        self.assertEqual(digest(self.base),original)

    def test_archive_idempotence_and_immutable_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json'
            register(p,self.base);register(p,self.new)
            self.assertEqual(register(p,self.new)['status'],'unchanged')
            changed=copy.deepcopy(self.base);changed['evidence_gaps']=bi('Changed','Modificat')
            with self.assertRaisesRegex(Invalid,'immutable'):register(p,changed)
            self.assertEqual(len(load(p)['snapshots']),2)

    def test_duplicate_release_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';register(p,self.base);register(p,self.new)
            d=copy.deepcopy(self.new);d['report_id']='rerun'
            with self.assertRaisesRegex(Invalid,'already reviewed'):register(p,d)

    def test_revision_keeps_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';register(p,self.base);register(p,self.new)
            d=copy.deepcopy(self.new);d.update(report_id='complete-review',supersedes_report_id=self.new['report_id'],cutoff='2026-08-08T12:00:00Z')
            d['review']['provisional']=False
            register(p,d);a=verify_archive(load(p))
            self.assertEqual(len(a['snapshots']),3)
            third=copy.deepcopy(d);third.update(report_id='amended-review',supersedes_report_id=d['report_id'],cutoff='2026-08-10T12:00:00Z')
            register(p,third)
            self.assertEqual(len(verify_archive(load(p))['snapshots']),4)

    def test_baseline_fresh_process_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';register(p,self.base);register(p,self.new)
            a=json.loads(p.read_text())
            d=baseline(a,identity(self.base['company']),before='2026-08-05T12:00:00Z')
            self.assertEqual(d['report_id'],self.base['report_id'])
            with self.assertRaisesRegex(Invalid,'Wrong company'):baseline(a,'wrong|security',report_id=self.base['report_id'])

    def test_editorial_revision_with_same_cutoff_is_selected_as_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';register(p,self.base)
            revised=copy.deepcopy(self.base);revised.update(report_id=self.base['report_id']+'-r2',prepared_at='2026-08-04T12:00:00Z')
            register(p,revised)
            a=json.loads(p.read_text())
            d=baseline(a,identity(self.base['company']),before='2026-08-05T12:00:00Z')
            self.assertEqual(d['report_id'],revised['report_id'])
            reg=Path(tmp)/'registry.json';catalog(reg,p,'file-1','archive.json')
            self.assertEqual(next(iter(load(reg)['companies'].values()))['latest_report_id'],revised['report_id'])

    def test_archive_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';register(p,self.base);a=load(p)
            a['snapshots'][self.base['report_id']]['research']['cutoff']='2027-01-01T00:00:00Z'
            with self.assertRaisesRegex(Invalid,'modified'):verify_archive(a)

    def test_registry_retains_real_file_identity_and_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'archive.json';r=Path(tmp)/'registry.json'
            register(p,self.base);self.new['company']['ticker']='NEW';register(p,self.new)
            catalog(r,p,'test-returned-file-id','test-archive.json')
            item=load(r)['companies'][identity(self.base['company'])]
            self.assertEqual(item['archive_file_id'],'test-returned-file-id')
            self.assertEqual(item['ticker_aliases'],['ALDR-DEMO','NEW'])

    def test_html_escapes_prose_and_embedded_data(self):
        self.base['summary'][0]['text']=bi('</script><img src=x onerror=alert(1)>','<img src=x>')
        out=render(self.base)
        self.assertNotIn('<img src=x',out)
        self.assertIn('&lt;img',out)
        self.assertIn('\\u003c/script\\u003e',out)

    def test_render_does_not_create_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            before=list(Path(tmp).iterdir());render(self.base)
            self.assertEqual(before,list(Path(tmp).iterdir()))

    def test_compare_rejects_mismatched_currencies(self):
        other=copy.deepcopy(self.base);other['report_id']='other'
        other['company']['security_id']='fictional:other'
        for e in other['evidence']:
            if e.get('currency'):e['currency']='EUR'
        spec={'title':'Comparison','summary':'Different currencies','limitations':'Fictional','rows':[{'question':'Revenue','interpretation':'Do not compare without FX','status':'Comparable','values':{self.base['report_id']:'revenue','other':'revenue'}}]}
        with self.assertRaisesRegex(Invalid,'Not comparable'):compare([self.base,other],spec)
        spec['rows'][0]['status']='Not comparable'
        self.assertIn('Not comparable',compare([self.base,other],spec))


if __name__=='__main__':unittest.main()
