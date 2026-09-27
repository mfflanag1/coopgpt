# Review: four-cycle counterexample certificate

All arithmetic below was done by hand from the packet contents. I did not execute `check_cycle.py` or any other tool.

## Findings

### Hand verification of the certificate (no correctness defects found)

**Matching worth and perfectness** (`FOUR_CYCLE_CERTIFICATE.json` lines 223–242; `check_cycle.py` lines 12–16).
Using row = first-sector label, column = second-sector label, as stated in `FOUR_CYCLE.md` line 3:
- (0,1,0,2): M01[0][1]+M12[1][0]+M23[0][2]+M03[0][2] = 1+2+2+2 = 7
- (1,2,1,0): 1+2+2+1 = 6
- (2,0,2,1): 1+2+2+0 = 5

Total 18 = T; each sector uses labels {0,1,2} once. ✓

**x is a nonnegative full-team cover of total 18** (lines 93–106). Sum of the numerators in eighths is 144 → 18 ✓. I enumerated all 81 teams by fixing (a,d) and iterating (b,c). Every team satisfies x(t) ≥ w(t); the tight teams are exactly (0,2,1,0), (0,1,0,2), (1,2,1,0), (2,0,2,2), (2,1,1,0), (2,0,2,1). Minimum coordinate 9/8 ✓. By weak duality every partition of the 12 players into disjoint full teams has worth ≤ x(N) = 18, so integral matching worth is exactly 18 and x is a core point. ✓

**Six dual weights** (lines 167–222). Worths: 7, 7, 6, 5, 6, 7. Σλ_t w_t = 21/4 + 7/4 + 3 + 5/2 + 3/2 + 7/4 = 63/4, so T − Σλw = 9/4.
Loads per player (flattened index): [1, 1/2, 1, 3/4, 1, 3/4, 3/4, 1, 3/4, 1, 1/2, 1]; all ≤ 1 ✓. Deficits d = [0, 1/2, 0, 1/4, 0, 1/4, 1/4, 0, 1/4, 0, 1/2, 0], Σd = 2, τ·Σd = 9/4 ✓. d_3 = 1/4 > 0 ✓. The set {d_i > 0} = {1,3,5,6,8,10} coincides with the level-9/8 set in `levels` (unverified auxiliary, but consistent).

**Identity and pinning argument** (`FOUR_CYCLE.md` lines 11–16). Σ_i d_i p_i + Σ_t λ_t(p(t) − w_t) = Σ_i p_i − Σ_i load_i p_i + Σ_i load_i p_i − Σλw = T − Σλw for any efficient p. Correct. With p in the core all terms are nonnegative, so (i) no core point has all p_i > τ (since Σd > 0), (ii) on p ≥ τ, Σ d_i p_i ≥ τΣd = RHS forces d_i(p_i − τ) = 0. Since x attains min 9/8, the first leximin level is 9/8 and player 3 is pinned there in any leximin-optimal core point regardless of later stages. No missing hypothesis: the argument uses only efficiency, cover constraints, and nonnegativity, all of which are core conditions for this game (only full teams productive, so coalition-wise constraints reduce to full-team plus nonnegativity).

**Ideal upper bound and attainment** (lines 153–166). Optimality of the matching (verified above) plus core covering makes each matching team tight, so p(2,0,2,1) = 5 and p_3 ≤ 5 by teammate nonnegativity. Witness y = [1,0,0,5,5,4,0,0,0,2,0,1]: sum 18 ✓, y_3 = 5 ✓. Since sector 2 contributes 0 and y_sector1 ∈ {5,5,4}, I checked the maximal w over c for every (a,b,d) against y(t); all 81 teams covered, with tight cases at e.g. (0,2,c,0) w=7 vs y=7, (0,1,c,2) w=7 vs 7, (2,0,c,1) w=5 vs 5. ✓ So H_3 = 5 and ratio = 9/40 < 10/40. ✓

**Checker logic** (`check_cycle.py`). `w` matches the documented indexing; perfect-matching test, both cover checks (162 constraints), floor positivity, load/deficit/identity checks, target-team selection (`t[1]==0` → (2,0,2,1)), and the ratio comparison are all correct for this JSON. `tuple(t) in teams` works since `teams` holds tuples.

### Low-severity / robustness notes (not defects in the mathematical claim)

1. **Low — `check_cycle.py` line 12: `zip(edges, matrices)` truncates silently.** If the JSON ever had fewer matrices than edges (or vice versa), `w` would silently drop edges. Suggest `require(len(r['edges'])==len(r['matrices'])==k)` and a shape/entry-range check (the doc claims entries in {0,1,2}; the checker does not verify this). For the supplied JSON the counts and entries are correct by inspection.

2. **Low — unverified auxiliary fields.** `H` (all 12 ideals), `levels`, and `raw_exclusions` are not checked by the script. The doc discloses that only x-as-floor-witness and the single target ideal are needed, which is accurate; but a reader may take `H[1]=9/2`, `H[10]=9/2`, or the full level structure as certified. Suggest either dropping them from the certificate file or labelling them "unverified, from optimizer".

3. **Low — wording, `FOUR_CYCLE.md` line 7 vs `check_cycle.py` line 25.** Doc says "six positive" weights; the checker only enforces `weight>=0`. Harmless here (all six are positive) but the checker is looser than the prose.

4. **Low — wording, `FOUR_CYCLE.md` line 20.** "verifies … disjointness" — the only disjointness check is the perfect-matching test at line 15; dual teams need not be disjoint (and are not). Consider saying "matching perfectness".

## Scope limitations

- Hand verification only; I did not run the script. The 81-team cover checks for x and y were done by hand via the (a,d)/(b,c) decomposition; I believe they are complete, but a transcription slip on my side is possible in principle.
- No Git HEAD available; cannot assess regressions or relation to the "prior path review".
- I did not assess novelty or whether c(C4) or a vanishing family is implied; the file's own scope statement (line 244) correctly disclaims those.
- The meaning of "raw-core", "raw_exclusions", and "full leximin" relative to any variant leximin notion in the broader project is not defined in the packet; my verification assumes the standard leximin over the core polytope.

## Verdict

**No findings in reviewed scope** (only low-severity robustness/wording notes). The matching worth 18, the cover x with floor 9/8, the six dual weights with loads ≤ 1, Σd = 2, the identity T − Σλw = 9/4 = τΣd, d_target = 1/4 > 0, the tightness-based ideal bound H_3 ≤ 5, and the witness y attaining 5 all check out by hand; the stated ratio 9/40 < 1/4 follows.
