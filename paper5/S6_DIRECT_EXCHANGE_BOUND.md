# Direct exactness-exchange proof that `s(6)=2/3`

Date: 2026-08-09

## Theorem and status

For every singleton-normalized exact game `v` on six players with
`T=v(N)>0`,

```text
||Lmin(v)-Lmax(v)||_1 / T <= 2/3.
```

The explicit exact game `G(2,3)` attains `2/3`.  Consequently

```text
s(6)=2/3.
```

The upper bound is a **direct table-free computer-assisted theorem**.  It
does not use the generator normal form, support/table census, equality
classification, a path or continuity theorem, first crossing, or either
local equality-profile handover.  Its only game-theoretic inputs are
singleton exactness and the defining lexicographic optimality of Lmin and
Lmax.  Its finite component is an exact QF_LRA split into the fifteen possible
sign counts of `Lmin_i-Lmax_i`.

All fifteen minimized formulas are UNSAT in Z3 and cvc5.  cvc5 emits CPC with
`--proof-pedantic=1` and `--no-proof-allow-trust`; no forbidden proof marker is
present; Ethos checks all fifteen proofs as `correct`.  The aggregate CPC size
is 52,856,780 bytes.  This result has not yet received external specialist
review, so it should not yet be presented as externally validated or as a
field-level breakthrough.

## 1. Normalize and split by comparison signs

Scale to `T=1` and write

```text
x=Lmin(v),       z=Lmax(v).
```

Both points are nonnegative and sum to one.  Put

```text
P={i:x_i>z_i},   M={i:z_i>x_i},   E={i:x_i=z_i}.
```

If the two selections differ, then `p=|P|` and `m=|M|` are positive and
`p+m+e=6`.  Up to a common relabeling of players there are exactly fifteen
such triples.  In each one,

```text
||x-z||_1 = 2 sum_{i in P}(x_i-z_i).                    (1)
```

The contradiction formulas assert that the right side of (1) is strictly
greater than `2/3`.

## 2. Exactness witnesses and automatic anchors

For every player `i`, exactness at `{i}` supplies a core allocation `q^i`
with `q^i_i=v({i})=0`.  The proof uses only nonnegativity, efficiency, and
this zero coordinate from each witness.

Three anchors follow directly from convexity of the core:

1. **Lmax has no singleton top stratum.**  If `z_i` were the unique maximum,
   then `z_i>0`; a short move from `z` toward `q^i` would lower the unique old
   maximum before any lower coordinate could cross it, improving the
   decreasing lexicographic vector.
2. **Lmax-top cross anchor.**  Some top player of `z` has `x_i>=z_i`.
   Otherwise a short move from `z` toward `x` would lower every old top
   coordinate.
3. **Lmin-bottom cross anchor.**  Some bottom player of `x` has `z_i<=x_i`.
   Otherwise a short move from `x` toward `z` would raise every old bottom
   coordinate.

These arguments use only line segments between core points and the positive
gap from the relevant extreme stratum to the next stratum.

## 3. Universal exactness blocker lemma

Let `h(N)=0`.  The finite formulas use the following sufficient improvement
tests.

- At `x`, `h` improves Lmin if the lowest payoff level touched by `h` has at
  least one positive coefficient and no negative coefficient.
- At `z`, `h` improves Lmax if the highest payoff level touched by `h` has at
  least one negative coefficient and no positive coefficient.

The predicates in `lex_improves` express exactly these sufficient conditions;
they do not claim to recognize every improving direction.

As a differential control, `audit_lex_improvement_predicate.py` compares the
pivot formulation with a separately written first-affected-stratum criterion
on all 4,683 labeled weak orders, all 1,610 bound-two directions, and both
sides: 15,079,260 Boolean comparisons with zero mismatches.

If such an `h` improves a selection `y`, optimality implies that some proper
coalition `S` tight at `y` has `h(S)<0`.  Otherwise every tight inequality has
nonnegative derivative, every nontight inequality has positive slack, and a
sufficiently short step `y+epsilon h` remains in the core while improving the
selection.

Core membership of the opposite selection and all six exactness witnesses
then gives the necessary blocker conditions

```text
y=x:  z(S)>=x(S) and q^i(S)>=x(S) for all i;             (2)
y=z:  x(S)>=z(S) and q^i(S)>=z(S) for all i.             (3)
```

