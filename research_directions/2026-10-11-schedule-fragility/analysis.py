#!/usr/bin/env python3
"""Exact, conditional analysis of saved schedules; no online policy or power fit."""
import argparse
import csv
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PRIMARY = 'gap10_deadline60_budget0.75_share0.5'
HARDWARE = ('laptop2', 'workstation')
R_GRID = ('1', '1.05', '1.10', '1.25', '1.5', '2')
Q_GRID = ('1', '.9', '.8', '.5')
P_GRID = (0, 1, 5, 10, 25, 50)
TOL = Fraction(1, 100_000_000)


def Q(x):
    return Fraction(str(x))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def close(a, b, label):
    need(abs(Q(a) - Q(b)) <= TOL, 'Source reconstruction mismatch: ' + label)


def energy_account(records, horizon):
    """Add nothing inside measured windows; keep cooldown and gap time distinct."""
    horizon = Q(horizon)
    need(horizon >= 0, 'Negative horizon')
    previous = Q(0)
    length = energy = slots = Q(0)
    for row in sorted(records, key=lambda x: Q(x['start'])):
        start, end, cost = map(Q, (row['start'], row['slot_end'], row['actual_energy_j']))
        need(start >= previous and end <= horizon, 'Overlapping/out-of-horizon slot')
        need(end > start + 4 and cost >= 0, 'Invalid slot duration or energy')
        length += end - start - 3
        slots += end - start
        energy += cost
        previous = end
    return dict(window_j=energy, window_s=length, omitted_s=horizon-length,
                cooldown_s=Q(3*len(records)), resident_gap_s=horizon-slots)


def uniform_frontier(slacks, omitted):
    """Intersection p*omitted<=slack. None=unlimited; negative=no p>=0 works."""
    need(len(slacks) == len(omitted) and len(slacks) > 0, 'Mismatched constraints')
    upper = []
    for s, t in zip(slacks, omitted):
        s, t = Q(s), Q(t)
        need(t >= 0, 'Negative omitted duration')
        if t:
            upper.append(s/t)
        elif s < 0:
            return Q(-1)
    return min(upper) if upper else None


def timing_trace(jobs, r, q):
    """Forward recurrence, used independently of the closed-form thresholds."""
    r, q = Q(r), Q(q)
    need(r >= 0 and 0 < q <= 1, 'Invalid timing parameter')
    previous = Q(0)
    result = []
    for job in jobs:
        t, d, a, deadline = (Q(job[k]) for k in ('t', 'd', 'arrival', 'deadline'))
        need(t >= a >= 0 and d > 0 and deadline > a, 'Invalid job')
        start = max(t, previous)
        previous = start + 4 + r*d
        response = previous - Q('3.5')
        result.append(dict(id=job['id'], start=start, end=previous,
                           response=response, ontime=response <= a+q*(deadline-a)))
    return result


def thresholds(jobs, q):
    """Exact min of all max-plus paths; each returned minimizer is a witness."""
    q = Q(q)
    need(0 < q <= 1, 'Invalid deadline multiplier')
    result = []
    for j, job in enumerate(jobs):
        deadline = Q(job['arrival']) + q*(Q(job['deadline'])-Q(job['arrival']))
        cumulative = Q(0)
        candidates = []
        for k in range(j, -1, -1):
            cumulative += Q(jobs[k]['d'])
            need(cumulative > 0, 'Nonpositive duration')
            numerator = deadline-Q(jobs[k]['t'])-4*(j-k)-Q('.5')
            candidates.append((numerator/cumulative, k, numerator, cumulative))
        critical, k, numerator, denominator = min(candidates)
        result.append(dict(id=job['id'], critical=critical,
                           witness_id=jobs[k]['id'], numerator=numerator,
                           denominator=denominator))
    return result


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True,
                              default=lambda x: str(x) if isinstance(x, Fraction)
                              else (_ for _ in ()).throw(TypeError(type(x))))+'\n')


