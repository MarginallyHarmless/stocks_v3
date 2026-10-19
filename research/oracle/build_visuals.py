"""Reproduce the dated Oracle visual supplement from inspected source rows."""
import json, calendar
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
B=lambda en,ro:dict(en=en,ro=ro)
periods=[]
for year in range(2027,2021,-1):
 for quarter in [4,3,2,1]:
  if year==2027 and quarter!=1: continue
  if year==2022 and quarter==1: continue
  month={1:8,2:11,3:2,4:5}[quarter]; y=year-1 if quarter<3 else year
  periods.append((f'Q{quarter} {year}',f'{y}-{month:02d}-{calendar.monthrange(y,month)[1]}'))
assert len(periods)==20
data={
'revenue':('income','Revenue',[19345,19184,17190,16058,14926,15903,14130,14059,13307,14287,13280,12941,12453,13836,12398,12275,11445,11840,10513,10360]),
'net_income':('income','Net Income to Common',[4679,4223,3699,6135,2927,3427,2936,3151,2929,3144,2401,2503,2420,3319,1896,1741,1548,3189,2319,-1247]),
'cfo':('cashflow','Operating Cash Flow',[23103,14620,7151,2066,8140,6157,5933,1304,7427,6081,5475,143,6974,5647,4275,849,6394,3985,3845,-3682]),
'fcf':('cashflow','Free Cash Flow',[-5396,-1873,-11484,-9967,-362,-2923,71,-2666,5124,3283,3801,-937,5660,3734,1647,-1586,4675,2562,2744,-4607]),
'diluted_shares':('income','Shares Outstanding (Diluted)',[3000,2915,2912,2922,2909,2871,2874,2869,2851,2834,2819,2817,2823,2796,2776,2746,2747,2742,2754,2694]),
'cash':('balance','Cash & Equivalents',[36369,31289,38455,19241,10445,10786,17406,10941,10616,10454,9481,8244,11613,9765,8219,6813,10448,21383,22682,17938]),
'investments':('balance','Short-Term Investments',[708,605,677,525,560,417,417,370,295,207,423,446,470,422,550,537,772,519,707,4900]),
'debt':('balance','Total Debt',[169143,167432,162165,131730,111622,108952,109176,99544,94192,94414,87980,88789,88941,90481,91811,90919,91577,75859,78413,78431]),
'sga':('income','Selling, General & Admin',[2187,2512,2441,2558,2439,2773,2509,2577,2394,2515,2419,2468,2419,2689,2552,2582,2588,2600,2339,2273]),
'rnd':('income','Research & Development',[2401,2614,2607,2561,2491,2654,2429,2471,2306,2226,2248,2226,2216,2226,2146,2158,2093,1965,1816,1754]),
'pe':('ratios','PE Ratio',[22.93,38.23,25.82,37.32,51.05,37.31,38.20,44.06,35.47,30.77,28.85,31.40,34.85,33.63,28.14,25.45,34.02,28.56,26.83,None]),
'ps':('ratios','PS Ratio',[5.98,9.64,6.52,9.44,10.76,8.09,8.33,9.32,7.24,6.08,5.85,6.17,6.41,5.73,4.91,4.86,4.47,4.52,4.85,5.99])}
urls={k:f'https://stockanalysis.com/stocks/orcl/financials/{p}/?p=quarterly' for k,p in [('income','income-statement'),('cashflow','cash-flow-statement'),('balance','balance-sheet'),('ratios','ratios')]}
urls.update(quote='https://www.wsj.com/market-data/stock/orcl',stats='https://stockanalysis.com/stocks/orcl/statistics/',forecast='https://stockanalysis.com/stocks/orcl/forecast/')
sources={k:dict(url=u,status='read',retrieved_at='2026-10-19',provider='WSJ' if k=='quote' else 'Stock Analysis / S&P Global',extraction_note='Observed source rows transcribed; financial amounts in USD millions. Historical rows reversed for display.',source_rows={}) for k,u in urls.items()}
series={}
for key,(src,row,values) in data.items():
 assert len(values)==20
 sources[src]['source_rows'][row]={p:('n/a' if v is None else str(v)) for (p,d),v in zip(periods,values)}
 ratio=key in ['pe','ps']
 series[key]=dict(unit='ratio' if ratio else ('shares' if key=='diluted_shares' else 'currency'),scale=1 if ratio else 1000000,basis='Provider period-end trailing GAAP' if ratio else 'Provider-standardized GAAP',period_kind='quarter',source_id=src,source_row=row,points=[dict(period=p,period_ending=d,value=v,state='unavailable' if v is None else 'observed') for (p,d),v in reversed(list(zip(periods,values)))])
 if key!='diluted_shares' and not ratio:series[key]['currency']='USD'
