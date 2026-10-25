#!/usr/bin/env python3
"""Frozen descriptive arithmetic on the preflight candidate subset, not valuation."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

NODES = ['3MON', '1YR', '5YR', '10YR', '30YR']


def display(x):
    if x is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 30
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def quantile(values, weights, p):
    """Left-inverse empirical CDF; no interpolation, all weights strictly positive."""
    if not values or len(values) != len(weights) or not 0 < p <= 1:
        raise ValueError('Invalid quantile input')
    if any(w <= 0 for w in weights):
        raise ValueError('Nonpositive weight')
    target, cumulative = sum(weights) * p, F(0)
    for value, weight in sorted(zip(values, weights)):
        cumulative += weight
        if cumulative >= target:
            return value
    raise AssertionError('Unreachable')


def calculate(candidate):
    nav = F(candidate['nav'])
    if nav <= 0:
        raise ValueError('NAV must be positive')
    nodes = []
    for node in NODES:
        s01 = candidate['raw_metrics'][f'INTRST_RATE_CHANGE_{node}_DV01']
        s100 = candidate['raw_metrics'][f'INTRST_RATE_CHANGE_{node}_DV100']
        d01, d100 = F(s01), F(s100)
        r = d100 - 100 * d01
        bp = 10000 * abs(r) / nav
        relative = abs(r) / (100 * abs(d01)) if d01 else None
        with localcontext() as ctx:
            ctx.prec = 80
            independent_residual = Decimal(s100) - 100 * Decimal(s01)
            if F(independent_residual) != r:
                raise ArithmeticError('Independent residual mismatch')
            independent_bp = 10000 * abs(independent_residual) / Decimal(candidate['nav'])
            if abs(F(independent_bp) - bp) > F(1, 10**60) * max(F(1), bp):
                raise ArithmeticError('Independent ratio mismatch')
        nodes.append({'node': node, 'residual_exact': str(r), 'residual': display(r),
                      'nav_bp_exact': str(bp), 'nav_bp': display(bp),
                      'relative_exact': str(relative) if relative is not None else None,
                      'relative': display(relative), 'one_sided_zero': (d01 == 0) != (d100 == 0),
                      'opposite_nonzero_signs': d01 * d100 < 0})
    primary = max(F(n['nav_bp_exact']) for n in nodes)
    vector = sum(F(n['nav_bp_exact']) for n in nodes)
    return {**candidate, 'nodes': nodes, 'primary_exact': str(primary),
            'max_node_nav_bp': display(primary), 'vector_discrepancy_nav_bp': display(vector),
            'vector_exact': str(vector), 'internal_precision': 'unknown'}


def distribution(rows, field):
    values = [F(r[field]) for r in rows]
    nav = [F(r['nav']) for r in rows]
    result = {}
    for name, weights in [('unweighted', [F(1)] * len(rows)), ('nav_weighted', nav)]:
        result[name] = {label: display(quantile(values, weights, q))
                       for label, q in [('median', F(1, 2)), ('p90', F(9, 10)), ('max', F(1))]}
    return result


def analyze(preflight):
    if preflight.get('status') != 'preflight_only':
        raise ValueError('Require successful complete preflight')
    rows = [calculate(r) for r in preflight['candidates']]
    if not rows or len({r['series_id'] for r in rows}) != len(rows):
        raise ValueError('Empty or duplicate-series sample')
    first = {r['series_id'] for r in sorted(rows, key=lambda r: r['series_id'])[:20]}
    ranked = sorted(rows, key=lambda r: (-F(r['primary_exact']), r['series_id']))
    cutoff = F(ranked[min(20, len(ranked)) - 1]['primary_exact'])
    top = {r['series_id'] for r in ranked if F(r['primary_exact']) >= cutoff}
    audits = []
    for row in sorted(rows, key=lambda r: r['series_id']):
        sid = row['series_id']
        if sid in first or sid in top:
            acc = row['accession']
            audits.append({'series_id': sid, 'accession': acc, 'cik': row['cik'],
                           'series_name': row['series_name'], 'max_node_nav_bp': row['max_node_nav_bp'],
                           'first_20': sid in first, 'top_20_including_ties': sid in top,
                           'filing_index': f'https://www.sec.gov/Archives/edgar/data/{int(row["cik"])}/{acc.replace("-", "")}/{acc}-index.html' if row['cik'] else None,
                           'status': 'not_source_reconciled'})
    total_nav = sum(F(r['nav']) for r in rows)
    thresholds = []
    for threshold in [1, 10, 100]:
        selected = [r for r in rows if F(r['primary_exact']) > threshold]
        thresholds.append({'strictly_above_nav_bp': threshold, 'fund_count': len(selected),
                           'registrant_count_nonmissing': len({r['cik'] for r in selected if r['cik']}),
                           'fund_share': display(F(len(selected), len(rows))),
                           'nav_share': display(sum(F(r['nav']) for r in selected) / total_nav)})
    summary = {'status': 'PROVISIONAL_BULK_ARITHMETIC_ONLY', 'sample_count': len(rows),
               'registrant_count': len({r['cik'] for r in rows if r['cik']}),
               'total_nav': display(total_nav), 'all_zero_vectors': sum(r['all_zero_vector'] for r in rows),
               'exact_scaling_all_nodes': sum(F(r['primary_exact']) == 0 for r in rows),
               'undefined_relative_nodes': sum(n['relative_exact'] is None for r in rows for n in r['nodes']),
               'nav_quarantined_not_included': preflight['exclusion_counts'].get('nav_reconciliation_requires_source_check', 0),
               'exclusion_counts': preflight['exclusion_counts'],
               'primary_distribution_nav_bp': distribution(rows, 'primary_exact'),
               'vector_distribution_nav_bp_NOT_joint_shock': distribution(rows, 'vector_exact'),
               'thresholds': thresholds,
               'quantile_convention': 'Left-inverse empirical CDF; unweighted and positive NAV weights',
               'arithmetic_checks': {'fraction_decimal_nodes_checked': 5 * len(rows), 'decimal_precision': 80},
               'audit_selection': {'first_20': len(first), 'top_20_plus_ties': len(top),
                                   'overlap': len(first & top), 'union': len(first | top)},
               'source_validated_funds': 0,
               'materiality_gate': 'NOT_ESTABLISHED; bulk thresholds alone do not meet source/convention requirements',
               'economic_interpretation_gate': 'NOT_ESTABLISHED; no independent revaluation',
               'priority_gate': 'INCOMPLETE; no novelty claim',
               'caveat': 'Conditional on exact-NAV preflight subset and unverified source conventions. Not all bond funds, losses, valuation errors, violations, pooling gains or margin calls.'}
    # Post-result review diagnostics, not new exclusions or replacement outcomes.
    summary['post_result_diagnostics'] = {
        'label': 'Added after snapshot review; literal filed zeros preserved, no missingness inferred.',
        'one_sided_zero_nodes': sum(n['one_sided_zero'] for r in rows for n in r['nodes']),
        'opposite_nonzero_sign_nodes': sum(n['opposite_nonzero_signs'] for r in rows for n in r['nodes']),
        'funds_with_one_sided_zero_primary_node': sum(any(n['one_sided_zero'] and n['nav_bp_exact'] == r['primary_exact'] for n in r['nodes']) for r in rows),
        'funds_with_opposite_sign_primary_node': sum(any(n['opposite_nonzero_signs'] and n['nav_bp_exact'] == r['primary_exact'] for n in r['nodes']) for r in rows),
        'threshold_breakdown': [{
            'strictly_above_nav_bp': threshold,
            'funds_with_one_sided_zero_primary_node': sum(F(r['primary_exact']) > threshold and any(n['one_sided_zero'] and n['nav_bp_exact'] == r['primary_exact'] for n in r['nodes']) for r in rows),
            'funds_with_opposite_sign_primary_node': sum(F(r['primary_exact']) > threshold and any(n['opposite_nonzero_signs'] and n['nav_bp_exact'] == r['primary_exact'] for n in r['nodes']) for r in rows),
        } for threshold in [1, 10, 100]],
    }
    return summary, rows, audits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=Path('complete_preflight.json'))
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(exist_ok=False)
    raw = args.input.read_bytes()
    summary, rows, audits = analyze(json.loads(raw))
    summary['preflight_sha256'] = hashlib.sha256(raw).hexdigest()
    for name, value in [('summary.json', summary), ('rows.json', rows), ('audit_selection.json', audits)]:
        (args.output_dir / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
