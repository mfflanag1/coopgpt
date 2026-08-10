# Forced-exchange relay trees in the six-player `(4,2,0)` case

Date: 2026-08-10

## 1. What the relay audit asks

Fix one of the eleven exact blocker packets in
`S6_P4_PACKET_CLASSIFICATION.md` and its frozen subset-minimal residual core.
At a current branch:

1. test which unused core directions are forced lex-improving;
2. among them choose one with the fewest feasible blocker alternatives;
3. discard every blocker alternative inconsistent with the current branch;
4. branch on the remaining concrete blockers; and
5. close a leaf when a forced improving direction has no blocker.

If no unused direction is forced, the leaf is explicitly left open.  A closed
tree is therefore a finite explanation of the parent UNSAT formula: every
branch is a sequence of necessary optimality blockers, ending when optimality
cannot supply the next blocker.  It is not an independent proof object, and a
SAT or open branch is not an exact game.

## 2. Five complete relay classes

The deterministic audit gives the following anatomy.  `Closed/open` counts
terminal leaves; depth zero means the first forced direction has no blocker.

| class | packet orbit size | core directions | closed/open | maximum depth | complete relay | separate hand proof |
|---:|---:|---:|---:|---:|---|---|
| 1 | 1 | 4 | `2/6` | 1 | no | no |
| 2 | 2 | 6 | `6/3` | 4 | no | no |
| 3 | 4 | 2 | `2/0` | 1 | yes | yes |
| 4 | 4 | 3 | `3/0` | 1 | yes | yes |
| 5 | 1 | 7 | `30/3` | 4 | no | no |
| 6 | 4 | 7 | `29/4` | 4 | no | no |
| 7 | 4 | 4 | `4/0` | 3 | yes | yes |
| 8 | 2 | 1 | `1/0` | 0 | yes | yes |
| 9 | 4 | 4 | `0/1` | 0 | no | no |
| 10 | 2 | 4 | `0/1` | 0 | no | no |
| 11 | 4 | 3 | `1/0` | 2 | yes | yes |

Thus classes `3,4,7,8,11` have complete relays without adding a payoff-order
split.  Their orbit sizes sum to eighteen of the 32 feasible labelled packets,
and all five are converted into explicit hand-checkable inequalities.  Of the
six classes left open by this no-new-order rule, class 9 is now also
hand-checkable after one exhaustive order split; Section 6 records that
refinement.  Class 10 is likewise hand-checkable after its nested order split.
Classes 1 and 2 are now hand-checkable after the universal root split.  The
combined hand coverage is therefore twenty-seven packets.

## 3. Two especially small targets

### Class 4: a three-leaf star

The first forced direction is

```text
-e_1-e_3+e_4+e_5       (Lmin).
```

Only three of its twenty negative cuts survive:

```text
{1,2,3,4},   {1,3,5},   {0,1,3,5}.
```

The first blocker forces `e_2-e_1` to improve Lmax, with no feasible blocker.
Either of the other two forces `-e_2-e_3+e_4+e_5` to improve Lmin, again with
no feasible blocker.  The whole four-packet orbit is therefore a depth-one,
three-leaf relay.

The root of this star is now humanized.  For class 4, `A` is empty and
`B={2}`.  Its packet `q` comparisons are

```text
q_4 >= x_1+x_4,                  q_2+q_5 >= x_1+x_2+x_5.       (4.1)
```

The complement of the second inequality and the first inequality give
`x_0+x_3>=x_1+q_0+q_3>=x_1`.  If `x_3<=x_m` for either `m=4,5`, bottomness of
`x_0` gives `x_4+x_5>=x_1`; hence

```text
D <= z_4+z_5-x_1 < z_4+z_5-z_1 <= 1/3.             (4.2)
```

Thus `x_1,x_3>x_4,x_5`, and the root direction necessarily improves Lmin.

Its negative cuts either contain no `M` player, in which case their `d`-sum
is positive, or have the form `{1,3,m} union K` with `m` in `{4,5}` and
`K subset {0,2}`.  The packet opposite comparisons and their complements are

