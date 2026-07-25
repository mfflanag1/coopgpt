# Exact games and egalitarian stability — working notes

Question (Dietzenbacher 2021, open): is every **exact** game **egalitarian stable (ES)**?
Known: true for n<=4 (exact => large core, Biswas et al. 1999; large core => ES, Thm 3.5).
First open case n=5. Also open for stable-core games (n<=5 known).

## 0. Toolkit / validation
- `src/eshunt.py`: inline egalitarian procedure (`egalitarian_procedure`, `is_ES`), exact rational.
  Validated against paper Example 2 (claims (3,7,7,7), ES) and Example 3 (claims (2,2,2), NOT ES).
- Exactness/exactify via `hunt_sd.py` (`is_exact_game`, `exactify`).

## 1. Clean equivalence (the reduction that organizes everything)

**ES  <=>  gamma-hat in core(v)  <=>  gamma-hat dominates a core element from below
     <=>  sum_i gamma-hat_i = v(N).**

Proof.
- gamma-hat is always an aspiration: gamma-hat(S) >= v(S) for all S, and for each player i
  there is a *tight* coalition S_i ni i with gamma-hat(S_i)=v(S_i) and gamma-hat_i = min_{j in S_i} gamma-hat_j.
- If ES then N is egalitarian admissible, so sum gamma-hat = v(N); combined with the aspiration
  inequalities gamma-hat(S) >= v(S), gamma-hat is efficient and satisfies every core constraint => gamma-hat in core.
- Conversely if gamma-hat in core it trivially dominates itself; and the paper's Thm-3.5 argument
  (any core y <= gamma-hat must satisfy y(S)=gamma-hat(S) on every admissible S, and admissible
  coalitions cover N) forces y = gamma-hat, i.e. gamma-hat in core, hence N admissible => ES.

So the entire question is: **for an exact game, does the egalitarian claims vector land in the core?**
Equivalently, is the total claim `sum gamma-hat` NOT inflated above v(N)?

## 2. Covering-LP form of ES (via LP duality)

Let g(S) := gamma-hat(S) - v(S) >= 0 (the aspiration gap; g(S_i)=0 on tight coalitions).
gamma-hat dominates a core element  <=>  exists t>=0 with t(N)=g(N), t(S)<=g(S) for all proper S.
By LP duality this is feasible iff

    g(N)  <=  min over fractional covers lambda of  sum_S lambda_S g(S),

where a fractional cover is lambda>=0 with sum_{S ni i} lambda_S >= 1 for all i (proper S only).

Consequences:
- For a fractional **partition** (sum_{S ni i} lambda_S = 1): sum_S lambda_S gamma-hat(S) = gamma-hat(N),
  so sum lambda_S g(S) = gamma-hat(N) - sum lambda_S v(S) >= gamma-hat(N) - v(N) = g(N),
  because Bondareva-Shapley gives sum lambda_S v(S) <= v(N) for balanced collections.
  => **partitions never certify non-ES.** A non-ES witness *requires a strict over-cover*
  (some player covered with total weight > 1).
- With over-cover coefficients c_i = sum_{S ni i} lambda_S >= 1, a violating cover needs
      sum_S lambda_S v(S)  -  sum_i (c_i - 1) gamma-hat_i  >  v(N).
  The subtracted term is >= 0 when claims are nonnegative, so over-covering only helps if it
  concentrates weight on high-worth coalitions faster than it inflates the claim penalty.

This localizes where a counterexample must live: exact game whose claims vector fails the
over-cover inequality above. (It is a condition on gamma-hat, which the procedure produces, so
it does not immediately settle the question — matches its open status.)

## 3. RESOLUTION — the answer is NO. Exact does NOT imply egalitarian stable.

**Certified counterexample (n=5), exact rational arithmetic, two independent
implementations + core-point witnesses for all 30 proper coalitions.**
Script: `src/verify_es_counterex.py` (self-contained certificate).

