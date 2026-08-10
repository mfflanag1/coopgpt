# Finite facet rays for the all-anchor witness projection

Date: 2026-08-10

## 1. Result

Fix blocker requirements `j in J`, coalitions `C_j`, and lower bounds `r_j`.
For player `k`, let `a^k in {0,1}^J` be the incidence column
`a^k_j=1[k in C_j]`.  A zero-anchor witness at `i` exists precisely when

```text
q>=0, q(N)=1, q_i=0, and q(C_j)>=r_j for every j.       (F1)
```

The support-function formulation in `S6_ZERO_ANCHOR_OVERCOVER_DUALITY.md`
says that (F1) is equivalent to

```text
lambda.r <= max_{k != i} lambda.a^k for every lambda>=0. (F2)
```

Condition (F2) looks infinite.  It has the following exact finite reduction.

**Finite-ray theorem.**  Fix the anchor `i`.  For each `k!=i`, define

```text
K(i,k)={lambda>=0:
        lambda.(a^k-a^l)>=0 for every l not in {i,k}}.   (F3)
```

It is enough to impose

```text
lambda.r <= lambda.a^k                                 (F4)
```

on the extreme rays of the finitely many cones `K(i,k)`.  Every such ray is
rational and has at most `n-1` nonzero coordinates.  Hence at six players all
witness-side facets use at most five blocker requirements.  Applying the same
finite list for all six anchors is equivalent to the all-anchor
second-largest-load condition; no witness coupling is added or lost.

## 2. Proof

The nonnegative orthant is the union of the cones `K(i,k)`: for a given
`lambda`, choose any non-anchor incidence column attaining the maximum in
(F2).  On `K(i,k)` that maximum is the linear form `lambda.a^k`.  A linear
inequality holds on a pointed polyhedral cone if and only if it holds on every
extreme ray, proving the finite reduction.

For the support bound, let an extreme ray have `s` positive coordinates.
The other `|J|-s` coordinate hyperplanes are active.  To cut the remaining
`s`-dimensional coordinate face down to a ray requires `s-1` independent
active comparison hyperplanes.  But (F3) has only `n-2` comparison
inequalities.  Therefore `s-1<=n-2`, or `s<=n-1`.  Since the incidence matrix
is integral, every extreme ray can be normalized to a primitive integer
vector.

The bound is sharp.  At `n=6`, take anchor `5`, proposed maximizer `0`, and
the five coalitions

```text
0234, 0134, 0124, 0123, 1234.
```

Against players `1,2,3,4`, their four comparison rows are the four unit
vectors followed by a common `-1` column.  Their unique positive null ray is
`(1,1,1,1,1)`, which has support five.

## 3. Mathematical meaning

This strengthens the earlier Helly statement in three ways.

1. It gives the complete finite inequality system, not only a bound on a
   minimal infeasible subfamily.
2. It is constructive: enumerate anchor/maximizer pairs, enumerate active
   comparison sets, and retain the primitive positive null rays.
3. It explains the sparse class-5/class-6 over-covers before inspecting any
   relay tree.  At six players a witness obstruction can always be expressed
   with at most five blocker requirements because there are only four rival
   non-anchor columns.

This is an exact polyhedral theorem for the witness projection, not a proof
of the global blocker transversal.  The opposite-selection signs and the
question of which blocker is forced at each relay node remain separate.  It
also is not presented as a novelty claim: it is an elementary consequence of
polyhedral cone decomposition and active-constraint counting.

## 4. Exact audit

The verifier uses rational row reduction only.  It imports no solver,
optimizer, production encoder, or frozen relay map.  It enumerates every
extreme ray for three representative menus, checks the maximizing-cone
conditions and the `n-1` support bound, and detects the sharp support-five
circuit above.

```bash
python3 coopgames/verifiers/s6/verify_zero_anchor_facet_rays.py \
  --output /tmp/zero_anchor_facet_rays.json
cmp /tmp/zero_anchor_facet_rays.json \
  coopgames/verifiers/s6/zero_anchor_facet_rays.json
```
