"""Reading-layer checks: visible meaning, retained evidence and frozen history."""
import copy
import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archive import verify_archive
from demo import fixture, update_fixture, bi
from model import Invalid, validate
from render import render


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def all(self, tag=None, cls=None):
        result = [self] if (tag is None or self.tag == tag) and (cls is None or cls in self.attrs.get('class', '').split()) else []
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.all(tag, cls))
        return result

    def text(self, visible=False):
        if visible and (self.tag in {'script', 'style', 'dialog'} or 'hidden' in self.attrs):
            return ''
        children = self.children
        if visible and self.tag == 'details' and 'open' not in self.attrs:
            children = [c for c in children if isinstance(c, Node) and c.tag == 'summary']
        return ''.join(c.text(visible) if isinstance(c, Node) else c for c in children)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in {'meta', 'link', 'input', 'br', 'hr', 'img'}:
            self.stack.append(n)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def by_id(self, key):
        return next(n for n in self.root.all() if n.attrs.get('id') == key)


class Guided(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        self.cash = next(s for s in self.data['sections'] if s['id'] == 'cash')

    def test_visible_story_interpretation_and_lessons_are_complete(self):
        doc = Document(render(self.data))
        for lang in self.data['languages']:
            for section in self.data['sections']:
                node = doc.by_id(lang+'-'+section['id'])
                visible = node.text(True)
                self.assertIn(section['guide']['claims'][0]['text'][lang], visible)
                self.assertIn(section['guide']['why_it_matters']['text'][lang], visible)
                self.assertIn(section['caveat'][lang], visible)
                deep = node.all('details', 'deep-data')[0]
                self.assertNotIn('open', deep.attrs)
                # Every authored interpretation is readable without opening anything.
                for claim in section['claims']:
                    self.assertIn(claim['text'][lang], visible)
                if section.get('lesson'):
                    for part in ('concept', 'example', 'trap'):
                        self.assertIn(section['lesson'][part][lang], visible)
                for metric in section['guide'].get('metrics', []):
                    self.assertIn(metric['meaning']['text'][lang], visible)
            watch = doc.by_id(lang+'-watch').text(True)
            for item in self.data['watchlist']:
                self.assertIn(item['criterion']['description'][lang], watch)
                self.assertIn(item['impact']['adverse'][lang], watch)

    def test_repeated_guide_text_is_shown_once(self):
        self.cash['claims'].insert(0, self.cash['guide']['claims'][0])
        doc = Document(render(self.data))
        for lang in self.data['languages']:
            visible = doc.by_id(lang+'-cash').text(True)
            self.assertEqual(visible.count(self.cash['guide']['claims'][0]['text'][lang]), 1)

    def test_guided_report_requires_every_section_guide(self):
        del self.cash['guide']
        with self.assertRaisesRegex(Invalid, 'every section'):
            validate(self.data)

    def test_explained_metrics_keep_their_provenance(self):
        self.cash['guide']['metrics'][0]['meaning']['evidence_refs'] = ['revenue']
        with self.assertRaisesRegex(Invalid, 'reference its metric'):
            validate(self.data)

    def test_guide_rejects_metric_overload(self):
        self.cash['guide']['metrics'] *= 4
        with self.assertRaisesRegex(Invalid, 'at most three'):
            validate(self.data)

    def test_guide_requires_translated_meaning(self):
        del self.cash['guide']['metrics'][0]['meaning']['text']['ro']
        with self.assertRaises(Invalid):
            validate(self.data)

    def test_forecast_label_remains_visible_and_cannot_be_fact(self):
        forecast = copy.deepcopy(self.data['evidence'][0])
        forecast.update(id='future-sales', kind='estimate')
        forecast['period']['forecast'] = True
        self.data['evidence'].append(forecast)
        metric = self.cash['guide']['metrics'][0]
        metric.update(evidence_ref='future-sales', label=bi('Expected sales','Vânzări estimate'))
        metric['meaning']['evidence_refs'] = ['future-sales']
        doc = Document(render(self.data))
        self.assertIn('Forecast', doc.by_id('en-cash').text(True))
        self.assertIn('Prognoză', doc.by_id('ro-cash').text(True))
        metric['meaning']['type'] = 'fact'
        with self.assertRaisesRegex(Invalid, 'estimate|forecast'):
            validate(self.data)

    def test_sources_have_readable_labels_and_resolvable_groups(self):
        doc = Document(render(self.data))
        ids = [n.attrs['id'] for n in doc.root.all() if 'id' in n.attrs]
        self.assertEqual(len(ids), len(set(ids)))
        buttons = doc.root.all('button', 'ref')
        self.assertTrue(buttons)
        self.assertTrue(any(len(json.loads(b.attrs['data-evidence-ids'])) > 1 for b in buttons))
        for button in buttons:
            self.assertIn(button.text(), {'Sources', 'Surse'})
            for key in json.loads(button.attrs['data-evidence-ids']):
                for lang in self.data['languages']:
                    doc.by_id('ev-'+lang+'-'+key)
        for card in doc.root.all('article', 'evidence-card'):
            for key in json.loads(card.attrs['data-inputs']):
                doc.by_id('ev-en-'+key)

    def test_render_preserves_research_and_baseline_history(self):
        new = update_fixture(self.data)
        before = copy.deepcopy([self.data, new])
        doc = Document(render(new, self.data))
        package = json.loads(doc.by_id('research-package').text())
        verify_archive(package)
        self.assertEqual(before, [self.data, new])
        for report in [self.data, new]:
            self.assertEqual(package['snapshots'][report['report_id']]['research'], report)

    def test_legacy_records_still_render_without_rewriting(self):
        self.data.pop('presentation')
        for section in self.data['sections']:
            section.pop('guide')
        before = copy.deepcopy(self.data)
        doc = Document(render(self.data))
        self.assertIn(self.cash['claims'][0]['text']['en'], doc.by_id('en-cash').text(True))
        self.assertEqual(before, self.data)


if __name__ == '__main__':
    unittest.main()