def load_sources(source):
    freeze = json.loads((BASE/'PROTOCOL_FREEZE.json').read_text())
    need(hashlib.sha256((BASE/'PROTOCOL.txt').read_bytes()).hexdigest() ==
         freeze['protocol_sha256'], 'Frozen protocol changed')
    for name, digest in freeze['source_sha256'].items():
        need(hashlib.sha256((source/name).read_bytes()).hexdigest() == digest,
             'Frozen source changed: '+name)
    with (source/'COHORT.csv').open(newline='') as f:
        cohort = {r['request_id']: r for r in csv.DictReader(f)}
    with (source/'REPLAY_TABLE.csv').open(newline='') as f:
        table = {r['case_id']: r for r in csv.DictReader(f)}
    # parse_float=str preserves every serialized decimal rather than another float pass.
    cases = [json.loads(line, parse_float=str) for line in
             (source/'REPLAY_EVENTS.jsonl').read_text().splitlines()]
    need(len(cases) == len(table) == 81 and len(cohort) == 92, 'Unexpected cohort/cases')
    need(len({c['case_id'] for c in cases}) == 81, 'Duplicate cases')
    return cohort, table, cases


def schedule_jobs(arm, row, cohort):
    offered = set(cohort)
    admitted = [r['id'] for r in arm['records']]
    rejected = [r['id'] for r in arm['rejections']]
    need(len(admitted) == len(set(admitted)) and len(rejected) == len(set(rejected)),
         'Duplicate IDs')
    need(set(admitted).isdisjoint(rejected) and set(admitted)|set(rejected) == offered,
         'Incomplete offered partition')
    need(arm['offered'] == len(offered), 'Wrong offered count')
    by_id = {x: i for i, x in enumerate(sorted(offered))}
    by_server = [[], []]
    for rec in arm['records']:
        h = rec['server']
        need(h in (0, 1), 'Unknown owner')
        source = cohort[rec['id']]
        d = Q(source[HARDWARE[h]+'_actual_api_s'])
        a = by_id[rec['id']]*Q(row['interarrival_s'])
        deadline = a+Q(row['response_deadline_s'])
        for x, y, label in [
                (rec['arrival'], a, 'arrival'), (rec['deadline'], deadline, 'deadline'),
                (rec['actual_service_seconds'], d+4, 'slot duration'),
                (Q(rec['slot_end'])-Q(rec['start']), d+4, 'slot endpoints'),
                (rec['response_end'], Q(rec['start'])+d+Q('.5'), 'response'),
                (rec['actual_energy_j'], source[HARDWARE[h]+'_actual_gpu_j'], 'energy')]:
            close(x, y, label)
        by_server[h].append(dict(id=rec['id'], t=Q(rec['start']), d=d,
                                 arrival=a, deadline=deadline, outcome=rec['outcome']))
    for jobs in by_server:
        jobs.sort(key=lambda j: (j['t'], j['id']))
        baseline = timing_trace(jobs, 1, 1)
        for job, result in zip(jobs, baseline):
            close(result['start'], job['t'], 'baseline start')
            need(result['ontime'] == (job['outcome'] == 'ontime'), 'Baseline label changed')
    need(sum(j['outcome']=='ontime' for jobs in by_server for j in jobs) == arm['ontime'],
         'Wrong original count')
    need(len(admitted) == arm['started'] and len(rejected) == arm['rejected'] and
         arm['started']-arm['ontime'] == arm['late'], 'Wrong terminal counts')
    return by_server


