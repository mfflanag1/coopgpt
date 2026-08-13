# External review packet: atomic common-two-flat quotient theorem

Review target: branch `codex/hybrid-overlap-facets`, theorem
`atomic common-two-flat quotient bound`.  This result has **not** yet been
externally validated and is not claimed novel.

## Claimed theorem

Let a nonnegative exact weighted four-role game have positive integer role
weights `h`, total atomic weight `n>=6`, and zero singleton worth on every
unit-weight role.  If weighted Lmin and weighted Lmax share endpoints of two
independent complementary pair-sum slabs, then

```text
O/T >= 4n/[n^2-(n mod 2)].
```

The claim is only the common-two-flat branch of the quotient program.  It
does not cover hinged or opposite-endpoint transitions between different
pair-slab edges, does not finish the carrier/separator gluing theorem, and
does not classify every equality game or exact-cone facet.

## Proof dependency map

1. Four-role cores are exactly an efficiency hyperplane cut by four
   coordinate intervals and three complementary pair-sum slabs.
2. On a common-two-flat line, weighted Lmin/Lmax are the two middle entries
   of a `2 by 2` crossing-time matrix; diagonal middle gaps are impossible.
3. With arbitrary nonnegative effective endowments, the exact adjacent
   unit-gap cost is
   `S_0(p,r;q,b)=2+p/q+(p+q+b)/r`, with `q<=b`.
4. Human integer inequalities prove the target for every `n>=10`.  At
   `n=6,7,8,9`, only six ordered relaxed weight rows can fall below target.
5. Weighted Lmin is max-min fair and weighted Lmax is min-max fair in the
   role per-capita coordinates.  This gives a stratum-free quantified-LRA
   selector definition.
6. For the six residual rows, the verifier retains a core witness attaining
   each required zero unit singleton, relaxes all other exactness attainment,
   and splits 12 common-endpoint orientations by 16 overlap sign cells.  Z3
   returns unsat on all 1,152 cells, with zero unknowns.

The human hub-payment lemma and its finite unit-hub corollary are additional
structural checks, not necessary for the final 1,152-cell relaxation.

## Exact paths

```text
coopgames/paper5/HYBRID_OVERLAP_FACET_PROGRAM.md
  FEC1--FEC5; EWS1--EWS31
coopgames/paper5/divergence.tex
  Theorem common-two-atomic and preceding endowed-seesaw argument
coopgames/paper5/PROTECTED_RESULTS_LEDGER.md
coopgames/verifiers/divergence/verify_weighted_endowed_seesaw.py
coopgames/verifiers/divergence/weighted_endowed_seesaw.json
coopgames/verifiers/divergence/verify_common_two_finite_z3.py
coopgames/verifiers/divergence/common_two_finite_z3.json
coopgames/verifiers/divergence/verify_weighted_fairness_selector.py
coopgames/verifiers/divergence/weighted_fairness_selector.json
coopgames/verifiers/divergence/verify_common_face_endowment_scope.py
coopgames/verifiers/divergence/common_face_endowment_scope.json
```

Discovery-only controls, not proof evidence:

```text
coopgames/verifiers/divergence/explore_weighted_four_role_faces.py
coopgames/verifiers/divergence/weighted_four_role_face_discovery.json
coopgames/verifiers/divergence/search_common_face_finite_exactness.py
coopgames/verifiers/divergence/common_face_finite_exactness_search.json
```

## Reproduction

Run from the repository root:

```bash
python3 coopgames/verifiers/divergence/verify_weighted_endowed_seesaw.py \
  --output /tmp/weighted-endowed-seesaw.json
cmp coopgames/verifiers/divergence/weighted_endowed_seesaw.json \
  /tmp/weighted-endowed-seesaw.json

python3 coopgames/verifiers/divergence/verify_common_two_finite_z3.py \
  --output /tmp/common-two-finite-z3.json
cmp coopgames/verifiers/divergence/common_two_finite_z3.json \
  /tmp/common-two-finite-z3.json

python3 coopgames/verifiers/divergence/verify_weighted_fairness_selector.py \
  --output /tmp/weighted-fairness-selector.json
cmp coopgames/verifiers/divergence/weighted_fairness_selector.json \
  /tmp/weighted-fairness-selector.json

PYTHONPATH=coopgames/verifiers/divergence:coopgames/src python3 \
  coopgames/verifiers/divergence/verify_common_face_endowment_scope.py \
  --output /tmp/common-face-endowment-scope.json
cmp coopgames/verifiers/divergence/common_face_endowment_scope.json \
  /tmp/common-face-endowment-scope.json

bash coopgames/paper5/build_arxiv_release.sh
```

The finite Z3 audit takes roughly 10--15 minutes on the development machine.

## Hostile review questions

1. Does the weighted max-min/min-max fairness criterion exactly characterize
   lexicographic optimization of the per-capita vector with each role value
   repeated according to its integer weight?
2. Does the coordinate-interval/pair-slab representation cover every
   four-role core after efficiency, with correct complement orientations?
3. Is retaining only zero-unit-singleton attainment a legitimate relaxation
   of objective A, so unsatisfiability proves the exact-game statement?
4. Do the symmetries reducing the unrestricted adjacent middle gap to
   `(p,r;q,b)`, `q<=b`, lose any labelled common-face orientation?
5. Is the derivation and attainment of
   `S_0=2+p/q+(p+q+b)/r` valid without face normalization?
6. Do the integer comparisons actually prove the target from `n=10` onward,
   and is the six-row list complete at `n=6,7,8,9`?
7. Does splitting 12 endpoint cells and 16 overlap sign cells exhaust the
   strict target-violation query, including boundary ties?
8. Is any statement accidentally promoted from a relative selection-face
   theorem to a full exact-game-cone facet theorem?

Please report correctness of the human argument, validity and completeness
of the finite encoding, equality scope, novelty, and significance as separate
verdicts.
