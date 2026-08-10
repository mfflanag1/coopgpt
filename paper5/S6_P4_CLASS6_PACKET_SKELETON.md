# Class-6 asymmetric-packet skeleton

## 1. Scope

Packet class 6 has representative

```text
P4={0,1,4},   P5={0,1,2,5}.
```

Its orbit contains four of the 32 feasible labelled packets.  The frozen
order-refined relay has 29 leaves.  This note gives a solver-free packet and
root lemma, not yet a complete class-6 hand proof, external review, or novelty
determination.

## 2. The asymmetric sandwich

Let `di=xi-zi>0` for `i=0,1,2,3` and
`delta_m=zm-xm>0`.  The two opposite packet comparisons are

```text
d0+d1    <= delta4,
d0+d1+d2 <= delta5.
```

Together with efficiency they give

```text
d0+d1 <= delta4 <= d3,
d0+d1+d2 <= delta5 <= d2+d3.                    (6.1)
```

For example
`delta4-d3=(delta4+delta5-sum_i di)+(d0+d1+d2-delta5)`.
Thus the asymmetry forces the strong relation `d0+d1<=d3`.

## 3. The universal root split closes by signs

On `x3<=x4`, the Lmax root is

```text
h11=e0+e3-e4-e5.
```

The chains `z0<x0<=x4<z4` and `z3<x3<=x4<z4` prove its activation.  Of its
twenty negative cuts, a cut containing both rich players has negative
`d(C)` by efficiency.  With one rich player, (6.1) eliminates every cut
except

```text
24, 124.                                         (6.2)
```

In particular the stronger lower bound for `delta5` eliminates all cuts
through player 5.  No witness comparison is needed.

On `x3>x4`, the Lmin root is

```text
h17=-e1-e3+e4+e5.
```

The anchor chain gives `x1>x4,x5`, while `x3>x4>=min(x4,x5)`, proving
activation.  A negative cut without a rich player has positive `d(C)`.  A
negative cut through player 4 contains players 1 and 3, and
`delta4<=d3` makes its `d(C)` strictly positive.  Through player 5, including
player 2 is impossible by `delta5<=d2+d3`.  Hence the exact root list is

```text
135, 0135.                                       (6.3)
```

Equations (6.2)--(6.3) replace both twenty-cut root censuses by two two-cut
lists using only the packet sandwich and strict signs.

## 4. Residual relay

The weak root has two symmetric-looking subtrees.  Each passes through the
automatic `h10=e0-e1` Lmax exchange, one of four `h10` blockers, the automatic
Lmin exchange `h15=e0-e1`, and then closes immediately with either `h17` or
the three-for-three Lmax exchange `h7=e0-e1+e2-e5`.  The strict root has only
seven leaves and depth four.  These 29 leaves remain machine-resolved until
their non-root blocker filters and terminal closures receive exact hand
identities.

## 5. Solver-free audit

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json
```

The checker imports no solver or production encoder.  Exact rational
coefficient arithmetic verifies (6.1) and exhaustively partitions both
twenty-cut root lists.  Finite order enumeration checks both activation
chains and rejects weakened-chain and candidate-deletion mutations.  Its read
of the frozen universal relay is separately labelled as an integration audit,
not proof evidence for the lemma or the human-to-machine implication.
