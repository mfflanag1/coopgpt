# Two-column Lmin obstructions: normal form and slack conservation

## The structural theorem

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and let
`H` be a proper cumulative richer suffix with positive slack

```text
s_H = phi(H)-v(H) > 0.
```

Suppose a strict tight-coalition cover of `H` has exactly two positive-support
coalitions. Then there is a partition into four nonempty blocks

```text
N = H disjoint-union X disjoint-union Y disjoint-union R
```

such that, after interchanging the two columns if necessary, the supported
coalitions are exactly

```text
A = H union X,    B = H union Y.
```

Moreover the exterior block pays for the failed exact face:

```text
0 < s_phi(H) <= s_phi(R).                             (ESB)
```

Thus every two-column failure is one oriented Boolean-lattice diamond, and
its target slack cannot exceed the slack of the exterior coalition. This is
a complete dimension-free classification of the two-column tier.

## Proof of the normal form

Let the two positive cover weights be `lambda,mu`, and let `alpha>0` be the
common load on `H`. Because `H` is slack, the laminar exact-face theorem says
the two support coalitions must cross. Write their four Venn cells as

```text
C=A intersection B, X=A setminus B, Y=B setminus A,
R=N setminus (A union B).
```

They have loads `lambda+mu, lambda, mu, 0`. The intersection `C` is nonempty.
Because `alpha` is one of these loads, `alpha<=lambda+mu`. No member of `C`
can therefore lie outside `H`, where every load is strictly smaller than
`alpha`. Hence `C` lies in and meets `H`, so `alpha=lambda+mu`. Every member
of `H` must therefore lie in both support coalitions, and every member of `C`
must lie in `H`. Consequently `C=H`, while the crossing arms `X,Y` lie outside
`H`.

## Proof of exterior-slack conservation

Exactness of `H` supplies `z` in the core with

```text
z(H)=v(H)=phi(H)-s_H.
```

Put `Delta=z-phi`. Tightness of `A` and `B` gives

```text
Delta(X)>=s_H,    Delta(Y)>=s_H.
```

Efficiency now yields

```text
Delta(R)=s_H-Delta(X)-Delta(Y)<=-s_H.
```

Core feasibility gives `z(R)>=v(R)`, or `Delta(R)>=-s_phi(R)`. Combining the
last two inequalities proves `(ESB)`. In particular, `R` is nonempty.

Equivalently, the incidence identity

```text
1_A + 1_B + 1_R - 1_H = 1_N
```

is an exact-balanced slack budget: tightness of `A,B,N` leaves precisely
`s_phi(H)<=s_phi(R)`. The local supermodularity defect is

```text
v(A)+v(B)-v(H)-v(A union B)
 = s_phi(H)+s_phi(A union B)>0.
```

## Sharp converse realization

Partition `N=C disjoint-union X disjoint-union Y disjoint-union R`, with all
four blocks nonempty. Choose levels `a>b>0`, give payoff `a` on `C` and `b`
elsewhere, and define

```text
A=C union X, B=C union Y,
K={z>=0:z(N)=phi(N), z(A)>=phi(A), z(B)>=phi(B)},
v(S)=min{z(S):z in K}.
```

The game is singleton-normalized exactly under the capacity condition

```text
|C|>=2  or  b|R|>=a.                                 (CAP)
```

Under `(CAP)`, it is exact, `Core(v)=K`, and `Lmin(v)=phi`. Its two slacks are

```text
s_phi(C)         = min{a|C|,b|R|},
s_phi(A union B) = b min{|X|,|Y|}.
```

The proof generalizes the binary construction. Outside coordinates can be
zeroed by moving their `b` units into `C`. A coordinate in `C` can be zeroed
by transferring its `a` units to another member of `C`; if `C` is a
singleton, zeroing it requires net additions of `a` to each arm and therefore
a withdrawal of `a` from `R`, possible exactly when `b|R|>=a`. Conversely,
the same aggregate inequalities show this capacity is necessary.

For Lmin, if every coordinate is at least `b`, subtracting `b 1_N` turns the
two tight inequalities into

```text
w(C)+w(X)>=(a-b)|C|,  w(C)+w(Y)>=(a-b)|C|,
```

while efficiency fixes `w(N)=(a-b)|C|`. Hence `w` vanishes outside `C`; the
remaining total on `C` is uniquely max-min equalized at `a` per player.
Aggregate minimization gives the displayed slack formulas.

## The four/five threshold

Four players force one player in each Venn cell. Normalization makes their
slacks equal to their Lmin payoffs, so `(ESB)` would say that the richer
member of `C` receives no more than the poorer member of `R`, a contradiction.
At five players, putting the extra player in `X` or `Y` leaves the same two
singletons and contradiction. The only possible extra capacity is therefore
a second player in `C` or a second player in `R`:

```text
(|C|,|X|,|Y|,|R|)=(2,1,1,1) or (1,1,1,2).
```

Thus the threshold is not merely a count of Venn cells. It is a sharp
slack-financing law: crossing consumes three cells, exact balancedness
requires an exterior cell, and singleton exactness requires one additional
unit of target or exterior capacity.

## Scope and next tier

This theorem classifies every failure whose strict cover has support two. It
does not claim that arbitrary failures reduce to this tier. Indeed, the
three-column half-integral family is a genuinely different minimal balanced
packet. Together, the two results begin a support-size classification of Lmin
obstructions. The next major question is whether support-minimal packets of
arbitrary size admit a finite collection of slack-conservation normal forms
or exhibit unbounded new circuit types.

## Reproduction

```bash
PYTHONPATH=src python src/verify_two_column_lmin_obstruction.py \
  --output results/two_column_lmin_obstruction.json
```

The verifier checks thousands of abstract two-column load patterns, the
saturated exterior budget in the sharp five-player game, and generalized
two-level realizations over an exact-rational grid with independent generic
Lmin replay through six players. It is an audit, not a proof dependency.

## Novelty calibration

Exact balancedness, lower-envelope exact games, and minimal balanced
collections are prior art. The candidate contribution is the Lmin-specific
two-column normal form, its exterior-slack conservation inequality, and the
sharp converse capacity theorem. A specialist must still determine whether
this package is implicit in existing exact-balanced or tight-set literature.
