# Class-5 rich-packet skeleton

## 1. Scope

Packet class 5 is the symmetric labelled packet

```text
P4={0,1,4},   P5={0,1,5}.
```

Its universal order relay closes, but the raw tree has 90 nodes and 51
leaves.  This note extracts reusable hand lemmas and gives complete exact
arithmetic for that tree conditional on its frozen relay/use maps.  It is not
yet an independent derivation of those maps, external review, or novelty
evidence.

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

This packet-level lemma alone does not close the 51 leaves.  Sections 7--8
settle their arithmetic exhaustively; the remaining humanization task is to
compress how preceding blocker comparisons filter (5.2) and force the
terminal two-for-two exchanges.

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

Conceptually, the witness half of all three identities is one incidence
over-cover.  The relevant comparison coalitions load every non-anchor player
once (or twice) and may overload only player 1, where `q1=0`; hence their
`q`-sums are at most one (or two).  `S6_ZERO_ANCHOR_OVERCOVER_DUALITY.md`
proves the exact support-function theorem behind this observation.

Thus the common predecessor/successor census falls from thirty formal pairs
to 23, and every actual class-5 relay edge respects the resulting crossing
rule.  Together with the root lemma, this isolates the remaining work to the
non-root blocker filters and terminal two-for-two closures.  The next two
sections settle their arithmetic exhaustively, while leaving conceptual
compression and independent validation of the maps open.

## 7. Complete cut-layer accounting

Exact Fourier--Motzkin elimination in the five difference coordinates gives
the following exhaustive partition across all 90 stages:

```text
1736 eligible negative-cut uses
 = 1464 pure difference-cone exclusions
 +   34 packet/ancestor-context exclusions
 +  150 target-witness exclusions
 +   88 relay branches.                              (5.5)
```

The 272 candidates left after the pure difference cone have only 24 distinct
candidate sets.  Every one is assigned exactly once to the last three layers
of (5.5), including every terminal no-blocker closure.  This is checked by a
solver-free exact-arithmetic census with mutations of the candidate digest,
direction and layer partition.

The 34 context exclusions and 150 target exclusions have sparse incidence
over-covers.  Context supports have size at most five, with sixteen of 34
using a coefficient two.  Target supports have size at most four, with only
three of 150 using a coefficient two.  The zero-anchor support theorem proves
their witness-side upper bounds.  Their allocation-side strict lower bounds
deduplicate to 107 exact rational identities checked at all 184 uses.  Of
those uses, 94 need no path comparison, 50 use ancestors only, 38 use the
target comparison only, and two use both.  Hence no cut-filter arithmetic
remains solver-only.  The assignment of the 34, 150 and 88 uses is still a
relay-derived integration record, not an independently derived hand map.

### A 15-template menu atlas

The 24 labelled candidate sets are not 24 unrelated cases.  Let
`r in {4,5}` and write `rbar=9-r`; juxtaposition denotes a coalition.  Put

```text
B10={1,12,13,123,124,125,1234,1235},
D10={1,12,13,123,1234,1235},
B15={14,15,134,135,145,1245,1345,12345}.
```

Every stage menu is one of the following fifteen parametric templates:

```text
h10: B10+{13r};                    D10+{12rbar,13rbar}
h11: {24,25,124,125};              {2rbar,12rbar}
h12: {13rbar};                     {3rbar,13rbar}
h15: B15+{12r}
h16: {12r}; {12r,012r};            {124,125,012r}
h17: {135,0135};                   {134,135,0134,0135}
h18: {23r};                        {234,235}.
```

Expanding `r=4,5` and removing the non-parametric duplicates gives exactly
the 24 stored menus.  The largest repetition is especially simple: the two
`h16` pair menus occur fifteen times each, while their singleton versions
occur nine times in total.  The cut verifier checks template membership and
the exact multiplicity of every labelled expansion, in addition to the
stage-by-stage candidate digest.

### A path-local transition grammar

The 88 relay edges also have a short description.  On the weak branch:

```text
h11(root) -> {24,124,25};
h11:2r -> h10:{12,123,124,13r};
h10:12  -> h15:{145,1245,1345};
h10:123 -> h15:{134,135,145,1345}.
```

All descendants are terminal except the three continuations

```text
(24,12,145) -> h16:0125,
(24,124)    -> h16:0125,
(124)       -> h16:0125,
```

whose following `h17` nodes are terminal.  On the strict branch:

```text
h17(root) -> {13r,013r}.
```

The short root blocker `13r` gives

```text
h16 -> {12r,012r};
012r -> h18:23r -> h11:2rbar,
```

and the resulting `h10` is terminal.  The long root blocker `013r` gives

```text
h10 -> {12,13,123,12r,13rbar}.
```

