## Provisional verdict

**No load-bearing findings in reviewed scope.** I re-derived every quantified claim in Theorem 1.1 against the supplied proofs and found no error; the most consequential item is presentational: the leximin-improvement step (lines 239–244) is justified in one sentence that does not address coordinates above $\alpha$ that may *decrease* under clipping. The claim is nonetheless correct.

## Findings

**1. (Low, rigor/presentation) §3, lines 239–244.** "Every old coordinate at most $\alpha$ weakly increases, and every old coordinate above $\alpha$ remains strictly above it. If a lower level increases, its first changed multiplicity decreases…" As written this does not rule out that a coordinate with $x_v(j)>\alpha$ strictly decreases in $z$, which a reader may think blocks the sorted-vector comparison. It does not: Lemma 3.2 gives $z_v(j)\ge\min\{x_v(j),\beta\}$ for $v\ne r$ and $z_r\ge x_r$, so for every $\gamma\le\alpha$, $|\{i:z_i<\gamma\}|\le|\{i:x_i<\gamma\}|$ and $\{i:z_i\le\alpha\}\subsetneq\{i:x_i\le\alpha\}$ (the target leaves). Lexicographic comparison terminates at or below $\alpha$, so decreases above $\alpha$ are irrelevant. *Suggested fix/verification:* insert the threshold-count sentence.

**2. (Low, scope statement) §2 line 247 / §5 line 559.** "$\rho(M)\ge1/K$ as well" uses that the same $x$ serves every target; this requires noting that re-rooting (and the diagonalizing relabeling) does not change the leximin point. True, but implicit.

**3. (Low, disclosed scope) Theorem 1.1 cyclic half.** The cyclic witnesses need zero matrices on chords and on edges to the zero-interaction sectors (lines 546–552), and the tree sharpness example needs $m=1$. Both are permitted by the stated model and are explicitly disclaimed (lines 167–169, 586–588), so this is a genuine restriction, not overclaiming.

**Checks that passed** (recomputed by hand, no execution): cut representation \eqref{eq:cut}–\eqref{eq:reconstruct} including the telescoping cover at arbitrary labels; clipping closure under translation/min, the nonroot and root bounds via $s_v=1+\sum s_b$ and $\sum_b s_b=K-1$, and nonnegativity of $z$; $T=6q+1$ and both covers $u,y$ over all mixed triples; $|U|=3q+3$, budget $\le1$, first-face pinning, $H_{c_{L_0}}=1$; simplex identity $(q+1)\alpha+l_0+\sum(d+r+e+f)+h=1$, sufficiency inequalities ($l_s\ge o_s$, $\alpha+r_s+d_s\le l_s\le1$, $p_{a_{O_s}}\ge3$), dimension $4q+2$; all ideals \eqref{eq:ideals} and their vertex attainments; $\sum_U H_i=2q+3$, $\delta=1$, and the $t=1/(2q+3)$ witness (incl. $b_{R_s}=1-\alpha-t\ge t$, $3\ge4t$); transfer lemma worth formula, unshifted/shifted lifts, equal-size total-preservation, bonus collection with $\mathcal H$, $D_{L_0}=0$, $T_\ell$, $|U|=\ell(q+1)$, $\rho\le1/(2q+2)$ from lower ideal bounds; $\ell_1$ bound $2(1-1/K)$.

## Scope limitations

No execution: the verification package, its negative controls, and README coverage are unreviewed. Literature attributions (e.g., Gangam et al. path core $=$ unit simplex; Atay–Solymosi Def. 3; Martínez-de-Albéniz Thm. 2) and priority/novelty are unverified; the manuscript already qualifies these.
