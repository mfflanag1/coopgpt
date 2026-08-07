# MathSciNet checklist — run by the human author (subscription access)

Twelve queries. Each line: the query with field specified, what a hit would mean,
and the expectation from the free-source sweep of 2026-08-07.

Known-safe neighbours to disregard wherever they appear:
Arin–Iñarra 2001, Arin–Iñarra 2002, Arin–Kuipers–Vermeulen 2003, Arin–Kuipers–Vermeulen 2008,
Dietzenbacher 2021, Dietzenbacher–Yanovskaya 2020, Llerena–Mauri 2016, Llerena–Mauri 2017,
Biswas–Parthasarathy–Potters–Voorneveld 1999, Studený–Kratochvíl 2022, Dutta–Ray 1989,
Lohmann–Borm–Herings 2012, Csóka–Herings–Kóczy 2011, Klijn et al. 2003,
Laplace Mermoud–Grabisch–Sudhölter 2022, Fujishige 1980, Frank–Murota 2018/2021/2023,
Young 1985, Housman–Clark 1998, Zhou 1991, Arin 2013, Arin–Katsev 2014/2016.

---

## Group A — result (a): quantitative divergence of Lmin and Lmax

**A1.** `Anywhere: leximin AND leximax AND core`
- A hit that compares the two selections *quantitatively* on any class of TU games
  is a direct collision with Theorem `thm:sup`.
- Expected: hits from the Vazirani leximin/leximax core-imputation line
  (assignment / max-flow / MST / b-matching, 2024–2026) and from social-choice
  leximin/leximax aggregation. Disregard both unless a distance, ratio, or
  supremum between the two appears.

**A2.** `Review Text: "leximax" AND "leximin"` restricted to MSC 91A12
- Same target, review-text channel, which is what free sources could not reach.
- Expected: 0 outside the known Vazirani line.

**A3.** `Title: leximax OR lexmax OR "leximax-min"` with MSC 91A12
- Locates every TU-game paper naming the Lmax selection under any of its names.
- Expected: Klijn et al. 2003 (*Neighbour games and the leximax solution*),
  Llerena–Mauri 2016 (*lexmax solution*), Arin–Benito-Ostolaza 2013 (bankruptcy,
  different domain). All known-safe. Anything else naming Lmax on exact or
  large-core games should be read.

**A4.** `Review Text: "decreasingly minimal" OR "increasingly maximal"`
- Tests whether the discrete-convex-analysis pair has been pushed off base
  polyhedra by anyone. A hit that treats non-M-convex feasible sets and measures
  the gap between the two optima would be the closest possible collision with (a).
- Expected: the Frank–Murota corpus and its citers, all on base-polyhedra /
  M-convex sets / integrally convex sets. Disregard those. Read anything that
  quantifies failure of the equivalence.

**A5.** `Anywhere: "exact game" AND (leximin OR egalitarian) AND (bound OR supremum OR ratio)`
- Any quantitative egalitarian statement on the exact domain.
- Expected: 0 hits.

## Group B — result (b): duality and one-coalition certificates

**B1.** `Review Text: "average worth" AND core AND (leximin OR egalitarian)`
- Targets the `nu = max_S v(S)/|S|` certificate. A hit stating `M = nu` (the
  leximax-min ceiling equals highest average worth) on any class beyond convex
  games collides with Theorem `thm:n5closed`.
- Expected: Dutta–Ray 1989 and its algorithmic descendants on convex games only.

**B2.** `Anywhere: "fractional cover" AND core AND egalitarian` (MSC 91A12)
- Targets Proposition `prop:cover` and the "no balanced collection can witness
  `M > nu`" observation.
- Expected: 0. Balanced-cover arguments in this literature certify core
  nonemptiness or stability, not egalitarian levels.

**B3.** `Review Text: "dual game" AND core AND "upper bound" AND coalition`
- Confirms the general duality `Core(v)={x>=0: x(N)=T, x(S) <= v*(S)}` is
  textbook, and finds the best single citation for it.
- Expected: many hits; this query is for **attribution**, not for novelty. Pick
  the earliest clean statement.

