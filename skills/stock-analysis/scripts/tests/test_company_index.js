const assert=require('node:assert/strict');
const S=require('../../assets/company-index-state.js');
const base={id:'q4',period:'Q4 2026',kind:'results',date:'2026-12-10',confidence:'Estimated',timezone:'America/New_York'};
const state=(overrides,now)=>S.eventState({...base,...overrides},new Date(now));
assert.equal(state({},'2026-09-17T12:00:00Z').days,84);
assert.equal(state({},'2026-12-11T01:00:00Z').key,'today'); // Still release day in New York.
assert.equal(state({},'2026-12-11T05:01:00Z').key,'check');
assert.equal(state({confidence:'Confirmed'},'2026-12-11T05:01:00Z').key,'review');
assert.equal(state({date:null},'2026-12-11T05:01:00Z').key,'unknown');
assert.equal(state({date:'2026-12-17'},'2026-12-11T05:01:00Z').key,'upcoming');
assert.equal(state({confidence:'Confirmed',scheduled_at:'2026-12-10T16:05:00-05:00'},'2026-12-10T21:04:59Z').key,'today');
assert.equal(state({confidence:'Confirmed',scheduled_at:'2026-12-10T16:05:00-05:00'},'2026-12-10T21:05:00Z').key,'review');
assert.equal(state({publication_status:'published',published_at:'2026-12-09T21:00:00Z'},'2026-12-09T22:00:00Z').key,'review');
assert.equal(state({reviewed_report_id:'review-1',review_provisional:false},'2026-12-11T12:00:00Z').attention,false);
assert.equal(state({reviewed_report_id:'review-1',review_provisional:true},'2026-12-11T12:00:00Z').key,'provisional');
const c={earnings_events:[base,{...base,id:'q1',period:'Q1 2027',date:'2027-03-10'}]};
assert.equal(S.companyState(c,new Date('2026-12-12T12:00:00Z')).primary.event.period,'Q4 2026');
assert.equal(S.companyState(c,new Date('2026-12-12T12:00:00Z')).next.event.period,'Q1 2027');
c.earnings_events[0].reviewed_report_id='review-1';
assert.equal(S.companyState(c,new Date('2026-12-12T12:00:00Z')).attention,false);
assert.equal(S.days('2027-03-15',new Date('2027-03-13T17:00:00Z'),'America/New_York'),2); // DST does not change calendar-day count.
console.log('Company index: 15 date/state assertions passed.');
