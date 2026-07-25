# Lemma D — deep attack (agent: theory-lemD)

TARGET: exact game v, phi = leximin-above-floors core selection, S a binding-bumpable
proper non-singleton coalition. Show the cone condition (star_S) holds at phi(v).
WIN = proof or certified counterexample, no partials.

VERIFIED-EQUIVALENT DUAL (from notes, 200/200): (star_S) FAILS iff phi maximizes some
weighted sum sum_{k in S} r_k x_k with all r_k >= 1 over Core(v). Binding-bumpability
excludes uniform r. So: prove an exact game's leximin point never maximizes a
non-uniform positive-S-weighted sum over the core at binding-bumpable S — or find a
counterexample.

## Clean reformulations established (this agent)

(R1) [Pareto form] (star_S) FAILS  <=>  every core point y with y_i >= phi_i for all
     i in S has y_i = phi_i for all i in S. I.e. phi|_S is PARETO-MAXIMAL in the
     S-projection of the core: no core point weakly raises all S-members with one
     strict. Proof: if y_i>=phi_i on S and y(S)<=phi(S) then sum(y_i-phi_i)<=0 with
     each term >=0, forcing equality. So (star_S) HOLDS  <=>  exists core y with
     y_i>=phi_i (i in S) and y(S)>phi(S).

(R2) [cone form] (star_S) FAILS  <=>  the normal cone of core(v) at phi contains a
     vector r supported on S with r_k>0 for all k in S (0 off S). [The ">=1" is just a
     scaling of a strictly-positive cone vector.] Equivalent to phi maximizing r.x.

(R3) [normal-cone generators] phi maximizes c.x over core(v)  iff
     c = mu*1_N - sum_{T tight} lambda_T 1_T with lambda_T>=0. Coordinatewise for the
     (star_S)-failure residual r (=0 off S, >0 on S):
       mu - sum_{T ni j} lambda_T = 0      (j not in S)
       mu - sum_{T ni k} lambda_T = r_k>0  (k in S).
     "off-S players covered by tight coalitions at exactly level mu; S-players
     UNDER-covered."

(R4) [leximin always sits on a stratum max-face] Round-1 LP dual of the Maschler
     scheme yields lambda_T>=0 (tight T), mu, and pi_i>=0 with sum_i pi_i = 1,
     pi_i = mu - sum_{T ni i} lambda_T, and pi supported on the lowest stratum B_1
     (compl. slackness: pi_i>0 => g_i=s_1). Hence phi ALWAYS maximizes the
     nonneg-weighted sum sum_{i in B_1} pi_i x_i over the core. So max-faces are
     intrinsic to leximin; the content of Lemma D is that for EXACT games no such
     face is strictly positive on a binding-bumpable S.

## KEY FINDING (this agent, decisive reframing)

"Binding-bumpable" MUST include exact-preservation: there is d>0 with v+d*1_S EXACT
(Lemma A). My first tooling omitted this and found "star failures" on exact games —
but EVERY such failure has max_exact_bump(g,S)=0: S cannot be bumped at all while
staying exact. So they are NOT binding-bumpable; Lemma D is intact.

Define d*(S) = max{d>=0 : v+d*1_S exact} = min_{T!=S} [ max{x(S): x in core, x(T)=v(T)} - v(S) ].
slack_S = phi(S)-v(S) >= 0. Binding-bumpable  <=>  d*(S) > slack_S (so the maximal
exact bump actually moves phi past its current S-total; implies d*>0).

REDUCED TARGET (proving this proves Lemma D, contrapositive):
  (LemD*) exact v, non-singleton proper S, star_S FAILS at phi  ==>  d*(S) <= slack_S.
Equivalently: star_S fails  ==>  EXISTS proper T!=S with
     max{ x(S) : x in core(v), x(T)=v(T) } <= phi(S).
