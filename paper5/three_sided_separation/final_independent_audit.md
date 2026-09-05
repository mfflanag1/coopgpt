# Final bounded independent code and proof audit

2026-09-04. Reviewed the complete contents of calibration/exact_three.py, verify_gadgets.py, and calibrate_three.py. No material mathematical or verification defect found.

- exact_three.core enumerates integral matchings correctly by either leaving the next A-player unmatched or assigning it a currently available B,C pair. Full coalition enumeration includes every nonempty coalition and uses its exact matching worth. The sparse triple version defines the same entire core because arbitrary coalition matching inequalities follow by summing triple inequalities and nonnegativity.
- The selector routine computes every lexicographic stage by exact rational optimization and freezes precisely those coordinates constant at that stage's optimal level. It is correct that previous free-coordinate caps are not explicitly retained: the previous face remains feasible after fixing its pinned coordinates, so later ascending levels cannot decrease and descending levels cannot increase. The new uniform cap therefore implies all previous caps. Compactness ensures a pinned coordinate exists, and failures or unknown optimizer statuses raise exceptions.
- The gadget generator validates colors and conflicting weights. The displayed disjoint integral matching and feasible nonnegative cover have the same total, exactly certifying integral optimum and core nonemptiness before selector computation. Omitting zero-value triples is sound.
- The exact formulas are independently compared against full selectors obtained directly from raw triple inequalities. The tests include multiple depths, replication counts, the unshifted family, shifted family, and structural negative controls.
- The root-anchor removal control asserts genuine enlargement of the entire core. Its code comment about unchanged selectors is not separately asserted, but this does not affect the asserted enlargement test or the main theorem. A reader should not count that comment as an additional independently enforced test.
- The bounded calibration includes all256 binary2x2x2 arrays, the zero case, the sourced empty-core example, the Lucas inequalities, additive3side markets, and12 fixed-seed3x3x3 arrays beyond the additive class. The final12 arrays are random draws from a fixed bounded domain, not an exhaustive3x3x3 classification.

## Direct full-leximin proof, avoiding symmetry assumptions

For the shifted family let eta be the smallest active payoff after fixed-zero dummies are removed, and write Q_l=sum_i q[l,i]. Recurrence gives Q_l=2Q_(l-1). Level1 U-payoffs imply q[1,i]>=eta; levelL V-payoffs imply q[L,i]<=1-eta. Therefore

  3*2^(L-1)*eta <= Q_L <= 3*(1-eta),

and eta<=2/(2^L+2). The explicit candidate t=1/(2^L+2), q[l,i]=2^l t attains this value for every L>=1. Equality forces all three q[1,i]=eta. Since J-I is invertible (eigenvalues2,-1,-1), all root coordinates equal eta/2. Hence the entire core point is unique already at the first nonfixed maximin stage, and is necessarily full leximin. Root values and every intermediate/copy payoff meet the claimed floor; t<=1/4 guarantees the root complements do also.

For the unshifted family, the analogous inequalities q[0,i]>=eta and q[L,i]<=1-eta give eta<=1/(2^L+1). Equality pins every q[0,i]=eta and uniquely identifies full leximin. For its minimax M, V[0,i]<=M gives q[0,i]>=1-M, while U[L,i]<=M gives q[L,i]<=M. Thus 3*2^L*(1-M)<=3M, or M>=2^L/(2^L+1), with equality uniquely pinning the same root vector. This proves coincident full selectors directly.
