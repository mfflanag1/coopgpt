# Adding a hub requires changing existing certificate weights

Date: 2026-09-07. Exact obstruction to a specified joining rule, with sharp rational control. The universal sharp constant and novelty remain unresolved; 1/3 <= S_3 <= 2/5.

## 1. The old certificate and the extension

Start with m=7 and P-teams

    e0=(0,1,2), e1=(3,0,4), e2=(5,6,0).

Label 0 is the only hub. At each of the twelve unmatched leaf players, assign weight 1/4 to all three P-teams and 3/4 to every nonroot diagonal. Send extra mass 1/2 to the root and 1/8 to each of the two sector-used leaves. Complete each destination equally with the three other unmatched players of the deletion sector. These are exact fractional deletion packings. Sector balance holds, E=0, R=3, and every leaf deficit is 1/2. HUB_EXTENSION_OLD_CERTIFICATE.json retains all coefficients, checked independently.

Turn leaf label 1, used in sector 1, into a new hub by adding

    e3=(1,7,8), e4=(10,9,1).

The enlarged tree has m=11, two hubs, nine leaves, and no degree-two labels. Every leaf type in each block is unique, so the block model introduces no within-type symmetry restriction here.

The attempted joining rule preserves every old P weight p_(i,e)=1/4 for each surviving old deletion root i and e in {e0,e1,e2}. It may change all transfers, all new-team weights, and all new-root rows. The surviving roots are the two unmatched players at each of labels 2,3,4,5,6, a set O of ten rows.

We retain the same-sector, E=0, maximal-diagonal and sector-balance restrictions of the established tree certificate model. We do not impose R=4 or prohibit hub transfers in the main theorem.

## 2. Sharp rebalancing inequality

**Theorem.** Every certificate for the enlarged support in this model satisfies

    W := sum_{i in O} [5 p_(i,e0)+p_(i,e1)+p_(i,e2)] <= 17.      (1)

The bound is attained by REBALANCING_SHARP_CERTIFICATE.json, a full rational certificate with 332 entries. The preserved old weights would give W=10*(7/4)=35/2, violating (1). Hence this old certificate cannot be extended while preserving all surviving old P weights, even after relaxing the minimum-root-mass equality condition.

The required change is quantitative:

    sum_{i in O,e<=2} w_e |p_(i,e)-1/4| >= 1/2,
    with (w_0,w_1,w_2)=(5,1,1).

Consequently the total unweighted absolute change in these thirty entries is at least 1/10, and at least one entry must change by at least 1/140. These are lower bounds, not claims of sharpness of the displacement measures.

The theorem concerns certificate weights. It is not a subsidy lower bound, a restriction on the market's core payoffs, or a counterexample to S_3=1/3.

## 3. Exact algebraic proof of (1)

The necessary marginal constraints are precisely those in TWO_HUB_BLOCK_REDUCTION.md: rooted ordering, pair-flow caps, root coverage, row supply, sector balance, leaf coverage and hub coverage. Here each row type represents one actual root. All marginal variables are nonnegative. local_extension_model.py instantiates these constraints for the displayed five teams and also lists the thirty optional fixed-weight equations 4p=1.

LOCAL_EXTENSION_DUAL.json gives 73 rational multipliers. Inequality multipliers are nonnegative; equality multipliers may have either sign. Combining them including the thirty fixed-weight equations gives

    a nonnegative linear expression <= -1,

an exact contradiction. More usefully, remove those thirty fixed-weight equations from the combination. The remaining valid constraints give

    2 W + Q <= 34,

where every coefficient of Q is nonnegative (there are 34 nonzero coefficients, all 2 or 4). Since every marginal variable is nonnegative, Q>=0 and (1) follows.

`verify_hub_rebalancing.py` regenerates the rational constraints and checks both algebraic combinations coefficient by coefficient. It does not use a numerical solver, tolerances, or the reported optimization status. It then independently checks every capacity, exclusion and pair coefficient in the full attaining packing, extracts its marginals from those entries, verifies all unfrozen marginal conditions, and checks W=17. This supplies a finite exact linear-certificate proof of the sharp cut, rather than a floating infeasibility claim.

## 4. A short explanation on the R=4 face

There is a simpler contradiction for the stronger proposed joining rule that also keeps R at its minimum 4. By ROOT_MASS_BALANCE.md, all supplies are used, every hub receives zero extra mass, and each leaf pair has exactly its deficit in extra coverage.

Consider the four surviving old rows with deletion sector 1, rooted at labels 2,3,4,5. Each still has P weight 1/4 on the old three teams and root extra mass 1/2. Let q3,q4 be that row's weights on the two new teams. Its source supply is 3/4+q3+q4. Besides its root, its only possible extra destinations are label 6, of capacity 1/4, and the new sector-1-used leaves 7 and 9, of capacities q3,q4. Thus exhausting the row supply forces mass 1/4 to label 6 in every such row.

Those four rows alone send total one to the pair at label 6 missing sector 1. Yet the two root rows at label 6 retain weights 1/4 on their old incident team, so its deficit is only 1/2. This contradicts exact leaf coverage. The general cut in Section 3 extends the obstruction beyond the R=4 face.

## 5. Positive controls and research consequence

The old uniform one-hub certificate is valid. The enlarged tree has valid certificates when its old weights may change: the sharp-cut control attains W=17, and HUB_EXTENSION_CONTROL.json attains R=4 with 366 independently checked entries. These controls distinguish failure of a joining rule from failure of certificate existence.

A numerical campaign tested 120 deterministic random-tree inputs with r=12,24,40 and seeds 0 through 39. Two zero-hub inputs were skipped because R=g+2 is impossible there. All 118 remaining inputs, including examples with seven hubs, were feasible with R=g+2. This is nonexhaustive floating evidence only. Separate numerical extension tests failed at all 19 leaf choices in the two retained two-hub seeds when surviving old weights were frozen, while all 19 were feasible when unfrozen. Those results motivate the exact smaller example above; they are not an exhaustive theorem about extensions.

A viable composition proof must allow rebalancing inside the existing tree, or use a different invariant/model. Two variants of the frozen-weight extension failed: preserving R at equality and allowing arbitrary R. Retire that joining rule. The next mathematical target is a controlled rebalancing operation that proves all marginal inequalities remain feasible; simply asserting that the old and new certificates can be combined is insufficient.

No external review has been performed. A local review packet can be prepared, but unavailable reviewer authentication is not proof verification. No purchases or outreach occurred.