Empirically the stronger d*(S)=0 holds in every failure seen (forcing some T tight
drives x(S) to its floor v(S)). Uniform-r subcase is immediate: star-fail with
uniform r => phi(S)=max_core x(S) => core(v') empty for d>slack => d*<=slack. Hard
case = non-uniform r.

## REDUCTION CHAIN (this agent) — Lemma D <== Conjecture C

Notation: m_k=v({k}); M_k := max{ x(S) : x in core(v), x_k = m_k }. Exactness of {k}
makes x_k=m_k core-attainable, so M_k >= v(S). Note M_k depends only on (v,S,k).

BRIDGE LEMMA (pure exactness, PROVEN): if S is binding-bumpable then M_k > v(S) for
every k in S.
  Proof. Binding-bumpable => exists d>0, v'=v+d*1_S exact, |S|>=2 so m_k unchanged.
  Exactness of {k} in v': min_{core(v')} x_k = m_k, so some w^k in core(v') has
  w^k_k = m_k. core(v') = core(v) cap {x(S)>=v(S)+d}, so w^k in core(v),
  w^k_k=m_k, w^k(S) >= v(S)+d > v(S). Hence M_k >= w^k(S) > v(S).  QED

CONJECTURE C (the crux, uses leximin; VERIFIED, PROOF IN PROGRESS): v exact, S
non-singleton proper, phi=leximin(v). If star_S FAILS at phi, then EXISTS k in S with
M_k = v(S) (forcing that one member to its floor forces all of S to its floor).

  Lemma D follows: binding-bumpable => M_k>v(S) all k (Bridge) => (contrapos. of C)
  star_S holds.  Equivalently the certificate coalition for d*(S)=0 is a SINGLETON
  {k}, k in S: bumping S breaks exactness of {k}.

EVIDENCE: star-fail => some k in S has M_k=v(S): 4/4 (seed7), plus all failing cases
have d*=0. Background hunts (n=5 s1,s2; n=6 s1): 100+ exact games, ~2800 binding-room
coalitions, star-fail always non-binding-bumpable, 0 Lemma-D counterexamples.

## CORRECTED CERTIFICATE (Conjecture C singleton form is FALSE; use a coalition)

Singleton M_k=v(S) fails (found exact game S={0,2,3,4}, no member's floor caps x(S);
certificate is the pair T*={2,4}). The correct canonical certificate:

Let star_S fail with cover (lambda_U>=0 on tight U at phi, sigma, r_j=sigma-sum_{U ni j}
lambda_U; r_j>=1 j in S, r_j=0 j not in S). Assume sigma>0 (true unless degenerate).
Define
    W  := union of the cover coalitions {U : lambda_U>0},
    T* := W ∩ S,   R := S \ W  (= the max-r members: r_k=sigma).
Then:
 (P1) every off-S player lies in W  (r_j=0 => sum_{U ni j}lambda_U=sigma>0 => j in some U),
      hence N\S ⊆ W, so  S ∪ W = N  and  S ∩ W = T*.
 (P2) MODULAR IDENTITY (needed): x(S)+x(W)=x(N)+x(T*) for ALL x (set identity
      1_S+1_W=1_N+1_{T*} since S∪W=N, S∩W=T*). Hence for x in core with x(T*)=v(T*):
        x(S) = v(N)+v(T*) - x(W) <= v(N)+v(T*) - v(W)   [core: x(W)>=v(W)].
 (P3) KEY CLAIM (verified, PROOF OPEN):  delta := v(S)+v(W)-v(N)-v(T*) >= 0
      (equivalently v(N)-v(N\R) <= v(S)-v(S\R): marginal of R to N <= marginal to S;
      empirically delta = 0 EXACTLY). Given (P3):
        M^{(T*)} := max{x(S): x in core, x(T*)=v(T*)} <= v(N)+v(T*)-v(W) <= v(S),
      and M^{(T*)} >= v(S) (exactness). So M^{(T*)} = v(S) => d*(S) = 0
      => S NOT binding-bumpable.  LEMMA D PROVED, modulo (P3).

VERIFIED: over all star-fail exact cases sampled (n=5, many seeds), (P1),(P2) hold and
delta = 0 (so M^{(T*)}=v(S)); 0 Lemma-D counterexamples. delta=0 => (P3).

## ============================================================================
## PROOF OF LEMMA D (complete modulo the verified 2-valued dichotomy, Step 2)
## ============================================================================

THEOREM (Lemma D). v exact, S proper non-singleton, phi=leximin(v). If S is
binding-bumpable (exists d>0 with v+d*1_S exact and phi(S)<v(S)+d) then (star_S)
holds at phi.

PROOF (contrapositive): assume (star_S) FAILS; show S is not binding-bumpable.

Step 1 (dual cover). (star_S) fails <=> (Farkas, verified) there are weights
lambda_T>=0 on coalitions T tight at phi (phi(T)=v(T)) and sigma in R with residual
   r_k := sigma - sum_{T ni k} lambda_T    satisfying  r_k>=1 (k in S), r_j=0 (j∉S).
(Equivalently phi maximizes r·x over core(v).) Off-S players have sum_{T ni j}
lambda_T = sigma; a tight coalition is needed so sigma>0.

Step 2 (TWO-VALUED DICHOTOMY — verified structural lemma, proof open).
The cover is 2-valued: r_k in {rho, sigma} for all k in S, rho:=min_S r_k>=1. Put
   T* := {k in S : r_k=rho}  (floor-r members),   R := {k in S : r_k=sigma}=S\T*.
[Verified: residual_cover is 2-valued in 100% of star-failures (n=5,6, many hundreds);
an ADVERSARIAL LP search maximizing random objectives over the whole cover polytope
produced 0 three-valued covers. Every exact game is v(T)=min over its core vertices
x(T), i.e. a min-of-points game, so the point-min sample ranges over all exact games.]

Step 3 (geometry). W := union of the cover coalitions {T : lambda_T>0}.
 (a) P:=N\S ⊆ W (off-S j has sum_{T ni j}lambda_T=sigma>0, so j is in some cover T).
 (b) W∩S = {k in S : sum_{T ni k}lambda_T>0} = {k in S : r_k<sigma} = T*  (2-valued).
 So S∪W=N, S∩W=T*, W=P⊍T* (disjoint). [If binding then R≠∅: else r≡rho uniform =>
 phi maximizes rho·x(S) => phi(S)=max_core x(S), contradicting phi(S)<max_core. So
 T*⊊S is a proper nonempty coalition, T*≠S.]

Step 4 (cover inequality). For any x in core(v):  0 <= sum_T lambda_T (x(T)-v(T)).
Since sum_{T ni j}lambda_T = sigma (j in P), = sigma-rho (k in T*), = 0 (k in R):
   sum_T lambda_T x(T) = sigma·x(P) + (sigma-rho)·x(T*),
and the same with phi (tight: v(T)=phi(T)). Subtracting:
   (★)   sigma·(x(P)-phi(P)) + (sigma-rho)·(x(T*)-phi(T*)) >= 0.

Step 5 (key bound). For x in core, x(W)=x(P)+x(T*). From (★),
   x(P)-phi(P) >= -((sigma-rho)/sigma)(x(T*)-phi(T*)), so
   x(W) >= phi(P) + (rho/sigma)x(T*) + ((sigma-rho)/sigma)phi(T*)
        >= phi(P) + (rho/sigma)v(T*) + ((sigma-rho)/sigma)v(T*) = phi(P)+v(T*),
using x(T*)>=v(T*), phi(T*)>=v(T*), and 0<rho<=sigma. Hence
   min_core x(W) >= phi(P) + v(T*).

Step 6 (certificate). Modular identity 1_S+1_W=1_N+1_{T*} (S∪W=N, S∩W=T*): every x
has x(S)+x(W)=x(N)+x(T*). For x in core with x(T*)=v(T*):
   x(S) = v(N)+v(T*)-x(W) <= v(N)+v(T*)-min_core x(W) <= v(N)+v(T*)-(phi(P)+v(T*))
        = v(N)-phi(P) = phi(N)-phi(P) = phi(S).
Therefore  M^{(T*)} := max{ x(S) : x in core, x(T*)=v(T*) } <= phi(S).

Step 7 (not binding-bumpable). Suppose v'=v+d*1_S exact with phi(S)<v(S)+d (binding).
Exactness of the proper coalition T*≠S in v' needs a core(v') point x with
x(T*)=v(T*); such x in core(v) has x(S)>=v(S)+d, so x(S)<=M^{(T*)}<=phi(S)<v(S)+d<=x(S),
contradiction. So no binding d preserves exactness: d*(S)<=phi(S)-v(S)=slack, i.e. S is
NOT binding-bumpable.  ∎ (modulo Step 2)

Also PROVEN unconditionally (no Step 2): the BRIDGE LEMMA (binding-bumpable => M_k>v(S)
for all k in S). Steps 3-7 are elementary and rigorous. Only Step 2 (2-valued cover)
is verified-not-proven.

## VERIFICATION (decisive, independent of the proof)
End-to-end chain verifier (src/_lemD_chain.py), exact rational, n=5 (seeds 1,2) & n=6:
every star-failure satisfies C1 (2-valued cover) & C2 (v(W)>=phi(P)+v(T*)) & C3
(M^{(T*)}<=phi(S)) & C4 (true d*(S)<=slack, i.e. Lemma D). 55+ star-fails, 0 failures,
0 counterexamples. Plus background hunts: thousands of exact games / binding-room
coalitions at n=5,6, every star-failure non-binding-bumpable, ZERO Lemma D
counterexamples.

## CORRECTION (later work): Step 2 (2-valued) is FALSE, but the proof GENERALIZES.
## Rare cases (n>=6) have a cover with r NON-constant on T*={k in S: r_k<sigma}
## (e.g. n6: S={0,1,2,3,5}, r=(3,1,1,2,1), so r on T*={1,2,3,5} takes values {1,2}).
## HOWEVER the certificate inequality v(W) >= phi(P)+v(T*) still HOLDS there (verified,
## e.g. 35 >= 55/2). So 2-valued was only an easy route, not essential. The real,
## unconditional target is:
##   (KEY)  v(W) >= phi(P) + v(T*)     [W=union cover, P=N\S, T*=W∩S].
## Since min_core x(W)=v(W) (exactness), (KEY) => M^{(T*)} <= phi(S) => Lemma D
## (Steps 6,7 unchanged). (KEY) is proved for r CONSTANT on T* by the elementary
## convexity (Steps 4,5). For general r, TOTAL BALANCEDNESS of exact games gives, via
## the balanced collection {cover coalitions}∪{nested r-level sets D_l⊆T*}:
##   v(W) >= phi(P)+v(T*)   <==   (GOAL3)  sum_l (rho_l - rho_{l+1}) slack(D_l) <= sigma*slack(T*)
## where rho_1>...>rho_q are the r-values on T* (all <sigma), D_l={k in T*: r_k>=rho_l},
## D_q=T*, slack(A)=phi(A)-v(A). GOAL3 is a concrete slack inequality; for CONSTANT r
## (q=1) it is trivial ((sigma-rho)*slack(T*)>=0). GOAL3 is the new clean open lemma
## (being verified incl. non-constant n6 cases). It is SUFFICIENT (total balancedness
## is a theorem for exact games). Status: (KEY) verified universal; GOAL3 the reduction.
##
## CLEANEST SUFFICIENT FORM (total balancedness w/ OPTIMAL T*-subgame top-up):
##   (NEED'')  (sigma - r)·phi|_{T*}  >=  max_{z in core(T*-subgame)} (sigma - r)·z,
##   (sigma-r_k)>=0 on T*.  NEED'' => (KEY) => Lemma D. Constant r: trivial (RHS is the
##   constant (sigma-rho)v(T*) < (sigma-rho)phi(T*)=LHS). Non-constant: OPEN (rare n>=6).
##
## HONEST BOTTOM LINE: Lemma D VERIFIED (0 counterexamples, thousands of cases n<=6).
## Proof COMPLETE for r-constant-on-T* covers (all n=5, most n=6). For rare non-constant
## covers (n>=6): reduces to (KEY) v(W)>=phi(P)+v(T*) [verified universal incl. the one
## fully-analyzed non-constant case, 35>=55/2], whose sufficient conditions GOAL3/NEED''
## are proven for the constant case, OPEN for non-constant. Proof NOT fully closed.
## Earlier "Step 2 (2-valued cover) verified universal" was WRONG (3-valued covers exist
## at n>=6); retracted.
##
## CLEANEST REFORMULATION OF (KEY) (slack form). W=T*⊍P. A core point y with
## y(W)=v(W) AND y(T*)=v(T*) exists (simultaneous flooring, verified: min{y(T*):
## y core, y(W)=v(W)}=v(T*) always). For it y(P)=v(W)-v(T*) and
##   y(P)-phi(P) = [v(W)-v(T*)] - [phi(W)-phi(T*)] = slack(T*) - slack(W).
## Hence, with slack(A):=phi(A)-v(A):
##   (KEY)  <==>  slack(W) <= slack(T*)   (adjoining the off-S set P to T* does not
##                                         raise the leximin slack).
## VERIFIED universal (identically equivalent to (KEY)). General slack-monotonicity is
## FALSE for arbitrary nested coalitions, so a proof must use that P is exactly the
## sigma-fully-covered off-S set. The leximin direction d=phi-y raises T* by slack(T*),
## lowers R by slack(W), moves P by slack(W)-slack(T*); need leximin to force d(P)<=0.
## OPEN. [NB: the R-complement form "min{y(R):y core,y(W)=v(W)}<=phi(R)" is NOT
## equivalent -- y(R)=v(N)-v(W) is constant on that face, so it only tests W-tightness.]
##
## BANKED CONDITIONAL THEOREM: on exact games, phi is coalitionally monotone for a
## binding-bumpable S PROVIDED (KEY)=[slack(W)<=slack(T*)] holds. (KEY) proven
## unconditionally when the cover residual r is constant on T* (all n=5, most n=6);
## verified universal in general; unconditional proof OPEN for non-constant-r covers.
##
## OLD notes on the (false) 2-valued route, kept for context:
## - rho = min_S r_k = 1 ALWAYS (provable): C_S := N(phi) cap {supp r subset S, r>=0}
##   is a cone; a minimal cover (vertex of C_S cap {r_k>=1}) has some r_k at its
##   floor 1, else scale the whole ray down. [Verified: min r = 1 in 100% of cases.]
##   So (★) is sigma(x(P)-phi(P)) + (sigma-1)(x(T*)-phi(T*)) >= 0.
## - The genuinely open part: the members NOT at r=1 are all at r=sigma (i.e. in NO
##   cover coalition) -- no intermediate 1<r_k<sigma. Equivalent to: r_k in {0,1} up to
##   the global scale, i.e. C_S cap {r>=1} has only "0/1-plus-uniform" vertices.
##   Verified structural (adversarial LP over the full cover polytope: 0 three-valued
##   covers, n=5,6). An uncrossing/laminar argument on the tight-coalition hypergraph
##   at the leximin point is the likely route.
## - If Step 2 fails for some exact game, the general case would need
##   GOAL3: sigma*(phi(T*)-v(T*)) >= sum_l (rho_l-rho_{l+1})(phi(D_l)-v(D_l)) over the
##   nested r-level sets D_l subset T*; this needs slack(D_l)<=slack(T*), which is
##   FALSE for arbitrary nested coalitions (so 2-valued is genuinely the crux).

# ============================================================================
# LEMMA E'  (pivot per team-lead) — star_S along the exact path => phi_i nondecreasing on S
# ============================================================================
# Setup (Lemma A): v exact, S proper non-singleton, v'=v+d*1_S exact. For tau in
# [v(S), v(S)+d], v_tau agrees with v except v_tau(S)=tau; core(v_tau)=core(v)∩{x(S)>=tau};
# every v_tau exact. phi(tau):=phi(v_tau) is piecewise-affine in tau, tight set constant
# between breakpoints. HYP: (star_S) holds at phi(tau) for all tau. GOAL: for i in S,
# tau |-> phi_i(tau) is nondecreasing (and phi_j nonincreasing for j not in S).
# Target: sign of dphi_i/dtau >=0 (i in S) on each affine segment, via cover/convexity.

## E' — findings (this agent)
# SEGMENT STRUCTURE of the path phi(tau), tau in [v(S), v(S)+d*]:
#  - NON-BINDING prefix tau <= phi(v)(S): phi(tau)=phi(v) CONSTANT (Lemma B; the
#    x(S)>=tau constraint is slack, leximin point unchanged). d phi/d tau = 0.
#  - BINDING part tau > phi(v)(S) (i.e. phi(tau)(S)=tau): phi moves. On each affine
#    sub-segment (tight set constant), d phi(S)/d tau = +1, d phi(N\S)/d tau = -1, and
#    the two-sided pattern d phi_i/d tau >= 0 (i in S), <= 0 (i notin S).
# WORKED n=4 EXAMPLE: v=[0,0,3,4,2,3,5,6,3,6,17,17,5,8,20,23], S={0,1,3}, v(S)=17,
#  d*=3, slack=2. phi=(2,17/2,4,17/2) for tau in [17,19]; on [19,20], d phi=(+,0,-,0):
#  player 0 (lowest-gain in S) rises 2->3, player 2 (off-S) falls 4->3, players 1,3 hold.
#  => extra S-mass comes ENTIRELY from N\S, delivered to the lowest-gain S-member; no
#  within-S transfer, no S-member drops.
# MECHANISM: the tightening x(S)>=tau+dtau forces mass INTO S; leximin takes it from
#  the highest-gain N\S players and gives to the lowest-gain S players. star_S guarantees
#  a FEASIBLE relief direction e (e(S)=1, e_i>=0 on S, e(T)>=0 tight) exists -- i.e. the
#  needed S-increase can be sourced from outside S without lowering any S-member.
# CRUX (same flavour as D, NOT yet closed): the leximin-STEEPEST feasible x(S)-ascent
#  direction e* (= d phi/d tau) has e*_i >= 0 on S. star_S gives a feasible e with that
#  property, but leximin-optimality could a priori prefer a within-S Robin-Hood (lower a
#  high-gain S-member to raise a low-gain one) -- must show it does NOT / is blocked.
# REDUCTION OBSERVATION: between two binding taus < tau' on a segment, star_S at phi(tau)
#  yields w = phi(tau)+s*e in core(v_{tau'}) with w_i >= phi(tau)_i on S and w(S)=tau';
#  then phi(tau') = leximin(core(v_{tau'})) must be shown >= phi(tau) on S. This is the
#  SAME "leximin preserves per-member S-lower-bounds under core-shrink" statement as D's
#  (star). So E' shares D's crux; closing D's slack(W)<=slack(T*) route likely transfers.

# ============================================================================
# REDUCTION THEOREM  (consolidating the whole conjecture onto (KEY))
# ============================================================================
# Aim (team-lead): present leximin coalitional monotonicity on exact games as
# CONDITIONAL ON THE SINGLE INEQUALITY (KEY), so any future proof of (KEY) settles
# everything. Below: what is rigorous (R), and the one remaining infinitesimal gap.

## Notation recap. v exact, S proper, d>0, v'=v+d*1_S exact. Path v_tau (tau in
## [v(S),v(S)+d]) all exact (Lemma A, PROVEN). phi(tau):=phi(v_tau). At a config where
## (star_S) fails, the cover gives W=union cover, P=N\S, T*=W∩S; (KEY) is the
## equivalent slack(W)<=slack(T*).

## PROP 1 (two-sided transfer; PROVEN, R). phi(tau) is piecewise-affine in tau.
##  - tau <= phi(v)(S): x(S)>=tau slack, phi(tau)=phi(v) (Lemma B). d phi/d tau = 0.
##  - tau > phi(v)(S): x(S)>=tau binds, phi(tau)(S)=tau. On each affine segment,
##    d phi(S)/d tau = +1 (differentiate phi(tau)(S)=tau) and, by efficiency
##    phi(tau)(N)=v(N), d phi(N\S)/d tau = -1. So the S-total rises at unit rate and
##    the complement falls at unit rate: mass is transferred from N\S into S.
##  [This is exactly the "S sourced from N\S" pattern seen independently in the
##   family-level and ES lanes.]

## The theorem <=> per-segment SIGN refinement: d phi_i/d tau >= 0 for every i in S
## (equiv. <= 0 for i not in S) on every binding segment. Integrating over the path
## gives phi_i(v') >= phi_i(v) on S. Call this (SIGN).

## PROP 2 (star supplies the relief direction; PROVEN, R). If (star_S) holds at
## phi(tau), there is a feasible ascent e with e(N)=0, e(S)=1, e_i>=0 (i in S),
## e(T)>=0 (tight T): the forced unit S-increase CAN be sourced from N\S without
## lowering any S-member. (Def. of star_S, normalized.)

## THE GAP (infinitesimal crux). The realized derivative e*=d phi/d tau is the
## LEXIMIN-steepest feasible S-ascent, not an arbitrary feasible one. (SIGN) says
## e*_i>=0 on S. star gives a feasible e with that property (Prop 2) but does not by
## itself force the leximin-optimal e* to avoid a within-S Robin-Hood (lower a
## high-gain S-member to raise a low-gain one). Excluding that is the infinitesimal
## analogue of (KEY): at phi(tau) it is the statement that phi(tau) does not sit on a
## positive-S-weighted max face in the "descent" sense -- the SAME cover object as D.

## ENDPOINT<->INFINITESIMAL IDENTIFICATION (structural, the consolidation). For
## tau<tau' on one binding segment, star at phi(tau) yields (Prop 2 integrated)
## w=phi(tau)+ (tau'-tau) e in core(v_{tau'}) with w_i>=phi(tau)_i on S, w(S)=tau'.
## Both D (finite: v -> v') and E' (infinitesimal) are then the ONE statement:
##   (MASTER) the leximin point of core(v) shrunk by tightening x(S) preserves every
##            S-member's lower bound, i.e. moves up (weakly) on S.
## D is MASTER at the path endpoints; E' is MASTER across each segment. (KEY) is the
## certificate that drives MASTER in the cases checked. So:
##   THEOREM (coalitional monotonicity on exact games)  <==  (KEY) at every star-fail
##   configuration along exact bump paths.
## Status: PROVEN modulo (KEY)-for-non-constant-covers. The reduction packages the
## entire conjecture on the single inequality slack(W)<=slack(T*). [Honest gap: the
## infinitesimal (SIGN) is the analogue, not yet a line-by-line corollary, of the
## finite (KEY); the shared cover object makes them the same in every checked case but
## a fully rigorous (KEY)=>(SIGN) corollary is still to be written.]

## (KEY) attack log — angles tried and their verdicts (for whoever resumes):
##  1. 2-valued convexity (single cover inequality) -- WORKS for r-constant-on-T*
##     (all n=5, most n=6). Does NOT extend: non-constant covers exist (n>=6).
##  2. Total balancedness + balanced collection {cover U's}∪{nested r-level sets D_l}
##     -- reduces (KEY) to GOAL3: sum_l (rho_l-rho_{l+1}) slack(D_l) <= sigma slack(T*).
##     Sufficient; trivial for constant r; for non-constant reduces to slack(D_l)<=
##     slack(T*) along the r-level chain, i.e. slack-monotonicity of r-level sets.
##     General slack-monotonicity is FALSE (tested), r-level version UNTESTED (cases
##     too rare to batch at n6).
##  3. NEED'': (sigma-r)·phi|_{T*} >= max_{z in core(T*)} (sigma-r)·z. Equivalent
##     sufficient form; the T*-subgame dual reduces to the SAME lossy balanced-collection
##     bound (singleton cover loses v(T*)->sum m_k). Circular with GOAL3.
##  4. Leximin-direction d=phi-y, want d(P)<=0 -- INSUFFICIENT: contrapositive
##     (slack(W)>slack(T*)) is fully consistent with phi leximin-optimal (the flooring
##     point y has P,T* lower and R higher, so phi being leximin-better is expected).
##     => (KEY) does NOT follow from leximin optimality alone; needs exactness.
##  5. Subgame-on-W angle -- DEAD: the W-subgame is NEVER exact (verified 0/22;
##     exactness does not restrict to subgames), and phi|_{T*} is NOT the leximin of the
##     T*-subgame with inflated grand value phi(T*) (verified: ~40% mismatch). Total
##     balancedness DOES restrict (exact => totally balanced) and is what angles 2-3 use;
##     but it yields only the lossy bound.
## NET: (KEY) proven for constant-r covers; for non-constant covers all concrete angles
## reduce to the SAME balanced-collection value bound (GOAL3/NEED'') that resists. It is
## verified universal. Likely needs the leximin structure of phi on the FULL game (the
## g_k gains on T* are not arbitrary) coupled into GOAL3 -- not yet found.
