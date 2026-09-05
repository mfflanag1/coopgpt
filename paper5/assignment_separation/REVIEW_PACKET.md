# Assignment-game separation: specialist review packet

## Exact claim

For a nonnegative weighted bipartite assignment game with positive matching value T, let x be the full ascending-lexicographic maximum of core payoffs and z the full descending-lexicographic minimum. The core is the entire optimal matching-dual face. If a fixed optimal matching has k positive-weight edges, then

    ||x-z||_1/T <= k/(k+1).

The same bound holds for any minimax core allocation z. It is attained for every k>=2. For k=1 the selections coincide. Counting all players, including isolated ones, gives exact maximum floor(n/2)/(floor(n/2)+1) for n>=4 and zero for n=2,3.

## Load-bearing arguments

1. **Half domination.** For any other core point y, threshold the changes y-x on one market side. Matching complementarity identifies a same-size set with opposite changes on the other side. No tight edge blocks the corresponding equal transfer. Full leximin then implies y_i<=2x_i for every player.
2. **Finite correction.** Write pair displacements as (d_i,-d_i), D=sum|d_i| and M=max z. Half domination implies each pair weight is at least 2|d_i| and D<=kM/2. Minimax optimality supplies one coordinate with z_i=M<=x_i. Its pair has an extra weight contribution of at least M, so T>=2D+M and the sharp bound follows.
3. **Attainment.** A complete market with identical rows (1,...,1,2) has a segment core: all left payoffs equal t, and right payoff j equals its column weight minus t. Leximin selects t=1/2, minimax t=1, and normalized distance is k/(k+1).

The structural lemma gives simultaneous half-of-maximum-core-payoff guarantees for leximin. The existing fair-price midpoint has a related guarantee; priority for this property of leximin itself needs review.

## Boundary with the previous exact-game result

Exact assignment games have zero divergence. Exactness for the two whole-side coalitions produces opposite side-zero core allocations. Their midpoint balances each matched pair and is majorized by every core point; therefore it is both selections. This is consistent with known exact-assignment and pairwise egalitarian results, and is not presented as a novel classification.

The new attaining family is nonexact: the distinguished high-value right player cannot receive zero anywhere in the core. Thus the unrestricted exact-game asymptotic maximum tending to two and the arbitrary-assignment maximum tending to one concern intersecting classes with a zero-divergence intersection.

## Questions for review

- Is the coordinatewise half-of-core-maximum guarantee already implicit in older egalitarian or alternating-adjustment characterizations?
- Has the sharp k/(k+1) normalized distance appeared under another name, or does an existing theorem imply it immediately?
- Is matched-pair count the most useful economic formulation, or should the distance theorem be presented as a consequence of the individual payoff guarantee?
- Which assumptions distinguish the theorem from weighted-agent fairness, bargaining solutions, or Owen-set variants?
- Would a short theorem paper on this natural market class be a useful contribution, given the elementary attaining family and exact finite answer?

## Evidence and next direction

The all-parameter proof has been independently reviewed. Exact full-coalition computations cover all 255 bounded 2-by-2 markets, targeted larger and rectangular cases, and attaining families. A second implementation covers both even and odd player counts. The dated source audit found no equivalent sharp quantitative theorem, but does not certify novelty.

The stated research target is resolved internally. The next priority is external correctness and prior-art review of this concise package. A subsequent structural campaign could ask whether weighted fairness priorities preserve a comparable guarantee, or which generalizations of matching complementarity retain it; their literature frontier should be checked before selection. Reopening numerical optimization of the settled finite formula has no research value.

This review packet has been prepared locally and has not been sent to anyone.
