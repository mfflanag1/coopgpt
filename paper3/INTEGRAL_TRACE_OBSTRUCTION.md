# Integral-trace obstruction for slack Lmin boundaries

## Status

This note extracts a dimension-free forbidden-pattern theorem from the
balanced-trace transport proof.  It uses no finite enumeration.  The only
external combinatorial input is the classical theorem that a balanced
zero-one matrix has an integral set-partitioning polytope (Berge, 1972).
Correctness and novelty still require hostile external review.

The qualitative tight-coalition criterion for Lmin/Lmax is also prior art:
Arin, Kuipers, and Vermeulen (2008) introduced property I for Lmax, and Mauri
(2018, Lemma 3) stated its antidual Lmin form using complement-tight
coalitions. The strict richer-side cover used below is presented as an
explicit quantitative LP-dual consequence/refinement of that known
optimality structure. The candidate new content begins with the simultaneous
strict-deficit certificate and, especially, its projection to the active
trace exact-cover polytope and the integrality contradiction.

## Active rich-side trace hypergraph

Let `v` be an exact singleton-normalized TU game, let `phi=Lmin(v)`, and fix a
strict payoff boundary with cumulative poorer side `L` and richer suffix `H`.
Define the active trace hypergraph

```text
A_phi(H) = { T cap H : T is a proper phi-tight coalition,
                         T cap H is nonempty }.
```

Its fractional exact-cover polytope is

```text
Q_phi(H) = { beta >= 0 :
             sum_(R in A_phi(H)) beta_R 1_R = 1_H }.
```

The strict richer-side cover lemma makes this polytope nonempty.  It is
bounded because every trace is nonempty.  Call the boundary **trace-integral**
if every vertex of `Q_phi(H)` is integral.  An integral point of this polytope
is exactly a set partition of `H`: every positive coefficient is one and the
selected traces are pairwise disjoint.

## The theorem

> **Integral-trace obstruction.** Suppose the exact `H`-face contains a core
> point `z` for which at most one poorer player gains relative to `phi`:
>
> ```text
> z(H)=v(H),
> |{i in L : z_i>phi_i}| <= 1.
> ```
>
> If `Q_phi(H)` is integral, then `phi(H)=v(H)`.

### Proof

Assume instead that

```text
s = phi(H)-v(H) > 0,
Delta = z-phi.
```

Efficiency gives `Delta(H)=-s` and `Delta(L)=s`.  Normalize the strict
tight-coalition cover to load every member of `H` once; its load `c_i` on
every `i in L` is strictly below one.  Summing its tight inequalities at `z`
shows that not all poor displacements are nonnegative.  Since their sum is
positive and at most one is positive, there is a unique gaining player `b`
and every other poor displacement is nonpositive.

Project the strict cover to `Q_phi(H)`.  By trace integrality, decompose that
point into a convex mixture of set partitions of `H`.  Lift each partition
back to deterministic original tight coalitions by choosing, independently
for each trace, one original coalition with that trace according to its
conditional cover weight.  In every lifted partition packet, the poor load
`r_i` is a nonnegative integer: it counts selected coalitions containing `i`.
The packet's rich traces partition `H`, so its tight inequalities at `z` give

```text
-s + sum_(i in L) r_i Delta_i >= 0.
```

If `r_b=0`, the left side is at most `-s`, impossible.  Hence every packet
loads `b` at least once.  Averaging the lifted packets gives `c_b>=1`,
contradicting the strict cover inequality `c_b<1`.  Therefore `H` is tight.

## Two-poorer forbidden-pattern corollary

If `L={a,b}` and `H` were slack, exactness would supply `z` exact on `H`.
Applying the normalized strict cover to this chosen `z` forces

```text
Delta_a < 0 < Delta_b
```

after relabeling.  Thus the theorem applies automatically:

> **Every slack Lmin suffix above exactly two poorer players has a
> nonintegral active trace exact-cover polytope.**

More generally, the contrapositive of the theorem gives a sign-complexity
law: at a trace-integral slack boundary, **every** core point exact on `H` has
at least two gaining poorer coordinates, while balanced-trace transport also
forces at least one losing poorer coordinate.  Hence trace-integral slack
requires at least three poorer players, regardless of the size of `H`.

Berge's balanced-matrix theorem now gives a concrete forbidden pattern.  Let
`A` be the player-by-trace incidence matrix of `A_phi(H)`.  If `A` were a
balanced zero-one matrix, its set-partitioning polytope would be integral.
Consequently:

> **Every two-poorer slack boundary contains an odd trace cycle:** an
> odd-order square submatrix with exactly two ones in each row and each
> column.

This is a dimension-free necessary condition on the actual tight-coalition
geometry of the game, not merely on the cardinalities `(|L|,|H|)`.

There is a stronger integer-semigroup layer beyond nonintegrality. Exact
singleton faces prohibit every nonnegative integer combination of proper
tight coalitions with rich incidence `1_H+k e_d`, `k>=1`, and nonzero
zero-one poor incidence. See
[`ROOTED_SEMIGROUP_OBSTRUCTION.md`](ROOTED_SEMIGROUP_OBSTRUCTION.md) and
Theorem `thm:lx-rooted-semigroup-obstruction`. The rank-two, four-rich, and
projective-plane exclusions are three rounding routes into this same
forbidden rooted fibre.

