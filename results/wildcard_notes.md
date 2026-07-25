# Wildcard sweep — thin-core exact generator vs universal claims

Agent: wildcard. Working dir ~/projects/counterexample-hunt/coopgames/.
Method: min-of-points generator v(S)=min_{p in P} p(S) => provably EXACT, thin core,
often non-large — hits the frontier random sampling misses.

## TARGET TRIAGE (lit-check first)

### (a) Davis-Maschler bargaining set = core on EXACT games  [PRIMARY]
ADM (Davis-Maschler) bargaining set IM_1^(i), individually-rational version.
Objection of i vs j at x: (S,y), i in S, j notin S, y(S)=v(S), y_i>x_i, y_k>=x_k (k in S).
Counterobjection (T,z): j in T, i notin T, z(T)=v(T), z_k>=y_k (k in S∩T), z_k>=x_k (k in T\S).
x in BS iff every objection has a counterobjection. Core ⊆ BS always.

LIT STATE (WebSearch 2026-07-24):
- BS = core for CONVEX games (Maschler-Peleg-Shapley 1972).
- BS = core for ASSIGNMENT games (Solymosi 1999) — NON-convex, so BS=core does NOT
  characterize convexity per-game. Good: exact is a genuinely separate axis.
- BS = core for PERMUTATION games (Solymosi-Raghavan-Tijs 2003).
- BS = core for ALL games with < 5 players when core nonempty. => counterexample needs n>=5.
- BS ⊋ core KNOWN to occur for 5-person TOTALLY BALANCED games (Solymosi, "On the
  bargaining set, kernel and core of superadditive games", IJGT 1999).
- Izquierdo-Rafels: convex is the ONLY zero-monotonic class where Mas-Colell (MB*) /
  steady (SB) bargaining set = core — but that's the LARGER MB*/SB variants, NOT classic DM.

GAP: exact ⊊ totally balanced. Known n=5 BS⊋core example is totally-balanced; is it EXACT?
If not exact, "exactness => BS=core" is unaddressed. Target: thin-core exact game (n>=5),
non-large, with a bargaining-set point strictly outside the core. Certify via LPs.

## IMPLEMENTATION (src/bargaining_set.py) — exact DM-BS membership oracle, VALIDATED
in_bargaining_set(game,x): for every ordered (i,j) and every S (i in S, j notin S,
v(S)>x(S)), solve LP  min delta s.t. v(T)-y(S∩T)-x(T\S)<=delta (all T: j in T,i notin T),
y_k>=x_k, sum y_k=v(S).  delta*<0 => justified objection => x NOT in BS. Exact (Fraction).
Plus float_has_justified_objection (scipy screen, 4.4x speedup, exact confirms survivors).
VALIDATION (all pass):
- Reproduces the 2025 Atay-Nunez-Solymosi Example 2 EXACTLY: kernel pt (1,1;1/3,1/3,1/3)
  outside unique core pt (0,0;1,1,1) is IN BS; dominated pts correctly rejected.
- BS boundary on that game: the SYMMETRIC segment (firms=a,workers=b) is in BS,
  asymmetric pts get specific justified objections. Matches paper structure.
- Convex games (n=4,5): outside-core points correctly rejected (BS=core, MPS 1972).
- Empty-core 3-majority: nucleolus in BS.

## KEY FACT: the 2025 minimal counterexample is NOT exact
Ex.2 game v(S)=min(#workers,2*#firms): balanced+superadd+totally-balanced, NOT exact
(worker singletons v=0 but core-min=1). Exactifying it makes it CONVEX (workers forced
to 1, unique imputation=core). So the phenomenon there is powered by NON-exactness:
underpaid singletons. Exactness raises v(i)=min_core x_i, shrinking room for BS-extension.

## FINDINGS (STRONG NO-GO for target (a) so far): exact games => BS = core
Searched thin-core exact games via min-of-points generator (exact by construction),
kernel/transfer points + prekernel + facet-crossing + symmetric segments, exact-certified.
- 240 random non-convex exact games (n=5): kernel ⊆ core (0 converged kernel pts outside
  core, 8000-iter transfer from n+8 starts). => target (b) kernel⊄core also NO-GO.
- 53 non-convex symmetric exact games (type 2,3): symmetric-segment outside-core pts: 0 in BS.
- 4 campaign non-large exact games (COUNTEREX_es_n5_*): ALL confirmed NON-large,
  ALL BS = core under thorough probe. (These are the true frontier: exact + non-large.)
- Symmetric orbit-closed generator yields LARGE cores (40/40) -> not the frontier; the
  plain few-point generator gives non-large. Both give BS=core.
Running: n=5 (600) + n=6 (250) batches with full probe. See wildcard_batch_n{5,6}.txt.

## LIT STATUS of "exact => BS=core": appears UNADDRESSED (genuinely open)
No stated theorem exact=>BS=core. BS=core proven only for structural classes: convex
(MPS72), assignment (Solymosi99), permutation (SRT03), veto (Solymosi99/Bahel16),
tree-restricted/simple-network (Solymosi08), quasi-hyperadditive (Bahel21), supplier-
firm-buyer (Atay-Solymosi18). Characterized (superadd) via balancedness of the maximal
excess game at BS imputations (Solymosi99; Holzman01 necessity for Mas-Colell). The
failure is documented only on NON-exact classes (2025 many-to-one = "first network-
optimization game to fail it"). => exact case is a clean unaddressed sharpening.
OUTCOME so far: strong evidence exact => BS=core (conjecture-shaped no-go), NOT a kill.

## LIT CONFIRMATION (2026-07-24, final pass)
- NO stated theorem "exact => BS=core" or "large-core => BS=core" for general TU games.
- On ASSIGNMENT games specifically, largeness = extendability = exactness are EQUIVALENT
  and imply core stability (so there the distinction collapses) — but for general games
  these are DIFFERENT classes, and the BS=core question is governed by Solymosi's
  maximal-excess-game balancedness characterization, not by exactness/largeness.
- => "does exactness imply BS=core?" is genuinely unaddressed in the general TU setting.

## KILL ATTEMPT: abundant-worker many-to-one markets (make the 2025 mechanism exact)
Idea: 2025 non-exactness came from SCARCE workers (core forces them paid => singleton
core-min > 0). Make workers ABUNDANT (W > total firm capacity) so unmatched workers have
core-min 0 => game may be exact while still many-to-one (the class that breaks BS=core).
Testing caps (2,1)/W4, (2,2)/W5, (1,2)/W4 for (exact AND non-convex AND BS!=core). [running]
Caveat (Solymosi Prop 4, 2025): BS!=core needs the degeneracy "no essential coalition in
all optimal matchings," which arises from TIED valuations => tension with exactness.
RESULT: abundant-worker many-to-one games (caps(2,1),W=4,n=6; incl. tied-valuation
degenerate ones) are NEVER exact (0/20 exact). Route CLOSED. Market/assignment games are
totally-balanced but not exact; the BS!=core phenomenon lives in non-exact totbal territory.

## ===== TERMINAL STATE (2026-07-24): NO KILL — strong conjecture-shaped no-go =====
Target (a) "exact => Davis-Maschler bargaining set = core": NO certified counterexample.
Target (b) "exact => kernel subset core": also no-go (kernel ⊆ core held everywhere tested).
Evidence for exact => BS=core:
 - validated exact BS oracle (reproduces published 2025 A-N-S Ex.2 exactly; correct on
   convex[BS=core] and empty-core[nucleolus in BS]);
 - 2025 minimal BS!=core example is NON-exact; exactifying it makes it CONVEX;
 - ~300 exact games probed (240 random kernel⊆core; 53 symmetric BS=core on sym segment;
   4 confirmed NON-large exact games BS=core under thorough kernel+prekernel+facet probe);
 - abundant-worker exact-market route closed (0/20 exact);
 - structural reason: exactness sets v(i)=min_core x_i, removing the underpaid-singleton
   mechanism the BS-extension needs; every exact route collapses to convex or fails exactness;
 - lit: no stated exact=>BS=core (or large=>BS=core) theorem for general TU games; the
   coincidence is governed by Solymosi's maximal-excess-game balancedness, and the failure
   is documented only on non-exact classes => the exact question is genuinely unaddressed.
Verdict: this is a "belief anchored by special cases" that appears TRUE (a positive
conjecture), not a false universal — so NOT a wildcard kill. Deliverables: src/bargaining_set.py,
src/bs_probe.py, src/hunt_bargaining_exact.py, src/hunt_bs_symmetric.py.
NOTE: an 8-process stES_reliable_enum.py lane was saturating all CPU cores; my python
cleanups killed it repeatedly (unintended) — flagged to team-lead to relaunch if needed.

## ===== ANALYTIC PIVOT (proof attempt on the positive pair) — attempted, not closed =====
Goal: prove kernel ⊆ core and/or BS = core on exact games (positive theorem).
LIT: NOT known — "exact characterization of when kernel ⊆ core remains an active research
area"; no stated exact=>kernel⊆core or exact=>BS=core theorem. So genuinely open.
(1) kernel ⊆ core:
 - REDUCTION EXPLORED then RULED OUT: "max-excess collection D balanced => contradiction"
   is VACUOUS. For any x∉core (core≠∅) and any core pt z*, w=z*-x has w(N)=0 and
   w(S)=z*(S)-x(S) >= e(S,x) > 0 on EVERY blocked coalition; so all blocked coalitions
   (incl. D) are ALWAYS jointly non-balanced. The excess LEVEL SETS are the wrong object.
 - The correct criterion (Solymosi 1999 / Holzman 2001) is balancedness of the derived
   MAXIMAL EXCESS GAME, not excess level sets. Could not retrieve its precise definition
   (Solymosi 1999 IJGT + almost-convex paper paywalled/served-as-HTML; sapub host down).
   Reconstruction attempt (superadditive cover m_x(S)=max_partition sum e(B,x)) FAILS the
   oracle test (m_x trivially always balanced => not the right object). Proof BLOCKED on
   this machinery.
 - ADVERSARIAL EMPIRICAL CHECK (new): kernel search SEEDED FROM OUTSIDE THE CORE
   (per-coalition excess-maximizing imputations, 12k-iter transfer) on all 4 non-large
   exact games: 0 outside-core kernel points. Reinforces kernel⊆core (no missed
   disconnected component).
(2) BS = core: same blocker (needs the maximal excess game); direct objection-LP route
   shows exactness only forbids the underpaid-SINGLETON mechanism, not a justified
   objection in general (x∈BS w.r.t. S0/i needs, for every j∉S0, a tight/blocked T∋j,∌i
   — exactness does not obviously prevent this). Not closed.
VERDICT of pivot: positive conjecture (exact => kernel⊆core AND BS=core) stands with
STRONG empirical support + confirmed-open status, but NO clean proof (blocked on the
maximal-excess-game definition). Bankable partial: the clean statement + the ruled-out
naive reduction + the reduction target. TERMINAL — analytic attack exhausted for this pivot.

## WHERE CONVEXITY ENTERS MPS (answers the pivot's core question) — CERTIFIED
MPS 1971 kernel⊆core (convex) relies on: the excess game e(S,x)=v(S)-x(S) is SUPERMODULAR
(v supermodular + x modular) <=> v convex. Supermodularity makes the max-surplus coalitions
argmax_{i in S, j notin S} e(S,x) a LATTICE (closed under ∪,∩) — this lattice is the lever
that drives MPS's transfer/uniqueness into the core.
EXACTNESS DOES NOT SUFFICE:
 - exact non-convex games have NON-supermodular excess games (verified on COUNTEREX_es).
 - the max-surplus LATTICE PROPERTY itself FAILS on exact non-convex games (CERTIFIED, 3/7
   sampled): e.g. v=[0,2,0,5,0,5,1,8,1,4,1,7,1,7,2,10,0,4,0,6,0,7,1,10,1,6,1,7,1,9,2,12],
   x=(48/11,18/11,0,18/11,48/11): coalitions S=19,S=25 both attain s_{4,2} but e(19∪25)<max.
=> The MPS argument DOES NOT TRANSFER to exact games. Both natural routes now closed:
   (i) excess LEVEL-SET balancedness — vacuous (blocked coalitions always jointly non-bal);
   (ii) MPS supermodular-lattice — lever absent (lattice fails on exact games, certified).
   Any proof of kernel⊆core (or BS=core) for exact games needs a genuinely new technique
   (Solymosi's maximal-excess-game balancedness, def. inaccessible). Analytic attack
   EXHAUSTED; conjecture remains open + strongly evidenced.

## ===== UNBLOCKED: maximal excess game def retrieved (team-lead) — NEW RESULTS =====
DEF (Atay-Solymosi EL 2018 p.101): ê_x(S)=max_{T⊆S} e_x(T), e_x(T)=v(T)-x(T). Monotonic
cover (over SUBSETS). Implemented src/... validated: on 2025 example, x∈classicalBS(outside
core) <=> ê_x NOT balanced, matching Solymosi99/Holzman01 on all 5 test pts.
THEOREMS: Solymosi99 (superadd): ê_x balanced => DM justified objection => x∉classical BS.
Holzman01: x∈I*\C => [x∉Mas-Colell BS M*_MC  <=>  ê_x has nonempty core]. (iff)

PROOF TARGET (T) "exact => ê_x balanced for all x∉core" is **FALSE** — CERTIFIED refutation:
  exact game COUNTEREX_es_n5_s1_t23 (v(N)=19), imputation x=(17/3,7,5,2/3,2/3):
  efficient, IR (singleton floors (2,6,4,0,0)), OUTSIDE core (S={1,2,3}: v=13>x=38/3 etc.),
  ê_x has EMPTY core (ê_x(N)=1/3 but min cover sum=1/2). Independently re-verified.
  => classical BS=core CANNOT be proved via ê_x-balancedness. Route (T) dead.

CONSEQUENCE (certified, by Holzman iff): **Mas-Colell bargaining set ⊋ core on EXACT games.**
  Same x is in M*_MC \ core (ê_x non-balanced). My classical DM oracle: x NOT in classical BS.
  => on exact games classical DM BS (=core, my conj.) and Mas-Colell BS (⊋core) SEPARATE.
  Found on 2 of 4 non-large exact ES games (s1,s3); other 2 (s0,s2): no such pt found.
  NOVELTY CHECK PENDING: Izquierdo-Rafels 2012a "convex is the ONLY zero-monotonic class
  with MB*(Shimomura)=core" — if MB*(Shimomura)=Holzman's M*_MC, this is KNOWN (rediscovery),
  else possibly open. Also: classical BS ⊆? Mas-Colell BS (inclusion direction unconfirmed).
STILL OPEN + NOVEL: classical DM BS = core on exact games (holds empirically incl. at the
  ê_x-nonbalanced points, via full DM objections beyond Solymosi's sufficient condition).
NEXT: Maschler 1976 (JET 13:184) 5-person totbal game w/ classical BS⊋core — GATE its
  exactness (exact => classical conjecture DEAD).

## CRITICAL LOGIC CORRECTION (re team-lead's (T)-route)
Holzman iff: ê_x balanced  <=>  x NOT in Mas-Colell BS. So (T)="exact => ê_x balanced for
all x∉core" is EXACTLY "Mas-Colell BS = core on exact games". I REFUTED (T) => Mas-Colell
BS ⊋ core on exact games (certified). Therefore the (T) route CANNOT prove the CLASSICAL
BS=core conjecture — (T) is about the Mas-Colell BS, which is strictly BIGGER (Holzman:
classical BS ⊆ Mas-Colell BS for superadd TU). Solymosi gives only ê_x balanced => classical
justified objection (SUFFICIENT, one direction); at ê_x-NONbalanced points classical BS can
still exclude x (my oracle DOES find a classical justified objection at the (T)-failure pts).
So: classical BS=core is a STRICTLY WEAKER statement than (T)/Mas-Colell=core, needs its own
criterion (not ê_x-balancedness). Maschler 1976 is a market game (~never exact) => gate likely
confirms. Since classical BS ⊆ Mas-Colell BS, any classical-BS\core witness must be among the
ê_x-nonbalanced (Mas-Colell\core) pts — hunting THAT region directly now.

## MASCHLER 1976 GATE — CLOSED (confirms conjecture)
Maschler 1976 (JET 13:184, classical BS⊋core, n=5) is a MARKET/GLOVE game. Glove markets
v(S)=min(#left,#right) tested: L,R = (2,3),(3,2),(2,4) all NON-exact (scarce side singleton
v=0 but core-min=1 — same non-exactness as the 2025 example). So Maschler's game is non-exact
=> does NOT refute "exact => classical BS=core". Gate confirms. (Market games ~never exact:
matches abundant-worker census 0/20 and glove result.)

## k*-ROUTE (Izquierdo-Rafels 2012, Econ Bull 32(3)) — DEAD for exact games
THM: classical BS M_1^i = core if v(N) >= k*(v̂), k*=min_{a_i<=v(i)} max_{proper S}[n(v(S)-a(S))+a(N)].
One LP: min eps s.t. eps+(n-1)a(S)-a(N\\S) >= n v(S) all proper S, a_i<=v(i). Implemented,
VALIDATED (additive game: k*=v(N)=12 exactly). Sufficient-only, NOT tight (glove: coincidence
holds but v(N)<k*).
RESULT: on EXACT games v(N) >= k* essentially NEVER holds: 0/319 exact-nonconvex n=5 games;
all 4 ES games (v(N),k*)=(10,24),(19,32),(18,25),(23,113/3) have v(N)<k*. => k*-route CANNOT
prove classical BS=core on exact games (kills the ROUTE, not the conjecture, since k* not tight).

## PROOF-LANDSCAPE SUMMARY for classical BS=core on exact games (all known routes fail)
 - MPS supermodular-lattice: lever absent (excess game not supermodular; lattice fails, certified).
 - excess LEVEL-SET balancedness: vacuous.
 - ê_x balancedness / (T): FALSE on exact games (it's the Mas-Colell criterion, strictly bigger set).
 - k* sufficient condition: v(N)>=k* holds for 0/319 exact games.
=> The classical BS=core conjecture on exact games (strong empirical support; classical witnesses
   would have to hide among Mas-Colell\\core = ê_x-nonbalanced points, and there classical
   membership tests FALSE) has NO working proof route among the standard tools. Genuinely open;
   any proof needs a new idea specific to the DM (hard-objection) bargaining set on exact games.
 - CLASS-CLOSEDNESS route (5th, also dead): Solymosi/Granot-Granot proved assignment-game
   coincidence by showing that class is CLOSED under x -> maximal-excess-game ê_x. Exact games
   are NOT closed under ê_x: my (T)-refutation gives an exact v and imputation x with ê_x having
   EMPTY core => ê_x not balanced => ê_x not exact. So the class-closedness technique cannot
   transfer to exact games either. No-go map COMPLETE (5 routes).

## FINAL STATUS: stand-down accepted by team-lead. Wildcard lane closed.
Deliverables: src/bargaining_set.py (classical DM BS oracle + float screen, validated on
2025 A-N-S example), ê_x + k* oracles (in-session, formulas in notes), src/bs_probe.py,
src/hunt_bargaining_exact.py, src/hunt_bs_symmetric.py. Certified: Mas-Colell BS ⊋ core on
exact games (known IR pattern). Conjecture-shaped positives (open, strong evidence): classical
DM BS = core AND kernel ⊆ core on exact games. Complete 5-route no-go map for the classical
proof. Maschler-1976 + 2025 gates survived (both non-exact). No wildcard KILL of a false
universal; the surfaced universals appear TRUE.

### (d) Every exact game has a vNM stable set?  [SECONDARY — hard to certify]
Lucas (1968) 10-person game has no stable set. Need: is it exact? Refuting
"every exact game has a stable set" requires PROVING nonexistence — hard to certify.
Only viable if a known non-existence game happens to be exact. Parked.

### (b)(c)(e) kernel⊆core / Mas-Colell BS / nucleolus monotonicity on exact
Parked pending (a).
