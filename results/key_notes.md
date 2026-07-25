# (KEY) attack — agent notes

TARGET (KEY): slack(W) <= slack(T*), equivalently v(W) >= phi(P) + v(T*).
Setup: exact game v, phi = leximin core point, star_S fails at phi with Farkas cover
(lambda_U>=0 on tight U, sigma, r_k=sigma-sum_{U∋k}lambda_U; r>=1 on S, r=0 off S).
W=union cover coalitions, P=N\S⊆W, T*=W∩S, R=S\W (r=sigma). slack(A)=phi(A)-v(A).
(KEY) proven for r CONSTANT on T* (Steps 4-5, convexity); open for non-constant r.

## DECISIVE NEGATIVE RESULTS (this agent) — two proof routes KILLED

### 1. Instant lattice route is DEAD. (team-lead's "start here")
Claim tested: is the tight-set family at phi closed under union/intersection, making
W = union of tight cover coalitions itself tight (=> slack(W)=0 => KEY instant)?
- THEORY: at a core point, for tight A,B: phi(A∪B)+phi(A∩B)=v(A)+v(B) (modular), and
  core gives phi(A∪B)>=v(A∪B), phi(A∩B)>=v(A∩B). So
     slack(A∪B) + slack(A∩B) = v(A)+v(B) - v(A∪B) - v(A∩B).
  This forces BOTH tight only if v is SUPERMODULAR on the pair. Exact games are NOT
  supermodular. So lattice-closure is NOT automatic. (It does force the submodular
  inequality v(A)+v(B) >= v(A∪B)+v(A∩B) at every tight pair, but not tightness.)
- EMPIRICS (src/_key_screen.py, n=5): among star-fails, W is NOT tight in 63/78 and
  74/90 (two seeds). W tight only ~18%. So slack(W)>0 generically. LATTICE ROUTE DEAD.

### 2. Constant-on-T* cover route is DEAD (sharp witness). (kills the Steps 4-5 rescue)
Question (Q1): for every star-fail, does there exist SOME Farkas cover whose residual r
is constant on its T* (i.e. a 2-valued cover: rho on T*, sigma on R)? If yes universally,
Steps 4-5 convexity would prove (KEY) by cover choice, closing everything.
- ANSWER: NO. Explicit exact witness (n=6):
    v = [0,1,8,9,5,8,15,18, 1,2,9,10,7,10,17,20, 2,3,10,11,10,13,20,21, 3,4,11,12,12,14,21,22,
         0,3,10,12,5,8,15,18, 2,5,12,13,7,10,17,20, 5,6,13,14,10,13,20,23, 6,7,14,15,12,15,22,25]
    phi = (2,9,7,2,4,1), gains (1,1,2,1,2,1).
    S = {0,1,2,4,5}. Found cover: {0,1,2,3}:1, {0,3,5}:1, {1,3,5}:1, sigma=3;
      r = (0:1,1:1,2:2,4:3,5:1). W={0,1,2,3,5}, T*={0,1,2,5}, P={3}, R={4}.
      r on T* = (1,1,2,1)  NON-constant.
    src/_key_constcover.py enumerates ALL splits S=T0⊍R0 and tests feasibility of a
    2-valued cover (rho on T0, sigma on R0, in normal cone): CONST_COVER_EXISTS = FALSE.
  So NOT merely "some cover is non-constant" — for this S NO 2-valued cover exists at all.
  The elementary convexity proof cannot be salvaged by re-choosing the cover.
- Yet (KEY) HOLDS here: slack(W)=1, slack(T*)=1, margin v(W)-rhs = 20-20 = 0 (tight).
  So this is a genuine non-constant, W-not-tight, KEY-tight instance — the real crux.