```text
d_1 <= delta_4 <= d_0+d_3,
d_1+d_2 <= delta_5 <= d_0+d_2+d_3.                  (4.3)
```

Using (4.3), an opposite blocker can only be

```text
{1,3,4}, {1,2,3,4}, {1,3,5}, {0,1,3,5}, {1,2,3,5}.
```

The first and last candidates are impossible by (4.1): their complementary
`q` comparisons respectively give `q_0+q_2+q_5<=x_0+x_2+x_5` and
`q_0+q_4<=x_0+x_4`, each forcing `x_1<=x_0`, whereas
`x_0<=x_4<z_4<=z_1<x_1`.  This leaves exactly the three branches displayed
above, with no finite search in the root classification.

All three child activations are also short.  The blocker `{1,2,3,4}` implies
`delta_5<=d_0`; therefore `D<=z_4-z_0`, and `z_1=z_2` would imply
`D<=1/3` exactly as in (11.2).  Hence `z_1>z_2`.  For blocker `{1,3,5}` its
`q` comparison and the complement of the first inequality in (4.1) give
`x_0+x_2>=x_1`; for `{0,1,3,5}` they give `x_2>=x_1`.  If `x_2` were no
larger than either `M` payoff, (4.2) would again follow.  Thus the required
child direction improves in both branches.

The three terminal exclusions also admit an exhaustive human-sized
description.  After the blocker `{1,2,3,4}`, the terminal Lmax direction is
`-e_1+e_2`.  Every negative cut contains `1` and excludes `2`, so its
complement is

```text
L={2} union K,                 K subset {0,3,4,5}.            (4.4)
```

Because `q(N)=z(N)=1`, the required blocker comparison `q(C)>=z(C)` is
equivalent to `q(L)<=z(L)`.  There are exactly sixteen sets in (4.4).  For
each one, the frozen certificate table gives nonnegative multipliers on the
packet, root-blocker, order, sign, and hypothetical `q(L)<=z(L)` inequalities
whose sum is the recorded positive integer multiple of `D-1/3`.  Thus no such
comparison can hold when
`D>1/3`.

After either blocker `{1,3,5}` or `{0,1,3,5}`, the terminal Lmin direction is
`-e_2-e_3+e_4+e_5`.  A negative cut containing an `M` player has the form

```text
{2,3,m} union K,              m in {4,5},  K subset {0,1}.   (4.5)
```

A cut with no `M` player has positive `d=x-z` sum and cannot satisfy the
opposite-selection blocker comparison.  The optional players in (4.5) also
have positive `d`, so any opposite comparison for (4.5) implies the same
comparison for the base cut `{2,3,m}`.  Four further weighted identities—one
for each root blocker and choice of `m`—show that this base comparison also
forces `D<=1/3`.

The checker
`verify_strict_exchange_p4_class4_hand_certificates.py` contains all sixteen
complement rows and all four base-cut rows.  It orients every named inequality
as `<=0`, checks that every inequality multiplier is nonnegative, and verifies
the exact affine identity using only rational coefficient arithmetic.  It
makes no satisfiability query, imports no production encoder, and rejects a
one-coefficient mutation control.  Equations
(4.1)--(4.5) plus these twenty inspectable rows therefore give a complete
hand-checkable proof of class 4, covering four labelled packets.

### Class 11: a unique three-exchange chain

There is no branching:

```text
Lmax: -e_1+e_2+e_3-e_5
  unique blocker {0,1,2,5}
Lmax: -e_1+e_2
  unique blocker {0,1,3}
Lmin: -e_1+e_2
  no feasible blocker.
```

This chain covers four labelled packets.  It is longer than class 4 but has a
particularly clean separation between its opposite-selection and
singleton-witness blocker tests.

Class 7 also has a complete hand proof, given in Section 5 below.

## 4. Human completion of class 11

