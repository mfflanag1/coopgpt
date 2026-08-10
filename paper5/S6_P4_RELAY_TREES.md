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
| 7 | 4 | 4 | `4/0` | 3 | yes | no |
| 8 | 2 | 1 | `1/0` | 0 | yes | yes |
| 9 | 4 | 4 | `0/1` | 0 | no | no |
| 10 | 2 | 4 | `0/1` | 0 | no | no |
| 11 | 4 | 3 | `1/0` | 2 | yes | no |

Thus classes `3,4,7,8,11` have complete forced relays.  Their orbit sizes sum
to eighteen of the 32 feasible labelled packets.  Classes 3, 4, and 8,
covering ten packets, have now been converted into explicit hand-checkable
inequalities.  The other eight packets in the closed relay set have
machine-checked trees that specify exactly which blocker lemmas remain to be
humanized.

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
single terminal obligation and is the cleanest candidate for a named
max-to-min exchange-relay lemma.

Class 7 is also complete but has four leaves and depth three.  It should be
attempted after class 11.

## 4. Human activation reduction for class 11

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

The finite audit still supplies the blocker classification

```text
first Lmax blocker:   {0,1,2,5} only;
second Lmax blocker:  {0,1,3} only;
final Lmin blockers:  none.
```

One awkward first-stage exclusion also has a short displayed certificate.  If
`C={0,1}` were an Lmax blocker, then

```text
3D-1 = -4z_0-z_2-z_3-q_4 +3(x_0-x_5)+2(z_5-z_1)
       +2(x(P5)-z(P5)) +(x(P5)-q(P5)) +(z(C)-q(C))
       +(q(N)-1)+q_1 <= 0.                              (11.4)
```

The audit checks (11.3) and (11.4) as literal polynomial identities, in
addition to independently restating the packet and relay.  Class 11 is not
yet labelled an all-human packet proof: the other cut exclusions still need
structural inequalities or an explicit family of checkable certificates.

## 5. What remains unresolved

The relay method stalls immediately in classes 9 and 10 because none of the
directions in the chosen subset-minimal core is forced before an additional
order split.  Classes 1, 2, 5, and 6 have many closed branches but retain,
respectively, 6, 3, 3, and 4 open leaves.  These are precise structural
residues, not counterexamples.

The relay audit does not replace the trust-disabled CPC proof of the weaker
parent formula and does not validate the human-to-machine map.  Its purpose is
to turn the residual finite proof into a short list of concrete exchange and
blocker lemmas suitable for external review.

## 6. Reproduction

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
```

The frozen JSON records every chosen direction, its side and role orbit, the
number of eligible negative cuts, every surviving blocker coalition, every
closed or open leaf, and the exact packet/core provenance.
