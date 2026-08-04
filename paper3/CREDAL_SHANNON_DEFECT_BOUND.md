# A sharp Shannon upper-entropy bound from richer-face defects

## Theorem

Let `K` be a nonempty compact set of probability distributions on `n>=2`
states, let `phi in K`, and let

```text
epsilon=max_j {phi(H_j)-min_{p in K}p(H_j)}
```

over the cumulative richer suffixes at the strict coordinate boundaries of
`phi`. Put

```text
tau=min{epsilon,1-1/n},
h(t)=-t log t-(1-t)log(1-t).
```

For Shannon entropy `H(p)=-sum_i p_i log p_i`, using any fixed logarithm
base consistently,

```text
sup_{p in K} H(p)-H(phi) <= h(tau)+tau log(n-1).          (SE)
```

For an atom-vacuous coherent lower probability and its inc-max distribution,
`epsilon` is bounded by the maximum normalized uncrossing-defect budget over
the strict payoff boundaries. Thus local binding-event defects give an
explicit, dimension-free upper-entropy regret guarantee.

## Proof

The defect-to-uncertainty stability theorem gives, for every `p in K`, a
distribution `q` Lorenz-dominated by `phi` with

```text
T=(1/2)||p-q||_1 <= epsilon.
```

Schur concavity of Shannon entropy gives `H(q)<=H(phi)`. The sharp classical
case of the Fannes--Audenaert inequality gives

```text
|H(p)-H(q)| <= h(T)+T log(n-1).
```

The right side increases through `T=1-1/n` and reaches `log n` there. Hence
its maximum over `0<=T<=epsilon` is the right side of `(SE)` with
`tau=min{epsilon,1-1/n}`. Combining the two inequalities proves the result.

The continuity inequality is established prior art. The candidate new step
is only its composition with the richer-face and binding-defect stability
theorem.

## Sharpness

The constants in `(SE)` cannot be improved for arbitrary compact `K`. Fix
`0<=epsilon<=1-1/n` and take

```text
phi=(1,0,...,0),
p=(1-epsilon,epsilon/(n-1),...,epsilon/(n-1)),
K={phi,p}.
```

The sole richer suffix of `phi` has slack `epsilon`, while

```text
H(p)-H(phi)=h(epsilon)+epsilon log(n-1).
```

This sharpness family concerns the general geometric theorem; `phi` is not
the inc-max point of this two-point set.

## Exact upper entropy in the five-state obstruction

The sharp five-state credal obstruction has normalized inc-max

```text
phi=(1,1,13/2,5,13/2)/20
```

and `epsilon=1/20`. Its unique Shannon-entropy maximizer can be written
exactly over `Q(sqrt(43))` as

```text
x*=(2 sqrt(43)-12,
    14-2 sqrt(43),
    13-sqrt(43),
    2 sqrt(43)-8,
    13-sqrt(43))/20.
```

It lies in the full credal core and binds exactly the two protector events
`{1,3,5}` and `{3,4,5}`. Strict concavity and the exact KKT identity

```text
x*_1 x*_4 = x*_2 x*_3 = x*_2 x*_5
```

prove uniqueness. In natural-log units,

```text
H(phi)        = 1.376701380459432,
H(x*)         = 1.377456128766748,
actual regret = 0.000754748307316,
theorem bound = 0.267829961401867.
```

The theorem is valid but deliberately worst-case; the flagship obstruction
does not nearly saturate the Shannon specialization.

For completeness, maximize entropy first on the relaxation defined only by
nonnegativity, total mass `20`, and the two lower bounds
`x({1,3,5})>=14`, `x({3,4,5})>=18`. The displayed point is positive and
binds both bounds. Its KKT multipliers are

```text
alpha=log(x*_1/x*_2)>0,
beta =log(x*_4/x*_2)>0,
```

and stationarity is exactly the displayed product identity. Strict concavity
makes it the unique maximizer of the relaxation. The full core is contained
in that relaxation, while exact quadratic-field checks put `x*` in the full
core. Hence it is also the unique maximizer of the full core.

## Prior art boundary

Audenaert (2007) proves the sharp continuity inequality and treats the
classical Shannon case explicitly. Horodecki, Oppenheim, and Sparaciari
(2018) establish the approximate-majorization distance used upstream.
Neither result is claimed here.

The candidate contribution is the route

```text
binding-event defects -> richer-face slack -> approximate majorization
                      -> simultaneous upper-entropy regret.
```

This cross-field composition requires review by specialists in information
theory, imprecise probability, and cooperative games.

## Exact audit

```bash
python src/verify_credal_shannon_stability.py \
  --output results/credal_shannon_stability.json
```

The verifier checks the quadratic-field core inequalities, KKT identity,
entropy values, continuity bound, and a sharpness family. It is not proof
evidence.
