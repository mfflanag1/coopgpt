# Exactness-aware exchange handover at the starved six-player profile

Date: 2026-08-09

This note removes the apparent need for staged Farkas certificates in the
504 starved-only refinements of the canonical `(4,2)` by `(2,4)` equality
profile.  The replacement is a finite family of ordinary lexicographic
exchange directions whose possible tight blockers are restricted by
singleton exactness.

The complete finite audit is exact rational QF_LRA evidence, not yet a human
proof of all 504 order types and not an independently checked proof-object
family.  Its value is structural: the former 131-row staged residue disappears
entirely.

## 1. The exactness-aware blocker lemma

Let `v` be singleton-normalized and exact, and put

```text
x=Lmin(v),             z=Lmax(v).
```

For every player `i`, exactness at `{i}` supplies a core point `q^i` with
`q^i_i=v({i})=0`.  Each `q^i` is nonnegative and has total `v(N)`.

Let `h` be efficiency-preserving.  If `h` lexicographically improves `x`
from below—at the first Lmin stratum on which it is nonzero, every coordinate
is nonnegative and at least one is positive—then Lmin optimality implies that
some proper `x`-tight coalition `A` has

```text
h(A)<0.                                                    (1)
```

Otherwise `x+epsilon h` stays in the core and improves Lmin for all
sufficiently small positive `epsilon`.  Tightness and core feasibility of
`z,q^0,...,q^5` give the necessary blocker inequalities

```text
z(A)>=x(A),             q^i(A)>=x(A) for every i.          (2)
```

The Lmax statement is identical except that `h` is negative at its first
changed top stratum and a blocker must obey

```text
h(A)<0,
x(A)>=z(A),             q^i(A)>=z(A) for every i.          (3)
```

Thus any finite menu of lex-improving directions forces one blocker satisfying
`(2)` or `(3)` for every menu member.  Proving those simultaneous blockers
algebraically impossible contradicts optimality.  This lemma uses no staged
normal certificate and no characteristic-function variables.

## 2. Starved roles and the handover rule

Aggregate a contiguous refinement back to the starved coarse table

```text
             Lmax-low   Lmax-high
Lmin-low         2           2
Lmin-high        0           2.
```

Call the three two-player cells `N`, `P`, and `R`, respectively.  In an
outward comparison they obey

```text
x_i>z_i on N and R,             z_i>x_i on P.             (4)
```

Use the same purely order-theoretic handover as the earlier packet census:

```text
choose Lmax iff some R player is strictly below both P players
in the refined Lmax order; choose Lmin otherwise.          (5)
```

Rule `(5)` chooses Lmax on 128 refinements and Lmin on 376.  The new audit
uses only `(4)`, ordered payoff strata and totals, distance `>2/3`, the six
simplex witnesses `q^i`, and the blocker lemma on the selected side.

## 3. Complete finite result

`starved_exactness_menu_audit.json` covers all 504 starved-only refinements.
For 502 rows, a menu drawn from primitive directions with coefficients in
`{-1,0,1}` is contradictory.  Exactly two rows—survivor indices `932` and
`2332`, both Lmin rows with role word `NPPNRR`—require coefficient two.

The minimized menu sizes are

```text
size 1: 189             size 2: 84
size 3: 115             size 4: 54
size 5: 53              size 6: 7
size 8: 2.
```

Only four direction multisets occur after forgetting player labels:

```text
(-1, 0, 0, 0, 0, 1),
(-1,-1, 0, 0, 1, 1),
(-1,-1,-1, 1, 1, 1),
(-1,-1,-1, 0, 1, 2).                                  (6)
```

The last shape occurs only in the two exceptional menus.  Consequently the
entire starved neighborhood is controlled by equal-size subset exchanges,
apart from one explicit coefficient-two boundary shape.

The earlier diagnostic decomposition

```text
222 payoff directions + 151 payoff menus + 131 staged rows
```

remains a valid ablation record, but “staged rows” is no longer the correct
structural interpretation.  All 131 are closed by exactness-aware menus of
sizes two through six, and the same mechanism closes all other starved rows.

## 4. Status and next theorem

This is a meaningful local simplification, not yet an unconditional proof of
`s(6)=2/3`.

What is now established computationally:

1. the selected-side formulas are exact linear arithmetic;
2. all 504 formulas are UNSAT;
3. the audit byte-reproduces from eight bounded shards plus the two explicit
   bound-two exceptions; and
4. the formulas no longer rely on a staged Farkas encoding.

What remains:

1. normalize the 504 menus by role word and the weak Lmin/Lmax order they use;
2. compress them into a small table-independent exchange-lemma family;
3. export each abstract formula to Z3 and cvc5, generate trust-free CPC, and
   check it with Ethos; and preferably
4. extract readable inequalities proving the four direction shapes cannot all
   have exactness-eligible blockers when the distance exceeds `2/3`.

That compression, combined with the already compressed positive neighborhood,
would complete the local first-crossing barrier conditional on the equality
classification.  A fully unconditional theorem would still need a structural
or proof-object replacement for the 3,348 equality-type exclusions and hostile
review of the normal-form and continuity arguments.

## 5. Reproduction

From the repository root, using a Python environment with `z3-solver`:

```bash
python3 coopgames/verifiers/s6/reproduce_starved_exactness_menus.py
```

The driver runs eight 63-row bound-one shards in bounded parallelism, reruns
the two exceptional rows at bound two, validates the complete position and
index sets, merges them, and byte-compares the result with
`starved_exactness_menu_audit.json`.
