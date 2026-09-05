# Independent hostile audit: asymptotic separation package

The main theorem survived this audit. I found no counterexample, invalid implication, missing parameter case, or reliance on an unjustified generating-hull identification in the released manuscript. This conclusion comes from reconstructing each proof and running new exact tests, not from accepting the package's saved PASS results.

The detailed obligations and source anchors are in [PROOF_OBLIGATIONS.md](PROOF_OBLIGATIONS.md). The independent test implementation is [independent_audit.py](independent_audit.py), with completed results in [independent_results.json](independent_results.json). Hypothesis-removal controls are in [hypothesis_controls.py](hypothesis_controls.py) and [hypothesis_controls.json](hypothesis_controls.json).

## Findings by severity and type

**Theorem failures: none found.** The universal argument at manuscript lines 149–179 is valid for arbitrary opposing first-stage choices, so later lexicographic ties do not weaken it. The segment equality at lines 218–229 genuinely proves the whole core, and the Fibonacci elimination at lines 285–295 includes m=2. The all-n choice at lines 304–313 handles discontinuities of the ceiling logarithm correctly.

**Incomplete mathematical exposition: no blocking gap.** Two places could be made more explicit if the author wants to reduce the review burden, but neither requires a theorem change:

- Lines 307–309 say the exponential left side “grows faster.” The exact induction gap is `[2^L+1−12(L+1)−2] − [2^{L−1}+1−12L−2] = 2^{L−1}−12 > 0` for L≥8.
- Lines 323–327 assert sufficiently large admissibility for the minimal-Fibonacci integer choice. In fact the earlier construction gives `m≤4L`, hence `n≥12L+2≥3m+2` for every n≥128. Also minimality gives `F_m<n²`, and `F_{m+1}<2F_m<2n²` because the applicable m exceeds 2. This proves the stronger explicit bound `scaled total < 2n³` in the same displayed regime.

**Verifier scope limitations:** At `verification/run_checks.py:21` and `:185`, the accepted scientific coverage is five raw cases and finitely many arithmetic identities. It does not computationally cover arbitrary matrices, the universal overlap lemma, or general sorted-selector existence. The manuscript at lines 333–357 states that limitation correctly. These are ordinary evidence boundaries, not verifier defects.

**Verifier lifecycle boundary:** Scientific exceptions after RUNNING are recorded at `verification/run_checks.py:240–243`, but imports at line 18 and output setup at lines 225–228 occur outside that try block. A pre-main/import failure can leave an older result file untouched. The package's precise claim “before checks” is narrower than a blanket promise that any failed invocation invalidates an old PASS. The coordinating review is separately reproducing and classifying that startup case. This does not affect the theorem or the validity of the completed scientific records.

**Formal proof boundary:** Z3 UNSAT results are exact rational satisfiability evidence under Z3's implementation; these new tests do not produce independently checkable proof objects. The coordinating audit is adding a separate backend. No primary-source theorem is load-bearing here, so this lane did not conduct an unrelated source or novelty search.

## Independent completed calculations

A fresh run of the unmodified package verifier, with its output redirected into this scratch directory, passed all five scientific cases, its closure control, and its arithmetic checks. The new record is [package-replay.json](package-replay.json). The package's old records were neither modified nor used as acceptance evidence.

The independent script imports no package code. In particular, its raw-core routine explicitly enumerates tuples of coalition membership and directly sums each coalition, instead of reusing the package's bit-mask subset-sum recurrence. Its exact Gaussian elimination was written separately.

| New check | Actual completed scope | Outcome |
|---|---|---|
| Universal overlap falsification | n=2,…,10; arbitrary nonnegative equal-total x,z satisfying only the two necessary directional-witness conditions; `sum min(x_i,z_i)<1/(n−1)` | UNSAT in all 9 cases |
| Sorted-selector uniqueness falsification | n=2,…,5; arbitrary labeled vectors with equal sorted vectors, distinct allocations, and a midpoint alleged not to improve the increasing lexicographic order | UNSAT in all 4 cases |
| Arbitrary 0/1 incidence matrices | Every 0/1 matrix of sizes p=1,…,4: 66,066 matrices; 22,741 invertible; 543 with strictly positive A⁻¹1 | Complete finite enumeration |
| General-matrix whole cores and selectors | All 15 positive matrices through p=3; one representative of each of the 5 distinct sorted donor vectors at p=4, since donor permutation leaves the game isomorphic | 20 complete raw-core cases; no off-segment point, no other optimal-face point, no strictly better first-stage objective |
| Fibonacci incidence elimination | m=2,…,40; direct exact solve of all 2m rows | Expected positive solution, `abs(det A)=F_{m+1}` in every case |
| Additional Fibonacci whole cores | (m,r)=(2,5),(2,6),(3,6),(4,6), including H>1; largest case has 15 players and 32,768 coalition constraints | All segment and selector queries UNSAT; exact distance formulas agree |
| Every logarithm interval endpoint in a long range | L=7,…,128; both least admissible n and greatest n in each interval, with n≥128 | Admissibility, Fibonacci dominance, and exact squeeze all hold |
| Alternative integer representation | n=128,129,256,1000,10⁶,10¹²,10³⁰,10⁶⁰ | Minimal m admissible; `n²≤F<2n²`; total `<2n³` |

