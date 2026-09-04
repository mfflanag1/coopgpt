# Specialist review packet

## Claim to assess

For singleton-normalized exact transferable-utility games with n players and T=v(N)>0, define x as the allocation lexicographically maximizing its increasingly sorted coordinates, and z as the allocation lexicographically minimizing its decreasingly sorted coordinates. Set rho=||x-z||_1/T and s_n=sup_v rho. We prove

    lim_(n -> infinity) n(2-s_n) = 2,
    2-s_n = 2/n + O(log(n)/n^2).

The four-page manuscript contains a complete conventional proof. The claim concerns entire exact-game cores. It is not a statement about Owen subsets, coalition-excess lexicographic optimization, or a fixed-n optimum.

## Three short obligations

1. **Generic bound.** For any compact convex nonnegative constant-total set, any maximin point x and minimax point z satisfy sum min(x_i,z_i)>=T/(n-1). A bottom-coordinate directional witness and a different top-coordinate directional witness prove the bound.
2. **Realization.** For invertible zero-one A with d=A^(-1)1>0, unit-sum donor subsets and complementary coalition inequalities force all receivers to agree and donors to solve Ay=t1. The lower-envelope core is exactly the segment between disjoint-support generators (H,d;0^r) and (0;1^r), where H=r-sum d>=1.
3. **Scale choice.** A 2m-by-2m incidence system encodes the Fibonacci recurrence with positive solution minimum 1/F_(m+1), sum m. Taking m=4ceil(log_2 n), r=n-2m-1 yields the required construction for every n>=128 and the explicit bound in Theorem 1.

Both selectors are already unique at their first stages. Thus later lexicographic tie-breaking does not create an unverified obligation. Scaling by the Fibonacci denominator gives integer-valued exact games with polynomial total and logarithmic bit length per generator coordinate.

## Independent corroboration

`THREE_GENERATOR_PROOF.md` gives a second all-parameter route. With q=(k+1)m-k+2, n=m+k+r+3, it gives rho=2-2(q+r+1)/(rq+m+1) under k>=1, m>=max(2,2k-2), r>=3. Its k=1 case recovers the frozen PXC151 construction; fixed-k optimization yields 2(1+1/sqrt(k+1))^2. Growing k proves the same sharp asymptotic constant.

The verification scripts use all coalition inequalities generated directly from the raw vectors. They do not impose the desired support equalities as additional assumptions. The main and secondary families have exact finite selector and uniqueness checks. The original convex-hull proposal is analyzed in `COALITION_CLOSURE_CONTROL.md`; it fails to preserve separation, which motivated controlling the entire core.

## Questions for a specialist

- Is an equivalent sharp quantitative separation theorem already known under another name or normalization?
- Is the segment-realization lemma already standard in the theory of exact cores, positive solutions of incidence systems, or balanced collections? The elementary exactness argument itself is not claimed as new.
- Are there hidden restrictions in the standard solution-concept definitions that would change this extremal class?
- Does the result address a recognized question about disagreement between fairness criteria, or is its significance principally as an explicit extremal example?
- Which natural subclass of exact games offers a substantive extension: assignment-game cores, other combinatorial cores, or a structural characterization of when both selections agree?

## Checked neighboring literature

These primary sources provide context, not a proof of novelty:

- [Vazirani, Fair Core Imputations for the Assignment Game](https://arxiv.org/abs/2402.11437): fairness concepts and algorithms in assignment-game cores.
- [Gangam et al., Equitable Core Imputations for Max-Flow, MST and b-Matching Games](https://arxiv.org/abs/2403.06037): equitable selections and algorithmic results for Owen sets.
- [Studeny and Kratochvil, Facets of the cone of exact games](https://arxiv.org/abs/2103.02414): established exact-game cone geometry.
- [Schoot Uiterkamp, A Characterization of Simultaneous Optimization, Majorization, and (Bi-)Submodular Polyhedra](https://doi.org/10.1287/moor.2023.0054): structural characterizations of simultaneous optimization and majorization.

A targeted search did not locate an equivalent quantitative theorem. That screen cannot certify novelty, and the two algebraic constructions do not establish field-wide significance by themselves.

## Assessment and recommended direction

The original constant hunt is now resolved internally. The earlier 3+2sqrt(2) benchmark was a local restriction of its family, and the two new mechanisms escape it. The structural realization lemma is the most reusable contribution; the computation supports it rather than constituting the contribution.

Prioritize specialist correctness and prior-art review of this short package. The strongest next internal question is whether comparable separation can occur in a natural combinatorial class, or whether a recognizable structural condition forces agreement or a smaller gap. A second-order optimization of the O(log(n)/n^2) term is available, but should be pursued only if it produces further structure. Do not resume the historical packet classifications merely to add cases to a settled first-order constant.

This packet is prepared for review; it has not been sent to anyone.
