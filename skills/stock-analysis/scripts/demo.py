#!/usr/bin/env python3
"""Generate a bilingual fictional baseline and earnings follow-up for UI/contract QA."""
import argparse
import copy
from pathlib import Path
from archive import write_json, register
from model import COVERAGE, digest, load, recompute
from render import render


def bi(en,ro):
    return {"en":en,"ro":ro}


def period(label,start,end):
    return {"kind":"duration","label":label,"start":start,"end":end,"forecast":False}


def add_guides(data):
    """Authored teaching layer for this fictional packet only, never real research."""
    def c(en, ro, ids, kind='interpretation'):
        return {'type':kind, 'text':bi(en,ro), 'evidence_refs':ids}
    answers = {
        'business': c('Alder makes measuring equipment and earns money maintaining it. Buying its shares means owning a small part of that business.', 'Alder produce aparate de măsură și câștigă bani din întreținerea lor. Cumpărând acțiuni, deții o mică parte din această afacere.', ['business']),
        'growth': c('We do not have sales for the same quarter last year. One quarter of sales cannot tell us how quickly the business is growing.', 'Nu avem vânzările din același trimestru al anului trecut. Un singur trimestru nu arată cât de repede crește afacerea.', [], 'limitation'),
        'cash': c('Sales are money earned from customers. Cash left after running the business and buying equipment is a separate measure. In this example, that cash amount is positive.', 'Vânzările reprezintă sumele câștigate de la clienți. Numerarul rămas după funcționarea afacerii și cumpărarea echipamentelor este un indicator separat. În acest exemplu, suma rămasă este pozitivă.', ['fcf']),
        'ownership': c('The business is divided into more shares than a year ago. That means its gains are spread across more units of ownership.', 'Afacerea este împărțită în mai multe acțiuni decât acum un an. Câștigurile sale se împart astfel între mai multe unități de proprietate.', ['dilution']),
        'valuation': c('We cannot judge the share price because this packet contains no observed price or reliable profit forecast.', 'Nu putem evalua prețul acțiunii: pachetul nu include un preț observat sau o prognoză justificată de profit.', [], 'limitation')
    }
    implications = {
        'business': c('Equipment sales and maintenance provide different reasons for customers to pay. We still need to learn why they would choose Alder over a competitor.', 'Vânzarea și întreținerea echipamentelor oferă motive diferite pentru care clienții plătesc. Trebuie să aflăm de ce ar alege Alder în locul unui concurent.', ['business']),
        'growth': c('A growth claim needs a comparable earlier period. Without one, the pace of growth remains unknown.', 'O afirmație despre creștere necesită o perioadă anterioară comparabilă. Fără aceasta, ritmul rămâne necunoscut.', [], 'limitation'),
        'cash': c('Positive cash generation gives the company more room to fund its needs. It does not prove that all this cash can be paid to shareholders.', 'Numerarul generat oferă companiei mai multe resurse pentru nevoile sale. Nu dovedește că întreaga sumă poate fi plătită acționarilor.', ['fcf']),
        'ownership': c('Look for improvement per share, because owning one share does not give you the whole company’s growth.', 'Urmărește evoluția pe acțiune: o acțiune nu îți oferă întreaga creștere a companiei.', ['dilution']),
        'valuation': c('A business can improve while its shares are still too expensive. A price conclusion must wait for the missing evidence.', 'O afacere se poate îmbunătăți, iar acțiunile ei să fie totuși prea scumpe. Concluzia despre preț trebuie să aștepte datele lipsă.', [], 'limitation')
    }
    metrics = {
        'cash': [('fcf', bi('Cash left after equipment purchases','Numerar rămas după cumpărarea echipamentelor'), c('This is operating cash minus the equipment purchases defined in this example. Debt payments and other commitments can still use it.', 'Este numerarul din exploatare minus cumpărările de echipamente definite în exemplu. Datoriile și alte obligații pot necesita în continuare acești bani.', ['fcf']))],
        'ownership': [('dilution', bi('Increase in the share count','Creșterea numărului de acțiuni'), c('This percentage shows how much the average share count rose from a year earlier. More shares can reduce the benefit reaching each existing share.', 'Procentul arată cu cât a crescut numărul mediu de acțiuni față de anul anterior. Mai multe acțiuni pot reduce beneficiul care ajunge la fiecare acțiune existentă.', ['dilution']))]
    }
    data['presentation'] = 'guided'
    for section in data['sections']:
        key = section['id']
        section['guide'] = {'claims':[answers[key]], 'why_it_matters':implications[key],
            'metrics':[{'evidence_ref':eid,'label':label,'meaning':meaning} for eid,label,meaning in metrics.get(key,[])]}
    return data


