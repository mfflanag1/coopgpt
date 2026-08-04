# A laminar domain theorem for exact partition at Lmin

## Exact-face boundary theorem

Let `v` be any exact game, let `phi` be any core allocation, and let `H` be
proper and nonempty.  Suppose there are nonnegative weights on proper
coalitions tight at `phi` whose positive support is laminar, whose incidence
load is a common `alpha>0` on every player of `H`, and whose load is strictly
below `alpha` on every player outside `H`.  Then `H` is tight at `phi`.

Consequently, for singleton-normalized exact games, if such a laminar strict
richer-side cover exists at every Lmin payoff boundary, the game is exact
partition witnessed at Lmin.  In particular, this holds whenever the
complete family of proper coalitions tight at Lmin is laminar, because Lmin
optimality supplies the required strict covers.

The exact-face theorem needs neither normalization nor Lmin.  Its Lmin
corollary is dimension-free and boundary-local: the full tight family need
not be laminar if one suitable laminar cover can be selected at each boundary.

## Proof

Discard the zero-weight coalitions and call the remaining laminar support
`F`.  For each `h in H`, choose an inclusion-minimal member `M_h` of `F`
containing `h`.  Such a member exists because the load of `h` is positive.

We claim that `M_h` is contained in `H`.  If it contained a poorer player
`i`, every supported coalition containing `h` would also contain `i`.
Indeed, such a coalition intersects `M_h`, so laminarity makes the two sets
nested; minimality of `M_h` among supported sets containing `h` rules out a
strict supported subset.  Therefore the load of `i` would be at least the
load of `h`, contradicting `c_i<alpha=c_h`.  Hence `M_h subseteq H`.

Take the inclusion-maximal distinct sets among `{M_h:h in H}`.  They cover
`H`, and laminarity plus maximality makes them pairwise disjoint.  Thus they
form a set partition `P` of `H` by coalitions tight at `phi`.

If `P={H}`, the conclusion is immediate.  Otherwise exactness closes the
argument.  The coefficients

```text
+1 on every B in P,  -1 on H,  +1 on N
```

form an exact-balanced vector: their incidence sum is `1_N`, with `H` the
only negatively weighted coalition.  Exact balancedness gives

```text
sum_(B in P) v(B) - v(H) + v(N) <= v(N).
```

Because every block is tight and the blocks partition `H`, the left sum is
`phi(H)`.  Hence `phi(H)<=v(H)`.  Core feasibility gives the reverse
inequality, so `v(H)=phi(H)`.

The strict richer-side cover used in the hypothesis exists without the
laminar restriction at every Lmin boundary by the published
egalitarian-core optimality structure.  The new content is that laminarity
turns that fractional cover into an internal tight partition and exactness
then forces suffix tightness.

## Why the hypothesis is substantive

The sharp five-player failure does not satisfy it: its two positive
protector coalitions cross in their richer pair.  More generally, every
slack boundary must force crossing in the support of every strict richer-side
cover.  This gives a new structural obstruction stronger than merely saying
that a particular trace-cover vertex is fractional.

The theorem should be presented as a candidate new domain result pending a
specialist literature review.  Laminar core systems and exact-balancedness
are established subjects; novelty is claimed only for this Lmin-boundary
combination.

## Finite audit

From `coopgames/` run:

```bash
python src/verify_laminar_lmin_domain.py \
  --output results/laminar_lmin_domain.json
```

The script exhausts small laminar supports and positive integer weights,
reconstructs the top-load set, and verifies the partition extraction.  It
also checks that the known crossing five-player support falls outside the
hypothesis.  This audit is not a proof dependency.
