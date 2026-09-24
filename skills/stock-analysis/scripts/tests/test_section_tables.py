"""Authored section tables are validated and always rendered by the core renderer."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import fixture, bi
from model import Invalid, validate
from render import render


def with_table(rows=None):
    data = fixture()
    data['sections'][0]['tables'] = [{
        'title': bi('Peer matrix', 'Matricea companiilor comparabile'),
        'columns': [bi('Measure', 'Indicator'), bi('Value', 'Valoare')],
        'rows': rows if rows is not None else [[
            {'type': 'fact', 'text': bi('Revenue', 'Venituri'), 'evidence_refs': ['revenue']},
            {'evidence_ref': 'revenue'},
        ]],
    }]
    return data


class SectionTables(unittest.TestCase):
    def test_tables_render_in_every_language(self):
        out = render(with_table())
        self.assertEqual(out.count('class="research-table"'), 2)
        self.assertIn('Peer matrix', out)
        self.assertIn('Matricea companiilor comparabile', out)

    def test_row_width_must_match_columns(self):
        with self.assertRaises(Invalid):
            validate(with_table([[{'evidence_ref': 'revenue'}]]))

    def test_unknown_evidence_is_rejected(self):
        with self.assertRaises(Invalid):
            validate(with_table([[{'evidence_ref': 'revenue'}, {'evidence_ref': 'missing'}]]))


class SavedReportsKeepTables(unittest.TestCase):
    def test_archived_tables_reach_the_published_html(self):
        root = Path(__file__).resolve().parents[4]
        registry = root / 'stock-analysis-registry.json'
        if not registry.exists():
            self.skipTest('Skill used outside the research repository')
        import json
        from company_index import repository_file
        for company in json.loads(registry.read_text())['companies'].values():
            archive = json.loads(repository_file(root, company['archive_path']).read_text())
            for report in company['reports']:
                research = archive['snapshots'][report['report_id']]['research']
                expected = sum(len(s.get('tables', [])) for s in research['sections'])
                html = repository_file(root, report['html_path']).read_text()
                self.assertEqual(html.count('class="research-table"'), expected * len(research['languages']),
                                 report['report_id'])


if __name__ == '__main__':
    unittest.main()