def fraction_summary(values):
    vals = [Q(x) for x in values if x is not None]
    vals.sort()
    return dict(minimum=vals[0], median=vals[len(vals)//2], maximum=vals[-1],
                count=len(vals), unlimited=len(values)-len(vals))


def run(source, output):
    cohort, table, cases = load_sources(source)
    output.mkdir(parents=True, exist_ok=False)
    energy_results, timing_results, certificates, frontiers = [], [], [], []
    source_jobs = threshold_checks = grid_checks = 0
    original_pass = sorted(k for k,v in table.items() if v['conditional_screen_passed']=='True')
    need(len(original_pass) == 9, 'Wrong original strict-screen subset')
    for case in cases:
        cid, row = case['case_id'], table[case['case_id']]
        horizon = max((len(cohort)-1)*Q(row['interarrival_s'])+Q(row['response_deadline_s']),
                      max((Q(r['slot_end']) for arm in ('autarky','pool')
                           for r in case[arm]['records']), default=Q(0)))
        budgets = list(map(Q, case['autarky']['initial_budgets_j']))
        need(budgets == list(map(Q, case['pool']['initial_budgets_j'])), 'Budget mismatch')
        close(sum(budgets), row['total_window_budget_j'], 'budget sum')
        accounts, trace_counts = {}, {}
        for arm in ('autarky','pool'):
            jobs_by_server = schedule_jobs(case[arm], row, cohort)
            source_jobs += sum(map(len, jobs_by_server))
            accounts[arm] = [energy_account([r for r in case[arm]['records']
                                            if r['server']==h], horizon) for h in (0,1)]
            for h in (0,1):
                close(accounts[arm][h]['window_j'], case[arm]['per_owner_energy_j'][h],
                      'owner energy')
                need(accounts[arm][h]['omitted_s'] == accounts[arm][h]['cooldown_s']+
                     accounts[arm][h]['resident_gap_s'], 'Omitted duration partition')
            close(sum(x['window_j'] for x in accounts[arm]), case[arm]['total_energy_j'],
                  'total energy')
            trace_counts[arm] = {}
            for q in Q_GRID:
                per_server = [thresholds(jobs, q) for jobs in jobs_by_server]
                if q == '1':
                    all_items = [dict(server=h, **item) for h, items in enumerate(per_server)
                                 for item in items]
                    first = min(all_items, key=lambda x: (x['critical'],x['id'])) if all_items else None
                    baseline = [(job,event) for jobs in jobs_by_server
                                for job,event in zip(jobs,timing_trace(jobs,1,1))]
                    minimum_deadline = max(((event['response']-job['arrival'])/
                                            (job['deadline']-job['arrival'])
                                            for job,event in baseline),default=Q(0))
                    frontiers.append(dict(case_id=cid,arm=arm,
                        all_admitted_ontime_slowdown_witness=first,
                        all_admitted_ontime_min_deadline_fraction_at_r1=minimum_deadline))
                for h, items in enumerate(per_server):
                    jobs = jobs_by_server[h]
                    for j, item in enumerate(items):
                        # Independent forward evaluation at the exact critical value.
                        # Recurrence algebra holds at any real r; physical stress uses r>=1.
                        r = item['critical']
                        prev = Q(0)
                        for job in jobs[:j+1]:
                            prev = max(job['t'], prev)+4+r*job['d']
                        deadline = jobs[j]['arrival']+Q(q)*(jobs[j]['deadline']-jobs[j]['arrival'])
                        need(prev-Q('3.5') == deadline, 'Critical witness is not attained')
                        threshold_checks += 1
                        certificates.append(dict(case_id=cid, arm=arm, server=h,
                                                 deadline_fraction=q, **item))
                for r in R_GRID:
                    count = 0
                    for jobs, items in zip(jobs_by_server, per_server):
                        results = timing_trace(jobs, r, q)
                        for event, item in zip(results, items):
                            need(event['ontime'] == (Q(r) <= item['critical']),
                                 'Threshold/recurrence disagreement')
                            grid_checks += 1
                            count += event['ontime']
                    trace_counts[arm][q,r] = count
        nodes_a, nodes_p = accounts['autarky'], accounts['pool']
        wa, wp = (sum(x['window_j'] for x in nodes) for nodes in (nodes_a,nodes_p))
        ia, ip = ([x['omitted_s'] for x in nodes] for nodes in (nodes_a,nodes_p))
        delta_w = wp-wa
        delta_l = [nodes_p[h]['window_s']-nodes_a[h]['window_s'] for h in (0,1)]
        slope = -sum(delta_l)
        crossing = -delta_w/slope if slope else None
        energy = dict(case_id=cid, horizon_s=horizon, original_budgets_j=budgets,
                      accounts=accounts, delta_window_j=delta_w,
                      delta_window_seconds_by_owner=delta_l,
                      uniform_p_delta_energy_slope_seconds=slope,
                      uniform_p_energy_equality_w=crossing if crossing is not None and crossing>=0 else None,
                      uniform_p_energy_equality_kind=('all' if not slope and not delta_w else
                                                     'none_nonnegative' if crossing is None or crossing<0 else 'point'),
                      uniform_p_gross_budget_frontier_w={
                          'autarky':uniform_frontier([budgets[h]-nodes_a[h]['window_j'] for h in (0,1)],ia),
                          'pool':uniform_frontier([sum(budgets)-wp],[sum(ip)])},
                      grid=[])
        for p0,p1 in itertools.product(P_GRID, repeat=2):
            ps = (p0,p1)
            ea = [nodes_a[h]['window_j']+ps[h]*ia[h] for h in (0,1)]
            ep = [nodes_p[h]['window_j']+ps[h]*ip[h] for h in (0,1)]
            delta = sum(ep)-sum(ea)
            need(delta == delta_w-sum(ps[h]*delta_l[h] for h in (0,1)), 'Common-H cancellation failed')
            energy['grid'].append(dict(p_w=list(ps), autarky_total_j=sum(ea), pool_total_j=sum(ep),
                delta_total_j=delta, autarky_gross_feasible=all(ea[h]<=budgets[h] for h in (0,1)),
                pool_gross_feasible=sum(ep)<=sum(budgets),
                autarky_topup_by_owner_j=[max(Q(0),ea[h]-budgets[h]) for h in (0,1)],
                autarky_topup_j=sum(max(Q(0),ea[h]-budgets[h]) for h in (0,1)),
                pool_topup_j=max(Q(0),sum(ep)-sum(budgets))))
        energy_results.append(energy)
        debt_free = all(Q(case[a]['max_actual_budget_overrun_j']) <= TOL for a in ('autarky','pool'))
        for q,r in itertools.product(Q_GRID,R_GRID):
            a,p = (trace_counts[arm][q,r] for arm in ('autarky','pool'))
            late_a,late_p = case['autarky']['started']-a,case['pool']['started']-p
            screen = Q(p-a)/len(cohort)>=Q('.05') and late_a==late_p==0 and debt_free
            timing_results.append(dict(case_id=cid, slowdown=r, deadline_fraction=q,
                autarky_ontime=a,pool_ontime=p,autarky_late=late_a,pool_late=late_p,
                autarky_rejected=case['autarky']['rejected'],pool_rejected=case['pool']['rejected'],
                ontime_gain_requests=p-a, old_screen_with_reference_energy=screen))
            if q==r=='1':
                need(screen == (cid in original_pass), 'Base strict-screen mismatch')
    summary = dict(status='EXPLORATORY_FIXED_SCHEDULE_SENSITIVITY_NOT_MEASURED_VALIDATION',
        cases=len(cases), offered_per_case=len(cohort), original_strict_pass_cases=original_pass,
        primary_energy=next(e for e in energy_results if e['case_id']==PRIMARY),
        primary_timing=[t for t in timing_results if t['case_id']==PRIMARY],
        uniform_p_frontier_w={arm:fraction_summary([e['uniform_p_gross_budget_frontier_w'][arm]
                                                  for e in energy_results]) for arm in ('autarky','pool')},
        timing_grid_summary=[])
    for q,r in itertools.product(Q_GRID,R_GRID):
        cells=[t for t in timing_results if t['slowdown']==r and t['deadline_fraction']==q]
        summary['timing_grid_summary'].append(dict(slowdown=r,deadline_fraction=q,
            positive=sum(t['ontime_gain_requests']>0 for t in cells),
            zero=sum(t['ontime_gain_requests']==0 for t in cells),
            negative=sum(t['ontime_gain_requests']<0 for t in cells),
            strict_pass=sum(t['old_screen_with_reference_energy'] for t in cells),
            original_nine_still_pass=sum(t['old_screen_with_reference_energy'] and
                                         t['case_id'] in original_pass for t in cells)))
    dump(output/'ENERGY.json',energy_results)
    dump(output/'TIMING.json',timing_results)
    with (output/'THRESHOLDS.jsonl.gz').open('wb') as raw, gzip.GzipFile(
            fileobj=raw,mode='wb',filename='',mtime=0) as f:
        for item in certificates:
            f.write((json.dumps(item,sort_keys=True,default=str)+'\n').encode())
    dump(output/'FRONTIERS.json',frontiers)
    dump(output/'SUMMARY.json',summary)
    dump(output/'CHECKS.json',dict(source_hashes_verified=True,baseline_labels_reconciled=True,
        saved_admissions_checked=source_jobs,exact_threshold_witnesses=threshold_checks,
        grid_classifications_checked=grid_checks,energy_grid_cells=len(cases)*len(P_GRID)**2,
        source_decimal_reconstruction_absolute_tolerance=str(TOL),
        threshold_classification_tolerance='0; exact rational arithmetic',
        deployment_gate=False,new_empirical_gate=False))
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=BASE.parent/'2026-10-11-measured-serving')
    parser.add_argument('--output',type=Path,required=True,help='A new, nonexistent directory')
    args=parser.parse_args()
    result=run(args.source,args.output)
    print(json.dumps({'cases':result['cases'],'output':str(args.output)}))
