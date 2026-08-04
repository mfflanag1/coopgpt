# The uncrossing-defect budget for exact core faces

## Theorem

Let `v` be an exact game, let `phi` be any core allocation, and fix a proper
nonempty coalition `H`.  Suppose an integer multiset of proper coalitions
tight at `phi` has common load `k>0` on every player of `H` and load at most
`k-1` on every player outside `H`.

Repeatedly choose two crossing coalitions `A_t,B_t` of positive multiplicity,
put `delta_t=min(lambda_A,lambda_B)`, and replace that multiplicity by their
intersection and union.  Discard empty sets.  Stop when the positive support
is laminar.  The process terminates because the integer energy

```text
sum_S lambda_S |S|(n-|S|)
```

strictly decreases at every step.

For each `h in H`, take a minimal final supported set containing `h`, and let
`P` be the inclusion-maximal distinct sets obtained this way.  Then `P`
partitions `H`.  If `mu` is the final multiplicity vector and

```text
m = min{mu_B:B in P},
D_phi(A,B)=v(A)+v(B)-v(A intersection B)-v(A union B),
```

then

```text
0 <= m s_phi(H)
   <= sum_S mu_S s_phi(S)
    = sum_t delta_t D_phi(A_t,B_t).                 (UDB)
```

This is a dimension-free quantitative conservation law.  It applies to any
core point of any exact game; Lmin and normalization are not required once
the cover is supplied.

## Proof

The incidence identity

```text
1_A+1_B=1_(A intersection B)+1_(A union B)
```

preserves all player loads.  The energy drop is

```text
2 delta |A setminus B| |B setminus A|,
```

a positive integer, so the procedure terminates.

The final support is laminar.  Let `M_h` be a minimal supported set containing
`h in H`.  If `M_h` contained an outside player `i`, every supported set
containing `h` would also contain `i`, by laminarity and minimality.  The final
load of `i` would be at least the load `k` of `h`, contradicting its load at
most `k-1`.  Thus every `M_h` lies in `H`.  Their maximal distinct members are
disjoint and cover `H`, giving the partition `P`.

Write `s(S)=phi(S)-v(S)`.  It is nonnegative because `phi` is in the core.
Initially the weighted slack is zero because every cover member is tight.
One uncrossing changes weighted slack by

```text
delta [s(A intersection B)+s(A union B)-s(A)-s(B)]
 = delta D_phi(A,B),
```

using modularity of `phi`.  Telescoping gives the equality in `(UDB)`.

Every block of `P` occurs with multiplicity at least `m`, so final weighted
slack is at least `m sum_(B in P)s(B)`.  Exactness implies

```text
v(H) >= sum_(B in P) v(B),
```

by the exact-balanced vector with `+1` on the partition blocks, `-1` on `H`,
and `+1` on `N`.  Hence `s(H)<=sum_(B in P)s(B)`, proving the inequalities.

## Consequences

1. Any slack target face requires strictly positive cumulative uncrossing
   defect, not merely one qualitative crossing.
2. If a cover can be completely uncrossed through zero-defect pairs, the
   target is tight.  The local-supermodularity theorem is the special case in
   which every intermediate derived set stays tight, so every step has zero
   defect.
3. The theorem applies automatically at every strict Lmin payoff boundary:
   its strict cover polyhedron is rational, so a rational cover can be chosen
   and scaled to integer multiplicities.
4. The right side is a conserved total along the chosen uncrossing path: it
   equals the final weighted slack exactly, even though individual step
   defects after the first step may have either sign.

For the sharp five-player cover, one uncrossing has defect two, the final
partition multiplicity is one, and the target slack is one.  For the
three-column seven-player obstruction, two uncrossings have signed defects
`3` and `3/2`, while the target slack remains one.

## Reproduction

```bash
python src/verify_uncrossing_defect_budget.py \
  --output results/uncrossing_defect_budget.json
```

The audit independently executes the integer uncrossing algorithm on the
five-player and three-column obstruction families and verifies every equality
in `(UDB)` using exact rational arithmetic.  It is not a proof dependency.

## Novelty calibration

Set-family uncrossing, exact-game superadditivity, and exact-balancedness are
prior art.  The candidate contribution is the quantitative bridge: cumulative
local supermodularity defects exactly conserve weighted core slack and bound
the slack of the target exact face.  This requires specialist review.
