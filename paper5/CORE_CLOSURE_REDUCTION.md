# Core-closure reduction for the six-player decision problem

Date: 2026-08-09

This note removes the principal computational bottleneck in the existing full
staged encoding of the six-player overlap conjecture.  It is an exact logical
reduction, not a relaxation and not archive evidence.

The old encoding represented exactness literally: for each of the 62 nonempty
proper coalitions `S`, it introduced a separate core allocation attaining
`v(S)`.  For a question depending only on the core and its Lmin/Lmax selections,
those 62 witnesses are unnecessary.  Six singleton witnesses suffice.

No novelty claim is made for the closure operation itself.  The new project
contribution is its use to quotient the full-staged decision encoding by
core-equivalence.

## 1. Exact closure preserves the core

Let `u` be any six-player game whose core `C=Core(u)` is nonempty and compact.
Define its core closure by

```text
cl_C(S) = min { y(S) : y in C }                         (CC)
```

for every coalition `S`.

### Lemma (core-equivalent exactification)

The game `cl_C` is exact and

```text
Core(cl_C) = C.                                         (CE)
```

Consequently every selection determined only by the core is preserved,
including Lmin and Lmax.

### Proof

Every `y in C` satisfies `y(S)>=cl_C(S)` by definition, so
`C` is contained in `Core(cl_C)`.  Conversely `cl_C(S)>=u(S)` for every
coalition, hence every allocation satisfying the closed inequalities also
satisfies the original inequalities.  Thus `Core(cl_C)` is contained in `C`,
proving (CE).

Compactness makes every minimum in (CC) attainable by a point of `C`.
Therefore every coalition is tight at some point of `Core(cl_C)=C`, which is
exactness.  QED.

In the normalized total-one encoding, `u({i})=0` gives `y_i>=0` throughout
the core.  These inequalities and efficiency put the core inside the unit
simplex, so nonemptiness already implies compactness.

## 2. Only singleton attainment must be imposed

Suppose the encoding also contains, for every player `i`, a core point `w^i`
with

```text
w^i_i = 0.                                               (SN)
```

Then

```text
cl_C({i}) = min { y_i:y in C } = 0,
```

so the closed game is singleton-normalized.  Thus an existential search for a
singleton-normalized exact game can use:

1. one system of coalition lower bounds defining a nonempty core;
2. the proposed Lmin and Lmax points in that core;
3. six witnesses (SN); and
4. the full staged optimality certificates for Lmin and Lmax.

It need not include an attaining witness for any other coalition.

The reduction also preserves the tight coalitions used by staged certificates.
If a certificate has positive weight on `S`, the encoding requires
`x(S)=u(S)` at its proposed selection `x`.  Since

```text
u(S) <= cl_C(S) <= x(S),
```

all three quantities are equal.  Hence every complementary-slackness support
used in the model remains tight after closure.

## 3. An `n+2`-generator exact normal form

There is a stronger, finite version of the reduction.  Let the encoded points
be Lmin `x`, Lmax `z`, and the `n` singleton witnesses `w^i`.  Define

```text
v_G(S) = min { x(S), z(S), w^1(S), ..., w^n(S) }.          (FG)
```

### Theorem (certificate-preserving finite exactification)

If the encoded staged certificates prove that `x` and `z` are respectively
Lmin and Lmax for the provisional core, then the lower-envelope game `v_G` is
singleton-normalized and exact, and has the same selections `x,z`.

### Proof

Every displayed generator is in the provisional core, so `v_G(S)>=u(S)` for
every coalition.  Every generator is in `Core(v_G)` directly from (FG), and
each coalition value is attained by a generator; hence `v_G` is exact.  For
each player `i`, witness `w^i` has coordinate zero while all generators have
nonnegative coordinates, so `v_G({i})=0`.

The new core may be smaller than the provisional core, but it still contains
`x` and `z`.  Every coalition carrying positive weight in a staged certificate
was tight at the relevant selection for `u`.  For such a coalition `S`,

```text
u(S) <= v_G(S) <= x(S) = u(S)
```