The independent completed suite took approximately 33.5 seconds on Python 3.13.5 / Z3 5.1.0. Its bounded checks support the reconstructed proof; they do not establish claims outside their stated ranges.

Two exploratory audit-script failures were retained as limitations rather than reinterpreted as scientific results. An initial direct piecewise-linear overlap search toward n=32 timed out without returning SAT or UNSAT; the final completed scope is n≤10. A first audit-script draft precomputed too short a Fibonacci table for the n=10⁶⁰ integer check and raised StopIteration; extending the exact table resolved this local harness bug. Neither event involved a failing manuscript claim, and neither is counted as a passed test. The package verifier itself passed its fresh replay.

## Independent attempts to break hypotheses

**Exactness does not identify the generating hull.** Take `U=(2,0,0)`, `V=(0,1,1)` and define every coalition by the minimum. The singleton values are zero and the game is exact because both generators are core points attaining every minimum. Nevertheless `Y=(1,1,0)` is in the core: its two nontrivial pair bounds are `Y₁+Y₂≥1` and `Y₁+Y₃≥1`; the remaining pair lower bound is zero. Y is off `[U,V]`, whose receiver coordinates must be equal. The independent control enumerates every coalition. This supports the need for the manuscript's complementary equalities at lines 218–229; it does not contradict them.

**Convexity is necessary for the overlap theorem as stated.** In the compact two-point set `{(1/2,1/2,0,0),(0,0,1/2,1/2)}`, both allocations are first-stage maximin and minimax optimizers, but their overlap is zero rather than at least 1/3. The convex hull contains the improving uniform midpoint. Thus the manuscript uses a material, explicitly stated hypothesis.

**Nonnegativity is also material.** Uniformly subtract 1/3 from every coordinate of the valid m=2,r=3 construction. This preserves the two sorted selectors on the translated compact convex segment and leaves positive total T=1/3. The translated selectors are

`x=(1/3,0,0,0,0,0,0,0)` and
`z=(1/6,−1/12,−1/12,−1/12,−1/12,1/6,1/6,1/6)`.

Their overlap is −1/6, below T/(n−1)=1/21. The violated nonnegativity condition is exactly the one required at manuscript lines 150–151 and used at lines 174–178. No such signed allocations are admitted into the paper's game class.

## Most important independent proof details

For selector uniqueness, equal sorted optimal vectors need not give equal labeled points automatically. The midpoint argument actually closes that gap: choose the least payoff level with different assigned player sets. Every lower-level assigned coordinate agrees in both vectors, and no higher coordinate can move down to the chosen level under averaging. Only the intersection of the two chosen-level sets remains at that level. Its cardinality is strictly smaller, so the midpoint's sorted vector first differs by an increase. Convexity contradicts optimality. Negating allocations maps the other convention to this one.

For the universal bound, the proof does not need exactness or unique first stages. A minimum coordinate of x that cannot rise toward z and a maximum coordinate of z that cannot fall toward x supply different indices i,j. Their contributions to overlap are respectively z_i and M. Since the other n−1 coordinates of z are each at most M, `T≤z_i+(n−1)M≤(n−1)(z_i+M)≤(n−1)O`. For n=2 this forces equality of opposing choices, as required by the zero upper bound for separation.

For the core realization, generator feasibility alone is insufficient. What makes it work is that each row-plus-receiver coalition and its complement have identical endpoint values. Every core point must satisfy each corresponding equality. Equal receiver coordinates leave one scalar t, invertibility fixes every nondistinguished donor at td_i, and efficiency fixes the distinguished donor at tH. Nonnegativity confines t to [0,1]. This establishes both containments rather than assuming either.

For the final asymptotic statement, `n−12L≥n/2` eventually, so the displayed bounds give the explicit one-sided estimate

`0 ≤ (2−s_n)−2/n ≤ 48L/n² + 2/n²`.

The claimed big-O error and first-order coefficient follow. The first inequality is even stronger, `2/(n−1)−2/n>0`. No claim about an exact second-order coefficient, finite-n sharpness, or supremum attainment follows and none is made.

The appropriate correctness conclusion is: the released theorem is supported by a valid conventional proof and the independent exact tests above. Novelty, specialist significance, and formal proof certification remain outside this lane's evidence.
