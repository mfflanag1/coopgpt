**Static review — no tools run, no files inspected on disk; everything below is derived by hand from the supplied text only.**

## 0. Reduction (elementary, exact)

For e=(a,b), D_e(t,c_-e)=min(t, mf(s,a), mf(b,t)) and the prefix/suffix flows do not use e, so for t ≥ D_e(c) nothing changes: D_e(t,c_-e)=D_e(c) and, for every h≠e, D_h(t,c_-e)=D_h(c) (only paths through e feel c_e). Hence
 y_e(c) = sup_{0≤t≤D_e(c)} z_e(t,c_-e), and trivially y_e ≤ D_e(c) and y_e ≤ U(K)T(c) (sum budget at the shifted profile, T monotone). This gives only the owner-dependent m·U(K)T baseline. (Elementary; not a result.)

Threshold form (as in OBSTRUCTION §3, general): with θ = min_{C∌e} s_C − min_{C∋e} s_C^{−e}, s_C = Σ_{h∈C} D_h U_h,
 z_e = E[min(D_e, θ_+)]. (ties: measure zero)

## 1. Theorem A (K-only bound on a structural class; rigorous)

Call a DAG *antichain-cut* if no inclusion-minimal structural cut contains two edges lying on a common s-t path (reachability-comparable). Then z is own-report monotone, y=z, and Σ_e y_e ≤ U(K)T.

Proof. Fix e, t≤c_e, c'=(t,c_-e). (i) D_h(c') ≤ D_h(c) for all h (DAG_BASELINE monotonicity), so min_{C∌e} s'_C ≤ min_{C∌e} s_C. (ii) If h≁e then no s→a_h or b_h→t path uses e, so D_h(c')=D_h(c). In an antichain cut C∋e every h∈C∖e is incomparable, so s'^{−e}_C = s^{−e}_C. Hence θ' ≤ θ and D_e(c') ≤ D_e(c), so z_e(c') = E[min(D_e(c'),θ'_+)] ≤ z_e(c). ∎

Contains TTSP (series/parallel compositions keep cuts antichains), consistent with the contract's TTSP calibration. Consistency with OBSTRUCTION: cut {x,w,p} has x<w (s-x-u-h-v-w-q); the non-monotonicity in formula (3) enters exactly through W=(x+ε)U_w inside A=min(Y,W), i.e. the comparable containing-cut edge. Not a universal bound; the class excludes the obstruction family by design.

## 2. Gain lemma (general DAG; rigorous)

For C∋e let d_C(t) = Σ_{h∈C∖e, h~e} (D_h(c)−D_h(t,c_-e))U_h ≥0 and Δ_e(t)=max_{C∋e} d_C(t). Then θ' ≤ θ+Δ_e(t), and since min(a,b+c) ≤ min(a,b)+min(a,c),
 y_e − z_e(c) ≤ sup_{t≤D_e} E[min(D_e(t,c_-e), Δ_e(t))].
Lipschitz refinement: by cycle-free path decomposition of a flow attaining D_h(c) (it carries ≤ D_e(c) on e; remove ≤(D_e−t)_+ of paths through e), D_h(c)−D_h(t,c_-e) ≤ (D_e(c)−t)_+. With n_e := max_{C∋e}|{h∈C∖e: h~e}|, E[min(t,Δ)] ≤ min(t,(D_e−t)n_e/2), so
 y_e ≤ z_e(c) + D_e(c)·n_e/(n_e+2), and y_e=z_e whenever n_e=0.
Budget consequence: Σy ≤ U(K)T + Σ_{e: n_e≥1} D_e(c). **Weaker than target**: the correction is the effective capacity of "non-antichain edges", owner-dependent in general (on the Wheatstone family it is D_x+D_w ≈ 2, giving ≤ U(5)+2 at T=1).

## 3. Lemma B (structural, all DAGs; rigorous but weak)

Σ_e y_e ≤ e·T·Σ_C ℓ(C) ≤ e·K·L·T, ℓ(C)= longest chain of mutually comparable edges in C (≤ longest path L).
Proof sketch. Pr[W'=C] ≤ Pr[s'_C ≤ T(c') ] ≤ Pr[s'_C ≤ T(c)]; integrating U_e, D'_e·Pr[·] = E[min(D'_e,(T−R'_C)_+)] ≤ E[min(D_e,(T−R^⊥_C)_+)] where R^⊥_C keeps only h≁e (unchanged D's, others dropped). All terms now sit at the original profile c (no cross-profile summation). Laplace bound (needs a_h≤1, which holds): term ≤ T a_e g(ρ^⊥_{e,C}), g(ρ)=min(1,(e/ρ)^ρ) nonincreasing. Partition C into ℓ(C) antichains (Mirsky); on antichain A∋e, ρ^⊥_{e,C} ≥ ρ_A, so Σ_{e∈A} ≤ ρ_A g(ρ_A) ≤ e. ∎
On antichain-cut DAGs this gives e·K·T — K-only but exponentially worse than U(K); Theorem A is sharper there. On the Wheatstone family Σℓ=6 → ≈16.3T, worse than the L=4 marginal baseline. Labeled: **weaker than target, and not competitive with the elementary baseline as a mechanism**.

## 4. Obstruction to the natural proof route (exact)

The first step of Lemma B (replace "C wins at the shifted profile" by "s_C ≤ T") destroys the disjointness that yields U(K): on a series of K bridges every cut has ρ_C=1 and Pr[s_C≤T]=1, so the relaxed sum is K·T while the truth is T. Any K-only bound near U(K) must retain win-events at each edge's own shifted profile, i.e. control Δ_e(t) collectively; §2 shows the only source of gain is comparable edges inside containing cuts, and competing excluding cuts can only get cheaper (hurting e).

## 5. Counterexample angle — outcome

No obstruction to C·U(K)T found. All hand-checked small families (parallel/parallel K=2, bridge+parallel, 2-vs-1 edge K=2 with Σz=7T/6) are antichain-cut, hence y=z by Theorem A. One non-antichain 7-edge example (s→a→b→c→t with s→c, a→t, b→t) gave, by rough (non-exact) computation, z_e(t)≈t[(1−t)/2+t²/6], increasing in t — no gain; **heuristic evidence only, not proof**. The certified Wheatstone gain (≈4·10⁻⁶) is far from Θ(T). My conjecture (unproved): envelope gains are small because every containing cut must also meet paths avoiding e, whose edges e cannot cheapen.

## 6. Defects/notes in supplied files (verification suggested)

- DAG_BASELINE "uniform Laplace bound ... (e/ρ_C)^{ρ_C}": valid only because a_h ≤ 1 (convexity of ln((1−e^{−λa})/(λa)) in a, then λ=ρ); it is false for a single term with a=10 (Pr=0.1). The text invokes a_e≤1 but does not say the bound depends on it. Suggest adding the convexity step.
- OBSTRUCTION §3 formula (3): checked by cases Y≤W and W<Y; correct.
- CONTRACT: "y=z on TTSP" is implied by Theorem A; suggest recording the antichain-cut class as the proved monotone class.

## Unresolved
Owner-independent K-only bound on general DAGs (target C·U(K)T): open. Whether Σ_{e:n_e≥1}D_e can be replaced by a K-only term: open.
