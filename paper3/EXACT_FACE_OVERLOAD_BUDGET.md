# Exact-face overload budget

## Statement

Let `v` be singleton-normalized and exact and let `phi` be a core allocation.
Split the players as a proper rich side `H` and its complement `L`. Take
nonnegative real weights on proper coalitions tight at `phi`. Suppose their
incidence load is

```text
1_H + q 1_D  on H,       q>0 and nonempty D subset H,
c_i <= 1   on every i in L.
```

Then

```text
q [phi(D)-v(D)] <= sum_(i in L) (1-c_i) phi_i.       (OB)
```

Thus an overloaded internal rich face consumes uncovered poorer-player
payoff. If every poorer player is loaded once, `D` must be tight at `phi`.

## Proof

Apply the boundary-cover inequality to target `D` with upper rich load
`alpha=1+q` and outside load `beta=1`. Every member of `D` has load
`1+q`; every member of `H\D` has load one; and every member of `L` has load
at most one. All completion terms vanish except those on `L`, giving (OB).

There is an equally short face proof. Exactify `D`, choosing a core point
`x` with `x(D)=v(D)`. Summing the tight-coalition inequalities gives

```text
x(H) + q v(D) + sum_(i in L) c_i x_i
  >= phi(H) + q phi(D) + sum_(i in L) c_i phi_i.
```

Singleton normalization gives `x_i>=0`. Raise every poorer load from `c_i`
to one on the left, use efficiency, and rearrange to obtain (OB).

## Why this changes the structural picture

The theorem accepts real cover weights and an arbitrary overloaded rich
coalition. The earlier rooted-semigroup theorem is only its discrete
singleton case. If `D={d}`, the weights are integral, and the poor loads are
zero--one, then

```text
q phi_d <= payoff of the omitted poor players.
```

At a strict boundary with two poorer players and at least one of them loaded,
this is impossible. This recovers every safe-root contradiction.

The unique-richest sacrifice budget is another specialization. Put
`H=D={r}` and weight tight protector coalitions so their total rich load is
`Lambda=1+q`, with poorer loads `c_i<=1`. Then (OB) becomes exactly

```text
phi_r (Lambda-1) <= sum_i (1-c_i) phi_i,
```

the inequality that produces the sharp four/five unique-richest threshold.
Consequently the low-dimensional threshold and the higher-rank rounding
theorems are governed by one exact-face budget, rather than unrelated
arguments.

There is a precise odd-cycle specialization. Alternating around an odd trace
cycle duplicates one cycle row. If the selected columns cover every external
rich row once or twice, their full rich load is

```text
1_H + 1_D,
```

where `D` consists of the duplicated cycle row and the twice-covered external
rows. With safe nonzero zero-one poor load, (OB) becomes

```text
s_phi(D) <= payoff of the omitted poor players.
```

When the cycle spans all rich rows, `D` is a singleton and the strict payoff
boundary makes this impossible. At the first `2|4` co-singleton obstruction,
the external fourth row joins the duplicated cycle row, so `D` is a pair; in
the sharp integral family its face slack equals the omitted poor payoff.
Thus the same budget identifies the exact geometric transition from the
unrealizable three-rich triangle to the realizable four-rich co-singleton
packet.

The real-valued hypothesis matters for disconnected rank-two packets. One
may alternate the unique poor-labeled odd cycle while leaving every other
odd-cycle component at weight one half. The untouched components still load
their rows exactly once, so the complete overload footprint is the singleton
root of the labeled cycle. This rules out all rank-two underloaded packets.
It does not put the selected vector in the integer tight-coalition semigroup
when other half-weight cycles remain; the integer rooted-fibre interpretation
is strictly stronger and applies directly only in the one-cycle case.

## Next structural target

For a supported fractional exact cover, seek a real or integral rounding
whose rich overload is constant on a nonempty set `D`. Formula (OB) then
either forces `D` tight or charges its slack to a precisely identified set of
uncovered poorer players. Iterating this operation along newly forced tight
faces is a possible route to a decomposition theorem: every obstruction must
either terminate in an exact partition or exhibit a minimal cover support
with no constant-overload rounding at any internal face.

The inequality is a specialization of the paper's boundary-cover inequality,
itself a quantitative consequence of published exact balancedness. No new
characterization of exact games is claimed. The candidate new contribution
is recognizing that the same internal-face overload budget controls both the
sharp four/five threshold and the trace-hypergraph obstruction hierarchy.
