**Provisional verdict: no substantive findings in reviewed scope.** The three-profile chain (reserve lower → diagonal ray price → axis ratio) is algebraically correct and every inequality step uses only nonnegative multipliers; the most important residual gap is that the checker only exercises the *saturated* equality case, not the inequality logic itself.

## Independently verified

- **Symmetry averaging (§1):** `p_g(C)=gᵀp(gC)` gives `p_g(C)·b = p(gC)·(gb)`; each `g` fixes K, F, and (4,0,0); `gD∈K`. Coverage, monotonicity, and total ≤ κF are linear in `p`, so the 8-term finite average preserves them and is equivariant (`g'=gh` reindexing). Forms `(a_0,0,0)`, `(a_d,b_d,b_d)`, `(a,b,0)`, and reflected `(a_d,b_d,−b_d)` follow from the respective stabilizers.
- **Reserve lower:** remainder `(t−η,x,y)∈K` iff `η≤F(C)`; singleton coverage gives `ηa(C)≥η`. All three aggregates are interior for `0<s<1`; remainders have `t≤1`, so public bound holds.
- **§2:** `U+O=C_0`, `U+D_1+O=C_d`, memberships, and `((1+s)/4)c_d ≥ h a_0 ≥ h` ⇒ (1). ✓
- **§3:** `U'+O=C'_d`, `|3s−1|≤1+s`, `B`, `C_a` all check. Low payment `((1+s)/4)a_d + s b_d = ((1−s)/4)a_d + (s/2)c_d` ✓; coefficients nonnegative, so (2) follows (this correctly handles possibly negative `b_d`). High payment `((3+s)/4)(a+b)` ⇒ (3). Total `p(C_a)·C_a = (1−r)a + r(a+b)` with `1−r=(1−s)/2≥0` ⇒ (4) `=4(1+s)/(3+s)`; `s=1/2 → 12/7`; `2−ratio=2(1−s)/(3+s)>0`, so 2 is a supremum, correctly phrased.
- **Owner-aware rule:** total `F(b_1+b_2)`; `y_i−F(b_i)` = half superadditivity gap ≥0; `Δy_i ≥ F(D_i)` via two superadditivity applications; F superadditive on K by the ∞-norm triangle inequality. ✓
- **§4 identity (5):** `(x+y)/2=z_0−z_3`, `(x−y)/2=z_1−z_2`, `max(|x|,|y|)=|z_0−z_3|+|z_1−z_2|` ⇒ (5). Ray relation and both pointwise descents `p·r_j=q_j` check; both aggregates equal `(3,1,1)`.

## Findings (all minor)

1. **Low — CHECK.py L29–36:** The script fixes `a_d=1, c_d=(1−s)/(1+s), a=1` and checks *equalities*. It therefore certifies the algebraic identities but not the inequality direction or the nonnegativity of multipliers `(1−s)/4, s/2, 1−r, r`. Suggest adding a randomized exact-rational test: sample `a_d≥1, c_d≥(1−s)/(1+s)`, arbitrary `b_d=(c_d−a_d)/2`, and assert `low ≥ (2)`; similarly for (3)→(4).
2. **Low — note L125–130:** The "Huber prices" `(0,2),(1,1),(1/3,5/3)` come from an orthant min2 rule not defined in the packet. The descent arithmetic is verified, but the claim that these are the outputs of a specific factor-3/2 rule is unverifiable here. The example is illustrative only; the theorem does not depend on it (as the note states).
3. **Info — note L4–13:** "Covers every coalition" is a stronger hypothesis than used (singleton coverage suffices, as L34 acknowledges). Consider stating the theorem with the minimal hypothesis to sharpen the separation.

## Scope limitations

- Cannot verify the "accepted L1 signed-transfer theorem" (factor 3/2, `1+c<2`) or the "finite-orthant price reduction theorem"; both are external. The separation vs. the owner-aware factor-1 rule is self-contained; the separation vs. `1+c` relies on `κ≥2>1+c` and the external result.
- The LP discovery aid is not in the packet (correctly declared non-dependency).
- Did not execute the checker; I traced its logic by hand. `range(7)` integer enumeration of (5) is exact.
- Historical novelty not assessed.

## Verdict

**No findings in reviewed scope** beyond the minor items above. The exact lower `κ ≥ 4(1+s)/(3+s) → 2` for aggregate-linear common cone prices on this fixed two-owner bounded model is correctly derived, and the contrast with the exactly efficient two-owner owner-aware rule is valid.
