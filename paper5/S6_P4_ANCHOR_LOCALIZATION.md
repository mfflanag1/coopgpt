# Anchor localization in the six-player `(4,2,0)` case

Date: 2026-08-10

## 1. Human reduction

Write `x=Lmin(v)`, `z=Lmax(v)`, and

```text
P={i:x_i>z_i},   M={i:z_i>x_i}.
```

In the `(4,2,0)` sign case, the two cross-selection anchors supply

- an `x`-bottom player `a` in `P`; and
- a `z`-top player `b` in `P`.

These players must be distinct.  If `a=b`, then for any `m in M`,

```text
x_m >= x_a > z_a >= z_m > x_m,
```

an immediate contradiction.  This closes the coincident-anchor branch by
hand, without an exchange direction, distance inequality, or exactness
witness.

In the remaining branch, relabel within `P` so that `a=0` and `b=1`.  Relabel
the other two `P`-players as `2,3` and the two `M`-players as `4,5`.  The
remaining symmetry is the independent swap of `2,3` and of `4,5`.

This is a genuine exhaustive reduction.  The cross anchors guarantee the
existence of `a,b`; their coincidence is impossible by the displayed chain;
and every distinct pair is carried to `(0,1)` by a sign-preserving player
permutation.

## 2. One localized exactness witness

Let `q^1` be the singleton exactness witness at the `z`-top anchor `b=1`:

```text
q^1 in core(v),   q^1_1=0,   q^1>=0,   q^1(N)=1.
```

For each retained improving exchange `h`, optimality supplies a proper tight
coalition `S` with `h(S)<0`.  The anchor-localized formula keeps only

```text
opposite selection:  z(S)>=x(S) on the Lmin side,
                     x(S)>=z(S) on the Lmax side;

localized witness:   q^1(S)>=x(S) on the Lmin side,
                     q^1(S)>=z(S) on the Lmax side.
```

These are necessary consequences of a real counterexample.  Deleting the
other five singleton-witness comparisons weakens the formula, so UNSAT of the
weaker formula remains sufficient.  The resulting formula declares only 18
reals: the twelve coordinates of `x,z` and the six coordinates of `q^1`.

## 3. Ten residual exchange orbits

After fixing the anchor roles, the final formula retains nineteen labelled
directions in ten complete orbits under the residual swaps.  A displayed
direction is the lexicographically least representative on labels
`(a,b,2,3,4,5)`.

| orbit | side | canonical direction | labelled directions | parent schema |
|---:|---|---|---:|---|
| R1 | Lmax | `(0,-1,0,1,0,0)` | 2 | C3 |
| R2 | Lmax | `(0,-1,1,1,-1,0)` | 2 | C2 |
| R3 | Lmax | `(1,-1,0,0,0,0)` | 1 | C3 |
| R4 | Lmax | `(1,-1,0,1,-1,0)` | 4 | C2 |
| R5 | Lmax | `(1,0,0,1,-1,-1)` | 2 | C4 |
| R6 | Lmin | `(0,-1,-1,0,1,1)` | 2 | C6 |
| R7 | Lmin | `(0,-1,0,0,0,1)` | 2 | C1 |
| R8 | Lmin | `(0,-1,0,1,0,0)` | 2 | C5 |
| R9 | Lmin | `(0,0,-1,-1,1,1)` | 1 | C6 |
| R10 | Lmin | `(1,-1,0,0,0,0)` | 1 | C5 |

The base system without these implications is SAT.  The complete unguarded
formula is UNSAT in Z3 and cvc5; cvc5 emits a trust-disabled CPC proof with no
forbidden markers, and Ethos checks it as `correct`.  Each of the nineteen
single-direction deletions and each of the ten whole-orbit deletions is SAT.
Deleting either remaining blocker-comparison source, the opposite selection
or `q^1`, is also SAT.

Those SAT ablations establish irredundancy only inside this relaxation.  They
are not games and are not independent proof evidence.

## 4. Exact soundness boundary

A genuine strict `(4,2,0)` counterexample maps into this formula as follows:

1. take its actual `x,z` and sign-relabel `P,M`;
2. choose the bottom anchor `a` and top anchor `b` supplied by the two convex-
   segment arguments;
3. use the hand contradiction to exclude `a=b`, then relabel `a=0,b=1`;
4. assign the actual singleton exactness witness `q^b` to `q^1`;
5. for every retained direction whose lex antecedent is true, use the
   negative-tight-coalition lemma and retain only the opposite and `q^1`
   comparisons.

No game values, common tightness variables, or omitted witnesses are needed
in the machine assignment.  This is intentionally a one-way relaxation.

The remaining non-human step is the incompatibility of the ten residual
orbit families.  The reduction is therefore a substantial humanization of
the former 90-direction/six-witness presentation, not a complete hand proof.

`S6_P4_PACKET_CLASSIFICATION.md` exposes a second layer of that
incompatibility.  Two C1 directions are forced active, and their blockers
form a pair

```text
{1,4} union A,   {1,5} union B,   A,B subsets of {0,2,3}.
```

Of the 64 labelled pairs, 32 are base-infeasible and the other 32 form only
eleven classes under the residual symmetry.  Every class closes with a
subset-minimal menu of at most seven of the remaining seventeen directions.
This is a reviewer-readable finite packet table, but its residual blocker
alternatives are still machine-resolved except in classes 3, 4, and 8.  Class
3 closes four labelled packets by a two-exchange blocker relay; class 4 closes
four by a three-leaf star and twenty exact weighted identities; class 8 closes
two labelled packets with the single direction `-e_1-e_3+e_4+e_5`.  The
class-8 activation and exclusion of all twenty eligible blockers use only the
opposite comparison, not `q^1`.

A forced-exchange relay audit closes classes `3,4,7,8,11` without an order
split, covering eighteen of the 32 feasible labelled packets.  The two closed
but not yet fully hand-written trees are recorded coalition by coalition in
`S6_P4_RELAY_TREES.md`; class 7 has depth three and class 11 is a unique
three-exchange chain.

## 5. Reproduction

Run from the repository root with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_anchor_core.py \
  --output /tmp/strict_exchange_p4_anchor_core.json \
  --formula /tmp/strict_exchange_p4_anchor_core.smt2
cmp /tmp/strict_exchange_p4_anchor_core.json \
  coopgames/verifiers/s6/strict_exchange_p4_anchor_core.json
cmp /tmp/strict_exchange_p4_anchor_core.smt2 \
  coopgames/verifiers/s6/p4_anchor_core_certificates/strict_exchange_p4_anchor_core.smt2
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp /tmp/strict_exchange_p4_packet_classes.json \
  coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp /tmp/strict_exchange_p4_relay_trees.json \
  coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
```

The frozen artifacts are

```text
coopgames/verifiers/s6/audit_strict_exchange_p4_anchor_core.py
coopgames/verifiers/s6/strict_exchange_p4_anchor_core.json
coopgames/verifiers/s6/p4_anchor_core_certificates/strict_exchange_p4_anchor_core.smt2
coopgames/verifiers/s6/p4_anchor_core_certificates/strict_exchange_p4_anchor_core.cpc
coopgames/verifiers/s6/p4_anchor_core_certificates/strict_exchange_p4_anchor_core.json
coopgames/verifiers/s6/verify_strict_exchange_p4_anchor_core_certificate.py
coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py
coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py
coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
```
