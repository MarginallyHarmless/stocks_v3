/* Date-only releases use the issuer's timezone; never assume a publication time. */
const StockIndexState = (() => {
  const DAY=86400000;
  function today(now=new Date(),zone='UTC') {
    const parts=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
    const p=Object.fromEntries(parts.map(x=>[x.type,x.value]));
    return `${p.year}-${p.month}-${p.day}`;
  }
  function days(date,now,zone) { return Math.round((Date.parse(date+'T00:00:00Z')-Date.parse(today(now,zone)+'T00:00:00Z'))/DAY); }
  function eventState(e,now=new Date()) {
    if(e.reviewed_report_id) return {key:e.review_provisional?'provisional':'reviewed',attention:!!e.review_provisional};
    if(e.publication_status==='published' && Date.parse(e.published_at)<=+now) return {key:'review',attention:true,published:true};
    if(!e.date) return {key:'unknown',attention:false};
    const delta=days(e.date,now,e.timezone||'UTC');
    const past=e.scheduled_at ? Date.parse(e.scheduled_at)<=+now : delta<0;
    if(past) return {key:e.confidence==='Estimated'?'check':'review',attention:true,days:delta,published:false};
    return {key:delta===0?'today':'upcoming',attention:false,days:delta};
  }
  function companyState(c,now=new Date()) {
    const ev=c.earnings_events||[];
    const rows=ev.map(e=>({event:e,...eventState(e,now)}));
    const rank={review:0,check:1,provisional:2,today:3,upcoming:4,unknown:5,reviewed:6};
    rows.sort((a,b)=>rank[a.key]-rank[b.key] || (a.event.date||'9999').localeCompare(b.event.date||'9999'));
    const pending=rows.filter(r=>!r.event.reviewed_report_id);
    const next=pending.filter(r=>r.key==='upcoming'||r.key==='today').sort((a,b)=>(a.event.date||'').localeCompare(b.event.date||''))[0];
    return {primary:rows[0]||{key:'unknown',attention:false},next,attention:rows.some(r=>r.attention),rows};
  }
  return {today,days,eventState,companyState};
})();
if(typeof module!=='undefined') module.exports=StockIndexState;
