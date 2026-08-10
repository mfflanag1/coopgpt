# Forced-blocker packet classification in the six-player `(4,2,0)` case

Date: 2026-08-10

## 1. The two blockers that cannot be avoided

Continue with the anchor-localized notation

```text
P={0,1,2,3},  M={4,5},  a=0,  b=1,
x=Lmin(v),    z=Lmax(v), q=q^1,
```

where `0` is an `x`-bottom player, `1` is a `z`-top player, and `q` is the
singleton exactness witness with `q_1=0`.  The two Lmin directions

```text
h^5=-e_1+e_5,     h^4=-e_1+e_4
```

are automatically lex-improving.  Indeed, for either `m in M`,

```text
x_1 > z_1 >= z_m > x_m.
```

Their negative tight blockers must therefore exist.  A blocker for `h^5`
contains `1` and excludes `5`.  Its opposite comparison `z(S)>=x(S)` forces
it to contain `4`: without player `4`, every member of `S` lies in `P`, where
`x_i>z_i`.  The same argument with `4,5` exchanged gives

```text
S_4={1,4} union A,    S_5={1,5} union B,
A,B subsets of R={0,2,3}.
```

Thus the original sixteen alternatives for each of these directions become
one exhaustive choice of a two-blocker packet `(A,B)` among only 64 labelled
pairs.  Each selected blocker satisfies both

```text
z(S)>=x(S),     q(S)>=x(S).
```

## 2. A packet inequality visible by hand

Put

```text
d_i=x_i-z_i,       w_i=x_i-q_i,
I=A intersect B,   C=R \ (A union B).
```

The two opposite comparisons give

```text
z_4-x_4 >= d_1+d(A),     z_5-x_5 >= d_1+d(B).
```

Since `sum d=0`, adding them and cancelling the `P/M` totals yields

```text
d(C) >= d_1+d(I).                                  (P1)
```

Similarly, the two `q` comparisons say `w(S_4)<=0` and `w(S_5)<=0`.
Using `sum w=0` and `w_1=x_1` gives

```text
w(C) >= x_1+w(I).                                  (P2)
```

In particular `C` is nonempty, because every `d_i` in `P` is positive.  This
is the human reason the two C1 directions form a coupled packet rather than
two unrelated blocker disjunctions.

The aggregate pair `(P1),(P2)` is not sufficient by itself: it forgets which
of the remaining players belongs to `A` and which belongs to `B`.  The exact
classification below deliberately retains that information.

## 3. Eleven exact packet classes

The residual symmetry independently swaps players `2,3` and players `4,5`;
the second swap exchanges `A` and `B`.  Of the 64 labelled pairs, 32 are
already inconsistent with the localized base constraints.  The other 32
form exactly eleven orbits.  For each representative, the table records a
subset-minimal menu of the remaining seventeen exchange implications that
closes it.  `Cj:k` means direction index `k` in parent schema `Cj` of the
frozen localized audit.

| class | `A` | `B` | orbit size | core size | subset-minimal residual core |
|---:|---|---|---:|---:|---|
| 1 | `-` | `-` | 1 | 4 | `C3:10, C6:16, C6:17, C6:18` |
| 2 | `-` | `0` | 2 | 6 | `C3:10, C4:11, C4:12, C6:16, C6:17, C6:18` |
| 3 | `-` | `02` | 4 | 2 | `C6:17, C6:18` |
| 4 | `-` | `2` | 4 | 3 | `C3:9, C6:17, C6:18` |
| 5 | `0` | `0` | 1 | 7 | `C3:10, C4:11, C4:12, C5:15, C6:16, C6:17, C6:18` |
| 6 | `0` | `02` | 4 | 7 | `C2:7, C3:10, C4:11, C4:12, C5:15, C6:17, C6:18` |
| 7 | `0` | `2` | 4 | 4 | `C3:10, C4:12, C6:17, C6:18` |
| 8 | `02` | `02` | 2 | 1 | `C6:17` |
| 9 | `02` | `2` | 4 | 4 | `C2:6, C3:9, C5:14, C6:17` |
| 10 | `2` | `2` | 2 | 4 | `C3:9, C4:12, C5:14, C6:17` |
| 11 | `2` | `23` | 4 | 3 | `C2:3, C3:9, C5:14` |

