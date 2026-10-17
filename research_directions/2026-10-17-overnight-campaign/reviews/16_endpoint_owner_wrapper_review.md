**Provisional verdict: no defects found in reviewed scope.** Most important check: the Claim‑1 endpoint enumeration and both KKT certificates reproduce exactly by hand; the (n+1)/2 lower bound and the scalar‑wrapper obstruction are quantifier‑clean.

## Findings

**Claim 1 (PROJECTION_ENDPOINT_OBSTRUCTION.txt) — verified, no defect.**
- Balanced closures (lines 10–13, 22): all 15 coalition worths of both games reconfirmed by exhibiting feasible points of P / P′ (e.g. v34=0 via (3,3,0,0), v1234′=4 via (1,1,0,2) with dual (½,½,½,0)).
- Interior certificate (lines 25–28): Aᵀλ=(¾,5/4,½,7/4), all four rows tight, multipliers ≥0 ✓. Cover set of the balanced closure equals the primitive polyhedron (rows 24,134,12,124 are themselves coalition constraints), so projecting onto the 4‑row system is legitimate.
- Endpoint cases (lines 37–55): each stated projection reproduces (e.g. (5,9,4,12)/7 with multipliers (8,4,1)/7; 24+12 only → (⅓,5/3,0,4/3)). Case decomposition is exhaustive over 32 masks; max 12/7, gap 1/28 ✓.
- Production realization (lines 59–75): the "+5h" offset is ≥ max vₛ=5, so W‑forms are inert at full report; P⊆P′ gives v′≤v at low report; coalitions omitting 4 have h=0. ✓
- Checker: `projection` skips singular Gram systems, which could in principle miss a witness, but any found witness is KKT‑verified and the minimizer is unique, so a PASS is sound. `vals`/`wvals` loop checks all 16×2 values ✓.
- Hidden assumption (interpretive, not an error): "endpoint" is fixed as {0, full‑game value}; reductions anchoring at other values (e.g. reported values) are not excluded. Line 83–86 already states this.

**Claim 2 (OWNER_FACE_NULL_AND_OBSTRUCTION.txt) — verified.**
- §1 OUT proof: uses superadditivity F(x+z)≥F(x)+F(z) (needs F(0)=0, implied by homogeneity) and C≥d; all four activity cases check.
- §2 (A),(B) and final‑profile count n+n(n−1)/2 ✓. Note scalar per‑owner coefficients are assumed; a per‑resource diagonal generalization escapes §2's algebra but is subsumed by §3 (such rules are globally monotone).
- §3: permutation/resource‑label averaging preserves all hypotheses because min(x₁,x₂) is label‑symmetric; the three comparison profiles are coordinatewise ≤ the final profile ✓. Sharpness matches §1's upper. ✓

**Claim 3 (SHARED_CAP_SCALAR_WRAPPER_OBSTRUCTION.txt) — verified conditional on external inputs.**
- Algebra: (b−δ)(1−(b−δ)/2b)=b/2−δ²/2b ✓; (3) ✓; telescoping with NΔ²→0 ✓; §2 squeeze ✓; §3 contradiction P/g>κ ✓.
- §4 numbers: payments ¾ and 5/7, gap 1/28, activity sums =1 ✓ (consistent with p_P in a linear Huber regime).
- Dependencies not in packet: the unit‑edge Huber share formula x(1−x/2b) and grand coverage Σzᵢ≥g are cited as "audited"; the theorem inherits their correctness.

## Scope limitations
- Huber share formulas, OUT/coverage definitions, and the "accepted" 1.543 mechanism are external to the packet.
- No tool execution; checker logic reviewed by reading only.
- Not assessed: novelty, or whether the obstructions bear on the live √n conjecture beyond what is stated.

## Verdict
**No findings in reviewed scope.** All three claims' quantifiers, fixed‑owner legality, finite‑partition and enumeration arguments, and KKT certificates hold as written; Claim 3 is sound modulo the cited Huber share properties.