## ============================================================================
## DECISIVE RESULT: (KEY) IS FALSE.  (this agent) — resolves the open question
## ============================================================================
Certified EXACT counterexample (n=6), fully verified in exact rationals
(src/_key_verify_lean.py, _key_confirm.py; witness results/WITNESS_KEY_FALSE_n6.json):

  v = [0,5,1,9,3,8,9,14, 3,11,4,12,12,19,13,21, 3,8,6,14,6,11,12,17, 8,16,9,17,17,22,18,26,
       1,6,4,12,4,9,10,15, 6,14,7,15,15,20,16,24, 4,9,9,15,7,12,13,18, 11,19,12,20,18,23,21,29]
  EXACT: min_core x(T)=v(T) verified for ALL 62 proper T (num_nonexact=0).
  phi = leximin = (20/3, 8/3, 19/3, 6, 14/3, 8/3), in core.

  S = {0,2,3,4}: star_S FAILS. residual_cover gives valid Farkas cover
    {1,2}:1, {0,1,5}:2, {2,3,5}:1 (sigma=3, r=(0:1,2:1,3:2,4:3); lambda>=0 on phi-tight
    coalitions, r>=1 on S, r=0 off S, phi maximizes r.x over core -- all checked).
    W={0,1,2,3,5}, T*=W∩S={0,2,3}, P={1,5}, R={4}.
      v(W)=24,  phi(P)=16/3,  v(T*)=19.
      (KEY) v(W) >= phi(P)+v(T*)  is  24 >= 16/3+19 = 73/3.  FALSE by margin -1/3.
    Step-6 certificate ALSO FALSE: M^(T*)=max{x(S):core, x(T*)=v(T*)} = 24 > phi(S)=71/3.
      Independent core WITNESS x=(7,2,8,4,5,3): in core, x(T*)=19=v(T*), x(S)=24>71/3.
  S = {0,2,3,5}: same game, symmetric second counterexample (margin -1/3, M^(T*)=22>65/3).

BATCH EVIDENCE (src/_key_float.py, float-screen + exact recheck of every suspect margin;
biased thin-core point games): ~9000 star-fails at n=6 + n=7, 10 DISTINCT (KEY)
counterexamples (n=6 AND n=7). (KEY) violations are RARE (~0.1% of star-fails) -- which
is why prior thin random sampling wrongly reported "(KEY) verified universal". A biased
generator (thin cores k=2,3, nested tight chains) + float screening surfaces them.

## CONSEQUENCE FOR THE PROOF
- (KEY) is NOT a theorem. The "REDUCTION THEOREM" that consolidates leximin coalitional
  monotonicity onto (KEY) is therefore NOT a valid proof -- it rests on a false lemma.
  Steps 4-7 (certificate T*=W∩S) are broken: both (KEY) and M^(T*)<=phi(S) fail.
- The elementary CONSTANT-r route (Steps 4-5) was already shown unrescuable (no 2-valued
  cover exists for some S, section 2 above); now the GENERAL (KEY) target is outright FALSE.

## BUT the THEOREM (Lemma D) is NOT refuted by any counterexample found.
In ALL 10 (KEY)-violation cases: d*(S)=0 <= slack, i.e. S is NOT binding-bumpable, so
Lemma D holds vacuously (checked exact for the n=6 witness, float for all 10; 0 refutations).
The non-bumpability is certified by a DIFFERENT coalition than T*=W∩S (some C!=S with
max{x(S):core,x(C)=v(C)}=v(S) forces x(S) to its floor).

## REVISED TARGET for a correct proof (this agent's recommendation)
The right theorem-level invariant is NOT (KEY) but:
   (D0)  star_S fails at phi  ==>  d*(S)=0
         i.e. EXISTS a coalition C!=S with max{x(S): x in core, x(C)=v(C)} = v(S).
Empirically d*(S)=0 in EVERY star-failure ever seen (this agent's 10 (KEY)-violations all
have d*=0, plus all prior background hunts). The certificate coalition is generally NOT
W∩S. A proof must produce this C from the star-failure structure directly; the cover's
W∩S is the wrong vehicle. [Note: prior notes' "Conjecture C singleton" and "pair" ideas
were early attempts at exactly this C; they were abandoned for the cover route, which is
now shown false. The C-hunt should be revived.]