The orbit sizes sum to 32, so the table covers every base-feasible packet.
Every displayed core is subset-minimal: deleting any one of its directions
makes that packet relaxation SAT.  This does not mean the core has minimum
cardinality, and the SAT ablations are not exact games.

The reduction changes the opaque residue from

```text
two 16-way C1 disjunctions plus seventeen implications
```

to

```text
eleven concrete packet rows, each using at most seven residual implications.
```

The table as a whole remains a finite computer-assisted lemma.  A complete
hand proof would still have to replace the residual blocker alternatives in
the unresolved rows by explicit inequalities or Farkas combinations.  Eight
rows can now be removed from that residue completely.

`S6_P4_RELAY_TREES.md` decomposes the remaining cores dynamically.  Five
classes (`3,4,7,8,11`), covering eighteen of the 32 feasible labelled packets,
close by forced-exchange relay trees with no order split, and all five are now
complete hand-checkable proofs.  Class 9 adds a sixth hand-checkable row after
the exhaustive split `x_3<=x_4` versus `x_3>x_4`, bringing the total to
twenty-two packets.  Class 10 adds a seventh hand-checkable row after the same
root split and one nested comparison, bringing the total to twenty-four
packets.  Class 1 is now the eighth hand-checkable row: twenty-one exact cut
censuses and 109 rational identities at 160 uses bring the total to twenty-five
packets.  Class 2 is the ninth: 21 cut censuses and 108 identities at 132 uses
bring the total to twenty-seven.  Of the two classes covering the other five
packets, class 6 now has complete exact arithmetic conditional on its frozen
relay/use maps, while class 5 retains machine-resolved residue.  Both close
under the same root split `x_3<=x_4` versus
`x_3>x_4`; in fact this split gives complete relay trees for all eleven
classes, with only class 10 needing one nested `x_1`/`x_2` split.
Class 4 uses
a three-leaf star whose terminal cuts are closed by sixteen `q^1`-complement
identities and four opposite-base-cut identities, all checked with pure exact
rational arithmetic in `verify_strict_exchange_p4_class4_hand_certificates.py`.
Class 11 uses a unique three-exchange chain: its activations are structural and
37 source-specific rational identities prove the exact two-blocker chain and
empty terminal blocker list.  Class 7 uses an eight-stage exact
difference-cone census, sixteen blocker filters, and nine activation identities
to humanize its depth-three relay without expanding it into a cut-by-cut dump.
Class 9 uses ten exact difference-cone censuses and 52 distinct rational
identities, checked at all 71 uses by a solver-free verifier.
Class 10 uses eighteen exact censuses and 108 identities checked at all 122
uses; 103 of its 105 blocker exclusions require only `q^1`.
Class 1 uses twenty-one exact censuses and a minimum-level lemma compressing
its activation audit to 75 cases; its 65 blocker plus 44 activation identities
are checked at all 160 uses without a solver or production import.
Class 2 uses the same lemma and its maximum-level dual; 52 blocker plus 56
activation identities are checked at all 132 uses.
Class 5 now has a solver-free packet skeleton, although not yet a complete
hand certificate.  Its symmetric packet gives
`d0+d1<=delta4,delta5<=d2+d3`; a cross-anchor chain makes both one-for-one
directions automatically improving, and the packet sandwich reduces every
`h15` blocker census from sixteen eligible cuts to the same ten candidates.
This single lemma covers all ten `h15` nodes of the 90-node frozen relay.  A
three-orbit crossing lemma then excludes seven of the thirty formal pairs
between their three `h10` predecessor blockers and ten `h15` candidates.  The
root order split is also human: the weak `h11` root has exactly `24,124,25`
as blockers, while the strict `h17` root has exactly
`134,0134,135,0135`; one seven-term witness identity is the only
non-sign filter needed at this layer.
Class 6 has a parallel solver-free root skeleton.  Its asymmetric packet gives
`d0+d1<=delta4<=d3` and `d0+d1+d2<=delta5<=d2+d3`; these stronger bounds
reduce the weak and strict twenty-cut roots directly to `24,124` and
`135,0135`, with no witness filter.
The cut filters themselves now have complete exact accounting.  Across the 49
class-6 nodes, 924 eligible cuts split into 711 pure difference-cone
exclusions and 213 candidates.  Of those candidates, 11 are excluded by the
existing packet/ancestor witness context, 155 by the target witness, and 47
are exactly the relay branches.  Only ten distinct difference-cone candidate
sets occur.  The witness filters have an exact common description: for any
coalition menu, the `q^1`-sum image is the convex hull of the five non-anchor
incidence columns.  Its nonnegative support function is the maximum
non-anchor incidence load.  This zero-anchor over-cover duality turns the
class-5 crossing identities into sparse incidence covers and gives an LP/facet
algorithm for the remaining witness filters.  In class 6 this program is now
exhaustive on the witness side: all 155 witness-rejected cuts across 49 stages
have supports of size at most five; 150 use unit coefficients and five use a
coefficient two.  The associated allocation-side strict inequalities are
now 53 deduplicated exact rational identities checked solver-free at all 155
uses.  Thirty-one identities need no path premise; 22 use an ancestor or
target comparison.  The 11 context exclusions similarly reduce to nine exact
identities.  A solver-free checker verifies the exhaustive
`213=11+155+47` partition and therefore every terminal no-blocker closure.
The use maps remain relay-derived, so this is a complete arithmetic
certificate conditional on those maps rather than an externally validated
tenth hand certificate.
At the activation layer, the 49 nodes yield 124 elementary failure cases.
Anchor/order arguments remove 84, four are allocation-infeasible, and all 36
remaining failures have packet/ancestor over-covers of support at most four.
This unifies activation and blocker filtering under the same incidence
theorem.  The 36 activation lower bounds now have 26 solver-free rational
identities, while the four direct cases share one more identity; only their
relay-derived coverage map remains encoding-shared.
The older order-tree artifact gives an encoding-shared differential check of
the class-9, class-10, class-1, and class-2 hand certificates.  The universal order audit
extends the same root comparison to all eleven rows; classes 5 and 6 remain
machine-checked hand-proof targets.

