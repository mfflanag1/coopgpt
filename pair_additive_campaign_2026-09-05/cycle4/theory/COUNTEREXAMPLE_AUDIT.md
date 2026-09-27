# Independent first-stage audit: exact ratio 1/9

The experiment candidate is a valid counterexample to the universal 1/6 conjecture, already at the positive first leximin stage. This note audits the raw pair matrices, two payoff covers, and a perfect matching; it does not trust the experiment's budget vector or an asserted complete leximin selector.

Input: `../experiment/candidate.json`. Independent check: `audit_candidate.py`; recorded output: `CANDIDATE_AUDIT.json`. All arithmetic is rational. The checker imports no solver and succeeds under Python `-O`.

## Market and full-core verification

There are 21 players in each sector I,J,K, indexed 0 through 20. The complete strict-triple worth is A_ij+B_ik+C_jk. The matrices have 30 positive entries, all nonnegative, and maximum entry 9. There are no profitable coalitions with fewer than three players.

The supplied matching contains 21 triples, covers every player exactly once, and has total worth 87. Both supplied vectors `x` and `y` are nonnegative, sum to 87, and satisfy all 9,261 triple inequalities. The checker separately verifies every matching equality for both vectors. Summing the triple inequalities over any disjoint matching proves the displayed perfect matching is optimal. Summing them over any coalition's optimal matching, and using nonnegativity for unmatched players, proves both vectors are in the whole labeled payoff core, including all coalitions. Thus T=87 and the full core is nonempty.

The vector named `x` in the input is used only as a floor-attaining cover: every coordinate is at least 1. Write ell for the actual complete ascending leximin allocation.

## A directly checkable whole-core upper budget

Every triple below uses local sector indices. Add these tight matched-team equalities, with the indicated multiplicities:

| Multiplicity | Matched triple | Worth |
|---:|---|---:|
| 3 | (0,2,2) | 6 |
| 1 | (3,5,5) | 3 |
| 1 | (4,3,4) | 12 |
| 1 | (6,8,8) | 9 |
| 1 | (11,11,9) | 3 |
| 1 | (12,13,13) | 9 |
| 1 | (17,17,15) | 3 |

The resulting right-hand side is 57. Subtract the following six lower-bound triple inequalities, each once:

| Triple | Worth |
|---|---:|
| (0,3,8) | 18 |
| (0,11,2) | 6 |
| (0,13,2) | 6 |
| (3,8,5) | 3 |
| (4,5,13) | 6 |
| (12,17,9) | 9 |

Their worth sums to 48. Cancelling the coordinates gives, for every full-core p,

\[
p_{I_6}+p_{I_{11}}+p_{I_{17}}+3p_{J_2}
 +p_{K_2}+p_{K_4}+p_{K_{15}}\le9.
\]

The coefficients are nonnegative and sum to 9. Consequently no core vector has every coordinate greater than 1. The supplied floor cover achieves minimum 1, so the first optimal floor is tau=1. At every point of that max-min face, each coordinate in the displayed budget is at least 1, and equality of the weighted sum forces each to equal 1. In particular, ell_(I6)=1, regardless of any later leximin stages.

The matched equality p_(I6)+p_(J8)+p_(K8)=9 and nonnegativity imply H_(I6)<=9. The independently verified core vector `y` has y_(I6)=9, so H_(I6)=9. Therefore

\[
\frac{\ell_{I_6}}{H_{I_6}}=\frac19<\frac16.
\]

Dividing all pair entries and payoffs by 3 gives the same ratio with pair weights in {0,1,2,3}, T=29, tau=1/3 and H_(I6)=3. This is only a rescaling; no player deletion or alteration of the core is involved.

## Residual partial-matching certificate

Let M denote unit weight on the displayed perfect matching. Let beta be the matching multiplicities in the first table (zero elsewhere) and alpha the unit multiplicities in the second table. Define

\[
\lambda=M-\beta/3+\alpha/3.
\]

Every lambda weight is nonnegative. Its player deficits d=1-load(lambda) equal one third of the displayed budget coefficient vector. Hence total deficit is 3, the I6 deficit is 1/3, and their ratio is exactly 9. The dual objective for residual triple values w-3 is 24=T-63. Thus lambda is an explicit optimal fractional partial matching for the residual-cover LP. The general identity in `RESIDUAL_PARTIAL_MATCHING.md` recovers H_(I6)<=9 from this certificate.

Conversely, any optimal residual partial-matching certificate with positive I6 deficit has total-deficit/target-deficit at least 9, because the valid ideal witness attains 9. Thus the proposed sufficient six-deficit certificate lemma is false as well.

## Audit limits

Only the designated full-leximin coordinate is certified here; the supplied floor cover is not claimed to equal the whole final selector. This audit makes no claim of novelty, smallest instance size, a universal 1/9 lower bound, or a family tending to zero. The bounded first-stage 1/6 proof attempt is closed by this counterexample.
