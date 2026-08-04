# Uniqueness of the first two-poorer hypergraphic obstruction

## The theorem

Let `v` be a singleton-normalized exact game, `phi=Lmin(v)`, and let a strict
boundary have two poorer players and exactly four richer players `H`. If `H`
is slack at `phi`, then the active trace exact-cover polytope has the vertex

```text
beta_(H\{h})=1/3 for every h in H,
beta_R=0 otherwise.
```

Consequently all four co-singletons of `H` occur as traces of proper
`phi`-tight coalitions. This identifies the first realizable obstruction up to
relabeling, rather than merely proving that some obstruction exists.

## Human four-point classification

At a vertex of the exact-cover polytope, the positive incidence columns are
linearly independent, so there are at most four. The full trace `H` can only
appear alone as an integral vertex. For proper traces, classify a fractional
vertex by the number `t` of triple columns. Relabeling `H=1234` and subtracting
the four cover equations gives:

| Type | Positive traces | Positive weights | Number of triples |
|---|---|---|---:|
| A | `1; 23,24,34` | `1; 1/2,1/2,1/2` | 0 |
| B | `1,23,24,134` | `1/2,1/2,1/2,1/2` | 1 |
| C | `12,134,234` | `1/2,1/2,1/2` | 2 |
| D | `12,13,14; 234` | `1/3,1/3,1/3; 2/3` | 1 |
| E | `123,124,134,234` | `1/3,1/3,1/3,1/3` | 4 |

The cases `t=0,1,2,3,4` yield respectively `A`; `B` or `D`; `C`; no positive
independent solution; and `E`. Direct substitution verifies each row. This is
a four-equation human classification; the discovery enumeration is not a
proof dependency.

## Why A--D are impossible

Balanced-trace transport supplies poor displacements

```text
Delta_a<0<Delta_b,
Delta_a+Delta_b=s,
```

and a lifted extreme packet with gaining-poor load `r_b<1`. Writing
`delta=-Delta_a>0`, the packet inequality is

```text
s(r_b-1)+delta(r_b-r_a)>=0.
```

Hence `r_a<r_b`.

A **safe root rounding** selects supported lifted coalitions so that the rich
load is `1_H+e_d`, each poor load is zero or one, and at least one poor player
is loaded. Types A--C are half-integral: the inequalities above force exactly
one half-weight coalition to carry `b` and none to carry `a`. The following
root roundings collectively contain every half-weight column:

```text
A: singleton 1 plus the two alternating edges containing the b-edge;
B: {24,134}, {23,134}, or {1,23,24};
C: {12,234} or {12,134}.
```

For type D, scale poor loads by three. If the weight-`2/3` triple carries `b`,
no pair does and at least two pairs carry no `a`. If the triple does not carry
`b`, one or two pairs do, the triple carries no `a`, and some `b`-pair carries
no `a`. Therefore one of

```text
{234,12}, {234,13}, {234,14}
```

is always a safe root rounding.

Exactify the duplicated rich singleton `d` and sum the selected original
tight-coalition inequalities. Add singleton inequalities for any omitted poor
player. If neither poor player is omitted, the right side exceeds efficiency
by `phi_d>0`; if one is omitted, it exceeds efficiency by
`phi_d-phi_i>0`. Thus safe root roundings are impossible.

These are precisely multiplicity-one safe rooted tight covers, so all four
contradictions are instances of the dimension-free theorem in
[`ROOTED_SEMIGROUP_OBSTRUCTION.md`](ROOTED_SEMIGROUP_OBSTRUCTION.md).

Only type E remains. It is exactly the four-co-singleton vertex used by the
sharp six-player internal-sacrifice family.

## Significance and limit

Together with the corrected rank-two trace exclusion, this gives a structural progression:

```text
nonintegrality is necessary;
graph-like underloaded packets are impossible by a real tight-cover overload;
at the first feasible rich-side size, the co-singleton 1/3 packet is unique.
```

This is a human local-minor theorem, not a dimension-free converse for all
larger suffixes.  The latter converse is now disproved by
[`THREE_TRACE_HALF_INTEGRAL_OBSTRUCTION.md`](THREE_TRACE_HALF_INTEGRAL_OBSTRUCTION.md):
from five rich players onward an exact family has only three active trace
columns and a unique half-integral cover.  Thus genuinely new irreducible
hypergraphs occur immediately one rich-side dimension later.

Correctness and novelty still require hostile specialist review.
