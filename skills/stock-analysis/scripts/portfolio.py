"""Validate unlevered portfolio snapshots and calculate authored comparisons.

No market-data fetching, profiling score, optimization, trading or persistence.
All weights/returns are fractions. All values already share one base currency.
"""
import argparse
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys


class PortfolioError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PortfolioError(message)


def number(value, label, low=None, high=None):
    require(isinstance(value, (int, float, Decimal, str)) and not isinstance(value, bool),
            f"{label}: expected a finite number")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise PortfolioError(f"{label}: invalid number") from exc
    require(result.is_finite(), f"{label}: expected a finite number")
    require(low is None or result >= low, f"{label}: below allowed minimum")
    require(high is None or result <= high, f"{label}: above allowed maximum")
    return result


def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: required text")
    return value


def weights(values, ids, label):
    require(isinstance(values, dict) and set(values) == ids,
            f"{label}: explicitly include every position, using zero for exclusions")
    out = {key: number(value, f"{label}.{key}", 0, 1) for key, value in values.items()}
    require(abs(sum(out.values()) - 1) <= Decimal('0.000000001'), f"{label}: must sum to 1")
    return out


def validate(data):
    require(isinstance(data, dict), "snapshot: expected an object")
    require(set(data) <= {'schema_version', 'kind', 'synthetic', 'scope', 'base_currency',
                         'as_of', 'positions', 'total_investable_value_base', 'target_weights',
                         'target_basis', 'scenarios', 'policy', 'contribution'},
            'snapshot: unsupported field; keep profile and other models separately')
    require(data.get('schema_version') == '1.0', "schema_version: expected 1.0")
    require(data.get('kind') == 'portfolio_snapshot', "kind: expected portfolio_snapshot")
    require(isinstance(data.get('synthetic'), bool), "synthetic: required boolean")
    require(data.get('scope') in ('whole_portfolio', 'stock_sleeve'), "scope: invalid")
    require(isinstance(data.get('base_currency'), str) and
            re.fullmatch('[A-Z]{3}', data['base_currency']), "base_currency: expected three uppercase letters")
    stamp = nonempty(data.get('as_of'), 'as_of')
    try:
        if len(stamp) == 10:
            date.fromisoformat(stamp)
        else:
            parsed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
            require(parsed.utcoffset() is not None, 'as_of: timestamp must include timezone')
    except ValueError as exc:
        raise PortfolioError('as_of: expected an ISO date or timezone-aware timestamp') from exc
    positions = data.get('positions')
    require(isinstance(positions, list) and bool(positions), 'positions: nonempty list required')
    ids, amounts = set(), {}
    themes, issuers = set(), set()
    for pos in positions:
        require(isinstance(pos, dict), 'position: expected an object')
        require(set(pos) <= {'security_id', 'issuer_id', 'label', 'asset_type', 'value_base',
                             'value_source', 'themes', 'theme_source'}, 'position: unsupported field')
        sid = nonempty(pos.get('security_id'), 'security_id')
        require(sid not in ids, f'duplicate security_id: {sid}; aggregate accounts first')
        ids.add(sid)
        require(pos.get('asset_type') in ('company', 'fund', 'cash', 'bond'), f'{sid}: unsupported asset_type')
        nonempty(pos.get('label'), f'{sid}.label')
        nonempty(pos.get('value_source'), f'{sid}.value_source')
        amounts[sid] = number(pos.get('value_base'), f'{sid}.value_base', 0)
        if pos['asset_type'] in ('company', 'bond'):
            issuers.add(nonempty(pos.get('issuer_id'), f'{sid}.issuer_id'))
        tags = pos.get('themes')
        require(tags is None or isinstance(tags, list), f'{sid}.themes: expected list or null')
        if tags is not None:
            for tag in tags:
                themes.add(nonempty(tag, f'{sid}.themes'))
            require(len(set(tags)) == len(tags), f'{sid}.themes: duplicate tag')
            nonempty(pos.get('theme_source'), f'{sid}.theme_source')
    total = sum(amounts.values())
    require(total > 0, 'portfolio value must be positive')
    denominator = data.get('total_investable_value_base')
    if denominator is not None:
        denominator = number(denominator, 'total_investable_value_base', total)
        if data['scope'] == 'whole_portfolio':
            require(denominator == total, 'whole_portfolio denominator must equal position values')
    target = None
    if 'target_weights' in data:
        target = weights(data['target_weights'], ids, 'target_weights')
        nonempty(data.get('target_basis'), 'target_basis')
    scenarios = data.get('scenarios', [])
    require(isinstance(scenarios, list), 'scenarios: expected list')
    scenario_ids = set()
    for scenario in scenarios:
        require(isinstance(scenario, dict), 'scenario: expected an object')
        require(set(scenario) <= {'id', 'label', 'horizon', 'assumptions', 'returns'},
                'scenario: unsupported field')
        sid = nonempty(scenario.get('id'), 'scenario.id')
        require(sid not in scenario_ids, 'duplicate scenario id')
        scenario_ids.add(sid)
        for key in ('label', 'horizon', 'assumptions'):
            nonempty(scenario.get(key), f'{sid}.{key}')
        returns = scenario.get('returns')
        require(isinstance(returns, dict) and set(returns) == ids,
                f'{sid}.returns: explicitly include all positions, including cash')
        for key, value in returns.items():
            number(value, f'{sid}.returns.{key}', -1)
    policy = data.get('policy', {})
    require(isinstance(policy, dict), 'policy: expected object')
    require(set(policy) <= {'max_issuer_weight', 'theme_caps', 'basis'}, 'policy: unsupported constraint')
    if policy:
        nonempty(policy.get('basis'), 'policy.basis')
    if 'max_issuer_weight' in policy:
        number(policy['max_issuer_weight'], 'max_issuer_weight', 0, 1)
    caps = policy.get('theme_caps', {})
    require(isinstance(caps, dict), 'theme_caps: expected object')
    for key, value in caps.items():
        require(key in themes, f'theme cap has no observed tag: {key}')
        number(value, f'theme_caps.{key}', 0, 1)
    contribution = data.get('contribution')
    if contribution is not None:
        require(isinstance(contribution, dict), 'contribution: expected object')
        require(set(contribution) <= {'amount_base', 'allocation_weights'},
                'contribution: unsupported field')
        number(contribution.get('amount_base'), 'contribution.amount_base', 0)
        weights(contribution.get('allocation_weights'), ids, 'contribution.allocation_weights')
    return amounts, total, denominator, target


