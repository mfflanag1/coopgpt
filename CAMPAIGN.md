# Cooperative game theory counterexample campaign

Started 2026-07-23. Method: exact-verifier-first discipline (DGG/Woodall playbook).
Target profile: ∀-claims over TU-game classes, witness = characteristic function on
5–8 players, verification = exact rational LP + Kohlberg certificate.

## Verifier stack (all exact, `src/`)
- `exactlp.py` — own two-phase simplex over `Fraction`, Bland's rule.
  **Why own:** sympy 1.14.0 `lpmin`/`linprog` returned an INFEASIBLE point as
  "optimum" on `min x+y+z s.t. pairwise sums ≥ 1` (returns 1 at (0,1,0); truth 3/2).
  Cross-validated 400/400 vs scipy HiGHS with exact feasibility asserts.
- `tugame.py` — game props (convexity via local supermodularity, superadditivity,
  balancedness LP, core), Kohlberg criterion certifier (balanced-collection LPs).
- `nucleolus.py` — float Maschler successive LPs (screening) → rational
  reconstruction → **exact Kohlberg certification** (verifier independent of search path).
- Validation: Talmud bankruptcy (E=100/200/300) exact match; gloves; unanimity;
  Kohlberg rejects wrong vectors; n=3 aggregate-monotonicity hunt finds nothing
  (matches theorem) — calibration clean.

## Certified results so far (all exact rational, Kohlberg-certified both games)
1. **Coalitional monotonicity, n=5, balanced+superadditive**: bump one v(S), player
   in S drops 4/5. (Rediscovery — Young/Megiddo class.)
