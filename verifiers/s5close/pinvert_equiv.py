"""Three-way equivalence check for the floor pinning-dual vertices.

The brief said pinvert.py was lost; it is not -- it is archived at
verifiers/o2/pinvert.py.  That script hardcodes the pinned set as a module
constant (L = [0,1,2]), so this task still needed a version taking the pinned
set as a PARAMETER; r22/pinvert.py is that generalization.  This script checks
that the generalization is faithful, and that the stored fixture is not stale,
by comparing all three sources of the same 354 vertices:

  1. the enumeration inside verifiers/o2/pinvert.py, re-executed here (its own
     main() writes to a scratchpad path that no longer exists, so the loop is
     driven directly using that module's solve() and constants);
  2. verifiers/o2/pinverts.json, the stored fixture r22/pinvert.py regresses
     against;
  3. r22/pinvert.py's parametric pinverts([0,1,2]).

All three must be equal as sorted lists of (alpha, ((A, beta_A), ...)).
"""
from __future__ import annotations
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as F

HERE = sys.path[0]
sys.path.insert(0, HERE)
REPO = ("/private/tmp/claude-501/-Users-maxf/"
        "f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/wt/coopgames")


def archived():
    spec = importlib.util.spec_from_file_location(
        "o2pin", f"{REPO}/verifiers/o2/pinvert.py")
    o2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(o2)
    rhs = [1 if k in o2.L else 0 for k in range(o2.N)]
    verts = set()
    for k in range(0, 5):
        for W in itertools.combinations(o2.PROPER, k):
            for I in itertools.combinations(range(o2.N), k + 1):
                A = [[1] + [1 if S >> i & 1 else 0 for S in W] for i in I]
                sol = o2.solve(A, [rhs[i] for i in I])
                if sol is None:
                    continue
                al, be = sol[0], sol[1:]
                if any(x <= 0 for x in be):
                    continue
                if all(al + sum(be[j] for j, S in enumerate(W) if S >> kk & 1)
                       >= rhs[kk] for kk in range(o2.N)):
                    verts.add((al, tuple(sorted((S, be[j])
                                                for j, S in enumerate(W)))))
    return sorted(verts)


def main():
    a = archived()
    fix = sorted((F(al), tuple((int(S), F(x)) for S, x in be))
                 for al, be in json.load(open(f"{HERE}/lib/pinverts_L012.json")))
    import pinvert
    mine = [(al, tuple(be)) for al, be in pinvert.pinverts([0, 1, 2])]
    print(f"  archived verifiers/o2/pinvert.py : {len(a)}")
    print(f"  stored pinverts.json fixture     : {len(fix)}")
    print(f"  r22 parametric pinverts([0,1,2]) : {len(mine)}")
    ok = (a == fix == mine) and len(a) == 354
    print("THREE-WAY EQUIVALENCE CONFIRMED (354 vertices)" if ok
          else "MISMATCH")
    json.dump({"archived": len(a), "fixture": len(fix), "parametric": len(mine),
               "all_identical": ok}, open(f"{HERE}/pinvert_equiv.json", "w"),
              indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
