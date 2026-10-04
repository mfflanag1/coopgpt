**Provisional verdict: no blocking findings in reviewed scope.** I could not break the k=3 softmax proof by hand-checking each step from the draft text; nothing was executed. The most important concrete issue is a mis-stated case in the fairness proof, which is repairable from the draft's own argument.

## Findings

**1. Nonblocking (proof wording) — `COORDINATOR_SOFTMAX_DRAFT.txt` L15–16.**
"For a short owner, M_i=c_i" is false when ρ_j=1 arises from capping. Example: a pool with one owner c_i=5 (others zero) and T=1 has C_j=1 and M_i=1=d_i≠c_i.
- The claim still holds: the L16–20 argument with u_j=(m−M_i)/T≥0 covers every owner with M_i>0, including u_j=0.
- Fix: state M_i=max(T−a,0)≤d_i and drop the short/non-short split.
- Verify: test profiles with a capped lone owner in a ρ=1 pool.

**2. Nonblocking (missing self-contained steps) — L12, L37.**
- Coverage cites "the two-pool proof", which is not in the packet. It does check directly: d(S∩N_j)≥min(c(S∩N_j),T), so min_j d(S∩N_j)=v_c(S), and Σ_j p_j d(S∩N_j)≥v(S) since Σp_j=1.
- L37 asserts the kinks without argument. It needs: y continuous in x for T>0, finitely many clip points, and y≤x→0 as T→0 when a=0.
- L33 silently uses x/T≤1.
- Verify: write these three lines into the draft.

**3. Nonblocking (scope of the k=4 stop) — L55–59.**
The witness is correct but refutes only the unit-temperature softmax. My unverified sketch suggests weights exp(−λu) pass the same short-region test when (k−1)e^{λ−2}≤1 (λ<1 for k≥4, feasible up to k=8), with the long-region and fairness steps apparently surviving for λ≤1. Either test this or relabel L58 as "unit-rate softmax".

**4. Nonblocking — L45–46.**
Attainment is stated for k=3 only, which is correct ((2+b)/3≈0.821<1). The three-owner construction needs b<1; larger k needs more owners per pool.

## Steps checked and found correct

- **Fairness:** H_i≤M_i; m≥M_i; t·e^{−t/T} increasing on [0,T]; Z≤k.
- **Long region:** T=B fixed, other weights fixed, derivative p_j[1−(m/B)(1−p_j)]≥0, constant for x≥B.
- **Short region:** y′=p_j[1+xΣp_lρ_l′]; −ρ_l/T≤ρ_l′≤0; the bracket condition reduces to Σ_{l≠j}u_l e^{−u_l}≤1, and 2/e<1.
- **Regime match at x+a=B:** both formulas give x/Z.
- **Budget:** Σy/T=1+F; max of (u−b)e^{−u} is e^{−1−b} at u=1+b; this gives b·e^b=(k−1)/e. For k=3, b≈0.46306<0.4631.
- **Residual-rule witness (L49–53):** at x=1 every pool has u=0, so the payment is 1/3 regardless of which short pool takes the residual. At x=99/100, y≥0.99·0.34=1683/5000>1/3. Valid.
- **k=4 derivative (L55–58):** Z(1)=1+3/e, Z′(1)=6/e, so the left derivative is (1−3/e)/(1+3/e)²<0, and y is constant for x>1. Valid.

## Scope limitations

- All checks are by hand from the draft; no verifier, exact-arithmetic certificate or test output was in the packet.
- CONTRACT L59 requires a fail-closed verifier and review records; none were supplied.
- Novelty, the "written independently" claim, the two-pool 1/(2e) rule and any lower bound were not reviewed.
- The result does not address the CONTRACT target of a k-independent constant. It gives β_3<0.4631 against the baseline (k−1)/2=1.

## Verdict

**Findings, all nonblocking.** The k=3 proof is correct in the reviewed scope after the L15–16 repair, and both failure witnesses are correct as scoped.