## 4. Class 3 is a two-exchange hand relay

For class 3, `A` is empty and `B={0,2}`.  The packet `q` comparisons are

```text
q_4 >= x_1+x_4,                                  (Q4)
q_0+q_2+q_5 >= x_0+x_1+x_2+x_5.                  (Q5)
```

The complement form of `(Q5)` is `q_3+q_4<=x_3+x_4`.  Together with `(Q4)`
it gives `x_3>=x_1+q_3>=x_1`.  Since the anchor order gives
`x_1>x_4,x_5`, the direction

```text
h^1=-e_1-e_3+e_4+e_5
```

necessarily improves Lmin.

Its blocker can be classified by hand.  A negative cut with no `M` player
has positive `d=x-z` sum.  If it contains player `4`, it contains both
negative-coefficient players `1,3`; the other packet inequality gives
`delta_4<=d_3`, so its `d` sum is at least `d_1>0`.  For a cut through player
`5`, the only optional players are `0,2`.  Including `2` but not `0` makes the
`q` comparison imply `q_0+q_4<=x_0+x_4`; `(Q4)` then gives `x_1<=x_0`,
contrary to `x_0<=x_4<x_1`.  Including both `0,2` leaves the complement
`{4}` and has positive `d` sum `delta_4`.  Hence the blocker must be

```text
S_K={1,3,5} union K,     K either empty or {0}.    (B1)
```

Either choice activates a second direction

```text
h^2=-e_2-e_3+e_4+e_5.
```

If `K={0}`, the complement of the `q` comparison in `(B1)` gives
`q_2+q_4<=x_2+x_4`; `(Q4)` yields `x_2>=x_1+q_2>x_4,x_5`.  If `K` is empty,
the same two comparisons give

```text
x_0+x_2 >= x_1+q_0+q_2.
```

Were `x_2<=x_4,x_5`, bottomness of `x_0` would imply
`x_4+x_5>=x_1`.  Therefore

```text
D=z_4+z_5-x_4-x_5 <= z_4+z_5-z_1 <= 1/3,
```

where the last inequality uses `z_4,z_5<=z_1` and `sum z=1`.  This
is the estimate
`3(z_4+z_5-z_1)<=z_1+z_4+z_5<=1`.  It contradicts `D>1/3`, so `h^2`
improves Lmin in both subcases.

The same cut classification shows that its blocker must be

