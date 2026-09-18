"""Annotate visible prose without touching links, controls, attributes or exports."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

TERMS = json.loads((Path(__file__).resolve().parent.parent / 'assets/financial-terms.json').read_text())
LOOKUP = {alias.casefold(): term for term in TERMS for alias in term['aliases']}
PATTERN = re.compile(r'(?<![\w/])(' + '|'.join(re.escape(a) for a in sorted(LOOKUP, key=len, reverse=True)) + r')(?![\w/])', re.I)

class Annotator(HTMLParser):
    skip = {'script', 'style', 'textarea', 'code', 'pre', 'a', 'button', 'select', 'option', 'summary', 'svg'}
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    def __init__(self, prefix):
        super().__init__(convert_charrefs=False)
        self.stack, self.out, self.definitions = [], [], []
        self.prefix, self.count = prefix, 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        lang = attrs.get('data-lang', self.stack[-1][1] if self.stack else 'en')
        blocked = tag in self.skip or (self.stack and self.stack[-1][2])
        blocked = blocked or 'term-definition' in attrs.get('class','') or 'stat-meaning' in attrs.get('class','')
        self.out.append(self.get_starttag_text())
        if tag not in self.void:
            self.stack.append((tag, lang, blocked))
    def handle_endtag(self, tag):
        self.out.append(f'</{tag}>')
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text())
    def handle_data(self, text):
        if self.stack and self.stack[-1][2]:
            self.out.append(text)
            return
        lang = self.stack[-1][1] if self.stack else 'en'
        def replace(match):
            term = LOOKUP[match[0].casefold()]
            self.count += 1
            key = f'{self.prefix}-term-{self.count}'
            self.definitions.append(f'<span class="term-definition" id="{key}" role="tooltip" hidden>{html.escape(term[lang])}</span>')
            return f'<button type="button" class="finance-term" aria-describedby="{key}" aria-expanded="false">{match[0]}</button>' 
        self.out.append(PATTERN.sub(replace, text))
    def handle_entityref(self, name): self.out.append(f'&{name};')
    def handle_charref(self, name): self.out.append(f'&#{name};')
    def handle_comment(self, data): self.out.append(f'<!--{data}-->')

def annotate(markup, prefix):
    parser = Annotator(prefix)
    parser.feed(markup)
    return ''.join(parser.out + parser.definitions)
