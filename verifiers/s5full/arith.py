"""A purely arithmetic upper bound on the ratio, from A3 alone.

Let x = Lmin, z = Lmax, T = v(N), mu = min x, M = max z.  Theorem
thm:n5closed (A3) says mu = lambda and M = nu, and both are ATTAINED:

  nu = M attained at S0:  v(S0) = M|S0|.  x in Core gives
        x(S0) >= v(S0) = M|S0|.                                    (N1)
  lambda = mu attained at S1:  f(S1) = mu|S1|.  z in Core gives
        v(N\\S1) <= z(N\\S1) = T - z(S1), so
        mu|S1| = f(S1) = T - v(N\\S1) >= z(S1).                     (N2)

(N1) and (N2) involve NO game data -- only the two allocation vectors.  So

    rho(v) = ||x - z||_1 / T  <=  max { ||x-z||_1 : x,z >= 0, x(N)=z(N)=T,
                                        x_i >= mu, z_i <= M,
                                        exists S0 with x(S0) >= M|S0|,
                                        exists S1 with z(S1) <= mu|S1| } / T.

The right-hand side is computed exactly here: normalise T = 1, enumerate the
pair (S0,S1) and the sign pattern of x - z (||.||_1 is convex, so its maximum
over a polytope is attained at a vertex and fixing the sign pattern linearises
it), and solve each LP exactly.  mu and M are free variables: the maximiser
automatically drives them to min x and max z, because (N1) is easier for
smaller M and (N2) easier for larger mu.
"""
from __future__ import annotations
import itertools, json, sys
from fractions import Fraction as F
import z3

def run(n):
    FULL = (1 << n) - 1
    best = (F(0), None)
    for S0 in range(1, FULL + 1):
        for S1 in range(1, FULL + 1):
            for sgn in itertools.product((1, -1), repeat=n):
                x = [z3.Real(f"x{i}") for i in range(n)]
                z = [z3.Real(f"z{i}") for i in range(n)]
                mu, M = z3.Real("mu"), z3.Real("M")
                o = z3.Optimize()
                for i in range(n):
                    o.add(x[i] >= 0, z[i] >= 0)
                    o.add(x[i] >= mu, z[i] <= M)
                    o.add(sgn[i] * (x[i] - z[i]) >= 0)
                o.add(z3.Sum(x) == 1, z3.Sum(z) == 1)
                s0 = [i for i in range(n) if S0 >> i & 1]
                s1 = [i for i in range(n) if S1 >> i & 1]
                o.add(z3.Sum([x[i] for i in s0]) >= M * len(s0))
                o.add(z3.Sum([z[i] for i in s1]) <= mu * len(s1))
                h = o.maximize(z3.Sum([sgn[i] * (x[i] - z[i]) for i in range(n)]))
                if o.check() != z3.sat:
                    continue
                up = o.upper(h)
                if z3.is_algebraic_value(up) or str(up) == "oo":
                    val = None
                else:
                    e = z3.simplify(up)
                    val = (F(e.as_long()) if z3.is_int_value(e)
                           else F(e.numerator_as_long(), e.denominator_as_long()))
                if val is not None and val > best[0]:
                    m = o.model()
                    best = (val, {"S0": s0, "S1": s1,
                                  "x": [str(m.eval(x[i], model_completion=True)) for i in range(n)],
                                  "z": [str(m.eval(z[i], model_completion=True)) for i in range(n)]})
    return best

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    val, wit = run(n)
    print(f"n={n}: max ||x-z||_1 / T subject to (N1)+(N2) = {val}")
    print("  attained at", json.dumps(wit))
    json.dump({"n": n, "bound": str(val), "witness": wit},
              open(f"/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/"
                   f"scratchpad/sel/s5full/arith_n{n}.json", "w"), indent=1)
