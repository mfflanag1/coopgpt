I have everything I need from the three supplied files; the remaining work is mathematics, which I carried out by hand below (no scripts, no edits).

## Result summary

**Gluing two independently valid (full-OUT, factor 1+α) mechanisms at a shared vertex by "output-maximizing capacity split + summed component payments" preserves the budget constant but does not preserve full OUT.** I give an exact fixed-owner counterexample on P4 itself (the smallest tree where the optimal split is unique on an open region, so no tie-break is involved), and a positive composition lemma for the opposite glue ("duplicate the shared vertex in both components"), which preserves OUT exactly but destroys the uniform budget constant. Together they isolate the load-bearing issue: a split of the shared resource that is optimal for the aggregate profile c cannot simultaneously be optimal for every withheld bundle d ≤ a.

## Setting and provenance

- Production F(c) for unit edge profits: `inputs/P4_PROTECTED_LEAF_OUT_FINAL.txt` lines 16–18; full OUT definition lines 20–27 (fixed owners, coordinatewise underreports, passive members included, budget benchmark = total payment vs F(c)).
- Single-edge rule (α=1/√2): for capacities X ≥ Y, w_X = αY, w_Y = min(Y, αX); full OUT iff α(1+α) ≥ 1 (`inputs/DOUBLE_COVER_ROUTE.txt` lines 18–31; same calculation in P4 file lines 97–104). I re-derived the edge-sum minimum: for t=Y/X ∈ [α,1], g_X+g_Y = αt + α/t + αθ_X(1−t) + αθ_Y(1−1/t), minimized at (θ_X,θ_Y)=(0,1) giving α(1+t) ≥ α(1+α) ≈ 1.207. Confirmed.
- Complete-blowup transfer (aggregate a group, apply group price to each member): P4 file Section 6, lines 197–213. The same argument applied to a single edge gives the star K_{1,n} rule: aggregate the leaves. (Inference: Section 6 is written for P4 groups, but its packing-redistribution argument is generic for complete bipartite group pairs.)
- Universal funding identity for any double-cover flow: `DOUBLE_COVER_ROUTE.txt` lines 11–16.
- On a tree, F(c) = min over vertex covers S of c(S) (bipartite LP integrality); I use only the P4 formula min(A+C, B+D, A+D) from line 18.

## 1. The natural gluing rule (specified exactly)

Let T = T₁ ∪ T₂ with T₁ ∩ T₂ = {s}. Let y¹, y² be valid mechanisms on T₁, T₂. **Rule G (output-maximizing glue):**
1. Split c_s = x + (c_s − x) with x ∈ argmax_x [F_{T₁}(c|_{T₁∖s}, x) + F_{T₂}(c|_{T₂∖s}, c_s − x)] (any tie-break).
2. Allocate each owner's s-holding proportionally (b_is·x/c_s to T₁, rest to T₂).
3. Pay y_i = y¹_i(component-1 profile) + y²_i(component-2 profile).

**Budget (always preserved).** Since any packing of T splits s's use, F_T(c) = max_x[F_{T₁}+F_{T₂}], so Σ_i y_i ≤ K(F_{T₁}(c¹) + F_{T₂}(c²)) = K·F_T(c). This is a proof, independent of the tie-break.

## 2. Exact counterexample to Rule G (incentive fails)

Take P4 = B–A–D–C as T₁ = star B–A–D (center A), T₂ = edge D–C, glued at s = D. Component rules: y¹ = single-edge rule on the leaf-blowup K_{1,2} (leaf group {B, D¹} aggregated); y² = single-edge rule. Both are independently full-OUT with factor 1+α by the cited sources.

**Split.** f(x) = min(A, B+x) + min(D−x, C), x ∈ [0, D]. On the open region
  **αB < A < B and αC < D < C**
