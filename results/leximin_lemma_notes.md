# Leximin-above-floors core selection: monotonicity notes (handoff to theory-es)

**Author:** hunt-fam5 (experiment + data). **For:** theory-es (formal proof).
**Status:** live candidate theorem — clean over 2000+ exact-preserving bumps at
n=4,5 incl. thin-core point games; fully-exact n=4 confirmation + adversarial
n=5/n=6 running. Proof open.

## 1. The selection phi

For a balanced game v on N (|N|=n), floors m_i := v({i}). Define
  phi(v) := the unique core point that lexicographically maximizes the
  ascending-sorted vector of gains g_i := x_i - m_i over core(v).
("leximin-above-floors" / "floors-egalitarian core selection".)

On EXACT games m_i = min_{core} x_i, so all gains g_i >= 0 and phi is the
egalitarian (leximin) distribution of the surplus x_i - v({i}) subject to
staying in the core. Single-valued (leximin over a polytope is unique).

Algorithm (implemented exact + float, `src/leximin.py`, Maschler-style over
PLAYER COORDINATES, validated: simplex -> barycenter; = equal-gains-above-floors
when core-feasible; float==exact & in-core 30/30):
  free = N; fixed = {}
  repeat:
    s = max{ t : x in core, x fixed on `fixed`, x_i - m_i >= t for i in free }
    pin every free i that cannot exceed m_i + s on the level-optimal face
      (max x_i over {core, fixed, x_j-m_j >= s all free j} == m_i + s);
    fix pinned i at m_i + s; remove from free
  until free empty.

## 2. Theorem (candidate)

