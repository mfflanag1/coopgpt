# Pair-additive triple pilot — 2026-09-05

The player-additive `1/3` coordinate guarantee does **not** extend to all nonnegative pair-additive strict triple games with nonempty core. A nine-player example has `min_i Lmin_i/H_i = 5/18`. This finite counterexample does not decide whether some smaller positive dimension-independent guarantee survives, whether that fraction can tend to zero, or whether the `4/3` distance bound extends. No novelty claim is made.

## Contract and bounded search

There are three sectors of equal size `m`. Inputs are nonnegative integer matrices `A_ij,B_ik,C_jk`; every feasible productive team is a complete triple with weight `A_ij+B_ik+C_jk`. Pairs alone produce zero. The grand worth is the **integral** maximum disjoint-triple matching value. For these complete nonnegative arrays, a partial matching can be completed without loss, so exhaustive `(m!)^2` perfect-matching enumeration gives the same value. Core admission uses this integral total, nonnegative payoffs and every triple inequality. Sums of disjoint triple inequalities imply all coalition inequalities; the nominated exact checks additionally enumerate all coalition values independently by dynamic programming.

The screen computes both **complete** lexicographic selectors: ascending sorted leximin, and the lexicographic minimum of descending sorted payoffs. At each stage it fixes every coordinate forced on the optimum face, then continues. It also maximizes each player's payoff over the full core, defining `H_i`; zero ideals are omitted only from ratios, never from core constraints.

Seed: `20260905`. Planned maximum:192 instances at each of `m=2,3`. Four alternating input modes: binary matrices; dense entries0..6;35%-occupied entries1..9; player-additive arrays plus `m+1` random pair-entry increments1..4. Discovery stops at the first exactly confirmed violation. No `m=4` search was run.

Completed random instances:192 at `m=2`,78 at `m=3`. Two additional player-additive calibrations were run. Including calibrations, counts were:

| m | Nonempty core, float screen | Empty core, float screen | Zero total |
|---|---:|---:|---:|
|2|191|0|2|
|3|78|1|0|

The empty-core classification is a screening outcome, not a separately certified example. Null outcomes for the sampled `m=2` instances are not a theorem. The first `m=3` candidate was dense case77: total39, coordinate fraction47/144, distance16/117. Its full exact data are in `pilot_summary.json` and all screened inputs/stages are in `screen_records.json`.

## Reduced exact witness

Four deterministic greedy entry-reduction passes made129 trial evaluations, preserving a strict coordinate-bound violation. Entry mass fell from89 to12. This is a bounded simplification, **not** a global minimality claim, and the last pass still accepted reductions. Exact recertification was performed on the final reduced input.

```
A = [[0,0,0], [2,0,1], [0,1,0]]
B = [[0,0,1], [1,0,0], [0,0,0]]
C = [[0,1,0], [3,0,0], [2,0,0]]
```

Names are `(a,b,c ; d,e,f ; g,h,i)` in sector order. The integral total is8. The matching `(a,f,i), (b,d,h), (c,e,g)` has weights1,3,4. A feasible core allocation below has total8, so it also certifies that no fractional or integral packing exceeds8.

```
x=Lmin = (1/3,4/3,5/6 ; 5/6,5/6,1/3 ; 7/3,5/6,1/3)
z=Lmax = (0,3/2,1     ; 1,3/2,1     ; 3/2,1/2,0)
H      = (1,3,2       ; 3,3,1       ; 4,2,1)
x/H    = (1/3,4/9,5/12; 5/18,5/18,1/3;7/12,5/12,1/3)
rho    = ||x-z||_1 / 8 = 11/24
```

Both `d` and `e` violate the proposed1/3 guarantee. In particular `x_d=5/6`, `H_d=3`, and an ideal-attaining point is

```
y = (0,0,0 ; 3,1,1 ; 3,0,0).
```

Every nonnegative/triple inequality for these points was checked in exact rational arithmetic. All nine ideals have primal attainment points and rational upper-bound duals in `rational_certificates.json`.

## Readable selector mechanism

In **every** core allocation, efficiency and the displayed optimal matching force

```
a+f+i = 1,    b+d+h = 3,    c+e+g = 4.
```

