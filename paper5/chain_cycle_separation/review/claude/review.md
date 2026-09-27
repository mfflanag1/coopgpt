# Review of `paper/manuscript.tex`

I re-derived every claim below by hand from the snapshot. I did not run any of the described certificate or Z3 checks, and none were supplied.

## Findings

No mathematical error was found. The items below are low-severity precision/presentation points; none affects a stated result.

### F1 (Low) — Lemma 3.2 proof, lines 261–263: strict lexicographic improvement is asserted in one sentence but requires a small extra argument
Evidence: "No payoff at or below α decreases, and at least one increases. Its sorted payoff vector therefore strictly improves."
The perturbed vector $x'$ has payoffs above $\alpha$ *decreasing* (only "kept above $\alpha$"), so it is not immediate that the sorted vector improves lexicographically. The claim is nonetheless correct: let $k=|\{f:x_f\le\alpha\}|$; since $x_e=\alpha$, $x^\uparrow_k=\alpha$. For $t\le k$, fewer than $t$ coordinates of $x'$ lie below $x^\uparrow_t$ (arcs in $D$ do not decrease; arcs outside $D$ stay $>\alpha\ge x^\uparrow_t$), so $x'^\uparrow_t\ge x^\uparrow_t$; and at most $k-1$ coordinates of $x'$ are $\le\alpha$, so $x'^\uparrow_k>\alpha=x^\uparrow_k$. The tied case (several payoff arcs at level $\alpha$) and the zero case ($\alpha=0$) are both covered by this argument. Suggested verification: add the two-line counting argument, or a citation to the corresponding step in the slack-balancing source.

### F2 (Low) — Lemma 2.1 proof, line 153: "Coordinates below α agree" is ambiguous wording
Evidence: the intended meaning is "at every coordinate $a$ with $x_a<\alpha$ (equivalently $y_a<\alpha$) one has $x_a=y_a$," which follows from the definition of $\alpha$. With that reading the multiplicity argument is correct: the average has strictly fewer entries at level $\alpha$, all lower levels identical, hence a lexicographically larger sorted vector. Purely a clarity issue.

### F3 (Low) — Section 5 chain-obstruction, lines 447–469: conclusion depends on the exact truncation form of the signed chain model
Evidence: the slice inequality $M_{11}+M_{22}\le M_{12}+M_{21}$ is proved for $M_{ik}=\max\{r_i+s_k,0\}$, i.e. for $w=\max\{P_{ij}+Q_{jk},0\}$ with the middle player fixed. The three displayed slices are correct (I recomputed each: $(2,1;0,1)$, $(3,1;1,1)$, $(1,0;0,1)$ for fixed $c_{L_0}$, $b_{L_0}$, $a_{L_0}$ respectively, all diagonals positive, all violating). The sentence "even allowing signed adjacent-pair entries with zero-truncated triple values" is therefore correct *for that form*, but the manuscript attributes the form to Atay–Solymosi Definition 3, which is not in the packet. This is a scoping caveat, not an error in the nonnegative-chain statement of Theorem 2.2.

## Verified items (no findings)

