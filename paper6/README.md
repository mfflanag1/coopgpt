# Boundary-partition characterization paper

DRAFT — not reviewed or integrated. Prepared for lead review.

This directory contains the standalone note on boundary partitions at the
leximin core: the configuration in which a slack strict payoff boundary
`H = {f,g}` carries two tight coalitions that partition the player set, one
anchored at each richer player. `partition.tex` proves the two-parameter
characterization

```text
a boundary partition of type (p,q) exists  <=>  p,q >= 1 and p+q >= 4
```

with both directions in closed form and no solver in either. Writing `P` and
`Q` for the two blocks' poorer players, the whole result turns on one
consequence of the uncrossing budget: a tight coalition containing `H` and
omitting all of `P` forces `|Q \ T| >= 2`. Read as a prohibition it kills
`p+q <= 3`; read as a design constraint it dictates the two realizing families
and their exact ranges.

Two by-products are used as the methods section and are reusable elsewhere:

- exactness of a game is an **existential** linear condition (one attaining
  core point per coalition), needing no semi-balanced catalogue, no vertex
  enumeration, and no bound on `n`;
- at a fixed payoff stratification, leximin optimality is a **Farkas
  certificate** supported on the tight coalitions — quantifier-free, because
  complementary slackness removes the bilinear terms and leaves a disjunction.

The note also corrects a conjecture from an earlier round of the program. We
had conjectured that a boundary partition requires `max(p,q) >= 3`, on the
strength of a census in which type `(2,2)` never appeared. It is realizable;
Example 25 of the paper exhibits a six-player game carrying it, and the
seven-player zero-payoff profile that the conjecture would have refuted is
therefore **realized** rather than impossible.

Build from this directory with:

```bash
pdflatex -interaction=nonstopmode -halt-on-error partition.tex
pdflatex -interaction=nonstopmode -halt-on-error partition.tex
```

Twelve pages, one open TODO: prior-art positioning, marked in the introduction
for the lead's citation verification pass. The bibliography deliberately lists
only the three works actually cited, each carried over verbatim from paper4's
bibliography; nothing was reconstructed from memory.

Everything in the main theorem is proved by hand. The single
machine proof dependency is the frontier dichotomy (Theorem 23), a finite check
over the 60 payoff stratifications of type `(1,3)` with a satisfiable control;
it is used nowhere else. Drivers, controls and audits are archived in
`../verifiers/part`, including the superseded `m=3` finite check and its
independent cross-check, which are retained as controls on the hand proof
rather than as dependencies.