For leximin, the first equation bounds the smallest payoff by1/3. At an optimum attaining this bound, `a=f=i=1/3`. The additional triple inequality `b+f+g>=4` implies `b+g>=11/3`. Combining the other matching equalities gives `c+d+e+h<=10/3`; the next ascending level is therefore at most5/6. The displayed `x` attains this level with all four coordinates equal, and the matching equalities then uniquely force `b=4/3,g=7/3`. Thus these first two substantive stages uniquely identify the **full** leximin point.

For descending lexicographic minimization, `f<=1` and `b+f+g>=4` imply `b+g>=3`, so the maximum is at least3/2. At ceiling3/2 these relations force `b=g=3/2,f=1,a=i=0`. The triple inequality `a+e+g>=3` forces `e=3/2`; the matching equation forces `c=1`. Finally `d+h=3/2` and `a+d+i>=1` give `d>=1`, so the next descending stage fixes `d=1,h=1/2`. This proves the complete displayed `z`.

Active triple inequalities at `x`, in one-based sector indices, are `(1,3,3),(2,1,2),(2,3,1),(3,2,1)`. At `z` additionally `(1,1,3),(1,2,1)` are active. Nonnegativity at `a,i` is active only at `z`.

The local mechanism is a cross-matching triple which couples the residual budgets of two matched blocks after the first small matched block fixes three coordinates. This is evidence of a concrete amplification mechanism worth understanding. The pilot establishes **no** scalable gadget, infinite family or zero-limit fraction; repeating disjoint copies would merely repeat the same fraction.

## Calibrations and exact verification

Player-additive controls for `m=2,3` were embedded into pair matrices using `A_ij=alpha_i+beta_j`, `B_ik=gamma_k`, `C=0`, for sectors `([2,1,...,1],[1,0,...,0],[0,...,0])`. Exact output reproduced coordinate fraction1/3 and distance `4m/[3(m+2)]`.

The primary-source control supplied by the literature lane, Atay–Núñez2019 Example5, was adapted to the strict-triples contract:

```
A=[[4,4],[5,0]], B=[[2,0],[1,5]], C=[[4,3],[0,9]]
T=24
x=(10/3,13/3 ; 10/3,13/3 ; 10/3,16/3)
z=(11/3,14/3 ; 11/3,14/3 ; 8/3,14/3)
H=(10,11 ; 10,11 ; 10,14)
min x_i/H_i=1/3, rho=1/9.
```

These are our strict-core calculations, not an attribution of these selectors to that source. See `published_control.json`. The known gap between bilateral optima and the jointly compatible triple matching remains present; the screen did not assume decomposability into three simultaneously optimal bilateral matchings.

The exact selector generator was reused from the frozen assignment package's `exact_three.py`; its absolute path and SHA256 are recorded in `pilot_summary.json`. Exact results were independently checked using insertion-sort SMT expressions: strict sorted improvement is UNSAT for each entire selector; each ideal's strict exceedance is UNSAT and equality is SAT. Both counterexamples and the published control used the full coalition-value encoding.

For the reduced witness,35 additional rational primal/dual identities certify9 ideals,8 stage levels and18 pinned-coordinate bounds. LP discovery used SciPy, but every multiplier sign, coefficient identity, primal constraint and matching objective equality was rechecked with `fractions.Fraction`. The saved artifact can be replayed using **only the Python standard library**, without Z3 or SciPy.

## Reproduction

Working directory: `/private/tmp/coopgt-pairadd-20260905/experiment`.

```
/private/tmp/coopgt-research-20260904/.venv/bin/python pilot.py --per-size 192 --seed 20260905
/private/tmp/coopgt-research-20260904/.venv/bin/python refine.py
/private/tmp/coopgt-research-20260904/.venv/bin/python rational_certificates.py
python3 verify_saved_rationals.py
```

Versions: Python3.13.5, NumPy2.5.2, SciPy1.18.1, Z3 5.1.0. Logs: `pilot.log`, `refine.log`, `rational_certificates.log`. The final standard-library replay passed all35 identities. `reduced_counterexample.json` contains all exact arrays, selectors, ideals, stages, sorting checks and the reduction trace.

No repository files, release manuscripts or external messages were edited by this computational lane.