The three exchanges in the class-11 chain are no longer black-box
activations.  Here `A={2}`, `B={2,3}`, write

```text
d_i=x_i-z_i  (i in P),     delta_m=z_m-x_m  (m in M),
D=d_0+d_1+d_2+d_3=delta_4+delta_5>1/3.
```

The two packet opposite comparisons and their complements give

```text
d_1+d_2 <= delta_4 <= d_0,
d_1+d_2+d_3 <= delta_5 <= d_0+d_3.              (11.1)
```

Since `x_0<=x_5`, (11.1) implies

```text
D <= d_0+delta_5 <= z_5-z_0.                    (11.2)
```

If `z_1=z_j` for `j=2` or `3`, topness of `z_1` and nonnegativity give

```text
3D <= 3(z_5-z_0) <= z_1+z_j+z_5-3z_0 <= 1,
```

a contradiction.  Hence `z_1>z_2,z_3`, which activates both Lmax directions
in the chain.

The last Lmin direction requires `x_1>x_2`.  If instead `x_1<=x_2`, direct
addition of valid nonpositive terms gives the checkable identity

```text
3D-1 = -x_4-4z_0-z_3 +2(z_1-x_1)+3(x_0-x_5)+2(z_5-z_1)
       +(x(P4)-z(P4))+3(x(P5)-z(P5))+(x_1-x_2)+(z(N)-1),   (11.3)
```

where `P4={1,2,4}` and `P5={1,2,3,5}` are the packet coalitions.  Every term
on the right of (11.3) is nonpositive; the last is zero.  Thus `D<=1/3`, a
contradiction.  This proves all three relay activations by displayed
inequalities.

It remains to prove the blocker classification

```text
first Lmax blocker:   {0,1,2,5} only;
second Lmax blocker:  {0,1,3} only;
final Lmin blockers:  none.
```

One first-stage exclusion has the short displayed certificate below.  If
`C={0,1}` were an Lmax blocker, then

```text
3D-1 = -4z_0-z_2-z_3-q_4 +3(x_0-x_5)+2(z_5-z_1)
       +2(x(P5)-z(P5)) +(x(P5)-q(P5)) +(z(C)-q(C))
       +(q(N)-1)+q_1 <= 0.                              (11.4)
```

The rest of the classification has a compact source-specific organization.
For the first direction, direct membership casework using positivity,
efficiency, and (11.1) reduces its twenty negative cuts to the seven sets

```text
{1}, {0,1}, {0,5}, {0,1,4}, {0,1,5},
{0,1,2,5}, {0,1,3,5}.                              (11.5)
```

The enumeration is exhaustive for the following reason:

| negative-coefficient players in `C` | positive-coefficient players in `C` | optional zero players | cuts not immediately having negative `d(C)` |
|---|---|---|---|
| `{1}` | none | subset of `{0,4}` | `{1}`, `{0,1}`, `{0,1,4}` |
| `{5}` | none | subset of `{0,4}` | `{0,5}` |
| `{1,5}` | none | subset of `{0,4}` | `{0,1,5}` |
| `{1,5}` | exactly one `r` in `{2,3}` | subset of `{0,4}` | `{0,1,r,5}` |

Indeed, `{1,4}` has `d`-sum at most `-d_2`, `{1,2,5}` has `d`-sum at most
`-d_3`, adding player `4` only decreases these sums, and adding both zero
players makes the cut the complement of an omitted positive-`d` player.  The
remaining cases are immediate from `delta_5>=d_1+d_2+d_3` or positivity.
Two opposite-comparison identities
eliminate `{0,5}` and `{0,1,5}` from (11.5).  Four `q^1`-comparison identities
then eliminate `{1}`, `{0,1}`, `{0,1,4}`, and `{0,1,3,5}`.  The only possible
first blocker is therefore `{0,1,2,5}`.

For the second direction, every negative cut has the form

```text
C={1} union K,                 K subset {0,3,4,5}.            (11.6)
```

