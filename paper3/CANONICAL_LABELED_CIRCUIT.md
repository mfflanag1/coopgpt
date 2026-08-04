# Canonical labeled-cover circuit

## Result

At every slack cumulative richer suffix above exactly two poorer players,
balanced-trace transport supplies a lifted extreme packet with gaining-poor
load below one. Append the poorer-player incidence rows and singleton dummy
columns for the two poor players. Filling each dummy with the uncovered poor
load extends the packet to an exact cover of all rows.

This extended point is not merely a witness that the augmented exact-cover
polytope is nonintegral. It is a **fractional vertex on the original player
rows**, and its support plus the all-ones right-hand side is a linear circuit.
The same packet gives a circuit in each of the two one-label augmentations.

## Proof

Let `M_S` be the rich trace-incidence matrix on the positive traces of the
chosen packet, and let `beta>0` be its normalized balancing vector:

```text
M_S beta = 1_H.
```

The packet comes from an extreme point of the rich exact-cover polytope, so
its traces form a minimal balanced collection. Consequently the columns of
`M_S` are linearly independent. Otherwise a nonzero kernel direction would
allow sufficiently small perturbations of `beta` in both signs, contradicting
extremality and uniqueness of the normalized balancing weights.

Lifting a trace to an original tight coalition only adds poor coordinates;
restriction back to the rich rows is still `M_S`. Hence the lifted full
columns remain independent. The two dummy columns vanish on every rich row,
so adjoining them also preserves independence. The vector

```text
(beta, 1-r_a, 1-r_b)
```

is feasible for the all-ones right-hand side. Transport gives

```text
0 <= -sigma + r_a Delta_a + r_b Delta_b,
Delta_a < 0 < Delta_b,
r_b < 1.
```

It follows first that `r_a<r_b`, and then that `r_b>0`. Thus both dummy
weights are positive and the gaining dummy weight lies strictly between zero
and one. The feasible point is therefore fractional. Independence of its
positive columns makes it a vertex.

Finally, the all-ones right-hand side has a unique expansion in those
independent columns, and every coefficient in that expansion is positive.
Adjoining the right-hand-side column therefore creates a minimally dependent
set: deleting any support column destroys this representation. This is the
claimed labeled-cover circuit.

The same argument after retaining only row `a` and dummy `e_a`, or only row
`b` and dummy `e_b`, gives the two one-label circuits. In the `a`-only case,
fractionality of the original packet follows because an integral rich
partition would have integer `b`-load at least one, contradicting `r_b<1`.

## What this resolves

The obstruction no longer needs an arbitrary minimally-nonideal reduction in
order to become irreducible. It is already support-minimal in a precise
linear-algebraic sense on the rows that retain the game-theoretic meaning:
the original rich players and one or both poor labels. This avoids the row
and denominator losses found in the parallelization audit.

## What it does not resolve

A linear circuit is not automatically a minimally nonideal clutter, a facet
of a covering polyhedron, or a deletion/contraction-minimal obstruction.
The result therefore does not prove that every failure contains a positive
Lehman pair, nor does it classify these circuits in arbitrary dimension.
Its value is to replace the noncanonical MNI target with an unconditional,
original-row object whose structure can now be classified directly.
