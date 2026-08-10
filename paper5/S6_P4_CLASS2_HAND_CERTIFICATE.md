# Class-2 extremal-level hand certificate

## 1. Scope and status

Packet class 2 has two labelled packets and canonical representative

```text
P4={1,4},   P5={0,1,5}.
```

The universal split `x3<=x4` versus `x3>x4` closes its relay.  The frozen
certificate below replaces that shared-encoder result with exact rational
identities and a solver-free checker.  It is a finite proof object, not an
external review or a novelty determination.

## 2. Asymmetric packet sandwich

Set

```text
di=xi-zi>0       (i=0,1,2,3),
delta4=z4-x4>0,  delta5=z5-x5>0.
```

Efficiency and the two packet comparisons give

```text
d0+d1+d2+d3 = delta4+delta5,
d1    <= delta4 <= d2+d3,
d0+d1 <= delta5 <= d0+d2+d3.                     (2.1)
```

The pure `Fraction` checker uses (2.1) to recompute every feasible negative
cut by exact Fourier--Motzkin elimination.

## 3. Eleven-leaf relay

On the weak branch `W`, Lmin exchange

```text
h16=-e1-e2+e4+e5
```

has the unique blocker `{0,1,2,4}`; the resulting Lmax exchange `h10=e0-e1`
has no blocker.  This is the single weak leaf.

On the strict branch `S`, Lmin exchange `h17=-e1-e3+e4+e5` has four blockers.
Their subtrees are:

```text
{1,3,4}:
  h16 -> {1,2,4}  -> h18 closes;
       -> {0,1,2,4} -> h18 -> {2,3,4} -> h10 -> {1,3,4} -> h11 closes.

{0,1,3,4}:
  h10 -> {1,2}       -> h18 closes;
      -> {1,3}       -> h18 closes;
      -> {1,2,4}     -> h16 -> {1,2,4} -> h18 -> {2,3,4} -> h12 closes;
      -> {1,3,5}     -> h16 closes.

{1,3,5}:
  h16 -> {1,2,5} or {0,1,2,5}; h18 closes both.

{0,1,3,5}:
  h16 -> {1,2,5}     -> h18 closes;
       -> {0,1,2,5}  -> h10 closes.
```

Here

```text
h18=-e2-e3+e4+e5,
h11=e0+e3-e4-e5,
h12=e0+e2-e4-e5.
```

The strict branch has ten leaves and depth at most four.  Together with the
weak leaf, the exact relay has 21 stages and eleven terminal leaves.

## 4. Shared extremal-level activation lemma

For every Lmin two-for-two exchange `-e_a-e_b+e_4+e_5`, activation is

```text
min(xa,xb)>min(x4,x5).
```

For the Lmax dual `e_a+e_b-e_4-e_5`, activation is

```text
max(za,zb)<max(z4,z5).
```

The failure of either statement has four DNF conjunctions.  The checker
verifies both equivalences on all 256 four-level assignments and audits those
four cases at every two-for-two node.  The four `h10` nodes each have the
single failure `z1<=z0`.  Thus all activation logic is covered by

```text
17*4 + 4 = 72 cases.
```

## 5. Exact census and proof-object compression

The 21 difference-cone censuses contain 79 feasible opposite-cut candidates.
Nineteen are the displayed relay edges; exact payoff/witness identities exclude
the other 60.  After deduplication,

```text
52 blocker identities + 56 activation identities = 108 identities,
60 blocker uses       + 72 activation uses        = 132 uses.
```

Of the 60 blocker exclusions, 38 use only `q1`, ten use only the opposite
allocation, and twelve use both.  Across all uses, 120 identities target
`D-1/3`, seven target the strictly positive P-sign `x0-z0`, and five target
the strictly negative strict-branch order `x4-x3`.

The checker rebuilds every premise at every use site, recomputes all candidate
sets, and rejects mutations of a coefficient, use site, candidate set, use
map, activation atom, or strict-target semantics.  It imports no solver and no
production encoder.

## 6. Reproduction and review boundary

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class2_hand_certificates.py \
  --output /tmp/strict_exchange_p4_class2_hand_certificate_audit.json
cmp /tmp/strict_exchange_p4_class2_hand_certificate_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class2_hand_certificate_audit.json
```

A reviewer should independently derive (2.1), the 21 candidate sets, all eleven
leaves, and both extremal-level activation equivalences.  The checker proves
the frozen affine arithmetic; it does not by itself prove that every genuine
game-theoretic counterexample enters the packet relaxation.  That implication
remains the primary external-review gate.
