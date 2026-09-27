# A prescribed cycle-pair boundary need not preserve the obstruction optimum

2026-09-07. Exact bounded counterexample to an auxiliary reduction; global bounds remain 1/3 <= S_3 <= 2/5. No novelty or external-review claim.

## Claim tested

For a unicyclic diagonal/P incidence support, choose a pair joining the two cycle labels in one P-team. Can the maximal fixed-P obstruction always be preserved while setting that particular pair weight to zero and reoptimizing every other supported pair weight?

**No.** This is a stronger allowance than merely deleting the weight in a fixed market. It still fails for a prescribed edge. The existential claim that some suitable edge can be chosen is not disproved.

## Exact counterexample

There are six labels, with sector-ordered partial matching

    P = [(1,0,2), (3,4,1), (0,5,4)].

The alternating incidence cycle runs through labels 1,0,4. Its three corresponding pair coordinates are AB(1,0), BC(4,1), and AC(0,4). Normalize original diagonal worth to T=1, keep every supported pair nonnegative, and require original core feasibility. The retained unrestricted primal gives

    F(P) >= 2/9.

Now require AC(0,4)=0, while freely optimizing all remaining pair values and retaining separate original-core witnesses for the unmatched ideals. The new exact dual proves

    F(P | AC(0,4)=0) <= 58/267 < 2/9,
    2/9 - 58/267 = 4/801.

Therefore no admissible choice of the other weights on this fixed support recovers the unrestricted obstruction lower bound after imposing this zero coordinate. This is an exact statement over all nonnegative real pair weights, not a finite grid search.

The coordinate restriction does not itself remove the hypergraph incidence cycle: the other two pair entries of that P-team remain. Do not describe this as a theorem about all genuine cycle-opening transformations, vertex splitting, changing P, or changing the number of labels. It rejects only a prescribed-coordinate boundary reduction on the original support.

## Verification

`verify_cycle_boundary.py` independently reconstructs all supported pair coordinates and full-team inequalities. It checks the existing unrestricted rational primal using the retained fixed-pattern verifier. The restricted upper certificate uses independent original-core witness blocks, nonnegative team multipliers and free total multipliers. It computes each residual objective coefficient exactly. Positive residuals are bounded by the valid coordinate bounds x<=1 and pair weights<=1; the forced-zero coordinate contributes zero. This proves the claimed upper by weak duality. No floating data or solver status is accepted as proof. An empty-dual negative control is rejected under optimized Python execution too.

Run `python3 -O verify_cycle_boundary.py`. The discovery driver, all four probe records and the exact certificate are archived. Discovery at r=2,3,4,6 found at least one alternative cycle pair whose zero restriction numerically preserved the optimum in every tested support. Those observations are not an existential all-support theorem, and the restricted 58/267 upper is sufficient for the counterexample without asserting exact restricted attainability.

## Decision

Retire the arbitrary prescribed-edge rule. Any boundary-based proof needs a selection lemma or an explicit loss term. Choosing the edge with maximal retained optimum simply restates another optimization problem unless a structural reason bounds that loss. Do not expand to more sampled supports without a falsifiable selection rule. This counterexample leaves the original one-third inequality and the primary sharp-constant goal unresolved.

Follow-up: ADAPTIVE_BOUNDARY_LIMIT.md now disproves adaptive zero-pair selection on a different six-label support. The earlier statement that adaptive selection remained open is historical.