Players {0,1,2,3,4}, bitmask index = sum 2^i.  Game v (integer-valued):

    v = [0,0,3,3,0,1,5,5,2,4,7,8,2,4,7,9,
         0,0,3,3,0,2,5,5,3,4,8,8,3,5,8,10]      # v[N]=v[31]=10

Key coalition worths: v({1,3})=7, v({1,2})=5, v({0,1,3})=8, v({1,3,4})=8,
v({1})=3, v(N)=10.

- **Exact**: for every proper S there is a core point x with x(S)=v(S), and
  min_{core} x(S) = v(S). (Verified via exact LP; `is_exact_game` = True.)
- **Balanced, superadditive, NOT convex.**
- **Egalitarian procedure** (n_v = 2):
  - Round 1: only {1,3} is admissible (per-capita 7/2 is the global max, attained
    by both members). Fixes gamma_1 = gamma_3 = 7/2.
  - Round 2: with 1,3 fixed at 7/2, admissible coalitions are {1,2}, {0,1,3},
    {1,3,4} (and {1,3}). Fixes gamma_2 = 3/2 (from {1,2}: (5 - 7/2)/1),
    gamma_0 = 1 (from {0,1,3}), gamma_4 = 1 (from {1,3,4}).
  - **Egalitarian claims  gamma-hat = (1, 7/2, 3/2, 7/2, 1),  sum = 21/2 > 10 = v(N).**
- N is NOT egalitarian admissible: at N the free players 0,2,4 split (10-7)/3 = 1
  each, so player 2 gets 1 < its claim 3/2. Hence N not admissible => **NOT ES**.
  Equivalently gamma-hat is an aspiration with gamma-hat(N)=21/2 > v(N)=10, so
  gamma-hat is NOT in the core (by section 1, ES <=> gamma-hat in core).

**Mechanism.** This is exactly the Example-3 pathology (two overlapping tight
coalitions sharing a "hub" whose worth is double-counted), lifted to n=5 and
*repaired to be exact*. In Example 3 (n=3) the hub player 3 sits in {1,3},{2,3};
exactness fails there only because the core forces x_3 = v(N) while v({3})=0.
Here the hub is player 1: it is fixed high (7/2) in the round-1 pair {1,3}, then
*reused* in {1,2} to inflate player 2's claim. The extra players (0,4 give player 1
outside partners; the singleton v({1})=3 etc.) give the core enough room that
every small coalition's worth is core-attainable, so exactness holds while the
claims still over-sum. The over-cover certificate of section 2 is realized by the
collection {1,3},{1,2},{0,1,3},{1,3,4}: player 1 is covered with total weight > 1.

Consistency with prior results: the game is exact but **not large core** (it must
be, since ES fails and large core => ES). This is precisely the exact-but-not-large
regime that first appears at n=5 (Biswas et al. 1999) — and it does contain non-ES
games. So the n<=4 result (exact => large core => ES) does not extend.

## 4. Search evidence

- `src/es_float.py`: fast float screener (HiGHS core-min + float egalitarian
  procedure with tolerance), every candidate re-certified in exact arithmetic
  (`certify` -> `eshunt.is_ES` + `hunt_sd.is_exact_game`). Screener validated to
  reproduce Examples 2 and 3.
- Exact non-ES games are **common**, not rare: all four independent seeds
  (esf_n5_s0..s3) produced certified counterexamples within the first few dozen
  trials. Representative claims found:
  s0 vN=10 (1,7/2,3/2,7/2,1); s2 vN=18 (1,1,15/2,3/2,15/2); s3 vN=23 (11/2,11/2,7,3/2,4).
- (Caveat that explains why the problem looked hard: a *random-aspiration* probe
  for non-large-core-ness detects 0% of these games — the offending aspiration is
  the egalitarian claims vector specifically, which random probing misses. So the
  games look large-core to a casual test yet are not.)

## 5. Bottom line
Every exact game egalitarian stable?  **NO.** Certified n=5 counterexample above.
(Since ES holds for all exact games with n<=4, n=5 is exactly the threshold, and
it is the same threshold at which exact-but-not-large-core first appears.)
The companion open question — stable-core games (known ES for n<=5) — is untouched here.