The first branch's two comparisons are now premises.  The `q^1` comparison
alone eliminates fifteen of the sixteen sets in (11.6), leaving exactly
`{0,1,3}`.  After its two comparisons are added, the terminal Lmin direction
has the same sixteen cuts, and its `q^1` comparison alone is impossible for
all sixteen.

The frozen certificate table records the resulting 37 identities: two
first-stage opposite exceptions, four first-stage `q^1` filters, fifteen
second-stage `q^1` filters, and sixteen terminal `q^1` filters.  Every named
inequality is oriented as `<=0`; every inequality multiplier is nonnegative;
and every weighted sum is the recorded positive integer multiple of
`D-1/3`.  The checker uses pure rational coefficient arithmetic, imports no
production encoder, makes no satisfiability query, exhausts each cut family,
and rejects a one-coefficient mutation control.  Together with
(11.1)--(11.6), these rows complete a hand-checkable proof of class 11.

## 5. Human completion of class 7

For class 7, `A={0}` and `B={2}`.  Put

```text
d_i=x_i-z_i  (i=0,1,2,3),       delta_m=z_m-x_m  (m=4,5).
```

The packet coalitions are `P4={0,1,4}` and `P5={1,2,5}`.  Their opposite
comparisons and complements are exactly

```text
d_0+d_1 <= delta_4 <= d_0+d_3,
d_1+d_2 <= delta_5 <= d_2+d_3.                    (7.1)
```

In particular `d_3>=d_1`.  Their `q=q^1` comparisons and complements give

```text
q_0+q_4 >= x_0+x_1+x_4,     q_2+q_5 >= x_1+x_2+x_5,
q_2+q_3+q_5 <= x_2+x_3+x_5,
q_0+q_3+q_4 <= x_0+x_3+x_4.                       (7.2)
```

Either lower inequality combined with the opposite upper inequality yields
`x_3>=x_1+q_3>=x_1`.  Since `x_1>x_4,x_5`, this activates the root Lmin
direction `-e_1-e_3+e_4+e_5` without a finite search.

Name the only blockers that survive below by

```text
B0={1,2,3,4},  B1={1,3,5},    B2={0,1,3,5},
B3={1,2},      B4={1,2,5},    B5={2,3,5}.          (7.3)
```

The opposite-source cut census is small.  Efficiency eliminates `delta_5`,
and (7.1) becomes the five-variable interval system

```text
delta_4 >= d_0+d_1,       delta_4 <= d_0+d_3,
delta_5  >= d_1+d_2,      delta_5  <= d_2+d_3,
delta_4+delta_5=d_0+d_1+d_2+d_3.                  (7.4)
```

Substituting the appropriate branch comparison into `d(C)<=0` for an Lmin
blocker or `d(C)>=0` for an Lmax blocker gives the complete table:

| stage | direction and side | opposite-source candidates |
|---|---|---|
| root | `-e1-e3+e4+e5`, Lmin | `{1,3,4}`, `B0`, `B1`, `B2` |
| after `B0` | `e0+e2-e4-e5`, Lmax | `{3,5}`, `{1,3,5}` |
| after `B1` | `-e2-e3+e4+e5`, Lmin | `{2,3,4}`, `B5`, `{1,2,3,4}` |
| after `B2` | `e0-e1`, Lmax | `{1}`, `B3`, `{1,3}`, `{1,2,3}`, `{1,2,4}`, `B4`, `{1,3,4}`, `{1,2,3,4}`, `{1,2,3,5}` |
| after `B2,B3` | `-e2-e3+e4+e5`, Lmin | `B5` |
| after `B2,B4` | `-e2-e3+e4+e5`, Lmin | `B5` |
| after `B2,B3,B5` | `e0+e2-e4-e5`, Lmax | `{3,4}`, `{1,3,4}` |
| after `B2,B4,B5` | `e0+e2-e4-e5`, Lmax | `{1,3,4}` |