def fixture():
    q1 = period('Q1 2026','2026-01-01','2026-03-31')
    prior = period('Q1 2025','2025-01-01','2025-03-31')
    ev = []
    def fact(key,label,value,unit='currency',definition=None,p=None):
        item = {"id":key,"kind":"fact","label":label,"value":value,"unit":unit,
                "scale":1000000 if unit in {'currency','shares'} else 1,"basis":"GAAP",
                "period":p or copy.deepcopy(q1),"definition":definition or key,"source_id":"demo-results",
                "extraction":{"locator":"Fictional Q1 packet / financial table","note":"Invented for workflow testing; not a disclosure."}}
        if unit=='currency': item['currency']='USD'
        ev.append(item)
    fact('revenue',bi('Revenue','Venituri'),100,definition='Consolidated revenue')
    fact('cfo',bi('Operating cash flow','Numerar din exploatare'),18,definition='Net cash from operating activities')
    fact('capex',bi('Cash investment','Investiții în numerar'),6,definition='Cash purchases of property and equipment')
    fact('shares-old',bi('Prior-year diluted shares','Acțiuni diluate, anul anterior'),100,'shares','Diluted weighted-average shares',prior)
    fact('shares',bi('Diluted shares','Acțiuni diluate'),106,'shares','Diluted weighted-average shares')
    fact('op-margin',bi('Operating margin','Marjă operațională'),12,'percent','GAAP operating income / revenue × 100')
    ev.append({"id":"business","kind":"fact","label":bi('Business model','Modelul de afaceri'),
               "state":bi('Precision instruments and maintenance contracts.','Instrumente de precizie și contracte de mentenanță.'),
               "definition":"Illustrative business description","period":q1,"source_id":"demo-results",
               "extraction":{"locator":"Fictional packet / overview","note":"Entirely fictional business."}})
    ev.append({"id":"contracts","kind":"fact","label":bi('Contract conversion baseline','Conversia contractelor'),
               "state":bi('No comparable conversion percentage disclosed.','Nu este publicat un procent comparabil de conversie.'),
               "definition":"Backlog converted into recognized revenue","period":q1,"source_id":"demo-results",
               "extraction":{"locator":"Fictional packet / backlog note","note":"Fictional evidence states that this metric was not supplied."}})
    for key,op,inputs,unit,definition in [
        ('fcf','difference',['cfo','capex'],'currency','Operating cash flow less cash property/equipment purchases'),
        ('fcf-margin','percent_ratio',['fcf','revenue'],'percent','Defined free cash flow / revenue × 100'),
        ('dilution','growth',['shares','shares-old'],'percent','YoY change in diluted weighted-average shares')]:
        item={"id":key,"kind":"calculation","label":bi({'fcf':'Free cash flow','fcf-margin':'FCF margin','dilution':'Share-count growth'}[key],{'fcf':'Flux de numerar liber','fcf-margin':'Marja FCF','dilution':'Creșterea numărului de acțiuni'}[key]),"value":0,"unit":unit,"scale":1000000 if unit=='currency' else 1,"basis":"GAAP","period":q1,"definition":definition,"operation":op,"inputs":inputs}
        if unit=='currency': item['currency']='USD'
        ev.append(item)
    def claim(text,refs,kind='interpretation'):
        return {"type":kind,"text":text,"evidence_refs":refs}
    sections=[
        {"id":"business","nav_label":bi('The business','Afacerea'),"question":bi('What does the business do?','Cum câștigă bani compania?'),
         "claims":[claim(bi('Alder sells precision instruments and earns recurring service revenue. This example does not establish a durable competitive advantage.','Alder vinde instrumente de precizie și obține venituri recurente din service. Acest exemplu nu dovedește un avantaj competitiv durabil.'),['business'])],"metrics":[],
         "caveat":bi('Customer retention, segment mix and competitor evidence are missing from this fictional packet.','Lipsesc date despre retenția clienților, segmente și concurenți.'),
         "lesson":{"concept":bi('A competitive advantage is a specific reason customers stay despite credible alternatives.','Un avantaj competitiv este un motiv concret pentru care clienții rămân, deși au alternative credibile.'),"example":bi('A machine integrated into a production line may be expensive to replace, even if a competing machine is cheaper.','Un aparat integrat într-o linie de producție poate fi scump de înlocuit, chiar dacă un model concurent costă mai puțin.'),"trap":bi('A high margin alone does not prove a durable advantage.','O marjă mare nu dovedește singură un avantaj durabil.')}},
        {"id":"cash","nav_label":bi('Profit and cash','Profit și numerar'),"question":bi('Are sales turning into cash?','Se transformă vânzările în numerar?'),
         "claims":[claim(bi('The business retains 12 cents of defined free cash flow per dollar of revenue after cash investment in equipment.','Afacerea păstrează 12 cenți de flux de numerar liber definit pentru fiecare dolar de venituri, după investițiile în echipamente.'),['fcf-margin'])],"metrics":['revenue','fcf','fcf-margin'],
         "caveat":bi('FCF is not automatically available for distribution: financing obligations and future commitments still matter.','FCF nu poate fi distribuit automat: obligațiile de finanțare și angajamentele viitoare contează.'),
         "lesson":{"concept":bi('Free cash flow here means operating cash flow minus cash purchases of property and equipment. It helps test whether accounting growth generates cash.','Fluxul de numerar liber înseamnă aici numerarul din exploatare minus achizițiile de imobilizări. Arată dacă dezvoltarea contabilă produce numerar.'),"example":bi('If operations produce 20 and equipment costs 7, defined FCF is 13. That is a teaching example, not Alder’s result.','Dacă operațiunile produc 20 și echipamentele costă 7, FCF definit este 13. Este un exemplu, nu rezultatul Alder.'),"trap":bi('Profit and cash flow answer different questions. Neither is automatically more truthful.','Profitul și fluxul de numerar răspund unor întrebări diferite. Niciunul nu este automat mai adevărat.')}},
        {"id":"ownership","nav_label":bi('Your share','Partea ta'),"question":bi('Is growth reaching each share?','Ajunge creșterea și la fiecare acțiune?'),
         "claims":[claim(bi('Diluted weighted-average shares rose 6% year over year. Company growth must outpace that increase for the same growth to reach each share.','Numărul mediu ponderat de acțiuni diluate a crescut cu 6% anual. Creșterea companiei trebuie să depășească acest ritm pentru a se reflecta integral pe acțiune.'),['dilution'])],"metrics":['dilution','op-margin'],
         "caveat":bi('Weighted-average diluted shares measure the earnings denominator; they are not an exact point-in-time ownership count.','Acțiunile diluate medii reprezintă numitorul profitului pe acțiune, nu numărul exact de acțiuni la o anumită dată.'),
         "lesson":{"concept":bi('New shares spread the business across more units. Compare company-wide growth with growth per share.','Acțiunile noi împart afacerea în mai multe unități. Compară creșterea totală cu cea pe acțiune.'),"example":bi('If 100 shares become 110, an unchanged holding falls to 100/110 of its original percentage ownership, a 9.09% relative reduction.','Dacă 100 de acțiuni devin 110, o deținere neschimbată ajunge la 100/110 din procentul inițial: o reducere relativă de 9,09%.'),"trap":bi('Buyback spending can offset employee issuance without reducing the net share count.','Răscumpărările pot compensa emisiunile pentru angajați fără să reducă numărul net de acțiuni.')}},
        {"id":"valuation","nav_label":bi('Price and uncertainty','Preț și incertitudine'),"question":bi('What would justify the price?','Ce ar justifica prețul?'),
         "claims":[claim(bi('No observed market price or defensible earnings forecast is supplied. A valuation conclusion and numerical scenarios remain unavailable.','Nu există un preț de piață observat sau o prognoză justificată de profit. Concluzia de evaluare și scenariile numerice rămân indisponibile.'),[],'limitation')],"metrics":[],
         "caveat":bi('Improving operations alone would not show that a stock is attractively priced.','Îmbunătățirea operațiunilor nu ar demonstra singură că prețul acțiunii este atractiv.')}]
    sections.insert(1, {'id':'growth','nav_label':bi('Growth','Creștere'),
        'question':bi('Do we know how fast sales are growing?','Știm cât de repede cresc vânzările?'),
        'claims':[claim(bi('The packet lacks same-quarter prior-year revenue. A year-over-year growth calculation is unavailable.','Pachetul nu include veniturile din același trimestru al anului anterior. Nu se poate calcula creșterea anuală.'),[],'limitation')],
        'metrics':['revenue'],'caveat':bi('Do not treat missing growth data as evidence that sales are falling.','Datele lipsă despre creștere nu dovedesc că vânzările scad.')})
    sections[3]['question'] = bi('What could reduce the benefit to each share?','Ce ar putea reduce beneficiul pe acțiune?')
    impact={"favorable":bi('Supports the case for the business; we must still consider the price.','Susține perspectivele afacerii; trebuie să luăm în calcul și prețul.'),"adverse":bi('Makes this part of the investment case less convincing.','Face această parte a argumentului investițional mai puțin convingătoare.'),"mixed":bi('Separate the improving and deteriorating components.','Separă componentele care se îmbunătățesc de cele care se deteriorează.'),"unresolved":bi('Keep the uncertainty open; do not score missing evidence as failure.','Păstrează incertitudinea; datele lipsă nu înseamnă eșec.')}
    watches=[]
    for key,question,base,operator,value,definition in [
        ('dilution',bi('Is dilution slowing?','Încetinește diluția?'),'dilution','lt',5,'YoY change in diluted weighted-average shares'),
        ('margin',bi('Is operating profitability recovering?','Își revine profitabilitatea operațională?'),'op-margin','gte',13,'GAAP operating income / revenue × 100')]:
        desc = bi('Below 5% YoY share-count growth in Q2 2026.','Creștere anuală a numărului de acțiuni sub 5% în T2 2026.') if key=='dilution' else bi('At least 13% GAAP operating margin in Q2 2026.','Marjă operațională GAAP de cel puțin 13% în T2 2026.')
        watches.append({"id":key,"criterion_version":1,"question":question,"why":bi('Check whether reported growth improves the economics of each share.','Verifică dacă dezvoltarea raportată îmbunătățește situația fiecărei acțiuni.'),"baseline_refs":[base],"due_period":"Q2 2026","criterion":{"kind":"numeric","basis":"analytical_test","description":desc,"rationale":bi('Invented threshold for demonstrating a saved test, not a universal rule.','Prag inventat pentru a demonstra un criteriu salvat, nu o regulă universală.'),"operator":operator,"value":value,"unit":"percent","scale":1,"accounting_basis":"GAAP","definition":definition},"impact":copy.deepcopy(impact)})
    watches.append({"id":"contracts","criterion_version":1,"question":bi('Are contracts becoming revenue?','Se transformă contractele în venituri?'),"why":bi('Backlog alone does not pay for the investment plan.','Portofoliul de comenzi nu finanțează singur planul de investiții.'),"baseline_refs":['contracts'],"due_period":"Q2 2026","criterion":{"kind":"qualitative","basis":"analytical_test","description":bi('Look for a disclosed reconciliation from opening backlog to recognized revenue.','Caută o reconciliere publicată între comenzile inițiale și veniturile recunoscute.'),"rationale":bi('A reconciliation would distinguish signed business from delivered business.','O reconciliere ar distinge contractele semnate de livrările efective.')},"impact":copy.deepcopy(impact)})
    d={"schema_version":"3.0","profile":"strict","mode":"full","report_id":"alder-2026-q1-demo","parent_report_id":None,"synthetic":True,
       "company":{"issuer_id":"fictional:alder","security_id":"fictional:alder-common","name":"Alder Instruments","ticker":"ALDR-DEMO","exchange":"Fictional exchange","share_class":"Common","reporting_currency":"USD","trading_currency":"USD","fiscal_year_end":"12-31"},
       "cutoff":"2026-05-10T12:00:00Z","prepared_at":"2026-05-10T12:00:00Z","freshness_checked_at":"2026-05-10T12:00:00Z","languages":["en","ro"],"default_language":"en",
       "sources":[{"id":"demo-results","authority":"synthetic","title":"Fictional financial packet","url":"https://example.com/fictional-alder-q1","status":"read","retrieved_at":"2026-05-10T10:00:00Z","published_at":"2026-05-08T12:00:00Z"}],"evidence":ev,
       "summary":[claim(bi('Alder has cash left after equipment purchases. Next, check whether it keeps more of each sale as operating profit while the number of shares grows more slowly.','Alder are numerar rămas după cumpărarea echipamentelor. Verificăm dacă păstrează mai mult din fiecare vânzare ca profit operațional, în timp ce numărul de acțiuni crește mai lent.'),['fcf','dilution','op-margin'])],
       "business_assessment":claim(bi('Cash remains after equipment purchases, but we do not know whether this can last.','Rămâne numerar după cumpărarea echipamentelor, dar nu știm dacă situația se poate menține.'),['fcf','business']),
       "price_assessment":claim(bi('Unresolved — no observed price or forecast in this example.','Neclar — exemplul nu include un preț observat sau o prognoză.'),[],'limitation'),
       "evidence_gaps":bi('Partial illustrative packet: no balance-sheet, peer, market-price or audited history research.','Pachet demonstrativ parțial: fără documentare de bilanț, concurenți, preț de piață sau istoric auditat.'),
       "sections":sections,"coverage":{k:{"status":"partial","reason":bi('Limited fictional evidence; not a completed company analysis.','Date fictive limitate; nu este o analiză completă.'),"section_ids":[sections[0]['id']]} for k in COVERAGE},
       "watchlist":watches,"next_event":{"id":"alder-q2-results","kind":"results","period":"Q2 2026","confidence":"Estimated","date":"2026-08-05","checked_at":"2026-05-10","source_id":"demo-results","basis":bi('Fictional schedule for demonstration; not an issuer announcement.','Calendar fictiv pentru demonstrație, nu anunț al unui emitent.')},"related_events":[]}
    mapping=load(Path(__file__).resolve().parent.parent/'references/checklist.json')
    ids=[c['id'] for s in mapping['sections'] for c in s['checks']]+[c['id'] for c in mapping['optional']]
    d['checklist']={key:{"status":"not_researched" if key.startswith('O') else "insufficient_evidence","reason":bi('Not supplied in the fictional packet.','Nu este inclus în pachetul fictiv.'),"evidence_refs":[],"section_ids":[]} for key in ids}
    return recompute(add_guides(d))


