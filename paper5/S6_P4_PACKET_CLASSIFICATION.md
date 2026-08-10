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

It remains a finite computer-assisted lemma.  A complete hand proof would
still have to replace the residual blocker alternatives in these eleven rows
by explicit inequalities or Farkas combinations.

## 4. Reproduction and proof status

Run from the repository root with the Z3-enabled Python environment:

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_p4_packet_classes.py \
  --output /tmp/strict_exchange_p4_packet_classes.json
cmp /tmp/strict_exchange_p4_packet_classes.json \
  coopgames/verifiers/s6/strict_exchange_p4_packet_classes.json
```

The audit independently checks within the parent encoding that

1. both C1 antecedents are forced;
2. all 64 blocker pairs receive a determinate SAT/UNSAT verdict;
3. exactly 32 pairs are base-feasible;
4. the eleven representatives cover all 32 pairs under the residual group;
5. every representative plus all remaining implications is UNSAT; and
6. every single deletion from every displayed residual core is SAT.

The authoritative proof object for the unsplit, weaker relaxation remains
the trust-disabled CPC proof in
`p4_anchor_core_certificates/strict_exchange_p4_anchor_core.cpc`, checked by
Ethos.  The eleven packet rows strengthen that parent formula by selecting
concrete disjuncts, so this classification is an explanatory decomposition,
not independent evidence for the theorem or for the human-to-machine map.
