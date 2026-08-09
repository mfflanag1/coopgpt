"""Task #32: the machine-checked coverage audit for n=6 -- the executable form
of VERDICT32.txt section 1(e).

Verifies, without trusting any tally printed elsewhere, that:
  1. the universe is exactly the set of (composition, composition, table)
     triples, and its size is 37,277;
  2. the compositions count is 2^(n-1), so none is missing;
  3. every configuration lands in exactly one bucket -- L1''-excluded, killed by
     the hand net, Stage B (populated), Stage C (remainder) -- with no gap and
     no overlap;
  4. the Stage-B population is exactly the set of configurations the harvests
     realize, and every one of them survived the hand net (nothing real was
     excluded).
Exit status is nonzero on any mismatch.
"""
import json, glob, sys
sys.path.insert(0,'.')
import nsix
N=6
def K(r,c,t): return (tuple(r),tuple(c),json.dumps(t))
bad=[]
comps=nsix.compositions(N)
if len(comps)!=2**(N-1): bad.append(f"compositions {len(comps)} != {2**(N-1)}")
universe={K(r,c,t) for r in comps for c in comps for t in nsix.tables(r,c)}
print(f"universe {len(universe)}")
if len(universe)!=37277: bad.append(f"universe {len(universe)} != 37277")
l1={k for k in universe if k[1][-1]==1}
tri=json.load(open('triage32.json'))
surv={K(*x) for x in tri['survivors']}
killed=universe-l1-surv
print(f"  L1''-excluded {len(l1)}  killed {len(killed)}  survivors {len(surv)}")
if not surv <= (universe-l1): bad.append("survivors not inside the post-L1'' set")
pop={K(*x[:3]) for x in json.load(open('stageB.json'))['stageB']}
print(f"  Stage B (populated) {len(pop)}   Stage C (remainder) {len(surv-pop)}")
if not pop <= surv: bad.append(f"{len(pop-surv)} populated configurations are NOT survivors")
# harvest realizes exactly the Stage-B set
obs=set()
for f in glob.glob('harvest6_60*.json'):
    for r in json.load(open(f))['records']:
        obs.add(K(r['lmin_shape'], r['lmax_shape'], r['tbl']))
print(f"  harvest-realized {len(obs)}")
if obs!=pop: bad.append(f"harvest set != Stage-B set (sym diff {len(obs^pop)})")
if obs-surv: bad.append(f"{len(obs-surv)} REALIZED configurations were excluded by the net")
parts=[l1,killed,pop,surv-pop]
tot=sum(len(p) for p in parts); union=set().union(*parts)
print(f"  buckets sum {tot}, union {len(union)}, overlap {tot-len(union)}")
if union!=universe: bad.append("buckets do not cover the universe")
if tot!=len(union): bad.append(f"buckets overlap by {tot-len(union)}")
json.dump({"universe":len(universe),"L1_excluded":len(l1),"hand_killed":len(killed),
           "stageB":len(pop),"stageC":len(surv-pop),"problems":bad},
          open("coverage32.json","w"), indent=1)
if bad:
    print("COVERAGE AUDIT FAILED:"); [print("  -",b) for b in bad]; sys.exit(1)
print("COVERAGE AUDIT PASSED: 37,277 partitioned exactly once; nothing realized was excluded.")
