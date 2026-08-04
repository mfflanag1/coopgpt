# Atomic reduction of every slack Lmin boundary

## Statement

Let `v` be exact, let `phi` be a core allocation, and split
`N=H disjoint-union L`, where `H` is nonempty and proper.  Suppose a family
of nonempty proper `phi`-tight coalitions has nonnegative weights `lambda_T`, common load
`alpha` on `H`, and loads `c_i<alpha` on every `i in L`.  Put

```text
beta = max_{i in L} c_i,       d_i = beta-c_i.
```

If `s_phi(H)>0`, then among the positive-support tight coalitions, the
deficit singletons `{i}` with `d_i>0`, and `H`, there is a subsystem `A`
with coefficients `a_S>0` for `S != H`, `gamma>0`, and a scalar `r` such
that

```text
sum_{S in A, S != H} a_S 1_S - gamma 1_H = r 1_N.   (A)
```

The subsystem can be chosen to be a pure minimal semi-balanced system with
exceptional coalition `H`, and

```text
|A| <= |N|.                                          (B)
```

Moreover `A` contains a deficit singleton of strictly positive `phi`-slack.
In a singleton-normalized game this means a poorer player `i` with
`d_i>0` and `phi_i>0`.

Thus every slack Lmin payoff boundary has an atomic certificate of this
form, because stagewise Lmin duality supplies the required strict tight
cover.

## Proof

Singleton completion gives the signed incidence relation

```text
sum_T lambda_T 1_T + sum_{i in L} d_i 1_{i}
  - (alpha-beta)1_H = beta 1_N.                      (C)
```

Project incidence vectors to the quotient space
`R^N / span{1_N}`.  Equation `(C)` is then a dependence whose only negative
coordinate is the coordinate of `H`.  The conformal circuit decomposition
theorem for a finite vector configuration writes this dependence as a
positive sum of circuit dependences with no new signs.  Since the total
coefficient of `H` is negative, at least one circuit has `H` as its unique
negative element.  Lifting that circuit out of the quotient gives `(A)`.

Minimality of a circuit makes its proper-coalition support a minimal
semi-balanced system.  Its unique negative sign makes it pure and makes `H`
its exceptional coalition.  The quotient has dimension at most `|N|-1`, so
every circuit has at most `|N|` elements, proving `(B)`.

Apply the exact-game slack inequality to `(A)`.  Every positive coalition
in the atom is either one of the original tight coalitions or a deficit
singleton.  Hence

```text
gamma s_phi(H)
  <= sum_{deficit singletons {i} in A} a_{i} s_phi({i}).  (D)
```

The left side is positive.  Consequently at least one deficit singleton in
the atom has positive slack.  Under singleton normalization its slack is
`phi_i`.

## What this does and does not claim

Conformal circuit decomposition is standard oriented-matroid/linear-algebra
machinery, and the resulting signed systems are the minimal semi-balanced
systems of the exact-game literature.  Neither ingredient is claimed as
new.  The candidate contribution is the Lmin-specific reduction: every
failed richer suffix selects an exceptional-coalition circuit whose positive
support is restricted to Lmin-tight protectors and costly poorer-side
singletons.

Minimal semi-balanced is not the same as *indecomposable* in the stronger
sense of Studeny and Kratochvil.  No claim of facet-inducing
indecomposability is made here.  Determining when the Lmin-selected atom can
be chosen indecomposable is the next structural question.

## Consequences for the research program

The obstruction search no longer needs arbitrary weighted covers.  It can
be organized around level-oriented signed circuits with at most `n`
coalitions.  The five-player broken diamond is the first support-four atom;
the seven-player three-trace example is a support-five atom.  A general
classification should therefore study which pure minimal semi-balanced
systems admit the additional Lmin level orientation, rather than enumerate
games or payoff vectors.

## The four/five threshold in one circuit count

An atom needs at least four coalitions: the exceptional suffix `H`, a costly
poorer singleton, and at least two tight protectors.  One protector cannot
strictly overload `H`: it would have to contain all of `H` and none of its
complement, hence would equal the slack coalition `H` while also being
tight.

The circuit bound therefore rules out every failure for `n<=3`.  At `n=4`
the atom is forced to have exactly two tight protectors and one poorer
singleton.  The two-column normal-form theorem turns those protectors into
the four nonempty Venn blocks `H,X,Y,R`.  All four blocks are singletons, so
the exterior budget reads

```text
phi(H) = s_phi(H) <= s_phi(R) = phi(R),
```

contradicting the strict richer/poorer payoff gap.  At five players one block
can acquire the extra slack capacity, and the sharp broken-diamond
realizations attain both possibilities.  This gives a structural proof of
the four/five threshold from circuit size plus slack conservation, without
enumerating payoff strata.

## Reproduction

```bash
PYTHONPATH=src python src/verify_atomic_lmin_obstruction.py \
  --output results/atomic_lmin_obstruction.json
```

The audit reconstructs the five- and seven-player games, recomputes Lmin,
checks the signed incidence identities with exact rationals, and verifies
that every proper subsupport is independent in the quotient incidence
configuration.  It checks the displayed examples only and is not a proof of
the conformal reduction.
