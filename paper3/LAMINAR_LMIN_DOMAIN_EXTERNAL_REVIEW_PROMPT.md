# Hostile external review — laminar Lmin domain theorem

Please review the candidate theorem at the exact commit supplied with this
packet.  Treat the result as unvalidated and try to falsify it before judging
novelty.

## Primary paths

- `paper3/LAMINAR_LMIN_DOMAIN_THEOREM.md` — self-contained statement and proof.
- `paper3/sections_leximin.tex` — paper theorem `thm:lx-laminar-strict-cover`
  and its dependency `lem:lx-strict-richer-cover`.
- `src/verify_laminar_lmin_domain.py` — finite combinatorial audit.
- `results/laminar_lmin_domain.json` — reproducible output.
- `paper3/wrapper.pdf` — compiled paper, theorem on pages 37--38.
- `paper3/LMIN_TIGHT_SKELETON_RETRACTION.md` — support-independent reduction
  that motivates the domain theorem.

## Claim to audit

At a strict payoff boundary `(L,H)` of `phi=Lmin(v)` in a
singleton-normalized exact game, suppose one strict richer-side cover has
laminar positive support: common positive incidence load on `H` and strictly
smaller load on every player of `L`.  Then `H` is tight at `phi`.  Hence a
laminar supported cover at every boundary implies exact partition at Lmin;
in particular, a laminar complete Lmin-tight family suffices.

## Required hostile checks

1. Verify the minimal-set step: for each `h`, does laminarity really imply
   that every supported coalition containing `h` contains every player of
   its inclusion-minimal supported set `M_h`?
2. Verify that maximal distinct `M_h` form a genuine partition of `H`,
   including equality and nesting edge cases.
3. Check the exact-balanced vector consisting of `+1` on the partition
   blocks, `-1` on `H`, and `+1` on `N`; confirm that the convention allowing
   the grand coalition is consistent with the cited exactness
   characterization.  If not, determine the correct equivalent formulation.
4. Check that singleton normalization is used only through the strict-cover
   dependency, and whether the theorem can be stated directly for an
   arbitrary exact game whenever the cover is given.
5. Search specifically for prior results combining laminar tight/core
   systems, egalitarian-core transfer blockers, exact-balanced collections,
   and exact-partition games.  Distinguish an established laminar-hypergraph
   lemma from the Lmin/exact-game combination claimed here.
6. Assess whether the boundary-local version is materially broader than the
   corollary assuming the whole tight family laminar.
7. Try to produce a counterexample if “laminar” is weakened to balanced or
   totally balanced incidence.  This determines whether the next research
   step is a true extension or a false route.

## Reproduction

From the repository root:

```bash
python src/verify_laminar_lmin_domain.py \
  --output results/laminar_lmin_domain.json
cd paper3
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
pdflatex -interaction=nonstopmode -halt-on-error wrapper.tex
```

The finite audit is only a bug detector, not proof evidence.  Please report
mathematical correctness, literature novelty, the strongest defensible
statement, and any missing hypotheses separately.
