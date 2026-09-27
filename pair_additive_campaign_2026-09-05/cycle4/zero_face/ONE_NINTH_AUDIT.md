# Independent raw audit of the 1/9 counterexample

5 September 2026. **PASS: the saved finite market disproves the proposed one-sixth individual guarantee, including its restriction to players at a positive first global leximin floor.** No numerical or rational inconsistency was found.

Input: `../experiment/candidate.json`, SHA-256 `ece7e5c8d09c3e314573654ec85d96648d0f29607f5be6ebc731253a3fb99472`. The raw verifier is `verify_one_ninth_raw.py`; the completed output is `one_ninth_raw_checks.json`. The script uses the candidate JSON as data, with no imports of the generator or campaign scientific modules. It ignores the `budget`, `floor_support`, and `predicted_ideal` fields completely.

The three pair matrices are each 21 by 21 and have nonnegative integer entries. The verifier independently constructs all 9,261 induced triple values from `A_ij+B_ik+C_jk`, with all three sectors and all 63 labeled players retained. It checks the 21 saved matching teams form an exact partition with one player from each sector per team. Their weights sum to 87. Both supplied rational allocations are nonnegative, sum to 87, and satisfy every one of the 9,261 triple covers: 18,522 exact Fraction checks in total.

The matching therefore supplies an integral lower bound of 87, and either covering allocation supplies an upper bound of 87 for every matching. Consequently the actual grand-coalition worth is 87 and the core is nonempty. The complete raw triple covers, nonnegativity, and this verified efficiency equation describe the full core: summing the covers over any coalition's optimal matching proves its coalition inequality, with unmatched players contributing nonnegative payoffs.

The raw audit establishes three statements with fresh linear-real-arithmetic queries:

1. There is no core point with every coordinate strictly greater than 1. The supplied first-face point has minimum 1, so the first global leximin floor is exactly 1. Independently, any weight-3 matching team already gives the upper bound.
2. There is no core point with every coordinate at least 1 and target coordinate 6 strictly greater than 1. Thus the target is identically 1 on the entire first max-min face. Every continuation of the full leximin refinement stays on that face, proving the target payoff is 1. **The argument needs no claim that the entire supplied first-face allocation is the full leximin vector.**
3. There is no core point with target coordinate greater than 9. The supplied second allocation has target 9. The upper bound also follows conventionally from the target's matching team `(6,8,8)` in sector-local indices: it has weight 9, so its matching equality and nonnegativity bound the target by 9. Hence the entire-core ideal is exactly 9.

All three solver outcomes were UNSAT. UNKNOWN, timeout, SAT, or any other outcome causes the verifier to raise an error; no optimizer or returned optimal objective is used. Z3 reports version 5.1.0. No exported proof object accompanies these raw queries. Matching, all cover checks, and the ideal attainment/upper bound have direct exact-arithmetic certificates; target forcing on the first face is independently reproduced here by the raw solver query, while the root agent separately audits a conventional budget proof.

The certified target ratio is therefore `1/9`, strictly below `1/6`. This audit asserts neither the other coordinates of the full selector, any descending selector, a distance result, an all-size family, a universal one-ninth lower bound, nor novelty. The zero-face reduction note in this directory remains valid but is logically unnecessary for this counterexample, whose first global floor is already positive.
