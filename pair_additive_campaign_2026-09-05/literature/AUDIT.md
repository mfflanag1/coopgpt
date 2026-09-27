# Independent adversarial audit of the finite nine-player witness

5 September 2026. Reviewed `/private/tmp/coopgt-pairadd-20260905/COUNTEREXAMPLE.md` and `verify_rational.py` read-only. Exact SHA-256 hashes are in `audit_results.json`. The literature gate is separately recorded in `SOURCE_GATE.md`.

**Verdict:** no mathematical error or proof gap found in the finite counterexample, either full selector, or the exact ratio. The example establishes `c_pair <= 5/18 < 1/3`. It does not establish vanishing protection, a new distance lower bound, minimality, or priority. The claim of solver-free arithmetic verification accurately describes the supplied script; the universal selector arguments remain conventional mathematical proofs, not a formal proof checked by that script.

## Obligations checked

1. **Membership in the frozen class — note lines 5–11; verifier lines 12–16.** There are three sectors of size three, every full triple is present, and all entries of A,B,C are nonnegative integers at most three. An independent literal transcription of all 27 triple values agrees entrywise with `A_ij+B_ik+C_jk`; the minimum and maximum triple values are zero and four. There are no productive pairs in the worth function used for this audit. Thus no generalized-market core or auxiliary-agent projection is being substituted.

2. **Integral worth and the entire core — note lines 13–21; verifier lines 17–32.** The three displayed teams partition all nine players and have values 1,3,4. Their value is 8. Any matching's value is bounded by the sum of its covered payoffs at x, hence by 8 because uncovered payoffs are nonnegative. This works for partial as well as perfect matchings. Conversely the displayed matching attains 8. A nonnegative efficient allocation satisfying all triple covers satisfies every coalition inequality: sum the covers of its disjoint teams, then add any unmatched players' nonnegative payoffs. Necessity follows from singleton and triple coalitions. Thus the argument really uses the full labeled payoff core. Independent dynamic programming over all 512 coalitions verifies x,y,z against every coalition inequality; all pass. Independent enumeration of the 36 perfect matchings gives maximum 8 and exactly one optimal perfect matching.

3. **Matching equalities — note line 19.** Each of the three corresponding team constraints has nonnegative slack. Their right-hand sides total 8 and their left-hand sides sum all payoffs, also 8. Their slacks must all vanish. This holds for every full-core point, not merely the three witnesses.

4. **Full ascending leximin — note lines 25–31; verifier lines 34–49.** At any point the minimum is at most `(a+f+i)/3=1/3`. Feasible x attains 1/3. On that entire maximizing face a=f=i=1/3. For the other six coordinates, adding the last two matching equalities and subtracting the weight-four cover b+f+g>=4 gives c+d+e+h<=10/3. Consequently their minimum is at most 5/6. At x all six are at least 5/6, so this is the optimum for the fourth ascending order statistic after the first three fixed entries. On its optimal face the four coordinates in this sum must each equal 5/6. Then the matching equalities force b=4/3 and g=7/3. The feasible face is a singleton. This proves the *full* ascending selector; it does not confuse a maximin witness with leximin.

5. **Individual maximum — note lines 35–41; verifier lines 24,26–32,57–58.** Every core point has b+d+h=3 and is nonnegative, so d<=3. The independently checked full-core point y has d=3. Hence H_d=3 exactly, not an optimum inferred from a numerical solver. At the uniquely determined x, `x_d/H_d=(5/6)/3=5/18`.

6. **Full descending lexicographic minimum — note lines 47–51; verifier lines 51–56.** At any core point f<=1, so b+g>=3. A payoff ceiling below 3/2 is impossible, and z attains 3/2. Under this ceiling, b=g=3/2, f=1, a=i=0 are forced. The (a,e,g) cover forces e=3/2, then c=1. The (a,d,i) cover forces d>=1, with h=3/2-d. Thus every minimax point lies on

   `p(t)=(0,3/2,1; t,3/2,1; 3/2,3/2-t,0)`.

   Independent exact intersection of all 27 covers, all nonnegativity constraints, and the 3/2 ceiling gives precisely `1<=t<=3/2`. This is the entire minimax face, not just a selected feasible segment. Its descending sorted vector is `(3/2,3/2,3/2,t,1,1,3/2-t,0,0)`, including the endpoint ties. The first varying descending entry is t, uniquely minimized at t=1. This recovers exactly z. The note's last selector step is correct; the explicit face parametrization is optional exposition, not a missing hypothesis.

7. **Distance and scope — note lines 53–59; verifier lines 59–60.** Exact Fraction arithmetic gives `||x-z||_1=11/3` and normalized distance `11/24`. The example separates failure of the 1/3 individual guarantee from large selector distance. The existing additive-family 4/3 supremum is a separate calibration result, not something demonstrated by this finite witness. No asymptotic mechanism is proved in the note, and its discussion correctly leaves that question open.

## Verification assessment and results

`python3 verify_rational.py` completed successfully with PASS, 81 triple-cover checks, T=8, H_d=3, fraction 5/18, and rho=11/24. Its exact `Fraction` arithmetic and explicit `require` function avoid floating tolerances and Python's removable assertion statements. It calls no solver, so solver UNKNOWN, unboundedness, and unchecked optimizer status are not applicable. The matrices and witnesses are fixed literals; it is a finite instance verifier, not a general-purpose input validator.

The checks at lines 45–49 and 54–56 test displayed values and useful identities. They do not independently prove quantifier statements about every feasible point, uniqueness, or anonymous sorted optimization. Those conclusions follow from the elementary deductions reviewed above. The script's final scope string already says “finite witness and conventional-proof identities,” which is appropriately limited. No formal certification claim should be added without a further proof interface.

`python3 literature/audit_checks.py` also passed. It imports neither the campaign verifier nor any solver. It independently transcribes the raw tensor, computes all coalition values by exact disjoint-team recursion, checks all 1,536 witness/coalition inequalities, enumerates all 36 perfect matchings, and intersects the exact minimax interval. Reproduction outputs are `audit_results.json` and `reviewed_verifier_result.json`.

Confidence is high in the finite mathematical counterexample and its stated selectors. Residual limitations are the ordinary trust in these short Python arithmetic checks and the conventional proof review, unestablished source priority, and the completely unresolved all-size sharp constants. No edits to the reviewed note, its verifier, existing papers, or other workers' files were made.
