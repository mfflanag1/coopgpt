# Exactness-aware exchange handover at the starved six-player profile

Date: 2026-08-09

This note removes the apparent need for staged Farkas certificates in the
504 starved-only refinements of the canonical `(4,2)` by `(2,4)` equality
profile.  The replacement is a finite family of ordinary lexicographic
exchange directions whose possible tight blockers are restricted by
singleton exactness.

The complete finite audit first showed that the former 131-row staged residue
disappears entirely.  That audit has now been compressed further to two
table-free exact-QF_LRA formulas, one for each side of the order handover.
Both formulas have independently checked trust-free CPC proofs.  Readable
inequalities remain desirable, but the starved local neighborhood no longer
depends on a 504-table solver census.

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

## 4. Table-free two-branch compression

The finite audit suggests a stronger statement that does not name any payoff
partition or contingency table.  Fix labels `N={0,1}`, `P={2,3}` and
`R={4,5}`.  Retain only:

1. the signs `(4)` and strict coarse gaps `x_(N union P)<x_R` and
   `z_N<z_(P union R)`;
2. the starved-only identity `x_4=x_5`;
3. the standard selection anchors: Lmax has at least two top players, some
   Lmax-top player has `x_i>=z_i`, and some Lmin-bottom player has
   `z_i<=x_i`;
4. the six singleton-zero simplex witnesses;
5. exactness-aware one-for-one blockers on the nonselected side; and
6. exactness-aware blockers for every lex-improving permutation of

```text
(-1, 0, 0, 0, 0, 1),
(-1,-1, 0, 0, 1, 1),
(-1,-1,-1, 0, 1, 2)                                   (7)
```

on the side chosen by `(5)`.

### Computer-assisted universal exchange lemma

Under these premises, `||x-z||_1<=2/3`.

The negation is one table-free QF_LRA formula for the Lmin branch and one for
the Lmax branch.  There are 240 labeled directions in the union of the three
permutation families.  Both formulas are UNSAT.  The three-for-three exchange
which appeared three times in noncanonical finite menus is redundant.

`starved_universal_exchange_mapping_audit.json` verifies without solver
verdicts that among all 1,352 starved survivor refinements, the 504
starved-only rows are exactly those in which the coarse-rich pair remains tied
at Lmin; the other 848 also refine the positive profile.  It also checks the
symbolic lex-improvement predicate against the finite rank implementation in
241,920 side/direction instances and recovers the `128/376` handover split.

The frozen formulas are approximately 6 MB each.  Z3 and cvc5 both return
UNSAT on identical bytes.  For each formula, cvc5 1.3.3 emits a proof with
trust disabled, no forbidden markers occur, and Ethos returns `correct`:

```text
Lmin CPC: 1,656,704 bytes,   sha256 a84af7a558799a0e...a201047
Lmax CPC: 1,860,649 bytes,   sha256 621ced79090225dc...f6f96d.
```

Thus the 504-table audit is now a discovery cross-check, not the proof-level
dependency of the local starved barrier.

## 5. Status and next theorem

This is a meaningful local simplification, not yet an unconditional proof of
`s(6)=2/3`.

What is now established computer-assistively:

1. the finite selected-side formulas are exact linear arithmetic and all 504
   are UNSAT;
2. the finite audit byte-reproduces from eight bounded shards plus the two
   explicit bound-two exceptions;
3. the map from those 504 rows to the two universal branches is checked
   combinatorially;
4. the two table-free formulas have independent Z3/cvc5 agreement and
   trust-free Ethos-checked CPC proofs; and
5. no formula relies on a staged Farkas encoding.

What remains:

1. extract readable inequalities proving the three families in `(7)` cannot
   all have exactness-eligible blockers when the distance exceeds `2/3`;
2. hostilely review the symbolic lex predicate, anchor hypotheses, handover
   disjunction, and singleton-exactness blocker lemma; and
3. integrate this local barrier with a fully reviewed first-crossing argument.

Combined with the already compressed positive neighborhood, this completes
the local first-crossing barrier at a computer-assisted proof-object level,
conditional on the equality classification and the first-crossing premises.
A fully unconditional theorem would still need a structural or proof-object
replacement for the 3,348 equality-type exclusions and hostile review of the
normal-form and continuity arguments.

## 6. Reproduction

From the repository root, using a Python environment with `z3-solver`:

```bash
python3 coopgames/verifiers/s6/reproduce_starved_exactness_menus.py
python3 coopgames/verifiers/s6/audit_starved_universal_exchange_mapping.py
python3 coopgames/verifiers/s6/audit_starved_universal_shape_ablation.py
python3 coopgames/verifiers/s6/reproduce_starved_universal_exchange.py
```

The driver runs eight 63-row bound-one shards in bounded parallelism, reruns
the two exceptional rows at bound two, validates the complete position and
index sets, merges them, and byte-compares the result with
`starved_exactness_menu_audit.json`.