**B4.** `Anywhere: polymatroid AND "cooperative game" AND (leximin OR "lexicographically optimal")`
- Tests whether anyone has transported Fujishige's bottleneck formula
  `mu = min_S f(S)/|S|` to a non-submodular `f`. A hit would bear directly on
  Conjecture `conj:floor`.
- Expected: Kaneko–Fushimi 1986 and convex-game applications only.

## Group C — result (c): facet catalogue and solution concepts

**C1.** `Anywhere: "semi-balanced"` (MSC 91A12 / 52B / 90C57)
- The whole point: does anyone besides Studený–Kratochvíl use semi-balanced
  systems, and if so, for what?
- Expected: Studený–Kratochvíl 2022 alone in the game-theoretic MSCs. Free
  citation indexes record at most one citing work. Any hit linking semi-balanced
  systems to a **solution concept** (nucleolus, egalitarian, leximin, kernel) is
  a **possible collision with (c) — flag immediately.**

**C2.** `Citations of: Studený–Kratochvíl, "Facets of the cone of exact games", MMOR 95 (2022) 35–80`
- MathSciNet's citation list is the authoritative version of the check that
  returned 1 (Semantic Scholar) and 0 (OpenAlex) hits.
- Expected: a handful, headed by Laplace Mermoud–Grabisch–Sudhölter. Read every
  one; this is the highest-collision-risk channel for (c).

**C3.** `Review Text: "facet" AND "exact games"` and `Review Text: "facet-defining" AND core AND selection`
- Catches anyone using facet descriptions of a game cone to analyse a selection
  rule rather than membership.
- Expected: 0. Kroupa–Studený 2019 (totally balanced cone) is known-safe and
  concerns membership.

## Group D — result (d): monotonicity failures and where the losers sit

**D1.** `Anywhere: "coalitional monotonicity" AND (egalitarian OR leximin OR "equal division")`
- Positions the section and confirms nothing already localizes failures.
- Expected: Young 1985, Housman–Clark 1998, Zhou 1991, Dietzenbacher 2021,
  Arin 2013, Arin–Katsev 2014/2016, Hougaard–Peleg–Østerdal 2005,
  González-Díaz–Sánchez-Rodríguez 2007 — all known-safe. A hit **bounding** the
  loss of a player by a slack quantity is a collision with Theorem
  `mono:thm:loss` — flag.

**D2.** `Review Text: (slack OR "excess") AND monotonicity AND core AND ("which players" OR "loser")`
- The specific novelty claim: nothing in the literature says *where* the losers
  sit.
- Expected: 0.

**D3.** `Anywhere: "exact games" AND monotonicity`
- Tests whether the exact domain has been studied for monotonicity at all.
- Expected: 0 or Dietzenbacher–Yanovskaya 2020 (antiduality, known-safe).

**D4.** Retrieve and read the review of **Arin (2013)**, *Monotonic core
solutions: beyond Young's theorem*, IJGT.
- Springer-paywalled and unread in this sweep. Needed to state correctly which
  domains admit monotonic core selections.

**D5.** Retrieve and read the reviews of **Housman–Clark (1998)** and
**Zhou (1991)**.
- Housman–Clark: confirm the exact statement (impossibility from **four**
  players, on which domain) and, if the review gives it, whether their
  counterexample game is exact. If it is, say so in paper4 — it makes the
  restriction to exact bumps the operative one rather than the domain.
- Zhou: confirm the precise form of weak coalitional monotonicity, so
  Lemma `mono:lem:reduce`(ii) can be attributed correctly.

---

## Two items to check outside MathSciNet

1. **AAMAS 2026**, *Equitable Core Imputations for Max-Flow, MST and b-Matching
   Games* (Vazirani et al.) — re-check the camera-ready for any statement
   comparing the leximin and leximax imputations quantitatively.
2. **arXiv full text** for the last six months (`semi-balanced`, `exact games`
   + `leximin`, `cone of exact games`) — the arXiv API was unreachable from the
   sweep environment, so this channel is uncovered.
