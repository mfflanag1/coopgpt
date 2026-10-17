**Provisional verdict: no findings in reviewed scope.** Every transition in the 9/7 chain checks (owners preserved, ≤2 deviators, stated withheld bundle/value), the elimination reproduces 7K ≥ 9+4w+2z, and the three-owner 5/4 upper/lower and the 15/8 counterexample recompute exactly. The most important unverified item is a side claim, not the audited result (see Scope).

## Findings

**Four-owner 9/7 lower (PAIRWISE_GAIN_FOUR_OWNER_LOWER.txt) — verified, no finding.**
- Profile data: A (S=3,G=1), B (S=2,G=1), H: sum (5,3), T=3, S=2, G=1 — all correct.
- Transitions (I recomputed each multiset): A→B withheld (1,0)+(0,1)=(1,1), value 1; A→C withheld (1,1); C→D withheld (1,1); swapped-C→E single owner (2,0)→(1,0), value 0 (so g≥u); E→I withheld (1,1); H→swapped-D withheld (2,1), value 1, low profile {(0,1),(0,1),(1,0),(2,0)} = σ(D) with participants mapped to q,r correctly; D→J withheld (0,1), value 0. All keep the same four owners.
- Elimination: (2) from budget A; (3) via g+l ≥ u+(1+p+r)/2 ≥ 1+z+(p+r)/2; e ≥ w+2−K from B coverage+budget; (4) follows. (5),(6),(7) correct; r ≥ 2−K and p+r ≥ 5−3K give 7K ≥ 9+4w+2z ≥ 9. I count exactly 14 contract inequalities plus w,z≥0, matching the stated certificate shape.
- Symmetrization is a convex average of linear constraints over a finite group fixing the ternary grid; sound. The file correctly refrains from promoting the LP optimum to an upper bound.

**Three-owner 5/4 (PAIRWISE_GAIN_THREE_OWNER_THEOREM.txt) — verified, no finding.**
- (4): direct expansion of (3) gives y_i+y_j = [F(b_i+b_j)+T−f_k]/2; the n-owner generalization (line 48) also checks by conditioning on j∈R.
- (5): Σy_i = [3T+ΣF(C−b_i)−S]/4 confirmed.
- (6): from the supplied lemma with rank ≤ 2: 3T−P ≤ 2T−S ⇒ P ≥ T+S. Upper: Σm_i ≥ T via supporting price ⇒ P ≤ 2T ⇒ Y ≤ S+5G/4. Lemma application (H=p·x−F nonneg on the face even with boundary jumps, by the limit argument along segments) is consistent.
- Lower: symmetry argument at P0/P1 is valid; Banzhaf at P1=((1,0),(0,1),(1,0)) pays 1/4,1/4,3/4 = 5/4, so the bound is tight.

**Four-owner coverage counterexample — verified.** Raw Banzhaf at (2,0),(0,1),(0,1),(1,0): 5/8, 5/8, 5/8, 3/8. First three total 15/8 < 2.

**§6 scaling remark — consistent**: scaled excess λ>1 for pure complements gives low-profile pair total λ>… then restoring to the G=0 profile ((1,1),(1,1)) forces total 2 < λ+1, violating pair OUT.

## Scope limitations
- Cannot run `check_gain_only_mask.py` or the "stdlib verifier"; certificate checked by hand only.
- Not audited: Theorems A, C, D of the mask file; the lemma was taken as upstream (I spot-checked its proof and found no error).
- Unverified side claims: "three coordinating owners preclude every finite coefficient" (three-owner line 20–21) and the "constant-value completion obstruction" (mask §8) have no proof in the packet.
- The 9/7 lower applies to fully eligible four-owner domains; no upper for n≥4 is claimed or checked.

## Verdict
No findings in reviewed scope. Suggested verification: machine-replay the 14-inequality certificate with the stated multipliers; numerically test (6) on random 2-D concave homogeneous F.
