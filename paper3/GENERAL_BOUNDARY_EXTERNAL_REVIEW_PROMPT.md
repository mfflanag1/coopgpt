# Hostile external-review prompt: slack budgets and the sharp five/six threshold

Please conduct a hostile mathematical and novelty review of the new
exact-balanced boundary framework and the sharp small-poorer boundary result.

## Primary files

- `coopgames/paper3/wrapper.pdf`: rendered manuscript; the new material is in
  Lemma 5.39 through Theorem 5.45 (numbers may shift after edits).
- `coopgames/paper3/sections_leximin.tex`: source labels
  `lem:lx-exact-balanced-slack`, `lem:lx-boundary-cover`,
  `cor:lx-boundary-defect`, and `thm:lx-small-poorer-threshold`.
- `coopgames/paper3/GENERAL_BOUNDARY_OBSTRUCTION.md`: expanded derivation,
  prior-art boundary, and research interpretation.
- `coopgames/paper3/N4_N5_STRUCTURAL_THRESHOLD.md`: standalone sacrifice-budget
  proof and four-generator obstruction family for every dimension at least five.
- `coopgames/paper3/N5_N6_SMALL_POORER_THRESHOLD.md`: standalone statement and
  human proof of the six-player construction.

## Exact verification files

- `coopgames/src/verify_exact_balanced_slack_budget.py`
- `coopgames/results/exact_balanced_slack_budget.json`
- `coopgames/src/verify_n5_small_poorer_suffix.py`
- `coopgames/results/n5_small_poorer_suffix.json`
- `coopgames/src/verify_n5_unique_richest_boundary.py`
- `coopgames/results/n5_unique_richest_boundary.json`
- `coopgames/src/verify_unique_richest_family.py`
- `coopgames/results/unique_richest_family.json`
- `coopgames/src/verify_n6_two_poorer_suffix_counterexample.py`
- `coopgames/results/n6_two_poorer_suffix_counterexample.json`

The two `hunt_*small*boundary.py` scripts and their results are discovery-only
falsification searches.  Please do not count their no-hit output as proof.

## Claims to audit

1. Does exact balancedness, under the conventions of Csóka--Herings--Kóczy
   (2011) and Lohmann--Borm--Herings (2012), imply the slack-budget inequality
   `(SB)` with the stated sign?
2. Is the direct exact-face proof of the boundary-cover inequality `(BC)`
   valid for arbitrary nonnegative tight-coalition weights and
   `alpha>beta>=0`?  Check every inequality direction and the singleton
   normalization dependence.
3. Is the exact-balanced completion following `(BC)` correct both for
   `beta>0` and `beta=0`?  Is any hypothesis about the negative coalition or
   grand-coalition coefficient missing?
4. Is the boundary-defect program `(BD)` stated correctly, including
   attainment/finite-value issues and the conclusion that zero defect forces
   suffix tightness?
5. In the five-player monotonicity example, verify
   `1_135 + 1_345 + 1_2 - 1_35 = 1_N`, the four coalition slacks, and the claim
   that the exact boundary-defect optimum is one.
6. Audit the human unique-richest threshold theorem.  Does the protector
   packing exhaust all one-, two-, and three-poorer-player configurations?
   For every `m>=4`, do the four parametric generators have common total and
   define an exact lower-envelope game?  Do the four displayed coalition
   values force `Lmin=(1^m,m-2)`?  Does the circuit
   `1_{3r}+1_{4r}+sum_{i in P\{3,4}}1_i-1_r=1_N` attain the slack budget at
   equality?  Do the two pair inequalities, the convex combination
   `a*g4+(1-a)*g2`, and the averaging step prove the claimed closed-form Lmax
   and hence Lmin--Lmax separation in every dimension?  Check the endpoint
   `m=4` separately, where the coefficient of
   `e5=er` in `(m-4)e5` is zero.
7. For the five-player small-poorer lower bound, inspect whether the imported
   definition-level exact-face and stagewise KKT encoding genuinely covers all
   ordered stratum compositions and every boundary after one or two cumulative
   poorer players.  Do not infer this from the previous n=4 review alone.
8. For the six-player upper bound, verify directly that the six displayed
   integer allocations have common total, that their lower envelope is exact,
   and that the five displayed coalition inequalities prove
   `Lmin=(1,1,2,2,2,2)` without an unstated assumption.
9. Confirm that `v({3,4,5,6})=6<8=Lmin({3,4,5,6})`, establishing sharp failure
   of the small-poorer conclusion at six.

## Novelty questions

Please separately assess whether any of the following already appears in the
exact-game, exact-balancedness, egalitarian-core, exact-partition, or Lorenz
core literature:

- the quantitative slack-budget reading `(SB-H)`;
- the protector-completion/boundary-cover inequality `(BC)`;
- the canonical boundary-defect LP `(BD)`;
- the sacrifice-budget interpretation and sharp unique-richest threshold;
- the four-generator integral family with `Lmin=(1^m,m-2)` for every `m>=4`,
  its closed-form Lmax, and whether it is merely a padding or replication of a
  known example;
- the sharp result that a richer Lmin suffix with at most two poorer players is
  tight through five players but can be slack at six;
- the fixed six-player integer lower-envelope construction.

The manuscript already treats the exact-balancedness characterization and the
Arin--Iñarra transfer-blocking property as prior art.  Please flag any remaining
novelty overstatement.

## Reproduction

From `coopgames/` run:

```bash
python src/verify_exact_balanced_slack_budget.py \
  --output results/exact_balanced_slack_budget.json
python src/verify_n5_small_poorer_suffix.py \
  --output results/n5_small_poorer_suffix.json
python src/verify_n5_unique_richest_boundary.py \
  --output results/n5_unique_richest_boundary.json
python src/verify_unique_richest_family.py \
  --max-players 12 --exact-lmin-through 7 --exact-lmax-through 6 \
  --output results/unique_richest_family.json
python src/verify_n6_two_poorer_suffix_counterexample.py \
  --output results/n6_two_poorer_suffix_counterexample.json
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```

## Requested verdict

Return `verified`, `verified with qualifications`, or `not verified`; list
every issue with exact file and line references; classify it as fatal,
repairable, or expository; report the commands actually run; and give a
separate prior-art/novelty assessment.  Please do not treat solver agreement,
unsatisfiable cores, or random-search no-hit results as independent proof.