---

# PART II — Generalization to all n >= 5 (infinite families + mechanism)

Independently re-verified the team-lead's cleaner n=5 witness with my own inline
procedure (validated on Examples 2/3): players 1..5, player i = bit i-1,
  v = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6], v(N)=6.
Claims (1,1,3,1,1), sum 7 > 6; admissible {3},{3,4},{3,5},{1,3,5},{2,3,5}; exact,
superadditive, not convex; NOT ES. (This is the base witness below; hub = player 3.)

## 6. Two infinite families (script: src/es_family.py; verified n<=9)

**Padding operation.** Given exact game v on N, adjoin player p with
  v'(S)=v(S) for S subset N,   v'(S union {p}) = v(S) + c   (constant c >= 0).
c=0 is a NULL player; c>=1 is an "additive" player (essential, not a dummy).

**Exactness is preserved (proof).** In any core allocation x of v':
x(N) >= v(N) and x_p >= v'({p}) = c and x(N)+x_p = v'(N)=v(N)+c force x(N)=v(N),
x_p=c. Hence core(v') = core(v) x {c}. Then for every S,
  min_core' x(S) = min_core x(S\p) + c[p in S] = v(S\p) + c[p in S] = v'(S),
so v' is exact.  => padding preserves exactness for ANY c>=0. (Iterating, an
arbitrary number of padded players keeps the game exact.)

**Non-ES is preserved.**
Family A (c=0, null padding) — PROVEN. Inertness Lemma: a null player leaves the
other players' egalitarian claims unchanged and itself receives claim 0. Proof by
induction on procedure rounds: for S subset N, chi'(S)=chi(S) (same worth, same
fixed values, p free). For S = S0 ∪ {p} with S0 having a free original member,
every free member (incl. p) gets share (v(S0)-f)/(|free(S0)|+1) <= (v(S0)-f)/|free(S0)|
= its value in S0 (using v>=0), so p's presence never gives an original player a
NEW maximum; thus the admissible collection restricted to N, and the fixed values,
match the run on v exactly. p can only be fixed once its original co-members are all
fixed, at value v(S0)-gamma(S0) <= 0 (aspiration), and >= v'({p})=0, hence exactly 0.
So gamma' = (gamma, 0), sum gamma' = sum gamma > v(N) = v'(N): NOT ES.  Therefore
**for every n >= 5, base-witness + (n-5) null players is exact and non-ES.** (QED)