## (old status line, now superseded:) "STATUS OF (KEY): still VERIFIED" -- WRONG, (KEY) is FALSE.

## Reduction attempt (this agent): (KEY) <=> GOAL-H, but GOAL-H is EQUIVALENT not weaker.
Let y be any core floor point of the face F={x: x(W)=v(W), x(T*)=v(T*)} (exists —
simultaneous flooring, verified). d = phi - y. Cover depth c_k = sigma - r_k
(= sum_{U∋k}lambda_U): c=sigma on P, in (0,sigma] on T*, 0 on R. Algebra:
  r·d >= 0 (phi maximizes r·x, y in core)  and  c·d = sum_U lambda_U(v(U)-y(U)) <= 0
  (each U tight, y in core). Both reduce to the SAME identity. One gets
     sigma·d(P) <= sum_{k∈T*}(sigma-r_k)(y_k-phi_k) = -sum_{k∈T*} c_k d_k.
  So (KEY)=[d(P)<=0]  <==  GOAL-H: sum_{k∈T*} c_k(phi_k - y_k) >= 0.
  BUT y(P)=v(W)-v(T*) is CONSTANT over all y∈F, so d(P)=phi(P)-(v(W)-v(T*)) is
  independent of y, and GOAL-H is algebraically EQUIVALENT to (KEY) — a cleaner
  restatement, not a reduction. In the hard case above GOAL-H holds with equality
  (c=(2,2,1,2) on T*, d=(-1,-1,2,1), sum = 0). phi is NOT >= y pointwise on T*
  (d has negative entries): (KEY) is a genuinely global/weighted fact, not monotone.
CONCLUSION: the missing ingredient is non-algebraic — must couple leximin's stratum
structure with exactness (matches the standing attack-log verdict). No new algebraic
identity closes it; the constant-cover and lattice shortcuts are both provably unavailable.

## HARNESS NOTE (discipline catch #15, per team-lead)
lemD.py binding_bumpable() is the NAIVE notion (max_core x(S) - phi(S) > 0); it returns
True on the (KEY)-FALSE witness (4/3 > 0) even though d*(S)=0. Operative notion is
max_exact_bump / exact_bumpable. NONE of this agent's _key_*.py used binding_bumpable();
all decisive bump checks went through max_exact_bump (exact) or a float d* sweep.

## ============================================================================
## (D0) CORRECTION + CERTIFICATE-STRUCTURE REGRESSION (this agent, per team-lead)
## ============================================================================
CORRECTION: the revised target (D0) "star-fail => d*(S)=0" is FALSE. Over a broad corpus
(~130k star-fails, biased thin-core exact games n=6,7) ~0.2% of star-fails have d*(S)>0
(seen d*=1 and d*=2), yet ALWAYS d*<=slack. My earlier "d*=0 in every star-failure" was
an artifact of measuring only the 139 (KEY)-violations (a biased subsample). The correct
theorem-level invariant is the ORIGINAL Lemma D:
   (D-cert)  star_S fails at phi  ==>  EXISTS C != S with M^(C):=max{x(S):core,x(C)=v(C)} <= phi(S).
   (equivalently d*(S) <= slack; the floor version M^(C)=v(S) [d*=0] is strictly stronger
    and NOT universal.)
PRIORITY-1 SAFETY: 0 theorem refutations (d*>slack) anywhere. Checked exactly on the n=6
(KEY)-witness and on all 139 (KEY)-violations; float d*<=slack on every d0_bad case
(src/_d0_safety.py, _dcert_mine.py). Lemma D intact.

