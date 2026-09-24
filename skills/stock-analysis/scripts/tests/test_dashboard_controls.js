// Exercise direct chart inspection: previews, persistent choices, touch and keyboard.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const element = (dataset = {}, textContent = '') => ({dataset, textContent, attrs:{}, handlers:{}, hidden:false,
  setAttribute(k,v) { this.attrs[k]=v; }, getAttribute(k) { return this.attrs[k]; },
  addEventListener(k,fn) { this.handlers[k]=fn; },
  fire(type,extra={}) { const event={preventDefault(){this.prevented=true;},...extra}; this.handlers[type](event); return event; },
  focus() { this.fire('focus'); }});
function fixture(values, periods, names) {
  const readouts = values[0].map((_,i)=>element({vizValue:String(i)}));
  const label = element(), pinned = element(), reset = element();
  const focus = element({start:'64',step:'100'}), chart = element();
  const points = values.flatMap((row,i)=>row.filter(v=>v!=='Not available').map(()=>element({vizPoint:String(i)})));
  const rows = periods.map((_,i)=>element({vizRow:String(i)}));
  const hits = periods.map((_,i)=>element({vizHit:String(i)}));
  hits.forEach(hit=>hit.closest=()=>hit);
  const one = {'.viz-values':element({},JSON.stringify({values,periods,series:names})),
    '[data-viz-period-label]':label,'[data-viz-focus]':focus,'[data-viz-pinned]':pinned,'[data-viz-reset]':reset};
  chart.closest = () => ({querySelector:q=>one[q],querySelectorAll:q=>q==='[data-viz-value]'?readouts:[...points,...rows]});
  chart.contains = el => hits.includes(el);
  return {chart,readouts,label,focus,points,rows,pinned,reset,
    hover(index,pointerType='mouse') { chart.fire('pointermove',{target:hits[index],pointerType}); },
    click(index) { chart.fire('click',{target:hits[index]}); },
    key(key) { return chart.fire('keydown',{key}); }};
}
const cash = fixture([['$-10','$-15'],['Not available','Not available'],['$30','$20']],['Q1 2025','Q2 2025','Q3 2025'],['Operating cash','Free cash']);
const shares = fixture([['100M'],['110M']],['FY 2024','FY 2025'],['Acțiuni']);
const document = {querySelectorAll:q=>q==='.viz-chart'?[cash.chart,shares.chart]:[]};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/dashboard.js'),'utf8'),{document});
assert.equal(cash.label.textContent,'Q3 2025');
assert.ok(cash.reset.hidden);
cash.hover(0);
assert.deepEqual(cash.readouts.map(el=>el.textContent),['$-10','$-15']);
assert.equal(cash.focus.attrs.transform,'translate(114,0)');
assert.equal(cash.chart.attrs['aria-valuetext'],'Q1 2025 · Operating cash: $-10 · Free cash: $-15');
assert.ok(cash.pinned.hidden);
cash.chart.fire('pointerleave');
assert.equal(cash.label.textContent,'Q3 2025');
cash.click(0);
assert.equal(cash.points.filter(el=>el.attrs['data-selected']==='true').length,2);
assert.equal(cash.rows[0].attrs['data-selected'],'true');
assert.ok(!cash.pinned.hidden && !cash.reset.hidden);
cash.hover(1);
assert.deepEqual(cash.readouts.map(el=>el.textContent),['Not available','Not available']);
assert.equal(cash.points.filter(el=>el.attrs['data-selected']==='true').length,0);
assert.ok(cash.pinned.hidden);
cash.chart.fire('pointerleave');
assert.equal(cash.label.textContent,'Q1 2025'); // Restore the pinned choice, not the latest.
cash.hover(2,'touch');
assert.equal(cash.label.textContent,'Q1 2025'); // Touch scrolling must not scrub the chart.
cash.click(2); // Browser-synthesized tap/click selects normally.
assert.equal(cash.label.textContent,'Q3 2025');
assert.equal(shares.label.textContent,'FY 2025'); // Cards are independent.
assert.ok(cash.key('Home').prevented);
assert.equal(cash.label.textContent,'Q1 2025');
cash.key('ArrowRight');
assert.equal(cash.label.textContent,'Q2 2025');
cash.key('ArrowRight'); cash.key('ArrowRight');
assert.equal(cash.chart.attrs['aria-valuenow'],'2');
cash.key('Escape');
assert.equal(cash.label.textContent,'Q3 2025');
assert.ok(cash.pinned.hidden && cash.reset.hidden);
cash.click(0); cash.reset.fire('click');
assert.equal(cash.label.textContent,'Q3 2025');
assert.ok(cash.reset.hidden);
shares.key('Home');
assert.equal(shares.readouts[0].textContent,'100M');
assert.equal(shares.chart.attrs['aria-valuetext'],'FY 2024 · Acțiuni: 100M');
shares.key('End');
assert.equal(shares.readouts[0].textContent,'110M');
assert.ok(!shares.key('Tab').prevented);
console.log('Chart hover, pinning, leave/reset, touch, keyboard and missing periods passed.');
