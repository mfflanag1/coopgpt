# Direct audit of the row-capacity identity

2026-09-07. Verification progress, not an improved bound. Independent Claude review is still unavailable: a fresh `claude auth status` returned loggedIn=false, authMethod=none. The user has been asked to sign in locally; no credentials were requested and no login was performed on their behalf.

## Original capacities and exact identity

Let a=1/h, beta=1-a, delta=max(0,t-2a), B=ell/h and x=L_s/h. The proportion of unmatched degree-two rows in this sector is n=1-B+x. Dividing the ORIGINAL capacity shortfall by h gives

    raw=max(0, x delta
               - n min(x,beta)
               - (1-n) min(x,beta-delta)).

For every admissible count configuration and every 0<t<1,

    raw=max(0, x(B-x)-B(1-t)-a(x+B)).

This checks the identity used in FINITE_UPPER_CORRECTION.md and EXTREMAL_LOCALIZATION.md without assuming which sectors need extra transfer at either the old or the new parameter.

## Domains, including the easily missed branch

The verifier uses a continuous superset of the actual normalized counts:

    0<a<=1/2, 0<=B<=3/2, 0<=x<=1, 0<=1-B+x<=1,
    either x<=1-a, or (x=1 and B=1).

The final alternative is justified by integer L_s: if L_s<h then L_s<=h-1. If L_s=h, the other two sectors each have at least ell-h used leaves by N_r/h=1-B+x_r>=0, while their total used leaves is ell-h; hence ell=h and B=1. Thus the large-column branch is included, not omitted. The single-sector continuous domain need not itself describe a realizable graph; proving the identity on this larger domain is sufficient.

A direct conventional check is also short. For x<=beta, if delta=0 both shortfalls vanish: beta-delta=beta and x<=1-t+a. If delta>0 set b=beta-delta=1-t+a. When x<=b, raw is zero and the polynomial is x(B-x-a)-Bb<=-x(x+a)<=0. When x>b, expanding the original capacities gives the displayed polynomial exactly. In the remaining branch x=B=1, n=1: raw=max(0,delta-beta)=0 because t<1, and the polynomial t-1-2a is negative.

## Exact check and failed direct queries

`verify_shortfall_identity.py --smt` asks for a counterexample using exact nonlinear real arithmetic. The result is UNSAT. It then changes the claimed expression by adding one; a counterexample exists (SAT), exercising a negative control. UNKNOWN is an error in this verifier, never acceptance.

Before isolating this identity, two broader queries encoded the full three-sector raw budget directly, once for the finite parameter and once for the localization parameter. Both returned UNKNOWN after their declared 20-second time limits. They establish neither validity nor invalidity of the complete raw-budget assertion. Their source and outcome are retained in discovery/direct_budget_audit.zip. The completed identity audit is distinct from those incomplete queries. The written budget proofs and their earlier scalar checks remain the support for the full budget conclusions.

## Status

The branch identity is now verified over a larger continuous domain and all parameters 0<t<1. This addresses a concrete verification concern in the two new all-size arguments. It does not supply a size-uniform improvement below 2/5, complete expert review, or establish novelty. The primary sharp-constant goal remains active.

Follow-up: DIRECT_FINITE_BUDGET.md completes the finite-parameter coupled-count budget check by an exhaustive active-subset split. The corresponding direct localization branch remains incomplete.
