# Independent audit of the finite 1/6 example

5 September 2026. **No mathematical gap found in the finite attainment claim.** The saved complete, nonnegative pair-additive market has 27 players, integral worth 24, a nonempty full core, full leximin payoff `x[b_1]=1/3`, and whole-core ideal `H[b_1]=2`. Hence its individual ratio is exactly `1/6`. This is an attainment example, not a universal lower bound or a priority claim.

Input: `../experiment/finite_attainment_exact.json`, SHA-256 `6a5732d9278f32772fea31127941581d2125227e7b0e8b55a6dbdf984bf08219`. The independent script imports this JSON as data; it imports no campaign scientific code or optimizer. Its input path is relative to the script's resolved location and is portable with the campaign directory.

## Full market and full core

The three 9 by 9 integer pair matrices define every one of the 729 triples by `w(i,j,k)=A[i,j]+B[i,k]+C[j,k]`. The verifier checks matrix dimensions and nonnegativity, rather than discarding unlisted mixed triples. In each of the three local blocks the disjoint teams `(a,f,i)`, `(b,d,h)`, and `(c,e,g)` have weights 1, 3, and 4. They partition all 27 players and give a matching of value 24.

The saved leximin allocation, descending-minimum allocation, and target ideal witness each have nonnegative coordinates summing to 24 and cover every triple, checked with exact fractions. Thus each bounds the worth of any matching by 24, while the displayed matching attains 24. The worth is therefore exactly 24. Triple covers plus nonnegativity imply every coalition inequality by summing over an optimal matching of that coalition, including unmatched players. Conversely, a full-core allocation satisfies these covers. The raw constraints used below consequently describe the entire core, not a selected face or a fractional relaxation with an unverified surplus.

## Conventional proof for the target

The minimum coordinate cannot exceed `1/3`, since any local team `(a,f,i)` has total payoff 1 throughout the core. The saved cover attains this floor. Every coordinate in each such small team is therefore `1/3` on the entire first max-min face. In particular, `a_0=i_2=1/3` there.

The three cross-pair entries make `(a_0,d_1,i_2)` a weight-3 triple. Its cover forces `d_1>=7/3` on the first face. The matching equality `b_1+d_1+h_1=3`, together with `b_1,h_1>=1/3`, forces `b_1=h_1=1/3` and `d_1=7/3`. Thus **every later refinement of the full leximin selector has the asserted target payoff**. No assumption about unexamined later levels is necessary for the individual-ratio claim.

On the entire core the same two team constraints yield `b_1<=a_0+i_2-h_1<=2`, because the two small-team equalities and nonnegativity give `a_0,i_2<=1`. Equivalently, the following exact identity is a nonnegative-slack certificate:

`2-b_1 = (1-a_0)+(1-i_2)+h_1+(a_0+d_1+i_2-3)`.

The saved ideal witness has `b_1=2`, and all its 729 triple covers were independently checked. Hence the ideal is attained on the full core and equals 2.

## Extra selector verification

`check_finite_attainment.py` also checks the complete saved labeled selectors. It verifies all five distinct ascending levels and all four distinct descending levels. At each level it rejects a strictly better floor or ceiling on the preceding face, imposes the attained weak bound, and proves that every claimed coordinate of that level is forced there. The candidate itself supplies feasibility and the higher or lower coordinates for the next stage. Induction therefore proves the full lexicographic conclusion, rather than merely proving one max-min or minimax optimization.

The nine levels require 18 raw linear-real-arithmetic UNSAT queries; a separate query proves the whole-core target upper bound. All 19 returned UNSAT. Every other solver status, including UNKNOWN, raises an error. No optimizer status or returned optimum is accepted. The reported full-selector distance `||x-z||_1/24=5/9` is also checked with exact fractions; it is ancillary to attainment and does not improve the distance lower bound.

## Evidence and limits

The completed run is recorded in `finite_attainment_checks.json`: 2,187 exact triple-cover checks across three allocations, the explicit integral matching, 19 UNSAT queries, target ratio `1/6`, and distance `5/9`. The implementation checks all 27 payoff coordinates, including the zeros of the descending selector and ideal witness. Z3 reports version 5.1.0. The target claim also has the short conventional proof above and exact feasible witnesses; the additional full-selector conclusions rely on the raw solver queries, without exported proof objects. Ideals of the other 26 players in the source record were not audited.

The independent six-player completion obstruction in `EMBEDDING_NO_GO.md` is logically separate. Its zero-slice and retained-clause hypotheses do not automatically hold for nested compositions of this finite gadget. It neither rules out a ratio below `1/6` in another pair-additive market nor obstructs every auxiliary-player construction.
