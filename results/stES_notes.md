# stable core => egalitarian stable — working notes (2nd prover, claims-structure route)

TARGET: every TU game whose core is a vNM-stable set is egalitarian stable (ES).
This is the 2nd (stable-core) half of Dietzenbacher (2021) open question.

## 0. Reformulations (all used; first two are from theory_es_notes.md, re-verified)

- **ES <=> gamma-hat in core(v) <=> sum_i gamma-hat_i = v(N)**, where gamma-hat is the
  egalitarian claims vector produced by the procedural-egalitarian procedure.
  gamma-hat is always an *aspiration*: gamma-hat(S) >= v(S) for all S, and its *admissible*
  (tight) coalitions A-hat = {S : gamma-hat(S)=v(S)} COVER N (each player lies in one, and is
  a minimizer of gamma-hat within it). Non-ES <=> delta := sum gamma-hat - v(N) > 0.

- **Core is vNM-stable <=> core is EXTERNALLY stable** (core is always internally stable):
  every imputation outside the core is dominated by some core element.
  Domination x dom_Q y: x_i > y_i for all i in Q and x(Q) <= v(Q).
  For a CORE x, x(Q) >= v(Q), so domination forces x(Q) = v(Q) (x tight on Q) and,
  summing, y(Q) < v(Q) (Q blocks y). So: only blocking coalitions can dominate, and a
  core element must be TIGHT on the blocking coalition it dominates through.

- **Contrapositive we prove:** non-ES => core NOT stable, i.e. construct an imputation y
  that is (i) outside the core, (ii) undominated by every core element.

## 0b. CLEAN REDUCTION (the cleanest reframing of the open problem) — PROVEN.
Dietzenbacher's Thm 3.5 (large => ES) only ever uses ONE consequence of largeness:
the existence of a core point y <= gamma-hat. Isolating that:

  **THEOREM (reduction).** For a balanced game, ES  <=>  there is a core element y <= gamma-hat.
  Proof (<=): given core y <= gamma-hat, on each admissible S: v(S) <= y(S) <= gamma-hat(S)=v(S)
   so y(S)=gamma-hat(S); with y<=gamma-hat coordinatewise and A-hat covering N this forces
   y=gamma-hat, efficient => sum gamma-hat=v(N) => ES. (=>): if ES, gamma-hat itself is the core point.

  Therefore: **stable => ES  ⟺  [ core stable  =>  ∃ core point y <= gamma-hat ].**
  This is exactly the LARGENESS property (∃ core below) but demanded only at the single
  aspiration gamma-hat. "Large => stable" and "large => (core below every aspiration)" are known;
  the open content is whether STABILITY alone forces a core point below this one aspiration.
  Contrapositive (what the escape construction attacks): no core point <= gamma-hat (⟺ non-ES,
  by the reduction) must be shown to imply an undominated escape.

## 0c. Subgame-core property — PROVEN (used throughout).
For every admissible S (gamma-hat(S)=v(S)), gamma-hat|S ∈ C(v|S).
Proof: for T ⊆ S, gamma-hat(T) >= v(T) (aspiration) and gamma-hat(S)=v(S) (admissible). QED.
So the claims vector restricts to a core element of every admissible subgame; ES fails only
because these subgame-core pieces overlap (at the hub) and cannot be packed efficiently.

## 0d. Over-cover characterization of non-ES — PROVEN (localizes the obstruction).
Let L* = min { sum_S lambda_S : lambda >= 0 on PROPER admissible coalitions,
sum_{S ni i} lambda_S >= 1 for all i } (cheapest fractional cover of N by admissible sets).
  **non-ES  =>  L* >= n/(n-1) > 1.**
Proof: any feasible lambda covers each of the n players, so sum_i sum_{S ni i} lambda_S >= n,
i.e. sum_S lambda_S |S| >= n. Proper S have |S| <= n-1, so (n-1) sum_S lambda_S >= n. QED.
(ES <=> N admissible => {N} covers with weight 1 => L*=1.) Verified 43/43 at n=5 (all L*>1).
Meaning: the admissible coalitions — on each of which gamma-hat restricts to a subgame-core
element (0c) — necessarily OVER-cover N; their subgame-core pieces cannot be packed into one
efficient allocation. THE CRUX of the whole problem is whether core STABILITY forces such a
packing (a core point <= gamma-hat, cf. reduction 0b) the way LARGENESS/EXTENDABILITY does.

