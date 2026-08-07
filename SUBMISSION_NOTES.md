# Submission notes — arXiv metadata, venues, cover letters

Two manuscripts, prepared together at commit `3587e55`, author **Maxwell
Flanagan**. They cite each other and are intended for simultaneous posting and
submission; that relationship is disclosed in both cover letters below.

| | Paper 4 | Paper 5 |
|---|---|---|
| File | `paper4/threshold.tex` | `paper5/divergence.tex` |
| Length | 23 pp. | 20 pp. |
| Short name | *threshold* / *phase diagram* | *divergence* |

---

## 1. Paper 4 — arXiv metadata

**Title**

```
Balanced transport at the egalitarian core: a complete boundary phase diagram
```

**Authors**

```
Maxwell Flanagan
```

**Abstract** (plain text; no LaTeX macros; 1,798 characters, inside arXiv's
1,920-character limit — see the trim note below)

```
For a transferable-utility game, exact partition at an allocation means that
every cumulative union of its richest payoff strata is tight. Both this
condition and its Lorenz consequence are due to earlier work. We determine
exactly when the condition can fail at the leximin core allocation of a
singleton-normalized exact game. If a strict payoff boundary has m cumulative
poorer players and h richer players, then a slack richer suffix exists if and
only if m >= m_min(h), where m_min(1) = 4, m_min(2) = m_min(3) = 3, and
m_min(h) = 2 for h >= 4. The lower bounds are structural. A normal-cone
theorem turns leximin optimality into one simultaneous strict cover by tight
coalitions. Projecting the cover to the richer side and applying a convex
defect functional shows more generally that every failure selects one lifted
minimal balanced packet with a positive rooted semi-balanced obstruction;
mixtures are unnecessary. The resulting certificate uses at most |N| - 1
positive coalitions, and its slack budget forces some one-player extension of
the richer suffix to be slack as well. One poorer player cannot support the
required opposing signs. A unique richest player needs four poorer players by
a fractional sacrifice budget. With two poorer players, every failure needs a
proper active hyperedge of size at least three, hence at least four richer
players. Three explicit dimension-free lower-envelope families attain every
remaining pair. The familiar four-player guarantee and sharp five-player
failure are immediate corollaries. The same boundary geometry governs the
failure of coalitional monotonicity on the exact domain: every failure
overshoots the slack of the bumped coalition, is financed coalition by
coalition by boundary slack, and respects tight richer suffixes in aggregate.
```

