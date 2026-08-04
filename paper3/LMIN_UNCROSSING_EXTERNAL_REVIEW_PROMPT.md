# Hostile external review — Lmin uncrossing theorem

Please try to falsify the theorem before assessing novelty.  Review the exact
commit supplied with this packet.

## Paths

- `paper3/LMIN_UNCROSSING_DOMAIN_THEOREM.md` — self-contained proof.
- `paper3/sections_leximin.tex` — paper theorem
  `thm:lx-local-supermodular-domain` and its dependencies.
- `paper3/LAMINAR_LMIN_DOMAIN_THEOREM.md` — laminar endpoint of uncrossing.
- `src/verify_lmin_uncrossing_domain.py` — exact audit.
- `results/lmin_uncrossing_domain.json` — reproducible output.
- `paper3/UNCROSSING_DEFECT_BUDGET.md` — quantitative conservation theorem.
- `src/verify_uncrossing_defect_budget.py` and
  `results/uncrossing_defect_budget.json` — exact two-family audit.
- `paper3/BINARY_BROKEN_DIAMOND_REALIZATION.md` — explicit realization and
  sharp four/five-player capacity proof.
- `src/verify_binary_broken_diamond_realization.py` and
  `results/binary_broken_diamond_realization.json` — exact parameter-grid
  audit with independent generic Lmin replay through six players.
- `paper3/wrapper.pdf` — compiled paper.

## Central claim

For any exact game and any core point `phi`, a proper coalition `H` is forced
tight whenever a strict tight-coalition cover loads `H` uniformly, underloads
every outside player, and the `phi`-tight family is closed under uncrossing.
If `H` is slack, a minimum-energy cover contains a broken tight diamond with
positive supermodularity defect.  As a corollary, supermodularity restricted
only to pairs tight at `phi=Lmin(v)` implies exact partition at Lmin.

## Hostile checks

1. Audit compactness of the fixed-load representation polytope, including
   the empty and grand coalitions.
2. Verify the exact energy identity
   `E(A)+E(B)-E(A∩B)-E(A∪B)=2|A\B||B\A|`.
3. Verify that local supermodularity plus core feasibility makes both the
   intersection and union tight individually, including `empty` and `N`.
4. Check removal of a positive grand-coalition coefficient: nonnegativity,
   positivity of the residual rich load, and preservation of strict gaps.
5. Check that the laminar theorem applies to the residual cover without an
   unstated rationality, finiteness, or support assumption.
6. Audit the converse: does a slack suffix force a crossing pair in a
   minimum-energy support, and is its defect exactly the sum of the two
   Lmin slacks?
7. Search the cooperative-game, polymatroid, uncrossing, balanced-family,
   exact-game, and exact-partition literatures for this local-at-Lmin theorem.
   Separate standard uncrossing machinery from the claimed application.
8. Verify the strengthened claim that singleton normalization and Lmin are
   unnecessary once the strict cover is assumed.
9. Assess whether the result is genuinely broader than the known convex-game
   domain and whether the supplied nonconvex example demonstrates that point.
10. Audit the quantitative uncrossing-defect budget separately.  Verify the
    termination argument, extraction of the final partition, exact-balanced
    partition inequality, telescoping signed-defect identity, multiplicity
    factor `m`, and the claim that any strict real cover can be replaced by a
    rational one and scaled to the integer theorem.
11. Search for the quantitative conservation identity in submodular-function,
    skew-supermodular uncrossing, cooperative-game exactness, and core-face
    literature.  The algebra may be standard even if this application is not.
12. Hostilely audit the binary broken-diamond theorem.  In particular, check
    `Core(v)=K` for the lower-envelope construction, every case in the
    singleton-zeroing argument, the closed forms for the intersection and
    union slacks, and the lexicographic max--min argument identifying Lmin.
13. Check the sharp-order argument independently: a broken diamond must have
    all four Venn cells nonempty; with four players the only shape has one
    player per cell; and exactness of the intersection singleton contradicts
    nonnegativity when its Lmin payoff strictly exceeds the other three.
14. Search specifically for prior versions of this four-cell capacity
    obstruction or lower-envelope realization in exact-game, exact-partition,
    core-polytope, lattice-of-tight-sets, and balanced-hypergraph literature.
    Do not infer novelty from the elementary nature of the proof.

## Reproduction

```bash
python src/verify_lmin_uncrossing_domain.py \
  --output results/lmin_uncrossing_domain.json
python src/verify_uncrossing_defect_budget.py \
  --output results/uncrossing_defect_budget.json
python src/verify_binary_broken_diamond_realization.py \
  --output results/binary_broken_diamond_realization.json
cd paper3
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
```

Treat the finite audit as a bug detector only.  Report correctness, missing
hypotheses, prior art, and significance separately.
