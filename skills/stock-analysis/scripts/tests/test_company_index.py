import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from archive import catalog,register,write_json
from company_index import enrich_entry,render_index
from demo import fixture,update_fixture
from model import identity,load


class CompanyIndex(unittest.TestCase):
    def test_repository_catalog_and_linked_index(self):
        b=fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=root/'archives/archive.json';r=root/'registry.json'
            (root/'reports').mkdir()
            (root/'reports/report.html').write_text('<html>Saved report</html>')
            register(a,b)
            catalog(r,a,repo_root=root,repository='MarginallyHarmless/stocks_v3',report_path='reports/report.html')
            data=load(r);entry=data['companies'][identity(b['company'])]
            self.assertEqual(entry['archive_path'],'archives/archive.json')
            self.assertNotIn('archive_file_id',entry)
            self.assertEqual(entry['reports'][0]['html_path'],'reports/report.html')
            html=render_index(data,repo_root=root)
            self.assertIn('reports/report.html',html)
            self.assertIn('"embedded_reports": {}',html)
            (root/'reports/report.html').unlink()
            with self.assertRaises(ValueError):
                render_index(data,repo_root=root)

    def test_repository_paths_reject_traversal(self):
        from company_index import repository_file
        with tempfile.TemporaryDirectory() as d:
            for path in ('../report.html','/report.html','reports/../../report.html','https://example.com/report.html'):
                with self.subTest(path=path),self.assertRaises(ValueError):
                    repository_file(d,path)

    def test_catalog_preserves_other_companies_links_and_newer_schedule(self):
        b=fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=root/'archive.json';r=root/'registry.json'
            register(a,b)
            catalog(r,a,'archive-real-id','archive.json','report-real-id','report.html')
            data=load(r);key=identity(b['company'])
            data['companies']['other-company']={'sentinel':'preserved'}
            data['companies'][key]['earnings_events'][0].update(date='2027-01-09',checked_at='2026-12-01')
            write_json(r,data)
            catalog(r,a,'archive-real-id','archive.json')
            after=load(r)
            self.assertEqual(after['companies']['other-company'],{'sentinel':'preserved'})
            self.assertEqual(after['companies'][key]['reports'][0]['html_file_id'],'report-real-id')
            self.assertEqual(after['companies'][key]['earnings_events'][0]['date'],'2027-01-09')

    def test_only_published_matching_period_marks_reviewed(self):
        b=fixture();u=update_fixture(b)
        entry=enrich_entry({},[b,u]);e=next(e for e in entry['earnings_events'] if e['period']==b['next_event']['period'])
        self.assertEqual(e['reviewed_report_id'],u['report_id'])
        wrong=copy.deepcopy(u);wrong['review']['release']['period']='UNRELATED'
        e=enrich_entry({},[b,wrong])['earnings_events'][0]
        self.assertIsNone(e['reviewed_report_id'])
        pending=copy.deepcopy(u);pending['review']['release']['status']='pending'
        self.assertIsNone(enrich_entry({},[b,pending])['earnings_events'][0]['reviewed_report_id'])

    def test_portable_index_embeds_actual_report(self):
        b=fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=root/'archive.json';r=root/'registry.json'
            register(a,b);catalog(r,a,'archive-real-id','archive.json','report-real-id','report.html')
            (root/'report.html').write_text('<html>Saved report</html>')
            html=render_index(load(r),root)
            self.assertIn('PGh0bWw+U2F2ZWQgcmVwb3J0PC9odG1sPg==',html)
            self.assertNotIn('/*INDEX_UI*/',html)

    def test_new_schedule_drops_old_exact_release_time(self):
        b=fixture()
        old=enrich_entry({},[b])
        old['earnings_events'][0]['scheduled_at']='2026-07-01T21:00:00Z'
        b['next_event'].update(date='2026-09-01',checked_at='2026-08-01')
        new=enrich_entry(old,[b])
        self.assertNotIn('scheduled_at',new['earnings_events'][0])
