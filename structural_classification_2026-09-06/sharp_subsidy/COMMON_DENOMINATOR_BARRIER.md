# A common affine normalization cannot cover independent leaf growth

Date: 2026-09-07. Conventional barrier theorem for a specific family of certificate formulas, with exact computational corroboration. Global bounds remain 1/3 <= S_3 <= 2/5. Novelty and external review are unconfirmed.

## 1. Statement and scope

Fix either two-hub block skeleton from TWO_HUB_BLOCK_REDUCTION.md, with any fixed admissible baseline leaf counts. Write its 15 independent nonnegative integer count increments as q_bt. Consider the compressed, sector-balanced, leaf-only, E=0 certificate model of that note. For a row type k=(b0,t,s), with multiplicity n_k=L_b0,t, define aggregate variables

    X_kb = n_k p_kb,       F_kb = n_k f_kb.

Absent row types have zero aggregates. Suppose every X and F has an affine numerator in all increments divided by the same affine denominator D, which is positive throughout the nonnegative orthant. Root and hub extra masses may be chosen arbitrarily; they need not have this form.

**Theorem.** If D has a strictly positive coefficient for any leaf-count increment, such a formula cannot give feasible certificates for every admissible count array.

In particular, normalization by total leaf count fails in both port configurations, even if every baseline leaf count is positive. The theorem excludes arbitrary affine numerators, not merely the coefficientwise sufficient search used in discovery. It does not exclude piecewise, nonlinear, or differently normalized formulas, and does not refute pointwise feasibility or the one-third conjecture.

## 2. Necessary relations

Write A_kb and B_kb for the affine numerators of X_kb and F_kb. Fix a block b and deletion sector s. Let J_s denote all row types with deletion sector s. Sector balance and leaf-flow capacity imply

    sum_{k in J_s} A_kb = D,
    Delta_k := A_kb-B_kb >= 0.                     (1)

Each A_kb and Delta_k is affine and nonnegative on the nonnegative integer orthant, so its constant and linear coefficients are nonnegative. This elementary implication follows by sending one integer coordinate to infinity with the others zero.

Let x=q_bs, let ell be its baseline count, and let k1,k2 be the two deletion types rooted at a sector-s-used leaf in b. The residual-pair coverage condition, multiplied by (ell+x)D, is

    (ell+x) sum_{k in J_s} B_kb + A_k1,b+A_k2,b
       >= (ell+x)D.

Using (1),

    (ell+x) sum_k Delta_k <= A_k1,b+A_k2,b.        (2)

The right side is affine. Therefore every linear coefficient in sum_k Delta_k is zero. For the coefficient of x, send x to infinity. For any other coordinate y, set x=y=N and send N to infinity. A positive coefficient on the left would give quadratic growth, while the right grows at most linearly; nonnegative coefficients prevent cancellation. By (1), each individual Delta_k has nonnegative coefficients, so **every Delta_k is constant in all increments**.

This argument remains valid when ell=0: apply coverage at positive x. It also holds when all baseline types are present.

## 3. Two row types force a contradiction

Choose x=q_bs with positive denominator coefficient alpha. Let t be either of the two sectors different from s, set y=q_bt, and set every other increment to zero. Let k=(b,t,s), whose multiplicity is n_k=n0+y, and let k* be its partner deletion type at the same root. On this plane write

    D=d+alpha*x+beta*y,
    A_kb=a0+a_x*x+a_y*y.

Aggregate root coverage requires Z_k>=n_k-X_kb-X_k*b. Aggregate row supply, after dropping nonnegative hub demands, consequently requires

    n_k D <= sum_c r_c A_kc - sum_c L_cs B_kc
               + A_kb + A_k*b.                   (3)

Only r_b and L_bs vary on this plane: r_b=r0+x+y and L_bs=ell+x. All other coefficients r_c,L_cs are fixed. Since Delta_k=A_kb-B_kb is constant by Section 2,

    r_b A_kb - L_bs B_kb
      = r0 A_kb - ell B_kb + x Delta_k + y A_kb.

Thus the quadratic part of the right side of (3) minus its left side is

    (a_x-alpha)xy + (a_y-beta)y^2.                (4)

There is no x^2 term. Feasibility for every nonnegative integer x,y forces a_x>=alpha. Otherwise choose a sufficiently large fixed positive integer M, set x=MN and y=N, and let N grow. The coefficient of N^2 in (4) becomes negative, contradicting (3), whose remaining terms grow only linearly.

Apply this argument separately to t equal to each of the two sectors other than s. The two distinct row types in J_s each have x-coefficient in their A_kb of at least alpha. But sector balance (1) gives

    sum_{k in J_s} coefficient_x(A_kb)=alpha.

All terms are nonnegative, so the left side is at least 2alpha>alpha. Contradiction.

This proves the theorem. It uses necessary inequalities, not a coefficientwise sufficient relaxation. A positive constant denominator can also be excluded: sector balance and nonnegative affine numerators force all A coefficients to vanish; taking each of the two root-type counts to infinity then forces two distinct constant A_kb values to be at least D, again contradicting sector balance. Consequently a common positive affine denominator, constant or nonconstant, cannot cover all these independent count directions.

## 4. Computational corroboration and its limits

The initial search imposed nonnegative affine coefficients and coefficientwise nonnegativity of every cleared polynomial inequality, with D equal to total leaves. It also used the sufficient choice Z_k=n_k-X_kb-X_k*b>=0. This is a narrower model than the theorem.

Both minimal-baseline models were infeasible. Exact Farkas combinations use eight constraints in the different-port case and thirteen in the same-port case. Each combines to an inequality with nonnegative variable coefficients and right side -1, impossible for nonnegative coefficient variables. AFFINE_BLOCK_DUALS.json retains the multipliers. The standard-library verifier regenerates the coefficient systems and checks the sign of every resulting coefficient and the strictly negative right side exactly. These checks verify the computational model; Sections 2-3 supply the broader conventional proof.

A second discovery variant raised every baseline leaf count to at least one. Both cases again returned numerical infeasibility. No separate exact dual is claimed for that run, but the conventional theorem now covers its shared-affine hypothesis as well.

A separate deterministic numerical stress test found pointwise feasible compressed solutions in 500 cases (250 per port type), including increments of 1000. It is discovery evidence, not exhaustive coverage, an exact feasibility theorem, or proof of novelty. Outcomes are retained in discovery/BLOCK_STRESS_RESULTS.json.

Run `python3 -O verify_affine_block_barrier.py` for exact dual verification. Optional discovery scripts require SciPy. The exact verifier requires only the standard library and rejects an empty dual.

## 5. Research consequence

Retire common affine normalization across independent leaf-count directions, including attempts to repair it merely by making all baseline counts positive. The next candidates are sector-dependent normalization with nonlinear root coupling, or a convex argument selecting weights jointly. This theorem does not show that either candidate succeeds.

The remaining goal still requires arbitrary-count feasibility or an actual market obstruction, a transferable composition argument, and resolution of cyclic supports. No global bound changes here, and no field-level breakthrough or novelty is claimed.
