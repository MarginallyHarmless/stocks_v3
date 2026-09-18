"""Stock Analysis v3: typed evidence and immutable earnings-review contract.

Standard library only. Validation checks internal consistency, not source truth.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from datetime import date, datetime
from urllib.parse import urlparse
from pathlib import Path

VERSION = "3.0"
COVERAGE = ("business", "moat", "growth", "profitability", "cash_flow", "balance_sheet",
            "capital_allocation", "dilution", "management", "valuation", "scenarios",
            "peers", "market_context", "risks")
OUTCOMES = {"Met", "Missed", "Mixed", "Not disclosed", "Not yet due", "Not comparable"}
KINDS = {"fact", "estimate", "assumption", "calculation", "judgment", "unavailable"}
UNITS = {"currency", "currency_per_share", "shares", "percent", "ratio", "count"}
BASES = {"GAAP", "IFRS", "adjusted", "market", "operating", "model"}


class Invalid(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Invalid(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise Invalid(f"Invalid ISO date: {value!r}") from None


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        need(result.tzinfo is not None, "Timestamps must include timezone")
        return result
    except (ValueError, TypeError, AttributeError):
        raise Invalid(f"Invalid timestamp: {value!r}") from None


def text_ok(value):
    return (isinstance(value, str) and bool(value.strip())) or (
        isinstance(value, dict) and bool(value) and set(value) <= {"en", "ro"}
        and all(isinstance(v, str) and v.strip() for v in value.values()))


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def identity(company):
    for key in ("issuer_id", "security_id", "name", "ticker", "exchange", "share_class"):
        need(isinstance(company.get(key), str) and company[key].strip(), f"company.{key} required")
    return company["issuer_id"] + "|" + company["security_id"]


def period(value):
    need(isinstance(value, dict), "Typed period required")
    need(value.get("kind") in {"instant", "duration"}, "period.kind must be instant or duration")
    end = parse_date(value.get("end"))
    need(text_ok(value.get("label")), "period.label required")
    need(isinstance(value.get("forecast"), bool), "period.forecast boolean required")
    if value["kind"] == "duration":
        need(parse_date(value.get("start")) <= end, "Period starts after its end")
    else:
        need("start" not in value, "Instant periods must not have a start")


def period_key(e):
    p = e["period"]
    return p["kind"], p.get("start"), p["end"], p["forecast"]


def dimensions(e):
    return e["unit"], e.get("currency"), e["basis"]


def number(e):
    return e["value"] * e.get("scale", 1)


def calculate(e, inputs):
    """Compute in base units; output value is expressed in its declared scale."""
    op = e.get("operation")
    need(bool(inputs), "Calculation requires inputs")
    need(all("value" in x for x in inputs), "Calculations need numeric inputs")
    vals = [number(x) for x in inputs]
    a = inputs[0]
    if op in {"sum", "difference", "ratio", "percent_ratio", "per_share"}:
        need(all(period_key(x) == period_key(a) for x in inputs), "Incompatible calculation periods")
        need(all(x["basis"] == a["basis"] for x in inputs), "Incompatible accounting bases")
        need(period_key(e) == period_key(a), "Calculation output period differs from its inputs")
        need(e["basis"] == a["basis"], "Calculation output basis differs from its inputs")
        if op == "per_share":
            need(len(inputs) == 2 and a["unit"] == "currency" and inputs[1]["unit"] == "shares",
                 "per_share requires currency and shares")
            need(e["unit"] == "currency_per_share" and e.get("currency") == a.get("currency"),
                 "Invalid per-share output unit/currency")
        else:
            need(all(dimensions(x) == dimensions(a) for x in inputs), "Incompatible input units/currencies")
        if op in {"sum", "difference"}:
            need(dimensions(e) == dimensions(a), "Incompatible output dimensions")
            need(op != "difference" or len(vals) == 2, "difference needs two inputs")
            answer = sum(vals) if op == "sum" else vals[0] - vals[1]
        else:
            need(len(vals) == 2 and vals[1] > 0, "Ratio denominator must be positive")
            if op != "per_share":
                need(e["unit"] == ("percent" if op == "percent_ratio" else "ratio"), "Invalid ratio unit")
            answer = vals[0] / vals[1] * (100 if op == "percent_ratio" else 1)
    elif op in {"ttm", "quarter_sum"}:
        need(all(dimensions(x) == dimensions(a) and x['definition'] == a['definition'] for x in inputs), "TTM inputs must measure the same item")
        need(all(x['period']['kind'] == 'duration' and not x['period']['forecast'] for x in inputs), "TTM needs actual flow periods")
        need(dimensions(e) == dimensions(a) and e['period']['kind'] == 'duration' and not e['period']['forecast'], "Invalid TTM output")
        if op == 'ttm':
            need(len(inputs) == 3, "TTM order is [full year, current YTD, prior YTD]")
            fy, cur, prev = [x['period'] for x in inputs]
            duration = lambda p: (parse_date(p['end'])-parse_date(p['start'])).days
            need(350 <= duration(fy) <= 371 and abs(duration(cur)-duration(prev)) <= 7, "Mismatched YTD/year durations")
            need(prev['start'] == fy['start'] and parse_date(prev['end']) < parse_date(fy['end']) < parse_date(cur['end']), "TTM periods must cover adjacent fiscal years")
            need((parse_date(cur['start'])-parse_date(fy['end'])).days == 1, "Current YTD must follow fiscal year")
            need(e['period']['end'] == cur['end'] and (parse_date(e['period']['start'])-parse_date(prev['end'])).days == 1, "TTM output boundaries wrong")
            answer = vals[0]+vals[1]-vals[2]
        else:
            need(len(inputs) == 4, "TTM quarter sum requires four quarters")
            need(all(75 <= (parse_date(x['period']['end'])-parse_date(x['period']['start'])).days <= 100 for x in inputs), "Expected fiscal quarters")
            need(all((parse_date(inputs[i+1]['period']['start'])-parse_date(inputs[i]['period']['end'])).days == 1 for i in range(3)), "Quarters must be ordered and contiguous")
            need(e['period']['start'] == a['period']['start'] and e['period']['end'] == inputs[-1]['period']['end'], "Wrong quarter-sum output boundaries")
            answer = sum(vals)
    elif op == 'average_balance':
        need(len(inputs) >= 2 and all(x['period']['kind'] == 'instant' and dimensions(x) == dimensions(a) and x['definition'] == a['definition'] for x in inputs), "Average balance requires comparable point-in-time balances")
        need(e['period']['kind'] == 'duration' and dimensions(e) == dimensions(a), "Average balance output must cover a duration")
        need((parse_date(e['period']['start'])-parse_date(a['period']['end'])).days in {0,1} and e['period']['end'] == inputs[-1]['period']['end'], "Average balance endpoints do not match")
        need(all(inputs[i]['period']['end'] < inputs[i+1]['period']['end'] for i in range(len(inputs)-1)), "Average balances must be ordered")
        answer = sum(vals)/len(vals)
    elif op in {'pe', 'net_debt_to_fcf', 'taxed_profit', 'product'}:
        need(len(inputs) == 2, "Operation needs two inputs")
        b = inputs[1]
        if op == 'pe':
            need(a['unit'] == b['unit'] == 'currency_per_share' and a.get('currency') == b.get('currency'), "P/E currency/per-share mismatch")
            need(a['basis'] == 'market' and a['period']['kind'] == 'instant' and b['period']['kind'] == 'duration' and vals[1] > 0, "P/E needs a quote and positive compatible EPS")
            need(e['unit'] == 'ratio' and e['basis'] == b['basis'] and period_key(e) == period_key(b), "P/E output must identify EPS period and basis")
            answer = vals[0]/vals[1]
        elif op == 'net_debt_to_fcf':
            need(a['unit'] == b['unit'] == 'currency' and dimensions(a)==dimensions(b) and vals[1]>0, "Net debt/FCF requires positive FCF and compatible currency/basis")
            need(a['period']['kind']=='instant' and b['period']['kind']=='duration' and a['period']['end']==b['period']['end'], "Net debt date must match TTM end")
            need(350 <= (parse_date(b['period']['end'])-parse_date(b['period']['start'])).days <= 371, "FCF must be TTM")
            need(e['unit']=='ratio' and e['basis']==a['basis'] and period_key(e)==period_key(b), "Invalid debt/FCF output")
            answer=vals[0]/vals[1]
        else:
            need(b['unit']=='ratio' and e['unit']==a['unit'] and e.get('currency')==a.get('currency'), "Product needs amount and dimensionless ratio")
            need(period_key(e)==period_key(a), "Product output period mismatch")
            need(text_ok(e.get('model_assumptions')) if b['kind']=='assumption' else period_key(a)==period_key(b), "Rate period mismatch or missing assumptions")
            need(e['basis']==('model' if b['kind']=='assumption' else a['basis']), "Product output basis mismatch")
            if op=='taxed_profit':
                need(a['unit']=='currency' and 0<=vals[1]<=1, "Taxed profit requires a valid effective rate")
                answer=vals[0]*(1-vals[1])
            else:
                answer=vals[0]*vals[1]
    elif op in {"growth", "cagr"}:
        need(len(inputs) == 2, "Growth input order is [new, old]")
        b = inputs[1]
        need(dimensions(a) == dimensions(b) and a["definition"] == b["definition"],
             "Growth requires compatible units, currency, basis and definition")
        need(a["period"]["kind"] == b["period"]["kind"], "Growth period kinds differ")
        if a["period"]["kind"] == "duration":
            days = lambda x: (parse_date(x["period"]["end"]) - parse_date(x["period"]["start"])).days
            need(abs(days(a) - days(b)) <= 7, "Growth periods have different lengths")
        years = (parse_date(a["period"]["end"]) - parse_date(b["period"]["end"])).days / 365.25
        need(years > 0 and vals[1] > 0, "Growth needs ordered periods and a positive base")
        need(e["unit"] == "percent" and e["basis"] == a["basis"] and period_key(e) == period_key(a),
             "Invalid growth output dimensions")
        if op == "cagr":
            declared = e.get("parameters", {}).get("years")
            need(finite(declared) and declared > 0 and abs(declared - years) <= .03,
                 "CAGR years must agree with dated endpoints")
            need(vals[0] >= 0, "CAGR cannot use a negative ending value")
            answer = ((vals[0] / vals[1]) ** (1 / declared) - 1) * 100
        else:
            answer = (vals[0] / vals[1] - 1) * 100
    elif op in {"equity_value", "valuation_multiple"}:
        need(len(inputs) == 2 and text_ok(e.get("model_assumptions")), "Valuation bridge assumptions required")
        b = inputs[1]
        need(e['basis'] == 'model', 'Valuation bridge must use model basis')
        need(a['period']['kind'] == 'instant' and not a['period']['forecast'], 'Valuation requires an observed point in time')
        need(period_key(e) == period_key(a), 'Valuation output date must match observed value')
        if op == 'equity_value':
            need(a['unit'] == 'currency_per_share' and a['basis'] == 'market', 'Equity value requires market price per share')
            need(b['unit'] == 'shares' and b['period']['kind'] == 'instant' and not b['period']['forecast'], 'Equity value requires observed shares')
            need(b['period']['end'] <= a['period']['end'], 'Share count cannot postdate quote')
            need(vals[0] > 0 and vals[1] > 0, 'Price and shares must be positive')
            need(e['unit'] == 'currency' and e.get('currency') == a.get('currency'), 'Equity value currency mismatch')
            answer = vals[0] * vals[1]
        else:
            need(a['unit'] == b['unit'] == 'currency' and a.get('currency') == b.get('currency'), 'Valuation multiple requires matching currencies')
            need(b['period']['kind'] == 'duration' and vals[1] > 0, 'Valuation multiple needs a positive duration denominator')
            need(e['unit'] == 'ratio' and not e.get('currency'), 'Valuation multiple must be dimensionless')
            answer = vals[0] / vals[1]
    elif op in {"discounted_value", "required_revenue", "eps_multiple"}:
        need(len(inputs) == 2 and text_ok(e.get("model_assumptions")), "Model assumptions required")
        need(e["basis"] == "model", "Model result basis must be model")
        need(inputs[1]["unit"] == "ratio" and inputs[1]["scale"] == 1, "Model rate/multiple must be a ratio")
        need(e.get("currency") == a.get("currency"), "Model currency mismatch")
        if op == "discounted_value":
            need(a["unit"] in {"currency", "currency_per_share"} and e["unit"] == a["unit"],
                 "Invalid present-value dimensions")
            years = e.get("parameters", {}).get("years")
            need(finite(years) and years > 0 and vals[1] > -1, "Invalid discount assumptions")
            elapsed = (parse_date(a["period"]["end"]) - parse_date(e["period"]["end"])).days / 365.25
            need(abs(years - elapsed) < .03 and a["period"]["forecast"] and not e["period"]["forecast"],
                 "Discount years/periods must identify a future value and present value")
            answer = vals[0] / (1 + vals[1]) ** years
        elif op == "required_revenue":
            need(a["unit"] == e["unit"] == "currency" and vals[1] > 0, "Invalid required-revenue inputs")
            need(e["period"]["kind"] == "duration", "Required revenue needs a financial duration")
            answer = vals[0] / vals[1]
        else:
            need(a["unit"] == e["unit"] == "currency_per_share" and vals[0] > 0 and vals[1] > 0,
                 "EPS multiple needs positive EPS and multiple")
            need(e["period"]["forecast"], "Scenario price must be labeled forecast")
            answer = vals[0] * vals[1]
    else:
        raise Invalid(f"Unsupported calculation operation {op!r}; do not invent a formula result")
    need(math.isfinite(answer), "Non-finite calculation")
    return answer / e["scale"]


def format_number(e, language="en"):
    """Never use author-supplied numeric display strings."""
    if "value" not in e:
        return e.get("state", "Unavailable")
    v = number(e)
    unit = e["unit"]
    if unit in {"currency", "shares", "count"}:
        divisor, suffix = next(((n, s) for n, s in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k"))
                                if abs(v) >= n), (1, ""))
        value = f"{v/divisor:,.{e.get('precision', 2)}f}".rstrip("0").rstrip(".") if e.get("precision",2) else f"{v/divisor:,.0f}"
        result = value + suffix
    else:
        result = f"{v:,.{e.get('precision', 2)}f}"
    if language == "ro":
        result = result.replace(",", "_").replace(".", ",").replace("_", ".")
    if unit in {"currency", "currency_per_share"}:
        result = e["currency"] + " " + result
    return result + ("%" if unit == "percent" else "×" if unit == "ratio" else "")


def refs(value, evidence, label, required=True):
    need(isinstance(value, list), f"{label}: evidence_refs must be a list")
    need(not required or bool(value), f"{label}: supporting evidence required")
    need(all(x in evidence for x in value), f"{label}: unknown evidence reference")
    if required:
        need(any(evidence[x]["kind"] != "unavailable" for x in value), f"{label}: only unavailable evidence")


def claim(c, evidence):
    need(c.get("type") in {"fact", "interpretation", "model", "limitation"}, "Invalid claim category")
    need(text_ok(c.get("text")), "Claim text required")
    refs(c.get("evidence_refs", []), evidence, "claim", c["type"] != "limitation")
    if c["type"] == "fact":
        need(all(evidence[x]["kind"] in {"fact", "calculation"} for x in c["evidence_refs"]),
             "Factual claims cannot cite estimates, judgments, or assumptions as facts")
        def actual(key, seen):
            need(key not in seen, 'Evidence cycle')
            e = evidence[key]
            need(e['kind'] in {'fact','calculation'}, 'Factual claim depends on a forecast or assumption')
            for child in e.get('inputs',[]):
                actual(child, seen | {key})
        for key in c['evidence_refs']:
            actual(key,set())


def event(ev, sources):
    need(ev.get("confidence") in {"Confirmed", "Estimated", "Not announced"}, "Invalid event confidence")
    for k in ("id", "period", "kind"):
        need(text_ok(ev.get(k)), f"event.{k} required")
    need(ev["kind"] in {"results", "call", "filing"}, "Keep event types separate")
    parse_date(ev.get("checked_at"))
    if ev["confidence"] == "Not announced":
        need(ev.get("date") is None, "Not announced must have null date")
        need(text_ok(ev.get("basis")), "Record where an unannounced date was checked")
    else:
        parse_date(ev.get("date"))
        need(ev.get("source_id") in sources, "Event date needs a source")
        if ev["confidence"] == "Confirmed":
            need(sources[ev["source_id"]]["authority"] == "issuer", "Confirmed date needs an issuer source")
        else:
            need(text_ok(ev.get("basis")), "Estimated date needs its provider or estimation basis")
    if ev.get("time"):
        need(bool(re.fullmatch(r"\d{2}:\d{2}", ev["time"])) and ev.get("timezone"), "Published time needs timezone")
    if ev.get("source_id"):
        need(ev["source_id"] in sources, "Unknown event source")


def watch(w, evidence):
    for key in ("id", "question", "why", "due_period"):
        need(text_ok(w.get(key)), f"watch.{key} required")
    need(isinstance(w.get("criterion_version"), int) and w["criterion_version"] > 0, "Positive criterion version required")
    refs(w.get("baseline_refs"), evidence, "watch baseline", required=False)
    need(bool(w.get("baseline_refs")), "Watch baseline needs an evidence record, including unavailable where necessary")
    c = w.get("criterion", {})
    need(c.get("kind") in {"numeric", "qualitative"}, "Criterion kind required")
    need(c.get("basis") in {"management_guidance", "external_estimate", "analytical_test"}, "Criterion basis required")
    need(text_ok(c.get("description")) and text_ok(c.get("rationale")), "Criterion and rationale required")
    if c["basis"] != "analytical_test":
        refs(c.get("evidence_refs", []), evidence, "criterion basis")
    if c["kind"] == "numeric":
        need(c.get("operator") in {"gt", "gte", "lt", "lte", "between"}, "Invalid threshold operator")
        need(finite(c.get("value")), "Numeric criterion value required")
        if c["operator"] == "between":
            need(finite(c.get("upper")) and c["upper"] >= c["value"], "Invalid threshold range")
        need(c.get("unit") in UNITS and c.get("accounting_basis") in BASES, "Criterion units/basis required")
        need(text_ok(c.get("definition")), "Criterion definition required")
        need(c.get("scale") in {1, 1000, 1000000, 1000000000, 1000000000000}, "Invalid criterion scale")
        if c["unit"] in {"currency", "currency_per_share"}:
            need(bool(re.fullmatch("[A-Z]{3}", c.get("currency", ""))), "Criterion currency required")
    impacts = w.get("impact", {})
    need(all(text_ok(impacts.get(k)) for k in ("favorable", "adverse", "mixed", "unresolved")), "Watch needs all four thesis implications")
    if w.get("due_date"):
        parse_date(w["due_date"])


def validate(data, baseline=None):
    need(data.get("schema_version") == VERSION, "Expected v3 schema; legacy data requires explicit migration")
    need(data.get("profile") == "strict", "New reports require profile=strict")
    need(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}", data.get("report_id", ""))), "Invalid report ID")
    need(data.get("mode") in {"full", "focused", "update"}, "Invalid research mode")
    need(isinstance(data.get("synthetic"), bool), "synthetic must be explicit")
    identity(data.get("company", {}))
    cutoff = timestamp(data.get("cutoff"))
    timestamp(data.get('prepared_at'))
    timestamp(data.get('freshness_checked_at'))
    need(data.get("languages") and set(data["languages"]) <= {"en", "ro"}, "Supported languages: en, ro")
    need(data.get("default_language") in data["languages"], "Default language unavailable")
    narrative_keys = {'text','evidence_gaps','question','why','description','rationale','caveat','nav_label',
                      'concept','example','trap','thesis_change','coverage_note','reason','thesis_impact',
                      'favorable','adverse','mixed','unresolved','comparability_reason','restatement_note'}
    def check_languages(value):
        if isinstance(value,list):
            for item in value: check_languages(item)
        elif isinstance(value,dict):
            for key,item in value.items():
                if key in narrative_keys and len(data['languages']) > 1:
                    need(isinstance(item,dict) and set(data['languages']) <= set(item) and all(text_ok(item[x]) for x in data['languages']), f'Missing authored translation for {key}')
                elif isinstance(item,dict) and set(item) <= {'en','ro'}:
                    need(set(data['languages']) <= set(item), f'Missing translation for {key}')
                if key not in {'sources','evidence','company'}:
                    check_languages(item)
    check_languages(data)
    sources = {}
    for s in data.get("sources", []):
        need(isinstance(s.get('id'),str) and bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',s['id'])) and s["id"] not in sources, "Unique safe source ID required")
        need(s.get("authority") in {"issuer", "regulator", "market", "secondary", "synthetic"}, "Invalid source authority")
        need(s.get("status") in {"read", "pending", "inaccessible"}, "Record actual source access status")
        need(text_ok(s.get("title")), "Source title required")
        need(urlparse(s.get("url", "")).scheme in {"http", "https"}, "Source needs HTTP(S) URL")
        timestamp(s.get("retrieved_at"))
        if s.get('published_at'):
            need(timestamp(s['published_at']) <= cutoff, 'Source was published after the information cutoff')
        else:
            need(text_ok(s.get('publication_note')), 'Missing source publication date needs an explanation')
        if not data["synthetic"]:
            need(s["authority"] != "synthetic", "Synthetic source in real research")
        sources[s["id"]] = s
    evidence = {}
    for e in data.get("evidence", []):
        need(isinstance(e.get('id'),str) and bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',e['id'])) and e["id"] not in evidence, "Unique safe evidence ID required")
        need(e.get("kind") in KINDS, "Invalid evidence kind")
        need(text_ok(e.get("label")) and isinstance(e.get("definition"), str) and e["definition"].strip(), "Evidence label/definition required")
        need("display" not in e and "raw_value" not in e, "Numeric display is generated; legacy display/raw_value is forbidden")
        if "value" in e:
            need(e["kind"] not in {"judgment", "unavailable"}, "Judgment/unavailable records cannot masquerade as numeric facts")
            need(finite(e["value"]), "Numeric value must be finite")
            need(e.get("unit") in UNITS and e.get("basis") in BASES, "Typed unit and basis required")
            need(e.get("scale") in {1, 1000, 1000000, 1000000000, 1000000000000}, "Invalid numeric scale")
            need(type(e.get("precision", 2)) is int and 0 <= e.get("precision", 2) <= 6, "Invalid precision")
            if e["unit"] in {"currency", "currency_per_share"}:
                need(bool(re.fullmatch("[A-Z]{3}", e.get("currency", ""))), "Currency code required")
            else:
                need(e.get("currency") is None, "Non-currency evidence cannot have currency")
            period(e.get("period"))
            if e['basis']=='market':
                need(timestamp(e.get('observed_at')) <= cutoff and text_ok(e.get('session')), 'Market value needs its actual observation time and session')
        else:
            need(text_ok(e.get("state")), "Non-numeric evidence needs an explicit state")
            if e["kind"] != "unavailable":
                period(e.get("period"))
        if e["kind"] in {"fact", "estimate"}:
            need(e.get("source_id") in sources, "Fact/estimate source required")
            need(sources[e["source_id"]]["status"] == "read", "Unread source cannot support evidence")
            extraction = e.get("extraction", {})
            need(text_ok(extraction.get("locator")) and text_ok(extraction.get("note")), "Source locator and extraction note required")
        if e["kind"] == "assumption":
            need(text_ok(e.get("rationale")), "Assumption rationale required")
        if e["kind"] == "fact" and e.get("period", {}).get("forecast"):
            need(False, "Future forecast must be estimate/assumption, not fact")
        evidence[e["id"]] = e
    visiting, visited = set(), set()
    def visit(key):
        need(key not in visiting, "Calculation dependency cycle")
        if key in visited:
            return
        visiting.add(key)
        e = evidence[key]
        if e["kind"] == "calculation":
            need("value" in e and isinstance(e.get("inputs"), list) and e["inputs"], "Calculation inputs/value required")
            need(all(x in evidence for x in e["inputs"]), "Unknown calculation input")
            for x in e["inputs"]:
                visit(x)
            expected = calculate(e, [evidence[x] for x in e["inputs"]])
            need(math.isclose(e["value"], expected, rel_tol=1e-8, abs_tol=1e-8), f"Calculation {key}: expected {expected}, got {e['value']}")
        if e["kind"] == "judgment":
            refs(e.get("evidence_refs", []), evidence, "judgment")
        visiting.remove(key)
        visited.add(key)
    for key in evidence:
        visit(key)
    need(bool(data.get("summary")), "Summary claims required")
    for c in data["summary"]:
        claim(c, evidence)
    for key in ("business_assessment", "price_assessment"):
        need(isinstance(data.get(key),dict), f'{key} requires a typed claim')
        claim(data[key],evidence)
    need(text_ok(data.get('evidence_gaps')), 'evidence_gaps required')
    sections = data.get("sections", [])
    need(bool(sections), "At least one question-led section required")
    need(data.get("presentation") in {None, "guided"}, "Unknown presentation")
    seen = set()
    for s in sections:
        need(s.get("id") and s["id"] not in seen, "Unique section ID required")
        seen.add(s["id"])
        need(text_ok(s.get("question")) and bool(s.get("claims")), "Section question/claims required")
        for c in s["claims"]:
            claim(c, evidence)
        refs(s.get("metrics", []), evidence, "section metrics", required=False)
        need(all("value" in evidence[x] for x in s.get("metrics", [])), "Metric must be numeric")
        need(text_ok(s.get("caveat")), "Visible section caveat required")
        if s.get('evidence_table'):
            table = s['evidence_table']
            need(text_ok(table.get('title')) and len(table.get('columns', [])) >= 2, 'Evidence table needs title and columns')
            need(all(text_ok(x) for x in table['columns']), 'Evidence table column label missing')
            for row in table.get('rows', []):
                need(text_ok(row.get('label')) and len(row.get('cells', [])) == len(table['columns']) - 1, 'Evidence table row width mismatch')
                for cell in row['cells']:
                    if 'evidence_ref' in cell:
                        refs([cell['evidence_ref']], evidence, 'Evidence table cell')
                    else:
                        claim(cell, evidence)
        guide = s.get("guide")
        if data.get("presentation") == "guided":
            need(isinstance(guide, dict), "Guided reports require a guide for every section")
        if guide is not None:
            need(isinstance(guide, dict), "Section guide must be an object")
            need(isinstance(guide.get("claims"), list) and 1 <= len(guide["claims"]) <= 3,
                 "Guide needs one to three short claims")
            for c in guide["claims"]:
                claim(c, evidence)
            need(isinstance(guide.get("why_it_matters"), dict), "Guide needs why_it_matters claim")
            claim(guide["why_it_matters"], evidence)
            metrics = guide.get("metrics", [])
            need(isinstance(metrics, list) and len(metrics) <= 3, "Guide allows at most three key metrics")
            metric_ids = []
            for metric in metrics:
                need(isinstance(metric, dict), "Guide metric must be an object")
                key = metric.get("evidence_ref")
                refs([key], evidence, "guide metric")
                need("value" in evidence[key], "Guide metric must be numeric")
                need("label" not in metric or text_ok(metric["label"]), "Guide metric label must be text")
                need(isinstance(metric.get("meaning"), dict), "Guide metric needs a meaning claim")
                claim(metric["meaning"], evidence)
                need(key in metric["meaning"].get("evidence_refs", []), "Metric meaning must reference its metric")
                metric_ids.append(key)
            need(len(metric_ids) == len(set(metric_ids)), "Duplicate guide metric")
        if s.get("lesson"):
            need(all(text_ok(s["lesson"].get(k)) for k in ("concept", "example", "trap")), "Lesson needs concept, hypothetical example, common misunderstanding")
    coverage = data.get("coverage", {})
    if data["mode"] == "full":
        need(set(coverage) == set(COVERAGE), "Full report requires 14 coverage items")
        need(any(s.get("lesson") for s in sections), "Full report needs beginner explanations")
        mapping = load(Path(__file__).resolve().parent.parent/'references/checklist.json')
        original = {c['id'] for s in mapping['sections'] for c in s['checks']} | {c['id'] for c in mapping['optional']}
        need(set(data.get('checklist',{})) == original, 'Preserve every original preparation/checklist/optional ID')
    for key, check in data.get('checklist',{}).items():
        need(check.get('status') in {'meets','mixed','does_not_meet','insufficient_evidence','not_applicable','not_researched'}, 'Invalid checklist assessment')
        need(check['status'] != 'not_researched' or key.startswith('O'), 'Only optional indicators may be not researched')
        need(text_ok(check.get('reason')), 'Checklist explanation required')
        refs(check.get('evidence_refs',[]), evidence, 'checklist', required=check['status'] in {'meets','mixed','does_not_meet'})
        need(all(x in seen for x in check.get('section_ids',[])), 'Checklist section not found')
    for key, v in coverage.items():
        need(key in COVERAGE and v.get("status") in {"covered", "unavailable", "inapplicable", "partial"}, "Invalid coverage record")
        need(text_ok(v.get("reason")), "Coverage reason required")
        need(all(x in seen for x in v.get("section_ids", [])), "Coverage references unknown section")
        if v["status"] == "covered":
            need(bool(v.get("section_ids")), "Covered item needs a section")
    need(isinstance(data.get("watchlist"), list), "watchlist required")
    if data["mode"] in {"full", "update"}:
        need(bool(data["watchlist"]), "Full/update report needs next watchlist")
    watch_ids = set()
    for w in data["watchlist"]:
        watch(w, evidence)
        need(w["id"] not in watch_ids, "Duplicate watch ID")
        watch_ids.add(w["id"])
    if data["watchlist"]:
        need(data.get("next_event", {}).get("kind") == "results", "Next event must identify the results release")
        event(data["next_event"], sources)
    for ev in data.get("related_events", []):
        event(ev, sources)
    if data["mode"] == "update":
        need(baseline is not None, "Update validation requires the actual saved baseline")
        validate_review(data, baseline, evidence, sources)
    else:
        need(not data.get("review"), "Earnings review belongs to update mode")
    return {"report_id": data["report_id"], "evidence": len(evidence), "sources": len(sources), "watch_items": len(watch_ids)}


def validate_review(data, baseline, evidence, sources):
    need(identity(data["company"]) == identity(baseline["company"]), "Baseline is another company/security")
    need(data.get("parent_report_id") == baseline["report_id"], "Parent does not match baseline")
    need(timestamp(data["cutoff"]) > timestamp(baseline["cutoff"]), "Update cutoff must follow baseline")
    review = data.get("review", {})
    need(review.get("baseline_sha256") == digest(baseline), "Baseline hash mismatch; original expectations changed")
    release = review.get("release", {})
    for k in ("id", "period"):
        need(text_ok(release.get(k)), f"Release {k} required")
    need(release.get("status") in {"published", "pending"}, "Verify release publication explicitly")
    need(text_ok(review.get("thesis_change")), "Explain what changes in the thesis")
    need(review.get("thesis_status") in {"strengthened", "weakened", "broadly_unchanged", "unresolved"}, "Invalid thesis status")
    need(isinstance(review.get("provisional"), bool) and text_ok(review.get("coverage_note")), "State release/filing/transcript coverage")
    if release["status"] == "published":
        sid = release.get("source_id")
        need(sid in sources and sources[sid]["authority"] in {"issuer", "regulator", "synthetic"} and sources[sid]["status"] == "read", "Published review needs read issuer/regulatory release")
        need(timestamp(release.get("published_at")) <= timestamp(data["cutoff"]), "Release after information cutoff")
    else:
        need(data['watchlist']==baseline['watchlist'], 'Pending review must retain the original watchlist unchanged')
    old = {w["id"]: w for w in baseline["watchlist"]}
    outcomes = review.get("outcomes", [])
    need(len(outcomes) == len(old) and {o.get("watch_id") for o in outcomes} == set(old), "Every original watch item requires exactly one outcome")
    for o in outcomes:
        w = old[o["watch_id"]]
        need(o.get("criterion_version") == w["criterion_version"] and o.get("criterion_sha256") == digest(w), "Original watch item or criterion changed")
        need(o.get("outcome") in OUTCOMES and text_ok(o.get("reason")) and text_ok(o.get("thesis_impact")), "Outcome, reason and impact required")
        if release["status"] == "pending":
            need(o["outcome"] == "Not yet due", "Unpublished release cannot resolve a watch item")
        refs(o.get("new_evidence_refs", []), evidence, "review outcome", required=o["outcome"] in {"Met", "Missed", "Mixed"})
        if o["outcome"] == "Not disclosed":
            need(bool(o.get("checked_source_ids")) and all(x in sources and sources[x]["status"] == "read" for x in o["checked_source_ids"]), "Not disclosed requires sources actually checked")
        if o["outcome"] == "Not comparable":
            need(text_ok(o.get("comparability_reason")), "Explain incompatible definitions/restatements")
        if o.get("restated_baseline_ref"):
            need(o["restated_baseline_ref"] in evidence and text_ok(o.get("restatement_note")), "Retain original and document restatement separately")
        if o["outcome"] in {"Met", "Missed", "Mixed"}:
            need(o.get("observed_period") == w["due_period"], "Later milestone cannot be resolved by an intervening quarter")
            if w.get("due_date"):
                need(parse_date(w["due_date"]) <= timestamp(data["cutoff"]).date(), "Milestone not yet due")
        c = w["criterion"]
        need(not (c['kind']=='numeric' and o['outcome']=='Mixed'), 'A single numeric threshold cannot have a Mixed outcome')
        if c["kind"] == "numeric" and o["outcome"] in {"Met", "Missed"}:
            eid = o.get("actual_ref")
            need(eid in o["new_evidence_refs"] and eid in evidence, "Numeric outcome requires actual_ref")
            actual = evidence[eid]
            need("value" in actual and actual["kind"] in {"fact", "calculation"}, "Outcome must use reported/calculated actuals")
            need(actual["unit"] == c["unit"] and actual.get("currency") == c.get("currency") and actual["basis"] == c["accounting_basis"] and actual["definition"] == c["definition"], "Outcome not comparable with saved criterion")
            need(actual["period"]["label"] == w["due_period"] and not actual["period"]["forecast"], "Actual belongs to a different/forecast period")
            v, threshold = number(actual), c["value"] * c["scale"]
            ok = {"gt": lambda: v > threshold, "gte": lambda: v >= threshold,
                  "lt": lambda: v < threshold, "lte": lambda: v <= threshold,
                  "between": lambda: threshold <= v <= c["upper"] * c["scale"]}[c["operator"]]()
            need(o["outcome"] == ("Met" if ok else "Missed"), "Outcome contradicts saved numeric criterion")
    for w in data["watchlist"]:
        if w["id"] in old and w != old[w["id"]]:
            need(w["criterion_version"] > old[w["id"]]["criterion_version"], "Changed future watch item needs a new version")
    need(isinstance(review.get("new_risks"), list), "Keep newly discovered risks separate")
    for c in review["new_risks"]:
        claim(c, evidence)


def recompute(data):
    """Recompute derived values without editing raw facts. Validation still follows."""
    data = copy.deepcopy(data)
    ev = {e["id"]: e for e in data["evidence"]}
    done, stack = set(), set()
    def visit(key):
        need(key not in stack, "Calculation dependency cycle")
        if key in done:
            return
        stack.add(key)
        e = ev[key]
        if e["kind"] == "calculation":
            for x in e["inputs"]:
                visit(x)
            e["value"] = calculate(e, [ev[x] for x in e["inputs"]])
        stack.remove(key)
        done.add(key)
    for key in ev:
        visit(key)
    return data
