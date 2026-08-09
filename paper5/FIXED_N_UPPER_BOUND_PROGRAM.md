# Fixed-n upper-bound and family-handover program

Date: 2026-08-09

This note records a human reduction of the fixed-dimension divergence problem,
a sharp explanation of the two known extremal-family regimes, and one failed
strengthening detected before it became a conjecture.  Nothing below upgrades
the open statement `s(n)=s_2(n)` to a theorem.

## 1. The right invariant is cross-selection overlap

Let

```text
x = Lmin(v),    z = Lmax(v),    T = v(N) > 0,
O(x,z) = sum_i min(x_i,z_i).
```

Because `x,z>=0` and `x(N)=z(N)=T`, one has the exact identity

```text
||x-z||_1 = 2(T-O(x,z)).                                  (1)
```

Equivalently, if `A={i:x_i>z_i}`, then

```text
D := x(A)-z(A) = z(N\A)-x(N\A) = T-O(x,z),
rho(v)=2D/T.                                               (2)
```

There is a second useful form.  Choosing independently at each coordinate
which of `x_i,z_i` is smaller gives

```text
O(x,z) = min_{S subseteq N} [x(S)+z(N\S)].                 (3)
```

Thus the candidate sharp fixed-n theorem

```text
s(n) <= 2 - 8n/(n^2-(n mod 2)),       n>=6               (UB_n)
```

is *exactly equivalent* to the hybrid-cut inequality

```text
Lmin(v)(S)+Lmax(v)(N\S)
    >= n T / floor(n^2/4)       for every S subseteq N.    (H_n)
```

It is enough to prove `(H_n)` for the comparison cut
`S={i:Lmin_i<=Lmax_i}`, but the all-cuts statement is the clean invariant.
The master family `G(p,k)` has

```text
O/T = n/[k(p+1)],       n=k+(p+1),                         (4)
```

so the balanced choice `{k,p+1}={floor(n/2),ceil(n/2)}`
attains equality in `(H_n)`.  This explains the otherwise opaque denominator
`floor(n^2/4)`: it is the largest product of the two carrier-block sizes.

The fixed-n problem should therefore be attacked as a lower bound on a
*hybrid overlap*, not as separate estimates on the leximin floor and leximax
ceiling.  Bounds linear in the floor and majorization of a generator have
already failed, whereas `(H_n)` is exactly sharp on the surviving family.

### Null-player reduction

There is one useful induction step.  If the leximin floor is zero, the game
has a null player.  Indeed, if every player received a positive payoff at
some core point, averaging those finitely many core points would produce one
core point positive in every coordinate, contradicting a zero max-min level.
Thus some player is zero throughout the core.  Exactness then gives
`v(S)=v(S\{i})` for every coalition, so deleting that player preserves
exactness, `Lmin`, `Lmax`, `T`, and `rho` on the remaining coordinates.

Consequently a minimal-dimensional counterexample to an inductive fixed-n
bound has strictly positive leximin floor.  In particular, the proven
`s(5)=1/2` excludes every null-player six-player counterexample to
`s(6)<=2/3`.  This does not prove the six-player bound, but it removes the
degenerate boundary of the exact cone from the live case.

## 2. A tempting stronger cut-size statement is false

Let `p=#{i:x_i>z_i}` and let `t=#{i:x_i=z_i}`.  Assigning tied coordinates to
either side, define

```text
P(x,z)=max { a(n-a) : p<=a<=p+t }.
```

The master family suggests the stronger inequality

```text
O/T >= n/P(x,z).                                          (CUT)
```

It would imply `(H_n)` because `P(x,z)<=floor(n^2/4)`.  It is false already
at `n=6`.  The exact game archived in
`verifiers/s6/harvest6_601.json`, record 125, has

```text
T=4,
x=(4/3,1/3,1/3,1/3,4/3,1/3),
z=(1,1,0,0,1,1),
O/T=2/3,
p=4, t=0, P=8,
n/P=3/4.
```

So this game attains the candidate global `n=6` bound but violates `(CUT)`.
The comparison cut need not be balanced at equality.  This is mathematically
useful: any proof of `(H_n)` that tries to recover the denominator from the
cardinality of the sign cut is blocked.

The audit script

```text
verifiers/divergence/audit_overlap_bound.py
```

found no violation of `(H_6)` in 375 archived exact six-player pairs, while
finding three violations of `(CUT)`.  This is a bug audit, not proof evidence.

## 3. The family handover is an exact crossover theorem

Two human families now coexist.

The starved family `C_n` has

```text
rho_C(n)=(n-4)/(n-3),
O_C(n)/T=(n-2)/(2(n-3)).                                  (5)
```

Its `Lmax` support has the fixed size four; the remaining `n-4` players are
zero.  Its overlap therefore tends to `T/2` and its ratio tends to `1`.

The balanced member of `G(p,k)` has

```text
rho_G(n)=2-2n/floor(n^2/4),
O_G(n)/T=n/floor(n^2/4).                                  (6)
```

Both carrier blocks grow with `n`, so the overlap tends to zero and the ratio
tends to `2`.

### Theorem (family handover)

Among these two families:

```text
n=5:  rho_C=1/2  > rho_G=1/3;
n=6:  rho_C=rho_G=2/3;
n>=7: rho_G>rho_C.
```

