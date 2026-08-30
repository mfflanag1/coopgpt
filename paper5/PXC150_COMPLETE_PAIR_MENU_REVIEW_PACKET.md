# Hostile review packet — PXC150 complete pair-menu bottleneck

Status: internal conventional proof plus two exact implementations. No external cooperative-game specialist has reviewed correctness or prior art. Do not treat the result as a field-level breakthrough.

## Claim under review

For a block-symmetric singleton-normalized exact game on
`U^m,b,c,d,A^u,B^v,g`, suppose the candidate Lmin allocation is
`(1^m;X_b,X_c;1,1^u,1^v,1)` and all rows

```text
P_ij = b c d g a_i b_j
H_ij = c g a_i b_j
R3   = b c d A B
R5_e = b e g
```

are tight. With `r=u+v` and `h=min(u,v)`, PXC150 claims

```text
X_b <= m(r-1)/(r-2),
X_c <= m-2+(m+r-2)/(h-1).
```

The proof uses separate exact core witnesses attaining singleton values at
`b` and `c`; it does not assume that the game has finitely many displayed
generators.

For `u=v=k`, both bounds are attained by the exact three-generator family
`Q_{m,k}` in `(PXC150c)`. The claimed selectors are

```text
Lmin = X,
Lmax = lambda X+(1-lambda)B0,
lambda = ((2k-1)m+2(k-1))/(m(4k-1)).
```

The resulting ratio is

```text
rho = 12(2k-1)(km-k+1)/((4k-1)(4k^2+6km-3m-4)),
lim_{m/k->a} rho = 3a/(3a+2) < 1.
```

This is a no-go theorem only for the displayed simultaneous-tightness
skeleton. It is not an upper bound for arbitrary pair menus, four-generator
games, or exact games.

## Human proof dependency map

1. Exactness and singleton normalization provide symmetry-averaged `b=0`
   and `c=0` core points.
2. `R3` plus efficiency bounds the `g` coordinate by `m+1` at both points.
3. `P` plus `R5` at the `b=0` point proves the `X_b` bound.
4. `P` plus `H` at the `c=0` point proves the `X_c` bound.
5. In the balanced realization, generator zero sets prove exactness and
   singleton normalization; complements of `P_ij` cap the Lmin floor.
6. A weighted Lmax cover uses `bd`, every `cde`, and every `Ucdeg`. Its
   excess incidence is supported on `c,d` with weights summing to one.
7. Equality in that cover pins `b,c,d,A,B`; the tight `beg` row and
   efficiency resolve the remaining `g/U` trade.
8. Direct coordinate comparison gives the overlap and ray limit.

## Authoritative paths

- Theorem and proof: `paper5/divergence.tex`, displays `(PXC150a)--(PXC150e)`.
- Primary symbolic/transcription verifier:
  `verifiers/divergence/verify_pxc150_pair_menu_three_generator.py`.
- Primary artifact:
  `verifiers/divergence/pxc150_pair_menu_three_generator.json`.
- Independent staged-selector implementation:
  `verifiers/divergence/verify_pxc150_pair_menu_three_generator_independent.py`.
- Independent artifact:
  `verifiers/divergence/pxc150_pair_menu_three_generator_independent.json`.
- Program status: `paper5/MECHANISM_PRICE_PROGRAM.md`, section 20.
- Protected statement: `paper5/PROTECTED_RESULTS_LEDGER.md`.

## Exact reproduction

From the parent directory containing `coopgames/`:

```bash
python3 coopgames/verifiers/divergence/verify_pxc150_pair_menu_three_generator.py \
  --output /tmp/pxc150-primary.json
cmp coopgames/verifiers/divergence/pxc150_pair_menu_three_generator.json \
  /tmp/pxc150-primary.json

python3 coopgames/verifiers/divergence/verify_pxc150_pair_menu_three_generator_independent.py \
  --output /tmp/pxc150-independent.json
cmp coopgames/verifiers/divergence/pxc150_pair_menu_three_generator_independent.json \
  /tmp/pxc150-independent.json

bash coopgames/paper5/verify_release.sh
```

The first verifier checks symbolic identities, all claimed row values,
weighted-cover loads and objectives, equality deductions, overlap formulas,
and a rational grid. The second independently generates every coalition
orbit and recomputes both staged selectors with Z3 QF_LRA. A one-unit
perturbation of `G0` undercuts `beg` and changes Lmin, serving as a
load-bearing negative control. Neither finite grid is offered as proof of
the all-parameter theorem.

## Questions for hostile review

1. Does exactness justify the separate singleton-attaining core witnesses
   exactly as used after block symmetrization, including all quantifiers?
2. Is the subtraction of `P_ij` and `R3` from efficiency valid with the
   displayed role multiplicities?
3. Does the weighted-cover incidence identity have the correct primal-dual
   sign, normalization, and efficiency multiplier?
4. Does equality in the dual really force every positively weighted row and
   both coordinate caps to be tight?
5. Is the final two-coordinate `g/U` argument sufficient for the entire
   leximax selector rather than only its first minimax stage?
6. Is `Q_{m,1}:=H_m` described clearly as a calibrated boundary definition,
   rather than an algebraic continuation of singular formulas?
7. Is the no-go scope stated narrowly enough? In particular, does any line
   accidentally imply a classification of all pair-indexed or all
   four-generator mechanisms?
8. Are the two witness bounds, weighted-cover identity, or the combined
   complete-pair-menu obstruction already known under exact-game,
   balanced-collection, semi-balanced-system, or Lorenz-solution language?

Please report critical, major, minor, and presentational findings separately,
and distinguish correctness, mathematical significance, and novelty.
