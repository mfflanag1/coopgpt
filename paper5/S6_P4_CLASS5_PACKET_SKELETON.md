# Class-5 rich-packet skeleton

## 1. Scope

Packet class 5 is the symmetric labelled packet

```text
P4={0,1,4},   P5={0,1,5}.
```

Its universal order relay closes, but the raw tree has 90 nodes and 51
leaves.  This note extracts reusable hand lemmas from that tree.  It is a
partial humanization, not yet a complete class-5 hand proof, external review,
or novelty evidence.

## 2. The rich-packet sandwich

Write

```text
di=xi-zi>0                 (i=0,1,2,3),
delta_m=zm-xm>0            (m=4,5),
s=d0+d1,                   t=d2+d3.
```

The two opposite packet comparisons and efficiency give

```text
s <= delta4,delta5,
delta4+delta5=s+t,
delta4,delta5 <= t.                              (5.1)
```

The upper bounds are not additional assumptions: for example
`delta4-t=(delta4+delta5-s-t)+(s-delta5)`.  In particular `s<=t`.

## 3. Two exchanges are automatic

The anchor roles and strict sign pattern contain the chains

```text
z0 < x0 <= x4 < z4 <= z1,
x0 <= x4 < z4 <= z1 < x1.
```

Consequently

```text
h10=e0-e1 strictly improves Lmax, because z0<z1;
h15=e0-e1 strictly improves Lmin, because x0<x1.
```

This observation is packet-independent.  In class 5 it replaces the
activation argument at all ten occurrences of `h15` in the frozen relay.

## 4. One exact blocker classification for all ten `h15` nodes

An `h15`-negative cut contains player 1 and excludes player 0, so there are
sixteen eligible cuts.  Put `d(C)=x(C)-z(C)`.  An Lmin opposite blocker must
satisfy `d(C)<=0`.

If `C` contains no rich player, `d(C)` is a strictly positive sum containing
`d1`.  If it contains exactly one rich player `m` and both players 2 and 3,
then (5.1) gives

```text
d(C)=d1+d2+d3-delta_m >= d1 > 0.
```

These arguments exclude exactly six cuts.  The only remaining
opposite-comparison candidates are

```text
14, 124, 134,   15, 125, 135,
145, 1245, 1345, 12345.                         (5.2)
```

The four cuts containing both rich players actually have

```text
d(C)=-d0-d({2,3}\C)<0,
```

by efficiency.  Thus (5.2) is the natural packet-level list; subsequent
relay blockers only filter it further using the single-witness comparisons.
Every child of every `h15` node in the frozen class-5 relay belongs to (5.2).

The compression is therefore exact at this layer:

```text
ten separate activation checks     -> one anchor-chain lemma,
ten copies of sixteen eligible cuts -> one ten-candidate packet census.
```

It does not close the 51 leaves.  The remaining task is to compress how the
preceding blocker comparisons filter (5.2) and force the terminal two-for-two
exchanges.

## 5. The root order split is structural

On the weak branch `x3<=x4`, the root direction is

```text
h11=e0+e3-e4-e5        (Lmax).
```

Both positive recipients lie strictly below player 4 in `z`:

```text
z0<x0<=x4<z4,     z3<x3<=x4<z4.
```

Hence `max(z0,z3)<z4<=max(z4,z5)`, so `h11` improves Lmax.  Of its twenty
negative cuts, (5.1) leaves only the four opposite-comparison candidates

```text
24, 124, 25, 125.
```

Cuts with both rich players omit at least one positive-`d` player and have
negative `d(C)` by efficiency.  With one rich player `m`, the cases with no
poor player or only player 1 have `d(C)<0` from `delta_m>=d0+d1`; only the
cases containing player 2 survive.  Finally, the `q1` comparison for `125`,
the packet-witness comparison for `P4`, the weak order, and the anchor/sign
premises have a seven-term exact weighted sum equal to `d0<=0`.  Thus the
weak root has exactly the three blockers

```text
24, 124, 25.                                      (5.3)
```

On the strict branch `x3>x4`, the root direction is

```text
h17=-e1-e3+e4+e5       (Lmin).
```

Here `x1>x4,x5` by the anchor chain and
`x3>x4>=min(x4,x5)`, so `h17` improves Lmin.  Its twenty negative cuts reduce
without a witness identity to

```text
134, 0134, 135, 0135.                              (5.4)
```

Indeed a cut with no rich player has positive `d(C)`.  A negative cut with
one rich player contains both 1 and 3; if it also contains player 2, then
`delta_m<=d2+d3` again makes `d(C)>0`.  No cut containing both rich players is
negative for `h17`.  Equations (5.3)--(5.4) give a complete hand
classification of the two roots of the 51-leaf tree.

## 6. A three-orbit `h10`/`h15` crossing lemma

Every `h15` node in the frozen relay has an earlier `h10` blocker

```text
B in {12,13,123}.
```

Pair this with an `h15` blocker `C` from (5.2).  Seven of the thirty formal
pairs are impossible, in only three orbits under the swaps `2<->3` and
`4<->5`:

```text
B={1,k},   C={1,l,m},      {k,l}={2,3}, m in {4,5};   (four pairs)
B=123,     C={1,m},                        m in {4,5};   (two pairs)
B=123,     C=12345.                                      (one pair)
```

There is one short exact weighted identity for each orbit.  In the first,
add nonnegativity of `x4,x5`, twice positivity of `d1`, positivity of `d_l`,
the two top-anchor inequalities `z4,z5<=z1`, the packet witness comparison
for the rich player other than `m`, and the `q1` comparisons for `B` and `C`;
then use `-sum(z)+sum(q)+2q1=0`.  The sum is exactly `d0<=0`.  The second
identity omits `d_l`.  The third uses both packet witness comparisons and
`-sum(x)-sum(z)+2sum(q)+2q1=0`.  Its sum is again `d0<=0`.  All contradict
the strict sign `d0>0`.

Thus the common predecessor/successor census falls from thirty formal pairs
to 23, and every actual class-5 relay edge respects the resulting crossing
rule.  Together with the root lemma, this isolates the remaining work to the
non-root blocker filters and terminal two-for-two closures.

## 7. Solver-free audit

Run

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_packet_skeleton_audit.json
```

The checker imports no solver or production encoder.  Exact rational
coefficient arithmetic verifies (5.1), every cut identity, the exhaustive
sixteen-cut partition, both twenty-cut root classifications, the weak-root
witness identity, and all seven crossing exclusions through three orbit
identities.  Finite total-preorder enumeration checks the anchor and root
activation chains and rejects weakened-sign mutations.  Reading the frozen relay
is confined to a separately labelled integration audit; it is not proof
evidence for the lemma or for the human-to-machine implication.