This is direct membership arithmetic, not an SMT census.  For example `B4`
forces `delta_5<=d_1+d_2`, hence equality in the second lower bound of (7.4),
while `B5` forces `delta_5>=d_2+d_3`, hence equality in its upper bound.  The
solver-free checker independently recomputes all eight table rows from (7.4)
by exact rational Fourier--Motzkin elimination.  It scales every strictly
positive difference magnitude to at least one, which is equivalent by
homogeneity and avoids any numerical treatment of strict inequalities.

Only sixteen candidates in the table need an additional source-specific
filter.  One `q` identity removes `{1,3,4}` at the root, leaving exactly
`B0,B1,B2`.  The two candidates after `B0` are removed by `q`; after `B1`,
two are removed by `q` and `B5` by the opposite comparison.  Seven `q`
identities remove all candidates after `B2` except `B3,B4`.  Finally two and
one `q` identities close the terminal lists after `B3` and `B4`, respectively.
Thirteen identities have target `D-1/3`; the other three have target `d_0`,
which is strictly positive.  Since every named premise is oriented as
nonpositive, either target is a contradiction.

The remaining activations are also explicit.  After `B0`, failure of the
Lmax direction means either `z_0>=z_4,z_5` or `z_2>=z_4,z_5`; two weighted
identities give `D<=1/3`.  After `B1`, its `q` comparison and the complement
of the first inequality in (7.2) give `x_2>=x_1+q_2>=x_1`, activating the
Lmin direction.  After `B2`, a weighted identity shows that `z_1<=z_0`
forces `D<=1/3`, so `e_0-e_1` improves Lmax.  On either `B3` or `B4`, another
identity shows that `x_2<=x_5` forces `D<=1/3`; together with
`x_3>=x_1>x_5`, this activates the next Lmin direction.  After `B5`, two
identities again exclude the two possible failure cases
`z_0>=z_4,z_5` and `z_2>=z_4,z_5`, activating the terminal Lmax direction.
There are nine activation identities in total.

Thus the relay is

```text
root -> B0 -> contradiction,
     -> B1 -> contradiction,
     -> B2 -> B3 or B4 -> B5 -> contradiction.    (7.5)
```

`verify_strict_exchange_p4_class7_hand_certificates.py` checks the eight exact
cut censuses, all sixteen blocker filters, and all nine activation identities.
It uses pure `Fraction` arithmetic, imports no production encoder, makes no
satisfiability call, and rejects both a coefficient perturbation and deletion
of a structural candidate.  Equations (7.1)--(7.5), the table, and the 25
weighted rows therefore give a complete hand-checkable proof of class 7,
covering four labelled packets.

## 6. Two complete order-split relays

The unsplit relay rule is deliberately conservative: it opens a leaf whenever
no direction is forced before any new payoff-order choice.  Classes 9 and 10
stall for exactly this reason, but both close after very small exhaustive order
trees.

For class 9, the single split

```text
x_3 <= x_4        or        x_3 > x_4
```

closes both branches.  The weak branch has two closed leaves and depth two;
the strict branch has three closed leaves and depth three.  Thus the entire
four-packet orbit is reduced to five terminal contradictions.

For class 10, the strict branch `x_3>x_4` closes with four leaves.  On the weak
branch `x_3<=x_4`, the one additional split

```text
x_1 <= x_2        or        x_1 > x_2
```

closes with one and four leaves, respectively.  The two-packet orbit is
therefore reduced to a nine-leaf tree of depth at most three.

`audit_strict_exchange_p4_order_split_relays.py` freezes every direction,
blocker coalition, branch, and SAT order premise in these two trees.  The
audit shares the parent encoding, so it is an explanatory decomposition and
not independent theorem evidence.

