# Specialist review packet: the pairwise/three-way boundary

## Exact claims

For standard three-sided assignment games with arbitrary nonnegative triple weights, positive integral matching worth T and a nonempty entire core, the supremum of ||leximin−leximax-min||_1/T is 2. Equally sized sectors and values in {0,1,2,3} suffice. All players, including fixed zeros, are counted.

An explicit family gives n=9(L+R)+12, T=3(L+R+2) and

    rho = 2[((R+2)2^L−1)] / [(2^L+2)(L+R+2)].

R=L² proves convergence to2; suitable parameters plus at most eight zero players give 2-S_n=O(log n/n). The same family gives a leximin/core-maximum coordinate ratio 2/(2^L+2), ruling out every positive dimension-independent fraction. A companion family instead has ratio 1/(2^L+1) and exactly zero selector distance.

## Load-bearing proof

1. Local matching triples and global-dummy alternatives force pair totals and zero dummies. A displayed integral matching and covering allocation have equal value; neither balancedness nor fractional worth is assumed.
2. Alternating sector colors permit complementary triple constraints encoding q_l=(J−I)q_(l−1). Cross-triples pin copies to top payoffs. Both directions of the entire-core description are proved.
3. Root pair offsets make the unit ceiling have a unique feasible allocation q0=0, hence full leximax-min. A positive floor η implies 2 sumq0>=3η and 2^L sumq0<=3(1−η). Thus η<=2/(2^L+2), with equality uniquely pinning every coordinate. This identifies full leximin without restricting to symmetric points or breaking first-stage ties arbitrarily.
4. Replicated top pairs dominate the normalized distance. The coordinate and distance conclusions follow from separate calculations.

The prior two-sided internal theorem gives the half-of-core-maximum guarantee and sharp n-player maximum floor(n/2)/(floor(n/2)+1). Matched pairs permit equal threshold transfers; matched triples support recursive amplification. This is the proposed significance of the comparison.

## Questions for specialist review

- Is either conclusion implied by a known representation theorem for multisided assignment cores? A polytope embedding would also need to control added payoff coordinates and full sorted selectors.
- Are these recurrence constructions or exponential payoff ratios present in Quint1991, Lucas1995, or subsequent multisided egalitarian work under different terminology?
- Does an economically motivated subclass of genuine triple complementarities preserve a uniform distance bound or individual protection?
- Does the all-n deficit improve from O(log n/n) to O(1/n), and would that refinement add meaning beyond the structural result?
- Is the comparison best presented as one two-sided/three-sided paper, with the unrestricted exact-TU result separate?

## Evidence and review boundary

The four-page note, expanded proof, independent structural audit, two raw generators, exact full-selector checks, bounded 2x2x2/3x3x3 calibrations and negative controls are included. Larger cases use exact primal/dual certificates before full selector optimization. Source coverage and unavailable originals are explicit in PRIMARY_SOURCE_AUDIT.md.

This packet records an internally proved candidate contribution. External correctness, novelty and field significance are not established. It has not been sent to anyone; no external communication is authorized.

The next direction is to consolidate the pairwise and three-way results and resolve their priority. The exact finite-n three-sided rate is a secondary question, not a reason to withhold the completed structural result.
