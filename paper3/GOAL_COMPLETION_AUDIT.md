# Breakthrough-goal completion audit

Audit date: 2026-08-03.  Branch:
`codex/n5-exact-leximin-counterexample`.

This file maps each requested research deliverable to current manuscript and
verification evidence.  It distinguishes mathematical completion from the
remaining external-review and GitHub-publication gates.

## 1. Compact certificate for `phi=a/4`

**Status: proved and independently replayed.**

The proof in `sections_leximin.tex` gives three Maschler stages.  The
coalition `125` plus efficiency bounds the first gain level by `3/4` and pins
players `3,4,6,7`; the tight constraints `13` and `27` then bound the second
level by `3/2` and pin player `5`; efficiency bounds the final level by `9/4`
for players `1,2`.  All bounds are attained at `a/4`.

Evidence:

- `src/verify_n7_exact_carrier_counterexample.py`
- `src/verify_n7_exact_carrier_counterexample_leximin.py`
- `paper3/N7_EXACT_CARRIER_COUNTEREXAMPLE.md`

## 2. Conceptual six/seven threshold

**Status: proved without relying on the large support census.**

After quotienting a violating six-player eta-dual by its target column and
positive singleton columns, at most three positive residual weights remain.
Two independent equal-subset-sum relations classify the possibilities.  The
`3+3` split has none; the `4+2` split has one orbit,

```text
1_S + e_1 + 2e_2 + 1_35 + 1_136 + 2*1_456 = 3*1_N,
```

whose objective is at least `2*gamma` by the carrier inequality for `C={4}`.
The old 65,133-support scan and 1,489-orbit exact-cone audit are independent
redundancy, not logical inputs to the new proof.

Evidence:

- `src/verify_n6_three_level_matrix_classification.py`
- `src/verify_n6_three_level_eta_duals.py`
- `paper3/N6_CARRIER_THEOREM.md`

## 3. Seven-player classification

**Status: all requested structural questions answered.**

- **Uniqueness:** false; an open two-parameter wedge gives inequivalent
  examples beyond permutation and scaling.
- **Core and generators:** the primary core is `conv{0,a,b}` and three lower-
  envelope generators are necessary and sufficient.
- **Target size:** three is minimal by the general two-player target theorem.
- **Outside-set size:** three is minimal at seven players.  The complete
  `5+2` determinant census leaves five orbits, all with exact lower bound
  three; an explicit `4+3` leximin obstruction attains the bound.
- **Robustness:** both the target-triple and outside-triple constructions
  persist on relatively open two-parameter wedges.

Evidence:

- `src/verify_n7_exact_carrier_structure.py`
- `src/verify_n7_exact_carrier_family.py`
- `src/verify_n7_exact_carrier_outside_triple_counterexample.py`
- `src/verify_n7_exact_carrier_outside_triple_leximin.py`
- `src/verify_n7_exact_carrier_outside_triple_family.py`
- `src/verify_n7_three_level_eta_dual_audit.py`
- `results/n7_three_level_eta_dual_audit.json`

## 4. Complete dimension threshold

**Status: proved for every finite dimension.**

Appending null players produces the exact game
`v+(T)=v(T intersect N)`.  Singleton rationality and the old-grand constraint
force every new coordinate to zero, so the enlarged core is exactly the old
core times fixed zeros.  The old Lmin coordinates, all carrier differences,
and eta therefore remain unchanged.  This proves validity exactly through
six players and failure for every `n>=7`, not merely through a tested cutoff.
The verifier replays finite instances through a user-selected regression
cutoff.

Evidence: `src/verify_n7_exact_carrier_dummy_extensions.py`.

## 5. Connection to coalitional monotonicity

**Status: settled negatively, with the failed proof mechanism localized.**

First, a binding-bumpable seven-player carrier failure has a completely
monotone Lmin path, proving the carrier inequality is not necessary for
monotonicity.  Second, a different exact five-player pair raises only
`v(1345):18->20` while target players `3` and `5` each lose `1/2`; the entire
exact affine path has a solver-free certificate.  A later exact symbolic
bridge proves normalized Lmin coalitionally monotonic through four players,
so the five-player failure is dimension-minimal.

Evidence:

- `src/verify_n7_binding_carrier_monotone_path.py`
- `src/verify_n5_exact_leximin_monotonicity_counterexample.py`
- `src/verify_n4_exact_lmin_pes_bridge.py`
- `results/n4_exact_lmin_pes_bridge.json`

## 6. Focused prior-art search

**Status: completed with cautious claim discipline.**

`PRIOR_ART_CARRIER.md` records the search scope and distinguishes the new
target-conditioned carrier theorem from prior minimal-balanced enumeration,
the known exact-game cone, ordinary Lmin/Lmax, and monotonicity results on
other domains.  No matching carrier threshold, triangular family, exact-game
proper-coalition Lmin counterexample, or four-player Lmin=Lmax bridge was
located.  The manuscript uses “we are not aware,” not “first.”

## Remaining nonmathematical gates

These do not negate the verified results but remain necessary before a
submission or public priority claim:

1. A specialist should search MathSciNet, zbMATH, and citation chains.
2. The new five-player counterexample and four-player symbolic bridge need an
   external hostile audit; the existing review predates them.
3. The focused branch is not on GitHub because both SSH authentication and the
   configured `gh` token fail.