## 0e. Domination-region geometry (external stability is genuinely hard).
For coalition S let opt_S(y) = max{ t : x in core, x(S)=v(S), x_i - y_i >= t for i in S }
= max_{x in face F_S} min_{i in S}(x_i - y_i). min_{i in S}(x_i - y_i) is jointly concave in
(x,y) and F_S convex, so opt_S is CONCAVE in y. y is dominated via S iff opt_S(y) > 0, so the
S-dominated region D_S = {opt_S(y) > 0} is CONVEX and open (superlevel set of a concave fn).
BUT the undominated set U = simplex \ union_S D_S = intersection_S {opt_S(y) <= 0} is an
intersection of COMPLEMENTS of convex sets — **U is NON-convex in general** (sublevel sets of
concave functions are not convex; my earlier "U convex" note was WRONG and is retracted).
The boundaries of D_S are piecewise-linear with breakpoints at PROJECTED CORE-VERTEX
coordinates, so U's vertices lie on planes "y_i = (core-vertex coord)" absent from the
coalition+floor arrangement (6/6b) — that arrangement is provably INCOMPLETE for certifying
"no escape". Certifying stability (U = C) is co-NP-hard in general (a bilinear/bilevel test;
the dualized opt_S<=0 has a bilinear coupling term sum_i c_i y_i). This matches
Grabisch-Sudholter's finite-but-heavy nested-balancedness being the known route. So a rigorous
"stable" verdict on cand1/cand2 is genuinely expensive; escapes can sit anywhere in U, not just
adjacent to core facets, so the facet/boundary searches are heuristic, not complete.

## 1. Lemma A (outside-core, PROVEN).
If y is efficient (y(N)=v(N)) and y <= gamma-hat coordinatewise, then y in core => y = gamma-hat
=> ES. Contrapositive: for a non-ES game every efficient y <= gamma-hat is OUTSIDE the core.
Proof: y in core => y(S) >= v(S) all S. On admissible S, (gamma-hat - y)(S) = v(S) - y(S) <= 0,
but gamma-hat - y >= 0 forces gamma-hat_i = y_i on S. A-hat covers N => gamma-hat = y => efficient
gamma-hat => ES. QED.  (So any efficient point weakly below the claims vector is a valid
"outside-core" candidate; the whole difficulty is UNDOMINATION.)

## 2. The strip construction (candidate universal escape).
delta = sum gamma-hat - v(N) > 0.  Build efficient y <= gamma-hat by removing total delta from
coordinates, never below the floor v({i}) (=> y an imputation, outside core by Lemma A).
Removing delta to reach EXTREME points (players pushed fully to their floor) is what makes y
undominated (the PES, an interior efficient point <= claims-capped, is DOMINATED — the known
dead route; extreme strips are not).

Reduction of domination for single-strip y = gamma-hat - delta*e_p (strip all delta onto p):
  - Only coalitions Q containing p block y (for p not in Q, y(Q)=gamma-hat(Q) >= v(Q)).
  - Domination via such Q needs a core x with x(Q)=v(Q), x_i > gamma-hat_i for i in Q\{p},
    and (by the tightness sum) gamma-hat_p - delta < x_p < gamma-hat_p - g(Q), g(Q)=gamma-hat(Q)-v(Q).
  So undomination of the single strip <=> the core has NO point tight on any p-coalition Q that
  sits strictly above gamma-hat off p and below gamma-hat_p - g(Q) on p.

## 3. Reverse-engineering the two certified witnesses (src/stES_explore.py, stES_allescapes.py)
Both non-ES witnesses have a single HUB h lying in every proper tight coalition; delta = 1.
- vN6 (hub, claims (1,1,3,1,1)): unique undominated arrangement-vertex escape is the SINGLE STRIP
  y = (1,1,3,1,0) = gamma-hat with player 4 dropped by delta to its floor 0.
- vN4 (canonical, claims (1,1,1,1,1)): THREE undominated escapes; one is the clean single strip
  y = (1,1,1,1,0). The other two boost the hub (0,1,1,2,0),(1,0,1,2,0) — not needed.
The stripped player in both is a CAPPED (non-strong-claimant) player pushed to its floor.

