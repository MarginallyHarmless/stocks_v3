// Exercise state transitions without claiming browser/layout verification.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const element = (extra = {}) => Object.assign({
  dataset: {}, handlers: {}, attrs: {}, hidden: false, open: false, value: '',
  addEventListener(type, fn) { this.handlers[type] = fn; },
  getAttribute(key) { return this.attrs[key]; },
  setAttribute(key, value) { this.attrs[key] = value; },
  fire(type) { this.handlers[type]({currentTarget: this, target: this}); },
  scrollIntoView() { this.scrolled = true; }
}, extra);
const language = element({value:'en', options:[{value:'en'}, {value:'ro'}]});
const reading = element();
const theme = element();
const dialog = element({opens:0, showModal() { assert.equal(this.open, false); this.open = true; this.opens++; }, close() { this.open = false; }});
const ids = {language, reading, theme, 'evidence-dialog':dialog};
for (const id of ['expand-lessons','evidence-search','open-sources','close-sources']) ids[id] = element();
ids['expand-lessons'].attrs['aria-expanded'] = 'false';
const langs = ['en','ro'].map(lang => element({dataset:{lang}}));
const details = [element({open:true}), element({open:true})];
const lessons = [element(), element()];
const cards = [];
for (const parentElement of langs) {
  for (const key of ['fcf','cfo','capex','revenue','dilution']) {
    const card = element({parentElement, textContent:key,
      dataset:{evidenceKey:key, inputs:JSON.stringify(key === 'fcf' ? ['cfo','capex'] : [])}});
    ids['ev-'+parentElement.dataset.lang+'-'+key] = card;
    cards.push(card);
  }
}
const source = element({dataset:{evidence:'fcf', evidenceIds:'["fcf","revenue"]'}});
const nested = element({dataset:{evidence:'cfo', evidenceIds:'["cfo","capex"]'}});
const groups = {'[data-lang]':langs, '.deep-data':details, '.lesson':lessons,
  '[data-evidence]':[source,nested], '.evidence-card':cards, '[data-copy]':[], '[data-export]':[]};
const document = {body:element(), documentElement:{lang:'en'},
  querySelector:sel => ids[sel.slice(1)], querySelectorAll:sel => groups[sel], getElementById:id => ids[id]};
const preferences = new Map([['stock-v3-reading','experienced'], ['stock-v3-language','ro'], ['stock-v3-theme','light']]);
const localStorage = {getItem:key => preferences.get(key), setItem:(key,value) => preferences.set(key,value)};
const sourceCode = fs.readFileSync(path.join(__dirname,'../../assets/report.js'),'utf8');
vm.runInNewContext(sourceCode, {document,localStorage});
assert.equal(reading.value,'beginner'); // Old mode preference must not defeat the new first-use default.
assert.ok(details.every(d => !d.open));
assert.equal(language.value,'ro');
assert.equal(theme.value,'light');
reading.value = 'experienced'; reading.fire('change');
assert.ok(details.every(d => d.open));
language.value = 'en'; language.fire('change');
assert.equal(reading.value,'experienced');
assert.ok(details.every(d => d.open));
assert.equal(theme.value,'light');
source.fire('click');
assert.equal(dialog.opens,1);
assert.ok(cards.filter(c => c.dataset.evidenceKey !== 'dilution').every(c => !c.hidden));
assert.ok(cards.filter(c => c.dataset.evidenceKey === 'dilution').every(c => c.hidden));
assert.ok(ids['ev-en-fcf'].scrolled);
nested.fire('click');
assert.equal(dialog.opens,1);
assert.ok(!ids['ev-en-capex'].hidden);
ids['open-sources'].fire('click');
assert.ok(cards.every(c => !c.hidden));
ids['expand-lessons'].fire('click');
assert.equal(reading.value,'beginner');
assert.ok(details.every(d => !d.open));
assert.ok(lessons.every(d => d.open));
assert.equal(language.value,'en');
assert.equal(theme.value,'light');
ids['close-sources'].fire('click');
assert.equal(dialog.open,false);
console.log('Reading modes, independent preferences and nested grouped sources passed.');
require('./test_dashboard_controls.js');
