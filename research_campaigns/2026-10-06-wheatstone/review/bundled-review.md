**Provisional verdict: no findings in reviewed scope** (all five effective capacities, all five conditional integrands, and all five own-report dependency lists check out by hand; the composition claim is structurally sound). The most important caveat is that budget inheritance (K=4, U(4)·T) and the exact definition of the "continuous Banzhaf" functional rest on documents not in the packet.

## Findings

**1. Effective capacities (lines 17–19) — verified.** Max flow through x = min(x, ΣC + min(h,w)); through y = min(y,w); through z_j = min(z_j,x) (u's only inflow is x); through w = min(w, y+min(x,h)); through h = min(h,x,w). All nondecreasing in every report. The coalition-preservation argument (lines 21–23) is correct: any S-feasible flow is grand-feasible, so edge flows ≤ d_e; reverse uses d≤c.

**2. Cut structure (line 8) — verified.** s-side sets {s},{s,u},{s,v},{s,u,v} give {x,y},{y,Z,h},{x,w},{Z,w}; h is backward across {s,v}. Exactly four for every k≥1.

**3. Conditional integrands (lines 28–32) — verified via q_e=min(d_e,(B_e−A_e)_+):**
- x: A=min(Y,W), B=Z+min(W,Y+H); difference = Z+min((W−Y)_+,H). ✓
- w: symmetric, Y+min((X−Z)_+,H). ✓
- y: A=min(X,Z+H), B=W+min(Z,X); difference W−min((X−Z)_+,H). ✓
- z_j: A=Z_{−j}+min(W,Y+H), B=X+min(Y,W); difference X−Z_{−j}−min((W−Y)_+,H). Focal-uniform exclusion is correct; Z_{−j} terms min(z_ℓ,x)U_ℓ do not depend on z_j. ✓
- h: A=Y+Z, B=min(X+Y,Z+W,X+W); (min(a,b,a+b))_+=min(a_+,b_+). ✓

**4. Own-report monotonicity (lines 41–47) — verified.** Each dependency list matches which d_e contain the focal report (x enters d_x,d_z,d_w,d_h; w enters d_w,d_y,d_x,d_h; y enters d_y,d_w; z_j enters d_zj,d_x; h enters d_h,d_x,d_w), and each moving argument appears positively in the focal integrand. With U_{−e} held fixed, pathwise monotonicity averages to payment monotonicity.

**5. Composition relationship — verified.** The obstruction graph is exactly (H_k ∥ p) in series with (r_1 ∥ r_2): five minimal cuts as listed in (1). The obstruction's D-values (x, ε, x, x+ε, x, 1, 1/2) coincide with the bundled d-formulas evaluated at its profile, so it is the same rule. Given H_k safe for all k (this file), p and r_1∥r_2 safe (TTSP), and failure for k≥10, closure under series/parallel composition is refuted — conditional on the previously audited certificate.

**Low severity / framing (line 13):** "arbitrarily many overlapping bridges" is parallel replication of one bridge edge; the class is unbounded in owners but has fixed cut count 4 and contains the bridge only as a single minor. The text's own "four-cut class" qualifier is accurate; the headline phrasing slightly oversells.

## Scope limitations
- The payment functional (integral of the marginal indicator over the focal uniform), "coalition-covering," and the U(K) Laplace/union-bound tail proof are not in the packet; I cannot confirm that proof depends only on K and d_e≤T rather than on owner count or cut size. d_e≤T itself holds by definition.
- Safety of the TTSP modules p and r_1∥r_2 relies on the referenced TTSP theorem (not supplied; trivially true for single-cut networks).
- Obstruction arithmetic (δ, (6)–(8)) not re-audited per instructions.

## Verdict
No findings in reviewed scope. The bundled theorem is a correct extension of the five-edge identities; the composition-failure conclusion follows from the graph relationship plus the externally audited certificate.