def update_fixture(base):
    d=copy.deepcopy(base)
    d.update(mode='update',report_id='alder-2026-q2-demo',parent_report_id=base['report_id'],cutoff='2026-08-06T12:00:00Z',prepared_at='2026-08-06T12:00:00Z',freshness_checked_at='2026-08-06T12:00:00Z')
    d['sources'][0].update(url='https://example.com/fictional-alder-q2',published_at='2026-08-05T12:00:00Z',retrieved_at='2026-08-06T10:00:00Z')
    for e in d['evidence']:
        e['period']=period('Q2 2025','2025-04-01','2025-06-30') if e['id']=='shares-old' else period('Q2 2026','2026-04-01','2026-06-30')
        if e['id'] in {'revenue','cfo','capex','shares','op-margin'}:
            e['value']={'revenue':120,'cfo':22,'capex':7,'shares':104,'op-margin':11}[e['id']]
        if 'extraction' in e:
            e['extraction']['locator']='Fictional Q2 packet'
    for w in d['watchlist']:
        w['criterion_version']+=1
        w['due_period']='Q3 2026'
        for lang in ['en','ro']:
            w['criterion']['description'][lang]=w['criterion']['description'][lang].replace('Q2','Q3').replace('T2','T3')
    d['next_event']={"id":"alder-q3-results","kind":"results","period":"Q3 2026","confidence":"Not announced","date":None,"checked_at":"2026-08-06","basis":bi('No future schedule supplied in this fictional packet.','Pachetul fictiv nu include calendarul următor.')}
    d['summary'][0]['text']=bi('The share count grew more slowly, but the company kept less of each sale as operating profit than our saved test required. Results are mixed.','Numărul de acțiuni a crescut mai lent, dar compania a păstrat mai puțin din fiecare vânzare ca profit operațional decât cerea criteriul salvat. Rezultatele sunt mixte.')
    sections = {s['id']:s for s in d['sections']}
    sections['cash']['claims'][0]['text']=bi('Defined free cash flow reached 12.5% of revenue. Cash generation remained positive.','Fluxul de numerar liber definit a ajuns la 12,5% din venituri. Generarea de numerar a rămas pozitivă.')
    sections['ownership']['claims'][0]['text']=bi('Share-count growth slowed to 4%, while operating margin fell to 11%.','Creșterea numărului de acțiuni a încetinit la 4%, iar marja operațională a scăzut la 11%.')
    outcomes=[]
    for w, status, actual, reason in zip(base['watchlist'],['Met','Missed','Not disclosed'],['dilution','op-margin',None],[bi('4% is below the original 5% threshold.','4% este sub pragul original de 5%.'),bi('11% is below the original 13% threshold.','11% este sub pragul original de 13%.'),bi('The release does not provide a comparable backlog reconciliation.','Comunicatul nu oferă o reconciliere comparabilă a comenzilor.')]):
        o={"watch_id":w['id'],"criterion_version":w['criterion_version'],"criterion_sha256":digest(w),"outcome":status,"observed_period":"Q2 2026","new_evidence_refs":[actual] if actual else [],"reason":reason,"thesis_impact":bi('Assess this component without changing the original criterion.','Evaluează această componentă fără a modifica criteriul original.')}
        if actual: o['actual_ref']=actual
        else: o['checked_source_ids']=['demo-results']
        outcomes.append(o)
    d['review']={"baseline_sha256":digest(base),"release":{"id":"fictional-release-q2-2026","period":"Q2 2026","status":"published","published_at":"2026-08-05T12:00:00Z","source_id":"demo-results"},"provisional":True,"coverage_note":bi('Release-only demonstration. No regulatory filing or transcript was supplied.','Demonstrație bazată numai pe comunicat. Nu a fost inclus un raport de reglementare sau o transcriere.'),"thesis_status":"unresolved","thesis_change":bi('Lower dilution supports the per-share case, but weaker operating profitability offsets it. Contract conversion remains unresolved.','Diluția mai mică susține evoluția pe acțiune, dar profitabilitatea mai slabă o compensează. Conversia comenzilor rămâne neclară.'),"outcomes":outcomes,"new_risks":[]}
    return recompute(d)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    root=Path(args.out); root.mkdir(parents=True,exist_ok=True)
    base=fixture(); new=update_fixture(base)
    write_json(root/'baseline.json',base); write_json(root/'update.json',new)
    (root/'stock-analysis-demo.html').write_text(render(base),encoding='utf-8')
    (root/'stock-analysis-follow-up-demo.html').write_text(render(new,base),encoding='utf-8')
    archive=root/'fictional-company-archive.json'
    register(archive,base);register(archive,new)
    print(root)


if __name__=='__main__':main()
