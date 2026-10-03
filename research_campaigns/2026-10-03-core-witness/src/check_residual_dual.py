#!/usr/bin/env python3
"""Exact independent semantic QA of the frozen residual-relaxation certificate.

Only the Python standard library is used. No discovery source, matrix builder,
semantic checker, or solver is imported or AST-extracted. Inequalities are
reconstructed below from their mathematical names. Raw primal checks use scalar
team values, separately from the sparse coefficient reconstruction.

Usage:
  python3 -B -O check_residual_dual.py CERTIFICATE --qa-output RESULT
  python3 -B -O check_residual_dual.py --check-stdin < CERTIFICATE

The QA command executes the baseline and each corruption in a fresh python -O
process. It writes only the explicitly requested result file.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys


EXPECTED = F(211, 714)
PAIR_SECTORS = ((0, 1), (0, 2), (1, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value):
    need(type(value) in (str, int), 'rational must be an exact string or integer')
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError('invalid rational') from error


def integer(value, stop, description):
    need(type(value) is int and 0 <= value < stop, description)
    return value


def check(document):
    need(type(document) is dict, 'document must be an object')
    m = document['m']
    need(type(m) is int and m > 0, 'm must be a positive integer')
    teams = document['P']
    need(type(teams) is list, 'P must be a list')
    for team in teams:
        need(type(team) is list and len(team) == 3, 'team shape')
        for label in team:
            integer(label, m, 'team label')
    for sector in range(3):
        need(len({t[sector] for t in teams}) == len(teams), 'P not player-disjoint')
    k = m - len(teams)
    used = {(s, t[s]) for t in teams for s in range(3)}
    unmatched = {(s, a) for s in range(3) for a in range(m)} - used
    allowed = {(p, a, a) for p in range(3) for a in range(m)}
    for team in teams:
        for p, (s, t) in enumerate(PAIR_SECTORS):
            allowed.add((p, team[s], team[t]))
    matrices = document['matrices']
    need(type(matrices) is list and len(matrices) == 3, 'matrix count')
    weights = {}
    for p, matrix in enumerate(matrices):
        need(type(matrix) is list and len(matrix) == m, 'matrix height')
        for a, line in enumerate(matrix):
            need(type(line) is list and len(line) == m, 'matrix width')
            for b, value in enumerate(line):
                value = rational(value)
                need(0 <= value <= 1, 'pair weight outside [0,1]')
                need((p, a, b) in allowed or value == 0, 'weight outside support')
                weights[p, a, b] = value

    def team_value(team):
        a, b, c = team
        return weights[0, a, b] + weights[1, a, c] + weights[2, b, c]

    diagonal = [team_value((a, a, a)) for a in range(m)]
    need(sum(diagonal) == 1, 'primal diagonal normalization')
    x_values, h_values = document['core'], document['h']
    need(type(x_values) is list and len(x_values) == 3*m, 'core shape')
    need(type(h_values) is list and len(h_values) == 3*m, 'h shape')
    x = {(s, a): rational(x_values[s*m+a]) for s in range(3) for a in range(m)}
    h = {(s, a): rational(h_values[s*m+a]) for s in range(3) for a in range(m)}
    need(all(0 <= v <= 1 for v in x.values()), 'core outside [0,1]')
    need(all(0 <= v <= 1 for v in h.values()), 'h outside [0,1]')
    need(sum(x.values()) == 1, 'primal core total')
    W = sum((team_value(t) for t in teams), F(0))
    budget = {(s, a): sum(weights[p, a, a] for p, st in enumerate(PAIR_SECTORS)
                          if s in st) for s in range(3) for a in range(m)}

    # Direct scalar primal semantics. Retain each named lhs/rhs to cross-check
    # the independently reconstructed linear rows at this primal point.
    scalar_rows = {}

    def primal_row(name, lhs, rhs=F(0)):
        need(lhs <= rhs, 'primal inequality: ' + str(name))
        scalar_rows[name] = (lhs, rhs)

    for team in itertools.product(range(m), repeat=3):
        primal_row(('core', *team), team_value(team) - sum(x[s, team[s]] for s in range(3)))
    for s in range(3):
        for a in range(m):
            i = s*m+a
            primal_row(('diagonal_cap', i), h[s, a] - diagonal[a])
            primal_row(('core_dominance', i), x[s, a] - h[s, a])
    for s, a in sorted(unmatched):
        primal_row(('unmatched_cap', s*m+a), h[s, a] + W, F(1))
    for s in range(3):
        for a in range(m):
            for b in range(m):
                if a == b:
                    continue
                team = [a, a, a]
                team[s] = b
                primal_row(('completion', s, a, b), h[s, a] - h[s, b]
                           + team_value(team) - diagonal[a])
                primal_row(('range', s, a, b), h[s, a] - h[s, b] - budget[s, a])
    for e, team in enumerate(teams):
        for s, t, u in itertools.permutations(range(3)):
            a, b, c = team[s], team[t], team[u]
            primal_row(('P_induced', e, s, t, u), h[u, b] - h[u, c]
                       + team_value(team) - diagonal[b] - budget[s, a])
    for s, a in sorted(unmatched):
        primal_row(('residual', s*m+a), k*h[s, a] + W - (k-1)*budget[s, a], F(1))
    objective = 3*W + sum((h[i] for i in unmatched), F(0))
    J = objective/3 - 1
    need(J == rational(document['J_relaxed']), 'primal claimed objective')

    # A pair shared by a diagonal and P, or multiple descriptions of a pair,
    # is ONE variable because these are set-valued, sector-tagged keys.
    variables = [('w', *edge) for edge in sorted(allowed)]
    variables += [('x', s, a) for s in range(3) for a in range(m)]
    variables += [('h', s, a) for s in range(3) for a in range(m)]
    z = {('w', *edge): weights[edge] for edge in allowed}
    z.update({('x', *i): value for i, value in x.items()})
    z.update({('h', *i): value for i, value in h.items()})

    def add(row, variable, coefficient):
        need(variable in z, 'unknown variable')
        row[variable] = row.get(variable, F(0)) + coefficient

    def add_team(row, team, coefficient=1):
        # Missing pairs are literal zero constants, not new decision variables.
        for p, (s, t) in enumerate(PAIR_SECTORS):
            edge = (p, team[s], team[t])
            if edge in allowed:
                add(row, ('w', *edge), coefficient)

    def add_budget(row, sector, label, coefficient):
        for p, st in enumerate(PAIR_SECTORS):
            if sector in st:
                add(row, ('w', p, label, label), coefficient)

    def coordinate(i):
        integer(i, 3*m, 'player index')
        return divmod(i, m)

    def named_row(name):
        need(type(name) in (tuple, list) and len(name) > 0 and type(name[0]) is str,
             'constraint name')
        kind, *indices = name
        row, rhs = {}, F(0)
        if kind == 'core':
            need(len(indices) == 3, 'core row arity')
            for a in indices:
                integer(a, m, 'core label')
            add_team(row, indices)
            for s, a in enumerate(indices):
                add(row, ('x', s, a), -1)
        elif kind in ('diagonal_cap', 'core_dominance', 'unmatched_cap', 'residual'):
            need(len(indices) == 1, 'player row arity')
            s, a = coordinate(indices[0])
            if kind == 'diagonal_cap':
                add(row, ('h', s, a), 1)
                add_team(row, (a, a, a), -1)
            elif kind == 'core_dominance':
                add(row, ('x', s, a), 1)
                add(row, ('h', s, a), -1)
            else:
                need((s, a) in unmatched, 'row target must be unmatched')
                add(row, ('h', s, a), 1 if kind == 'unmatched_cap' else k)
                for team in teams:
                    add_team(row, team)
                if kind == 'residual':
                    add_budget(row, s, a, -(k-1))
                rhs = F(1)
        elif kind in ('completion', 'range'):
            need(len(indices) == 3, 'comparison row arity')
            s, a, b = indices
            integer(s, 3, 'comparison sector')
            integer(a, m, 'comparison source')
            integer(b, m, 'comparison destination')
            need(a != b, 'comparison must use distinct labels')
            add(row, ('h', s, a), 1)
            add(row, ('h', s, b), -1)
            if kind == 'completion':
                team = [a, a, a]
                team[s] = b
                add_team(row, team)
                add_team(row, (a, a, a), -1)
            else:
                add_budget(row, s, a, -1)
        elif kind == 'P_induced':
            need(len(indices) == 4, 'P-induced row arity')
            e, s, t, u = indices
            integer(e, len(teams), 'P-team index')
            need(all(type(v) is int for v in (s, t, u)) and {s, t, u} == {0, 1, 2},
                 'P-induced sectors must be a permutation')
            team = teams[e]
            a, b, c = team[s], team[t], team[u]
            add(row, ('h', u, b), 1)
            add(row, ('h', u, c), -1)
            add_team(row, team)
            add_team(row, (b, b, b), -1)
            add_budget(row, s, a, -1)
        else:
            raise ValueError('unknown constraint type: ' + kind)
        return row, rhs

    for name, (lhs, rhs) in scalar_rows.items():
        row, reconstructed_rhs = named_row(name)
        need(rhs == reconstructed_rhs, 'scalar/coefficient rhs disagreement')
        need(sum(coefficient*z[v] for v, coefficient in row.items()) == lhs,
             'scalar/coefficient lhs disagreement: ' + str(name))

    c = {v: F(0) for v in variables}
    for team in teams:
        add_team(c, team, 3)
    for i in unmatched:
        c['h', *i] += 1
    need(sum(c[v]*z[v] for v in variables) == objective, 'objective coefficient mismatch')

    dual = document['residual_dual']
    need(type(dual) is dict and type(dual['rows']) is list, 'dual shape')
    remainder = dict(c)
    weighted_rhs = F(0)
    weighted_slack = F(0)
    counts = Counter()
    for entry in dual['rows']:
        need(type(entry) is dict, 'dual row entry')
        mass = rational(entry['mass'])
        need(mass >= 0, 'negative inequality multiplier')
        row, rhs = named_row(entry['constraint'])
        weighted_rhs += mass*rhs
        weighted_slack += mass*(rhs - sum(value*z[v] for v, value in row.items()))
        for v, coefficient in row.items():
            remainder[v] -= mass*coefficient
        counts[entry['constraint'][0]] += 1
    normalization = rational(dual['normalization'])
    core_total = rational(dual['core_total'])
    # Equality multipliers are FREE in sign; both equality rhs values are 1.
    for p in range(3):
        for a in range(m):
            remainder['w', p, a, a] -= normalization
    for s in range(3):
        for a in range(m):
            remainder['x', s, a] -= core_total
    # For 0 <= z_v <= 1, r_v*z_v <= max(0,r_v), including negative r_v.
    correction = sum((max(F(0), r) for r in remainder.values()), F(0))
    need(correction == rational(dual['box_correction']), 'dual box correction mismatch')
    raw_bound = weighted_rhs + normalization + core_total + correction
    bound = raw_bound/3 - 1
    need(bound == rational(dual['upper']), 'dual upper mismatch')
    need(bound == J, 'primal/dual gap')
    need(bound == EXPECTED, 'unexpected CW-01 optimum')
    need(correction == 0, 'expected coefficient domination without box correction')
    need(all(r <= 0 for r in remainder.values()), 'coefficient domination failure')
    box_slack = sum((max(F(0), remainder[v])-remainder[v]*z[v] for v in variables), F(0))
    need(raw_bound-objective == weighted_slack+box_slack, 'gap identity failure')
    need(weighted_slack == box_slack == 0, 'nonzero complementary slackness')
    return {
        'status': 'PASS', 'm': m, 'P_size': len(teams), 'k': k,
        'pair_variables': len(allowed), 'total_variables': len(variables),
        'unmatched_players': len(unmatched), 'full_triples_checked': m**3,
        'primal_rows_checked': len(scalar_rows),
        'primal_row_counts': dict(sorted(Counter(n[0] for n in scalar_rows).items())),
        'dual_rows': len(dual['rows']), 'dual_row_counts': dict(sorted(counts.items())),
        'W': str(W), 'sum_unmatched_h': str(sum(h[i] for i in unmatched)),
        'raw_objective': str(objective), 'primal_J': str(J),
        'dual_weighted_rhs': str(weighted_rhs), 'normalization': str(normalization),
        'core_total': str(core_total), 'box_correction': str(correction),
        'raw_dual_bound': str(raw_bound), 'dual_upper': str(bound),
        'zero_residual_coefficients': sum(r == 0 for r in remainder.values()),
        'negative_residual_coefficients': sum(r < 0 for r in remainder.values()),
        'maximum_residual_coefficient': str(max(remainder.values())),
        'weighted_primal_slack': str(weighted_slack), 'box_slack': str(box_slack),
        'scope': 'exact optimum of the stated necessary-condition relaxation; h is not certified actual H',
    }


def altered(document, change):
    result = copy.deepcopy(document)
    change(result)
    return result


def qa(path):
    document = json.loads(path.read_text())
    script = Path(__file__).resolve()
    command = [sys.executable, '-B', '-O', str(script), '--check-stdin']

    def execute(value):
        completed = subprocess.run(command, input=json.dumps(value), text=True,
                                   capture_output=True, check=False)
        return {'exit_code': completed.returncode, 'stdout': completed.stdout.strip(),
                'stderr': completed.stderr.strip()}

    baseline = execute(document)
    need(baseline['exit_code'] == 0, 'baseline subprocess failed: ' + baseline['stdout'])
    cases = []

    def reject(name, mutate):
        result = execute(altered(document, mutate))
        need(result['exit_code'] != 0, 'corruption accepted: ' + name)
        parsed = json.loads(result['stdout'])
        need(parsed.get('status') == 'REJECT', 'corruption crashed instead of rejected: ' + name)
        cases.append({'name': name, **result})

    reject('positive_dual_mass_increased', lambda d: d['residual_dual']['rows'][0].update(
        mass=str(rational(d['residual_dual']['rows'][0]['mass']) + 1)))
    reject('dual_mass_negative', lambda d: d['residual_dual']['rows'][0].update(mass='-1'))
    reject('critical_core_row_removed', lambda d: d['residual_dual']['rows'].pop(0))
    reject('normalization_multiplier_increased', lambda d: d['residual_dual'].update(
        normalization=str(rational(d['residual_dual']['normalization']) + 1)))
    reject('core_total_multiplier_increased', lambda d: d['residual_dual'].update(
        core_total=str(rational(d['residual_dual']['core_total']) + 1)))
    reject('claimed_upper_changed', lambda d: d['residual_dual'].update(
        upper=str(rational(d['residual_dual']['upper']) + F(1, 1009))))
    reject('claimed_box_correction_changed', lambda d: d['residual_dual'].update(box_correction='1/1009'))
    reject('primal_core_changed', lambda d: d['core'].__setitem__(0, str(rational(d['core'][0]) + F(1, 1009))))
    used = {s*document['m']+t[s] for t in document['P'] for s in range(3)}
    target = min(set(range(3*document['m']))-used)
    reject('primal_unmatched_h_changed', lambda d: d['h'].__setitem__(target, str(rational(d['h'][target]) + F(1, 1009))))
    reject('primal_diagonal_weight_changed', lambda d: d['matrices'][0][0].__setitem__(0,
        str(rational(d['matrices'][0][0][0]) + F(1, 1009))))
    reject('primal_claimed_objective_changed', lambda d: d.update(J_relaxed='0'))
    reject('unknown_dual_row', lambda d: d['residual_dual']['rows'][0].update(constraint=['unknown', 0]))
    reject('boolean_dual_mass', lambda d: d['residual_dual']['rows'][0].update(mass=True))
    reject('float_dual_mass', lambda d: d['residual_dual']['rows'][0].update(mass=0.25))
    reject('boolean_player_index', lambda d: d['residual_dual']['rows'][0].update(constraint=['core', True, 1, 2]))
    return {
        'status': 'PASS', 'python_version': platform.python_version(),
        'qa_driver_optimization': sys.flags.optimize,
        'subprocess_command': command,
        'checker': str(script), 'checker_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
        'certificate': str(path.resolve()),
        'certificate_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'independence': 'standard library only; no discovery imports, solver imports, shared matrix builder, or AST-extracted semantic checker',
        'baseline_execution': baseline,
        'baseline_result': json.loads(baseline['stdout']),
        'corruptions_rejected': len(cases), 'corruption_executions': cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', nargs='?', type=Path)
    parser.add_argument('--check-stdin', action='store_true')
    parser.add_argument('--qa-output', type=Path)
    args = parser.parse_args()
    try:
        if args.check_stdin:
            need(args.certificate is None and args.qa_output is None, 'incompatible stdin options')
            result = check(json.load(sys.stdin))
            result['optimization'] = sys.flags.optimize
        else:
            need(args.certificate is not None, 'certificate path required')
            if args.qa_output:
                result = qa(args.certificate)
                args.qa_output.write_text(json.dumps(result, indent=2) + '\n')
            else:
                result = check(json.loads(args.certificate.read_text()))
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError, TypeError, IndexError) as error:
        print(json.dumps({'status': 'REJECT', 'error': str(error), 'optimization': sys.flags.optimize}))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
