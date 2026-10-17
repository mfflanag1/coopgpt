**Provisional verdict: no findings in reviewed scope** (lift identity and 3/2 transfer check out); one Low-severity evidence gap on the "sharp uniform constant" sentence.

## Findings

**[Low — unsupported sub-claim] `UNIVERSAL_RATIONAL_WEIGHT_LIFT.txt:22-24`.** The statement that "root's separately audited general-mechanism lower theorem makes 3/2 the sharp uniform constant" relies on a document not in the packet, and the included dependency `HUBER_PRICE_THREE_HALVES_v2.txt:33` explicitly disclaims optimality over all mechanisms ("No claim of optimality over all eligible mechanisms is made"). Within this snapshot, 3/2 is established only as (i) an upper bound for the lifted Huber rule and (ii) the rule-specific supremum (Huber v2 §RULE-SPECIFIC SHARPNESS). Verification: attach the lower theorem or downgrade line 22-24 to "rule-specific sharpness; general lower bound pending."

No mathematical errors found in the lift or transfer. Traced steps:

- **Primal (lines 37-43).** For edge uv, profit w, the w lifted edges {(u,a),(v,w-1-a)}, a=0..w-1, touch each copy of u and of v exactly once, so load at (v,a) ≤ Σ_{e∋v} x_e ≤ c_v; lifted value = Σ w_e x_e. Correct, including zero c_v (forces x=0 on both sides).
- **Dual (lines 45-59).** Clipping at W: if p_u>W then p_u+p_v ≥ W ≥ w_uv, so feasibility and optimality are preserved. For a+b ≤ w−1, (p_u−a)+(p_v−b) ≥ 1. Clip lemma: if both s,t<1 and s+t≥1 then s,t>0, so clipping is the identity — correct. Telescoping Σ_{a=0}^{W-1} clip(p−a) = ⌊p⌋ + frac(p) = p for p∈[0,W] (p=W gives W ones) — correct. Weak duality on H plus strong duality on G gives F_H(Bc) ≤ F_w(c). Nothing in the argument uses bipartiteness; I sanity-checked a triangle with profits (2,1,1), unit capacities: F_w=2, lifted H (W=2, 5 edges) has fractional matching 2 and cover {(a,0),(b,0)} of cost 2.
- **Rational scaling (62-64), edge count w(w+1)/2, size O(nW+mW²), pseudo-polynomial disclaimer (80-88):** correct and appropriately hedged.
- **No strategic cloning.** B is a fixed 0/1 matrix applied to each actual owner's bundle; owner set unchanged, no report-independent capacity (c_v=0 ⇒ all copies 0). Lifted coalition bundle = B·Σ_S b_i by linearity, so Huber coverage gives Σ_S P_i ≥ (1/q)F_H(BΣ_S b_i) = F_w(Σ_S b_i).
- **Monotonicity transfer (69-78).** A withholding by i changes all W copies of each withheld v simultaneously (a correlated lifted change). This is covered because Huber v2 Lemma 4 / Corollary (lines 128-130, 156-162) chain single-coordinate nondecreasing steps into arbitrary coordinatewise increases, with outsiders' lifted reports fixed. Funding bound divides by q.

I could not construct a counterexample: the transfer is black-box, so any failure would have to be a failure of unit-Huber on H itself.

## Scope limitations

- Huber v2 treated as a dependency per instructions; I spot-checked derivatives (5),(6) and KKT (3) (algebra correct) but did not re-audit Lemma 1's simultaneous perturbation, Lemma 4's piecewise-rational/connectedness argument, or Lemma 5's ε-regularization limit in full.
- Referenced files (`root/OUTSIDE_PRODUCTION_BOUNDS.txt`, the general-mechanism lower theorem, the 20,528-profile sweep) are not in the packet; nothing was executed.
- Irrational profits are explicitly out of scope (line 87-88); agreed.

## Verdict

**No findings in reviewed scope** for lift correctness and the 3/2 coalition-total-monotone transfer; **insufficient evidence** for the mechanism-independent sharpness sentence at lines 22-24.