The SMT formulas disjoin (2) or (3) over all proper coalitions with `h(S)<0`.
They do not encode a game or require the eligible coalition to be genuinely
tight.  They are therefore relaxations of the exact-game problem.  UNSAT of
the relaxation is sufficient for the theorem.

## 4. Complete strict-distance classification

All efficiency-preserving integer directions with coefficients in `[-1,1]`
already eliminate thirteen sign-count cases.  Only `(p,m,e)=(2,3,1)` and
`(3,3,0)` require the pool with coefficients in `[-2,2]`.  No canonical
payoff profile and no equality-specific premise is used.

UNSAT cores were used only to find smaller direction menus.  Every retained
menu was rebuilt without assumption literals and checked again.  The frozen
suite contains 252 labeled directions in total, occupying 64 sign-preserving
orbit signatures.

| sign counts `(p,m,e)` | direction bound | retained directions | sign orbits |
|---|---:|---:|---:|
| `(1,1,4)` | 1 | 1 | 1 |
| `(1,2,3)` | 1 | 1 | 1 |
| `(1,3,2)` | 1 | 1 | 1 |
| `(1,4,1)` | 1 | 1 | 1 |
| `(1,5,0)` | 1 | 0 | 0 |
| `(2,1,3)` | 1 | 2 | 2 |
| `(2,2,2)` | 1 | 5 | 2 |
| `(2,3,1)` | 2 | 14 | 5 |
| `(2,4,0)` | 1 | 8 | 1 |
| `(3,1,2)` | 1 | 2 | 2 |
| `(3,2,1)` | 1 | 52 | 17 |
| `(3,3,0)` | 2 | 71 | 18 |
| `(4,1,1)` | 1 | 2 | 2 |
| `(4,2,0)` | 1 | 90 | 9 |
| `(5,1,0)` | 1 | 2 | 2 |

Every row asserts the common simplex, signs, strict distance, three anchors,
six singleton witnesses, and only its retained blocker implications.  Every
row is UNSAT.  Since the sign split is exhaustive, a strict counterexample
cannot exist.

## 5. Lower bound and equality information

The family theorem for `G(p,k)` gives

```text
rho(G(p,k)) = 2(p(k-1)-1)/(k(p+1)).
```

At `(p,k)=(2,3)` this is `2/3`, and the family membership proof establishes
that the game is exact and singleton-normalized.  This supplies the matching
lower bound.

The separate proof-object family in `EQUALITY_EXCHANGE_CLASSIFICATION.md`
shows more: every exact six-player game attaining `2/3` has, up to player
permutation, one of the two canonical starved or positive payoff pairs.  That
rigidity theorem is not needed for the upper bound.

## 6. Proof-object boundary and review standard

The checked implication is

```text
strict exact-game counterexample
  => one of 15 sign labels + anchors + singleton witnesses + blockers
  => one of 15 frozen QF_LRA formulas
  => contradiction.
```

The CPC objects independently prove the last implication for the exact
formulas.  Human review must still verify the first implication: normalization,
sign relabeling, the three anchors, both lex-improvement predicates, and the
exactness blocker lemma.  None is a large theorem, but each is load-bearing.

The highest-risk implementation overlap has a second lane.  The two cases
that require coefficient-two directions, `(2,3,1)` and `(3,3,0)`, are rebuilt
by an independently formulated encoder.  It shares only the frozen retained
menus as theorem data and imports no production encoder, lex predicate,
blocker, direction pool, minimizer, or serializer.  Both base systems with the
exchange implications removed are SAT; both full systems are UNSAT in Z3 and
cvc5; fresh trust-disabled CPC proofs check `correct` in Ethos.

The three largest menus have also been quotiented under relabelings internal
to `P`, `M`, and `E`: 213 labeled directions become 44 sign-role orbits and
eight oriented coefficient templates, or six up to sign reversal.  The
one-for-one and two-for-two templates cover 179 of the 213 rows.  This is a
readability reduction, not an all-human replacement for the finite proof.

A second, proof-checked orbit reduction is stronger.  It retains complete
orbits but shrinks the three cases to 19 selected sign-role schemas and 136
labeled implications.  The `(3,2,1)` and `(4,2,0)` cases use only one-for-one
and two-for-two exchanges.  The balanced `(3,3,0)` case additionally uses one
asymmetric coefficient-two shape and its reversal.  Each of the three reduced
unguarded formulas is UNSAT in Z3 and cvc5 and has a fresh trust-disabled CPC
proof checked by Ethos; deleting any one selected orbit makes that reduced
relaxation SAT.  The SAT ablations establish irredundancy only inside the
relaxation and are not games or independent proof evidence.