on the Lmin side, and analogously at `z`; hence it remains tight.  The same
dual certificates therefore prove every lexicographic stage over the new core.
Thus `Lmin(v_G)=x` and `Lmax(v_G)=z`.  QED.

Consequently, if a counterexample exists on `n` players, one exists as a lower
envelope of at most `n+2` common-total nonnegative allocations.  For `n=6`, an
eight-generator rational game is a complete output format.  This normal form
does not assert that all eight generators are necessary.

### Corollary (extremal-domain reduction)

For every fixed `n`, the supremum of any objective depending only on
`(Lmin,Lmax)` over singleton-normalized exact games is unchanged if the domain
is restricted to lower envelopes of at most `n+2` common-total nonnegative
allocations whose coordinatewise zero sets cover `N`.

One inequality is immediate because finite lower-envelope games form a
subclass of exact games.  For the reverse inequality, apply the theorem to an
arbitrary exact game and its two selected points; the resulting finite game has
the identical ordered pair `(Lmin,Lmax)`.  In particular, the extremal
divergence problem defining `s(n)` has this finite-generator normal form.

This reduces the representation class, not the continuous dimension of the
optimization, and by itself gives neither attainment nor a closed-form value
of `s(n)`.

## 4. Logical scope of verdicts

The reduced encoding is equivalent to the original full-exactness encoding for
the counterexample decision problem.

- Every singleton-normalized exact game is feasible for the reduced encoding:
  use the game itself and its singleton-attaining core points.
- Every reduced SAT model yields, by (FG), a singleton-normalized exact game
  with the same Lmin, Lmax, and overlap (its core may be a certified subcore of
  the provisional one).

Therefore an `UNSAT` result excludes the specified Lmin-stratum,
Lmax-stratum, and incidence-table configuration without an additional
realizability assumption.  A `SAT` result is a valid existence result in
principle, but the project convention remains stricter: materialize (FG) in
exact rationals and independently recompute Lmin and Lmax before reporting a
counterexample.

## 5. Initial performance audit

The implementation has two equivalent forms in

```text
verifiers/s6/core_closure_pipeline.py
```

`pipeline2_core_closure` retains provisional worth variables but only six
singleton witnesses.  `pipeline2_generator_normal_form` applies the finite
exactification theorem completely and removes the worth variables.  A
coalition is eligible to support an Lmin staged dual only if every other
displayed generator has at least the Lmin coalition sum; the Lmax condition is
the mirror image.  These are exactly the tightness conditions for the finite
lower envelope.

with a checkpointed census driver in

```text
verifiers/s6/run_core_closure_census.py.
```

On four configurations recorded as 600-second unknowns for the prior encoding,
the reduced encoding returned exact `UNSAT` in respectively approximately

```text
0.82 s, 0.65 s, 0.54 s, 0.17 s.
```

On ten initial survivor configurations, it agreed with every verdict the old
encoding resolved under a five-second control cap and converted all five old
timeouts to `UNSAT`.  On five configurations realized by archived exact games,
both encodings returned `SAT` when asked for the nonfailure side of the overlap
inequality.

The first 100 hand-net survivor configurations all returned `UNSAT`, with no
timeouts under a 30-second cap and a maximum solve time of 13.43 seconds.
These timings and partial counts are engineering evidence only.  They do not
prove the six-player theorem; a complete configuration census, independently
checkable UNSAT evidence, equality analysis, and external review remain
necessary.

The first capped closure sweep isolated a small collection of five-level
timeout types.  The direct generator-normal-form encoding resolved every one
of the first seven such controls as exact `UNSAT` in 5--24 seconds under
concurrent load.  This is still a performance result, not a completed census.

## 6. Mathematical next step

The closure lemma changes the best route to the theorem.  Full staged pinning
no longer needs to be approximated by a first-stage support pair merely to make
the computation tractable.  The reduced full-staged census can first decide
which stratum/table configurations survive.  Sparse Lmax over-covers, Lmin
one-packets, and the individual pinning certificates can then be extracted
from the small residue to produce human structural inequalities or compact
rational certificates.

This retains the support-classification objective but reverses its role: sparse
supports explain and certify the final residue rather than serving as an
insufficient relaxation of full lexicographic selection.
