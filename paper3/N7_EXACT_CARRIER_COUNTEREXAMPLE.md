# Sharp seven-player exact carrier counterexample

The quantitative carrier inequality is true for every exact game through six
players and false at seven. The sharp counterexample is elementary.

Let

```text
a = (-3,  1, 3, -1,  2, -1, -1)
b = ( 3, -2, 0, -1, -1, -1,  2)
```

and define the exact three-generator lower-envelope game

\[
v(T)=\min\{0,a(T),b(T)\}.
\]

The exact leximin point is

```text
phi = a/4 = (-3/4, 1/4, 3/4, -1/4, 1/2, -1/4, -1/4).
```

It has a three-stage hand certificate. The singleton floors are

```text
m = (-3,-2,0,-1,-1,-1,-1),
```

and the successive gain strata are

```text
level 3/4: players 3,4,6,7
level 3/2: player 5
level 9/4: players 1,2.
```

Indeed, `v(125)=0` and efficiency force `x(3467)<=0`, giving the first
level and fixing players 3,4,6,7. On that face, `v(13)=v(27)=0` bounds
players 1 and 2 and forces `x5<=1/2`, giving the second level. Efficiency
then fixes `x1+x2=-1/2`, giving the final level. Thus no optimizer output is
needed to recognize `phi` as the leximin point.

For target `S={1,2,3}` and outside set `P={4,5,6,7}`, each of the six
nonempty proper `C` contained in `S` satisfies

\[
s_\phi(P\cup C)-s_\phi(C)=\frac34,
\]

so `gamma_S(phi)=3/4`. All four coalitions below are tight at `phi`. Applying
the displayed incidence identity to `x-phi` proves that every core point
dominating `phi` on `S` has the same `S`-sum. Thus `eta_S(phi)=0`, directly
disproving the leximin-specific quantitative carrier inequality.

The same construction has a stronger normalized gap at the reference core
point `psi=0`: each of the six differences satisfies

\[
s(P\cup C)-s(C)=1,
\]

so `gamma_S(0)=1`.

The four zero-valued coalitions

```text
13456, 457, 3467, 567
```

satisfy the incidence identity

\[
\mathbf1_S+\mathbf1_{13456}+\mathbf1_{457}
+\mathbf1_{3467}+\mathbf1_{567}+e_1+2e_2=3\mathbf1_N.
\]

For a core point nonnegative on `S`, every term on the left has nonnegative
payoff, while efficiency makes the right side zero. Hence its total payoff
on `S` is zero. Since the zero point is feasible, `eta_S(0)=0`.

Run the solver-free integer verifier from `coopgames/`:

```sh
python src/verify_n7_exact_carrier_counterexample.py
```

Replay the exact rational leximin calculation with:

```sh
python src/verify_n7_exact_carrier_counterexample_leximin.py
```

The first verifier checks the structural construction without a solver. The
second independently computes the leximin point in exact rational arithmetic.
Together they establish that the complete computer-assisted theorem through
six players is dimension-sharp and resolve the unrestricted quantitative
carrier conjecture negatively.

## Every higher dimension

Appending any number of null players preserves the counterexample. Extend all
three generators by zero. The enlarged core is exactly the old core times
fixed zero coordinates, so the old leximin point, carrier differences, and
eta value are unchanged. Consequently the inequality holds universally
exactly through six players and fails at every dimension `n>=7`.

The extension identities can be replayed through any desired finite cutoff:

```sh
python src/verify_n7_exact_carrier_dummy_extensions.py --max-n 12
```

## Structure and nonuniqueness

Eight zero-valued coalitions form a degree-four balanced collection of
incidence rank five. They force the entire core into `span{a,b}`; the core
constraints at `3`, `13`, and `4` then give

```text
Core(v) = conv{0,a,b}.
```

Each vertex uniquely minimizes one of `1`, `2`, and `123`, so all three
generators are indispensable.

The example belongs to a nontrivial two-parameter family.  For every rational
or real pair satisfying

```text
kappa >= 0,   theta - 2*kappa > 1/4,   kappa + theta <= 1,
```

```text
v_(kappa,theta)(T) = min{0,a(T),(kappa*a + theta*b)(T)}
```

has the same leximin point `a/4` and

```text
gamma_S = theta - 2*kappa - 1/4,   eta_S = 0.
```

Thus the counterexample is not unique up to permutation and scaling and is
robust on a relatively open two-dimensional generator-perturbation wedge.
Replay the structural and family certificates with:

```sh
python src/verify_n7_exact_carrier_structure.py
python src/verify_n7_exact_carrier_family.py
```

The family does **not** directly refute proper-coalition monotonicity.  This is
intrinsic to the tight-face certificate, rather than an accident of unique
attainment at the zero vertex.  The incidence identity

```text
1_135 - 2*1_123 = 1_13456 + 1_457 + 1_567 - 2*1_N
```

implies `x(135) >= 2*x(123)` at every core point, because the three coalitions
on the right have value zero.  On the zero-valued face `F_135`, core
feasibility therefore forces `x(123)=0`.  The exact bump capacity at the
failure target is zero: no positive exact bump of `123` exists.  Any
deformation preserving these zero faces remains blocked, so a monotonicity
counterexample requires a genuinely different, binding-bumpable obstruction.