we have B+x ≥ B > A and D−x ≤ D < C, so f(x) = A + D − x: the **unique** maximizer is x = 0 (so step 2's allocation rule is also moot). F_{P4}(c) = A + D here, consistent with min(A+C, B+D, A+D).

**Glued payments on the region.** T₁ has D-copy of capacity 0, so T₁'s rule is the edge (B, A) with B > A > αB: w_A = min(A, αB) = αB, w_B = αA. T₂ is the edge (C, D) with C > D > αC: w_D = min(D, αC) = αC, w_C = αD.

**Fixed owners.** S holds all of A and all of D (one mixed owner); O₁ holds all of B; O₂ holds all of C. Numerics: (A, B, C, D) = (0.9, 1, 1, 0.9), α ≈ 0.7071.

- Truthful: y_S = w_A + w_D = αB + αC = 2α ≈ 1.4142.
- S legally underreports A′ = D′ = 0.8 (δ = 0.1; any δ < A − αB keeps the profile in the region). Split still x = 0; y_S = αB + αC = 2α. **Drop = 0 exactly** (w_A, w_D are flat in A, D on the region).
- Withheld bundle d = (d_A, d_B, d_C, d_D) = (0.1, 0, 0, 0.1): F_{P4}(d) = min(0.1, 0.1, 0.2) = 0.1 > 0 (S can operate edge A–D alone).

Full OUT fails; indeed singleton OUT fails, with no ownership reassignment and legal high/low reports. The coalition {S, O₁} with passive O₁ also fails (drop 0.1α ≈ 0.071 < 0.1). Meanwhile the budget is fine: total payment 3.8α ≈ 2.687 ≤ (1+α)·F(c) = 1.707·1.8 ≈ 3.07. The failure holds for every α < 1 (region nonempty) and is an open-region, exact phenomenon, not a tie or numerical artifact.

**Why it fails (structural).** On this region Rule G discards edge A–D entirely, so the glued rule is the disjoint-union rule on the forest P4 − {A–D}, which is OUT only relative to F_{forest}(d) = 0 for the above d, strictly below F_{P4}(d). The aggregate-optimal split sees no marginal value in A–D (B already absorbs A, C absorbs D), but the withheld bundle's standalone production uses only A–D.

**Contrast with the audited P4 rule** at the same profile (middle cone, P4 file 4C, lines 114–126): u = v ≈ 0.193 > 0, w_A = α(B+D) − βC = w_D ≈ 0.8435, ∂(w_A+w_D)/∂A = ∂/∂D = α, so S's drop under the same underreport is 2αδ ≈ 0.141 ≥ δ. Total payment is also 3.8α — identical budget, different incentive behaviour. The coupled selector is not a sum of component mechanisms.

## 3. Positive composition lemma (incentive-preserving glue)

**Lemma (duplicate glue).** Let y¹, y² be full-OUT with coverage on T₁, T₂ with constants K₁, K₂. Define on T = T₁ ∪_s T₂: y_i(b) = y¹_i(b|_{T₁}) + y²_i(b|_{T₂}), with every owner's full s-holding entering both components. Then y is full-OUT with coverage on T, and Σ_i y_i ≤ K₁F_{T₁}(c|_{T₁}) + K₂F_{T₂}(c|_{T₂}) ≤ max(K₁,K₂)·min(2F_T(c), F_T(c) + c_s).

*Proof.* For coalition holding a and withholding d, component k sees the legitimate component withholding d|_{T_k} with outsiders unchanged (the component profile is exactly c|_{T_k} − d|_{T_k}), so drop_k ≥ F_{T_k}(d|_{T_k}). Any packing of T at d restricts to packings of T₁, T₂ each using ≤ d_s at s, hence F_{T₁}(d|_{T₁}) + F_{T₂}(d|_{T₂}) ≥ F_T(d). Coverage: take d = a. Budget: optimal component packings union to a T-packing violating only s by ≤ c_s; deleting ≤ c_s of flow at s gives F_T(c) ≥ F_{T₁}+F_{T₂} − c_s; also each F_{T_k}(c|_{T_k}) ≤ F_T(c). ∎

The bound is not uniform below 2: for P3 with all capacities 1, duplicate glue of two edge rules pays 4α ≈ 2.83 = 2.83·F_T(c).

Fixed-fraction splits λc_s/(1−λ)c_s interpolate: budget ≤ K·F_T(c), drop ≥ F_{T₁}(d, λd_s)+F_{T₂}(d,(1−λ)d_s), which equals F_T(d) for all d only if λ ∈ {0,1}-type degenerate cases — i.e., no constant split gives exact OUT (single edge u–s inside T₁ with d_u = d_s already loses (1−λ)d_s).

## 4. Consistency check (where composition happens to work)

Gluing two single-edge rules at a common center with the *proportional* split x = c_s·c_u/(c_u+c_v) (always an output maximizer for K_{1,2}) gives both components the same ratio r = c_s/(c_u+c_v), hence identical s-prices min(1, α/r) (r ≤ 1) or α/r (r ≥ 1), and leaf prices αr or min(1, αr). This is exactly the K_{1,2} leaf-blowup of the edge rule (P4 file §6), so it is OUT — but only because the glue coincides with an already-coupled rule, not by a composition argument. Different output-maximizing tie-breaks on K_{1,2} are not covered by this check.

## Unresolved / load-bearing

- **Settled:** Rule G (any tie-break) fails full and singleton OUT on P4 in an open region; duplicate glue preserves OUT but not the constant.
- **Unresolved:** whether some *state-dependent* split λ(c) with summed component payments can achieve 1+α on P5 or spiders; the counterexample only forces λ = 0 for output-maximizing splits. Whether a genuinely coupled whole-tree double-cover selector (like the P4 rule) exists for all trees is untouched here, per scope.
- Component validity of the K_{1,2} blowup rests on reading P4 file §6's argument as generic for complete bipartite group pairs (inference, not re-audited line by line); the failure computation itself only uses the explicit edge formulas.

## Limitations

No novelty or all-tree claim; this is one composition route closed and one trade-off lemma proved. No files were edited; no acceptance checks were run.
