# Third reconstruction of the two coefficient-two cases

Date: 2026-08-10

## 1. Purpose and independence boundary

The strict six-player proof uses coefficient magnitude two only in the
`(2,3,1)` and `(3,3,0)` sign cases.  The production encoder and the existing
independent encoder both construct solver expressions through Z3 and express
activation through a first-affected-level pivot.  The third formulation is
designed to expose a correlated error in either choice.

```text
coopgames/verifiers/s6/third_bound_two_direct_smt.py
```

imports only the Python standard library.  It imports neither previous
encoder and does not import Z3.  It serializes SMT-LIB directly, enumerates
coalitions by cardinality combinations, and shares only the frozen retained
direction menus as theorem data.

This is independent formulation evidence for the machine layer.  It is not
external review and does not independently prove the selection anchors,
lexicographic-improvement lemma, or negative-tight-blocker lemma.  Those human
claims remain the gate in `S6_INTERFACE_REVIEW_WORKSHEET.md`.

## 2. A different activation formula

Let `R={i:h_i>0}` and `D={i:h_i<0}`.  Since `h(N)=0` and `h` is nonzero,
both sets are nonempty.

For Lmin, the lowest affected payoff level contains a positive coefficient
and no negative coefficient exactly when

```text
there exists r in R such that y_r < y_d for every d in D. (Tmin)
```

Indeed, if `(Tmin)` holds then the minimum payoff on `R union D` is attained
in `R` only.  Conversely, any positive player at the lowest affected level is
strictly below every member of `D`.  No pivot-to-pivot comparison within `R`
is needed.

The Lmax dual is

```text
there exists d in D such that y_d > y_r for every r in R. (Tmax)
```

Thus the third encoder uses strict support separation, not the existing pivot
syntax.  Coefficient magnitudes affect the negative-cut family but not these
activation equivalences.

The no-unique-Lmax-top anchor is also written differently.  Instead of a tied
top disjunction or the negation of a unique strict maximum, it asserts

```text
for every i, there exists j!=i with z_j>=z_i.
```

For a finite vector this is equivalent to saying that no coordinate is the
unique maximum.

## 3. Complete reconstruction

The two direct-text formulas contain:

| case | base assertions | direction rows | negative cuts | comparisons |
|---|---:|---:|---:|---:|
| `(2,3,1)` | 72 | 14 | 264 | 1,848 |
| `(3,3,0)` | 72 | 71 | 1,462 | 10,234 |
| **total** | | **85** | **1,726** | **12,082** |

For each case, the verifier checks every third assertion against the
corresponding production assertion and the corresponding second-encoder
assertion after renaming variables.  This gives

```text
2*(86+143)=458
```

exact logical-equivalence queries.  All are UNSAT.  Both 72-assertion base
systems are SAT, while both full third formulas are UNSAT.

Two mutations are detected on every one of the 85 direction rows:

1. replace strict support separation by non-strict separation; and
2. delete the first negative-cut alternative.

The second control is a local row-semantic test.  Some first-listed cuts are
redundant after all global base assertions are imposed; local inequivalence is
the correct test for whether the complete mathematical disjunction was
reconstructed.

## 4. Reproduction

```bash
python3 coopgames/verifiers/s6/third_bound_two_direct_smt.py \
  --output-dir /tmp/third_bound_two
cmp /tmp/third_bound_two/audit.json \
  coopgames/verifiers/s6/third_bound_two/audit.json
cmp /tmp/third_bound_two/p2_n3_t1.smt2 \
  coopgames/verifiers/s6/third_bound_two/p2_n3_t1.smt2
cmp /tmp/third_bound_two/p3_n3_t0.smt2 \
  coopgames/verifiers/s6/third_bound_two/p3_n3_t0.smt2
python3 coopgames/verifiers/s6/verify_third_bound_two.py \
  --output /tmp/third_bound_two_verification.json
cmp /tmp/third_bound_two_verification.json \
  coopgames/verifiers/s6/third_bound_two/verification.json
```

The verifier requires a Z3-enabled Python only for parsing and equivalence
checks.  The formula generator itself remains standard-library-only.

The existing cvc5/CPC/Ethos proof objects certify the semantically equivalent
frozen systems.  This third reconstruction adds a direct Z3 UNSAT check and
row equivalence; it does not claim a third independently generated proof
object.
