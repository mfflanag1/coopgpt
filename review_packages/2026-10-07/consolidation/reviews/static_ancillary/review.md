**Provisional verdict: no mathematical blockers found in the self-contained material; several claims depend on evidence outside the packet.** Most important point: Theorem `flow:endpoint` (lines 519–676) and Theorem `anc:ring` (871–993) were re-derived line by line and check out; the K-sector bound (23–199) is algebraically correct.

## Findings

**1. (Low) K-sector bound, lines 66–199 — verified.** Recomputed the ordered-pair count in (four:team-comparison): budget multiplicity (K−1)(K−2), ideal coefficient K p_{a,j}+(K−1)q_{a,j}−n_j = Σ_{b≠a}q_{b,j} ✓; weights 1/(K−1),(K−2)/(K−1) cancel β and give (K²+K−4)/(K−1) = K+2(K−2)/(K−1) ✓; integral weights sum to 1 and cancel β ✓ (k=1 degenerates to V_K ≤ KT, consistent). Strictness via C₂=0 ⇒ β=0 and attainment on the compact dual polytope is sound. Dependence on "main theorem" for K=3 sharpness: not in packet.

**2. (Low) Twelve-owner counterexample, lines 539–676 — verified.** Checked: capacity sums 197/196; all eight weight-55 subsets and both weight-54 subsets; the 61/92 subset-sum exclusion; U,V coverage case analysis (d=0 case uses the weight-98 membership fact correctly); the linear identities (flow:identities), θ(C₀)=−4p+19q+20r, and the derived inequalities r−q≥p+1, r≤2q−1, α≤q+r−p ⇒ β≥1−p+4q+5r. Final bounds Σz≥35p+64, α+β≥15p+29 follow. Verdict of H_source=(1,6,23,31,38), source total ≤98, x_A+x_B≤43, s=0 is correct.

**3. (Low) Ring/broken-ring, lines 871–993 — verified.** Player-disjointness of P, worth of y (hub 4/3,4/3,1/3; 7/3 elsewhere), ring monotonicity x_B(j+1)≥x_B(j), x_A(j)≥x_A(j+1) via completions (j,j+1,j),(j,j+1,j+1) with BC[j+1,j]=AC[j,j+1]=0 ✓, c=C, attached bounds p≥2+a, witness colorings (checked all soft-pair teams for targets A,B,C at z), and 16b−2 lower/upper bound all check. Corollary δ_b=1/(6b) ✓.

**4. (Medium – unverifiable) Prop `anc:attainment`, 821–846.** Depends on `prop:family` (not supplied): needs H_i=3 for unmatched i, diagonal worth 3 at unmatched labels, value-one diagonal pairs, special-team worth 5, T=6ℓ+3. Argument is internally consistent but cannot be certified.

**5. (Medium – unverifiable) Prop `anc:cycles`, 1020–1139.** Entirely certificate-based; JSON and `verify_cyclic_necessity.py` not in packet. Cycle-rank arithmetic (17 vertices, 18 edges, connected) and the "free player per label" list (A,B,A,…) are consistent with the two listed tight off-diagonal teams. Note the forcing table requires that the diagonal teams through A₀,A₁,B₉,B₁₀,C₁,C₇ are *not* tight at y (else those players lie in two tight teams); the text says only "twelve tight teams" — should be stated explicitly.

**6. (Low) Flow theorems, 254–475 — verified** (cut-lattice argument, chain family T=n with b_i cuts, path-cover upper bound, transfer lemma, capping argument, many-to-one core characterization and lattice closure). Attribution of the salary-lattice to `AtayNunezSolymosi2026` is unverifiable; this is classical for many-to-one assignment (Sotomayor), which the text should acknowledge if priority matters.

**7. (Low) Prop `anc:compression`, 762–804 — verified**; the "supported even when zero" convention is essential and correctly used.

## Scope limitations
No external files, cited works, `prop:family`, the main theorem, or checker outputs were available. No tests run.

## Verdict
**No findings of mathematical error in reviewed scope**; items 4–5 are insufficient evidence (external dependencies).
