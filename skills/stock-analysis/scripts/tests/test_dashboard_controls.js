// Regression: period selection must change chart focus as well as headline values.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const element = (dataset = {}, textContent = '') => ({dataset, textContent, attrs:{},
  setAttribute(k,v) { this.attrs[k]=v; }, getAttribute(k) { return this.attrs[k]; }});
function fixture(values, periods, chartLabel) {
  const readouts = values[0].map((_,i)=>element({vizValue:String(i)}));
  const label = element();
  const focus = element({start:'64',step:'100'});
  const chart = element(); chart.attrs['aria-label']=chartLabel;
  const points = values.flatMap((row,i)=>row.filter(v=>v!=='Not available').map(()=>element({vizPoint:String(i)})));
  const rows = periods.map((_,i)=>element({vizRow:String(i)}));
  const one = {'.viz-values':element({},JSON.stringify(values)),'.viz-chart':chart,
    '[data-viz-period-label]':label,'[data-viz-focus]':focus};
  const card = {querySelector:q=>one[q],querySelectorAll:q=>q==='[data-viz-value]'?readouts:[...points,...rows]};
  const select = {value:String(periods.length-1),closest:()=>card,handlers:{},
    get selectedOptions() { return [{textContent:periods[Number(this.value)]}]; },
    addEventListener(name,fn) { this.handlers[name]=fn; },
    choose(index) { this.value=String(index); this.handlers.change(); }};
  return {select,readouts,label,focus,chart,points,rows};
}
const cash = fixture([['$-10','$-15'],['Not available','Not available'],['$30','$20']],['Q1 2025','Q2 2025','Q3 2025'],'Cash flow');
const shares = fixture([['100M'],['110M']],['FY 2024','FY 2025'],'Acțiuni');
const document = {querySelectorAll:q=>q==='.viz-period'?[cash.select,shares.select]:[]};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/dashboard.js'),'utf8'),{document});
assert.equal(cash.label.textContent,'Q3 2025');
assert.deepEqual(cash.readouts.map(el=>el.textContent),['$30','$20']);
cash.select.choose(0);
assert.deepEqual(cash.readouts.map(el=>el.textContent),['$-10','$-15']);
assert.equal(cash.label.textContent,'Q1 2025');
assert.equal(cash.focus.attrs.transform,'translate(114,0)');
assert.equal(cash.chart.attrs['aria-label'],'Cash flow — Q1 2025');
assert.equal(cash.points.filter(el=>el.attrs['data-selected']==='true').length,2);
assert.equal(cash.rows[0].attrs['data-selected'],'true');
assert.equal(cash.rows[2].attrs['data-selected'],'false');
assert.equal(shares.label.textContent,'FY 2025'); // Other cards remain independent.
cash.select.choose(1);
assert.deepEqual(cash.readouts.map(el=>el.textContent),['Not available','Not available']);
assert.equal(cash.points.filter(el=>el.attrs['data-selected']==='true').length,0);
assert.equal(cash.focus.attrs.transform,'translate(214,0)');
assert.equal(cash.chart.attrs['aria-label'],'Cash flow — Q2 2025');
shares.select.choose(0);
assert.equal(shares.readouts[0].textContent,'100M');
assert.equal(shares.chart.attrs['aria-label'],'Acțiuni — FY 2024');
console.log('Chart period focus, grouped values, missing periods and independent cards passed.');
