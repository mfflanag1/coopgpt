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
