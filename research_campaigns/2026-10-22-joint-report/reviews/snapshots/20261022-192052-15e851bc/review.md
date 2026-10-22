**Provisional verdict: no findings of an invalid step in the reviewed scope.** The most consequential check — that the exposed face Q0 of the order-statistic polytope equals P_h and inherits the ≤ binom(d,2) edge-direction bound — holds as written; the strongest residual caveat is that Sections 5–6 depend on structural facts about f_h (recursive min(A+B, C+D) form, 0/1 cut indicators, constant cardinality 2^h) that live in composition_obstructions.txt, which is not in the packet.

## Findings

**1. (Low / dependency, not an error) mixed_resources.txt §5–6, lines 107–136.** The argument needs: (a) f_h(t) = min over 0/1 indicator vectors of equal cardinality L=2^h; (b) f_h = min(left-pair sum, right-pair sum) so that cuts split as c_h/2 left and c_h/2 right, with left and right cuts on disjoint leaf sets. These are consistent with the recurrence c_h=2c_{h-1}^2 and c_h=2^(2^h−1) (verified: 2,8,128,32768), but the definition itself is outside the snapshot. Verification: confirm f_h's definition in composition_obstructions.txt matches (a),(b).

**2. (Info) §4 lemma, lines 85–104 — verified correct.** Hypersimplex edge characterization (single exchange) is correct; the midpoint argument for ≥2 exchanges is valid (X∪{a,d}, X∪{b,c} share the midpoint of X∪{a,b}, X∪{c,d} and lie off the segment). The pull-back step is sound: for exposing functional w, H = argmin_Δ (Aw)·x satisfies A^T H = E, H's vertices are edge-connected within H, and faces of faces are faces, so some hypersimplex edge e_r−e_s has nonzero image parallel to E. No injectivity is needed. Count of unoriented directions ≤ binom(d,2) is exact.

**3. (Info) §5 face identification — verified.** For small ε, min_Q(1+εv)·q = L+ε·min_{Q0} v·q; for P_h the identity is exact since 1·p=L on all vertices. Equality on all strictly positive profiles (a neighbourhood of 1 suffices) forces equal support functions in every direction, hence Q0=P_h, and edges of P_h are edges of Q. Correct.

**4. (Info) §6 distinct directions — verified.** Cost-1-on-C∪D, cost-2-elsewhere exposes exactly {1_C,1_D} because any other left cut has a leaf outside C and outside D (disjoint supports). 1_C−1_D = λ(1_{C'}−1_{D'}) forces |λ|=1; λ=−1 is excluded by sign on the left block (C nonempty); λ=1 gives C=C', D=D'. Numerics d≥2,7,92,23171 recomputed and correct; d ≥ c_h/√2 ⇒ Ω(2^(√n)) with n=4^h.

**5. (Info) veto_transport.txt §1, lines 17–33 — verified.** Payment P_j(q(b)) to c_j only: c_j's underreport lowers only y_j (q_j monotone), outer own-monotonicity gives nondecrease; helpers get identically 0. For actual coalition S, veto zeroes blocks whose c_j∉S and monotonicity gives q_j(b_S)≤y_j, so F(b_S)≤g(y_C)≤Σ_{j∈C}P_j(y)=Σ_{i∈S}x_i. Budget transfers exactly. No regrouping or multi-owner manipulation used; incentives are all-profile.

**6. (Info) veto_transport.txt §3 grid optimum — arithmetic verified.** Lower bound: the three averaged coverage sums at PA/PB plus the two legal controller comparisons give 2(A^A+A^B)+(2/m)(H^A+H^B) ≥ 9−H^0/m; with (2) at T=2 this yields β(8m−6)≥9m−7. Primal: totals 2+2(m−1)δ = 2+v/2 = 2β_m; all 15 coalition cases at PA (and mirrored PB) covered; only two nontrivial own comparisons, both preserving v. §5 disaggregation counterexample checked (13/16 < 1). These are correctly labelled finite-grid results; the all-real theorem bounds F_m's optimum by that of g=f_1, whose all-real rate remains unknown.

**7. (Info) §2–3 of mixed_resources.txt** (not the focus): the R=2 combination and the k≥1 extension (numerator/denominator weights 18 and 20, difference 21/(2k)) recompute correctly, conditional on the external base certificate.

## Scope limitations
- composition_obstructions.txt (f_h definition, base 9/8 certificate) and both replay scripts are not in the packet; I did not run anything.
- I did not search for alternative hard technologies with few edge directions or for finite-certificate-only compressions; the notes correctly list these as open.

## Verdict
No findings of invalid steps or missing assumptions in reviewed scope, subject to the external f_h dependency (Finding 1). The results are correctly scoped as exclusions; no stronger arbitrary-mechanism lower rate is claimed or established.
