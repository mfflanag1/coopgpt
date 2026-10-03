#!/usr/bin/env python3
"""Freeze a bounded deterministic support campaign without running an optimizer.

Inventory novelty is relative to recoverable retained artifacts, not a claim that
unrecorded numerical search states have never been visited. All validity checks
use explicit exceptions, so python -O does not disable the negative controls.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import platform
import sys
import zipfile
import networkx as nx

SECTORS = tuple(permutations(range(3)))
SUPPORT_KEYS = {'P', 'partial_matching', 'matching', 'dual_matching', 'dual', 'packing'}
ROOT_REL = Path('structural_classification_2026-09-06/sharp_subsidy')


def digest(data):
    return sha256(data).hexdigest()


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(m, P):
    require(type(m) is int and m > 0, 'invalid m')
    require(isinstance(P, (list, tuple)) and len(P) > 0, 'empty P')
    require(all(isinstance(t, (list, tuple)) and len(t) == 3 for t in P), 'not triples')
    require(all(type(j) is int and 0 <= j < m for t in P for j in t), 'invalid label')
    require(all(len({t[s] for t in P}) == len(P) for s in range(3)), 'P is not player-disjoint')


def support(value):
    if not isinstance(value, list) or not value:
        return None, None
    if len(value) == 3 and all(type(j) is int for j in value):
        return [value], 'single_triplet'
    if all(isinstance(t, list) and len(t) == 3 and all(type(j) is int for j in t) for t in value):
        return value, 'triplet_list'
    if all(isinstance(t, list) and len(t) == 2 and isinstance(t[0], list) and len(t[0]) == 3 and all(type(j) is int for j in t[0]) for t in value):
        try:
            require(all(Fraction(str(t[1])) >= 0 for t in value), 'negative packing mass')
            return [t[0] for t in value if Fraction(str(t[1])) > 0], 'positive_weighted_support'
        except (ValueError, ZeroDivisionError):
            return None, None
    return None, None


def infer_m(obj, inherited, location):
    for key in ['m', 'market_size']:
        if type(obj.get(key)) is int and obj[key] > 0:
            return (obj[key], key)
    H = obj.get('H')
    if isinstance(H, list) and H and len(H) % 3 == 0 and not isinstance(H[0], (list, dict)):
        return (len(H) // 3, 'len(H)/3')
    for key in ['AB', 'AC', 'BC', 'A', 'B', 'C']:
        a = obj.get(key)
        if isinstance(a, list) and a and all(isinstance(row, list) and len(row) == len(a) for row in a):
            return (len(a), 'matrix:' + key)
    if obj.get('scope') == 'three-label sparse module with optimal diagonal; not sharp global subsidy':
        return (3, 'explicit three-label scope field')
    return inherited


def inventory(source):
    occurrences, skipped, sources = [], [], []
    def visit(obj, context, location, pointer):
        if isinstance(obj, dict):
            context = infer_m(obj, context, location)
            for key in sorted(obj):
                value = obj[key]
                at = pointer + '.' + key
                # Deletion rows are fractional auxiliary objects, not examined P supports.
                if key in {'packings', 'deletion_packings', 'deletion_matchings'}:
                    continue
                if key in SUPPORT_KEYS:
                    P, schema = support(value)
                    if P is not None:
                        if context is None:
                            skipped.append({'source': location, 'pointer': at, 'reason': 'market size not inferable from accepted schema'})
                        else:
                            m, method = context
                            try:
                                validate(m, P)
                            except ValueError as e:
                                skipped.append({'source': location, 'pointer': at, 'reason': str(e)})
                            else:
                                occurrences.append({'m': m, 'P': sorted(P), 'source': location, 'pointer': at, 'schema': schema, 'm_provenance': method})
                if isinstance(value, (dict, list)):
                    visit(value, context, location, at)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    visit(value, context, location, pointer + '[' + str(i) + ']')
    def parse(blob, location):
        try:
            text = blob.decode('utf-8')
        except UnicodeDecodeError:
            return
        parsed = 0
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            for line_no, line in enumerate(text.splitlines(), 1):
                line = line.strip()
                if not line.startswith(('{', '[')):
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                visit(obj, None, location, f'line:{line_no}')
                parsed += 1
        else:
            visit(obj, None, location, '$')
            parsed = 1
        sources.append({'source': location, 'sha256': digest(blob), 'bytes': len(blob), 'parsed_json_values': parsed})
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        relative = str(path.relative_to(source))
        if path.suffix.lower() in {'.json', '.jsonl', '.log', '.txt', '.out'}:
            parse(path.read_bytes(), relative)
        elif path.suffix.lower() == '.zip':
            blob = path.read_bytes()
            sources.append({'source': relative, 'sha256': digest(blob), 'bytes': len(blob), 'kind': 'zip_archive'})
            with zipfile.ZipFile(path) as z:
                for member in sorted(z.namelist()):
                    if Path(member).suffix.lower() in {'.json', '.jsonl', '.log', '.txt', '.out'}:
                        parse(z.read(member), relative + '!' + member)
    unique = {}
    for item in occurrences:
        key = (item['m'], tuple(map(tuple, item['P'])))
        if key not in unique:
            unique[key] = {'m': item['m'], 'P': item['P'], 'provenance': []}
        unique[key]['provenance'].append({k: v for k, v in item.items() if k not in {'m', 'P'}})
    return {'sources': sources, 'occurrences': len(occurrences), 'supports': list(unique.values()), 'skipped': skipped}


def graph(m, P, sectors=(0, 1, 2)):
    g = nx.MultiGraph()
    g.add_nodes_from((('label', j), {'kind': 'label'}) for j in range(m))
    g.add_nodes_from((('team', i), {'kind': 'team'}) for i in range(len(P)))
    for i, team in enumerate(P):
        for s in range(3):
            g.add_edge(('team', i), ('label', team[s]), sector=sectors[s])
    return g


def stats(m, P):
    validate(m, P)
    G = graph(m, P)
    used = [{t[s] for t in P} for s in range(3)]
    degrees = [sum(j in u for u in used) for j in range(m)]
    L = [sum(degrees[j] == 1 and j in used[s] for j in range(m)) for s in range(3)]
    N = [sum(degrees[j] == 2 and j not in used[s] for j in range(m)) for s in range(3)]
    h = m - len(P)
    margins = [N[s] * min(L[s], h-1) + h-N[s] - L[s]*(h-2) for s in range(3)]
    components = nx.number_connected_components(G)
    return {'m': m, 'r': len(P), 'h': h, 'components': components, 'cycle_rank': 3*len(P)-m-len(P)+components,
            'degree_counts': {str(k): degrees.count(k) for k in range(4)},
            'degree_three_labels': degrees.count(3), 'repeated_label_teams': sum(len(set(t)) < 3 for t in P),
            'L': L, 'N': N, 'uniform_margins_rhs_minus_lhs': margins,
            'uniform_safe': min(degrees) >= 1 and h >= 2 and all(x >= 0 for x in margins)}


def signature(m, P):
    s = stats(m, P)
    return (m, len(P), tuple(s['degree_counts'].values()), s['repeated_label_teams'])


def equivalent(m, P, n, Q):
    if signature(m, P) != signature(n, Q):
        return False
    g = graph(m, P)
    for sigma in SECTORS:
        if nx.is_isomorphic(g, graph(n, Q, sigma),
                            node_match=nx.algorithms.isomorphism.categorical_node_match('kind', None),
                            edge_match=nx.algorithms.isomorphism.categorical_multiedge_match('sector', None)):
            return True
    return False


def canonical(m, P):
    """Exact lex minimum over row/sector orders and first-occurrence label maps.

    Missing labels contribute only m. Intended only for r<=7 selected supports;
    the inventory uses exact VF2 instead of factorial expansion for larger r.
    """
    require(len(P) <= 7, 'canonical enumeration bounded to r<=7')
    best = None
    for sigma in SECTORS:
        transformed = [tuple(t[s] for s in sigma) for t in P]
        for rows in permutations(transformed):
            relabel, flat = {}, []
            for row in rows:
                for j in row:
                    if j not in relabel:
                        relabel[j] = len(relabel)
                    flat.append(relabel[j])
            key = tuple(flat)
            if best is None or key < best:
                best = key
    return {'m': m, 'P': [list(best[k:k+3]) for k in range(0, len(best), 3)]}


def safe_reasons(m, P):
    s = stats(m, P)
    reasons = []
    if s['h'] < 2:
        reasons.append('elementary_h_below_2')
    if s['components'] == 1 and s['cycle_rank'] == 0 and s['degree_three_labels'] <= 1:
        reasons.append('ONE_HUB_THEOREM')
    if s['degree_counts']['0'] == 0 and s['degree_counts']['1'] <= 3:
        reasons.append('LEAF_AND_DELETION_leaf_count_at_most_3')
    if s['uniform_safe']:
        reasons.append('UNIFORM_TEMPLATE_C_s')
    # Every published leaf-dilation family here is an incidence tree.
    # Reject all trees conservatively; the present size window is cyclic anyway.
    if s['cycle_rank'] == 0:
        reasons.append('conservative_tree_exclusion_including_LEAF_DILATION')
    return reasons


class KnownIndex:
    def __init__(self, records):
        self.by_signature = defaultdict(list)
        for rec in records:
            self.by_signature[signature(rec['m'], rec['P'])].append(rec)
    def match(self, m, P):
        for rec in self.by_signature.get(signature(m, P), []):
            if equivalent(m, P, rec['m'], rec['P']):
                return rec
        return None


def transformed(m, P):
    return [[m-1-t[2], m-1-t[0], m-1-t[1]] for t in reversed(P)]


def self_test(inv, source):
    index = KnownIndex(inv['supports'])
    frontier = json.loads((source/'CYCLIC_FRONTIER_CERTIFICATES.json').read_text())
    require(len(frontier) == 34, 'frontier record count changed; audit needed')
    count = 0
    for item in frontier:
        p = item['pattern']
        for Q in [p['P'], transformed(p['m'], p['P'])]:
            require(index.match(p['m'], Q) is not None, 'known frontier support escaped exclusion')
            count += 1
    # Parallel sector incidences are retained and are not equivalent to an ordinary tree.
    require(equivalent(3, [[0,0,1]], 3, [[2,1,2]]), 'repeated incidence equivalence failed')
    require(not equivalent(3, [[0,0,1]], 3, [[0,1,2]]), 'parallel edges collapsed')
    negative_controls = []
    for name, m, P in [('player_disjointness',3,[[0,1,2],[0,2,1]]),('label_range',3,[[0,1,3]])]:
        try:
            validate(m,P)
        except ValueError:
            negative_controls.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    require(stats(4, [[0,1,2]])['components'] == 2, 'isolated label not counted')
    require(safe_reasons(3, [[0,1,2]]), 'safe calibration escaped')
    for item in frontier[:8]:
        require(stats(item['pattern']['m'],item['pattern']['P'])['uniform_safe'], 'uniform safe calibration failed')
    return {'frontier_records':34,'known_and_transformed_rejections':count,'negative_controls':negative_controls,
            'parallel_incidence_checks':2,'uniform_frontier_safe_controls':8, 'optimized_python': not __debug__, 'status':'PASS'}


def mutations(m, P):
    # Each mutation changes actual teams; no market coefficients are evaluated.
    used = [{t[s] for t in P} for s in range(3)]
    for s in range(3):
        for a in range(len(P)):
            for b in range(a+1,len(P)):
                Q = [t[:] for t in P]
                Q[a][s],Q[b][s] = Q[b][s],Q[a][s]
                yield Q, {'kind':'within_sector_swap','sector':s,'rows':[a,b]}
        for a in range(len(P)):
            for new in sorted(set(range(m))-used[s]):
                Q = [t[:] for t in P]
                old = Q[a][s]
                Q[a][s] = new
                yield Q, {'kind':'reconnection','sector':s,'row':a,'old_label':old,'new_label':new}


def select(inv):
    seeds = [x for x in inv['supports'] if 9 <= x['m'] <= 12 and len(x['P']) in [6,7]
             and stats(x['m'],x['P'])['components'] == 1]
    seeds.sort(key=lambda x:(x['m'],len(x['P']),x['P']))
    index = KnownIndex(inv['supports'])
    pool, visited, counters = [], set(), Counter()
    # Deterministic breadth-first exploration with an explicit finite node cap.
    # Inspect all first-generation children and a bounded second generation.
    queue = [(x['m'],x['P'],k,[]) for k,x in enumerate(seeds)]
    for m,P,_,_ in queue:
        visited.add((m,tuple(map(tuple,sorted(P)))))
    cursor = 0
    while cursor < len(queue) and cursor < 500:
        m,P,seed_id,path = queue[cursor]
        cursor += 1
        for Q,op in mutations(m,P):
            key=(m,tuple(map(tuple,sorted(Q))))
            if key in visited:
                continue
            visited.add(key)
            counters['mutations_seen'] += 1
            s=stats(m,Q)
            if s['components'] != 1:
                counters['disconnected'] += 1
                continue
            nextpath = path + [op]
            if len(nextpath) < 2:
                queue.append((m,Q,seed_id,nextpath))
            reasons=safe_reasons(m,Q)
            if reasons:
                counters['safe'] += 1
                continue
            if index.match(m,Q) is not None:
                counters['known_equivalent'] += 1
                continue
            # Retain only an initial bounded pool, then rank without objective data.
            if any(equivalent(m,Q,r['m'],r['P']) for r in pool):
                counters['pool_equivalent'] += 1
                continue
            pool.append({'m':m,'P':Q,'statistics':s,'seed_inventory_index':inv['supports'].index(seeds[seed_id]),'mutation_path':nextpath})
            if len(pool) >= 80:
                break
        if len(pool) >= 80:
            break
    # Bounded augmentation adds one actual team using sectorwise-unused players.
    # This changes r from 6 to 7, hence m=12 cycle rank from 1 to 3.
    augmentation_pool = []
    augmentation_attempts = 0
    augmentation_seeds = [x for x in seeds+pool if x['m'] == 12 and len(x['P']) == 6]
    augmentation_choices = []
    for seed in augmentation_seeds:
        unused = [sorted(set(range(12)) - {t[s] for t in seed['P']}) for s in range(3)]
        degrees = Counter(j for t in seed['P'] for j in t)
        # Topological priority: fill degree-two labels before other labels.
        choices = sorted(product(*unused),key=lambda t:(-sum(degrees[j]==2 for j in set(t)),t))
        augmentation_choices.append(choices)
    for rank in range(216):
        for seed, choices in zip(augmentation_seeds,augmentation_choices):
            if augmentation_attempts >= 500:
                break
            team=choices[rank]
            augmentation_attempts += 1
            Q = seed['P'] + [list(team)]
            if safe_reasons(12,Q):
                counters['augmentation_safe'] += 1
                continue
            if index.match(12,Q) is not None:
                counters['augmentation_known_equivalent'] += 1
                continue
            if any(equivalent(12,Q,12,x['P']) for x in augmentation_pool):
                counters['augmentation_pool_equivalent'] += 1
                continue
            parent_path = seed.get('mutation_path',[])
            parent_index = seed.get('seed_inventory_index')
            if parent_index is None:
                parent_index=inv['supports'].index(seed)
            augmentation_pool.append({'m':12,'P':Q,'statistics':stats(12,Q),
                'seed_inventory_index':parent_index,
                'mutation_path':parent_path+[{'kind':'unused_player_team_augmentation','team':list(team)}]})
        if augmentation_attempts >= 500:
            break
    pool.extend(augmentation_pool)
    # Prefer shape diversity, alternating ordinary/repeated-label cases when present.
    # Ranking and held-out positions are fixed here, before any LP is run.
    def shape(r):
        s=r['statistics']
        return (r['m'],len(r['P']),s['degree_three_labels'],tuple(sorted(s['L'])),tuple(sorted(s['N'])),s['repeated_label_teams'])
    pool.sort(key=lambda r:(len(r['mutation_path']),r['m'],r['statistics']['repeated_label_teams'],r['P']))
    chosen, shapes = [], set()
    # With two available augmented supports: 4 r=6 and 2 r=7, with one of each
    # assigned to the two held-out slots. Otherwise use the original r=6 pool.
    requested_r = [6,6,6,7,6,7] if len(augmentation_pool) >= 2 else [6]*6
    for r_target,repeated in zip(requested_r,[False,True,False,True,True,False]):
        base=[x for x in pool if len(x['P'])==r_target and x not in chosen]
        eligible=[x for x in base if shape(x) not in shapes and bool(x['statistics']['repeated_label_teams'])==repeated]
        if not eligible:
            eligible=[x for x in base if shape(x) not in shapes]
        if not eligible:
            eligible=base
        if not eligible:
            break
        pick=eligible[0]
        chosen.append(pick)
        shapes.add(shape(pick))
    for i,rec in enumerate(chosen,1):
        rec['id']=f'CW-{i:02d}'
        rec['priority']=i
        rec['held_out']=i >= 5
        rec['canonical']=canonical(rec['m'],rec['P'])
        rec['canonical_sha256']=digest(encoded(rec['canonical']))
        rec['novelty']='not equivalent to any support recoverable from frozen retained-artifact inventory'
        require(index.match(rec['m'],rec['P']) is None,'selected known support')
        require(not safe_reasons(rec['m'],rec['P']),'selected safe support')
        require(rec['statistics']['components']==1,'selected disconnected support')
        require(rec['statistics']['cycle_rank']>=1 or rec['statistics']['degree_three_labels']>=2,'selected outside topology scope')
    require(len({r['canonical_sha256'] for r in chosen})==len(chosen),'duplicate selected canonical')
    for rec in chosen:
        require(canonical(rec['m'], transformed(rec['m'],rec['P'])) == rec['canonical'], 'canonical symmetry test failed')
        require(equivalent(rec['m'],rec['P'],rec['m'],rec['canonical']['P']), 'canonical and VF2 disagree')
    return chosen,{'seeds':len(seeds),'queue_nodes_processed':cursor,'pool_count':len(pool),'counters':dict(counters),'max_queue_nodes':500,'max_mutation_depth':2,'max_initial_pool_count':80,'augmentation_attempts':augmentation_attempts,'augmentation_survivors':len(augmentation_pool),'max_augmentation_attempts':500,'augmentation_priority':'round-robin retained seeds and initial pool; first maximize distinct degree-two labels filled, then lexicographic new team'}


def write_new(path,data):
    require(not path.exists(),'refusing to overwrite frozen artifact: '+str(path))
    path.write_bytes(data)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    source=args.repo/ROOT_REL
    inv=inventory(source)
    test=self_test(inv,source)
    if args.self_test and args.output is None:
        print(json.dumps({'inventory_occurrences':inv['occurrences'],'unique_labeled_supports':len(inv['supports']),'tests':test},indent=2))
        return
    require(args.output is not None,'--output required to freeze registry')
    chosen,generation=select(inv)
    test['selected_canonical_symmetry_checks'] = len(chosen)
    test['selected_canonical_VF2_agreement_checks'] = len(chosen)
    require(chosen,'no candidates found within bounded search')
    out=args.output
    out.mkdir(parents=True,exist_ok=True)
    inventory_data={'scope':str(ROOT_REL),'novelty_limit':'retained-artifact inventory only','sources':inv['sources'],'occurrence_count':inv['occurrences'],'unique_labeled_support_count':len(inv['supports']),'supports':inv['supports'],'skipped_support_fields':inv['skipped']}
    ibytes=json.dumps(inventory_data,indent=2,sort_keys=True).encode()+b'\n'
    safe_files=['LEAF_AND_DELETION.md','UNIFORM_TEMPLATE.md','ONE_HUB_THEOREM.md','LEAF_DILATION_THEOREM.md','CYCLIC_PATTERN_BOUNDS.md','CYCLIC_FRONTIER.md','REDUCTIONS.md']
    registry={'schema':'coopgpt-support-registry-v1','frozen_at_utc':datetime.now(timezone.utc).isoformat(),'optimization_run_during_generation':False,
              'inventory_sha256':digest(ibytes),'generator_sha256':digest(Path(__file__).read_bytes()),
              'environment':{'python':platform.python_version(),'networkx':nx.__version__},
              'equivalence':'simultaneous label permutation, P row permutation, global sector permutation; sector-coloured parallel incidence edges retained',
              'canonical_method':'lexicographic minimum after all P-row orders and six sector orders, with first-occurrence label renaming; m included',
              'priority_rule':'bounded BFS pool and 500 unused-player seventh-team augmentations; shortest mutation path, m, repeated-team count, labeled P; prefer four r6 and two r7 with one of each heldout if available; prefer unseen degree/sector-count shapes and alternate repeated-label cases',
              'held_out_rule':'priority 5 and 6 if present; frozen before optimization',
              'generation':generation,'tests':test,'safe_class_scope':{'implemented':['h<2','LEAF_AND_DELETION leaf count <=3 when all labels incident','UNIFORM_TEMPLATE C_s (including cyclic/repeated incidences)','all incidence trees conservatively (including one-hub and leaf-dilation families)','all recoverable previously examined fixed supports, irrespective of numerical status'],
              'not_claimed':'No complete classification of all safe cyclic supports; no exhaustive support census. Weight-specific ring/broken-ring theorems do not prove arbitrary-weight support safety.',
              'source_hashes':{f:digest((source/f).read_bytes()) for f in safe_files}},'supports':chosen}
    rbytes=json.dumps(registry,indent=2,sort_keys=True).encode()+b'\n'
    write_new(out/'retained_inventory.json',ibytes)
    write_new(out/'supports.json',rbytes)
    write_new(out/'supports.sha256',(digest(rbytes)+'  supports.json\n').encode())
    gap='''# Retained-history provenance limits\n\nThe frozen supports are not equivalent to any support recoverable from the frozen retained-artifact inventory. This is not an absolute never-tried claim. Earlier best-only numerical logs and alternating searches did not retain every intermediate support; absent states cannot be reconstructed. The plan's stronger “genuinely untested” requirement is therefore unresolved in that literal sense and must not be silently certified.\n\nThe scan recursively reads JSON, JSONL, parseable complete JSON logfile lines, and matching archive members under sharp_subsidy. It records source bytes and SHA-256 values, schema paths, and accepted market-size inference. It does not execute discovery scripts. Python-source-only parameterized support generators and truncated/non-JSON log fragments are outside extraction; nine ZIP containers are hashed even when they hold only scripts. The probe records carry H, so their size is reconstructed from len(H)/3. Auxiliary deletion packings are omitted; weighted dual/packing fields are retained only when their positive support is an actual player-disjoint matching. Skipped recognized support fields are listed in the inventory.\n\nAll 34 CYCLIC_FRONTIER records and transformed copies must be rejected by the exact sector-coloured multigraph isomorphism filter. Canonical forms for the selected supports are generated by a separate exhaustive row/sector permutation construction. Fixed safe patterns are rejected through the inventory, the at-most-three-leaves theorem and uniform-template count theorem are applied to cyclic and repeated-label supports, and all incidence trees are conservatively excluded. This does not establish completeness of the collection of proven safe classes.\n\nThe deterministic generator inspects a bounded BFS pool and 500 seventh-team augmentations and selects at most six supports. If two r=7 candidates survive, four r=6 and two r=7 supports are selected, with one of each held out. Neither LP objectives nor numerical feasibility results are used for candidate generation or ranking. The final two positions are held out before solves. Registry files refuse overwrite; any later change requires a new explicitly versioned registry and disclosure.\n'''
    write_new(out/'PROVENANCE_GAPS.md',gap.encode())
    print(json.dumps({'registry_sha256':digest(rbytes),'candidate_count':len(chosen),'inventory_occurrences':inv['occurrences'],'unique_labeled_supports':len(inv['supports']),'skipped':len(inv['skipped']),'generation':generation,'tests':test,'selected':[{k:r[k] for k in ['id','m','P','held_out','statistics']} for r in chosen]},indent=2))

if __name__=='__main__':
    main()
