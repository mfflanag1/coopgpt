# Hostile external review — Lmin-tight-skeleton retraction

Please try to falsify the proposed support-independent theorem rather than
polish its exposition.  The theorem says that a singleton-normalized exact
game may be replaced by the lower envelope of the polytope defined only by
efficiency, nonnegativity, and the proper coalitions tight at Lmin, without
changing Lmin or the tight/slack status of any coalition.

## Authoritative paths

- Human proof:
  `coopgames/paper3/LMIN_TIGHT_SKELETON_RETRACTION.md`
- Manuscript theorem `thm:lx-tight-skeleton-retraction`:
  `coopgames/paper3/sections_leximin.tex`
- Compiled manuscript:
  `coopgames/paper3/wrapper.pdf`
- Independent finite audit:
  `coopgames/src/verify_lmin_tight_skeleton_retraction.py`
- Reproducible output:
  `coopgames/results/lmin_tight_skeleton_retraction.json`

## Claims to rederive

1. For `Core(v) subseteq K_phi`, identify exactly where singleton
   normalization is used and confirm that exactness gives
   `min_Core(v) x(A)=v(A)` for every coalition.
2. Check the pointwise inequality `R_phi(v)<=v` and both directions of
   preservation of the complete tight/slack pattern.  Look especially for a
   coalition omitted from the skeleton that could become newly tight.
3. Prove both inclusions `Core(R_phi(v))=K_phi`.  Check that the new singleton
   values really are zero and that no unlisted coalition inequality cuts the
   proposed core.
4. Audit exactness of the new game for every coalition, including `empty` and
   `N`, using attainment on the compact polytope.
5. Rebuild the progressive Lmin induction.  At every strict payoff boundary,
   sum the strict richer-side cover and use efficiency to derive

   ```text
   sum_(i in L_j) (alpha_j-d_i)(x_i-phi_i) <= 0.
   ```

   Verify that earlier strata are already fixed, every coefficient on the
   current stratum is positive, and the last stratum follows from efficiency.
   Try examples with three or more payoff levels; do not accept a two-level
   argument as sufficient.
6. Verify idempotence from equality of the total and the complete tight set.
7. Check rational scaling: the conclusion is an integral characteristic
   function after one common scaling, not necessarily an integral vertex
   description before scaling.
8. Decide whether this construction is already known under another name in
   the literature on exact games, coherent lower probabilities, core
   representations, property I, egalitarian solutions, or polyhedral
   retractions.  The component facts are not claimed new:
   - property I and egalitarian-core blocking are prior art;
   - the strict-cover lemma is presented only as a quantitative consequence;
   - the lower envelope/exact cover is the known unique exact game with a
     given balanced game's core.
   The candidate claim is the combined idempotent operation preserving Lmin
   and every coalition's exact-partition tightness status.
9. Audit Corollary `cor:lx-tight-skeleton-realization` as a genuine converse.
   Starting only from `(T,phi)`, verify that coordinate-zero certificates and
   one strict cover per payoff boundary suffice for a normalized exact game
   with Lmin `phi`.  Verify that the omitted-coalition strict inequalities are
   necessary and sufficient for the proper tight set to be exactly `T`.
   Decide whether this is a substantive hypergraph realization theorem or a
   routine restatement of property I plus lower-envelope duality.

## Reproduction

From `coopgames/` run:

```bash
python src/verify_lmin_tight_skeleton_retraction.py \
  --output /tmp/lmin_tight_skeleton_retraction.json
cmp /tmp/lmin_tight_skeleton_retraction.json \
  results/lmin_tight_skeleton_retraction.json
```

The audit includes a three-stratum five-player case, a four-co-singleton
six-player case, and a three-column seven-player case.  It is audit evidence,
not a substitute for the dimension-free proof.

## Required calibration

Please conclude with one of:

- false;
- correct but essentially a known/repackaged polyhedral fact;
- correct and useful, but not field-level;
- correct and plausibly a major conceptual advance, subject to definitive
  literature review.

Do not call it a breakthrough merely because it compresses the existing
examples.  Explain whether it actually changes the proof architecture or
only renames the active-constraint polytope.
