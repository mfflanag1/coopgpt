**Provisional verdict: no substantive findings in reviewed scope.** I re-derived every step of Claims A–E by hand from the packet and found no counterexample or gap. Nothing was executed, and the draft's own exact finite checks remain pending.

## Findings

**1. Low (scope of statement) — Claim C, lines 58–60, 81–83.** The bound is only an asymptotic improvement over the baseline (k−1)/2.
- At k=2, R_2≈3.35, so the bound is about 4.2 against a baseline of 0.5.
- My hand estimate puts the crossover near k≈12.
- Suggested verification: tabulate R_k+1/log R_k against (k−1)/2 exactly, and state the result as min of the two or "for large k".

**2. Low (assumption explicitness) — Claim E, lines 89–96.** The obstruction needs more than the headline says.
- Each pool needs n≥q=√k owners (n divisible by q), so it says nothing about bounded-owner-count classes such as single-owner pools.
- k must be a perfect square; general k needs a floor/rounding argument, which is not written.
- The step p_j(high)=p_j(all 1/n) depends on prices seeing only rho and fixed counts, and on zero capacities; the draft does disclose both.
- The algebra checks: other pools have d=1/n≤x and rho=q, the coalition value is x, and B≥q²/(2q−1)>√k/2. This is a bound on B=1+beta, so beta≥√k/2−1.

**3. Low (exposition) — Claim D, lines 77–80.** "Sharp" is a supremum over owner counts as well as profiles.
- The family needs r~log k/log log k owners per pool.
- A single owner of capacity r gives rho=1 after capping, so the family cannot be compressed to bounded counts.

## Steps checked with no gap found

- **Claim A, coverage:** v(S)=min_j d(S∩N_j) holds because the short pool has d(N_j)=T. The base payment is Σ_j p_j d(S∩N_j) with Σp_j=1.
- **Claim A, R constant:** if a≤B then T(x)≥a≥c_h for every other own-pool owner; if a>B then T≡B. Both cases hold, including a=0 and x=0.
- **Claim A, monotonicity:** d_i(x)=min(x,B), and Y is pointwise nondecreasing under the same U coupling. The identity min(d_i,(Y−R)_+) is correct, including at d_i=0 and the T=0 convention.
- **Claim A/B, M bound:** H_i≤M_i follows from x(N)=T and x(N∖i)≥v(N∖i). M_i=(c_i−δ)_+ holds in both cases A_j≤B and A_j>B.
- **Claim B, top-up:** the per-pool sum is ≤A_j−rδ≤T, so ΣM_i/k≤T, and max(a,b)≤a+b gives the additive T.
- **Claim C, tail:** p_j≤P(X_j/T≤1) uses X_s≤T. Jensen, the product bound and Markov at t=ρ_j are valid. (e/r)^r is decreasing for r≥1, R_k>e is unique, and the tail integral gives R_k+1/log R_k.
- **Claim D, lower family:** the Irwin–Hall CDF u^r/r! on [0,1] is correct. Subsidy is (r−1)(1−p_1), and the top-up is zero for the long pools (M=0 when r≥2).
- **Claim D, quantifier exchange:** for each fixed ε, p_1→0 gives liminf ≥1−ε; then ε↓0 gives liminf ≥1, matching the limsup ≤1 from Claim C. This is legitimate.
- **Sharpness scope:** the claim is correctly limited to this rule, and the draft says the unrestricted optimum may still be bounded.

## Scope limitations

- This was a hand check of the supplied text only; no verifier, exact integration or source or novelty check was run or seen.
- The asymptotic equivalence R_k~log k/log log k was checked to leading order only.
- The contract's "bottleneck ties" gate was checked only analytically, via the probability-zero tie argument for X_j.

## Verdict

No findings that block Claims A–E as stated for this rule. The three low-severity items are about precision of the statement. Draft status should stand until the pending exact finite checks pass.