- **Model / core characterization (lines 116–136):** the reduction of the coalitional core to nonnegativity + triple inequalities + efficiency is correct; completion of partial matchings uses equal sizes and $w\ge0$.
- **Chain core as potential system (Section 3.1):** $T=\max P+\max Q$ (projection and joining), diagonal tightness from efficiency, and the equivalence of the core with (2.5)–(2.7) via $(i,j,j)$, $(j,j,k)$ and re-summation are all correct. The duality nonemptiness argument is correct.
- **Arc table (lines 285–298):** every slack matches its constraint: $U_j\to0$ gives $u_j$; $0\to Z_j$ gives $z_j$; $Z_j\to U_j$ gives $v_j$; $U_i\to U_j$ with constant $P_{jj}-P_{ij}$ gives (2.6); $Z_j\to Z_k$ with constant $Q_{jj}-Q_{jk}$ gives (2.7).
- **Cut step (lines 249–258):** with $S$ = nodes reaching tail$(e)$ in $D$, no $D$-arc enters $S$; the direction $h=\mathbf 1_S$ (shifted to fix the anchor) gives nonnegative derivative on $D$ and $+1$ on $e$; omitted arcs have strictly positive slack or value $>\alpha$. Correct.
- **Cycle telescoping (lines 264–277):** correct; the conclusion $y_e\le r x_e$ and the zero-coordinate remark (line 280–282) follow.
- **Exactly three payoff arcs (lines 300–307):** the layer argument is correct: the only $U\to Z$ passage is through node $0$, the only $Z\to U$ passage is a middle-player arc; a simple cycle uses $0$ at most once.
- **Sharpness and Corollary 3.3:** simplex example gives ratio $1/3$ and $\ell_1$ distance $4/3$; $\|x-y\|_1=2(T-\sum\min)$ is right.
- **Cyclic family (Section 4):** count $8q+1$ correct; diagonal worth $6q+1$ correct. I checked the cover exhaustion symbolically for all $q$: for $a$-label in $L\cup R$, $w=C_{uv}\le1$ and the four two-player sums in the table are correct ($1-\tau$, $1-\tau$, $1+(3s-1)\tau$, $1-\tau$ for $u$; $1,1,2,1$ for $y$); for $a_{O_s}$, "both positive" forces $b\in\{O_s,R_s\}$, $c\in\{O_s,L_s\}$ and the four sums ($4$, $4+3\tau$, $5-3\tau$, $5$ for $u$; $4,4,5,5$ for $y$) are correct; the "at most one positive" bound $w\le3$ against $u_a\ge3+4\tau$ and $y_a=3$ is correct (and $4-(3q-1)\tau=3+4\tau$ exactly). Hence $T=6q+1$ integrally and $u,y\in\mathcal C$; $u>0$ coordinatewise.
- **Partial matching (Section 4.2):** $N_s=5$, $E_s=1$, disjointness, total $6q$, and the unmatched set $U$ with $|U|=3q+3$ are correct; $u$ equals $\tau$ on all of $U$ (I checked each of the six label types). Budget (4.3) and pinning of $c_{L_0}$ on the entire first max-min face are valid; the text (lines 430–434) explicitly avoids claiming $u$ is the final leximin point. $H_{c_{L_0}}=1$ via diagonal-tightness plus $y$ is correct.
- **Spot check $q=1$:** $\tau=1/6$; $u=(L_0:(1/6,2/3,1/6),\,L_1:(1/6,1/6,2/3),\,R_1:(1/6,2/3,1/6),\,O_1:(11/3,1/6,1/6))$, total 7, $N_1$ and $E_1$ tight, $\sum_U u=1$.
- **Certificate count (line 475):** $2\sum_{q=1}^4(3q+1)^3=128+686+2000+4394=7208$, consistent with the stated design.
- **No overreach found** in abstract/intro relative to proofs: "zero" for the pair class is stated as $c_{\rm pair}=0$ (an infimum); the target's value is proved for the full leximin point, not merely for the floor witness; sharpness is attained; scaling remark (line 195–197) is correct.

## Scope limitations

- I could not execute or inspect the exact-rational verifier, the frozen input files, or the Z3 script; the manuscript's finite-check claims are taken as unverified.
- The bibliographic characterizations (Atay–Solymosi Definition 3, Held et al. §3.2, Núñez–Rafels Definition 6, Gangam et al. §3.1.4, and the four originals the manuscript lists as unread) are outside the packet; I cannot confirm them, and I make no statement on priority or novelty.
- The review covers only the mathematics as written; no compilation of the LaTeX was performed.

## Verdict

**No findings of mathematical error in reviewed scope.** The full-core and full-leximin hypotheses are used consistently; the uniqueness lemma, chain core equivalence, cut/cycle certificate (including tied and zero coordinates), three-payoff-arc count, all-$q$ cover exhaustion, integral worth, disjoint partial matching, first-face pinning, ratio, and sharpness claims all check out. Three low-severity clarity/scoping notes (F1–F3) are recorded; none requires a change to any stated result.
