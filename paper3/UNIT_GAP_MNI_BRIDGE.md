# Unit-gap bridge to minimally-nonideal set covering

At a slack two-poorer Lmin boundary, let `a` lose and `b` gain at a core
point exact on the richer suffix `H`. A lifted fractional packet covers every
rich player exactly once and has gaining-player load `r_b<1`.

Give each lifted tight-coalition column the integral cost

```text
c_T = |T intersect H| + 1_{b in T}.
```

The fractional packet has cost

```text
|H| + r_b < |H| + 1.
```

Every integral set cover costs at least `|H|+1`. Indeed, its total rich
incidence is an integer at least `|H|`. If it is larger, it is already at
least `|H|+1`. If it equals `|H|`, the selected columns form an exact
partition of `H`. Such a partition must use `b`: otherwise its summed
tight-coalition displacement is

```text
-[phi(H)-v(H)] + r_a Delta_a < 0,
```

contradicting core feasibility at the exact point.

Thus the active trace matrix is nonideal for an explicit integral objective,
with a strict unit-threshold gap. More importantly, every lifted fractional
exact cover has cost exactly `|H|+r_b`. Preserving the cost below `|H|+1`
through a minor reduction is therefore exactly the same as preserving the
single scalar gaining-player deficit `r_b<1`.

Combined with `LEHMAN_MINOR_LIFTING.md`, this changes the remaining question
from an informal two-label problem into a cost-aware minimally-nonideal
reduction problem:

> Does every such unit-gap active matrix have a positive Lehman minor whose
> lifted fractional core still has cost below `|H|+1` and covers every
> uncontracted rich row exactly once?

If yes, contracted columns are automatically poor-label-free and the Lehman
rooted-cover or strict slack-amplification conclusions lift to the original
suffix. Otherwise the excess on classical noncore MNI rows needs a separate
structural treatment.

The manuscript theorem is `thm:lx-unit-gap-set-cover` in
`paper3/sections_leximin.tex`.