```text
T_L={2,3,5} union L,     L either empty or {0}.    (B2)
```

It remains to exclude the four pairs `(K,L)`.  Add twice `(Q4)`, once `(Q5)`,
and the `q` comparison for `(B1)`.  With `k=1` when `K={0}` and zero otherwise,
efficiency of `x,q` and `q_1=0` reduce the sum to

```text
q_4+q_5+k q_0 >= x_4+x_5+3x_1+k x_0.
```

Nonnegativity gives `x_1<=1/3`.  If `L` is empty, the complement of the
opposite comparison in `(B2)` is

```text
z_0+z_1+z_4 <= x_0+x_1+x_4.
```

Using `z_5<=z_1`, `x_0<=x_5`, and `z_0>=0` gives `D<=x_1`.  If `L={0}` the
complement is `z_1+z_4<=x_1+x_4`, which again gives `D<=x_1`.  Thus every
pair has `D<=1/3`, the final contradiction.

This closes all four labelled packets in class 3 by hand.  The local audit
checks the first activation, the exact two-candidate blocker lists, both
relay activations, and all four final blocker-pair contradictions from a
fresh statement of the displayed premises.

## 5. Class 8 closes completely by hand

For class 8, `A=B={0,2}`.  Write

```text
D=d(P)>1/3,   s=d_0+d_1+d_2,
delta_m=z_m-x_m=-d_m  for m in M.
```

Consider the single residual direction in its core,

```text
h=-e_1-e_3+e_4+e_5.                               (H)
```

First, `(H)` is necessarily Lmin-improving.  Suppose instead that
`x_3<=x_4,x_5`.  The two packet opposite comparisons imply

```text
x(P) <= z_0+z_1+z_2+z_4,
x(P) <= z_0+z_1+z_2+z_5,
```

because `x_3<=x_4,x_5`.  Subtracting `z(P)` gives

```text
D <= z_4-z_3,      D <= z_5-z_3.
```

The top-anchor order `z_1>=z_4` and nonnegativity now give

```text
1=sum z >= z_1+z_4+z_5+z_3 >= 3D+4z_3 >= 3D,
```

contrary to `D>1/3`.  Hence `x_3>min{x_4,x_5}`.  The anchor chain already
gives `x_1>x_4,x_5`; choosing the lower of players `4,5` shows that the lowest
stratum touched by `(H)` has positive and no negative coefficients.  Thus
`(H)` improves Lmin.

Second, `(H)` has no possible opposite blocker.  The packet inequalities say

```text
delta_4>=s,       delta_5>=s.
```

Since `delta_4+delta_5=D=s+d_3`, each `delta_m<=d_3`.  If `h(S)<0` and `S`
contains no `M` player, then it contains at least one of `1,3` and only
positive-`d` players, so `d(S)>0`.  If it contains exactly one `M` player
`m`, it must contain both `1,3`, and therefore

```text
d(S) >= d_1+d_3-delta_m > 0.
```

With both `M` players, `h(S)<0` is impossible.  Consequently every eligible
negative cut has `x(S)>z(S)`, while an Lmin blocker would require
`z(S)>=x(S)`.  No blocker exists, contradicting optimality.

This is an all-human closure of one full packet orbit (two of the 32 labelled
feasible packets).  It uses neither the `q^1` blocker comparison nor a solver
in the proof.  The audit separately checks the negation of the activation
argument and all twenty eligible negative cuts from only the displayed
reduced premises.

## 6. Reproduction and proof status

Run from the repository root with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp /tmp/strict_exchange_p4_packet_classes.json \
  coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
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
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class5_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class5_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class5_packet_skeleton_audit.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_packet_skeleton.py \
  --output /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json
cmp /tmp/strict_exchange_p4_class6_packet_skeleton_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_packet_skeleton_audit.json
python3 coopgames/verifiers/s6/verify_zero_anchor_overcover_duality.py \
  --output /tmp/zero_anchor_overcover_duality_audit.json
cmp /tmp/zero_anchor_overcover_duality_audit.json \
  coopgames/verifiers/s6/zero_anchor_overcover_duality_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --output /tmp/strict_exchange_p4_class6_overcovers.json
cmp /tmp/strict_exchange_p4_class6_overcovers.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_overcovers.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_allocation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_allocation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_allocation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_allocation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_class6_activation_overcovers.py \
  --details --output /tmp/strict_exchange_p4_class6_activation_overcovers_details.json