## 3b. CRITICAL REFRAMING — the open frontier is n >= 6, NOT n = 5.
Estévez-Fernández (2012): **large core <=> stable core for n <= 5**. Dietzenbacher: large => ES.
Hence **stable => ES is already a THEOREM for n <= 5** (his concluding remark says so).
Consequence: EVERY non-ES n=5 game is automatically non-large AND non-stable; my n=5
"core not stable" confirmations (below) validate the CONSTRUCTION but do NOT probe the open
question. The genuine test is n >= 6, where stable-but-non-large cores first exist. Two jobs:
  (i) prove the escape construction for general n (=> theorem all n); the construction is
      n-agnostic, so n=5 success is real evidence it is the right engine;
  (ii) at n=6 directly hunt a STABLE (no undominated escape) + NON-LARGE + NON-ES game
      (= counterexample) — my construction predicts none exists.

## 3c. Structural facts across n=5 AND n=6 (src/stES_structure.py)
n=5 (41 non-ES) and n=6 (59 non-ES) games:
  - subgame-core property: 100/100 (it is the PROVEN lemma 0c).
  - reduction (non-ES => NO core point <= gamma-hat): 100/100 (Lemma A, proven).
  - HUB (a player in EVERY proper admissible coalition): 41/41 at n=5 but only 56/59 at n=6.
    => the hub is an n<=5 artifact; at n>=6 the over-cover spreads across >=2 players
    (3 explicit no-hub n=6 non-ES games recorded). A hub-based proof does NOT generalize;
    the general argument must use the over-cover / subgame-core structure, not a single hub.

## 4. Empirical status — n=5 CONSTRUCTION VALIDATION (src/stES_test_construction.py)
n=5, 48 non-ES balanced games (point-generated exact + random balanced superadditive):
  - EVERY one (48/48) has an undominated arrangement-vertex escape => core non-stable.
  - single-strip undominated: 47/48; greedy vertex-strip 45/48. (n=5 is the KNOWN regime.)

## 5. THE ESCAPE CONSTRUCTION — two regimes (unified, both n=5 and n=6).
For non-ES v (delta = sum gamma-hat - v(N) > 0) the undominated escape is always one of:
  (S) SINGLE-STRIP: y = gamma-hat - delta*e_p, one capped player p dropped by delta to its
      floor-feasible value (needs gamma-hat_p - v({p}) >= delta). Works ~99% (n=5: 47/48).
  (B) HUB-BOOST: strip a satellite s FULLY to its floor v({s}) (freeing gamma-hat_s - v({s})
      >= delta) and put the surplus (freed - delta) on a HIGH-CEILING player t (large M_t).
      This handles the residual "hard" games where no single strip works (n=5 hard game;
      the n=6 candidate below). Escape sits at an arrangement VERTEX (satellite at floor).
Both keep sum y = v(N) and y outside core (Lemma A / extreme vertex). The PES (interior) is
dominated — extremeness (players pinned at floors) is what defeats domination.

