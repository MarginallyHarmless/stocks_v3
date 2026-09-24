"""Editorial revisions and replaced reports stay traceable on the page."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import fixture, bi
from model import Invalid, digest, validate
from render import render


class Revisions(unittest.TestCase):
    def setUp(self):
        self.old = fixture()
        self.new = copy.deepcopy(self.old)
        self.new.update(report_id=self.old['report_id'] + '-r2', prepared_at='2026-05-11T12:00:00Z',
                        editorial_revision_of=self.old['report_id'],
                        revision_note=bi('Provenance correction only.', 'Doar corecție de proveniență.'))
        self.archive = {'schema_version': '3.0', 'kind': 'company_archive',
                        'identity': self.old['company']['issuer_id'] + '|' + self.old['company']['security_id'],
                        'snapshots': {d['report_id']: {'sha256': digest(d), 'research': d} for d in (self.old, self.new)}}
        self.links = {self.old['report_id']: 'old.html', self.new['report_id']: 'new.html'}

    def test_revision_shows_its_note_and_original(self):
        out = render(self.new, archive=self.archive, report_links=self.links)
        self.assertIn('Editorial revision of <a href="old.html">', out)
        self.assertIn('Doar corecție de proveniență.', out)
        self.assertNotIn('replaces this one', out)

    def test_replaced_report_points_to_the_newer_one(self):
        out = render(self.old, archive=self.archive, report_links=self.links)
        self.assertIn('A newer saved report replaces this one: <a href="new.html">', out)

    def test_revision_note_requires_the_revised_id(self):
        del self.new['editorial_revision_of']
        with self.assertRaises(Invalid):
            validate(self.new)


if __name__ == '__main__':
    unittest.main()
