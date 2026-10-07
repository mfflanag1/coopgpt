**Provisional verdict: no invalid step found in reviewed scope.** Most notable gap: BASE_FLOW_DOMINATION line 17's `2U(K)` alternative depends on an unstated "previously proved base budget" that is not in the packet and `U(K)` is undefined there; the `L*T` half is self-contained and correct.

## Findings

**1. (Low) Unverifiable external dependency — BASE_FLOW_DOMINATION.txt:17, 34–35.**
`sum_e r_e <= 2U(K)T` is derived from `r<=2z` plus a base budget `sum z <= U(K)T` not supplied. Verification: supply or cite the prior statement with its exact hypotheses. The `L*T` branch (path decomposition, each path has ≤L edges, total ≤T) is valid.

**2. (Low) Measurability of f(X) asserted, not argued — BASE_FLOW_DOMINATION.txt:7.**
`fbar=2E f(X)` requires a measurable selection. The lexicographic optimizer on the optimal face is plausibly measurable (closed-valued Borel correspondence), but no argument is given. Only `E f_e(X)` enters; a one-line justification would close this.

**3. (Informational) Concavity argument is redundant but correct — BASE_FLOW_DOMINATION.txt:23–28.**
Explicitly, `g(u)=min(A+uD_e,B)-min(A,B)=min(uD_e,(B-A)_+)`, so `∫g = a - a²/(2D_e)` with `a=min(D_e,(B-A)_+)`, giving formula (1) `r_e=E[2a-a²/D_e]` exactly, and `a/2 ≤ ∫g ≤ a` since `a≤D_e`. Checked: at `a=D_e` both give `D_e`; `B=∞` gives `r_e=D_e`.

## Verified steps

- `m_e(X)≤f_e(X)` simultaneously: path decomposition in a DAG, each path uses e at most once; removing e-paths leaves a flow of value `F(X)-f_e(X)` feasible with `x_e=0`. Correct.
- `g(1)=min(D_e,(B-A)_+)` matches THEOREM.txt (4); `E g(1)=z_e`. Correct.
- `fbar` feasibility: `f_e≤D_eU_e ⇒ 2E f_e ≤ D_e`; conservation linear; `maxflow(D)=T` (THEOREM §2) gives antichain bound `sum_A fbar ≤ T`. Correct.
- Cross-substitute example: h=0 → `z_e=Pr(U_1+U_2>U_e)=1-1/6=5/6`. h=1 → `D=(1,1,2,2)`, `Pr(2W≤S)` for iid triangular S,W = `1/32+11/96=7/48`, so `z_e=41/48`. Both constants confirmed; `41/48>5/6`.
- SERIES §1: minimal cut meets X in ≤1 edge (no internal attachments); argmin of iid uniforms independent of min and externals; every owner's unilateral reports realise bottleneck exactly `[0,q]`; `Z_X(q')≤d(q')≤d(q)≤T`. Correct. Beta(1,k) for min of k uniforms correct.
- SERIES §2 constants: `T_i=1,K_i=2,K=2r`; standalone total `1+(m-1)Pr(H<L)≤1+(m-1)/m!≤2` (simplex volume `1/m!`, m≥2). Composition: `Pr(H_i≤1/4)=4^{-m}/m!=1/r`; `1-(1-1/r)^r≥1-1/e>1/2`; `Var L_i=1/(12M)`; Chebyshev `≤16/(12M)=4/(3M)`; union `r·4/(3M)=1/12`; net `5/12`; payout `m` when heavy cut wins. All correct. Own-monotonicity on relevant intervals: light underreport leaves other light caps `1/M` (since `(M-1)/M≥1/M`), heavy caps `min(1,T')` nondecreasing, A fixed; heavy underreport leaves T=1 since `m-1+t≥1`. Correct, so `y=z`. `m~log K/log log K` correct.
- SERIES §3: `D_e=min(d_{i,e},T)` by restrict-to-e-paths/scale argument; cut family disjoint union. Correct.

## Scope limitations

Cannot verify the "previously proved base budget"/`U(K)` definition, the earlier TTSP co-cut theorem, or THEOREM.txt's own correctness beyond what these files use (formula (4), `maxflow(D)=T`). Frozen-deletion truthfulness is explicitly open and not assessed. No tests run.

## Verdict

No findings of invalid steps or missing quantifiers in the reviewed claims; two low-severity completeness gaps (items 1–2). Numeric constants (5/6, 41/48, 1/r, 4/(3M), 1/12, 5/12, bound 2) all check.