*Trim note.* This is the manuscript abstract with LaTeX removed and one
closing sentence dropped ("The proof of the phase theorem enumerates no games
and no payoff-stratum patterns; its only case analyses are over the shapes of
a protector trace and over the components of a rank-two vertex") to stay
inside arXiv's 1,920-character abstract limit. Nothing else was changed. If
the sentence is wanted, drop instead the two sentences on the one-packet
sparsity bound — but the trimmed sentence is the more expendable, since §8
already makes the same point and the metadata field is not the place to
pre-empt a referee.

**Primary category**

```
math.OC  (Optimization and Control)
```

*Justification.* The paper's engine is polyhedral and convex-analytic: a
tangent cone, a polar-cone alternative, vertices of an exact-cover polytope,
minimal balanced collections, and facets of the cone of exact games. Its four
closest published antecedents — Studený–Kratochvíl (2022), Csóka–Herings–Kóczy
(2011), Lohmann–Borm–Herings (2012), and Laplace Mermoud–Grabisch–Sudhölter
(2025) — sit in the operations-research/discrete-optimization stream rather
than in economic theory, and the paper contains no economic modelling,
no behavioural content, and no equilibrium argument. math.OC is where a
reader looking for facets of a game cone will look.

**Cross-lists**

```
cs.GT   (Computer Science and Game Theory)  -- the standard cross-list for
        cooperative TU-game structure results; reaches the algorithmic-game-
        theory readership that works on core and balancedness certificates.
econ.TH (Theoretical Economics)  -- the object classified is a fairness
        selection (the leximin core allocation) and §7 concerns coalitional
        monotonicity, both squarely economic-theory topics.
math.CO (Combinatorics)  -- optional; justified only by the balanced-collection
        and set-system enumeration in §6. Add it if a third cross-list is
        wanted; it is the weakest of the three.
```

**MSC2020**

```
91A12  Cooperative games
       -- Primary. The entire object of study is a core selection of a
       cooperative TU game.
90C57  Polyhedral combinatorics, branch-and-bound, branch-and-cut
       -- Proposition 26 proves a family of facets of the cone of exact games;
       Theorems 30 and 31 classify set systems by facet-defining status.
       This is the code a polyhedral-combinatorics reader searches on.
52B12  Special polytopes (linear programming, centrally symmetric, etc.)
       -- The exact-cover polytope P_H and its vertices (minimal balanced
       collections) are the paper's central polytope; Lemma 11's rank-two
       classification is fractional-perfect-matching-polytope geometry.
91B32  Resource and cost allocation (including fair division, apportionment)
       -- Optional fourth. Justified by the egalitarian/fairness framing and
       by §7's monotonicity content. Include only if four codes are allowed;
       otherwise drop it before dropping any of the three above.
```

**arXiv comments field**

```
23 pages. Companion paper: "Maximal divergence of the leximin and leximax
core selections in exact games" (same author).
```

---

## 2. Paper 5 — arXiv metadata

**Title**

```
Maximal divergence of the leximin and leximax core selections in exact games
```

**Authors**

```
Maxwell Flanagan
```

**Abstract** (plain text; no LaTeX macros; 1,825 characters, inside arXiv's
1,920-character limit)

```
A singleton-normalized exact transferable-utility game carries two canonical
egalitarian core selections: the leximin allocation Lmin and the leximax-min
allocation Lmax. They coincide on every exact game with at most four players.
We measure their separation by rho(v) = ||Lmin(v) - Lmax(v)||_1 / v(N), which
never exceeds 2, and show that 2 is the exact supremum. The witnesses form an
explicit two-parameter family G(p,k) of two-generator lower-envelope games
with rho(G(p,k)) = 2(p(k-1)-1)/(k(p+1)) and the deficit identity
2 - rho(G(p,k)) = 2n/(k(p+1)), n = p+1+k, so that s(n) >= 2 - 8n/(n^2 - (n mod
2)) for every n >= 4; the ratio reaches 1 at eight players and exceeds it from
nine on. The mechanism is a single family of tight (p+1)-player caps that both
selections saturate: leximin reads a cap as a ceiling and piles the residual
onto one player, leximax-min reads it as a budget and spreads the residual
over half the players, so the two supports become asymptotically disjoint. The
concentrating selection is the leximin one. On the two-generator class we
prove a dual description of the core, Core(v) = {x >= 0 : x(N) = T, x(S) <=
max(g(S), h(S))}, deduce a one-coalition upper bound on the leximin floor, and
exhibit the smallest game in a complete enumeration at which the mirror bound
for the leximax-min ceiling fails. At n = 5 the family formula is not sharp: a
five-player game analysed by hand attains 1/2, the complete two-generator
enumeration finds nothing above it, and we prove that at five players both
egalitarian levels are certified by single coalitions -- the property whose
failure from six players on accompanies the climb of s(n). We also close one
natural route to a matching upper bound, by a seven-player game in which
smoothing a generator toward uniformity collapses rho from 1/5 to 0.
```

*Trim note.* This is the manuscript abstract verbatim with LaTeX removed
(macros expanded to `Lmin`/`Lmax`, `\|\cdot\|_1` to `||...||_1`, the displayed
core description inlined). No sentence was dropped; it fits the arXiv limit.

**Primary category**

```
math.OC  (Optimization and Control)
```

*Justification.* The paper is an extremal-value determination for two
lexicographic optima over a polytope. The proofs are LP duality (Theorem 7 and
Conjecture 8's reduction), fractional covers (Proposition 9, Proposition 23),
staged optimization over a compact convex set (Theorem 13), and exact-rational
feasibility checks against a facet description (Theorems 24 and 25). Keeping
it with the companion also keeps the pair together for readers.
*Considered and rejected:* econ.TH as primary. The paper measures a
discrepancy between two fairness selections but derives no economic
implication from it, and its methods are entirely polyhedral; econ.TH is the
right cross-list, not the right primary.

**Cross-lists**

```
econ.TH (Theoretical Economics)  -- the question "how far apart can two
        egalitarian solutions be?" is a fair-division question, and the answer
        (asymptotically the entire worth of the grand coalition) is of
        interest to that readership independently of the proofs.
cs.GT   (Computer Science and Game Theory)  -- core selections, exact games,
        and certificate/covering structure.
```

**MSC2020**

```
91A12  Cooperative games
       -- Primary, as above.
91B32  Resource and cost allocation (including fair division, apportionment)
       -- Stronger here than in Paper 4: the paper's whole content is a sharp
       constant for the disagreement of two fair-division rules.
90C05  Linear programming
       -- The floor/ceiling certificates are LP duals; Theorems 24 and 25 are
       exhaustive infeasibility checks over exact rational linear programs.
52B12  Special polytopes (linear programming, centrally symmetric, etc.)
       -- Optional fourth, for the two-generator core duality (Theorem 6) and
       the cover-polyhedron vertex enumeration in Theorem 24. Weaker than in
       Paper 4; drop first if the list must be shortened.
```

*Not recommended for this paper:* `90C57`. Paper 5 uses the facet catalogue
of the exact cone as an input to a feasibility check, but proves nothing about
facets; claiming a polyhedral-combinatorics code would be over-reach.

**arXiv comments field**

```
20 pages. Companion paper: "Balanced transport at the egalitarian core: a
complete boundary phase diagram" (same author).
```

---

## 3. Suggested venues

### Paper 4 (phase diagram + selection + monotonicity)

1. **Mathematical Methods of Operations Research.** It published both
   Studený–Kratochvíl's facet description of the exact cone and
   Csóka–Herings–Kóczy's balancedness conditions for exact games — the two
   papers this manuscript argues against and with, and whose catalogue §6
   uses as a classification target; no other journal's readership already
   knows what a min-semi-balanced system is.
2. **International Journal of Game Theory.** Published Arin–Iñarra's
   characterization of the egalitarian core, which is the paper's other pillar,
   and routinely carries 20–30 page structural results about core selections.
3. **Mathematical Social Sciences.** Published Arin–Kuipers–Vermeulen,
   Llerena–Mauri and Lohmann–Borm–Herings; the natural home if the paper is
   ever shortened or if §7 is spun out as a note (see `paper4/SPLIT_MEMO.md`).

*Considered and not recommended:* **Mathematical Programming**, despite
Proposition 26 being a genuine facet theorem — the polyhedral content is in
service of a game-theoretic classification rather than of optimization method,
and the paper would read as out of scope. **Games and Economic Behavior** —
the manuscript's contribution is structural rather than conceptual-economic,
and §7's headline is a conjecture.

### Paper 5 (divergence)

1. **International Journal of Game Theory.** The comparison of two canonical
   core selections, with a sharp supremum and an explicit witness family, is
   exactly IJGT's format, and IJGT is tolerant of a paper whose matching upper
   bound is left open provided the ledger is honest — which §7 is.
2. **Mathematical Social Sciences.** At 20 pages with one clean headline
   constant, this is the kind of sharp result MSS publishes quickly, and MSS
   already carries the Llerena–Mauri and Arin–Kuipers–Vermeulen background the
   paper leans on.
3. **Mathematical Methods of Operations Research.** Third choice: the LP-duality
   and fractional-cover machinery, and the use of MMOR's own exact-cone facet
   catalogue as the proof engine of Theorem 24, make it a defensible fit if
   the first two decline.

*Considered and not recommended:* **Games and Economic Behavior** — it
published Biswas et al. and Dietzenbacher, so the topic is in range, but GEB
will want the upper bound, and the paper's open problem list is long enough
that a desk rejection is the likely outcome. Revisit if the upper bound closes.

---

## 4. Cover letters

Drafts for the first-choice venue in each list. Both run a little over 200
words (246 and 262 including salutation and sign-off); the excess is the
companion-paper disclosure, which should not be cut. No superlatives are
used: the program's own assessment is strong specialist work, and the letters
say no more than the manuscripts do.

### 4.1 Paper 4 → Mathematical Methods of Operations Research

> Dear Editors,
>
> I submit for your consideration "Balanced transport at the egalitarian core:
> a complete boundary phase diagram".
>
> The paper determines exactly when exact partition fails at the leximin core
> allocation of a singleton-normalized exact game. At a strict payoff boundary
> with m cumulative poorer and h richer players, a slack richer suffix is
> possible if and only if m is at least m_min(h), where m_min(1) = 4,
> m_min(2) = m_min(3) = 3 and m_min(h) = 2 for h at least 4; every admitted
> pair is realized by an explicit integral indecomposable game. The proof turns
> leximin optimality into one simultaneous strict cover by tight coalitions and
> then selects, by a convex defect functional, a single minimal balanced packet
> on the richer suffix. Two further sections classify which catalogued
> semi-balanced types that selection produces, and show that the same geometry
> governs the failure of coalitional monotonicity on the exact domain.
>
> The paper's two nearest antecedents, Studený and Kratochvíl on facets of the
> exact cone and Csóka, Herings and Kóczy on balancedness conditions, appeared
> in this journal, and Section 6 uses the former's catalogue as its
> classification target.
>
> I should disclose that a companion paper, "Maximal divergence of the leximin
> and leximax core selections in exact games", is being prepared for submission
> simultaneously; the two cite each other, but neither depends on the other's
> proofs. Three status tables separate what is proved by hand, what rests on
> exhaustive finite checks over set systems, and what remains conjectural.
>
> Yours sincerely,
> Maxwell Flanagan

### 4.2 Paper 5 → International Journal of Game Theory

> Dear Editors,
>
> I submit for your consideration "Maximal divergence of the leximin and
> leximax core selections in exact games".
>
> A singleton-normalized exact game carries two canonical egalitarian core
> selections, the leximin and the leximax-min allocation; they coincide on
> every exact game with at most four players. The paper measures their
> separation by the scale-invariant ratio rho(v), which never exceeds 2, and
> shows that 2 is the exact supremum. An explicit two-parameter family of
> two-generator lower-envelope games, with both selections in closed form,
> yields a deficit identity giving s(n) at least 2 - 8/n for even n; from nine
> players on the two selections can differ by more than the worth of the grand
> coalition, and their supports become asymptotically disjoint. One family of
> tight caps drives both: leximin reads a cap as a ceiling, leximax-min as a
> budget. The paper also proves that at five players both egalitarian levels
> are certified by single coalitions, a property that fails from six on, and
> closes two natural routes to a matching upper bound, which remains open.
>
> The subject is the comparison of two core selections whose characterizations
> appeared in this journal, and the contribution is a sharp structural constant.
> The pair itself has recent precedent in the fair-core-imputation literature,
> which the paper credits; the quantitative worst case, and its exact value,
> are new.
>
> I should disclose that a companion paper, "Balanced transport at the
> egalitarian core: a complete boundary phase diagram", is being prepared for
> submission simultaneously; the present paper cites it for the four-player
> rigidity and for the lower-envelope technique, but neither depends on the
> other's proofs. The final section separates the proved statements from the
> finite checks, from the enumerations, and from the five open problems.
>
> Yours sincerely,
> Maxwell Flanagan
