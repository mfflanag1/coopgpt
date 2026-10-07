**Static review / independent attack C — no tools used, nothing executed, no on-disk files inspected beyond the three supplied texts.**

## 1. Proved: a truthfulness-free class ("probabilistic marginal mechanisms", PMM)

Setting as in CONTRACT/DAG_BASELINE: DAG G=(V,E), reports c∈ℝ≥0^E, v_c(S)=maxflow using only S, T=v_c(E).

**Lemma 1.** For each e fix any probability measure ν_e on subsets Q⊆E∖{e}, chosen as a function of G only (not of c). Define
 p_e(c) = E_{Q∼ν_e}[ v_c(Q∪{e}) − v_c(Q) ].
Then for all profiles c∈ℝ≥0^E: (a) p_e(c)≥0; (b) p_e is nondecreasing in c_e with c_{−e} fixed; (c) p_e(c) ≤ D_e(c); (d) convex combinations of PMMs, and of PMMs with any eligible mechanism (e.g. the envelope y), remain nonnegative and own-report monotone.

Proof. (a) v is monotone in the edge set. (b) v_c(Q) does not involve c_e; v_c(Q∪e) is nondecreasing in c_e (feasible-flow inclusion); ν_e is report-independent; expectation preserves monotonicity. (c) Delete from a cycle-free max flow on Q∪e the path flows using e: v(Q) ≥ v(Q∪e) − f_e ≥ v(Q∪e) − D_e. (d) Monotonicity and nonnegativity are closed under nonnegative combinations. ∎

Instances: ν_e=δ_{E∖e} is the marginal rule M of DAG_BASELINE (coverage proved there; cost ≤ L·T). ν_e = predecessor set under a uniformly random order is the Shapley value Sh of the flow game, with **exact** budget Σ_e Sh_e = T at every profile (efficiency), truthful by (b).

**Consequence (demonstrated):** On the OBSTRUCTION.txt family, truthfulness is a non-issue for every PMM; the obstruction attacks only the pairing "D_e × argmin-cut probability". Within PMM the entire problem collapses to a single profile-wise covering inequality (Section 2). This is the sense in which PMMs lie "outside pointwise-majorant repairs": they need not dominate z, and coverage—not monotonicity—is their only constraint. (Not novel: this is the classical probabilistic-value/semivalue construction; I cannot cite URLs without tools.)

## 2. Exact reduction of Target 2 inside PMM

**Lemma 2.** For a PMM p^ν define the coverage ratio
 ρ_ν(G) = sup_{c: T(c)>0} max_{S⊆E, v_c(S)>0} v_c(S)/p^ν(S)(c)  (∞ if some p^ν(S)=0<v_c(S)).
Then ρ_ν·p^ν is deterministic, nonnegative, own-report monotone, coalition-covering at every profile, with total cost ρ_ν·Σ_e p^ν_e. For Shapley the cost is exactly ρ_Sh(G)·T.
Proof: immediate from Lemma 1 and the definition. ∎

Hence **Target 2 (for the Shapley instance) is equivalent to the single inequality**
 (★) Σ_{e∈S} E_σ[v_c(P_e^σ∪e) − v_c(P_e^σ)] ≥ v_c(S)/f(K) for all c, S,
with f(K)=o(K). No monotonicity argument is needed anywhere; (★) is pure cooperative-game geometry.

## 3. Falsification attempts on (★) — what I could verify by hand

- K=2, edges a:s→m (cap 1), b₁,b₂:m→t (cap 1): v({a,b_i})=1, v(E)=1. Sh_a = Pr(a not first)=2/3, Sh_{b_i}=1/6. Coalition {a,b₁}: 5/6 ⇒ ρ_Sh ≥ 6/5 already at K=2. So Shapley is **not** core-selecting on DAGs; a scale factor >1 is unavoidable.
- Deterministic-order PMMs (ν_e=δ_{predecessors}) fail unboundedly: same graph mirrored (a₁,a₂:s→m, b:m→t, order b,a₁,a₂) gives p=(0,1,0) with v({a₂,b})=1 ⇒ ρ=∞. Averaging over orders is essential.
- Series path of m edges with one parallel substitute per level (caps 1, or caps 1/2 on substitutes): exact level symmetry forces Sh(path)=v(path); ratio 1. Asymmetric variant (substitute only at level 1): ρ ≈ 1+1/(m(m+1)). Hierarchical A/B gloves with |A|=n², |B|=n: Sh(A) ≈ 1/n, all tested coalitions covered within 1+O(1/n). I found **no** family where ρ_Sh grows.
- Inference (not a proof here): CONTRACT states a weighted multi-glove lower theorem ~log K/log log K for every eligible TTSP rule. Since ρ_Sh·Sh is eligible, that theorem forces ρ_Sh(G) ≥ Ω(log K/log log K) on that family. So ρ_Sh is neither trivially bounded nor shown unbounded.

**Status of (★): unresolved.** Precise open inequality: does sup over DAGs with K structural cuts of ρ_Sh(G) grow as o(K) (ideally O(log K/log log K))? I have neither an upper bound better than the trivial ρ_Sh ≤ |E| (from Sh_e ≥ M_e/|E|, useless) nor a growing lower bound beyond the inferred glove rate.

## 4. Proved reformulation for cut-mixture mechanisms (the other sub-route)

**Lemma 3.** If π(c) is any distribution over structural minimal cuts and p_e(c)=D_e(c)·Pr_π[e∈C], then p covers every coalition (DAG_BASELINE argument), and p is eligible whenever Pr_π[e∈C] is nondecreasing in c_e (D_e already is). Cost = Σ_C π_C D(C), with D(C) ≤ |C|T.
Honest tension (not a theorem): raising c_e raises D_h for all h and raises D(C) for every C∋e by ≥ΔD_e, so any cost-sensitive π tends to *lower* Pr[e∈C]; on OBSTRUCTION.txt one needs Pr[x∈C](x₁)·(19/20) ≥ Pr[x∈C](x₀)·(9/10). I could not construct a report-dependent π satisfying this with o(K) cost; every variant I tried either reinvents the envelope y or loses the budget control. I regard this sub-route as blocked, not refuted.

## 5. Deliverable summary

- Proved: Lemmas 1–3 (full arguments above); the obstruction never bites PMM; ρ_Sh ≥ 6/5 at K=2; deterministic-order PMMs are inadmissible.
- Not proved / conjecture: ρ_Sh(G)=O(log K/log log K). This is the single sharp inequality (★) I propose as the next step; it is checkable by exact rational LP on the glove family and on OBSTRUCTION.txt (K=5, L=4, where M already gives ≤4T; Shapley there is uncomputed by me).
- Explicit failures: no o(K) general bound obtained; no growing lower bound for ρ_Sh constructed.
- Limitations: static reasoning only; small-example computations done by hand and should be rationally re-verified by the controller before any use; no novelty claims (PMM/semivalue machinery is classical).