supp=dict(kind='visual_research_supplement',schema_version='1.0',ticker='ORCL',identity='CIK:0001341439|NYSE:ORCL:COMMON',retrieved_at='2026-10-19',currency='USD',sources=sources,series=series,
market=dict(overview_quote=dict(price=128.23,observed_at='2026-10-16T16:00:00-04:00',session='regular_close',source_id='quote'),stats_quote=dict(price=130.58,observed_at='2026-10-19T12:16:00-04:00',session='intraday',source_id='stats'),forecast_quote=dict(price=130.44,observed_at='2026-10-19T12:08:00-04:00',session='intraday',source_id='forecast'),range=dict(low=114.50,high=289.24,low_date=None,high_date=None,method='Provider intraday 52-week range on October 19; dates of extremes unavailable',source_id='quote'),ma200=dict(value=159.87,method='Provider 200-day average on October 19; adjustment convention not independently reproduced',source_id='stats')),
consensus=dict(targets=dict(low=110,mean=237.36,median=240,high=400,horizon_months=12,source_id='forecast'),ratings=dict(counts={'Strong Buy':28,'Buy':7,'Hold':7,'Sell':0,'Strong Sell':1},total=43,period='October 2026',source_id='forecast',score=68/43,score_scale='1 = Strong Buy; 5 = Strong Sell')),
basis_note=B('Twenty fiscal quarters, Q2 FY2022 through Q1 FY2027. Latest financial values reconciled to Oracle filings. Provider period-end P/E and P/S are historical observations, not prices on filing dates. One P/E observation is missing.','Douăzeci de trimestre fiscale, T2 FY2022–T1 FY2027. Valorile recente sunt reconciliate cu Oracle. P/E și P/S sunt observații istorice la sfârșit de perioadă, nu prețuri la depunere. O observație P/E lipsește.'),
caveats=[B('Debt chart includes recognized operating and finance leases: $169.1bn in August, versus $125.3bn borrowings excluding leases. Historical provider classification is not independently reconstructed. Future uncommenced leases are outside this chart.','Graficul datoriei include leasing operațional și financiar recunoscut: 169,1 mld. USD în august, față de împrumuturi de 125,3 mld. fără leasing. Clasificarea istorică nu este reconstruită independent. Leasingul viitor neînceput nu este inclus.'),B('CFO includes customer financing prepayments. FCF is CFO less cash capex, before finance-lease principal. Profits are attributable to common shareholders. These measures are not project-level cash returns.','CFO include avansuri de finanțare de la clienți. FCF este CFO minus investiții în numerar, înaintea principalului leasingului financiar. Profitul revine acționarilor ordinari. Măsurile nu reprezintă randamentele proiectelor.'),B('Reference close and intraday provider snapshots differ. Consensus targets are opinions with a 12-month horizon, not estimated intrinsic value. Historical multiple averages do not establish a fair price.','Închiderea de referință diferă de cotațiile intraday. Țintele consensului sunt opinii pe 12 luni, nu valoare intrinsecă estimată. Mediile multiplilor nu stabilesc un preț corect.')])
out=ROOT/'research/visuals/ORCL-2026-10-19.json'
out.write_text(json.dumps({'ORCL':supp},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ROOT/'research/visuals/manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m['ORCL-2026-10-19-v3']=dict(path='research/visuals/ORCL-2026-10-19.json',key='ORCL');p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Wrote visual supplement and manifest entry.')
