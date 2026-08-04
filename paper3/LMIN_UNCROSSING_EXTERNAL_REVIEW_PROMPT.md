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
- `paper3/wrapper.pdf` — compiled paper.

## Central claim

For a singleton-normalized exact game, supermodularity restricted only to
pairs of coalitions tight at `phi=Lmin(v)` implies that `v` is exact partition
witnessed at `phi`.  Conversely, every slack Lmin suffix yields crossing
tight coalitions with a strict supermodularity defect; they can be selected
from a minimum-uncrossing-energy strict cover.

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
8. Determine whether singleton normalization is needed once the strict cover
   is assumed, and state the strongest correct boundary-local version.
9. Assess whether the result is genuinely broader than the known convex-game
   domain and whether the supplied nonconvex example demonstrates that point.

## Reproduction

```bash
python src/verify_lmin_uncrossing_domain.py \
  --output results/lmin_uncrossing_domain.json
cd paper3
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
```

Treat the finite audit as a bug detector only.  Report correctness, missing
hypotheses, prior art, and significance separately.
