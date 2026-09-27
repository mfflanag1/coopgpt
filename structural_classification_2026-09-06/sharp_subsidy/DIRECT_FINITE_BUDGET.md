# Coupled-count verification of the finite donor budget

2026-09-07. This closes the incomplete finite-budget verification route recorded in SHORTFALL_IDENTITY_AUDIT.md. It does not change the global bounds or replace external review.

## Exact reduction of the counterexample query

Use the previously verified raw-capacity identity. Set a=1/h, B=ell/h, x_s=L_s/h and t=4/5+a/20. Then the total normalized shortfall is

    sum_s max(0,f(x_s)),
    f(x)=x(B-x)-B(1-t)-a(x+B).

For any three real numbers, sum of their positive parts equals the maximum of their eight subset sums. Thus it suffices to bound every subset sum. The count domain and parameter are invariant under sector permutations, so the three nonempty subset sizes q=1,2,3 represent all seven nonempty subsets, not a sampling of them. The empty subset follows from nonnegative donor budgets.

Normalize the degree-three donor count by h. Connectedness and nonnegative counts require

    n3/h >= max(0,B-1-a).

For this finite parameter t is independent of n3 and 2-t>0; replacing n3/h by its minimum can only lower the available budget. Splitting at B=1+a removes the remaining maximum. The resulting six exact nonlinear-real counterexample queries retain the coupled variables a,B,x_1,x_2, with x_3=B-x_1-x_2. Each checks

    sum_{s=1}^q f(x_s)
       <= (1-t)(3-2B)+(2-t)max(0,B-1-a)

on its complete branch. All six returned UNSAT.

## Coverage of the original integer count domain

For h>=3, 0<a<=1/3. Each sector satisfies x_s>=0, x_s>=B-1 and x_s<=1. If L_s<h, integrality gives x_s<=1-a. These are precisely the main continuous-domain restrictions used by the verifier; allowing nonrealizable intermediate real counts strengthens the tested assertion.

If any L_s=h, the incidence identities force B=1 and the other two L counts to zero, as proved in SHORTFALL_IDENTITY_AUDIT.md. All shortfalls vanish in that exceptional branch. If h=2, t=33/40<1 and delta=max(0,t-1)=0, again giving no shortfall. Nonnegative donor budgets cover both cases. Together with the raw-capacity identity, the six queries therefore cover every count branch used by the finite all-size construction. The previously established capacity and pair-domination arguments then apply.

## Reproduction and honest status of other queries

Run `verify_shortfall_identity.py --smt` and `verify_finite_budget_direct.py --smt` using the configured research Python. The first connects original capacities to f. The second tests the coupled count domain directly, without replacing sector dependence by the quadratic F_q estimates in the written proof. It fails on UNKNOWN, verifies all six branch labels, and detects a deliberately zeroed donor budget with a SAT negative control.

The same initial split also tested localization. Its three B<=1 queries returned UNSAT, but all three B>=1 queries returned UNKNOWN at their declared eight-second limits. Those do not verify that half of the localization budget. EXTREMAL_LOCALIZATION.md continues to rely on its conventional proof, coefficient checks and earlier eight scalar implications. The two unsplit 20-second timeouts remain historical facts, not mathematical counterexamples. The new discovery source and complete outcome log are archived in discovery/split_budget_audit.zip.

This is verification progress for the finite correction, not a stronger value of S_3, a new extremal family or completed independent specialist review. The sharp goal remains active and the Claude-login request is still pending.
