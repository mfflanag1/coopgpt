"""Zero-CPU re-derivation of the EVENT-7 position analysis, plus the k-strata
tables for the clean gate.  Reads only completed checkpoint files.

The clean gate ran 10 shards, each writing its rows in completion order to
gate32_<sh>.json.  'Position within the shard' is the index in that file, which
is also the order the solves were performed in that process -- so if accumulated
z3/heap state degrades later solves, unknown% should RISE with position.
"""
import glob, json, collections

rows = {}
for f in sorted(glob.glob('gate32_[0-9]*.json')):
    sh = f.split('_')[1].split('.')[0]
    rows[sh] = json.load(open(f))

allr = [r for v in rows.values() for r in v]
print(f"clean gate: {len(allr)} configurations across {len(rows)} shards")
tal = collections.Counter(r['res'] for r in allr)
print(f"  tally {dict(tal)}")

print("\nPOSITION-WITHIN-SHARD (the EVENT-7 test):")
bypos = collections.defaultdict(list)
for v in rows.values():
    for i, r in enumerate(v):
        bypos[i].append(r)
for i in sorted(bypos):
    g = bypos[i]
    u = sum(1 for r in g if r['res'] == 'unknown')
    med = sorted(r['s'] for r in g if r['res'] == 'unsat')
    print(f"  position {i}: n={len(g):2d}  unknown {u}/{len(g)} = {100*u/len(g):.0f}%"
          f"   median unsat {med[len(med)//2] if med else float('nan'):.1f}s")

print("\nK-STRATIFICATION (Lmin stratum count):")
byk = collections.defaultdict(list)
for r in allr:
    byk[len(r['lmin'])].append(r)
for k in sorted(byk):
    g = byk[k]
    u = sum(1 for r in g if r['res'] == 'unknown')
    med = sorted(r['s'] for r in g if r['res'] == 'unsat')
    print(f"  k={k}: n={len(g):2d}  unsat {len(g)-u}  unknown {u}  ({100*u/len(g):.0f}%)"
          f"   median unsat {med[len(med)//2] if med else float('nan'):.1f}s")

print("\nLMAX-STRATIFICATION:")
byl = collections.defaultdict(list)
for r in allr:
    byl[len(r['lmax'])].append(r)
for k in sorted(byl):
    g = byl[k]
    u = sum(1 for r in g if r['res'] == 'unknown')
    print(f"  b={k}: n={len(g):2d}  unknown {u}  ({100*u/len(g):.0f}%)")

print("\nCONFOUND CHECK -- is position confounded with k?")
for i in sorted(bypos):
    ks = [len(r['lmin']) for r in bypos[i]]
    print(f"  position {i}: mean k = {sum(ks)/len(ks):.2f}   ks={sorted(ks)}")

print("\nSOLVE-TIME DISTRIBUTION of the 32 decided:")
ts = sorted(r['s'] for r in allr if r['res'] != 'unknown')
print(f"  min {ts[0]}  q1 {ts[len(ts)//4]}  median {ts[len(ts)//2]}"
      f"  q3 {ts[3*len(ts)//4]}  max {ts[-1]}")

print("\nISOLATION EVIDENCE IN HAND (fresh-process re-runs of gate unknowns):")
for f in sorted(glob.glob('iso28_*.json')):
    for r in json.load(open(f)):
        print(f"  [{f}] gate {r['res']} {r['s']}s -> ISOLATED-FRESH {r['iso']}"
              f" {r['iso_s']}s   lmin={r['lmin']} lmax={r['lmax']}  k={len(r['lmin'])}")