`S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md` supplies the assertion-by-assertion
human soundness proof.  Its literal audit confirms that every original frozen
formula declares exactly 48 reals and consists of exactly 72 documented base
assertions followed only by its recorded direction implications.  This is the
review boundary that matters: a reviewer should prove or refute that every
genuine counterexample satisfies those assertions, not merely rerun UNSAT.

The direct proof makes the older first-crossing, equality-neighborhood, and
support-table programs logically unnecessary for `s(6)=2/3`.  They remain
valuable differential checks and structural information about the equality
boundary.  The old concern that leximin continuity may require a delicate
lexicographic theorem is now irrelevant to the upper bound.

## 7. Reproduction

Run from the repository root:

```text
python3 coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
python3 coopgames/verifiers/s6/verify_independent_bound_two.py
python3 coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output /tmp/strict_exchange_formula_interface.json
cmp /tmp/strict_exchange_formula_interface.json \
  coopgames/verifiers/s6/strict_exchange_formula_interface.json
python3 coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
python3 coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py \
  --output /tmp/strict_exchange_large_case_templates.json
cmp /tmp/strict_exchange_large_case_templates.json \
  coopgames/verifiers/s6/strict_exchange_large_case_templates.json
```

This byte-regenerates all fifteen strict SMT-LIB formulas from the minimized
menu audit, compares them with the frozen files, and verifies every stored
formula hash, proof hash, Z3/cvc5 verdict, forbidden-marker field, and Ethos
status.

The relevant paths are:

```text
coopgames/verifiers/s6/audit_equality_universal_exchange_relaxation.py
coopgames/verifiers/s6/minimize_equality_exchange_directions.py
coopgames/verifiers/s6/strict_exchange_direction_cores.json
coopgames/verifiers/s6/strict_exchange_sign_orbits.json
coopgames/verifiers/s6/audit_lex_improvement_predicate.py
coopgames/verifiers/s6/lex_improvement_predicate_audit.json
coopgames/verifiers/s6/export_strict_exchange_bound_smt.py
coopgames/verifiers/s6/generate_equality_exchange_certificates.py
coopgames/verifiers/s6/reproduce_strict_exchange_bound.py
coopgames/verifiers/s6/verify_strict_exchange_bound_certificates.py
coopgames/verifiers/s6/certificates/strict_exchange_*.{smt2,cpc,json}
coopgames/verifiers/s6/independent_bound_two_reconstruction.py
coopgames/verifiers/s6/verify_independent_bound_two.py
coopgames/verifiers/s6/independent_bound_two/*.{smt2,cpc,json}
coopgames/verifiers/s6/audit_strict_exchange_large_case_templates.py
coopgames/verifiers/s6/strict_exchange_large_case_templates.json
coopgames/verifiers/s6/audit_strict_exchange_large_case_orbit_cores.py
coopgames/verifiers/s6/strict_exchange_large_case_orbit_cores.json
coopgames/verifiers/s6/orbit_core_certificates/*.{smt2,cpc,json}
coopgames/verifiers/s6/verify_strict_exchange_orbit_core_certificates.py
coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py
coopgames/verifiers/s6/strict_exchange_formula_interface.json
coopgames/paper5/S6_COUNTEREXAMPLE_TO_SMT_INTERFACE.md
coopgames/paper5/S6_EXCHANGE_ORBIT_LEMMAS.md
coopgames/paper5/S6_LITERATURE_NOVELTY_AUDIT.md
```

The correct significance statement before external review is: a direct,
independently proof-checked fixed-dimension theorem resolving the six-player
case.  It is a major breakthrough for this project.  Whether it is novel and
important enough to be a field-level breakthrough depends on hostile review,
literature comparison, and conversion of at least the larger sign cases into
readable exchange arguments.

For a targeted exact regression of the sharp endpoint, run
`python3 coopgames/verifiers/s6/verify_g23_witness.py`. It rebuilds `G(2,3)`,
checks the generator exactifiers, recomputes both selections by exact staged
LP, and verifies `rho=2/3`. This is a bug audit; the family theorem remains
the proof of attainment.
