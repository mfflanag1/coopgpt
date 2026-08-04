# Odd-cycle overload footprint

## Structural lemma

Let a family of proper tight coalitions restrict on rich rows `R` to an odd
cycle incidence matrix. Select an alternating near-perfect cover of that
cycle. It covers every row of `R` once except one duplicated row `d`.

Assume each rich row outside `R` is covered once or twice by the same selected
columns. Define the **overload footprint**

```text
F = {d} union {external rich rows covered twice}.
```

Then the complete rich load is `1_H + 1_F`. If the two poor loads are
zero-one and nonzero, the exact-face overload budget gives

```text
s_phi(F) <= sum of the payoffs of omitted poor players.
```

Thus loading both poor players forces `F` to be tight. Loading only one poor
player requires the omitted player to pay for the entire face slack of `F`.

The weights outside the alternated cycle need not be integral. In a
rank-two extreme packet with several disjoint odd cycles, keep every other
cycle at its original half weights. Those components still cover their rich
rows exactly once and, after transport identifies the unique poor-labeled
edge, carry no poor player. Alternating only the labeled cycle therefore has
footprint `F={d}` and full real load `1_H+e_d+e_b`. The overload budget gives
`phi_d<=phi_a`, impossible at a strict boundary. This proves the
dimension-free rank-two exclusion, but it is not an integer semigroup-fibre
argument unless there is only one odd cycle.

## Why three and four rich players differ

If the odd cycle spans all rich rows, there are no external rows and
`F={d}`. Singleton normalization gives `s_phi(F)=phi_d`, which is strictly
larger than either poor payoff. The rounding is impossible. This is the
budget form of the three-rich triangle exclusion.

With four rich players, a three-row odd cycle can leave one external rich
row. In the co-singleton packet, every alternating pair covers that external
row twice, so the footprint has two players rather than one. The sharp
integral family realizes this possibility exactly. At `h=4`, write

```text
H = {r1,r2,k1,k2}.
```

Select the poor-free coalition with trace `H\{r1}` and the `p1`-carrying
coalition with trace `H\{k1}`. Their full rich load is

```text
1_H + 1_{ {r2,k2} },
```

their poor load is `e_p1`, and direct substitution in the generator family
gives

```text
s_phi({r2,k2}) = phi_p2.
```

The overload budget is attained at equality. The fourth rich player is not
merely an extra coordinate: it creates the first nonsingleton internal face
capable of absorbing the unavoidable odd-cycle rounding excess.

## Scope

This lemma does not show that every higher-dimensional circuit has an
alternating selection whose external loads are all one or two, nor that its
poor labels are safe. Those are the remaining combinatorial selection
problems. It does isolate exactly what any successful selection must pay and
turns the low-dimensional threshold into a face-slack transition rather than
an enumeration artifact.
