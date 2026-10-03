#!/usr/bin/env python3
"""Independent rational QA for the two completed diagnostic markets.

Standard library only. No discovery solver or matrix-builder import. Run with
python -B -O. Only CW-01 through CW-04 are named; no held-out files are read.
"""
import ast
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
from fractions import Fraction as F

REPO = Path('/Users/maxf/projects/economics-research/game-theory/coopgpt')
BASE = REPO / 'research_campaigns/2026-10-03-core-witness'
OUTPUT = Path('/private/tmp/coopgpt-witness-20261003/diagnostic_qa.json')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rational(value):
    need(type(value) in (str, int), 'rational type')
    return F(value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(items):
    d = {}
    for key, value in items:
        need(key not in d, 'duplicate JSON key')
        d[key] = value
    return d


def load(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def market(raw):
    m = raw['m']
    need(type(m) is int and m > 0, 'm')
    P = raw['P']
    need(type(P) is list, 'P list')
    for team in P:
        need(type(team) is list and len(team) == 3, 'P arity')
        need(all(type(j) is int and 0 <= j < m for j in team), 'P labels')
    need(all(len({t[s] for t in P}) == len(P) for s in range(3)), 'P overlaps')
    raw_mats = raw['matrices']
    need(type(raw_mats) is list and len(raw_mats) == 3, 'matrix count')
    mats = []
    for mat in raw_mats:
        need(type(mat) is list and len(mat) == m, 'matrix rows')
        need(all(type(row) is list and len(row) == m for row in mat), 'matrix columns')
        mats.append([[rational(v) for v in row] for row in mat])
    ends = ((0, 1), (0, 2), (1, 2))
    for k, (s, t) in enumerate(ends):
        for a in range(m):
            for b in range(m):
                allowed = a == b or any(team[s] == a and team[t] == b for team in P)
                need(mats[k][a][b] >= 0, 'negative pair')
                need(allowed or mats[k][a][b] == 0, 'off-support pair')
    # Raw full-team table, constructed without discovery layout code.
    teams = []
    worth = {}
    for a in range(m):
        for b in range(m):
            for c in range(m):
                team = (a, b, c)
                worth[team] = mats[0][a][b] + mats[1][a][c] + mats[2][b][c]
                teams.append((team, (a, m + b, 2*m + c), worth[team]))
    diag = [worth[(j, j, j)] for j in range(m)]
    need(sum(diag) == 1, 'diagonal normalization')
    U = [s*m+j for s in range(3) for j in range(m)
         if all(team[s] != j for team in P)]
    h = list(map(rational, raw['h']))
    need(len(h) == 3*m and min(h) >= 0, 'relaxed h')
    return dict(m=m, P=P, mats=mats, teams=teams, worth=worth, diag=diag,
                U=U, h=h, W=sum(worth[tuple(t)] for t in P))


def check_target(rec, data):
    m, diag = data['m'], data['diag']
    target = rec['target']
    need(type(target) is int and target in data['U'], 'target not unmatched')
    H = rational(rec['H'])
    need(rational(rec['relaxed_h']) == data['h'][target], 'relaxed h mismatch')
    x = list(map(rational, rec['witness']))
    need(len(x) == 3*m and min(x) >= 0, 'witness dimensions or sign')
    for j in range(m):
        need(sum(x[s*m+j] for s in range(3)) == diag[j], 'witness diagonal tightness')
    need(sum(x) == 1, 'witness total')
    for team, players, val in data['teams']:
        need(sum(x[i] for i in players) >= val, 'witness full-team coverage: %r' % (team,))
    need(x[target] == H, 'target H is not attained')
    nu = list(map(rational, rec['dual_diagonal']))
    need(len(nu) == m, 'dual diagonal dimension')
    coeff = [nu[j] for s in range(3) for j in range(m)]
    bound = sum(a*b for a, b in zip(nu, diag))
    seen = set()
    for row in rec['dual_teams']:
        need(type(row) is list and len(row) == 4, 'dual team row')
        a, b, c = row[:3]
        need(all(type(j) is int and 0 <= j < m for j in (a, b, c)), 'dual team label')
        need((a, b, c) not in seen, 'duplicate dual team')
        seen.add((a, b, c))
        mass = rational(row[3])
        need(mass >= 0, 'negative dual team coefficient')
        for i in (a, m+b, 2*m+c):
            coeff[i] -= mass
        bound -= mass*data['worth'][(a, b, c)]
    margins = [coeff[i] - int(i == target) for i in range(3*m)]
    need(min(margins) >= 0, 'dual coefficient domination')
    need(bound == H, 'dual objective does not equal H')
    return dict(target=target, H=str(H), exact_dual_objective=str(bound),
                minimum_coefficient_margin=str(min(margins)),
                full_team_checks=len(data['teams']), dual_rows=len(seen))


def expect_rejection(rec, data, label, required_text=None):
    try:
        check_target(rec, data)
    except ValueError as exc:
        if required_text is not None:
            need(required_text in str(exc), label + ': unexpected rejection: ' + str(exc))
        return dict(control=label, rejected=True, reason=str(exc))
    raise ValueError(label + ': corrupted certificate accepted')


def negative_controls(rec, data):
    out = []
    bad = copy.deepcopy(rec)
    bad['H'] = str(rational(rec['H']) + F(1, 1000003))
    out.append(expect_rejection(bad, data, 'changed_H', 'not attained'))
    critical = next((k for k, row in enumerate(rec['dual_teams'])
                     if rational(row[3]) > 0 and data['worth'][tuple(row[:3])] > 0), None)
    need(critical is not None, 'no positive-worth critical dual row')
    bad = copy.deepcopy(rec)
    del bad['dual_teams'][critical]
    out.append(expect_rejection(bad, data, 'missing_critical_dual_team', 'objective'))
    bad = copy.deepcopy(rec)
    bad['dual_teams'][critical][3] = str(rational(bad['dual_teams'][critical][3]) + 1)
    out.append(expect_rejection(bad, data, 'increased_dual_multiplier'))
    # Preserve every diagonal sum, total, nonnegativity, and the target value.
    # Select an actual full-team violation independently of check_target.
    m = data['m']
    x = list(map(rational, rec['witness']))
    corruption = None
    for j in range(m):
        if corruption is not None:
            break
        for donor in range(3):
            if corruption is not None:
                break
            i = donor*m+j
            if i == rec['target'] or x[i] == 0:
                continue
            for receiver in range(3):
                k = receiver*m+j
                if k == i or k == rec['target']:
                    continue
                y = x[:]
                y[k] += y[i]
                y[i] = F(0)
                failed = next((team for team, players, val in data['teams']
                               if sum(y[p] for p in players) < val), None)
                if failed is not None:
                    corruption = (y, i, k, failed)
                    break
    need(corruption is not None, 'could not construct a pure core-coverage corruption')
    y, donor, receiver, failed = corruption
    bad = copy.deepcopy(rec)
    bad['witness'] = list(map(str, y))
    row = expect_rejection(bad, data, 'corrupt_witness_preserving_diagonals', 'coverage')
    row.update(donor=donor, receiver=receiver, independently_detected_team=list(failed))
    out.append(row)
    return out


def comparison(data, sector, a, b, expected):
    m = data['m']
    team = [a, a, a]
    team[sector] = b
    val = data['worth'][tuple(team)]
    constant = val - data['diag'][a]
    need(constant == expected, 'path comparison arithmetic')
    coeff = [0]*(3*m)
    for s in range(3):
        coeff[s*m+team[s]] += 1
        coeff[s*m+a] -= 1
    wanted = [0]*(3*m)
    wanted[sector*m+b] += 1
    wanted[sector*m+a] -= 1
    need(coeff == wanted, 'comparison coefficient identity')
    return dict(sector=sector, source=a, destination=b, team=team,
                worth=str(val), source_diagonal=str(data['diag'][a]), difference=str(constant))


def path_qa(markets, ideals):
    answers = {}
    for name in ('CW-01', 'CW-04'):
        data = markets[name]
        m = data['m']
        floors = [[F(0)]*m for _ in range(3)]
        if name == 'CW-01':
            arcs = [comparison(data, 0, 6, 7, F(1, 51)),
                    comparison(data, 1, 9, 7, F(1, 51))]
            floors[0][7] = floors[1][7] = F(1, 51)
            expected_J = F(59, 153)
            need(data['W'] == F(47, 51), 'CW01 W')
            need(sum(data['diag'][i % m] for i in data['U']) == F(73, 51), 'CW01 diagonal caps')
            need(data['h'][31] == F(4, 51), 'CW01 separated h')
            need(data['h'][7]-data['h'][6] == F(1, 51), 'CW01 A ideal comparison equality')
            need(data['h'][m+7]-data['h'][m+9] == F(1, 51), 'CW01 B ideal comparison equality')
        else:
            arcs = [comparison(data, 2, 3, 6, F(83, 2361)),
                    comparison(data, 2, 6, 0, F(6, 2361)),
                    comparison(data, 2, 0, 5, F(-29, 2361)),
                    comparison(data, 1, 1, 9, F(6, 2361))]
            floors[2][6] = F(83, 2361)
            floors[2][0] = floors[2][6] + F(6, 2361)
            floors[2][5] = floors[2][0] - F(29, 2361)
            floors[1][9] = F(6, 2361)
            expected_J = F(2252, 7083)
            need(data['W'] == F(2150, 2361), 'CW04 W')
            need(sum(data['diag'][i % m] for i in data['U']) == F(3100, 2361), 'CW04 diagonal caps')
            need(all(data['h'][i] == data['diag'][i % m] for i in data['U']), 'CW04 h equals diagonal caps')
            need(data['h'][2*m+6] - data['h'][2*m+3] == F(83, 2361), 'CW04 ideal comparison equality')
        caps = {i: data['diag'][i % m] - sum(floors[s][i % m] for s in range(3) if s != i//m)
                for i in data['U']}
        need(all(rational(r['H']) <= caps[r['target']] for r in ideals[name]['results']), 'exact ideal exceeds path cap')
        bound = data['W'] + sum(caps.values())/3 - 1
        need(bound == expected_J, 'path objective bound')
        if name == 'CW-04':
            need(bound < F(1, 3) and F(1, 3)-bound == F(109, 7083), 'CW04 threshold gap')
            need(sum(caps.values()) == F(2885, 2361), 'CW04 capped sum')
        else:
            need(bound > F(1, 3) and caps[31] == F(3, 51), 'CW01 limitation')
        separated = [dict(target=i, relaxed_h=str(data['h'][i]), valid_cap=str(cap))
                     for i, cap in caps.items() if data['h'][i] > cap]
        answers[name] = dict(comparisons=arcs, separated=separated,
                             sum_unmatched_caps=str(sum(caps.values())),
                             fixed_market_fixed_P_upper=str(bound), below_one_third=bound < F(1, 3))
    data = markets['CW-01']
    Q = data['P'][:3]
    labels = {j for t in Q for j in t}
    used = {s*data['m']+j for t in Q for s, j in enumerate(t)}
    diagonal = sum(data['diag'][j] for j in labels)
    value = sum(data['worth'][tuple(t)] for t in Q)
    need(labels == {0, 1, 2, 3, 4, 10}, 'old subset labels')
    need(diagonal == F(26, 51) and value == F(24, 51), 'old subset arithmetic')
    victims = [i for i in data['U'] if i % data['m'] in labels and i not in used
               and data['h'][i] > diagonal-value]
    need(len(victims) == 8, 'old subset separated count')
    answers['old_CW01_subset_slack'] = dict(diagonal=str(diagonal), matching_worth=str(value),
                                          cap=str(diagonal-value), separated_targets=victims)
    return answers


def retained_checkers():
    out = {}
    checker_path = BASE/'src/check_certificate.py'
    semantic_path = BASE/'src/relaxation.py'
    # Execute the unmodified retained semantic check function only. Importing its
    # containing module would unnecessarily load numpy/scipy and the LP builder.
    # Its globals are precisely Fraction, product, permutations and builtins.
    source = semantic_path.read_text()
    definitions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'check']
    need(len(definitions) == 1, 'semantic checker function inventory')
    tree = ast.Module(body=definitions, type_ignores=[])
    namespace = {'Q': F, 'product': itertools.product, 'permutations': itertools.permutations}
    exec(compile(ast.fix_missing_locations(tree), str(semantic_path), 'exec', optimize=1), namespace)
    semantic_check = namespace['check']
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for name in ('CW-01', 'CW-02', 'CW-03', 'CW-04'):
        command = [sys.executable, '-B', '-O', str(checker_path), str(BASE/'paired'/f'{name}_full.json')]
        proc = subprocess.run(command, text=True, capture_output=True, env=environment, timeout=60)
        need(proc.returncode == 0, name + ': retained full checker failed: ' + proc.stderr)
        full = json.loads(proc.stdout)
        need(full['accepted'] is True, name + ': full checker not accepted')
        relaxed = semantic_check(load(BASE/'paired'/f'{name}_relaxed.json'))
        need(relaxed['status'] == 'PASS', name + ': semantic relaxed checker failed')
        out[name] = dict(full=full, full_checker_command=command, full_checker_returncode=proc.returncode,
                         relaxed=relaxed)
        if name in ('CW-02', 'CW-03'):
            upper = F(full['upper'])
            need(upper < F(278, 1000), name + ': upper not below 278/1000')
            out[name]['exact_upper_below_278_over_1000'] = True
            out[name]['margin_below_278_over_1000'] = str(F(278, 1000)-upper)
    return dict(results=out, semantic_check_execution='unmodified AST-extracted check function; no module imports or row builder',
                semantic_check_source_sha256=hashlib.sha256(ast.get_source_segment(source, definitions[0]).encode()).hexdigest())


def run():
    need(sys.flags.optimize >= 1, 'run this QA under python -O')
    diagnostic_path = BASE/'interpretation/DIAGNOSTIC_IDEALS.json'
    diagnostics = load(diagnostic_path)
    need(set(diagnostics) == {'CW-01', 'CW-04'}, 'diagnostic support inventory')
    markets, verified = {}, {}
    total_checks = total_controls = 0
    for name in ('CW-01', 'CW-04'):
        data = market(load(BASE/'paired'/f'{name}_relaxed.json'))
        markets[name] = data
        packet = diagnostics[name]
        need(packet['m'] == data['m'], 'diagnostic market size mismatch')
        records = packet['results']
        targets = [r['target'] for r in records]
        need(all(type(t) is int for t in targets), 'diagnostic target types')
        need(targets == data['U'], 'diagnostic targets must equal sorted unmatched set exactly')
        accepted, controls = [], []
        for rec in records:
            accepted.append(check_target(rec, data))
            controls.append(dict(target=rec['target'], controls=negative_controls(rec, data)))
        sum_H = sum(rational(rec['H']) for rec in records)
        J = data['W'] + sum_H/3 - 1
        total_checks += len(records)*len(data['teams'])
        total_controls += 4*len(records)
        verified[name] = dict(target_count=len(targets), targets=targets, records=accepted,
                              negative_controls=controls, sum_H=str(sum_H), W=str(data['W']),
                              exact_fixed_market_fixed_P_J=str(J), scope='unmatched ideals and fixed-P J only; not full subsidy')
    paths = path_qa(markets, diagnostics)
    old = retained_checkers()
    files = [diagnostic_path, BASE/'interpretation/PATH_COMPLEMENT.md',
             BASE/'src/check_certificate.py', BASE/'src/relaxation.py', Path(__file__)]
    for name in ('CW-01', 'CW-02', 'CW-03', 'CW-04'):
        files += [BASE/'paired'/f'{name}_full.json', BASE/'paired'/f'{name}_relaxed.json']
    return dict(status='PASS', python=sys.version, executable=sys.executable, optimize=sys.flags.optimize,
                no_solver_or_discovery_builder_imported=True, held_out_reads=False,
                exact_core_team_checks=total_checks, negative_control_rejections=total_controls,
                diagnostic_ideals=verified, path_complement=paths, retained_checkers=old,
                hashes={str(p): digest(p) for p in files})


if __name__ == '__main__':
    try:
        result = run()
    except Exception as exc:
        result = dict(status='FAIL', error=type(exc).__name__ + ': ' + str(exc), optimize=sys.flags.optimize)
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(json.dumps(result))
        raise
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'optimize', 'exact_core_team_checks', 'negative_control_rejections')}, sort_keys=True))