CERTIFICATE STRUCTURE (the deliverable; src/_dcert_mine.py, ~8000 star-fails n=6+n=7):
 - THEOREM cert exists: 100% (0 missing).
 - The cert can ALWAYS be taken as a SUBSET OF S lying within a SINGLE leximin stratum: 100%.
 - A SINGLETON cert works: 99.9% (one n=7 case needed a same-stratum PAIR).
 - min thm-cert size: avg 1.00, max 2. subset-of-S ~85%, single-stratum 100%.
 - Floor-certs (d*=0) are NEVER phi-tight (PROVEN: a phi-tight floor-cert C puts phi on
   {x(C)=v(C)} where max x(S)=v(S), forcing phi(S)=v(S), contradicting slack>0). This
   REFUTES the "C = union/intersection of phi-tight sets from different strata" hypothesis:
   the certificate lives OFF the tight-set family, inside S, within one stratum.

CLEAN NEW TARGET (replaces the false (KEY)):
   (STRAT-CERT)  star_S fails at phi(exact v)  ==>  EXISTS nonempty C subset of S, all of C
                 in ONE leximin stratum, with max{x(S): x in core, x(C)=v(C)} <= phi(S).
   Realizable by a SINGLETON k in S in 99.9% of cases:  (SINGLE-CERT) exists k with
   M^({k}) <= phi(S).  Verified EXACTLY on the (KEY)-FALSE witness: C={0} (stratum 0),
   M^({0})=v(S)=22 <= phi(S)=71/3 for S={0,2,3,4}. This is the revived Conjecture-C
   singleton/pair form, now with the correct <=phi(S) (not =v(S)) bound and the
   single-stratum structural constraint that makes it universal.
   WHY IT'S TRACTABLE: C subset S (not the sprawling W); single stratum couples leximin
   strata with exactness directly; small (singleton/pair). This is the recommended proof
   target. Tooling: src/_dcert_mine.py (structure regression), src/_d0_safety.py (d* safety).

## Stratum-location refinement (this agent): the singleton cert k can be taken IN S
## (M^({k})<=phi(S), k in S): 100% over 1300 star-fails (n=6,7). But it is NOT confined to
## the lowest stratum of S (a lowest-S-stratum cert exists only ~50%): the certificate
## lives in SOME single stratum, which one varies. So the proof cannot fix the stratum a
## priori; it must show SOME S-member's floor caps x(S) at phi(S). Rare (~0.1%) cases need
## a same-stratum PAIR in S instead of a singleton (still subset-of-S, single-stratum:
## (STRAT-CERT) is the 100% universal form).

## ============================================================================
## SHARPENED TARGET (this agent): the MIN-RESIDUAL member of S is the certificate
## ============================================================================
Data (src /tmp/rtest.py-style, ~1100 star-fails n=6,7): among singleton certs, the
certifying k is (essentially always) a MINIMUM-RESIDUAL member of S. With the residual
cover r (r_i>=1 on S, r=0 off S, rho:=min_S r_i = 1 provably), let k satisfy r_k=1. Then
   (RMIN-CERT)  M^({k}) := max{x(S): x in core, x_k = v({k})} <= phi(S).
Match rate: n=6 99.6%, n=7 100% (coincides with "a singleton-in-S cert exists"; the
~0.4% n=6 residue is the pair-cases where no singleton certifies at all -> use STRAT-CERT
same-stratum pair). Verified exactly on the (KEY)-FALSE witness: r=(0:1,2:1,3:2,4:3) on
S={0,2,3,4}, min-residual members {0,2}, and BOTH {0},{2} certify (M=v(S)=22<=71/3).

PARTIAL ALGEBRA (exact remaining gap). phi maximizes r.x over the core, so for all core x
   Sum_{i in S} r_i x_i <= Sum_{i in S} r_i phi_i.
Writing r_i = 1 + (r_i-1) (r_i-1>=0, =0 at the min-residual k):
   (**)  x(S) - phi(S) <= Sum_{i in S} (r_i - 1)(phi_i - x_i).
(RMIN-CERT) needs LHS<=0 for every core x with x_k=v({k}). (**) reduces this to
   Sum_{i in S, r_i>1} (r_i-1)(phi_i - x_i) <= 0   for all core x with x_k = v({k}).
