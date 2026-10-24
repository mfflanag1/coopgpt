Evidence gathering is complete (five primary PDFs read directly; Denault's RiskLab copy failed on an expired TLS certificate, so I cite his axioms only as reproduced in Buch–Dorfleitner). Writing up now.

# Result: coalition-stable risk capital for rates books — scope audit

## 1. Primary sources (free copies, with locations)

1. **Csóka, Herings, Kóczy (2009), *Stable allocations of risk*, GEB 67:266–276** — https://cris.maastrichtuniversity.nl/ws/portalfiles/portal/64776577/Herings_2009_stable_allocations_of_risk.pdf
   - Def 2.1 coherent ρ (P&L convention: `ρ(X+a1)=ρ(X)−δa`); Def 2.3 k‑expected shortfall `ES_k(X) = −δ(1/k)Σ_{s≤k} X_{s:S}` (equiprobable states); Def 2.6 exact game; Thm 2.7 Schmeidler's characterization; Def 2.9/2.10 risk environment `(N,S,p,X,ρ)` and game `v(C) = −ρ(X(C))`; Def 2.11 no aggregate uncertainty `X(N)=α1^S`.
   - Prop 3.1 (`Γ_r ⊆ Γ_tb`), Prop 3.2 (`Γ_tb ⊆ Γ_r`; construction uses **ρ = 1‑expected shortfall (max loss), δ=1, S = 2^n−1 equiprobable states**, rows = core elements of subgames, eqs (8)–(9)); Thm 3.4 `Γ_r = Γ_tb`. Prop 4.1 (no aggregate uncertainty ⇒ exact, proof via Thm 2.7 and subadditivity/positive homogeneity/translation invariance); Prop 4.2 (every exact game arises with **S = 2^n−2** states and ρ = ES_1); Thm 4.3 `Γ_rnau = Γ_e`; Thm 4.4 for n<4, `Γ_rnau = Γ_c` (convex).
2. **Csóka, Pintér (2010 WP; BEJTE 2016), *On the impossibility of fair risk allocation*** — https://mpra.ub.uni-muenchen.de/26515/1/AixomShapley10.pdf
   - Def 3.2 (CC, PO, ETP, SM); Thm 3.3 (Young 1985); **Thm 3.4**: on totally balanced games *or* on exact games, PO+ETP+SM ⇔ Shapley; Example 3.1 (3‑player TB game, Shapley `(1/6,2/3,1/6)` blocked by `{1,2}`); p.11 + fn 7: for exact games the counterexample is Rabie (1981), **5 players, and none exists for ≤4 players**; Def 3.6–3.7 solution core; **Cor 3.10**: no rule meets CC+ETP+SM, nor ψ‑CC+ETP+SM; Conclusion: valid also under no aggregate uncertainty.
3. **Buch, Dorfleitner (2008), *Coherent risk measures, coherent capital allocations, and the gradient allocation principle*** (Regensburg open copy) — https://epub.uni-regensburg.de/3801/1/e1270e8233da016cc233bf7c443eb4125b37.pdf
   - Def 2.3 reproduces Denault's axioms: **no undercut** `Σ_{k∈M} A_k ≤ ρ(Σ_{k∈M} u_k X_k)` (= cost‑core condition), symmetry, riskless allocation; Def 2.4 gradient/Euler principle; **Thm 3.1** subadditive ρ ⇒ gradient allocation satisfies no undercut; Cor 3.1; **Thm 3.6** gradient principle symmetric ⇔ ρ linear (no diversification).
4. **Tasche (2008), *Capital allocation … the Euler principle*, arXiv:0708.2542** — https://arxiv.org/abs/0708.2542 (PDF https://arxiv.org/pdf/0708.2542)
   - Def 2.2 full allocation / RORAC compatibility; Prop 2.1 (Euler contributions `(2.6)` uniquely RORAC‑compatible); §2.3 eq (2.9b) Euler contribution ≤ stand‑alone risk for homogeneous subadditive ρ; Prop 2.2 marginal (with/without) contributions under‑allocate; Remark 2.2 ES is homogeneous, subadditive, comonotonic additive.
5. (Context only) Denault (2001), *Coherent allocation of risk capital*, J. Risk 4(1) — RiskLab copy http://www2.risklab.ch/ftp/papers/CoherentAllocation.pdf **not retrieved** (TLS certificate expired on both http/https attempts); CAS abstract page https://www.casact.org/abstract/coherent-allocation-risk-capital confirms the Aumann–Shapley result only.

## 2. Savings‑game transformation — verified, with two corrections of emphasis

Let `C(S) = ρ(Σ_{i∈S} L_i)` on losses (ρ coherent), `k` a capital charge vector. Define `y_i = C({i}) − k_i`, `v(S) = Σ_{i∈S} C({i}) − C(S)`.

- `k(N)=C(N)` ⇔ `y(N)=v(N)`; `k(S) ≤ C(S)` ⇔ `y(S) ≥ v(S)`. So **cost‑core(C) ↔ core(v) bijectively via an additive shift**, and `v` is 0‑normalized (`v({i})=0`), nonnegative and superadditive (subadditivity of ρ). Correct as stated in RESEARCH_CONTEXT.txt lines 37–40.
- `v` is strategically equivalent to the Csóka et al. game `−ρ(X(C))` (Def 2.10, with `X = −L`) plus the additive vector `(C({i}))_i`. Exactness, total balancedness and the core are invariant under this affine map, so **C exact (as a cost game) ⇔ v exact**, and Thm 4.3 applies to `v` unchanged.
- Correction 1: no‑aggregate‑uncertainty (Def 2.11) is **sufficient** for exactness (Prop 4.1), not necessary for a *fixed* ρ. Beyond `Σ L_i` deterministic, exactness must be checked case by case.
- Correction 2 (selector transfer, line 41–42 of the context is right and sharper than stated): Lorenz/egalitarian core selections are not covariant under the additive shift `C({i})`; "egalitarian in savings `y`" and "egalitarian in capital `k`" are different allocations, so whichever fairness selector the project uses must be stated in `v`‑coordinates and its meaning in `k`‑coordinates re‑interpreted. Shapley and nucleolus *are* covariant, egalitarian/Lorenz selections generally are not. (Inference from the definitions; no source gives this for risk games.)

## 3. Straightforward corollary vs. candidate contribution

**Corollary (classical).** Any theorem about all 0‑normalized exact n‑player games (project result 1) transfers *verbatim* to "diversification‑savings games of a riskless aggregate book under some coherent ρ" by Thm 4.3. But note what the representation uses (Prop 4.2 proof): **ρ = max loss (ES_1), 2^n−2 equiprobable states, rows = core points of subgames.** So the transferred statement says nothing about a *fixed* ES level α or a *fixed* factor model; it only says there exists some risk environment realizing each extreme. That is classical (2009) and is not a contribution.

**Fixed‑α ES alone is not obviously binding either.** The Prop 4.2 construction can be replicated with ES_α for any α ≤ 1/(2^n−2) by giving each designed state probability α (ES_α then reduces to the max over designed states); for a *fixed* α (e.g. 2.5%) and n large this breaks, and I found **no source** settling whether all exact games remain representable under fixed‑α ES with unrestricted states. Unresolved; do not claim either way.

**Candidate contribution (genuinely restricted class).** Fix a public d‑factor law `Z∈ℝ^d` and a fixed ES_α; desk i holds signed exposure `β_i∈ℝ^d`, `L_i = β_i·Z`. Then by positive homogeneity/subadditivity, `C(S) = h(β(S))` with `h(b) = ES_α(b·Z)` **sublinear on ℝ^d**, i.e. the support function of the convex compact set `Q_α = {E_Q[Z] : dQ/dP ≤ 1/α}`; for Gaussian/elliptical `Z`, `h(b) = κ_α‖b‖_Σ` (α enters only through the constant, so "fixed ES" = "standard‑deviation rule" there). The game is `v(S) = Σ_{i∈S} h(β_i) − h(β(S))` — exactly the `t_sum − norm(x_sum)` form of project item 4. Facts (my derivations, elementary):
- Core nonempty always; the subgradient/Euler point `k_i = q*·β_i`, `q* ∈ ∂h(β(N))`, lies in the cost core (this is Buch–Dorfleitner Thm 3.1 / Tasche (2.9b) specialized). The core is in general strictly larger (e.g. `d=2`, `β_1=e_1, β_2=e_2`: core is the segment `k_1+k_2=√2, k_i≤1`; the point `(1, √2−1)` is not a gradient allocation).
- `β(N)=0` ⇒ exact (Prop 4.1). For `d=1`, symmetric `Z`: `v(S) = 2c·min(β⁺(S), β⁻(S))` — a divisible **glove market** (Shapley–Shubik). If `β⁺(N) > β⁻(N)`, every long desk with `β⁺(N)−β_i ≥ β⁻(N)` gets zero savings; if `β⁺(N)=β⁻(N)` (exact case) the core contains both "all savings to longs" and "all savings to shorts", whose normalized L1 distance is already **2**. So one factor does *not* shrink the core's diameter; any restriction of fairness extremes must come from the specific opposing *selectors*, not from core width. This is an early warning, not a refutation.
- Dimension count: a d‑factor game has `nd` free parameters vs. a full‑dimensional cone of exact games in `ℝ^{2^n−n−1}`; for `d=2, n≥4` the class is thin, and planar sublinearity imposes constraints beyond coalition subadditivity (positive collinearity `β(S)=λβ(T) ⇒ C(S)=λC(T)`). So the restriction is real; whether it binds the project's extremes is open.

## 4. Nearby incentive/fairness impossibilities (risk‑allocation specific)

- Csóka–Pintér Thm 3.4 + Example 3.1 / Rabie ⇒ Cor 3.10: **no CC + ETP + SM rule** on totally balanced (n≥3) or exact (n≥5) risk allocation games, also with the weaker solution core. Implication for the project (inference): any core selector satisfying ETP must violate Strong Monotonicity on exact classes with n≥5 — a desk whose marginal contributions all weakly rise can be allocated *less*. That is the incentive‑relevant defect to disclose for egalitarian core selections.
- Buch–Dorfleitner Thm 3.6: gradient/Euler allocation is **symmetric only if ρ is linear** — Euler is core‑compatible but unfair in Denault's symmetry sense whenever there is diversification benefit.
- Thm 4.4 of Csóka et al.: for n≤3, exact = convex, so Shapley is in the core and no tension arises; **n≥4 is the minimum interesting size**, n≥5 for Shapley‑core failure.
- Reporting incentives: project item 3 (coordinatewise underreport only, nonnegative inputs) **does not apply** — exposures are signed and misreports in either direction are available; in the glove structure a desk on the long (abundant) side gains by appearing short. No funding‑factor transfer without new hypotheses.

## 5. One exact falsifiable target and one decisive failure gate

**Target T(2).** Let `𝓔_2(n)` be the 0‑normalized games `v(S)=Σ_{i∈S}h(β_i)−h(β(S))`, `β_i∈ℝ^2`, `β(N)=0`, `h` the ES_α‑induced sublinear function of a fixed centered 2‑factor law (level/slope). Let `s_n^{(2)}` be the sup over `𝓔_2(n)` of the project's normalized L1 separation between its two opposing egalitarian core selections. **Claim:** `limsup_n s_n^{(2)} ≤ 2−δ` for some `δ>0` independent of n, whereas project result 1 gives `s_n → 2` on all exact games. Falsified by any sequence in `𝓔_2(n)` with separation `→ 2`.

**Decisive failure gate (algebraic, pre‑numerical).** For any centered or non‑centered *elliptical* factor law, `h(b) − h(−b)` is linear in `b`, hence with `β(N)=0`: `C(S) − C(N∖S)` is additive in S, equivalently **`S ↦ v(S) − v(N∖S)` must be modular** (`= 2h(S) − v(N)` for some `h∈ℝ^n_+` with `h(N)=v(N)`). Apply this to the project's extremal exact game family from result 1: if it passes (modular complement difference) for each n, the extremal games may be 2‑factor‑representable and T(2) should be abandoned; if it fails, the restriction has bite and T(2) is worth an LP study for n≤8 (exact core computation is cheap at 2n parameters). Secondary gate: compute `s_n^{(1)}` for the d=1 glove case first — if the project's selectors already separate to `2−O(1/n)` there, the few‑factor hope dies at d=1.

## 6. Assumptions that must hold

- **Signed positions, no capital floor.** If regulatory floors `k_i ≥ 0` are imposed, then in the exactness regime `β(N)=0` we have `C(N)=h(0)=0`, so core ∩ floor = `{0}`: the whole‑core structure collapses; if the book carries deterministic positive carry, `C(N)<0` and the floored core is **empty**. The bridge therefore only concerns internal transfer pricing with negative charges (rebates for hedges) allowed — not CCP margin (root's lane).
- **Information.** Allocator observes all `β_i` (positions verifiable), the factor law/scenario set and α are public and common; the game is determined by `O(nd)` data, not `2^n` values. Self‑reported exposures reintroduce misreport incentives not covered by project item 3.
- **Linear exposures, fixed law, one horizon.** Nonlinear rates products (options, convexity) break `C(S)=h(β(S))`; model risk in Σ or `Q_α` is outside the game.

## 7. Limitations / unresolved

- Denault (2001) not retrieved (expired certificate); his axioms are cited via Buch–Dorfleitner Def 2.3. Kalkbrener (2005) and Rabie (1981) not accessed; Rabie's 5‑player game is cited via Csóka–Pintér only.
- Fixed‑α ES representability of all exact games for large n: unresolved in the sources.
- The glove‑market, core‑segment, floor‑collapse and modularity statements are my elementary derivations, not from the sources; the modularity gate assumes elliptical (hence `h(b)−h(−b)` linear) laws and does not cover skewed scenario sets.
- Nothing here is a novelty or empirical claim; T(2) is a conjecture with a kill test, and the egalitarian selectors' exact definitions (project‑internal) were not available to me.