def calculate(data):
    amounts, total, denominator, target = validate(data)
    current = {sid: amount / total for sid, amount in amounts.items()}
    overall = total if data['scope'] == 'whole_portfolio' else denominator
    scale = total / overall if overall is not None else None
    policy = data.get('policy', {})

    def exposure(vector):
        issuer, theme = defaultdict(Decimal), defaultdict(Decimal)
        unknown = Decimal(0)
        for pos in data['positions']:
            weight = vector[pos['security_id']]
            if pos['asset_type'] in ('company', 'bond'):
                issuer[pos['issuer_id']] += weight
            if pos.get('themes') is None:
                unknown += weight
            else:
                for tag in pos['themes']:
                    theme[tag] += weight
        breaches = []
        cap = policy.get('max_issuer_weight')
        if cap is not None:
            cap = number(cap, 'max_issuer_weight')
            breaches += [{'type': 'issuer', 'id': key, 'weight': val, 'cap': cap}
                         for key, val in sorted(issuer.items()) if val > cap]
        for key, cap_value in sorted(policy.get('theme_caps', {}).items()):
            cap = number(cap_value, 'theme cap')
            if theme[key] > cap:
                breaches.append({'type': 'theme', 'id': key, 'weight': theme[key], 'cap': cap})
        return {'direct_issuer_weights': dict(sorted(issuer.items())),
                'tagged_theme_weights': dict(sorted(theme.items())),
                'unclassified_theme_weight': unknown, 'breaches': breaches,
                'policy_status': ('not_assessed' if not policy else 'breach_found' if breaches
                                  else 'incomplete_theme_coverage' if policy.get('theme_caps') and unknown
                                  else 'no_direct_breach_found')}

    result = {'schema_version': '1.0', 'kind': 'portfolio_calculations',
              'synthetic': data['synthetic'], 'as_of': data['as_of'],
              'scope': data['scope'], 'base_currency': data['base_currency'],
              'portfolio_value_base': total, 'total_investable_value_base': overall,
              'suitability': 'not_assessed_by_calculator', 'positions': [],
              'current_exposure': exposure(current),
              'effective_number_of_positions_including_cash': 1 / sum(w * w for w in current.values()),
              'scenarios': [],
              'limitations': ['Authored assumptions; no automatic target selection or suitability assessment.',
                             'Direct exposure only; no fund look-through or statistical risk model.',
                             'Theme tags may overlap; their weights are not shares of portfolio risk.',
                             'Scenarios use fixed initial weights and base-currency total returns; no rebalancing.',
                             'Gross arithmetic excludes taxes, trading costs and market impact.']}
    for pos in data['positions']:
        sid = pos['security_id']
        row = {'security_id': sid, 'label': pos['label'], 'value_base': amounts[sid],
               'current_weight': current[sid],
               'current_weight_of_total': current[sid] * scale if scale is not None else None}
        if target is not None:
            row.update(target_weight=target[sid],
                       target_weight_of_total=target[sid] * scale if scale is not None else None,
                       delta_weight=target[sid] - current[sid],
                       delta_value_base=target[sid] * total - amounts[sid])
        result['positions'].append(row)
    if target is not None:
        result['target_basis'] = data['target_basis']
        result['target_exposure'] = exposure(target)
    for scenario in data.get('scenarios', []):
        entry = {key: scenario[key] for key in ('id', 'label', 'horizon', 'assumptions')}
        for name, vector in [('current', current), ('target', target)]:
            if vector is None:
                continue
            contributions = {sid: weight * number(scenario['returns'][sid], sid)
                             for sid, weight in vector.items()}
            outcome = sum(contributions.values())
            entry[name] = {'return_fraction': outcome, 'change_base': outcome * total,
                           'ending_value_base': total * (1 + outcome),
                           'position_return_contributions': contributions}
        result['scenarios'].append(entry)
    contribution = data.get('contribution')
    if contribution is not None:
        amount = number(contribution['amount_base'], 'contribution.amount_base')
        allocation = weights(contribution['allocation_weights'], set(amounts), 'contribution allocation')
        result['after_contribution'] = {
            'amount_base': amount, 'portfolio_value_base': total + amount,
            'weights': {sid: (value + amount * allocation[sid]) / (total + amount)
                        for sid, value in amounts.items()}}
        result['after_contribution']['exposure'] = exposure(result['after_contribution']['weights'])
    return result


def reject_constant(value):
    raise PortfolioError(f'non-finite JSON constant: {value}')


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f'duplicate JSON key: {key}')
        out[key] = value
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'calculate'])
    parser.add_argument('snapshot', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.snapshot.read_text(), parse_float=Decimal,
                          parse_constant=reject_constant, object_pairs_hook=unique_object)
        if args.command == 'validate':
            validate(data)
            result = {'valid': True, 'suitability': 'not_assessed_by_calculator'}
        else:
            result = calculate(data)
        # Decimal strings preserve arithmetic precision in the exported result.
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str, allow_nan=False))
    except (PortfolioError, OSError, json.JSONDecodeError) as exc:
        print(f'Portfolio input error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
