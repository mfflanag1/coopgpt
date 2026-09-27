**Provisional verdict: findings (minor only) — no error found in the algebra or certificate.** I independently re-derived the entire proof chain by hand and it holds; the most important issue is verifier coverage, not correctness: `verify_affine_refinement.py` never checks that the sharp witness actually satisfies the class hypothesis "optimal diagonal matching," which is exactly the hypothesis that makes the b ≥ 13/18 lower bound binding.

## What I re-derived (all confirmed)
- Packing JSON ↔ table (all 6 rows, multiplicities /18) match; each row has zero load on its excluded player and max load exactly 6/18 = 1/3.
- Aggregate cover is *exactly* tight on all 12 target edges: 4/18 on each label-0 diagonal pair (= 2/9 = 1−a−b), 17/18 on each label-1,2 diagonal pair, 18/18 on each P-pair.
- Deletion inequality Σ_t m_t·worth(t) ≤ Σ_p load_p x_p ≤ (T−H_i)/3 summed over |U| = 6 rows gives 2T − ΣH_i/3 ≥ W + (17/18)T − (13/18)d0 ⇒ J ≤ T/18 + (13/18)d0. Line 33–34's "other pairs nonnegative" argument is valid (cover ≥ 0, target = 0 off-support, w ≥ 0).
- Witness: d = (1/8,7/16,7/16), T = 1, W = 13/16, ΣH_i = 1/8+3/16+1/8+3/16+3/16+3/16 = 1, J = 13/16+1/3−1 = 7/48 = 1/18+13/144. (J−a)/d0 = 13/18. Slack vs 17/27 = 5/432 ✓.
- Scalar face: F0=F1=F2=29/82 at (q,v)=(11/41,11/82); weights (260,261,12)/533 sum to 1, cancel q and v, and give 29/82; 29/82−1/3 = 5/246. v=q/2, q=2/7 ⇒ 24a+9b ≤ 7 ⇒ b ≤ 17/27. I also reproduced the legacy 37/94 (b=17/18 ⇒ 47q=11 ⇒ F0=37/94), which corroborates the F-formulas' internal consistency.

## Findings
1. **Low–Medium — verify_affine_refinement.py:41–49 (coverage gap).** No assertion that the witness market's optimal matching is diagonal, yet that hypothesis is what licenses sum(x)=T and membership in the class. Manual enumeration of team worths gives max matching = 16/16 = T (best non-diagonal = 13/16), so the claim survives. *Verification:* enumerate the 36 assignments and assert diagonal is the unique max.
2. **Medium — verify_affine_refinement.py:67 vs 20 (weak negative control).** The `b='17/27'` control trips the hardcoded `require((a,b)==(1/18,13/18),'claimed bound')` at line 20 before any mathematical content runs; it certifies nothing about the pair-domination or sharpness logic. *Verification:* parameterize a,b and confirm failure is raised at `'pair domination'` (target 17/54 > cover 12/54) and at `'sharpness equality'`.
3. **Info/scope — AFFINE_REFINEMENT.md:28–35, 47–50.** The bridge identity J = W + (1/3)Σ_{i∈U}H_i − T and the face formulas F0,F1,F2 are imported from CORE_COMPATIBILITY_UPPER.md, which is not in the packet. `status: PASS` validates certificate arithmetic only, not these imports.

No conflation found: the document explicitly labels 29/82 as an obstruction "NOT an actual market counterexample," disclaims global sharpness/novelty, and keeps the global bound at 39999/100000.

## Scope limitations
Snapshot-only; I did not execute the verifier and cannot confirm the reported run. Parent-document definitions, the claim that the old coefficient was 17/18, "changes no original-core ideal," and the completeness of the listed scalar-face constraint set are unverifiable here. Sections 2/3/5 and donor slack excluded per instructions.

**Verdict: findings (minor verifier-coverage/control issues); the stated local theorem, its sharpness witness, and the 29/82 obstruction check out exactly in the reviewed scope.**