i.e. flooring the min-residual member k must force the HIGHER-residual S-members to sit at
or above their phi-values in the (r_i-1)-weighted sense. The x_k=v({k}) constraint is the
unused ingredient; (**) alone (no flooring) does NOT close it. This is the concrete open
inequality — a per-player statement, far tighter than (KEY), and the recommended proof
handle. [Honest status: not closed. Attack log: KEY false; lattice/W-tight dead; constant-
cover dead; d*=0 false; certificate = min-residual singleton of S, reduces to (**)-gap.]

## PROOF ATTEMPT on (RMIN-CERT) — dual certificate, PARTIAL (honest wall)
M^({k})<=phi(S) has an exact LP-dual certificate (DUAL-k): exists alpha_A>=0 on phi-tight
A, beta, gamma>=0 with coverage  beta on N\S, beta-1 on S\{k}, beta+gamma-1 on {k}
(then M^({k}) <= phi(S) - gamma*g_k <= phi(S), g_k=phi_k-m_k>=0). CONSTRUCTIVE ATTEMPT:
take alpha = (residual cover lambda) + alpha', where alpha' is supported on phi-tight
coalitions CONTAINED IN S and supplies coverage (r_i-1) on S\{k}. This works iff
   (COVER-S)  the deficiency (r_i-1)_{i in S\k} is realizable by nonneg combos of
              phi-tight subsets of S.
TESTED (/tmp/covertest.py): COVER-S feasible only 68% (n=6) / 57% (n=7). So the
tight-subsets-of-S construction is INSUFFICIENT (fails ~1/3), even though (RMIN-CERT)
itself holds ~99.6%. Typical failure: S with NO tight proper subsets but a member i with
r_i>1 (e.g. S={1,3}, r=(2,1), no tight subset) -- the certifying alpha must then use
phi-tight coalitions CROSSING S (covering off-S players too), i.e. the general (DUAL-k)
with beta>0 on N\S. Constructing that alpha from the star-fail data is OPEN. This is the
current frontier: (DUAL-k) is equivalent to the claim (strong duality), so a proof needs a
genuine construction of the crossing dual cover, not the S-internal one.

## ============================================================================
## SELECTOR MINING (this agent, per team-lead addition 2) — the certifier is computable
## ============================================================================
For each star-fail, coverage depth c_k := sigma - r_k on S (c_k MAX <=> r_k MIN; on the
(KEY)-witness cert k=0 has c=2 = max). Data src/_selector.py (~1000+ star-fails n=6, 800 n=7):
 - In EVERY star-fail, SOME max-coverage member of S certifies (M^({k})<=phi(S)):  maxc none = 0 (100%).
 - When the max-coverage member is UNIQUE, it ALWAYS certifies: 55/55 = 100% (n=6 checkpoint).
 - P(cert | k is max-coverage) ~ 77% (n=6) / 70% (n=7);  P(cert | k not max-coverage) ~ 7-8%.
   (In a TIE, ~50% of the time ALL tied max-coverage members certify; always at least one does.)
 - STRAT-CERT universal form (single-stratum subset-of-S cert of size <= 2 EXISTS): 100%.
SELECTOR THEOREM (candidate, the sharp target):
   star_S fails ==> a MAX-COVERAGE member k of S (c_k=sigma-r_k maximal, i.e. r_k minimal)
   has  M^({k}) <= phi(S).  Unique-max case is clean (100%); ties need "some", not "any".
This collapses the proof to ONE LP-duality statement about a max-coverage member k -- exactly
the (DUAL-k) certificate with that specific k. Safety batches (dcert_safety_*.log): 0 theorem
refutations (thmBAD=0) over the continuing sweep.