python3 coopgames/verifiers/s6/verify_strict_exchange_p4_class6_activation_identities.py \
  --overcover-details /tmp/strict_exchange_p4_class6_activation_overcovers_details.json \
  --output /tmp/strict_exchange_p4_class6_activation_identity_audit.json
cmp /tmp/strict_exchange_p4_class6_activation_identity_audit.json \
  coopgames/verifiers/s6/strict_exchange_p4_class6_activation_identity_audit.json
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_universal_order_relays.py \
  --output /tmp/strict_exchange_p4_universal_order_relays.json
cmp /tmp/strict_exchange_p4_universal_order_relays.json \
  coopgames/verifiers/s6/strict_exchange_p4_universal_order_relays.json
```

The audit independently checks within the parent encoding that

1. both C1 antecedents are forced;
2. all 64 blocker pairs receive a determinate SAT/UNSAT verdict;
3. exactly 32 pairs are base-feasible;
4. the eleven representatives cover all 32 pairs under the residual group;
5. every representative plus all remaining implications is UNSAT; and
6. every single deletion from every displayed residual core is SAT;
7. the class-3 relay has exactly two blockers at each stage and all four
   blocker pairs are UNSAT;
8. the reduced class-8 activation negation is UNSAT; and
9. each of the twenty eligible class-8 blocker comparisons is UNSAT without
   a `q^1` premise;
10. the class-11 activation negations are UNSAT, and the displayed
    `x_1<=x_2` and `C={0,1}` weighted sums are literal identities; and
11. the independently restated class-11 relay has the unique blockers
    `{0,1,2,5}`, then `{0,1,3}`, and no terminal blocker; and
12. the separately restated class-4 star has exactly five opposite candidates,
    exactly three full root blockers, all three forced child activations, and
    no terminal blocker; the first leaf closes using `q^1` comparisons alone
    and the other two using opposite comparisons alone; and
13. the solver-free class-4 certificate checker exhausts all sixteen
    `q^1`-complement cuts and all four opposite-base-cut cases, uses only
    nonnegative inequality multipliers, and verifies every exact weighted
    identity with rational coefficient arithmetic; a one-coefficient mutation
    is rejected; and
14. the solver-free class-11 checker exhausts its two opposite exceptions,
    four first-stage `q^1` filters, fifteen second-stage `q^1` filters, and
    sixteen terminal `q^1` filters, verifies 37 exact identities, and rejects
    its mutation control; and
15. the solver-free class-7 checker independently recomputes all eight
    difference-cone cut censuses by exact Fourier--Motzkin elimination,
    verifies sixteen blocker filters and nine activation identities, and
    rejects both coefficient and candidate-set mutations; and
16. the order-split audit closes class 9 after `x_3<=x_4` versus `x_3>x_4`,
    and class 10 after the same root split plus `x_1<=x_2` versus `x_1>x_2`
    on the weak branch; every order branch remains SAT before its relay is
    added; and
17. the solver-free class-9 checker independently recomputes all ten exact
    difference-cone cut censuses, checks 52 distinct rational identities at
    all 71 stage uses, exhausts all 56 discarded blockers and eleven relay
    activations, and rejects coefficient, use-site, candidate-deletion,
    use-map-deletion, and strict-target mutations; and
18. the solver-free class-10 checker independently recomputes all eighteen
    exact difference-cone censuses, checks 108 identities at 122 uses,
    exhausts 105 discarded blockers and seventeen activations, localizes 103
    blocker exclusions to `q^1` and two to the opposite comparison, and
    rejects the same five mutation classes; and
19. the universal order audit closes all eleven packet classes after the
    single root split `x_3<=x_4` versus `x_3>x_4`; class 10 is the unique row
    needing `x_1<=x_2` versus `x_1>x_2` on its weak branch.

The authoritative proof object for the unsplit, weaker relaxation remains
the trust-disabled CPC proof in
`p4_anchor_core_certificates/strict_exchange_p4_anchor_core.cpc`, checked by
Ethos.  The eleven packet rows strengthen that parent formula by selecting
concrete disjuncts, so this classification is an explanatory decomposition,
not independent evidence for the theorem or for the human-to-machine map.
