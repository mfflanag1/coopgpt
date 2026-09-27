# Exact rejection of the single-baseline local P-weight rule

Date: 2026-09-07. Global bounds remain 1/3 <= S_3 <= 2/5. This result rejects a specific certificate ansatz, not the universal one-third conjecture.

## The rule being rejected

For the existing junctions(16) pattern, m=67, |P|=33, h=34 and u=102. For a P-team e let Q_e be the number of unmatched players whose diagonal label occurs in e. In this pattern Q_e is 2 or 4. Consider a single common baseline b and weights

    p_{i,e}=b+(3-u b)/Q_e  if label(i) occurs in e,
    p_{i,e}=b              otherwise.

These automatically give sum_i p_{i,e}=3. Permit arbitrary feasible same-sector diagonal and pair-block marginals from VARIABLE_P_DIRECTION.md; the rule constrains only the P weights. Thus the rejection is not caused by fixing a particular diagonal transfer recipe.

**Exact bounded-pattern result:** the pair-coverage parameter for this rule is at most

    993043032491/1000000000000 = 0.993043032491 < 1.

Consequently this rule cannot give the desired one-third certificate, whose parameter is 1, even on this specified tree. The numerical optimizer searched the usual increasing-nearby-weight range 0<=b<=3/u. The retained exact upper certificate uses only the weaker valid bound b<=1, so the rejection also covers feasible nonnegative baselines outside that numerical search range. Remote rows impose p=b<=1. Parameter t is considered in [0,2], which includes the target 1.

This does not reject all incidence-based formulas, edge-dependent baselines, globally coupled weights, cross-sector transfers, or the actual frozen-ideal subsidy bound.

## Marginal LP and calibration

The transportation lemma permits an LP with variables p_{i,e}, d_{i,j}, q_{i,j}, and R_i. The row residual source capacity is

    R_i=m-1-sum_e p_{i,e}-sum_j d_{i,j}.

The total residual demand inequality is equivalently sum_j q_{i,j}+sum_e p_{i,e}<=m-1. The singleton cut is

    q_{i,j}-2d_{i,j}+A_{i,j}<=R_i,

where A is the remaining sector-player capacity defined in VARIABLE_P_DIRECTION.md. The interval constraints on d,q and aggregate coverage are unchanged. Adding the displayed local rule gives the model certified here.

The marginal model has 17,138 variables and 37,974 equality/inequality rows at m=67. On smaller patterns it reproduces the earlier direct packing optimizations. Separately, verify_marginal_extraction.py extracts exact marginals from the retained rational packing certificates and verifies all interval, total-flow, singleton-cut and coverage conditions on 102 deletion rows at m=11,19,35. This calibration checks the model translation; it is not a general feasibility theorem.

## Exact dual verification

MARGINAL_LOCAL_16_DUAL.json records rational inequality and equality multipliers at denominator 10^12. verify_local_rule_dual.py reconstructs the model coefficients, without SciPy or a solver, and checks the weak-duality upper bound with integer arithmetic at common denominator 4*10^12.

For max c.z subject to A.z<=a, E.z=e and 0<=z<=M, arbitrary lambda>=0 and unrestricted nu give

    c.z <= lambda.a+nu.e
           + sum_j M_j max(0,c_j-(A^T lambda+E^T nu)_j).

The verifier uses M=1 for p,d,q and b, M=m-1 for R, and M=2 for t. These bounds follow from the displayed model or the target parameter interval. Its exact positive-residual correction is 609/250000000000. The resulting upper bound is strictly below 1, as stated above. An empty-dual negative control fails. No floating tolerance is used to conclude impossibility.

The explicit P array in the certificate defines the fixed case. The verifier checks matching disjointness, dimensions and all coefficient identities used by the bound. The conventional construction junctions(16) supplies its tree interpretation.

## Completed discovery and the next direction

The unrestricted marginal model returned floating parameters 1+1/m for junction counts 2,8,16. The local formula returned approximately 1.083110, 1.009443 and 0.993043. Only the retained exact dual supports the impossibility claim above; the numerical unrestricted 16-junction solution is not yet promoted to an exact certificate or a universal theorem.

All six comparison runs and the dual-export rerun completed. No solver process remains pending. The optional generator is discovery/marginal_probe.py; its default reruns the 16-junction local case and exports the dual alongside itself. Independent verification uses the canonical JSON beside verify_local_rule_dual.py.

The earlier fixed-baseline failure and this optimized single-baseline failure rule out pursuing that same formula as a universal mechanism. The next proof attempt should derive P weights from broader incidence structure, such as cut-dependent or tree-recursive allocations, and use the proven transportation conditions to realize them. Global sharpness and the free-original novelty audit remain unresolved.