### Proof

The first two lines are substitution.  For even `n=2k`, `k>=3`, subtract the
overlaps in (5)--(6):

```text
O_C/T-O_G/T = (k-2)(k-3)/[k(2k-3)].
```

This is zero at `k=3` (`n=6`) and positive for `k>=4`.  For odd
`n=2k+1`, put

```text
Q(k)=2k^3-7k^2+3k+4.
```

Then

```text
O_C/T-O_G/T = Q(k)/[4k(k+1)(k-1)].
```

At `k=2` (`n=5`) the numerator is `-2`.  At `k=3` it is `4`, and
`Q'(k)=6k^2-14k+3>0` for every `k>=3`; hence it stays positive from `n=7`
on.  Smaller overlap means larger `rho` by (1).  QED.

This is more than a numerical crossing.  The starved mechanism uses a fixed
four-player ceiling carrier, so adding players only enlarges its zero set.
The `G` mechanism splits the carrier into two growing blocks and minimizes
their overlap by maximizing their product.  Six players are the unique
coexistence point: the archive contains both a `4|2` comparison-cut equality
game (the starved family) and `3|3` equality games (the `G` family).  Thus no
unique extremal sign pattern should be expected even if `(UB_6)` is true.

## 4. Concrete proof target

The live general theorem is now the following single statement.

> **Hybrid overlap conjecture.**  For every singleton-normalized exact game
> on `n>=6` players and every coalition `S`,
> `Lmin(S)+Lmax(N\S) >= n v(N)/floor(n^2/4)`.

The all-cuts form may be stronger than necessary.  A first defensible target
is the comparison-cut form obtained by taking
`S={i:Lmin_i<=Lmax_i}`.  The following routes are already excluded:

1. deriving the denominator from the size of that comparison cut (`(CUT)` is
   false);
2. making a generator uniform by majorization (the ratio is non-monotone);
3. bounding the gap by a dimension coefficient times the leximin floor (the
   `G` family refutes such bounds from `n=9`).

A successful proof must instead use exactness to couple the two different
lexicographic normal systems.  The missing Lmax object has now been
constructed in `LMAX_OVERCOVER_COUPLING.md`: a dispersion-optimal top
over-cover has a linear-size tight-coalition representation and yields a
dimension-free spectral lower bound for the hybrid overlap.  That bound is
sharp on all archived six-player equality cases and, together with null-player
deletion, certifies the full archived six-player bank.

The remaining bridge is no longer existence or sparsity.  It is a
**strengthened two-packet inequality**: retain the individual
tight-coalition inequalities from the Lmax over-cover and the full Lmin packet
simultaneously, rather than only their weighted spectral aggregates, and prove
that their joint incidence geometry forces `(H_6)`.  The audit in
`TWO_PACKET_EXACTIFICATION_BOUNDARY.md` proves that replacing the full Lmin
packet by its aggregate first-stage under-cover is insufficient: an abstract
pair then reaches overlap `1/2`, and only the missing staged Lmin information
repairs it under singleton exactification.  A finite-support route remains
available because the full certificates have linear support.

There is now also an exact computational route that retains the full staged
information without 62 coalition-attainment witnesses.  The core-closure lemma
in `CORE_CLOSURE_REDUCTION.md` shows that six singleton-attaining core points
are enough: closing the resulting core exactifies every coalition while
preserving the core and both selections.  Initial hard-case timings improve
from 600-second unknowns to subsecond UNSAT verdicts.  A complete census is
still required, and solver verdicts must ultimately be converted into human
inequalities or independently checkable rational certificates.

The first complete run of that route is recorded in
`S6_GENERATOR_CENSUS_CHECKPOINT.md`: all 3,350 hand-net survivors have decisive
strict-failure verdicts, with `0 SAT / 3350 UNSAT / 0 UNKNOWN`.  This closes the
configuration census at the solver-evidence level.  It does not remove the
stated certificate or external-review requirements.

`S6_EQUALITY_CLASSIFICATION.md` now completes the equality census at the same
evidence level.  Exactly two support types survive, their normalized payoff
pairs are rigid, and both have dispersion exactly `1/3`.  Exact reconstructed
games and checked CPC proofs cover rigidity and the two anchor negations within
those types.  A first-crossing argument localizes any hypothetical outward
counterexample direction at one of these two profiles.  The remaining human
target is therefore a tangent/normal-cone barrier at the two equality
profiles, not another archive search.

Both coarse equality types now have human barriers.  For the starved `(4,2)`
by `(2,4)` profile, the direction `(0,0,1,1,-1,-1)` is feasible at every
Lmin-tight coalition whenever the distance would exceed `2/3`.  For the
positive `(5,1)` by `(2,4)` profile, an eight-direction Lmax exchange lemma
forces the rich-cell gap identity `w=2v`; three then-forced common tight
triples and a zero-coordinate exactness witness give `v<=1/9`.  Both arguments
also force the canonical payoff pair at equality.

This removes the last coarse-profile barrier, but it does not by itself prove
the global six-player theorem.  At a first crossing, several equal payoff
blocks may split simultaneously.  The new live target is therefore the
**refined tangent theorem**: show that every outward exact-game direction at
either canonical pair descends to one of the coarse exchange directions, or
extend the exchange-menu argument uniformly to all contiguous refinements.