## 6. n=6 FRONTIER RESULTS (the genuinely open regime) — src/stES_n6_fast.py
- Fast hunt over point-generated exact n=6 games; escape candidates screened by FAST float
  domination then EXACT-certified. NOTE: pure random float search is UNRELIABLE (misses thin
  escapes — the campaign's standing methods lesson), so it produced FALSE "stable" candidates.
- First flagged CANDIDATE (gamma-hat=(2,1,1,1,2,2), delta=1, hub=player 5 with M_5=6): single
  strip fails for ALL players, BUT deterministic HUB-BOOST finds the exact-certified escape
  **y=(2,1,1,1,0,3)** (strip satellite 4 to floor 0, boost hub 5 by 1; blocked by {4,5},{0,4,5},
  {2,4,5},{1,2,4,5},{2,3,4,5}; undominated — CERTIFIED). => its core is NOT stable. FALSE ALARM.
- Lesson: any "candidate stable non-ES" from float screening must be re-checked with the
  deterministic single-strip + hub-boost patterns before it is taken seriously.
- Re-run with deterministic hub-boost (seeds 31-34, ~20k point-generated games): single-strip
  + hub-boost + float resolves the vast majority; a handful of float-screen CANDIDATES survive
  (fractional delta, incl. NO-HUB games — the genuine n>=6 structure). These are NOT taken as
  counterexamples — they are re-checked deterministically:
  - cand0 (gamma-hat=(3/2,7/4,5/4,7/4,7/4,7/4), delta=3/4, hub=player 3): FULL arrangement
    enumeration (float-prescreened, exact-certified) found escape **y=(0,1,2,2,2,2)** (player 0
    to floor, a multi-strip/multi-boost vertex) => core NOT stable. FALSE ALARM.
  - cand1 (gamma-hat=(3/2,1/2,1,1/2,3/2,3/2), delta=1/2, NO hub, floors (1,0,0,0,1,0)) and
    cand2 (gamma-hat=(3/2,1,3/2,3/2,3/2,3/2), delta=1/2, NO hub, floors (1,0,1,1,1,0)):
    resist single-strip, hub-boost, low-gap vertex search (topk<=34), and the
    denominator grid d=2,3,4 (comprehensive per denominator). All 3 candidates PASS the
    Gillies/GS necessary condition (every singleton exact) so that cheap test does not
    rule out stability. DEFINITIVE test = full float-prescreened arrangement enumeration
    (10.4M vertices, exact-certified hits; validated by re-finding cand0's escape) is
    RUNNING on cand1,cand2. Verdict pending: escape found => false alarm; NO escape =>
    strong counterexample candidate requiring exact-domination confirmation.
    NOTE: these are point-generated EXACT non-ES n=6 games — a DIFFERENT class from the
    structured families (assignment, big-boss) that the campaign verified are ES, so they
    are the sharpest available probe of the open question. No verdict claimed yet.

## 6b. cand1 & cand2 VERDICT (2026-07-24, in progress) — POTENTIAL COUNTEREXAMPLES, NOT confirmed
- FULL float-prescreened arrangement enumeration (ALL coalition+floor vertices, ~5.0M
  non-singular vertices each, 8 parallel workers, exact-certified hits): **NO undominated
  escape found for EITHER candidate.** (Validated: same enumerator re-found cand0's escape.)
- Exact-domination re-enumeration (removes float-screen false negatives; exact certify of
  EVERY imputation-outside-core vertex) RUNNING for rigorous confirmation.
- *** CRITICAL COMPLETENESS CAVEAT (do not skip before any counterexample claim): ***
  The coalition+floor arrangement is NOT provably complete for the maximal-undominated set U.
  y is dominated via S iff y|S lies strictly below the Pareto frontier of the projected core
  face pi_S({core x : x(S)=v(S)}); that frontier's breakpoints are PROJECTED CORE-VERTEX
  coordinates, so boundary vertices of U can occur at planes "y_i = (core-vertex coord)_i",
  which are NOT coalition or floor planes. Hence "no escape among coalition+floor vertices"
  is strong evidence but NOT a proof of core stability. Before claiming a counterexample:
  (1) finish exact-domination enumeration; (2) EXTEND the arrangement with core-vertex-
  coordinate planes and re-enumerate; (3) cross-check via a complete external-stability test
  (Grabisch-Sudholter nested balancedness, or a direct undominated-imputation feasibility).
  Prior: the theorem is widely expected TRUE (35,854 stable assignment games + all stable
  big-boss ES; n<=5 proven). A stable-core exact non-ES n=6 game would be a MAJOR negative
  resolution — so the bar for claiming it is a COMPLETE stability certificate, not just this.
  LESSON CONFIRMED (campaign standing note): escapes can be complex multi-strip/multi-boost
  arrangement vertices; single-strip + hub-boost + random float ALL under-detect them, so the
  hunt's "candidate" flags are float-screening false negatives, not stable cores. Reliable
  verdicts need deterministic vertex enumeration.

## 6c. cand1/cand2 have 1-DIMENSIONAL (segment) cores — reframes them as likely FALSE ALARMS.
Affine-hull reduction (src/stES_corevx2.py): both cores are a LINE SEGMENT (affine dim 1,
12 fully-tight coalitions each).
  cand1 core = [A=(1,1,0,1,3,0), B=(2,0,1,0,1,2)]   cand2 core = [A=(3,0,2,2,1,0), B=(1,1,1,1,2,2)]
Precedent (team-lead): paper-2's canonical ES witness was ALSO a 2-vertex segment core, and
its escape was found readily. Geometric read: a 1-D core cannot be externally stable in a 5-D
imputation simplex, so an undominated escape almost surely EXISTS — it just lives on the
domination-boundary planes the plain coalition+floor arrangement omits, which is why the base
re-enum found 0 survivors.
COMPLETE characterization for a segment core [A,B]: domination is ONLY by (i) A, on coalitions
S with A(S)=v(S); (ii) B, on S with B(S)=v(S); (iii) interior points x_t=(1-t)A+tB, on
FULLY-TIGHT coalitions. So the undominated-set vertices lie on planes {coalition, floor,
y_i=A_i, y_i=B_i, and pairwise segment-support (y_i-A_i)(B_j-A_j)=(y_j-A_j)(B_i-A_i)}. Adding
the <=15 pairwise planes makes the arrangement COMPLETE => a rigorous stability certificate.
Passes: coalition+floor (base, 0 surv) -> +coordinate (reenum3, 0 surv) -> +pairwise
(reenum4, COMPLETE) [gating on cand0 then running]. Fast conservative-margin screen throughout
(no false negatives; validated on cand0's escape).

## 6d. COUPLED-FAILURE evidence for the theorem (for the write-up).
If cand1/cand2 resolve as false alarms (escapes found), the campaign-wide pattern is:
the SAME thin, over-covered structure that makes a game non-ES (admissible coalitions
over-cover N, sec 0d; claims inflate past v(N)) is ALSO what makes its core non-stable
(the thin core cannot dominate the outside region). Non-ES and non-stable fail TOGETHER,
across: our exact witnesses + all paddings (agent_stable Part B); 35,854 stable assignment
games all ES; all stable big-boss games convex hence ES; every non-ES game at n=5 (complete)
and n=6 (this hunt). Under this reading the hunt's negative results are THEOREM-SUPPORT, not
search failure: "stable => ES" looks TRUE, with the coupled thin-core mechanism as the reason.
The remaining gap is the general PROOF that stability forces the admissible over-cover to pack
into a core point <= gamma-hat (sec 0b crux).

## 6e. SEGMENT-CORE COMPLETENESS THEOREM (the certificate that surv=0 => STABLE) — PROOF.
Setup: core(v) is the segment [A,B] (2 vertices, affine dim 1). For a coalition S let
F_S = {x in core : x(S)=v(S)} and opt_S(y) = max_{x in F_S} min_{i in S}(x_i - y_i); y is
dominated via S iff opt_S(y) > 0, and y is undominated iff opt_S(y) <= 0 for ALL S.
U := {imputations y : opt_S(y) <= 0 for all S} is the set of undominated imputations; core C ⊆ U;
STABLE <=> U = C.

Lemma 1 (domination sources). Since A(S), B(S) >= v(S) for the core points A,B and x_t(S)=
(1-t)A(S)+tB(S) is affine in t, F_S is exactly: the whole segment if A(S)=B(S)=v(S)
("fully-tight"); {A} if only A(S)=v(S); {B} if only B(S)=v(S); empty otherwise. So the only
dominating core points are A, B, and interior x_t on fully-tight coalitions. (Proof: min over
the segment of x_t(S) is at an endpoint; =v(S) forces that endpoint tight.)

Lemma 2 (opt_S is concave PWL; its affine pieces). min_{i in S}(x_t,i - y_i) is jointly concave
in (t,y) (min of affine) and F_S convex, so opt_S is CONCAVE in y, hence a MIN of affine
functions. Its affine pieces are: (i) y -> A_i - y_i and y -> B_i - y_i (endpoint/coordinate
pieces, boundaries y_i=A_i, y_i=B_i); (ii) for a fully-tight S the interior-t optimum, where
two coordinates i,j in S tie x_t,i - y_i = x_t,j - y_j = opt_S at the same t in [0,1]: solving
the tie gives t=(y_i - y_j -(A_i-A_j))/((B_i-B_j)-(A_i-A_j)) and opt_S = [Dj y_i - Di y_j]/
(Di-Dj)+const with Di=B_i-A_i, whose zero locus is the PAIRWISE plane Dj(y_i-A_i)=Di(y_j-A_j),
i.e. (y_i-A_i)(B_j-A_j)=(y_j-A_j)(B_i-A_i). (Verified concretely: cand1 fully-tight S={0,1},
A|S=(1,1),B|S=(2,0): the interior-t domination boundary is y_0+y_1=2, exactly the pairwise
plane.) A 3-way interior tie is the intersection of two such pairwise planes, so pairwise
planes suffice.

Theorem (completeness). {opt_S<=0} = union over affine pieces l of {l(y)<=0} (sublevel of a
min-of-affines = union of halfspaces). Hence U = intersection_S (that union) ∩ simplex is a
finite UNION OF POLYTOPES, each cut out only by planes from
  P := { coalition y(S)=v(S), floor y_i=v({i}), efficiency, coordinate y_i in {A_i,B_i},
          pairwise (y_i-A_i)(B_j-A_j)=(y_j-A_j)(B_i-A_i) }.
If U ⊋ C, pick y0 in U\C; it lies in some polytope piece Pc ⊆ U with Pc ⊄ C. Because C is
CONVEX and cut by linear y(S)>=v(S), Pc ⊄ C implies some VERTEX w of Pc is outside C (else
Pc=conv(vertices) ⊆ C). w in U (Pc ⊆ U), w not in C: an undominated imputation outside the
core at a VERTEX of the arrangement of P. Therefore: **enumerating all vertices of the P-
arrangement and finding NO undominated one certifies U=C, i.e. the core is STABLE.** QED.
(reenum4 enumerates exactly this arrangement; the pairwise class = 15 planes for all pairs is a
superset of what's needed, which only adds candidate vertices, never removes the escape vertex.)

LATTICE-GAP LEMMA (closes the outside-core/imputation classification skip — the last gate).
For cand1/cand2 ALL data are integers: v(S) integer (point-generated from integer vectors), and
the endpoints A,B are integer. Every arrangement plane row is integer (coalition/floor/coordinate
0/1; pairwise entries B_i-A_i in [-2,2]; efficiency all 1) and every rhs is integer. So each 6x6
basis matrix M is INTEGER; if non-singular, det(M) is a NON-ZERO INTEGER, |det(M)| in {1,...,D}.
D bound: Hadamard gives |det| <= 173 (empirical max over 500k random bases: 24 for cand1, 32 for
cand2). By Cramer each vertex coordinate is (integer)/det(M), denominator <= D, so every classifier
value y(S)-v(S), y_i-v({i}) is either 0 or has magnitude >= 1/D >= 1/173 ≈ 5.8e-3. The float solve
of a non-singular integer system is accurate to ~1e-12 (cond·eps·||y||; the |det|>=1 filter excludes
singular bases, so no ill-conditioning), and the classifier tolerance is 1e-7. Since
  lattice spacing (>= 5.8e-3)  >>  tolerance (1e-7)  >>  float error (~1e-12),
a strict exact violation can never float as non-violation and vice versa: the float
inside-core / not-an-imputation / blocking classification is EXACT on the entire vertex set.
Hence NO vertex is wrongly discarded before the exact stage; combined with the domination-skip
guarantee below, reenum4's "surv=0" is fully rigorous. (src verifying D: one-off det sweep.)

No-false-negative guarantee of the DOMINATION skip: a vertex is SKIPPED only when exact_dom_ok verifies
an exact rational core point x* with x*(S)=v(S), x*_i>y_i for all i in S (a genuine exact
dominator) — so every skip is exactly justified; borderline float margins (<=1e-4) fail the
>MARG test and go to full exact certify_undominated. Hence a true escape is never skipped.
Validated: reenum4 re-finds cand0's escape and (n=5 acid test, src/stES_validate_n5.py) the
canonical segment-core NON-STABLE witness's escape (0,1,1,2,0).

## 6f. VERDICT — RESOLVED NEGATIVELY (joint verification PASSED; published in paper2 v2).
reenum4 COMPLETE pass, full arrangement (89 planes, 41,507,642 vertices enumerated to the last
ordinal, 20.8M non-singular, 4.5M outside-core each): SURVIVORS=0, ESCAPES=0 for BOTH cand1,cand2.
By the completeness theorem 6e (+ lattice-gap lemma + no-false-negative screen), this RIGOROUSLY
certifies core(cand1), core(cand2) are vNM-STABLE. Both are exact and non-ES (two independent
egalitarian-procedure implementations agree; gamma-hat sums 13/2, 17/2 > v(N)=6, 8).
=> **"stable core => egalitarian stable" is FALSE. Dietzenbacher (2021) second open question
resolved NEGATIVELY.** Joint independent verification with team-lead PASSED (my side: completeness
theorem + lattice lemma + reenum4 + battery; team-lead side: non-ES, exactness via the two-point
generator lemma v=min(A,B), segment geometry, Estévez-Fernández n=6 minimality). Claim published:
paper2 extended to "Exact and stable games need not be egalitarian stable" (v2). Witnesses:
results/WITNESS_STABLE_NONES_cand{1,2}.json.

## 7. STATUS OF BOTH HALVES OF DIETZENBACHER'S QUESTION.
- EXACT half: NO (exact ⇏ ES), resolved earlier this campaign (certified n=5 witnesses; sec 3, theory_es_notes).
- STABLE-CORE half: **NO (stable core ⇏ ES)**, resolved here (cand1/cand2, n=6, minimal per Estévez-Fernández).
Both halves NEGATIVE. The proven partial theory (reduction 0b, Lemma A, subgame-core 0c,
over-cover 0d, domination geometry 0e) stands as the structural backbone; the earlier
"theorem appears TRUE" reading was OVERTURNED by the segment-core witnesses — thin 1-D cores are
exactly where a non-ES game can still be stable, because a segment core, while unable to be
LARGE, CAN be externally stable (it dominates the outside region coalition-by-coalition even
though no single core point lies below gamma-hat). The coupled-failure heuristic (6d) is thus
FALSE in general: non-ES and non-stable do NOT always fail together — cand1/cand2 are non-ES yet
stable. Lesson logged.

## 8. TERMINAL SUMMARY (lane closed).
HEADLINE: **stable core ⇏ egalitarian stable** — Dietzenbacher (2021) second open question
resolved NEGATIVELY by two certified n=6 witnesses (cand1, cand2), the campaign's biggest result.
Both are exact, balanced, non-ES, with a 1-DIMENSIONAL (segment) core that is nonetheless
vNM-STABLE.

How it was found (route + method, for the record):
1. Reframed the frontier to n>=6 (n<=5 known via Estévez-Fernández large<=>stable + Dietzenbacher
   large=>ES). Built the escape construction (single-strip; hub-boost) and proved the reduction
   stable=>ES <=> [stable => ∃ core point <= gamma-hat] (0b), Lemma A (1), subgame-core (0c),
   over-cover characterization (0d), domination-region geometry (0e).
2. Biased point-generation (min of few integer vectors => thin cores) surfaced non-ES n=6 games
   that resisted all escape search; the standing methods-lesson (float sampling misses thin
   escapes; deterministic enumeration needed) forced the exhaustive arrangement enumeration.
3. Key structural discovery: their cores are SEGMENTS (affine dim 1, 12 fully-tight coalitions).
   That collapsed external stability to a COMPLETE finite test (6e): domination sources are only
   A, B, and interior x_t on fully-tight coalitions => the undominated set U is a union of
   polytopes cut by {coalition, floor, endpoint-coordinate, pairwise segment-support} planes;
   C convex => U!=C forces an arrangement-vertex escape. Enumerating all such vertices with a
   no-false-negative conservative-margin screen and the integer-lattice classification lemma
   gives a RIGOROUS stability certificate at float speed. 0 escapes => STABLE.
4. Validated end-to-end: reenum4 re-finds cand0's escape; the n=5 acid test re-finds the
   canonical segment-core NON-stable witness's escape; pairwise-plane formula = actual
   domination boundary; lattice lemma closes the classification skip; full 41.5M-vertex coverage
   confirmed from checkpoints.

Reusable assets: src/stES_reenum4.py (complete segment-core stability certifier),
src/stES_validate_n5.py (acid test), src/stES_corevx2.py (affine-hull core-vertex reduction),
src/stES_verify_witness.py (battery), results/WITNESS_STABLE_NONES_cand{1,2}.json.
Correction trail (honest): retracted a wrong "U convex" claim (U is non-convex; D_S convex);
one over-broad pkill damaged other lanes (fixed discipline: kill by exact script name only).
Both halves of Dietzenbacher's question are now NEGATIVE. Lane CLOSED.
