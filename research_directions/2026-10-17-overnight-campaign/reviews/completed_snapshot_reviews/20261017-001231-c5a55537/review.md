**Provisional verdict: no findings of substance in reviewed scope.** Both proofs check line-by-line; the only concrete gaps are (a) `AGGREGATE_PRICE_OPTIMALITY_CANDIDATE.txt` never states the edge worth function it relies on (implicitly min(A,B)), and (b) the "exact optimum" sentence is conditional on an external audit.

## Findings

**1. [Low] unrestricted/AGGREGATE_PRICE_OPTIMALITY_CANDIDATE.txt, lines 5–13, 19, 25, 28** — The worth function is never defined. The proof uses "grand worth 1" at (1,1), "owner 3 alone produces 1" at report (1,1), and "grand production is 1" at aggregate (M,1); all three require worth = min(A,B). With that hypothesis stated, the chain is correct: p+q≥1 and p,q≥0 (coverage/nonnegativity at ((1,0),(0,1),(0,0))); MP(M,1)≥p (owner 1 monotonicity); P(M,1)+Q(M,1)≥1 (singleton {3} coverage at ((M−1,0),(0,0),(1,1)), which is a legal profile since owner 3 may report both); total MP+Q ≥ 1+(M−1)P ≥ 1+(1−1/M)p; mirror gives q; max(p,q)≥1/2 ⇒ ≥3/2−1/(2M); sup over M gives 3/2. Verification: add "the edge produces min(A,B)" to the setup. The three-owner restriction and the "why not all mechanisms" caveat are correctly scoped.

**2. [Low] unrestricted/…, lines 38–41** — "3/2 is the exact worst-case optimum of this architecture" depends on the Huber-price rule attaining 3/2, explicitly flagged as unaudited. Only the lower bound is established here.

**3. [Info] energy/SHARED_SOURCE_PRICE_THEOREM.txt** — Verified items:
- §1 primitive: total T[1+q(ρ−1)] ≤ (1+1/(2e))T; coverage via s≤T and Σ_S min(x_r,T) ≥ min(l,T); long-side derivative q(1−d/T)≥0; ρ′(T)=−Σ_{l_r<T}l_r/T² so q′=qΣ_{l_r<T}l_r/T² ≤ qρ/T, giving 1−q(1+ρ)≥0 since (1+ρ)e^{1−ρ} is decreasing from 2 at ρ=1. At E=H every owner has x_r≤T, ρ=1, q=1/2, so both side conventions pay x_r/2 — the tie is well-defined and continuous.
- §2 patch: m_j = min(E,H)−min(H,E−e_j) is nondecreasing in e_j; max of monotone functions is monotone; case E≤H gives exactly T + qρT ≤ 3T/2; case H≤E: formula (2) rederived (1−q + q(E−e_B) + e_B − kδ); k=1 bound (1−q)(1−δ)=f(δ)≤1/2 with f′=−1+e^{−t}(2−t)/2≤0; k≥2 bound 1−q−(k−1)δ ≤1/2 since d/dδ = q−(k−1)<0; the e_b≥1 case (ρ=1+t, m_b=1−t, others zero) matches. Zero reports pay 0 on both sides and m_j=0; T=0 pays 0.
- §3 identity (3): greedy top-x matching is optimal by rearrangement; Fubini on the indicator c(x)≤t≤v(x) gives min(E_t,H_t) because c is nondecreasing and v nonincreasing in the quantile x. Requires c,v≥0 for the ∫_0^∞ range — stated at lines 9–11.
- §4–5: per-threshold coverage and 3/2 integrate; ∫[T_t(N)−T_t(N\{j})]dt = M_j by (3) applied to N and N\{j}; per-coordinate tier monotonicity holds since each tier enters pooled quantity in a public set of thresholds.

Note the §2 bound is attained at E=H (total exactly 3T/2), so the stated rule cannot be improved; nonsharpness refers only to other rules, consistent with line 26.

## Scope limitations
No code execution; the 4/3 numerical remark (lines 145–148) not assessed. Novelty of either result not evaluated. Mixed-role owners (§5, line 125) excluded by the authors and not examined.

## Verdict
**No findings** of mathematical error in reviewed scope. Minor: file 2 should state worth = min(A,B) explicitly; its optimality sentence remains conditional.