Let v be EXACT, S a coalition, d>0, v' = v + d·1_S (bump only v(S)), and suppose
v' is also exact. Then phi_i(v') >= phi_i(v) for every i in S.
(I.e. phi is a coalitionally monotonic single-valued core selection on exact
games — settling paper 1's Conjecture affirmatively via an explicit selection.)

## 3. Mechanism sketch (non-singleton S)

Floors are UNCHANGED (v'({i}) = v({i}) since |S|>=2), and
  core(v') = core(v) ∩ H,  H := { x : x(S) >= v(S)+d } ⊆ core(v).
So phi(v') is the leximin-above-floors point of a SHRUNK core, same floors.

(a) If phi(v) ∈ H already (i.e. phi(v)(S) >= v(S)+d): then phi(v) is leximin-
    optimal over core(v) ⊇ core(v') and lies in core(v'), hence it is leximin-
    optimal over core(v') too. So phi(v') = phi(v). Monotone with equality.

(b) Else the new constraint x(S) >= v(S)+d binds. Potential/KKT view: the
    leximin point is the limit (as the risk-aversion parameter -> infinity) of
      argmin_{x in core(v')} Σ_i h(x_i - m_i),  h strictly convex, decreasing
      marginal (e.g. h(g) = -log g or g^{1-ρ}, ρ→∞).
    The constraint x(S) >= β (β = v(S)+d) carries a KKT multiplier μ >= 0. Its
    stationarity adds μ·1[i∈S] to the marginal value of raising x_i, i.e. it
    behaves like LOWERING the effective marginal cost for members of S — pushing
    their optimal gains UP. Increasing β weakly increases the active multiplier
    μ (tighter constraint), monotonically pushing every i∈S weakly up and (by
    the efficiency/complementarity) pulling mass from N\S. This is the
    comparative-statics statement to formalize: **the leximin-above-floors point
    is monotone nondecreasing on S under tightening a lower bound on x(S).**

CRUX to nail (where a proof could break, and the thing to check hardest): when
x(S)=β binds, could leximin redistribute WITHIN S — lowering a high-gain member
j∈S while raising a low-gain member k∈S (keeping x(S)>=β)? That would drop j∈S.
Empirically it never happens. Heuristic why: the extra mass S needs comes from
N\S players who sit above their floors; leximin taps the globally-lowest gains
first, which raises the low members of S without needing to strip a high member
of S. A rigorous proof must exclude the within-S downward move — likely via the
separable-convex-potential monotone comparative statics (Topkis / polymatroid-
style), or a direct exchange argument on the leximin level sets.

Relation to known results: on CONVEX games the core is a base polytope and this
is the Dutta–Ray (1989) constrained egalitarian solution, which IS monotone
there. The novelty/difficulty is EXACT (non-convex) games, whose core is a
general polytope; Dietzenbacher's procedural-egalitarian/L_max solution is the
other egalitarian route but it can leave the core / fails on exact non-ES games
(the frontier that just killed the ES route). phi is defined to always be IN the
core, and the data says it stays monotone there — that is the new content.

## 4. Singleton bump case (S = {j})

v'({j}) = v({j})+d, so the FLOOR m_j rises by d and
  core(v') = core(v) ∩ { x_j >= m_j + d }.
Two forces both push phi_j up: (i) the core now forces x_j >= m_j+d; (ii) in the
gain coordinate g'_j = x_j - (m_j+d), player j's gain is shifted DOWN by d, so
leximin (equalizing gains) compensates by raising x_j. Need phi_j(v') >= phi_j(v).
Data: singleton bumps are included in the exhaustive-coalition adversarial sweep,
0 violations. Formalization should be easier than the non-singleton case (only
one watched coordinate, and both effects are co-monotone).

## 5. Supporting data & width law (pointers)

- phi monotonicity, float-screened + exact-certified path:
  n=4: 694 exact bases, 1503 exact-preserving bumps, 0 violations
       (`results/agent_leximin_n4.txt`).
  n=5: 402 exact bases, 501 exact-preserving bumps, 0 violations
       (`results/agent_leximin_n5.txt`).
  Fully-EXACT (no float) n=4 confirmation: `results/agent_leximin_...` (running).
  Adversarial thin k=2 point games, EXHAUSTIVE coalitions, singleton bumps,
  dmax=6, n=5/n=6: `results/agent_leximin_adv_n{5,6}.txt` (running, clean).
- WIDTH LAW (independent evidence the family LP is uniformly strictly feasible):
  the co-singleton/star family monotonicity slack satisfies
      t* >= min_w / (n(n-1)),   min_w = min_i (max_core x_i - min_core x_i),
  verified over 1244 families, 0 violations, infimum EXACTLY 1/(n(n-1)); tight on
  the simplex co-singleton family where t* = c/(n(n-1)) exactly (n=4,5,6, closed
  form, independent of bump depth). `results/widthslack5.csv`, `src/widthslack5.py`.
  This is the "there is room to move" quantitative backbone; the leximin point is
  a canonical selection realizing that room. min_w=0 ⇒ a player is core-fixed at
  v({i}) ⇒ reduce to (n-1)-player exact game (induction; 0/500 bases had min_w=0).
- Diamonds (depth-2) clear the width floor with margin (min t*/min_w = 0.125).

## 6. Open items for the proof
- The comparative-statics lemma of §3(b) (exclude within-S downward move).
- Whether leximin = argmin of a single separable convex potential over the core
  exactly, or only as a limit (affects which comparative-statics theorem applies).
- Singleton case §4 (should be short).
- Beyond single bumps: multi-coalition / depth>=2 DAGs (compactness reduction
  then needs phi monotone along every edge — same lemma applied edgewise).
- n-independence: mechanism has no n cap; adversarial n=6 is the current stress.

Code: `src/leximin.py` (selection), `src/hunt_leximin.py` /
`src/hunt_leximin_adv.py` / `src/leximin_exact_check.py` (tests),
`src/widthslack5.py` (width law).

---

# theory-es contributions (proof backbone + sharpness)

Two additions that are fully rigorous, plus an honest read on the crux.

## 7. Exactness is NECESSARY (proven; two certified counterexamples)

phi is NOT coalitionally monotone on balanced NON-exact games. Both witnesses are
exact-rational-certified (phi(v),phi(v') in core; a member of the bumped S strictly
drops); both are NON-SINGLETON bumps -- so exactness is essential even for the
non-singleton case, and cannot be relaxed to balancedness. Hunt: src/hunt_leximin_nonexact.py.

- **n=5, floors ATTAINED, non-exact only at pairs** (the strong version):
  v=[0,0,1,2,1,1,3,3,1,1,2,3,2,2,4,4,2,-1,2,4,4,4,5,6,3,4,1,5,5,5,6,7]; bump S={0,1,2}, d=1.
  phi(v)=(1/2,3/2,3/2,1,5/2) -> phi(v')=(1,1,2,1,2): player 1 drops 3/2->1.
  m=(0,1,1,1,2)=min_core x_i for ALL i (floors attained), yet monotonicity fails.
  => it is *coalition-level* exactness, not floor attainment, that the theorem needs.
  results/WITNESS_leximin_nonexact_n5.json
- **n=4, floor UNattained**: v=[0,-3,5,11,2,7,4,13,2,2,10,14,8,9,13,20]; bump S={0,1,2}, d=3.
  phi=(5/2,17/2,9/2,9/2)->(2,9,5,4): player 0 drops 5/2->2. (v({0})=-3<1=min_core x_0.)
  results/WITNESS_leximin_nonexact_n4.json

Consequence for §3/§4: the mechanism sketch's implicit reliance on "floors attained" is
NOT sufficient by itself (n=5 has floors attained and still fails). The proof must use
exactness at higher coalitions -- captured exactly by Lemma A next.

## 8. The exact-interval lemma (PROVEN) -- where exactness enters

**Lemma A.** v exact, S proper, d>0, v'=v+d*1_S exact. For tau in [v(S), v(S)+d] let
v_tau agree with v except v_tau(S)=tau. Then v_tau is exact for every such tau.

*Proof.* core(v_tau)=core(v) ∩ {x(S) >= tau} (only the S-inequality moves; v(N) fixed
as S proper), nonempty since it contains core(v')!=∅. Need min_{core(v_tau)} x(T)=v_tau(T).
T=S: min = max(tau, min_{core(v)} x(S)) = max(tau,v(S)) = tau. T!=S: f_T(tau):=
min_{core(v_tau)} x(T) is nondecreasing in tau (shrinking set) and >= v(T) (subset of
core(v)); it equals v(T) at tau=v(S) and tau=v(S)+d (v,v' exact); a nondecreasing function
equal to v(T) at both endpoints and >= v(T) between is identically v(T). Hence exact. ∎

**Why it matters.** The bump is a continuous path of EXACT games in which only the lower
bound tau on x(S) rises. The theorem <=> along this path phi_i(v_tau) is nondecreasing in
tau for i in S. For merely balanced v the interior of the path leaves exactness (Lemma A
fails), which is exactly the room in which the Section-7 counterexamples live. This
isolates the crux to a clean 1-parameter monotone-comparative-statics statement on a path
of exact games (Lemma C, §5 above), rather than a 2-endpoint comparison.

Also (combine with §5 width law): every v_tau is exact => min_core x(T)=v_tau(T) for ALL
T along the path -- the "room to move" holds uniformly on the path, not just at the ends.

## 9. Binding regime -- where any counterexample must hide (stress test)

By Lemma B the constraint often does NOT bind: for most exact-preserving bumps the
exact-preserving range of d is <= the slack phi(v)(S)-v(S) (so phi is unchanged and
monotonicity is trivial). Binding requires phi(v)(S) < max_core x(S). I ran a hunt that
tests ONLY binding exact-preserving bumps (d>slack, exact-preserving), exact-certifying
each: src/hunt_leximin_binding.py (n=5 seeds 1-3, n=6). In every binding case observed:
y(S)=v(S)+d exactly, y_i>=x_i for all i in S, y_i<=x_i for all i not in S. [running;
results/lx_binding_n5_s*.log, lx_binding_n6.log -- update counts on completion.]

## 10. Assessment of the crux (Lemma C), adversarially
- Lemma C is a leximin parametric-monotonicity statement. The nucleolus (a cousin) is
  NOT coalitionally monotone, so nothing generic forces this -- exactness (Lemma A) is
  doing real work and a proof must use it. The "self-defeating within-S Robin-Hood"
  heuristic (§3b, §4) is NOT yet a proof.
- The smoothing/KKT route (§3b) I tested numerically is unreliable (SLSQP overflow);
  finite-alpha monotonicity is not evidently clean, so "leximin = limit of a monotone
  smoothed rule" is not yet established. Treat §3b as motivation, not proof.
- Most promising next step: prove Lemma C using the leximin nested-tight-set (Kohlberg-
  balanced level) structure together with Lemma A's uniform exactness along the path --
  i.e. show that at a binding tau, raising tau marginally moves the active leximin level
  structure so that d(phi_i)/dtau >= 0 for i in S. The two-sided pattern (outsiders weakly
  lose) suggests a conserved-flow argument on the level sets.

## 11. A candidate proof skeleton via a cone condition (theory-es; PARTIAL, honest)

Define, at x=phi(w) for a game w with tight set T(x)={T: x(T)=w(T)}:
  (star_S): there exists e in R^N with e(N)=0, e(S)>0, e_i>=0 for all i in S,
            and e(T)>=0 for every tight T in T(x).
(A first-order direction that raises x(S) without lowering any S-member or breaking a
tight core constraint.)

Findings (float LP, exact-certifiable):
- **monotone => (star)**: a bump is coalitionally monotone only if (star_S) holds at
  phi(v). No exception found (star=False always came with a drop). So (star) is a clean
  NECESSARY condition, and it FAILS at the Section-7 non-exact counterexamples (verified:
  the n=5 witness has no such direction at phi(v)).
- **exact => (star)** at every binding-bumpable S: 39/39 and 13/13, no exception.
- **(star) is NOT sufficient** on general balanced games: 22/1696 binding bumps had
  (star) at phi(v) yet dropped an S-member (all non-exact). [Corrects an earlier
  small-sample claim that (star)<=>monotone.]
- **(star) along the whole (exact) path => monotone**: sampling (star) at phi(v_tau) for
  tau at v(S), midpoint, v(S)+d, "star at all three" implied monotone in 0/600 failures
  (monotone-but-not-star-at-all-three occurred 91x -- (star)-path is sufficient, not
  necessary).

**Candidate proof skeleton (exact games):**
  (Lemma A) exact endpoints => path v_tau all exact.
  (Lemma D) each exact v_tau => (star_S) at phi(v_tau).       [39/39; PROOF OPEN]
  (Lemma E') (star_S) at phi(v_tau) for all tau => phi_i nondecreasing on S. [0/600; OPEN]
  Compose => theorem.

**Obstruction found (why Lemma D is not immediate):** v' exact gives a core point z with
z(S)=v(S)+d and z(T)>=v(T); then e=z-phi(v) satisfies e(N)=0, e(S)>0, e(T)>=0 on tight T
-- BUT z_i can be < phi_i(v) for some i in S, so e may lower an S-member. Hence the
easy construction yields only the WEAKER cone condition (drop the "e_i>=0 on S"). The
full (star_S), with per-member nonnegativity, is what separates exact (monotone) from
non-exact, and proving exact=>(star_S) is the current crux (the LP always finds such e on
exact games, but not via z-phi(v)).

Net status unchanged from Sections 7-10: necessity PROVEN; positive theorem reduced to
Lemmas D + E' with (star) isolating the mechanism, but not closed.

## 12. Lemma D: clean equivalent forms + Farkas dual (theory-es; verified, still open)

Equivalent forms of (star_S) at x=phi(v) (all verified equivalent computationally):
  (star_S)  <=>  exists core point y with y_i >= phi_i for all i in S and y(S) > phi(S)
            <=>  max{ y(S) : y in core(v), y_i >= phi_i (i in S) } > phi(S).
[Proof of the middle equivalence: y=phi+eps*e for the (star) direction e, and any core
point mixture y has y(T)>=v(T)=phi(T) at tight T so e=y-phi meets the tight-cone part for
free -- the lead's mixing observation.]

**Farkas dual (verified 200/200: (star) feasible <=> the cover below INfeasible):**
  (star_S) FAILS  <=>  the TIGHT coalitions T(x)={T: x(T)=v(T)} admit weights
     lambda_T >= 0 and beta >= 1 with  sum_{T ni k} lambda_T = beta (k not in S),
     <= beta-1 (k in S).
  Equivalently (multiply a core point through the cover):
  (star_S) FAILS  <=>  phi(v) MAXIMIZES  sum_{k in S} r_k x_k  over core(v)
     for some weights r_k >= 1 (k in S), 0 elsewhere.
So a bump is monotone-safe exactly when phi does NOT sit on a positive-S-weighted maximal
face of the core.

**Reduction of Lemma D:** exact v, binding-bumpable S (so phi(S) < max_core x(S)).
Must show phi does not maximize any sum_{k in S} r_k x_k (r>=1 on S) over core(v).
- For UNIFORM r (r_k=c): maximizing c*x(S) => phi(S)=max_core x(S), contradicting
  binding-bumpability. So uniform weights are already excluded -- the whole content is
  NON-uniform weights.
- Open: exactness must exclude phi sitting on a non-uniform positive-S-weighted max face.
  Intuition: leximin EQUALIZES gains, so it will not push some S-members to a weighted
  maximum unless the core forces it; exactness ("core fat enough", every coalition
  attained) removes that forcing. Not yet a proof. The NON-exact counterexamples DO have
  phi on such a face (that is exactly why (star) fails there).
- Note: the naive mixing construction {z, w^i attaining max x_i for deficient i} is
  INSUFFICIENT (built a valid direction in only 11/16 exact binding cases); the general
  core point from the max-LP is needed, i.e. the LP/dual form above, not a fixed finite
  mixture.

Status: Lemma D reduced to a sharp, verified core-geometry statement; final "exact =>
no positive-S-weighted max face" step OPEN. Lemma E' still open. Conditional theorem
(phi coalitionally monotone on exact games given Lemmas D + E') + unconditional necessity
stand.