Family B (c>=1, additive padding) — NON-DEGENERATE, verified. Same core-decomposition
gives exactness; computationally the added player receives claim c and all other
claims are unchanged, so inflation stays exactly 1 and every player is essential
(no dummies). Verified exact + non-ES for n=6,7,8,9 with c=1 (and c=2). This yields
an infinite family of exact non-ES games in which EVERY player is essential.
(The null-case dilution proof does not transfer verbatim because +c can raise a
mixed coalition's share; hence Family B is stated as verified, Family A as proven.)

Sample (Family B, c=1): inflation 1 at every n; e.g. n=6 claims (1,1,3,1,1,1),
sum 8 > v(N)=7.

## 7. Obstruction: why a naive SYMMETRIC scaling family fails

Natural attempt: hub H (singleton m), one absorber D, k leaves; set v(H+D+>=1 leaf)
= m+2, v(N)=m+3, v(H,D)=m+1. The RAW game is non-ES for all k>=3 (claims (m,1,...,1),
sum m+1+k > v(N)=m+3), but it is NOT exact: the single coalition {H,D} has
min_core x(H,D) > m+1 (the leaf constraints x(H,D,leaf_i) >= m+2 with x(N)=m+3 pin
the leaves down, inflating x(H,D)). EXACTIFYING {H,D} up to its core-min hands the
surplus to the absorber (claim rises to 3/2, leaves drop to 1/2) and the game
becomes ES. So this whole one-parameter family collapses to ES under exactification.
The n=4 member is exact AND ES — consistent with the theorem that all n<=4 exact
games are ES. Lesson: the non-ES property is destroyed by the very exactification
needed to make these symmetric constructions exact; a genuine exact non-ES game
must be ASYMMETRIC (multiple direct satellites + absorbers, as in the base witness),
which is exactly why padding an existing witness — rather than scaling a symmetric
template — is the robust route.

## 8. Mechanism as a proposition (sufficient conditions for exact non-ES)

Recall (Part I sec.1-2) for exact v:  NOT ES  <=>  sum(gamma-hat) > v(N)  <=>
gamma-hat is a Pareto-minimal aspiration outside the core  <=>  there is an
over-cover lambda (frac. weights on proper coalitions, sum_{S ni i} lambda_S >= 1,
strict for some player) with sum_S lambda_S(gamma-hat(S)-v(S)) < gamma-hat(N)-v(N).

**Proposition (hub over-cover).** Suppose an exact game admits a player h and tight
coalitions T_0={h}, T_1, ..., T_r (each gamma-hat(T_j)=v(T_j), each h in T_j) whose
union is N and on which the egalitarian procedure fixes h first (via T_0, so
gamma-hat_h = v({h}) is the global per-capita maximum) and then fixes every other
player i at gamma-hat_i via some T_j reusing h's value. Because each T_j "spends"
h's full claim gamma-hat_h but h is a single player, the claims over-count h:
formally {T_j} is a strict over-cover of N at h, so
  sum_j 1 * (gamma-hat(T_j)-v(T_j)) = 0 < gamma-hat(N)-v(N),
i.e. the section-2 certificate fires and sum(gamma-hat) > v(N): the game is NOT ES.
Exactness survives iff the core is fat enough that h's small-coalition worths (incl.
v({h})) are still attained by core points — achieved by giving h absorber-partners
who can carry value while h's satellites sit at 0 (the base witness: core point
(x_H,x_a,x_b,x_c,x_d)=(3,0,0,1,2) attains v({H})=3).

This is the "claims-incompatibility" structure: the tight coalitions certifying the
claims are pairwise incompatible (all require the hub) and therefore cannot be packed
into an efficient allocation, so the egalitarian claims inflate above v(N) while every
individual coalition worth remains core-attainable.

## 9. Bottom line (Part II)
- Exact-but-non-ES games exist for **every n >= 5** (null-padding family, proven).
- They exist with **every player essential** for every n >= 5 (additive-padding
  family, verified n<=9).  Reproduce: `python src/es_family.py`.
- The threshold n=5 is sharp (n<=4 all ES) and coincides with the onset of
  exact-but-not-large-core.
- Mechanism: a hub whose claim is reused across pairwise-incompatible tight
  coalitions (strict over-cover at the hub) inflates the egalitarian claims above
  v(N), while absorber players keep the core fat enough to preserve exactness.

---

# PART III — Paper draft (canonical primary witness)

Per team-lead, the PRIMARY witness for the writeup is hunt-pes's canonical game
(v(N)=4, minimal): v(S)=min(x1(S),x2(S)) with x1=(0,0,1,1,2), x2=(1,1,0,2,0)
(both sum 4). Independently re-verified with my implementation: exact, balanced,
monotone, superadditive, not convex; single-round procedure (n_v=1), symmetric
claims (1,1,1,1,1) sum 5 > 4; A-hat={{4},{3,4},{4,5},{1,4,5},{2,4,5}} (all route
through pivot player 4); PES=(3/4,3/4,3/4,1,3/4), violating {3,4},{4,5} by 1/4
and {1,4,5},{2,4,5} by 1/2. Generator lemma (min over finite equal-sum point set
is exact; Schmeidler lower-envelope specialization) verified 19/19 on random
inputs. Padding family re-verified from this base (null + additive, n=6..7).
Hub witness (claims (1,1,3,1,1)) and my half-integer witness (1,7/2,3/2,7/2,1)
are now SECONDARY. Deliverables: paper2/sections_theory.tex (compiles, 6pp),
paper2/supplement_data.json (primary + 2 secondaries, 30 exactness witnesses),
src/gen_cert2.py (regenerates supplement).