## EXACT CERTIFICATION of the d*>0 correction (catch #16, per team-lead addition 1)
Two EXACT n=6 star-fails with d*>0 (results/WITNESS_dstar_positive_n6.json), fully exact
(game exact all 62 T; phi=leximin in core; star fails; d*=max_exact_bump exact):
 CASE A [d*=2 SHARPNESS EXHIBIT] S={0,2,3,5}, v(N)=28. phi=(3,6,5,1,7,6). phi(S)=15,
   v(S)=8, slack=7. cover sigma=3, r=(0:1,2:1,3:3,5:1), coverage c=(2,2,0,2). EXACT d*(S)=2
   (>0), d*<=slack (2<=7): Lemma D holds. Max-coverage members {0,2,5} ALL certify:
   M^({0})=15, M^({2})=13, M^({5})=14, all <= phi(S)=15.
 CASE B [d*=1] S={0,1,3,4}. phi=(4/3,7/3,7/3,4/3,16/3,13/3). phi(S)=31/3, slack=7/3.
   EXACT d*(S)=1 (>0), <=slack. Max-coverage {0,3} certify: M=9 <= 31/3.
These EXACT certificates confirm: d*=0 is FALSE (d* can be 1 or 2), but d*<=slack always,
and the max-coverage singleton certificate M^({k})<=phi(S) holds. Catch #16 now rests on
exact rationals, not float. [tool: src/_exactcert.py; each exact LP ~2.5s, ~6min/case.]

## ============================================================================
## LANE CLOSED (team-lead, mission complete). Final index of this agent's results.
## ============================================================================
1. (KEY) slack(W)<=slack(T*) is FALSE. Certified exact n=6 witness, independently
   verified by team-lead. WITNESS_KEY_FALSE_n6.json. Kills the REDUCTION THEOREM route.
2. Two rescue routes killed with proof: instant-lattice (W not tight ~82%; exact != supermodular)
   and constant-on-T* cover (no 2-valued cover exists for some S).
3. (D0) "star-fail => d*=0" is FALSE (catch #16). Exact d*=2 and d*=1 exhibits
   (WITNESS_dstar_positive_n6.json). Operative invariant is the original Lemma D: d*<=slack.
4. Theorem (Lemma D / coalitional monotonicity) INTACT: 0 refutations over ~140k star-fails
   (n=6,7), exact on the n=6 witness + all 139 (KEY)-violations, float d*<=slack elsewhere.
5. Certificate structure: star-fail => EXISTS C subset S in ONE leximin stratum, |C|<=2,
   M^(C):=max{x(S):core,x(C)=v(C)} <= phi(S)  [(STRAT-CERT), 100%]. Generic (~99.6%): a
   MAX-COVERAGE member k of S (c_k=sigma-r_k max <=> r_k=1 min) has M^({k})<=phi(S)
   [(SINGLE-CERT)]; unique max-coverage member certifies 100%. Certs are NEVER phi-tight
   (proven) -> the tight-set-union hypothesis is refuted.
6. Strong-duality reduction: the whole conjecture reduces to constructing (DUAL-k) for a
   max-coverage k -- a nonneg combo of phi-tight coalitions with coverage (beta off S, beta-1
   on S\k, beta+gamma-1 on k), gamma>=0. Remaining exact gap for core x with x_k=v({k}):
       Sum_{i in S\k} (r_i-1)(x_i - phi_i) <= 0.
   S-internal cover ~2/3 feasible; needs phi-tight coalitions CROSSING S. THIS is the named
   leave-off frontier: "here is exactly the object whose construction is the proof."
Tools: src/_key_float.py, _dcert_mine.py, _selector.py, _exactcert.py, _d0_safety.py,
_key_constcover.py, _key_verify_lean.py, _key_confirm.py.

## FINAL SAFETY-NET COUNTS (lane closed, batches wound down)
Post-closure d*<=slack sweep (src/_dcert_mine.py, seeds 811/812/813 n=6, 821 n=7):
14000 additional star-fails, thmBAD (theorem refutations, d*>slack) = 0. Combined
with prior corpus: ~140k star-fails at n=6,7, ZERO Lemma-D refutations. Batches stopped.