There is a further dimension-free exclusion. If every active trace has size
at most two, every extreme exact cover is a union of singleton blocks,
isolated edges, and half-weight odd cycles. In the packet whose gaining-poor
load is below one, transport forces exactly one odd-cycle edge to carry that
poor player and no edge to carry the losing poor player. Alternating-rounding
that odd cycle duplicates one rich vertex; exactifying its singleton then
contradicts efficiency. Thus:

> **Every slack two-poorer boundary has an active trace of size at least
> three.**

The full proof is in [`RANK_TWO_TRACE_EXCLUSION.md`](RANK_TWO_TRACE_EXCLUSION.md)
and Theorem `thm:lx-rank-two-trace-exclusion` of the manuscript. Hence the
necessary obstruction is genuinely hypergraphic, not a bare graph odd cycle.

At the first feasible rich-side size, the obstruction is unique. A human
classification of the five fractional exact-cover vertex types on four
players shows that four admit a safe root rounding and are eliminated by the
same exact-singleton argument. The sole survivor is

```text
beta_(H\{h})=1/3 for every h in H.
```

Thus every slack `2|4` boundary has all four co-singletons as active traces.
See [`H4_FIRST_OBSTRUCTION_CLASSIFICATION.md`](H4_FIRST_OBSTRUCTION_CLASSIFICATION.md)
and Theorem `thm:lx-four-rich-trace-classification`.

The next canonical rank-three incidence system is also constrained by
exactness. For a projective-plane packet of order `q`, simple-point counting
and a pencil rounding rule out every poor-label pattern satisfying

```text
|B|(q+2-|B|) > binom(|A|,2).
```

In particular all such packets through order six are impossible.  A
two-sided convex Lehman-row interpolation is stronger: at a point on exactly
one gaining line, it normalizes either the gaining or the losing poor load.
This eliminates projective-plane packets in every finite order, without
assuming Desarguesian coordinates.
See
[`PROJECTIVE_PLANE_TRACE_EXCLUSION.md`](PROJECTIVE_PLANE_TRACE_EXCLUSION.md)
and Theorem `thm:lx-projective-plane-trace-exclusion`.

## How it explains the sharp threshold

- Every underloaded minimal packet at a slack two-poorer boundary contains a
  proper trace `R` with `3<=|R|<=|H|-1`.  Indeed, the full trace cannot occur
  in a nontrivial minimal balanced support. If all remaining traces had size
  at most two, alternate the unique poor-labeled odd cycle and leave all other
  components at their original weights. The real overload budget then gives
  the forbidden singleton inequality `phi_d<=phi_a`. Therefore slack is
  impossible whenever `|H|<=3`, without enumerating the three-player
  exact-cover vertices.
- For every `|H|=h>=4`, the internal-sacrifice family has all co-singleton
  traces `H\{x}` active.  The three rows indexed by distinct
  `x_1,x_2,x_3` and the three columns
  `H\{x_1},H\{x_2},H\{x_3}` contain

  ```text
  0 1 1
  1 0 1
  1 1 0,
  ```

  the smallest odd trace cycle.  More globally, assigning weight `1/(h-1)`
  to every co-singleton is a fractional exact cover of `H`.  Its support
  matrix is `J-I`, which is nonsingular, so this point is a fractional vertex
  of the full active-trace polytope, not merely a fractional convex
  combination.  Thus the
  universal sharpness family crosses exactly the integrality gate required by
  the theorem.

The `2|3` versus `2|4` threshold is therefore the first realizability
transition for a **proper rank-three trace**.  At three rich players a
rank-three trace is the full trace and cannot belong to the required
fractional minimal packet.  At four, the co-singleton triples are proper and
their odd-cycle submatrix is realizable.

## Significance and limits

This result turns the finite-looking threshold into a general hypergraph
obstruction.  It does **not** classify all nonintegral active trace
hypergraphs, nor does nonintegrality by itself guarantee realizability by an
exact game.  The proposed universal-minor strengthening is false: the exact
theorem in [`THREE_TRACE_HALF_INTEGRAL_OBSTRUCTION.md`](THREE_TRACE_HALF_INTEGRAL_OBSTRUCTION.md)
classifies the entire support-three tier.  Every such underloaded packet is a
blown-up triangle with unique cover `(1/2,1/2,1/2)`; exact singleton faces
force the two atoms adjacent to the gaining label to have size at least two,
and an exact family realizes every admissible atom triple.  Hence these
packets begin with five rich players and cannot contain the four-column
co-singleton packet under row/column deletion or contraction.  The next major
target is a classification of the multiple irreducible realizable classes.

Classical prior art retained explicitly:

- J. Arin, J. Kuipers, and A. J. Vermeulen (2008), *An axiomatic approach to
  egalitarianism in TU-games*, International Journal of Game Theory 37,
  565--580, DOI
  [`10.1007/s00182-008-0133-6`](https://doi.org/10.1007/s00182-008-0133-6).
- L. Mauri Masdeu (2018), *Essays on egalitarianism-based solution concepts
  for cooperative TU-games*, doctoral thesis, Universitat Rovira i Virgili,
  especially Lemma 3.
- C. Berge (1972), *Balanced matrices*, Mathematical Programming 2, 19--31,
  DOI [`10.1007/BF01584535`](https://doi.org/10.1007/BF01584535).
- Minimal balanced collections and the set-partitioning polytope are standard;
  the candidate new contribution is forcing their **nonintegrality** from a
  slack two-poorer Lmin boundary in an exact game.