Its five successors obey only these rules:

```text
12   -> h18:23r -> h15:12r -> terminal h12;
13   -> h15:{14,134,15,135,145,1345,12345};
        only 13r,145,1345 continue h16:012r,
        and only 13r then continues h18:23r;
123  -> h15:{134,135,145,1345}, with terminal h16 children;
12r  -> h16:12r -> h18:23r -> terminal h12;
13rbar -> terminal h15.
```

These rules generate exactly 88 edges and 51 terminal leaves.  Unlike a raw
stage list, they expose the two true state variables: the weak/strict root
regime and the selected rich player `r`, with only three exceptional weak
continuations.  The verifier compares this grammar directly with every
stored child set and rejects a relay-edge deletion.  This materially
compresses the map, but external review must still establish that the relay
semantics themselves are necessary for every genuine counterexample.

## 8. Complete activation-layer accounting

The 90 stages have 285 elementary activation-failure conjunctions.  Their
exact partition is

```text
285 = 195 allocation-infeasible cases + 90 witness over-covers.       (5.6)
```

The failure expansion includes the four conjunctions for the two-for-two
Lmin direction

```text
(x1<=x4 or x2<=x4) and (x1<=x5 or x2<=x5),
```

so (5.6) audits the disjunction rather than replacing it by a stronger
one-for-one condition.  Every one of the 90 witness cases has a unit-weight
incidence support of size at most four; these reduce to 63 support signatures.
The allocation arithmetic for all 285 cases deduplicates to 72 exact rational
identities: 18 zero-target contradictions cover the 195 infeasible cases and
54 strict lower-bound identities cover the 90 witness cases.  A solver-free
checker reconstructs every failure atom and named affine premise, checks its
availability on the recorded relay path, verifies the detailed witness digest,
and rejects coefficient, failure-case and layer-partition mutations.

The 285-use map itself has a sharp path-free/path-dependent split.  Forty-one
identities use only global anchors or the root order and cover 253 uses:
29 anchor/sign identities cover 202 uses and twelve order identities cover 51.
Only 32 uses require an ancestor comparison.  They fall into three relay
families:

```text
terminal h11/h12 endpoints:       4+4 =  8 uses,
exceptional h16 activations:  2+1+1+9 = 13 uses,
terminal h17/h18 activations:   2+6+3 = 11 uses.       (5.7)
```

If source-depth aliases are forgotten and the rich-player swap `4<->5` is
canonicalized, the 72 stored identities reduce to 47 exact affine motifs.
The 41 path-free identities give 27 motifs; the 31 path-dependent identities
give only 20 motifs at the 32 uses in (5.7).  The verifier recomputes this
canonicalization from the exact affine forms rather than trusting identity
labels, and rejects a path-site mutation.  Thus the opaque residue is no
longer a 285-row list: it is a global 253-use layer plus a 32-use residual in
three geometrically identifiable families.  A reviewer must still derive the
placement of those residual uses from the relay semantics.

Equations (5.5)--(5.6) put class 5 at the same proof status as class 6: all
arithmetic leaves are exact and solver-free conditional on frozen relay/use
maps.  It is still not a tenth independently hand-derived packet lemma.  A
reviewer must verify the maps against the relay semantics and the overarching
counterexample-to-formula implication.  The cut menus and transitions now
have the orbit-level atlas and path grammar above; activation is reduced to
47 affine motifs and the 32-use residual (5.7).  The remaining task is a
human derivation of that residual placement rather than further arithmetic.

## 9. Solver-free audit

Run

```bash
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_packet_skeleton_audit.json

python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class5_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class5_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class5_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class5_allocation_identity_audit.json
cmp /tmp/strict_exchange_p4_class5_allocation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_allocation_identity_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_cut_census.py \
  --output /tmp/strict_exchange_p4_class5_cut_census_audit.json
cmp /tmp/strict_exchange_p4_class5_cut_census_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_cut_census_audit.json

python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class5_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class5_activation_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class5_activation_details.json \
  --output /tmp/strict_exchange_p4_class5_activation_identity_audit.json
cmp /tmp/strict_exchange_p4_class5_activation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_activation_identity_audit.json
```

The checker imports no solver or production encoder.  Exact rational
coefficient arithmetic verifies (5.1), every cut identity, the exhaustive
sixteen-cut partition, both twenty-cut root classifications, the weak-root
witness identity, and all seven crossing exclusions through three orbit
identities.  The additional checkers prove the exact cut and activation
identities over the rationals without a solver.  Finite total-preorder
enumeration checks the anchor and root activation chains and rejects
weakened-sign mutations.  Reading the frozen relay is confined to separately
labelled integration audits; it is not proof evidence for the lemma, the use
maps, or the human-to-machine implication.