2. **Aggregate monotonicity, n=4 general**: certified violation. (Rediscovery.)
3. **Aggregate monotonicity, n=4 CONVEX**: certified violation — raising v(N) by
   d>0 on a convex 4-player game strictly lowers a nucleolus payoff.
   (Hokari-2000-class; if literature's smallest is n≥5, this is a size record.)
4. **Population monotonicity, n=5 CONVEX**: certified violation (gap 7/12).
   (Hokari-class rediscovery.)

Lattice note: convex ⟹ exact, convex ⟹ large core (Sharkey). So #3/#4 kill
monotonicity claims for every class ⊇ convex: exact games, large-core games,
balanced, superadditive, totally balanced. Open territory = incomparable classes.

5. **Coalitional monotonicity, n=5 VETO BALANCED**: certified violation —
   bump v({0,2,3}) by 5 (veto player 0 ∈ S, class preserved, both balanced),
   player 3 drops 1/6. Bumped game loses superadditivity (fine for veto-balanced
   claims; redo with superadditivity filter if needed).

## Probes / no-gos (domains where NO violation found — conjecture-shaped)
- Assignment entry-monotonicity (raise a_ij, watch row i / col j own payoffs):
  3×3 ≤12: 0/400; 4×3 ≤12: 0/500; hill-climb 3×3 + wide (≤40 entries, 4×4) running.
- MCST cost-monotonicity (raise edge (a,b), watch incident players'
  cost shares for a DROP): n=5: 0/500.
- Per-capita nucleolus aggregate/coalitional monotonicity: probes running.

## Literature adjudication (lit-scan + lit-narrow, 2026-07-23)
- Housman–Clark boundary SHARP: coalitional monotonicity + core selection impossible
  n≥4, possible n=3. Aggregate + core selection compatible ALL n (Calleja–Rafels–Tijs).
  → closed, no hunt.
- Hokari 2000: convex aggregate failure known AT n=4 ("as few as four agents") —
  my witness MATCHES the record, no delta. Convex PM failure known (likely n=4).
  My n=4 general witness subsumed. Megiddo-9 "improvement" already closed by Hokari.
- Veto-balanced coalitional failure: known (Arin–Feltkamp school). Rediscovery.
- Core-stability chain sharp (exact⇏large at n≥5, holds n≤4). Stable core
  characterized (Grabisch–Sudhölter 2024 nested balancedness). Closed.
- Assignment games: bargaining set=core, nucleolus=core∩kernel etc. closed;
  PMAS-admissibility characterized (Solymosi SCW 2024).
- MCST cost-monotonicity of nucleolus: LIKELY known-false (Dutta–Kar 2004 built
  their rule because standard solutions fail it) — but no verbatim source/example
  extracted. My 500 random + climbs find margin ≤ 0 exactly (suspicious plateau).
- March 2026 precedent: quasi-convex game without PMAS (IJGT) — single-witness
  disproof of 30-year Sprumont question. The wave has NOT hit coop game theory yet.

## HEADLINE WITNESS (2026-07-23)
**The nucleolus of permutation games is NOT pairwise monotonic** (n=4):
K = [[0,7,0,0],[1,0,0,1],[1,0,0,0],[0,9,1,0]]; raise K[3][2] 1→2 (only
v({2,3}) 1→2 and v({0,2,3}) 2→3 change; v(N)=11 fixed). Nucleolus goes
(1/2, 33/4, 1/2, 7/4) → (2/3, 23/3, 1/3, 7/3): player 2 — member of BOTH
improved coalitions — drops 1/2 → 1/3. Both games totally balanced (permutation);
both nucleoli in core, Kohlberg-certified exact. Mass-20 integer matrix.
File: results/WITNESS_permutation_pairwise.json.
Contrast: assignment games (bipartite case) show ZERO violations in ~2700 trials
+ exhaustive 2×2 — the bipartite/two-sided lattice structure looks load-bearing.
Novelty pending lit check on MMOR 2008 (bespoke pairwise-monotonic selection for
permutation games — does its intro exhibit a nucleolus example?).

## LIVE TARGETS (committed)
A. **Entry/valuation monotonicity of the nucleolus on assignment games** — no
   accessible source states it either way for the nucleolus (JET 2021 paywalled,
   free UB preprint being read by agent). My evidence: 0 violations in ~1500
   random 3×3/4×3/wide trials + climbs. Near-tie targeted search running.
   Either a certified witness (settles unstated question) or small-case proof.
B. **SD-prenucleolus coalitional monotonicity on general balanced games**
   (Arin–Katsev proved convex + veto-balanced; general case looks open;
   perfect "belief anchored by special cases" template shape). Blocked on
   exact recursive definition — agent extracting from preprints.

## Novelty adjudication of headline witness (2026-07-23, round 2)
- Núñez–Rafels 2002a = "The assignment game: the τ-value" (IJGT 31): proves τ-value +
  optimal stable rules pairwise monotonic; SILENT on nucleolus. Safe.
- Sasaki 1995 (IJGT 24): weak/JOINT pairwise monotonicity, core-as-set. Safe — and our
  witness SATISFIES the joint version (pair sum 9/4→8/3 rises) while violating the
  individual version: sharp "individual-but-not-joint" failure.
- Miquel 2009 (MMOR 70: 465-475): merged-τ-value pairwise-monotonic core selection for
  permutation games. Abstract silent on nucleolus; INTRO PAYWALLED, no free copy
  anywhere. UNRESOLVED novelty risk — plausible her motivation is nucleolus failure.
  Her theorem doesn't contradict our witness either way. To settle: institutional access.
- MCST big-delta campaign complete: 0 violations in 550 trials n=5,6 (core-moving regime).
- n=3 permutation: 1500+ matrices × 9 bumps clean → n=4 minimality supported.

## Final collection (2026-07-23)
- Serial rule (= SD-prenucleolus on veto-balanced) implemented + validated exactly
  vs AFM-2012 Example 2 (d=(0,6,8,8), phi=(8,2,1,1)). src/serial_rule.py.
- Veto-balanced AGGREGATE monotonicity: certified violation n=5, veto player drops
  55/2 -> 107/4 when v(N)+1; both games balanced+superadditive. (Known phenomenon,
  AFM 2012; archived redisc_agg_veto_n5.txt.)
- n=3 permutation sweep COMPLETE: 0 candidates / 4000 matrices x 9 bumps (36k tests)
  -> n=4 minimality of headline witness strongly supported.

## Loop closed (2026-07-23, final)
- Exact certified 2x2 assignment sweep: 300+/625 clean (0 violations, 0 cert-fails);
  still running to completion, results land in results/exact_sweep_2x2.txt.
- Near-tie 3x3: 1000+ matrices x 18 bumps = 18,000+ tests, 0 candidates.
- n=3 permutation: COMPLETE, 0/36,000 -> n=4 minimal (screen-level).
- Per-capita: aggregate 0/500 (theorem-consistent); coalitional 35 certified kills.
- SD general recursion: still blocked (Springer/ADDI/dokumen.pub all down).
  Unblock = any one PDF of MMOR-2014 or 2018 chapter pp.301-321.
- Deliverables: report artifact (final-collection), WITNESS_permutation_pairwise.json,
  serial_rule.py validated, memory updated.
- Near-tie 3x3 COMPLETE: 1200 matrices x 18 bumps = 21,600 kink-region tests, 0 candidates.
- Exact 2x2 sweep COMPLETE: 625 matrices x 4 bumps, ALL Kohlberg-certified, 0 violations, 0 cert-failures -> 2x2 case finite-checked on 0..4 grid.
- Vector bank job stopped (superseded by direct definitional alignment from lit agents; near-tie + exact sweeps cover its purpose). All coopgames compute concluded.

## SD-PRENUCLEOLUS BOUNDARY THEOREM (2026-07-23, definition unblocked by Max)
Recursion implemented from the 2018 chapter text (src/sd.py); validated on FIVE anchors:
chapter worked example (exact match), 2-player=prenucleolus 10/10, serial rule on veto
10/10, bankruptcy (200;100,200,300) -> (100/3,250/3,250/3) = Minimal Overlap division
(Thm 14.4 confirmed independently), convex core+monotonicity self-test 8/8.
HEADLINE 2: **SD-prenucleolus NOT coalitionally monotonic on EXACT games, n=4.**
v=(0,0,0,8,0,15,9,23,0,12,16,18,3,24,19,47), bump v({0,2,3}) 18->19, player 0 drops
101/8 -> 49/4 (-3/8). Both games exact+totally balanced+superadditive (exact LPs);
SD-Kohlberg certified; 400-direction exact lex-optimality probes clean both sides.
Companion witness on totally balanced (supbal hunt, trial 7; also totbal both sides).
=> Boundary of Arin-Katsev monotonicity = CONVEXITY itself on the chain
convex ⊂ exact ⊂ totbal ⊂ balanced. Corollary: exactness ⇏ SD-relevance.
Witnesses: results/WITNESS_sd_exact.json, hunt logs hunt_sd_*.txt. Minimizer running.

## Round-2 agent results (2026-07-23 late)
- lit-hc: exact-games impossibility NOT in literature (HC family exactness unknown,
  paywalled — being chased); SD-prekernel single-valuedness + SD-on-markets both
  confirmed unstudied. Estévez-Fernández IJGT 2013 "beyond Young's theorem" = related.
- **RESULT 3: SD-prenucleolus NOT population monotonic on CONVEX games, n=4.**
  v({0,2})=2, v({0,1,2})=2, v({2,3})=4, v({0,2,3})=6, v({1,2,3})=4, v(N)=6 (else 0).
  SD on {2,3} = (2,2); SD on {0,2,3} = (2/3, 11/3, 5/3): player 3 drops 2 -> 5/3.
  Full game + both subgames convex; certified + independently re-verified (lex probes).
  => On their home class, SD is coalitionally monotonic (their thm) but NOT PM —
  sharp separation vs Dutta-Ray (PM on convex). Agent: hunt-sd-pm.
- agent-sdpk gate: SD point equalizes bilateral SD-complaints 10/10 (7th anchor,
  independently confirms chapter's SD ⊆ SD-PK).
- Strong aggregate monotonicity of SD confirmed strictly, 150/150 (6th anchor).
- HC 1998 family RETRIEVED (Goshen College scan via Wayback; lit-narrow) and VERIFIED:
  base v exact; all four bumped games NON-exact (singleton cores confirmed by exact
  core-range LPs); whole HC proof reproduced as one INFEASIBLE family LP (validates
  the family-LP tool). Structural lemma: exact + singleton core => additive, so HC's
  pinning mechanism is unavailable on exact games; exact pinning must go through core
  faces (M_i(v') = max core x_i <= v'(N) - v'(N\{i})). Exact-games impossibility
  GENUINELY OPEN — both directions live. Guidance sent to hunt-hc-exact.
- **RESULT 4 (hunt-sd-pm closers): PM witness minimized to n=3** hub-spokes
  v({0,1})=v({1,2})=1, v(N)=2 (convex+exact): spoke 2 drops 1/2 -> 1/3 when spoke 0
  joins. Violations GENERIC: 52% (n=4), 70% (n=5) of random convex games.
  Independently re-verified.
- **RESULT 5 (hunt-sdpk): SD-prekernel MULTI-VALUED on exact games** — contains a
  positive-dimensional core segment SD ± t(1,-1,-1,1), t∈[-1/2,1/2], on
  v=(0,5,6,20,2,10,8,22,5,12,14,25,12,17,18,32) (exact+totbal, not convex);
  all points equalize all 6 bilateral SD-complaints exactly; control points fail
  correctly. Second witness on balanced+superadditive with segment radius 11/4.
  Boundary of single-valuedness = convexity (their convex singleton theorem is tight).
  Independently re-verified endpoint-by-endpoint.
- Arin-Iñarra 1996 benchmark: classical nucleolus reproduces published
  (16/9,16/9,16/9,4/3,4/3) exactly (transcribed game is NOT convex/exact per checkers
  — survey gloss wrong or transcription context differs; anchor still valid).
  New data point: SD on it = (28/15,28/15,28/15,6/5,6/5).
- Iñarra-Serrano-Shimomura 2019 survey saved to papers/ (citations + terminology
  flag: IJGT 2016a "SD-nucleolus" vs MMOR 2014 "SD-prenucleolus" — pin before citing).
- **RESULT 6 (hunt-sd-markets): SD mirrors the nucleolus on all three market classes.**
  Permutation: SD FAILS pairwise monotonicity — on OUR mass-20 witness the SAME
  player drops 1/2 -> 1/4 (worse than nucleolus's 1/3); independent random witness
  too (trial 184). One matrix kills the property for both canonical core selections.
  Assignment: 0 violations (~700 trials + exhaustive 2x2). MCST: 0/400.
  Bipartite dichotomy is solution-independent. Independently re-verified.
- STRUCTURAL LEMMAS (main session, hand-proved): in exact games,
  max_core x_i = v(N) - v(N\{i}) exactly; sum_i of these >= v(N) by balancedness
  of the {N\{i}} cover; single bumps never tighten any face bound (only S=N\{i}
  changes M_i, and then i is unpinned). => HC-style efficiency contradictions are
  IMPOSSIBLE for depth-1 exact families; any impossibility must be joint-geometry
  (or depth >= 2). Guidance sent to hunt-hc-exact; lane may pivot to EXISTENCE.
- DEFINITIONAL AUDIT (lit-scan, verbatim HC p.611): our C-MON test is
  character-for-character the literature's (one coalition bumped, ALL its members
  protected, universal quantifier). Strict-bump witnesses refute weak+strict
  phrasings. All certified refutations stand as literature-stated. Manuscript
  footnote: keep coalitional monotonicity distinct from Young's strong/marginal
  monotonicity (Shapley characterization) and from aggregate (T=N special case).

## CAMPAIGN CONSOLIDATED (2026-07-23 final)
hc-exact lane interim: thousands of exact families LP-tested, ZERO infeasible
(consistent with depth-1 obstruction lemmas); 100k-trial sweep + depth-2 +
existence experiments continuing in background. Crown-jewel question now
precisely framed: does ANY coalitionally monotonic core selection exist on
exact games? Evidence tilts toward existence. All six certified results
definitional-audited against verbatim HC p.611. Report artifact final.
- **RESULT 7 (hunt-hc-exact): MINIMAL 3-game infeasible family on balanced games**
  (base + overlapping-triple bumps A={0,1,2}+3, B={1,2,3}+1; Farkas-certified +
  independently re-verified). 2-game families always feasible (bump shrinks core)
  => 3 is THE minimal impossibility certificate size; HC's 5-game family not minimal.
  None of the 3 games is exact (consistent with escape lemma).
- **RESULT 8 (hunt-hc-exact): V-ESCAPE THEOREM on exact games** (n-independent,
  hand-proved, machine-verified): exact base + exact overlapping-arm bumps =>
  pointwise-max balanced, one shared core point serves all three games. Census
  ~209k exact families (V + star, incl. disjoint arms): ZERO infeasible.
  => The family obstruction behind HC's impossibility is ABSENT from exact games;
  existence of a monotonic core selection on exact games = the campaign's
  crown-jewel open question, evidence tilting to existence. Scope caveats:
  multi-base DAGs, v(N) bumps, n>=5 untested; disjoint-arm balance empirical.
  Engine: src/family_infeasible.py (exact Farkas certificates).
- hunt-hc-exact FINAL: census conclusive — 816k+ exact families (215,249 V +
  600,863 star, 6,000 exact bases), ZERO infeasible. Disjoint exact pairs: M
  balanced 79,954/79,954 (empirical). AUDIT CATCH: agent's "exact disjoint
  instance" has NON-exact arms (only base exact) — decoupling mechanism stands
  as illustration, disjoint case remains empirical, report worded accordingly.
  Lane closed; crown-jewel existence question handed to the manuscript.
- hunt-hc-exact snapshot: 1M+ exact families (7,500 bases), 0 infeasible; HC 5-game
  family reproduced in-engine (Farkas verified) as positive control. Razor's edge:
  min cover-slack and min M-margin both hit EXACTLY 0.000, never negative.
  PIN-INVARIANCE THEOREM (their depth-generalization of my lemma, verified + further
  generalized here): any chain constraining group T bumps only S ⊇ T, never N\T,
  so M_T = v(N)-v(N\T) is invariant at ALL depths for ALL groups => no aggregated-
  pin contradiction ever on exact games; infeasibility would need a non-pin
  polyhedral Farkas combination. Depth-2 lattice-minus-top + analytic-center
  existence tests starting.
- DEPTH-2 COLLAPSE (hunt-hc-exact): lattice-minus-top vacuous on exact games —
  top game balanced in 600k/600k arm-triples (~6,400 bases). HELLY CONJECTURE
  crystallized: b exact + each single-arm bump exact => all-arms bump balanced
  (cores of exact bumps of a common exact base always intersect). Overlapping
  pair: proven (agent). Disjoint pair partition inequality: PROVEN here via
  EXACTNESS CHAINING (t2 exact at N\S1 absorbs d2 into b(N\S1); t1 exact at
  N\S1 lifts: b(N) >= b(S1)+d1+b(S2)+d2+b(rest)). General collections/m arms:
  open, mechanism named. This conjecture is now the manuscript's mathematical
  heart — it would close the star/lattice direction entirely.

## LANE CLOSED: exact-games existence question (final form)
- Helly exact-verified: 3,017 triples exact arithmetic, 0 unbalanced tops.
- Canonical selections ALL fail individually on exact games (SD known; coordinate-
  extreme core-center 136/1059 violations) yet family LPs always feasible (1.1M+).
- COMPACTNESS REDUCTION (main session): existence of a coalitionally monotonic
  core selection on exact games <=> EVERY finite bump family is feasible
  (Tychonoff product of cores + FIP; monotonicity constraints closed, finitely
  supported). HC impossibility = one infeasible finite family (their 5 / our
  minimal 3). Non-canonicality is predicted: selection arises from global choice,
  not a formula. Open theorem = finite-family feasibility for arbitrary finite
  bump-DAGs of exact games; engine candidate = exactness chaining.
- FINAL VERIFICATIONS (hunt-hc-exact): disjoint chaining proof confirmed 0/1600;
  Helly disjoint M-balance 0/81k direct checks; non-pin depth-2 obstructions
  structurally foreclosed (unbalanced top never instantiable). FALSE ALARM
  RETRACTED (discipline ledger #8): closed-form M-balance test flagged ~10
  disjoint cases via float-exactness tolerance edge; direct balancedness LP
  (float + exact) shows 0 — lesson: near the exactness boundary trust the
  direct LP oracle over derived closed forms. Lane DEFINITIVELY CLOSED;
  m-arm Helly induction deferred to manuscript phase.

## MAJOR REVISION after external expert review (discipline catch #9)
- HELLY CONJECTURE REFUTED by reviewer: b(N)=5, proper=0, four arms
  t_k = b + 4e_{N\{k}} — all exact, cores' intersection EMPTY (x_k<=1 forces
  x(N)<=4<5), M unbalanced. VERIFIED here. Census missed it: only m<=3 arms
  tested; failure starts at m=n. CRUCIAL: family remains FEASIBLE
  (theta(b)=(2,1,1,1)) => existence conjecture SURVIVES; family feasibility
  is strictly weaker than core intersection = the paper's corrected framing.
- Fixed hypotheses: pin invariance -> proper bumps only; disjoint chaining ->
  R nonempty (2-player counterexample confirmed); overlapping lemma -> A!=B
  proper nonempty + b(N) typo; Lemma 2-game -> S=N case via +d/n shift;
  Lemma facebound -> m>=2.
- Prior art found by reviewer: Solymosi-Forgó-Pintér OTKA 2008 report claims
  proof of nucleolus pairwise monotonicity on assignment games
  (real.mtak.hu/1330, verbatim confirmed). Conjecture split: nucleolus half
  -> supported prior claim; SD half remains our conjecture.
- SD recursion CONFIRMED against accessible Arin-Katsev 2011 WP (reviewer) —
  reconstruction caveat removed; Kohlberg criterion restated as iff over
  lower level sets; balanced collection defined.
- Added: Appendix A certificates (SD satisfaction levels + weights, complaint
  tables, permutation Kohlberg data); balancedness witnesses in Thm 3.2;
  hand proof of PM theorem; assignment/permutation game definitions;
  environment manifest. Bibliography corrected (Arin 2013 not Estévez;
  Mirás Calvo et al. for core-center; Iñarra 2020 71(2) 225-266; Z. Zou;
  MPR pages; SFP2008 + ArinKatsev2011 added).
- Wording: "smallest found", sampling-scheme framing, Sasaki soften,
  "several standard selections". Discipline ledger now NINE catches.

## SECOND REVISION (review round 2 — all items addressed)
- SDPK segment proof REPLACED with reviewer's parametric satisfaction formulas
  (verified exactly at 7 values of t; constancy-of-fixing-order argument makes
  the interpolation rigorous). "Identical fixing structure" claim was wrong —
  structures DO differ at endpoints (verified).
- REAL certificate package built: paper/supplement/{certificates.json (21KB:
  full game tables, per-coalition exactness witnesses for all 6 exact games,
  complete satisfaction/excess tables, positive weights for EVERY cumulative
  level set incl. permutation SD certs), verify_paper.py (one command, 50+
  exact checks, ALL PASS), generate_certificates.py, environment.txt}.
- Search-methodology language corrected everywhere: negative campaigns are
  float-screened with exact certification of positives (none arose); only the
  2x2 assignment sweep is fully exact; PM frequencies reframed as exploratory/
  indicative (counting scripts not preserved).
- Prior art sharpened: Solymosi-Brugueras-Raghavan 2012 manuscript (via OTKA
  final report real.mtak.hu/12261) cited; open problem = recover that proof.
- "Only known" qualified (Dietzenbacher 2021: Dutta-Ray-tradition egalitarian
  solutions are coalitionally monotonic core selections on convex); SD's
  distinction = balanced-domain core selector + both convex & veto monotonic.
- Tightenings: face-bounds conclusion restricted to partition aggregation;
  "can fail when m=n=4"; Prop 7.5 = empty-intersection-insufficient only;
  existence conjecture per fixed n; SD-relevance via footnote; Tijs et al.
  1984 + Curiel-Tijs 1986 cites; witness superadditivity stated (companion
  dropped); n<=2 PM minimality sentence; two-stage recursion; Farkas
  multipliers 9x1+2x2; nonempty-S bump def; PDF metadata; 0 overfull.

## THIRD REVISION (round-3 audit — release candidate)
- MAJOR PRIOR-ART INTEGRATION (reviewer + verified here): Dietzenbacher 2021
  L_max/procedural egalitarian = coalitionally monotonic core selection on
  PES-stable ⊇ large-core games; Biswas et al. 1999: exact n<=4 => large core.
  => EXISTENCE SETTLED AFFIRMATIVELY for exact n<=4 (new Prop 7.6 in paper);
  conjecture restated for n>=5; frontier = Dietzenbacher's PES-stability
  question; census reframed as pipeline validation (implied by the theorem).
  VERIFIED on our own games: corrected large-core checker (must include the
  grand-coalition constraint in U(v) — first version had a bug) shows all 4
  exact witnesses have large cores. "Non-standard selection" claims removed.
- SDPK proof: full stage-induction with the two half-interval fixing orders
  (both orders VERIFIED computationally at t=±1/4, matching reviewer's);
  stale "identical fixing structure" sentence purged from Appendix A too.
- Supplement hardened: verify_paper.py now STANDALONE (stdlib only, runs on
  bare system python3), checks stored-vs-recomputed level-set EQUALITY,
  full coalition coverage, the 5.4 subgame certificate, bump relations;
  7 segment samples in JSON. All checks pass.
- Wording: "can fail at m=n=4" everywhere; float-screen false-negative
  caveat added; "eight games claimed exact + one by convexity"; stale
  "extensive exact search"/"all numerical claims" fixed in intro.
- IJGT prep: abstract 206 words, keywords, declarations (data availability,
  AI-assistance disclosure, competing interests), PDF metadata. Remaining
  pre-submission items for Max: affiliation/email, author-year reference
  conversion, Online Resources packaging, Miquel novelty resolution.
- Bib: Biswas et al. 1999 added; SD-prekernel mimeo -> IKERLANAK IL 96/16.

## FOURTH REVISION (submission-preparation pass — complete)
- All 8 exact games verified large-core (Prop attribution now Dietzenbacher's
  observation w/ Biswas; large core + PES-stable defined; Sharkey 1982 cited).
- "A stronger sufficient route" (PES-stability sufficient, not equivalent);
  §7.3 heading renamed; "no selection is known to work"; 36k sweep
  float-qualified; Dutta-Ray "elsewhere" clause removed; Miquel
  "states" not "proves"; Dietzenbacher-Doğan 2025 cited.
- Verifier integrity: stored Farkas multipliers now AGGREGATED and checked to
  refute (corruption test: tampered multiplier -> exit 1); segment samples'
  t-labels parsed and x(t)=SD+t(1,-1,-1,1) asserted.
- IJGT format: author-year (natbib) throughout, alphabetized bibliography
  (Maschler<Miquel<Mirás), Mueller-Trost entry removed, SBR prose-only w/
  footnote URL, verified DOIs (ArinKatsev2016a, DietzDogan2025), affiliation
  placeholder + corresponding email, Funding: none, AI disclosure in §8,
  Online Resource 1 naming, TU spelled out, abstract lit-refs removed.
- Final build: 16pp, 0 errors, 0 overfull, 0 undefined citations.
- REMAINING FOR MAX: affiliation fill-in, Miquel full-text novelty check,
  read-through, IJGT upload.

## FIFTH REVISION (round-5 — upload-ready package)
- Verifier Prop 7.5 checks now CERTIFICATE-DERIVED (face caps sum 4 < b(N)=5;
  all-arm collection 16 > 15), replacing the literal expression the reviewer
  spoofed; final statement narrowed to certificate-backed claims (non-exactness
  + large-core prose claims explicitly delegated to the LP pipeline).
- Núñez–Rafels corrected to 2003 (publisher-verified, DOI added).
- Bibliography in IJGT house style ("Arin J (2013) Title. Int J Game Theory
  42:325–337"), (Young 1985) punctuation via aysep, 24/26 entries with
  VERIFIED DOIs (doi-fetch agent, Crossref; Curiel-Tijs legitimately DOI-less;
  2 working papers). Added: Kohlberg 1971, Dutta-Ray 1989, Schmeidler 1972
  (exact games), Arin-Feltkamp 2012 EJOR (published serial-rule source,
  replacing the CeDEx discussion paper). Dietz-Doğan = IJGT 54:42.
- Front matter: conventional affiliation block + corresponding author;
  "Statements and Declarations"; Online Resource 1 zip packaged with README
  metadata + caption (generator script excluded).
- Scope claims restricted to pinning/partition/two-arm mechanisms as proved.
- Final: 16pp, 0 errors/overfull/undefined; Miquel body check + affiliation
  remain the only Max-side items.

## SIXTH REVISION (prior-art catch #10 — Peleg-Sudhölter)
- DECISIVE PRIOR ART (reviewer): Peleg-Sudhölter 2003 textbook Thm 8.2.3
  already gives a 3-game (base + two bumps, n=4) impossibility construction;
  Arin 2013's construction also implicitly needs only 3. Our novelty shrinks
  to: (a) the two-game feasibility lemma, (b) the EXACT MINIMALITY statement
  (3 = optimum), (c) our self-contained certificate + six-line proof —
  reviewer confirms the minimality statement appears unrecorded.
- Reframed: abstract, intro contribution 1, §3 preamble, Thm 3.2 closing;
  PelegSudholter2003 added to bibliography (DOI 10.1007/978-1-4615-0308-8).
  Discipline ledger: TEN catches (this one at round 6 of external review).

## NEW CAMPAIGN: EGALITARIAN STABILITY (Dietzenbacher 2021 open question)
Target (verbatim from GEB 127:194-205 concluding remarks): "Whether all exact
games and all stable core games with an arbitrary number of players are
egalitarian stable is an interesting open question." Frontiers: exact n=5
(Biswas: exact n<=4 => large core => ES), stable-core n=6 (Estévez-Fernández
GEB 76 (2012) 160-180: large <=> stable core for n<=5).
- lit-es CONFIRMED: both halves open, no 2021-2026 attack; Dietz-Doğan 2025
  is PMAS-domain work, doesn't bear. PES primary: Dietzenbacher-Borm-Hendrickx
  GEB 106 (2017) 179-187.
- Lanes: hunt-pes (PES impl + random exact n=5 sweep), hunt-fam5 (family
  feasibility, dichotomy hunt), theory-es (both directions), main-session
  structured Example-3-lift probe + independent validated ES implementation
  (src/es_check_main.py, gates: paper Examples 2 & 3 exact match).

## ★★ HEADLINE: DIETZENBACHER'S OPEN QUESTION RESOLVED (exact half, negative)
2026-07-24. Witness found by main-session structured probe (Example-3 lift,
trial ~34): 5-player EXACT game, NOT egalitarian stable.
v (bitmask) = [0,0,0,0,3,3,3,3,0,0,0,0,4,4,4,4,0,0,0,0,4,5,5,5,0,0,0,0,4,5,5,6]
i.e. hub player 3: v({3})=3; +4 gives 4; +5 gives 4; +5+(1 or 2) gives 5;
v(N)=6; coalitions without 3 all 0. Claims (1,1,3,1,1) sum 7 > 6 = v(N) =>
N not egalitarian-admissible. Admissible {3},{3,4},{3,5},{1,3,5},{2,3,5};
maximal {3,4},{1,3,5},{2,3,5}; D = {3} (INTERSECTION reading of strong
claimants — verified on paper Ex2/Ex3; union reading is wrong).
PES = (3/4,3/4,3,3/4,3/4), violates {3,4},{3,5} by 1/4, {1,3,5},{2,3,5} by 1/2.
VERIFIED: balanced + exact (30 exact LPs) + hand-traced procedure + validated
independent implementation (es_check_main.py, gated on paper Examples 2,3).
n=5 MINIMAL (exact n<=4 => large core => ES, Biswas/Dietzenbacher).
Consequence: L_max/PES dead as monotonic-core-selection candidate on E_5;
our paper's "stronger sufficient route" is closed off; existence conjecture
for E_5 now has NO known candidate solution. Mechanism: hub-incompatible
tight coalitions inflate claims past v(N) while exactness survives.
Pending: hunt-pes independent cross-verification, minimization, theory-es
infinite-family generalization (all n>=5), fam5 dichotomy hunt continues.
- theory-es INDEPENDENTLY resolved the question in parallel (own witness:
  v(N)=10, claims (1,7/2,3/2,7/2,1) sum 21/2; hub player 1; two internal
  implementations + core witnesses for all 30 coalitions). CROSS-VERIFIED
  both ways through main-session implementation => THREE implementations,
  TWO independent witnesses. Structural Lemma (theory-es): ES <=> claims
  vector in core <=> sum(claims) = v(N). Frequency: 4/4 seeds hit within
  dozens of trials — non-ES exact games are COMMON at n=5 (why it stayed
  open: random aspiration probes don't find the claims vector).
  Main witness locally minimal under single decrements (max value 6).
  Remaining: infinite family all n>=5 (theory-es), hunt-pes third-path
  verification + stats, fam5 dichotomy hunt, then the note.
- hunt-fam5 interim: n=4 positive control matches paper certificate exactly;
  ~1,160 n=5 families float-screened, 0 infeasible (min slack 0.05, never <=0);
  n=5 CO-SINGLETON analog EXACTLY certified (5 arms, empty core intersection,
  family feasible, x^b=(2,1,1,1,1)) — Prop 7.5 extends to n=5. KEY LEAD:
  slack ~ core width; exact-preserving arms need positive width => candidate
  uniform lower bound = existence-proof skeleton. Retasked to firm it up.
- theory-es COMPLETE: (a) 4th independent verification of primary witness;
  (b) INFINITE FAMILY: padding operation (adjoin p, v'(S∪p)=v(S)+c) preserves
  exactness for any c>=0 (core(v') = core(v)×{c}, clean proof); c=0 null case
  PROVEN non-ES via Inertness Lemma => exact non-ES game FOR EVERY n>=5, QED;
  c=1 all-essential variant verified n=6..9. (c) Hub over-cover mechanism
  proposition. (d) Obstruction insight: symmetric scaling templates collapse
  to ES under exactification — asymmetry essential. SHARP THRESHOLD THEOREM:
  exact => ES iff n<=4. Notes: results/theory_es_notes.md, src/es_family.py.
- hunt-pes COMPLETE: THIRD independent witness, now CANONICAL — v(N)=4,
  claims (1,1,1,1,1) sum 5>4, monotone+superadditive+exact, minimal v(N)
  over 2-point configs; generator v(S)=min(x1(S),x2(S)), x1=(0,0,1,1,2),
  x2=(1,1,0,2,0) + general lemma: min over finite point set is ALWAYS exact.
  18 validation gates. WHY IT STAYED OPEN: exactified random games are
  non-large-core only 3/499 => searches never left the ES-safe region;
  point-generator hits the thin-core frontier (2.6% non-ES, 6.5% at k=2).
  Cross-verified via main implementation => 3 witnesses x 4 implementations.
  PES=(3/4,3/4,3/4,1,3/4) leaves core. Note drafting: primary witness swapped.
- hunt-fam5 WIDTH-SLACK LAW: t* >= min_w/(n(n-1)) over 1,244 families, ZERO
  violations; tight EXACTLY at simplex co-singleton family (t* = c/(n(n-1))
  analytically, all c, all d). Right normalizer = min PER-PLAYER coordinate
  width (not coalition directional width). Mechanism: slack feeds n-1 members
  by dropping excluded player toward its exactness floor. min_w = 0 collapses
  to (n-1)-player game (induction base). Lemma skeleton: maximin core point +
  explicit per-arm dominating construction. RETASKED: test the LEXIMIN-ABOVE-
  FLOORS core selection DIRECTLY for coalitional monotonicity on exact games
  (incl. thin-core point-generated) — candidate constructive resolution of
  the existence conjecture.
- hunt-pes FINAL: minimized canonical witness mass 41 (v(N)=4 floor proven),
  cross-verified 4th time; frequency 493/18,507 = 2.66% non-ES among
  point-generated exact n=5 (symmetric-claims mode only 2/493 — rare);
  lane CLOSED. Note assembly: skeleton compiles, §4 rework in progress.
- hunt-pes LANE CLOSED: mass-41 form locally minimal (single decrements,
  exhaustive); mass-46 generator form shrinks to it; tight coalitions
  identical in both => one trace table serves both. Official trace archived
  (canonical_witness_trace.txt); one-round failure visible immediately.
  Note draft delivered to Max (8pp); awaiting theory-es final polish.
- Paper-2 supplement verifier built (stdlib-only, gated on paper examples);
  CAUGHT catch #11: halfinteger block stored lambda=13/8 (doesn't meet
  budget); correct PES = (1,7/2,3/2,3,1), lambda=3, three violations by 1/2.
  Other three blocks verify perfectly. Fix requested from theory-es.

## PAPER 2 FINAL ASSEMBLY (2026-07-24)
- theory-es shipped final sections (placeholder filled, final frequency
  numbers, 3 overfull boxes fixed); halfinteger PES block hot-patched with
  verifier-correct values (lambda=3; generator fix owed by theory-es).
- Final build: 8pp, 0 errors/overfull/undefined. OnlineResource1_paper2.zip
  packaged (supplement_data.json + verify_paper2.py + README); verifier
  passes STANDALONE from the archive in a clean dir (bare python3).
- hunt-stable: assignment route CLOSED for counterexamples — 23,564
  strictly-stable non-large 3x3 games (+ ~12k broad) ALL ES; 250 dual-
  implementation cross-checks clean; literature lead: Llerena-Núñez-Rafels
  2010 Lorenz-maximal result suggests "stable-core assignment games are ES"
  is a THEOREM (caveat: DR-vs-PES identity unverified). 4x4 running;
  prong 1 (padded-witness core stability) started.
- hunt-stable PRONG 1 DONE: our witnesses + ALL paddings have NON-stable
  cores — certified undominated escape imputations (deterministic vertex
  enumeration; sampling finds nothing — standing methods lesson) + LIFT
  LEMMA (escapes survive padding, proof). Assignment route: 35,854 stable
  non-large games (n=6 AND n=8) all ES. Second half stays OPEN; needs
  non-assignment n>=6 stable-core structure. RETASKED: big-boss/clan
  stable-core generator (veto-hub shape = our over-cover mechanism!) +
  positive companion proof attempt (dominant-diagonal assignment => ES via
  Llerena-Núñez-Rafels Lorenz-maximal route).
- ★ LEXIMIN VERDICT CLEAN (hunt-fam5): leximin-above-floors core selection
  survives 2,004 exact-preserving bumps (n=4: 0/1503, n=5: 0/501) INCLUDING
  thin-core point-generated frontier. LIVE CANDIDATE THEOREM: leximin is
  coalitionally monotonic on exact games => constructive resolution of
  paper-1 Conjecture. Mechanism: floors pinned by exactness; single-halfspace
  tightening; self-defeating-drop argument. Diamonds respect width floor
  (min ratio 0.125 > 1/20); co-singleton extremal confirmed. Division of
  labor: fam5 = adversarial stress + n=6; theory-es = formal proof (also
  test necessity: balanced non-exact counterexample for sharpness);
  main = independent replication (running).
- theory-es LEXIMIN PROGRESS: (1) EXACTNESS NECESSITY PROVEN — two certified
  balanced non-exact counterexamples (n=4, n=5; the n=5 one has ALL floors
  core-attained => coalition-level exactness is the real hypothesis; sharp).
  (2) EXACT-INTERVAL LEMMA proven: both endpoints exact => whole bump path
  exact; reduces conjecture to 1-parameter Lemma C (parametric leximin
  monotonicity along exact paths). (3) Smoothing/KKT route DEBUNKED
  (unreliable — honest negative). (4) Binding regime rare; binding-only
  hunts clean; two-sided pattern (S gains, outsiders lose). Crux open;
  nested-tight-set route next. Fragment capture ordered first.
- hunt-stable BIG-BOSS RESULT: literature CORRECTION (big-boss cores NOT
  unconditionally stable — certified counterexamples; MNPT's stable-set claim
  needs convexity/union-tightness). KEY STRUCTURE: interior slack destroys
  stability AND ES simultaneously (coupled failures). Both classical stable-
  core families force ES => EMERGING TARGET: general theorem 'stable core =>
  egalitarian stable' (would resolve Dietzenbacher's 2nd half POSITIVELY;
  with our exact-half negative = complete resolution of his question).
  Entry: if non-ES, is PES itself an undominated escape? (decisive cheap
  check ordered on our certified witnesses). ES <=> claims fit box lemma
  for big-boss recorded.
- theory-es LEXIMIN REFINEMENT: cone condition (star_S) isolates exactness's
  role — necessary for monotonicity (no exceptions), holds 39/39 on exact
  binding bumps, FAILS at the non-exact counterexample; NOT sufficient alone
  (22/1696 non-exact star-yet-drop; earlier equivalence claim self-retracted
  — 200-sample artifact). Reduction: (A proven) + (D: exact => star, open) +
  (E': star-along-path => monotone, open). Fragment banking ordered;
  Lemma D attack assigned: MIXING of attaining core points (convex combos
  automatically respect tight constraints; z + w^i repairs; corner case
  phi_i = M_i to rule out).
- theory-es FINAL: paper3 fragment banked (3pp, compiles clean) — conditional
  theorem (leximin monotone on exact games modulo Lemmas D,E') +
  UNCONDITIONAL necessity theorem (certified) + Lemma A + cone condition +
  evidence tables. Lemma D reduced to sharp dual: (star) fails <=> phi on a
  positive-S-weighted max face (r_k>=1); verified 200/200; open content =
  'exact => no non-uniform such face when binding-bumpable'; mixing
  construction insufficient (11/16). Corner case ruled out empirically
  (0/16+). Lane CLOSED after two serious proof attempts — the two open
  lemmas are the campaign's flagged frontier.

## BREAKTHROUGH PUSH (no-partials directive) — status 2026-07-24 afternoon
Four lanes deployed; three crashed on API ECONNRESET after hours of work;
ALL FOUR RESUMED via transcript-resume messages (liveness monitor armed).
Pre-crash progress banked:
- prove-lemD R4: leximin ALWAYS maximizes a nonneg stratum-weighted sum
  (round-1 dual, pi on lowest stratum) => max-faces intrinsic; Lemma D =
  "exact => never strictly positive on binding-bumpable S". Normal-cone
  system written out.
- prove-stES: escapes = SINGLE-STRIP of claims vector (capped player to
  floor); 48/48 non-ES games have escapes (contrapositive empirically
  universal); 47/48 single-strip; exceptional-case rule = missing lemma.
- hunt-stable: skeleton Lemmas A,B,1 + ceiling mechanism; same gap
  (right-vertex selection). Two lanes converging on the same last lemma.
- wildcard: target = DM bargaining set vs core on EXACT games (known n=5
  BS⊋core example is totally-balanced, exactness UNCHECKED => live gap);
  BS-membership LP being built; stable-set-existence parked (uncertifiable).
- VERIFICATION PASS: all four lanes alive post-crash-resume.
  prove-lemD: LEMMA D PROVED MODULO ONE INEQUALITY (P3): with W = union of
  cover coalitions, T* = W∩S, modular identity 1_S+1_W = 1_N+1_T* gives
  M^(T*) <= v(N)+v(T*)-v(W); (P3) delta := v(S)+v(W)-v(N)-v(T*) >= 0 (empir.
  delta = 0 EXACTLY, 38/40; 2 anomalies under study; intermediate 'Conj C'
  refuted and being revised) => M = v(S) => star-fail S never binding-
  bumpable (91/91 at scale). One inequality from the theorem.
  prove-stES: CRITICAL REFRAME — stable=>ES already a THEOREM for n<=5
  (E-F 2012 + Dietzenbacher); open frontier = n>=6 (stable-but-non-large
  first exists there); n=5 work validates the escape construction (48/48);
  jobs: general-n proof + n=6 direct hunt.
  hunt-stable: rule_finder running (400 trials); wildcard: BS-vs-core probe
  built (bs_probe.py), hunts running.
- ★ prove-lemD DECISIVE: LEMMA D PROVED modulo one sub-lemma (2-valued cover
  dichotomy, exhaustively + adversarially verified, 0 exceptions n=5,6).
  Proof chain: exact-preservation reframing of binding-bumpable (dissolves
  the earlier anomalies; delta=0 was an artifact, delta=-3 occurs); Bridge
  Lemma; cover-convexity => min_core x(W) >= phi(P)+v(T*); modular identity
  => forcing T* tight caps x(S) at phi(S) => d* <= slack. Dead ends
  catalogued (incl. S-tightness — my hint, killed). Remaining for the full
  leximin theorem: Step 2 (dichotomy — basic-certificate dimension-counting
  angle suggested: only ONE 2-valued cover needed per failure) and Lemma E'
  (path monotonicity). Zero counterexamples to Lemma D anywhere.
- prove-lemD CORRECTION (catch #13, self-caught via basic-solution probe):
  2-valued cover dichotomy FALSE (>=3-valued covers exist at n>=6, rare;
  n=5 universality was sampling artifact). CLEANER SURVIVING STRUCTURE:
  Lemma D reduces to ONE inequality (KEY): v(W) >= phi(P) + v(T*)
  [W = P ∪ T* disjoint], verified universal incl. the non-constant case;
  PROVEN for constant-on-T* covers (all n=5, most n=6); non-constant
  reduces to GOAL3 (r-level-set slack chain). Reformulation sent:
  (KEY) <=> min{y(R): y core, y(W)=v(W)} <= phi(R) — leximin-optimality
  handle on the top-residual set R = N\W. Lemma D itself: still ZERO
  counterexamples over thousands of games.
- prove-lemD FINAL FORM of the D-gap (catch #14 = my R-form algebra slip,
  caught by agent): (KEY) <=> slack(W) <= slack(T*) — adjoining the
  sigma-covered off-S players P never increases leximin slack. Three
  equivalent forms exhausted; proven for constant-on-T* covers (all n=5);
  general case = flagged frontier inequality. BANKED; agent pivoting to
  Lemma E' (path monotonicity) with the cover/convexity machinery.
- ★ CONSOLIDATION (prove-lemD): E' REDUCES TO D'S CRUX — the infinitesimal
  and endpoint versions of the same fact. WHOLE LEXIMIN THEOREM now hangs
  on ONE inequality: slack(W) <= slack(T*) at star-fail configurations.
  Two-sided transfer mechanism characterized (forced S-increase sourced
  entirely from N\S — matches independent observations in fam5 + ES lanes).
  Crux-reduction theorem being written; then all force on (KEY).
- prove-lemD lane CLOSED WITH HONORS (D proven for all observed n=5 configs;
  reduction theorem written with honest gap; 5 dead angles catalogued).
  NEW LANE key-hunter: single target = (KEY) slack(W) <= slack(T*).
  Jobs: (1) falsification with teeth — CONSTRUCT non-constant-cover
  star-fail configs (reverse-engineer the known n=6 instance) and batch-test
  (KEY) + d*-vs-slack; (2) fresh polyhedral routes: simultaneous-flooring
  face geometry, UNCROSSING/tight-set lattice check (if tight sets at phi
  close under union, W is tight and (KEY) is instant — cheap decisive
  opening check ordered).

## 2026-07-24 — (KEY) RESOLVED: FALSE (key-hunter lane, decisive)
- ★★ (KEY) slack(W) <= slack(T*) is FALSE. Certified exact n=6 counterexample
  (results/WITNESS_KEY_FALSE_n6.json): v with v(N)=29, phi=leximin=
  (20/3,8/3,19/3,6,14/3,8/3), S={0,2,3,4} star-fails with valid Farkas cover
  {1,2}:1,{0,1,5}:2,{2,3,5}:1; W={0,1,2,3,5}, T*={0,2,3}, P={1,5};
  v(W)=24 < phi(P)+v(T*)=73/3, margin -1/3. Step-6 certificate M^(T*)<=phi(S)
  also false (core witness x=(7,2,8,4,5,3): x(T*)=v(T*)=19, x(S)=24>71/3).
  Symmetric second case S={0,2,3,5}. Batch: 10 distinct violations at n=6,7
  out of ~9000 star-fails (~0.1% — why thin sampling had wrongly "verified" it).
- CONSEQUENCE: the crux-reduction proof route (Steps 4-7, certificate T*=W∩S)
  is DEAD — it rested on a false lemma. Also independently killed: tight-set
  lattice route (W not tight in ~82% of star-fails; exact ≠ supermodular) and
  constant-cover rescue (explicit S with NO 2-valued cover at all).
- THEOREM SURVIVES: in ALL 10 violations d*(S)=0 (S not exact-bumpable),
  certified by a coalition C ≠ W∩S. Zero Lemma-D refutations anywhere.
- REVISED TARGET (D0): star_S fails ⟹ d*(S)=0, with certificate C produced
  directly from the star-fail structure (revives the old Conjecture-C hunt;
  the cover's W∩S is provably the wrong vehicle).
- MAIN-SESSION INDEPENDENT VERIFICATION: leximin recomputed = stated; phi in
  core; star_S failure re-derived (max y(S)=71/3=phi(S)); cover coalitions
  tight; (KEY) margin -1/3 re-derived; step-6 core witness checked (62
  constraints). Exactness (62 LPs) + d*(S)=0 running in background.
  NOTE (discipline catch #15, harness-side): lemD.py binding_bumpable() is
  the NAIVE core-max notion (max_core x(S) > phi(S)) — TRUE here (d=4/3)
  even though exact-bump d*(S)=0. Lemma D's operative notion is
  max_exact_bump/exact_bumpable. Do not conflate.
- Paper-3 fragment UNAFFECTED: sections_leximin.tex never stated (KEY) or the
  reduction theorem — (D)/(E') are marked open, main result conditional.
  Fragment to be STRENGTHENED with the new counterexample (it sharpens why
  the natural dual certificate fails).

## 2026-07-24 evening — stES frontier: two unconfirmed survivors; pkill incident
- prove-stES: cand1/cand2 (n=6 exact non-ES, no-hub, every singleton exact)
  SURVIVED full 5M-vertex coalition+floor arrangement enumeration with NO
  undominated escape found. NOT claimed as counterexamples — two honest gaps:
  (i) float domination screen (exact re-enum running), (ii) COMPLETENESS GAP:
  undominated-set vertices can lie on projected-core-vertex-coordinate planes
  absent from the coalition+floor arrangement. STANDING CAVEAT adopted: all
  escape_enumerate-based ABSENCE claims (n=5 included) are incomplete-arrangement
  results; the tool is validated to FIND escapes, not certify absence.
  Close-out plan: exact re-enum → extended arrangement with core-vertex planes →
  independent complete stability certificate (Gillies/GS route). Cross-check
  ordered: hunt-stable's escape construction attacking cand1/cand2 directly.
- hunt-stable resumed: rule_finder batches running; main task = close the ~5%
  escape-construction gap (corpus + vertex diff + generalization), now with
  cand1/cand2 as priority targets.
- INCIDENT: prove-stES over-broad `pkill python3` killed key-hunter's six
  _key_float falsification batches + _lemD_nc/_key_main + THREE cross-session
  jobs (sbo_extend.py [woodall/rank-4 session], intensify.py [EFX session],
  hunt_jiasong.py). key-hunter notified to restart; cross-session losses
  surfaced to Max. NEW RULE: kill by pid/unique script pattern only; batch
  jobs must checkpoint to disk.

## 2026-07-24 evening 2 — wildcard terminal state + fleet resource war resolved
- wildcard CLOSED (hunting): no kill. Deliverables: (1) src/bargaining_set.py —
  exact DM bargaining-set oracle, VALIDATED on the published Atay-Núñez-Solymosi
  2025 minimal BS≠core example (reproduced exactly) + convex + empty-core
  anchors. (2) DECISIVE GATE: the known n=5 BS≠core example is NOT exact
  (worker singletons v=0 vs core-min=1); exactifying makes it convex. No
  "exact⟹BS=core" theorem in the literature — the question is apparently OPEN.
  (3) Sweep ~300 thin-core exact games: ZERO BS-outside-core, kernel⊆core
  throughout. (4) Structural no-go: many-to-one market games never exact
  (0/20) — exactness deletes the underpaid-singleton mechanism.
  CONJECTURE-SHAPED RESULT: exact ⟹ BS=core AND kernel⊆core (both apparently
  open, positive). wildcard redirected to CPU-light proof attempt: MPS-1971
  geometry with exactness-attainment replacing convexity (kernel⊆core), and
  Solymosi maximal-excess-balancedness route (BS=core).
- INFRA POSTMORTEM: BOTH prove-stES and wildcard ran blanket pkill python3;
  wildcard's kills hit the stES exact re-enum repeatedly (root cause: 8 enum
  workers pinning all 14 cores → wildcard timeouts → cleanup kills). Fleet
  rules now law: kill by pid only; nice -n 10 all batches; ≤6 workers per
  lane; append-only checkpoints. All three compute lanes relaunching.

## 2026-07-24 evening 3 — wildcard UNBLOCKED (main session lit retrieval)
- wildcard's blocker (paywalled Solymosi 1999 maximal-excess-game definition)
  RESOLVED by main session: Atay-Solymosi EL 167 (2018) p.101 open PDF states
  it verbatim. ê_x(S) = max_{T⊆S} e_x(T) = MONOTONIC COVER of the excess game
  (wildcard's failed reconstruction was the superadditive/partition cover).
  Solymosi 1999: superadditive + x imputation outside core + ê_x balanced ⟹
  DM justified objection (x not in classical BS). Holzman 2001 Thm 1: ê_x
  balanced ⟺ x ∉ Mas-Colell BS (iff!). PROOF TARGET now concrete:
  (T) exact ⟹ ê_x balanced for every imputation x outside core.
- Survey (Iñarra-Serrano-Shimomura 2019 §5.3) also yields: Solymosi 2002
  (n≤4 balanced ⟹ classical BS = core — conjecture's open content starts
  n=5); Maschler 1976 JET 13:184-192 five-person totally balanced game with
  BS ⊋ core — DECISIVE EXACTNESS GATE ordered; Izquierdo-Rafels 2012b
  threshold k*(v) with formula (v(N) ≥ k*(v) ⟹ BS=core) — alternative
  route: exactness ⟹ v(N) ≥ k*(v).

## 2026-07-24 evening 4 — wildcard MPS door closed (certified), ê_x route live
- wildcard pinned WHERE convexity enters MPS kernel⊆core: excess game
  supermodular ⟺ v convex; supermodularity makes max-surplus argmax coalitions
  a lattice — MPS's lever. CERTIFIED on exact non-convex games: excess game
  non-supermodular AND the max-surplus lattice property FAILS (witness n=5
  exact v=[0,2,0,5,0,5,1,8,1,4,1,7,1,7,2,10,0,4,0,6,0,7,1,10,1,6,1,7,1,9,2,12],
  x=(48/11,18/11,0,18/11,48/11): S={0,1,4},{0,3,4} both attain s_{4,2}, union
  does not). Both naive routes now closed with certificates: level-set
  balancedness (vacuous) + MPS lattice (lever absent).
- Sole principled route = ê_x balancedness (T), now UNBLOCKED (defs retrieved
  prev entry); Holzman iff means (T) ⟺ Mas-Colell coincidence exactly.
  wildcard redeployed on (T) after a delivery race (stood down asking for the
  definition already in its inbox).

## 2026-07-24 evening 5 — key-hunter certificate regression: (D0) corrected, (STRAT-CERT) target
- CORRECTION (catch #16, self-caught by agent): "(D0) d*(S)=0 at every star-fail"
  was a biased-subsample artifact (only the 139 (KEY)-violations were measured).
  Broad corpus ~130k star-fails n=6/7: ~0.2% have d*>0 (d*=1,2 seen), ALWAYS
  d*≤slack. Lemma D (the actual theorem invariant) intact: 0 refutations
  anywhere. Floor form M^(C)=v(S) NOT universal; operative bound M^(C)≤phi(S).
- Main session's tight-set hypothesis REFUTED with a 2-line proof: a phi-tight
  certificate would force phi(S)=v(S), contradicting slack>0. Certificates live
  OFF the tight family.
- CERTIFICATE STRUCTURE (the real find): a theorem-cert always exists and can
  always be taken C⊆S within a SINGLE leximin stratum; ~99.9% a SINGLETON k∈S
  (rare same-stratum pair). Verified exactly on the (KEY)-FALSE witness:
  C={0}, M^({0})=22=v(S)≤71/3=phi(S). Certifying k NOT confined to the lowest
  stratum (~50%) — proof can't fix the stratum a priori.
- NEW TARGET: (STRAT-CERT) star-fail ⟹ ∃ single-stratum C⊆S with M^(C)≤phi(S);
  singleton form (SINGLE-CERT) is the working conjecture. Paper3 fragment
  paragraph corrected accordingly (d*=0 claim removed), PDF rebuilt.

## 2026-07-24 evening 6 — key-hunter lane CLOSED WITH HONORS (terminal state)
- (RMIN-CERT): certifying singleton = MINIMUM-RESIDUAL member k∈S (r_k=1 in
  the star-failure's dual cover). Match 99.6% n=6 / 100% n=7 (~1100 cases);
  coincides exactly with singleton-cert existence; residue = same-stratum pair.
  Verified exactly on the (KEY)-witness ({0},{2} both certify).
- EXACT DUAL (DUAL-k): M^({k})≤phi(S) ⟺ ∃ nonneg weights on phi-tight
  coalitions, coverage β on N∖S, β−1 on S∖{k}, β+γ−1 on {k}. By strong duality
  the whole conjecture ⟸ constructing this cover. S-internal support suffices
  only ~68%/57% — proof MUST use phi-tight coalitions CROSSING S. That crossing
  construction = the named open frontier.
- Final arc: (KEY) false (certified) → (D0) corrected → theorem 0 refutations
  in ~130k star-fails → cert structure (single stratum ⊆ S, min-residual
  singleton) → dual reduction (DUAL-k). Honest exhaustion; deliverable met.
  Fragment updated with (RMIN-CERT)+(DUAL-k) as the leave-off frontier; PDF
  rebuilt. Tools: _dcert_mine.py, _d0_safety.py, covertest.py. LANE CLOSED.

## 2026-07-24 evening 7 — wildcard: (T) refuted (Mas-Colell ⊋ core on exact); classical route re-armed
- (T) "exact ⟹ ê_x balanced outside core" is FALSE — certified: exact game
  COUNTEREX_es_n5_s1_t23, x=(17/3,7,5,2/3,2/3) IR imputation outside core,
  ê_x has EMPTY core. By Holzman's iff ⟹ MAS-COLELL BS ⊋ CORE on exact games
  (likely confirmation of Izquierdo-Rafels convexity characterization, not
  novel — correctly flagged by agent). Classical DM BS still excludes those
  points (oracle-verified) — classical conjecture INTACT; scope error in the
  route caught by the agent (ê_x criterion is Mas-Colell-iff, classical-
  sufficient only). Filter gained: classical witnesses ⊆ ê_x-non-balanced set.
- MAIN SESSION RETRIEVALS (Izquierdo-Rafels EB 2012 open access): k*(v̂) LP
  formula (Thm 1: v(N)≥k* ⟹ classical BS=core AND kernel⊆core) — new proof
  route "exact ⟹ v(N)≥k*" with empirical k*-test ordered (caution: k* not
  tight, glove market k*=4>2=v(N) with coincidence anyway). MASCHLER 1976
  GATE SETTLED: v(S)=min{|S∩P|,½|S∩Q|}, singleton core (0,0,½,½,½),
  min_core x({3})=½>0=v({3}) ⟹ NOT exact — conjecture survives its most
  dangerous published example. Meertens 2007 caveat: coincidence not monotone
  in v(N). IR Example 4: classical=core while all MC variants ⊋ core — known
  divergence pattern matching our exact-games finding.

## 2026-07-24 evening 8 — key-hunter final additions (exact certs + selector)
- Catch #16 now EXACT-certified: n=6 exact games with d*(S)=2 (S={0,2,3,5},
  slack=7) and d*=1 (slack=7/3), both d*≤slack, singleton max-coverage certs
  verified in rationals (WITNESS_dstar_positive_n6.json; copied to paper3/).
- SELECTOR COMPUTABLE: in every star-fail some MAX-COVERAGE member of S
  certifies (~2300 cases, 99.93-100%); UNIQUE max-coverage member certifies
  100% (126/126). P(cert|max-cov)≈71-77% vs 8% baseline. Lone "miss" = the
  pair-case (no singleton exists at all) — consistent.
- FINAL THEOREM SHAPE: (STRAT-CERT) single-stratum C⊆S, |C|≤2, M^(C)≤phi(S);
  generic singleton = max-coverage member. Open inequality (the frontier):
  for k max-coverage, Σ_{i∈S∖k}(r_i−1)(x_i−phi_i) ≤ 0 for all core x with
  x_k=v({k}). Fragment updated with exact-witness pointer + the reduced
  inequality; witnesses copied into paper3/; PDF rebuilt. Safety net stays
  live (thmBAD=0, ~142k cumulative star-fails). LANE CLOSED (confirmed).

## 2026-07-24 evening 9 — wildcard lane CLOSED (terminal): four-route no-go map
- k*-TEST: 0/319 exact games satisfy v(N)≥k* (ES games: (10,24),(19,32),
  (18,25),(23,113/3)) — k*-route dead (sufficient-only, so conjecture
  untouched). LP implementation validated on additive (k*=v(N) exact).
- Maschler-1976/glove gate independently confirmed non-exact (2×3,3×2,2×4
  glove markets all non-exact: scarce-side singleton v=0 < core-min).
- COMPLETE PROOF-ROUTE NO-GO MAP on exact games (all with certificates):
  (1) MPS supermodular lattice — lever absent; (2) excess level-set
  balancedness — vacuous; (3) ê_x balancedness — false AND Mas-Colell-scoped;
  (4) v(N)≥k* — 0/319; (5, corollary of (T)-refutation) class-closedness
  under maximal excess games — fails (ê_x with empty core is not exact).
- VERDICT: "exact ⟹ classical DM BS = core" (+ kernel⊆core) = strongly
  supported, gate-survived, genuinely OPEN pair of conjectures; falsification
  filter = Mas-Colell∖core points (classical membership FALSE on all anchors).
  Bankables: ê_x + k* + BS oracles (src/bargaining_set.py etc.), certified
  Mas-Colell⊋core on exact games, no-go map. LANE CLOSED; CPU freed for stES.

## 2026-07-25 — STABLE ⟹ ES RESOLVED NEGATIVELY (pending final write-up): TWO CERTIFIED CANDIDATES
- reenum4 (provably-complete arrangement for segment cores: coalition + floor +
  endpoint-coordinate + 15 pairwise segment-support planes; gated by re-finding
  cand0's known escape) COMPLETED on cand1 AND cand2: 41.5M ordinals/candidate,
  ~20.8M non-singular vertices tested each, ~4.5M outside-core each, EVERY one
  exactly dominated (conservative-margin screen, skip only on exact-verified
  domination witness). SURVIVORS = 0, ESCAPES = 0, both games.
- ⟹ under the segment-core completeness theorem: U = core, cores are STABLE.
  Both games exact + non-ES ⟹ 'stable core ⟹ egalitarian stable' is FALSE at
  n=6; Dietzenbacher (GEB 2021) open question resolved negatively in BOTH
  halves (exact half = paper 2; stable half = here).
- MAIN-SESSION INDEPENDENT VERIFICATION PASSED (bwfuqtrtd): both games exact
  (62 exact LPs each, own pipeline), non-ES (own egalitarian implementation:
  claims (3/2,1/2,1,1/2,3/2,3/2) sum 13/2>6; (3/2,1,3/2,3/2,3/2,3/2) sum
  17/2>8), segment geometry (endpoints in core, 12 fully-tight coalitions,
  rank 5 ⟹ dim 1).
- REMAINING before claim: prove-stES's rigorous write-up of the completeness
  theorem (interior-t/pairwise-plane lemma), tolerance-gap statement for the
  float outside-core classification (coordinates are small-denominator
  rationals; float error ≪ 1e-7 tolerance — state the determinant bound),
  witness JSONs. Ordered; in progress.

## 2026-07-25 — PAPER 2 EXTENDED: "Exact and stable games need not be egalitarian stable" (v2)
- Max directive: extend paper 2 with the stable half; external audit to follow.
- KEY PRESENTATION FIND: cand1/cand2 are TWO-POINT GENERATOR games —
  v = min(A,B) verified (cand1: A=(1,1,0,1,3,0), B=(2,0,1,0,1,2), τ=6;
  cand2: (3,0,2,2,1,0)/(1,1,1,1,2,2), τ=8). Exactness free via the paper's
  Lemma 2.1; unifies both halves under one device.
- CITATION PINNED (Tinbergen open PDF, abstract verbatim): Estévez-Fernández
  2012 "equivalence between largeness of the core and stability of the core
  for games with at most 5 players" ⟹ stable(n≤5) ⟹ large ⟹ ES ⟹ our n=6
  witnesses are MINIMAL. Sharp thresholds: n=5 (exact), n=6 (stable).
- New §6 in sections_theory.tex: stable-set defs (vNM 1944 added to bib),
  Theorem 6.1 (both witnesses), Lemma 6.2 (segment domination sources),
  Lemma 6.3 (plane family), Prop 6.4 (finite stability certificate for
  segment cores — union-of-polytopes vertex argument), computer-assisted
  stability proof with both soundness guarantees (exact domination witnesses;
  lattice-gap: Hadamard det ≤7000 ⟹ nonzero constraint values ≥1.4e-4 ≫
  tolerance 1e-7 ≫ float error), Corollary 6.5 (full resolution), Remark 6.6
  (coupled failure). main.tex: new title, abstract, intro bullet, methods
  (enumeration + independent-toolchain dual verification), vNM bib entry.
- Supplement: stable_witness_1/2 blocks (game, generators, claims, Ahat,
  12 fully-tight, segment, stability_certificate stats+gates); verifier
  extended (generator check, claims/ES/Ahat recompute, fully-tight, exact
  rank-5 Gaussian elimination); 52 checks ALL PASS standalone from the zip.
  README updated. 11pp PDF compiles clean, no undefined refs.
- versions/v2/: paper2_main_v2.pdf, sources, zip, SHA256SUMS_v2.

## 2026-07-25 — prove-stES lane CLOSED (terminal summary complete)
- Post-crash resume delivered the final items: LATTICE-GAP LEMMA in notes
  (computed bound: lattice spacing ≥ 5.8e-3 ≫ 1e-7 tolerance ≫ ~1e-12 float
  error — tighter than the paper's conservative Hadamard ≤7000/1.4e-4, both
  valid), verification battery run, WITNESS_STABLE_NONES_cand{1,2}.json,
  §8 terminal summary with honest correction trail (retracted "U convex";
  pkill incident owned). Reusable assets: stES_reenum4.py (complete
  segment-core stability certifier), stES_validate_n5.py, stES_corevx2.py,
  stES_verify_witness.py. ALL FOUR BREAKTHROUGH LANES NOW CLOSED.

## 2026-08-02 — QUANTITATIVE CARRIER CONJECTURE RESOLVED SHARPLY AT n=7
- The complete exact theorem through `n=6` is dimension-sharp.  For
  `N={1,...,7}` and `S={1,2,3}`, the exact
  three-generator lower-envelope game `v(T)=min{0,a(T),b(T)}` with
  `a=(-3,1,3,-1,2,-1,-1)` and `b=(3,-2,0,-1,-1,-1,2)` has exact leximin
  point `phi=a/4` and `(gamma_S(phi),eta_S(phi))=(3/4,0)`.  At the reference
  point zero the pair is `(1,0)`.
- All six carrier differences are exactly one.  The four zero-valued
  coalitions `13456,457,3467,567` satisfy the degree-three identity
  `1_S + sum 1_Q + e_1 + 2e_2 = 3 1_N`, forcing every core point
  nonnegative on `S` to have `S`-sum zero.
- The solver-free integer verifier checks all 128 lower-envelope/core
  identities, exactness, carrier differences, eta degrees, zero dual cost,
  and rank-seven minimal balanced support.  An independently formulated
  primal LP also returns eta zero.  A second exact-rational verifier computes
  the leximin point and all six `3/4` differences.  The paper fragment and PDF
  now state the sharp positive-through-six/negative-at-seven theorem.
- The leximin point now has a hand-checkable three-stage Maschler certificate:
  gain strata `{3,4,6,7}` at `3/4`, `{5}` at `3/2`, and `{1,2}` at `9/4`.
  Appending null players preserves the exact core, leximin coordinates,
  carrier differences, and eta obstruction.  Hence the inequality holds
  universally exactly for `n<=6` and fails for every `n>=7`.
- STRUCTURE: eight zero-valued coalitions form a degree-four balanced
  rank-five face and force `Core(v)=conv{0,a,b}`.  Coalitions `1`, `2`, and
  `123` uniquely require `a`, `b`, and zero, so three lower-envelope
  generators are minimal.  The two-parameter family
  `min{0,a,kappa*a+theta*b}`, with `kappa>=0`,
  `theta-2*kappa>1/4`, and `kappa+theta<=1`, keeps `phi=a/4` and has
  `(gamma,eta)=(theta-2*kappa-1/4,0)`.  Its relatively open parameter wedge
  proves nonuniqueness and genuine two-parameter perturbation robustness.
  The known target size three and total player count seven are globally
  minimal.  The minimum outside-set size at `n=7` is now exactly three, even
  at the leximin reference.  The exact lower-envelope game `min{0,A,B}`, with
  `A=(-4,1,2,2,-1,1,-1)` and
  `B=(2,-1,0,0,1,-1,-1)`, has `S=1234`, `P=567`, and
  exact leximin point `phi=A/3`.  All fourteen leximin carrier differences
  equal `2/3`, while eta is zero.  The degree-four rank-seven identity
  `1_S+e1+3e2+2*1_56+1_357+1_457+2*1_13467=4*1_N` is the hand eta
  certificate.  A three-stage Maschler proof has gain strata `{3,4,5,7}` at
  `2/3`, `{2,6}` at `4/3`, and `{1}` at `8/3`.
  This second obstruction is also robust: throughout
  `kappa>=0`, `theta-3*kappa>1/3`, `kappa+theta<=1`, the game
  `min{0,A,kappa*A+theta*B}` keeps `phi=A/3` and has
  `(gamma,eta)=(theta-3*kappa-1/3,0)`.  Thus the outside-triple finding is an
  open two-parameter wedge, not a single enumerated example.
  The wedge is nevertheless intrinsically unbumpable.  The zero-valued-face
  identity `1_N+1_35=1_1234+1_56+1_357` forces `x(1234)=0` on `F_35`, so
  `d*(1234)=0` throughout the family.  A broader floating capacity screen of
  all 34 residual `4+3` canonical games finds no binding-capable target; all
  three leximin carrier violations have zero exact bump capacity.
- MONOTONICITY-BRIDGE BREAKTHROUGH: a nearby exact three-generator game
  crosses that boundary while remaining exactly solvable.  For
  `A=(-215,53,104,103,-56,51,-40)` and
  `B=(108,-55,-4,-1,50,-60,-38)`, the game `min{0,A,B}` at `S=1234` has
  integer leximin point `(-75,17,32,35,-20,15,-4)`,
  `(gamma,eta)=(36,35)`, selection slack `sigma=9`, and exact bump capacity
  `d*=10`.  Thus the quantitative carrier inequality fails in a genuinely
  binding-bumpable exact game.  Yet the complete admissible path is
  `phi_tau=phi` through `tau=9` and
  `phi_tau=phi+(tau-9)(e1-e6)` on `[9,10]`: player 1 gains, the other target
  players remain fixed, and proper-coalition monotonicity survives.  The
  endpoint game is the lower envelope of four displayed integer allocations,
  and the four-stage Maschler, eta, capacity, endpoint-exactness, and path
  certificates replay without an optimizer.  This proves the carrier bound is
  not necessary for monotonicity and sharply localizes what a true
  counterexample must do.
- ★ PROPER-COALITION MONOTONICITY REFUTED ON EXACT GAMES: a direct
  exact-pair construction found a five-player counterexample with zero
  singleton floors.  The base game is the lower envelope of
  `A=(2,0,12,6,0)`, `B=(0,0,0,0,20)`, and `P=(0,2,10,4,4)`; the endpoint
  removes `P`.  Both games are exact, have common total `20`, and differ only
  at `S=1345`, whose worth rises `18 -> 20`.  Nevertheless
  `phi_base=(1,1,13/2,5,13/2)` and `phi_end=(2,0,6,6,6)`, so target players
  3 and 5 each lose `1/2`.  The full path is constant through `tau=19` and
  equals `(tau-18,20-tau,16-tau/2,tau-14,16-tau/2)` on `[19,20]`.
  A four-stage hand certificate proves the formula, and the star condition
  holds at every binding interior point.  Thus the former E' implication is
  false even along an exact path: the existence of an all-target-improving
  direction does not force leximin to select it.  An independent direct-pair
  screen found no drop in 476 binding four-player pairs; the later exact
  suffix-tightness theorem now proves minimum dimension five.
- MONOTONICITY CONNECTION: the failure target `S=123` has exact bump capacity
  zero throughout the family.  Coalition `135` is uniquely tight at zero, so
  its face blocks every positive exact bump of `123`.  Thus this carrier
  failure does not itself refute proper-coalition monotonicity; a future
  counterexample must be binding-bumpable.
  This is now certificate-intrinsic: the exact incidence identity
  `1_135-2*1_123=1_13456+1_457+1_567-2*1_N` gives
  `x(135)>=2*x(123)` throughout the core.  Hence every deformation preserving
  those zero faces remains unbumpable; merely adding generators to the
  triangular core cannot convert this obstruction.
- PRIOR-ART AUDIT: general minimal-balanced enumeration through n=7 is not
  new (Laplace Mermoud--Grabisch--Sudhölter, arXiv:2507.05898), and the exact
  cone already has a facet theory via minimal semi-balanced systems
  (Studený--Kratochvíl, MMOR 2022).  No matching prior statement was located
  for the eta/carrier inequality, its sharp 6/7 threshold, or the triangular
  family.  Novelty language remains “we are not aware” pending MathSciNet/
  zbMATH and expert review; see paper3/PRIOR_ART_CARRIER.md.
- LMIN NAMING CORRECTION: the leximin-above-floors selector is exactly
  `m+Lmin(v^0)` after canonical singleton normalization.  Arin--Iñarra (2001)
  introduced ordinary Lmin; Dietzenbacher (2021) already gives broader-domain
  aggregate-monotonicity failures for Lmin.  The n=5 witness has zero floors,
  so it is directly a proper-coalition monotonicity counterexample for Lmin on
  exact games.  Novelty is the exact-game/proper-coalition theorem and compact
  certificate, not the selector itself.
- ★ N=5 LMIN FAILURE IS DIMENSION-MINIMAL (NEW STRUCTURAL THEOREM): a human
  protector-coalition proof shows that every richer-player suffix at a strict
  Lmin payoff gap is tight in every singleton-normalized exact game through
  four players.  The dual of a completed Lmin coordinate stage forces a tight
  coalition containing each richer player and omitting the pinned player.
  Exact singleton witnesses then exclude a unique richest player, force a
  singleton poorest complement, and close the sole remaining `2|2` geometry.
  The previous exact KKT and primal-tangent encodings remain independent
  audits rather than the theorem proof.
  Hence Lmin Lorenz-dominates the core and equals Lmax/PES through n=4.
  Biswas et al. (1999) plus Dietzenbacher (2021) then give coalitional
  monotonicity through four players, while the exact five-player witness above
  is sharp.  Negative controls become satisfiable after deleting either
  exactness or individual pins.  The finite theorem received a favorable
  hostile review; the new human proof still requires separate external review.
  See `paper3/N4_LMIN_LMAX_HUMAN_PROOF.md` and
  `paper3/N4_LMIN_MINIMALITY_PROGRAM.md`.
- N=4 MINIMALITY SCREEN (NOW INDEPENDENT SUPPORT): after singleton normalization,
  normalized Lmin agreed exactly with PES/Lmax on 100 random exact
  four-player games.  This suggests a sharp literature bridge: Biswas et al.
  (1999) prove exact games have large cores through four players, and
  Dietzenbacher (2021) proves PES=Lmax is coalitionally monotone on the
  resulting egalitarian-stable domain.  The missing step is to prove
  `Lmin=PES` for singleton-normalized exact games at n<=4; largeness alone
  must not be cited as supplying that equality.  Targeted direct-pair screens
  found zero drops among 545 binding two-generator endpoints and 1,948
  binding endpoints with two through six generators.  Every observed target
  sign pattern was either `+++` or had exactly one `+` and two zeros.  A
  prospective hand proof is now localized: any four-player drop appears to
  force two old-Lmin tight coalitions `ac` and `bc`; exact attainment of the
  singleton face `c=0` would violate efficiency when `phi_c>phi_p`.  See
  `paper3/N4_LMIN_MINIMALITY_PROGRAM.md` and
  `src/audit_n4_exact_lmin_minimality.py`.
- THRESHOLD BREAKTHROUGH: the complete n=6 theorem no longer logically needs
  any coalition-support census.  Any violation supplies an eta-dual floor
  separator with at least three coordinate levels.  After quotienting by
  `S` and its positive singleton columns, balance becomes two independent
  equal-subset-sum relations among at most three positive weights.  Every
  such relation is either `z_i=z_j` or `z_i+z_j=z_k`.  This gives no
  three-level pattern for `3+3` and exactly one for `4+2`, namely
  `1_S+e1+2e2+1_35+1_136+2*1_456=3*1_N`.  Its objective is at least
  `2*gamma` from the single `C={4}` carrier inequality.  A tiny reduced-matrix
  verifier checks the subset-sum classification; both the 65,133-support scan
  and the 1,489-orbit exact-cone audit are now independent redundancy.
- SEVEN-PLAYER OUTSIDE CLASSIFICATION: a focused determinant census checks
  `9,086,132` supports for `4+3` and `8,798,030` for `5+2`.  After the
  two-level separator theorem and direct carrier-mass bounds, only 34 and 5
  symmetry orbits remain.  Exact global-witness cone values are
  `{0:14,1:12,2:8}` for `4+3` and `{3:5}` for `5+2`; every rational lower
  bound replays without optimization.  Hence outside pairs are impossible at
  `n=7`, while the explicit outside-triple game is sharp at both zero and
  leximin references.  The earlier
  alternating screen missed the `4+3` obstruction and is retained only as a
  documented false-negative diagnostic.

## 2026-08-06 — multi-agent campaign: selection, monotonicity, divergence

Seven-agent parallel campaign (three research routes, then rolling waves;
two hostile-audit agents added afterwards), all headline claims re-verified
on a coordinating thread before use.  Twelve commits through `a6a7850`,
plus audit amendments after; `paper4/threshold.tex` grew from 12 to 22
pages, `paper5/divergence.tex` (19 pages) is new.

### Proved this campaign (in the papers)
- Selection Section (paper4 §8): positive-load, crossing-budget (pairwise and
  k-fold sunflower), and zeroing lemmas; star normal form; every star St(H,Q)
  is a facet (binom(n-1,2) types); five-player selection theorem — a system
  (P) is a facet iff its packet is full-trace, realized types = rows
  16,14,11,13,10; poorer-side threshold at h=2 (split facets first at m=5, by
  finite shape check); h=3 collection theorem (only {H} and the 2-cover carry
  facets).
- Monotonicity Section (paper4 §9): reduction lemma, loss-bounded-by-slack,
  exactness pushback with prefilter g(S) > s_phi(S), shields proposition;
  two six-player examples retiring "losers = slack suffix" and "losers = one
  stratum"; containment conjecture W ⊆ H* ⊆ S (1041/1041, two sampling
  regions).
  → RESOLVED 2026-08-08 (task #12, verifiers/cc/): C-C LEFT is FALSE — a
  five-player MULTI-SLACK counterexample (both richer suffixes slack, the
  middle stratum pays; lead-verified independently; the campaign's fourth
  sampling artifact: all 1041 records were single-slack, where innermost =
  outermost).  REPAIRED as C-C^: W ⊆ Ĥ ⊆ S with Ĥ the OUTERMOST slack
  suffix — PROVED at n=5 by an exact decision procedure (32/32 UNSAT each
  half; Lemma-L leximin certificates, iff, cross-validated against task
  #23's Theorem B 30/30+6/6; faithfulness: the same lab's SAT model on
  C-C-left realized as the counterexample), conjectured for n≥6.  New
  proved lemmas: exact-bump window (closed interval, alpha_ex ≤ g(S)),
  null-players-forbid-exact-bumps, Lemma C+ (phi'-tight T ≠ S weakly
  loses, supersets of S included), master inequalities (MA)/(MB).  BT
  closed forms delivered: 137 members, 93 regions, piecewise linear,
  93/93 verified.  Paper4 monotonicity section rewritten accordingly
  (third retiring example, five-player containment theorem, repaired
  conjecture, window proposition).
- Divergence paper (paper5): two-generator core duality (general form);
  master family G(p,k) with closed forms and membership for all parameters;
  deficit identity 2−ρ = 2n/(k(p+1)); sup_n s(n) = 2, s(n) ≥ 2−8/n; overlap
  identity; n=5 maximum 1/2 (2-generator, hand proof); M-side asymmetry with
  smallest counterexample; majorization non-monotonicity; covering
  obstruction; ONE-COALITION CERTIFICATE THEOREM at n=5 (mu=lambda, M=nu),
  proved by finite exact check against the 280 permuted facet inequalities —
  the facet catalogue used as a proof engine.

### Retired this campaign (each replaced by something sharper)
ratio bounds (n−4)/(n−2), (n−4)/(n−3), fit (n−2)/6; lemma gap ≤ 4(n−4)·mu;
h=2 full-trace conjecture (twice recalibrated → m-indexed + facet form);
"no split packets at n=5" (sampling artifact, twice); losers=H (C-A),
losers=one-stratum (C-B), SC1, frozen-above; smoothing/majorization route;
localization of exactness; "|B|=4 is special".

### Open ledger (sharpest known obstruction each)
- s(5) = 1/2 in full: the CFG case is CLOSED ((*) proved by finite check,
  10,974 exact LPs, minimal hypotheses = both solution vectors in core +
  poor-stratum pinning); remaining are the (1,2,2)/(1,1,3) Lmax shapes and
  the (4,1) boundary.
- C-C containment proof (task #12); exact-partition impossibility
  (conjectured; 10,239-bump zero-failure search; rigidity proposition
  proved).
- ZP residue RESOLVED to one conjecture (2026-08-07): the j≠e branch and
  profile (4,0) are PROVED impossible by a well-founded null-player descent
  (verifiers/zp/PROOF.txt: k-fold RO forces the kernel player to zero; a
  common zero player is null; deletion descends; the phase theorem floors
  the descent).  Profile (2,2) is equivalent to the open half of:
  CONJECTURE PART(p,q) realizable iff p,q >= 1 and max(p,q) >= 3
  (descent-correspondence evidence across 380k games; the m=5 ZP profiles
  are exactly the m=4 PART splits).  Decisive-LP route blocked exactly by
  the multi-stage leximin encoding, recorded for continuation.
  → CLOSED 2026-08-08 (task #23, verifiers/part/): the conjecture is FALSE.
  PART(p,q) realizable ⟺ p,q ≥ 1 and p+q ≥ 4, BOTH halves proved; PART(2,2)
  and the n=7 ZP(2,2) are REALIZED by explicit audited witnesses
  (lead-verified independently).  The two decisive-LP blockers were removed
  exactly: exactness is existential/linear (one attaining core point per
  coalition — no catalogue at any n) and leximin is a quantifier-free Farkas
  certificate (complementary slackness kills the bilinear terms, leaving a
  support disjunction).  New by-products: block rigidity (PART's S1,S2 tight
  on the whole core), protector lemma, rich-pair merge is exact (M1–M3) but
  does NOT transport Lmin (T1/T2 refuted — recorded so it is not retried);
  padding lemma.  The "PART(2,2) never" evidence was a sampling artefact
  (hit rate ~1/16k), the campaign's third.
  → Theorem D UPGRADED 2026-08-08 (task #24, verifiers/part/PROOF_M3.txt):
  "no PART at m=3" is now a HAND theorem — block rigidity collapses the
  core to 3 variables where the b/c-separating facet normals cannot exist;
  three universally-improving directions force blocking disjunctions; the
  exactness-at-{f} direction contradicts all four combinations, two lines
  each.  No stratification case tree; the 48-UNSAT and CEGAR runs are now
  cross-checks.  The threshold mechanism is identified: Lemma 3's crossing
  budget needs |Q\T| <= 1 and expires exactly at m=4.  [CORRECTED
  2026-08-08 by r23 itself: the initially-claimed "equality at the frontier
  / razor-thin" reading was an overreach from one witness — 74 audited
  PART(1,3) configurations have the budget STRICT (gaps up to 47/48), and
  a control shows strictness removes no solutions.  The true sharpness
  statement is Theorem G4's dichotomy: a tight T over H omitting P is
  IMPOSSIBLE at q<=2 (hand proof, G1 Step 2) and MANDATORY at q=3 (finite
  check, 60/60 UNSAT with SAT control) — the forbidden object flips from
  unavailable to unavoidable, nothing degrades gradually.]
  Reusable frame for all m: a PART core is a polytope in |L| variables
  whose facet normals cannot separate same-block players.
- s(5) = 1/2 PROVED IN FULL, UNCONDITIONALLY (2026-08-08, task #22,
  verifiers/s5close/, paper5 thm:s5): 2961-configuration split, TWO
  pipelines sharing no machinery — (1) anchor lemmas L1'-L2 + game-free
  triage + single/multi-stage pinning ladders (the ceiling second stage
  BUILT per the archived sketch); (2) existential exactness (Theorem A) +
  staged Farkas certificates for both selections (Theorem B + re-derived
  leximax mirror), needing neither A3 nor the facet catalogue — so the
  theorem is unconditional.  Perfect pipeline agreement, machine-audited
  coverage, the certificate-not-realizable phenomenon hit its 4th and
  largest instance (108 single-stage models, all genuine games in the
  wrong configuration).  Also: (4,1) regime <= 1/3 attained (thm:regime41);
  starved player always Lmin-poor (cor:poorstarved, 2-line hand proof,
  closes S5PROOF E3 and kills the jrich branch); L1' (Lmax top stratum
  >= 2); 2M + 3mu <= T.  Lead verified independently: 400-game own-code
  falsification sweep 0 violations, coverage/agreement re-run, proof-file
  line audit.  Paper5 updated (new sec:s5full, abstract, scope now 4 open
  problems).  Residues: hand proof of A3 (mechanism only), hand
  distillation of the 649 solver-closed configurations, s(6).
- Round 2 on C-C^ and PART (2026-08-08 evening, tasks #25/#26):
  (a) C-C-left ALSO fails at n=6 — two audited multi-slack games (one with
  tight/slack suffixes INTERLEAVING; lead re-verified Case A end-to-end);
  C-C^ survives ~2,800 designed n=6 danger-class violations (0 failures
  either half, left-of-C-C failing ~28% on the same corpus).  New L-out
  lemma (paper4 cor:lout): EVERY outsider sub-coalition carries slack >= rho
  — absorbs push(ii)/(iii).  Hand-proof of cchat de-prioritized on evidence:
  72-assertion irredundant unsat core even after the two-strata reduction,
  and exactness of v' at non-supersets of S provably irreplaceable (L-out
  alone flips UNSAT->SAT).  Data-loss law: d14_n6multi.py hardcodes its
  output name — rename per seed or earlier runs are destroyed.
  (a2) EXACT-PARTITION IMPOSSIBILITY PROVED AT n=5 (task #28,
  verifiers/cc/ d23-d26, paper4 thm:expart + cor:allfail): same decision
  lab, 31 patterns UNSAT, non-vacuous (7/15 patterns admit exact bumps —
  they just never produce a loser; the 8 dead control patterns are exactly
  EP2's exclusion).  Free hand lemmas: EP1 (suffix-tight core point IS the
  leximin — certificate 1_{H_j}) and EP2 (no singleton top stratum at
  exact partition).  Consequence: at n=5, EVERY failure has a slack
  suffix, Ĥ always exists, W ⊆ Ĥ ⊆ S always, four/five threshold applies
  to all failures.  paper4's old "two hundred expected" null retracted as
  unsound (structurally different population).  No short hand proof: 302
  irredundant assertions (vs 72 for two-strata C-C) — recorded, not
  chased.  n>=6 open; family generator for window-bearing exact-partition
  bases archived (method, not yet weight).  Final d18 corpus: 6,246
  certified n=6 danger-class violations, 1,815 C-C-left failures, 0 C-C^.
  ROUND-2 SHARPENINGS (d27): THE INVERSION — at exact partition the
  "dangerous shape" (losers slack-but-not-a-suffix) occurs in EVERY
  certified exact bump (200/200 n=5, 80/80 + 2,224 total n=6), always
  with losers strictly OUTSIDE S, ~75% with intra-stratum redistribution
  (S financed by its own stratum-mates outside it); the conjecture is
  about loser LOCATION, not occurrence — now printed in paper4.  Lead's
  route-3 briefing was BACKWARDS and is retracted: at exact partition the
  guaranteed suffix certificate makes (MA) trivially = Prop D; a decisive
  ablation (system minus cert2 is SAT) shows the entire proving force is
  on the phi'-side certificate (223 of 302 irredundant assertions).
  (b) PART characterization unified (verifiers/part/PROOF_GENERAL.txt): ONE
  inequality (KEY: tight T over H omitting P forces |Q\T| >= 2) drives both
  halves.  Lemmas N*/I*/E*/X* generalize the m=3 frame to all (p,q);
  Theorem G1 (p=1 => q>=3) subsumes PROOF_M3; recipes A (p,q>=2) and B'
  (p=1,q>=3) construct witnesses (5 audited realizations; recipe A uniform:
  L at 1/4, H at 1/2).  Threshold explained: a PART configuration must buy
  a tight coalition over H omitting one block's poorer side, priced by KEY
  at two spare players in the other block.  Residue: closed-form recipe
  family for all (p,q) by progressive leximin.
  → CLOSED (task #29, verifiers/part/PROOF_FAMILY.txt): explicit envelope
  FAMILIES for every (p,q) — Family A (p,q>=2; m+2 rows; Lmin = 1 on L, 2
  on H, slack constant 4) and 4-row Family B (p=1, q>=3; Lmin = 1 on L,
  q-1 on H, slack q-2) + mirror; proved by a 4-line PINNING LEMMA
  (uniqueness above 1_N + block rigidity pins both stages) with no solver
  in the proof; (KEY)'s two readings visible as row-arithmetic caps.
  Machine-validated 18 instances n<=9, 97 checks 0 failures; lead verified
  3 instances independently.  Padding lemma retires from load-bearing
  duty; Theorem G7 = closed-form sufficiency.  PART program: nothing
  outstanding.  Method law (r23): do NOT reverse-engineer envelope rows
  from SAT-model v-vectors (needs vertex enumeration) — design rows
  BACKWARDS from the intended leximin proof (pick phi, pick the pins,
  solve the row arithmetic); that is why Family B is 4 rows independent
  of q and why the (KEY) budgets surface as row constraints.
- paper6 DRAFTED (task #30, coopgames/paper6/partition.tex, 12pp clean):
  the ZP/PART program as a standalone note, "boundary partition" naming
  for print, both directions closed-form, methods section = existential
  exactness + Farkas certificates with full proofs, status table with ONE
  machine dependency (G4).  En route r23 caught + corrected an overclaim
  in Lemma I*'s statement (the claimed converse of the indicator form is
  FALSE — blocking indicators doesn't block cross-block mixtures; nothing
  load-bearing used it; dated correction in PROOF_GENERAL.txt).  Lead
  review: pruned the bibliography to cited+verified entries (the from-
  memory Llerena-Mauri entry was invented — deleted), prior-art
  positioning pass PENDING and marked in the tex.  NOT submission-ready:
  needs the positioning pass + a hostile audit round.
- s(5) DISTILLATION, increment 1+2 (task #27, verifiers/s5close/
  PROOF27/REPORT27): seven new hand lemmas, ALL A3-FREE, one idea (an
  improving core direction must leave the polytope) — L7/L7' extremal
  rigidity (every core point has max_{D1} >= M, min_P <= mu), L1''
  (|D1| >= 2 with no A3: exactness at {i} + L7 forces v({i}) >= M > 0),
  L5, L6 (singleton bottom stratum forces f({i}) = mu), protector level
  forms L11/L12 (first lemmas coupling the two allocations).  L2/L2'
  (starved-player) now A3-free.  Solver residue 208 -> 132 (2,829/2,961
  hand-excluded); the A3-free net (204) BEATS the A3 baseline (208); T1's
  17 solver cases -> 9.  Tight-family lemmas L14-L17 proved but buy ZERO
  configurations (negative result recorded; complement-closure FALSE
  4,433/15,335).  RESIDUE NAMED: 27 possible configurations = the
  mu-lower-bound problem (= hand-A3, Part D's deepest gap; includes CFG's
  mu >= 1/8) + 105 impossible-but-not-yet-hand-excluded (87 with >= 3
  Lmin strata; barrier = no second canonical core point in the stage-1
  face — L13 proved but vacuous without one).  Controls: whole-core LP
  validation of L7/L7' + all lemmas 0 failures over 2,668 games.  Paper
  integration deferred until audit #31 lands (fixed diff range).
  INCREMENT 3 (decisive negatives + splice audit): seven candidate
  middle-stratum lemmas DEAD with recorded counterexamples — notably C7:
  Lmin does NOT Lorenz-dominate Lmax on exact games in general (1,102
  failures), killing a whole argument family and showing Lemma 0's
  exact-partition hypothesis does real work.  Theorem-A attaining points
  buy nothing level-only.  HARD BARRIER PROVED: the full hand net is
  consistent on all 105 impossible survivors with the failure hypothesis
  removed — level-only reasoning with this vocabulary CANNOT exclude
  them; the five T1 stragglers are SAT under anchors+protectors and need
  the full ladders.  Residue 132 = 27 + 105 is sharp for this lemma
  class.  r22's audit of the lead's four s5close restatements in paper5:
  sound, 3 LOW fixes applied (111 not 64 at ratio 1/3 — source error in
  r22's own REPORT.txt sec.4; 5,250 mirror certificates; control counts
  attributed per pipeline).
  #27 CLOSED: final fold archived; C7 witness (T=4 integral game,
  Lorenz violation at k=4, ratio exactly 1/3) independently verified by
  the lead; twelve A3-free lemmas; residue 132 = 27 (hand-A3 core, future
  task) + 105 (proved beyond level-only reasoning); the barrier = no
  second canonical core point in the stage-1 face.
- AUDIT #31 ROUND 2 (REPORT_AUDIT2.txt in verifiers/cc/): all seven
  round-1 fixes verified (S7 checked for circularity — clean); paper6
  CLEAN including both external references verified against the
  literature per the invented-bibitem law, and the Lemma-I* correction
  faithfully carried (no leak).  Four new findings, all fixed: R1 the
  multi-slack figures now use both sweeps (~10,000 bases, 30 violations
  — strengthening the argument); R2 the inversion's four properties
  re-attributed to the measured corpus (200+80), the larger sweeps
  separated; R3 the unarchived 2,224 removed from print (interim
  snapshot only — a printed count with no artifact is what
  reproducibility notes exist to prevent; r12's own runs, never
  finished); R4 paper6's 74 are stratification-j PAIRS, not
  configurations — attribution corrected by r23 itself: the slip was in
  its draft prose (PROOF_GENERAL.txt had it right; the distinction was
  flattened at restatement and nothing consumed it — the
  audit-the-unused-half failure mode, live within hours of adopting the
  law).  Checklist phantom resolved: "97 family checks" = the
  97 OK lines of families_closed.log, real but never printed.
- NEW WAVE (Aug 8 late, tasks #32-#34): HAND-A3 CORE CRACKED, TARGET 1
  (task #33, verifiers/cfg_hand/): paper5 thm:cfg (f({j}) >= T/8 in CFG)
  is a HAND THEOREM — one page replacing 10,974 programs.  Four steps:
  KEY LEMMA (an f-tight cap never meets {p1,p2} more than R — from core
  membership of BOTH selections; six violating complement shapes, only
  U={p_i}∪R uses mu<1/8, so the constant FALLS OUT and is sharp: at
  mu=T/8 the lemma fails at S={j,p_other}, realized in thm:n5's extremal
  game); dualized pinning (loads B >= 1+A on P, A on R); the pivot
  2(rho-mu) = 1-5mu = c EXACTLY forces the certificate optimal and every
  support set f-tight; weighted count 2+2A <= 2A.  Uses only A2 (easy
  direction), cor:poorstarved, core membership, the pinning — NOT A3's
  hard direction, NOT the catalogue.  Lead line-audited every step +
  re-derived the six kills + ran the guards.  Paper5 thm:cfg proof
  replaced (now 24pp); finite check demoted to archived confirmation.
  Method notes for the other 26: cap-shape lemma + load count, nothing
  CFG-specific but the numbers.  Targets 2-3 (mu=lambda by hand; the
  other 26) not attempted.
- s(6) PROGRAM, PHASE-1 RECON (task #32, verifiers/s6/): universe 37,277
  configurations at n=6; the A3-FREE hand net (levels + L1'' + L7/L7' +
  L11/L12 — anchors and L3 dropped, they route through A3 which is false
  M-side at n>=6) leaves 3,350 survivors at target 2/3 = 91% hand-
  excluded (vs 93% at n=5), soundness clean (kills none of the 74
  populated configurations).  Fresh harvest (2,400 draws, 374 positive-
  ratio): MAX RATIO EXACTLY 2/3, attained in two configurations
  (Lmin(5,1)xLmax(2,4) and (4,2)x(2,4)) — no extremality refutation,
  consistent with s(6)=2/3.  Cost gate: pipeline-2 per-configuration
  median seconds but heavy tail, unknown rate 0-25% UNMEASURED — the
  crux.  A tightness-hoisting optimization proposed, tested, WITHDRAWN
  (logically equivalent, strictly worse: eager tightness decisions; do
  not adopt), with a self-caught like-for-like comparison error en
  route.  Plan: Stage B (74 populated configs + n=6 controls) + Stage C
  gate (60-sample unknown-rate measurement at 600s) then full run or
  honest PARTIAL ("<= 2/3 except a named list").
- HAND-A3 TARGET 2 PARTIAL (task #33 cont., verifiers/cfg_hand/
  REPORT_A3.txt + covers.py/json): mu = lambda at n=5 REDUCED exactly to
  "no fractional-cover vertex undercuts g(N)" (the Part-D obstruction,
  now pinned).  Lemma B (balanced covers free — paper5 prop:balanced
  recovered, dimension-free) + NEW Lemma E1 (single-excess-player
  covers free via exactness at the complement, dimension-free) kill
  2,076 of the 2,286 proper-cover vertices; 210 SURVIVORS, all with
  support 2-3 and |E| in {2,3} — hand-sized, not yet hand-proved.
  BLOCKER NAMED: self-similarity — the needed mu_E >= lambda is the
  same question restricted to E; doesn't terminate alone.  FIVE-NESS
  LEAD (flagged as lead, not result): survivors' sub-problems live on
  <= 3 players where the n<=4 rigidity R4 is available — if the R4
  route closes, that localization IS the "why five" answer, since both
  killing lemmas are dimension-free and only the surviving family's
  support size depends on n.  Bonus: independent reproduction of the
  archived 2287 cover-vertex count (2286 proper-only + the trivial
  beta_N cover; conventions reconciled, no discrepancy).
- HAND-A3 TARGET 2, ROUND 2 (task #33 cont.): mu = lambda at n=5 is now
  EQUIVALENT TO ONE INEQUALITY — (R): max over the core of 2y_p + y_q
  >= 3*lambda, for every ordered pair (equivalence verified by the
  lead: mu=lambda supplies a uniform-lambda core point, giving (R)
  trivially; (R) frees the last vertices).  New dimension-free Lemmas C
  (equal excess: y(E) >= lambda|E| via f(E)) and D (the dual can only
  beat 3*lambda through eta < 0 — the located failure boundary) join
  B/E1; the 2,286 cover vertices reduce 1291+785+150 to 60 SURVIVORS =
  ONE SHAPE up to relabelling (S1={p,x}, S2={p,q,y}, S3={p,q,z}; loads
  3,2,1,1,1).  (R) is SHARP: margin zero somewhere on 250 random exact
  games — no crude bound disposes of it.  "Why five" in print-ready
  form: prove (R) at n=5, or show its eta<0 branch empty at n=5 and
  nonempty at n=6.  Config-free — if (R) falls, ALL 26 residue
  configurations of the s(5) distillation become corollaries (target 3
  retired as a separate frame).
- s(6) GATE CONTAMINATION CAUGHT + THE n=6 EXTREMAL CLASS (task #32):
  running the gate and Stage B concurrently on a shared 14-core box
  oversubscribed CPU; z3 timeouts are WALL-CLOCK, so 11/26 gate configs
  "unknowned" at exactly 600.0-600.1s (every real solve 8.5-268.3s —
  the tell).  Face value = 42% unknown = the wrong branch of the
  pre-agreed rule; r22 did NOT trip it, quarantined the data under
  contaminated/, let Stage B run alone (39/74 UNSAT, clean), gate to
  re-run in isolation; Stage C stays pre-authorized on the CLEAN number
  only.  NEW LAWS: total solver processes <= cores, hard; any 'unknown'
  at the cap to within 0.1s is presumed a scheduling artifact until
  re-run in isolation.  (Lead's "run concurrently" instruction
  contributed; "concurrent scheduling, not simultaneous saturation.")
  PROFILING (PROFILE6.txt): the n=6 extremal class at 2/3 is TWO
  classes, both Lmax shape (2,4): Class A Lmin(5,1), Lmax=(1/18 x2,
  2/9 x4), NOT starved; Class B Lmin(4,2), Lmax=(0,0,1/4 x4), STARVED
  — the CFG family continued (zeros 1->2, poor stratum 3->4, M=T/4,
  ratio 1/2->2/3).  "Extremal => starved Lmax" FAILS at n=6; the (2,4)
  Lmax shape is where an n=6 hand bound should start.
- DISJOINT-SUPPORT RIGIDITY REFUTED + CORRECTED (task #35,
  verifiers/extremality/REPORT5.txt): the region-D "rho = 0 at n=6"
  was r12's OWN generator artifact (round-robin block assignment emits
  only (2,2,2)/(2,2,1,1) at n=6 — both genuinely rigid — while the
  breaking profile (3,2,1) was unreachable; 5th sampling-artifact
  instance, self-caught, this one in a DESIGNED corpus).  Refutation
  witness lead-verified (envelope (1,4,1|1,5|6), Lmin != Lmax, rho =
  1/3).  CORRECTED, dimension-free: Lmin = Lmax for disjoint-support
  envelopes iff every block <= 2 OR at most one block >= 2 (fails iff
  some block >= 3 AND another >= 2); 11/11 hand-picked profiles, both
  failure modes of the condition exercised ((4,1,1) rigid, (2,2,2)
  rigid); sweep CLOSED EXHAUSTIVELY: relabelling equivariance means the
  block-size PROFILE is the right unit (the ~1,020-set-partition sweep
  was computing 39 numbers fifty times over — killed, replaced by
  d32_profiles.py), and all 39 profiles with k >= 3 parts at n = 5-8
  agree with the condition, zero mismatches; the 13 breaking profiles
  all have (>=3)+(>=2) blocks, every rigid one fails a clause, and the
  discriminating cases (6,1,1)/(2,2,2,2) are covered at every n.
  STILL UNPROVED both directions — exhaustive-over-profiles at small n
  is evidence and the campaign's law says what that is worth; but the
  theorem, if it exists, is about two size clauses and not about n.
  Hand-proof target pinned: cover (6,1,1) and (2,2,2,2), fail on
  (3,2,1).  NEW LAW (generalized): a zero-failure
  region is worth exactly the SHAPES its generator can emit —
  enumerate emittable shapes BEFORE reporting the zero.
- THE CFG-FAMILY CROSSOVER (task #32 side-result, verifiers/s6/
  PROFILE6.txt): the starved family (4 players at T/4, poor stratum
  n-2 absorbing the zeros) has mu = 1/(4(n-3)) and ratio EXACTLY
  (n-4)/(n-3) — derived structurally, lead-verified telescoping, both
  observed members reproduced.  Against s_2(n): EXCEEDS at n=5 (1/2 >
  1/3, why s(5) beats the G-family), TIES at n=6 (2/3 = 2/3, why the
  extremal class is TWO classes — the handover), undershoots from n=7
  (3/4 < 5/6), saturates at 1 vs 2.  "Why the G-family wins from n=6"
  answered: the CFG family stops winning there.  n=7 prediction 3/4
  untested — first construction attempt FAILED for a construction-
  internal reason (the two-generator envelope of the target pair zeroes
  only z's zero-set, so v({i}) != 0 for four players; a valid instance
  needs a zero-cover generator set that doesn't disturb the pins — the
  design-backwards problem).  Explicitly NOT family-nonexistence
  evidence; the crossover stays a verified TWO-point closed form and
  must not be printed as three-point.  Stage B meanwhile 58/74 all UNSAT; clean gate CHAINED to
  auto-run after Stage B (HALT-marker guard).
- (R) ROUNDS 4-5 (task #33 cont., verifiers/cfg_hand/): three routes
  CLOSED — (a) the lead's merge/contraction route (direction argument:
  contraction enlarges the core, upper-bounds the max (R) needs
  lower-bounded); (b) the lead's chain-attainment route (nested f-caps
  NOT simultaneously attainable: 64/4000 pairs fail over 200 games,
  explicit T=14 witness with max = 15 < 16; (R) survives all 64 with
  margin >= 1 — the strictly stronger statement was the false one);
  (c) Lemma D alone (the eta < 0 dual branch is ACTIVE on ~1% of
  instances — 13/1200 pairs strictly worse under eta >= 0).  Lead's
  fallback framing corrected by r23: by strong duality the dual-vertex
  characterization IS (R), an enumeration strategy not a reduction.
  Constraint (ii) (exactness load-bearing) remains CHALLENGED by the
  lead — the balanced witness mu = 8/5 < 5/3 uses proper-only lambda;
  under paper5's N-inclusive lambda the game has mu = lambda = T/5
  exactly, and the free zeroth filter (lambda_proper > T/5 forces
  mu = lambda for ANY nonempty-core game) means the question lives
  only in lambda_proper <= T/5.  Resolution pending.  r23's
  recommendation: bank the specification as paper5 open problem 4 and
  hand (R) to a fresh attempt — three consecutive route-closures being
  the honest signal it needs a new idea.
- (ii) WITHDRAWN + SPEC BANKED (task #33 closure): r23 confirmed the
  lead's challenge on every point — the lambda-proper convention slip
  was SYSTEMATIC (one line copied across four scripts); the balanced
  witness satisfies mu = lambda under the paper's definition; the
  zeroth filter is now a lemma (127/400 games out of regime, all
  mu = lambda); everything structural survives BECAUSE the derivation
  used the N-inclusive lambda all along (Lemma D's step IS T >= 5*
  lambda).  (R) still tight in-regime (margin 0 at T=7).  In-regime
  balanced witness: NONE in 20,000 samples, recorded as OPEN (weak
  sampler; the right instrument is targeted construction over the
  residual cover shape).  Revised constraints: (i) establish (R);
  (iii) engage eta<0; (iv) no contraction; (v) no chain saturation;
  (ii) struck pending witness.  Live thread handed forward: the FACE
  y_p = f({p}) restriction (not covered by the contraction refutation;
  the face is the core of a reduced game where R4 could bite).  The
  specification is BANKED as paper5 open problem 4 (rewritten, with
  the crossover as part one).  NEW SIBLING LAW (r23, from three
  corrected claims with one shared cause): RE-READ THE DEFINITION YOUR
  CODE IMPLEMENTS against the definition the paper states, especially
  when you copy the line.
- BLOCK-RIGIDITY STEP 2 (task #35 cont., verifiers/extremality/
  REPORT5.txt addendum): DUAL DESCRIPTION proved + verified (26 games,
  5 profiles, 0 failures) — for disjoint-support envelopes,
  v(X) = min_j w(X cap B_j) and Core = {x >= 0 : x(N) = T, x(A) <=
  rho(A) := max_j w(A cap B_j)}, a pure upper-cap system (the analogue
  of paper5 thm:duality; lead re-derived the duality chain).  The
  cross-block caps x_u + x_v <= max(w_u, w_v) are the mechanism to aim
  at.  TRAP FLAGGED, NOT RESOLVED, on the record so nobody builds on
  it: the cap form invites a polymatroid/base-polytope argument
  (Dilworth truncation + Fujishige dec-min = inc-max), which would
  conclude Lmin = Lmax for EVERY profile — FALSE against the audited
  (3,2,1) witness.  Either the polytope is not the base polytope of a
  submodular rho^, or the dec-min = inc-max identity needs hypotheses
  this polytope lacks; settle (i)-vs-(ii) ON THE WITNESS before using
  the route.  A plausible chain contradicting an audited witness,
  handed over labelled instead of buried in a sketch.  No hand proof
  yet.
- THE s(6) GATE RULE, QUANTIFIED IN THE RECORD (pre-data; auditor's
  catch): the ledger had carried only the recon's soft form ("~0 ->
  launch; materially positive -> PARTIAL").  The lead's authorization
  messages had already fixed numbers BEFORE any gate data (0 -> launch;
  <=2% of sample -> launch with quarantine; >2% -> stop; restated as
  <=1/60 launch, 2+ stop), but messages are not the auditable record —
  hence this entry, written while the clean gate is still running and
  no clean number exists.  GOVERNING RULE, adopting the auditor's
  middle-band protocol: denominator = 60 configurations each run in
  ISOLATION (a contaminated run is void and the SAME configuration is
  re-run in isolation; it is neither success nor failure).  Then:
  0/60 unknown -> launch Stage C (600s cap, sharded <= cores,
  isolated).  1-2/60 -> re-run exactly those configurations at 1800s
  in isolation; all resolve -> launch Stage C with the same 3x-retry
  protocol for any Stage-C unknown; any survivor -> PARTIAL with the
  named list.  >=3/60 -> PARTIAL ("rho <= 2/3 except a named list"),
  no Stage C without a new decision.  Any SAT at target 2/3 anywhere ->
  HALT everything for the end-to-end audit.  Contingency: if the
  already-armed chain executes the earlier <=1-launch form before this
  refinement reaches r22, the earlier form governs — both are
  pre-data, and the audit records which executed.
- BLOCK-RIGIDITY ROUND 3 (task #35 cont.): TRAP RESOLVED, branch (i),
  hand-checkable — the tight rank function IS rho^ (verified on all 62
  coalitions of the witness) but rho^ is NOT SUBMODULAR (A={1,4},
  B={2,4}: 6 > 5 on the (3,2,1) witness), so Core is no base polytope
  and Fujishige/Frank-Murota never applied; the Dilworth truncation is
  submodular for INTERSECTING-submodular inputs only.  Route dead for
  a clean reason (lead's branch-(i) hunch confirmed).  PROVED by hand,
  case (a) of the rigid direction: at most one block >= 2 implies
  Lmin = Lmax — the core collapses to a CAPPED SIMPLEX (singleton
  blocks carry weight T so their caps trivialize) and both selections
  are the water-filling point (mechanism verified 36/36 at n=5-7).
  BLOCKERS STATED: (b) all-blocks-<=2 — cross-block caps bind, not a
  capped simplex, needs a different argument; (c) the breaking
  direction needs a witness FAMILY.  Not yet a paper5 proposition
  (needs (b)).  Compute rule complied: all r12 background jobs killed
  (the mid-run extremality hunts died — final tables lost, no claim
  affected since snapshots were already flagged as snapshots).
- (ii) RESTORED WITH A VALID WITNESS (task #33 final round,
  verifiers/cfg_hand/designed.py): the targeted search over the
  residual shape — COMPLETE for balanced games, since Lemmas B/C/E1
  use only core membership and the residual shape is thus the only
  violable vertex — found an in-regime balanced non-exact game in
  seconds: T=1, v(cd)=3/4, v(ce)=1/4, v(bde)=5/6, else 0; core point
  (0,1/6,1/6,7/12,1/12); lambda_proper = 1/12 (at ac, abe) <= T/5;
  mu = 1/18 < 1/12; exactness fails at d.  LEAD-VERIFIED all four
  claims independently.  So exactness IS load-bearing; constraint (ii)
  is a theorem about games; the specification is complete at FIVE
  constraints + the zeroth filter, banked in paper5 open problem 4
  (updated).  Ledger distinction per r23: last round's withdrawal was
  right about the invalid witness and over-cautious about the claim —
  the claim was true, the evidence was not; different failures.  The
  random sampler's 0/20,000 was the sampler, not the world: the
  designed search found the witness in seconds (tune generators, not
  volume — again).  Live thread handed forward: the face restriction.
- s(6) STAGE B CONTROLS ALL PASS (task #32): teeth 15/15 SAT and
  15/15 REALIZABLE at n=6 (Theorem-A LP audits, no vertex enumeration)
  — pipeline 2 SURVIVES THE DIMENSION JUMP, the round's key
  validation; drop-the-hypothesis 69/69 SAT; main verdicts 65 UNSAT /
  3 unknown / 0 SAT of 68 done.  All three unknowns cap-exact (600.0s
  vs max genuine solve 183.7s — nothing between), from OTHER agents'
  compute contending on the shared box; presumed artifacts per the
  standing law, auto-rerun in isolation at 1200s before the chained
  clean gate.  FLEET COMPUTE RULE adopted: while a solver stage runs,
  other agents refrain from heavy multi-core work.
- EXTREMALITY STRESS-TEST + C-C^ n=6 WALL (task #34, verifiers/
  extremality/): four designed regions at n=6 (bound 2/3) and n=7 (5/6),
  ~21,000 games, ZERO above either bound.  Region A (starved-Lmax
  hybrids) tops out FAR below AT n=6 ONLY — 8/15 vs 2/3, stable as the
  run grew: carrying the n=5 mechanism up COSTS ratio at six players.
  [RETRACTED by r12 same day: the n=7 companion figure 23/45 was a
  mid-run snapshot that later climbed to 2/3 (still under 5/6) — the
  costs-ratio reading is a SIX-PLAYER statement only; r12's own R3
  finding (never print a number off a running job) reproduced by its
  author within hours.  Quote figures only from completed
  extremal_*.json, never from ext*.log.]  Region C
  reaches 2/3 from a non-G construction.  NEW: region D — 3,718 games
  with 3-4 pairwise-disjoint-support generators at n=6 ALL have
  Lmin = Lmax (rho EXACTLY 0), while n=7 reaches 8/15; candidate
  rigidity theorem.  C-C^ n=6: encoding FAITHFUL (4 pinning controls),
  wall located EXACTLY = the CONJUNCTION exv2 x cert2 (cost tracks
  certificate-block count; structural; escape needs a sound multiplier
  bound or Caratheodory selector, neither found).  Lead premise
  corrections (2, recorded): the old lab already used existential
  exactness + Farkas certificates; two r12 harness bugs self-caught
  (control expectations are part of the control; stratum-index vs
  cut-position coincide only on singleton lower strata).
- PROCESS LAW (r23, from the Lemma-I* miss + the invented-citation miss,
  both of which passed every audit): AUDIT THE UNUSED HALF.  An "iff"
  whose converse is never invoked, a declared reference never cited, a
  hypothesis never discharged — nothing consumes them, so nothing checks
  them, and that is exactly where errors survive audits.  Both failures
  were invisible to use-driven checking and surfaced only on line-by-line
  reading against a source.
- s2(n) = 2−8n/(n²−(n mod 2)) as upper bound; 2-generator extremality.
- General facet dichotomy (packet facet iff full-trace).
- h=4/h=5 completeness at n=7 (needs per-type construction, not sampling).

### Method laws (validated hard this campaign)
1. Random-harvest "never occurs" claims are sampling artifacts until a finite
   check or design search confirms: split packets "absent" in 58k+239k games
   existed; two loser-set laws perfect on all data died on region change.
2. Tune generators, not volume: two-row envelopes give 56% slack-bearing
   games vs 17% mixed; unseeded c-space search certifies nothing at n≥6.
3. "Characterize what the hill-climb plateaus at" converts resistance into
   lemmas (rich-overlap found this way; ZP configuration likewise).
4. Complete-enumeration-to-total-T is complete only up to denominator T:
   a lower-bound method, never a sup determination.
5. Every subagent headline re-verified centrally before use: caught a wrong
   empty-set convention, a membership gap in a "proved for all (p,k)" claim,
   and an attribution error that our own large-core result refutes.