Class 9 is now hand-checkable.  `S6_P4_CLASS9_HAND_CHECKPOINT.md` gives its
difference-cone table and terminal anchor-threshold lemma.  The solver-free
`verify_strict_exchange_p4_class9_hand_certificates.py` recomputes all ten
cut censuses and checks 43 blocker identities, seven activation identities,
and two terminal-anchor identities at all 71 required uses.  It imports no
production encoder or solver and rejects five mutation controls.  Class 10 is
also hand-checkable.  Its solver-free verifier recomputes eighteen cut
censuses and checks 95 blocker plus thirteen activation identities at all 122
uses.  Of 105 blocker exclusions, 103 use only `q^1`; the two weak-left
exceptions use only the opposite comparison.
Class 1 is now hand-checkable as well.  Its solver-free verifier recomputes
twenty-one cut censuses and checks 65 blocker plus 44 activation identities at
160 uses.  The identity `min(x_a,x_b)>min(x_4,x_5)` compresses every two-donor
activation to four failure conjunctions, giving 75 activation cases in total.
Class 2 reuses the minimum-level lemma and its maximum-level dual.  Its
solver-free verifier checks 21 cut censuses, 52 blocker plus 56 activation
identities, and all 132 uses.  The eleven-leaf tree covers two labelled packets.

## 7. Universal order completion and remaining hand gap

The unsplit relay method stalls immediately in classes 9 and 10, while the
order-split refinement and exact certificate audits now close both trees by
hand.  The same root split `x_3<=x_4` versus `x_3>x_4` also closes every open
leaf in classes 1, 2, 5, and 6.  Imposing it uniformly gives complete relay
trees for all eleven packet classes; class 10 alone needs the nested
`x_1<=x_2` versus `x_1>x_2` split.  `S6_P4_UNIVERSAL_ORDER_RELAY.md` records
the resulting all-class anatomy.

Classes 5 and 6 remain unresolved only at the hand-certificate layer.
Their order-refined trees share the parent encoding and have not yet been
compressed into complete independent exact identities.  Class 5 now has a
solver-free packet skeleton: one sandwich and anchor-chain lemma covers all
ten `h15` activations and gives their common ten-candidate blocker census.
Three orbit identities also remove seven of the thirty formal blocker pairs
with the preceding `h10` step.  The root `h11` and `h17` blocker lists are now
proved by the packet sandwich and one witness identity.  It does not yet close
the 51 leaves.  Classes 1 and 2 have crossed
that boundary, although their proof objects remain compression targets rather
than a short conceptual lemma.  The remaining rows are precise structural
targets, not counterexamples or unexplained open leaves.
Class 6 also has a solver-free asymmetric-packet root skeleton: its two
twenty-cut root censuses collapse to two blockers each without a witness
identity.  Its 29 leaves remain at the hand-certificate boundary.

The relay audit does not replace the trust-disabled CPC proof of the weaker
parent formula and does not validate the human-to-machine map.  Its purpose is
to turn the residual finite proof into a short list of concrete exchange and
blocker lemmas suitable for external review.

## 8. Reproduction

Run from the repository root with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_relay_trees.py \
  --output /tmp/strict_exchange_p4_relay_trees.json
cmp /tmp/strict_exchange_p4_relay_trees.json \
  coopgames/verifiers/s6/strict_exchange_p4_relay_trees.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class4_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class4_hand_certificates.json
cmp /tmp/strict_exchange_p4_class4_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class4_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class11_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class11_hand_certificates.json
cmp /tmp/strict_exchange_p4_class11_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class11_hand_certificates.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class7_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class7_hand_certificates.json
cmp /tmp/strict_exchange_p4_class7_hand_certificates.json \
  coopgames/verifiers/s6/strict_exchange_p4_class7_hand_certificates.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_order_split_relays.py \
  --output /tmp/strict_exchange_p4_order_split_relays.json
cmp /tmp/strict_exchange_p4_order_split_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_order_split_relays.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class9_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class9_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class9_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class9_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class10_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class10_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class10_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class10_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class1_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class1_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class1_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class1_hand_certificate_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class2_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp /tmp/strict_exchange_p4_universal_order_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
```

The frozen JSON records every chosen direction, its side and role orbit, the
number of eligible negative cuts, every surviving blocker coalition, every
closed or open leaf, and the exact packet/core provenance.
