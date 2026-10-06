# Research report — bounded first pass on the general nonlinear upper-bound route

**Status: NO QUALIFYING PROGRESS.** No unrestricted bound was improved. Below: one explicit candidate formula with separate incentive/coverage/budget checks, its exact failure witnesses, the leave-one-out repair and its exact failure, the envelope repair and its exact budget failure, and one proved (but bounded-family, hence non-qualifying) fact that isolates a narrower live sub-question. Everything is hand-computed; I ran no code.

## 1. Candidate Φ (dilution-weighted marginal + proportional sharing)

For T>0, owner i∈N_j, with e_j=C_j−T, M_i=(c_i−e_j)_+ (the manuscript's marginal), and the *other-pool dilution*
φ_j = (1/(k−1)) Σ_{ℓ≠j} T/C_ℓ ∈ (0,1]:

  **y_i = M_i·(1−φ_j) + T·c_i / ((k−1)·C_j)**,  y=0 at T=0.

Motivation: at all-tight profiles φ_j=1 so the M-part vanishes and the sharing part alone costs kT/(k−1); the M-part is only "switched on" when other pools are diluted.

**Coverage (proved).** Let pool 1 be a minimum pool (e_1=0, so M_i=c_i on N_1). For S with S_ℓ=S∩N_ℓ:
y(S) ≥ c(S_1)(1−φ_1) + c(S_1)/(k−1) + Σ_{ℓ≥2} c(S_ℓ)·T/((k−1)C_ℓ).
If min_ℓ c(S_ℓ) is attained at ℓ=1, the last sum is ≥ c(S_1)·φ_1 and the total is ≥ c(S_1). Otherwise let m attain the min; each term is ≥ its c(S_m)-version and the same algebra gives ≥ c(S_m)(1−φ_1+1/(k−1)+φ_1) ≥ v(S). ✓

**Budget (proved, and bad).** Σ_i y_i = Σ_j (1−φ_j)·Σ_{N_j}M_i + kT/(k−1) ≤ T·Σ_ℓ(1−T/C_ℓ) + kT/(k−1), using Σ_{N_j}M_i ≤ T (manuscript Lemma floor). This is ≤ 3T when ≤1 pool has excess, but the general bound is ~kT. Exact witness: pool 1 total T, pools 2..k singletons of capacity R≫T. Each singleton has M=T, 1−φ_ℓ → (k−2)/(k−1); total ≈ (k−1)T·(k−2)/(k−1)+… ≈ (k−2)T. Worse than the frontier U(k)=R_k+1/log R_k for k≥7 or so.

**Own-monotonicity (FAILS — exact witness).** Fix i∈N_j, x=c_i, a=C_j−x, b=min_{ℓ≠j}C_ℓ. The sharing term T(x)·x/(x+a) is nondecreasing (both factors are), but M_i=min(x,(b−a)_+) is nondecreasing while 1−φ_j is *nonincreasing* in x through T(x). Witness: k=3, pools {x}, (1), (1).
 x=0.8: T=0.8, M=0.8, φ=0.8 → marginal 0.16; sharing 0.8·0.8/(2·0.8)=0.4; **y=0.56**.
 x=1: T=1, M=1, φ=1 → marginal 0; sharing 1/2; **y=0.50**. Decrease of 0.06.
This is exactly the CONTRACT's warned trap ("normalizing by report-dependent T does not preserve report edges"); Φ is refuted as a mechanism.

## 2. Repair Φ′ (leave-one-owner-out weight) — coverage FAILS

Replace φ_j by the owner-specific, c_{−i}-only quantity w_i = (1/(k−1))Σ_{ℓ≠j}(1−b_i/C_ℓ), b_i=min_{ℓ≠j}C_ℓ, giving y_i = M_i·w_i + T c_i/((k−1)C_j).
- Own-monotone (proved): M_i nondecreasing, w_i constant in c_i, sharing term nondecreasing. ✓
- Coverage fails because for i in a *unique* minimum pool, b_i>T gives w_i < 1−φ_1 (wrong direction). Exact witness: k=3, pools (1), (1,1,1), (1,1,1). T=1, b_1=3, w_1=0, y_1=1/2; pools 2,3 owners have M=0 and sharing 1/6 each. Coalition {owner 1, one from pool 2, one from pool 3}: v=1, payment 1/2+1/6+1/6=**5/6<1**.

Φ and Φ′ fail on complementary axes; this is the normalizer-dependence obstruction stated concretely.

## 3. Repair Φ″ (monotone envelope of Φ) — budget FAILS linearly

E_i(c)=sup_{x≤c_i} y_i^Φ(x,c_{−i}) is own-monotone, covers (E≥Φ), vanishes at T=0 (BARRIERS §4). Exact budget witness: k singleton pools, all capacity 1 (T=1). For each owner, x≤1 gives y^Φ(x)=x(1−x)+x/(k−1)=x(k/(k−1)−x), maximized at x=k/(2(k−1)) with value k²/(4(k−1)²). Total **E(N)=k³/(4(k−1)²) ≈ k/4** — linear in k, strictly worse than the frontier's (1+o(1))log k/log log k (already worse at k≈20; k=100 gives 25.5 vs ≈6.5).

## 4. Proved bounded-family fact (evidence only, NOT claimed as progress)

Define class **G**: y_i = d_i·g_i(c_{−i}) with owner-specific price *independent of own report* (not a common pool price). Own-monotonicity is automatic (d_i=min(x,b) is nondecreasing). Neither the capped-Banzhaf base (p_j depends on c_i), nor M, nor the manuscript's Theorem-escape payments (which need r·a_h=b_{h+1}, false at h=0: (r−1)/r ≠ (r−1)²/r²) lie in G.

**Lemma (checked by hand).** On the manuscript's domain 𝒟₁ (reports in {1/r,1}, ≤1 altered pool) class G admits a covering factor-2 rule: with T_h, z_h as in the manuscript, set outside price e_h=z_h/(k−1), low/unit price in the altered pool G(h)=1−min{z_{h+1}, T_h/(r−h)} for h≤r−2, G(r−1)=1/k, and 1/k at H. Consistency: a low owner at h and a unit owner at h+1 share c_{−i} and both receive price G(h); the last-low owner shares c_{−i} with H and both get 1/k. Coverage: G(h−1)≥1−z_h handles n≤b; for n≥b+1, (m/r)(1−G(h)) ≤ (m/r)T_h/(r−h) ≤ z_h. Budget: hG(h−1)+((r−h)/r)G(h)+T_h ≤ 2T_h.

Consequence (inference, not theorem): the proportional-class divergence (Theorem prop) is caused specifically by *common* pool prices, not by own-report-independence. Hence the strictly narrower sub-question "does class G admit a universal constant?" is live and not blocked by any supplied failure.

Partial forcing lemma for G (proved): if all outside capacities are ≥x and x+a_i ≤ every outside total, coverage of {i}∪(one owner per outside pool) plus budget gives g_i ≥ 1 − B(x+a_i)/(m·x), where m is the minimum outside owner count. **Unresolved load-bearing step:** amplifying this into Σ_i d_i g_i ≫ T at a common profile. My attempts found that "forced g_i≈1" needs i's pool-mates small *and* outside pools many-owner, while a common high-capacity profile needs the outside pools' own owners to satisfy the same — these conflict in every instance I tried, which is weak evidence *for* class-G feasibility, not a proof either way. Why this is not simply the original problem: in G the incentive obligation is discharged identically, leaving a pure coverage/budget system in functions of c_{−i}; a class-G obstruction would be a new structural lemma of the Theorem-prop type, and a class-G constant rule would be dimension-free.

## 5. Comparison to frontier / disposition

- No formula here beats U(k)=R_k+1/log R_k; Φ costs ~kT (budget), Φ′ fails coverage, Φ″ costs ≥k/4·T.
- No new lower constant above 2 and no divergent certificate.
- The 15-minute pass yields: three exact falsifiers (persist them so they are not retried renamed), and one reframed narrower target (class G) with its weakest step named.

**Limitations.** All arithmetic is by hand (rational, small instances); nothing executed. The 𝒟₁ class-G rule is a bounded-family construction and is explicitly *not* offered as target progress. Global novelty of class G as a framing is not assessed.
