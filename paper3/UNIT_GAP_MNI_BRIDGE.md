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

There is a sharper scale-separated version. Let `q` be the number of active
columns and choose an integer `Lambda>q`. Use

```text
c_T = Lambda |T intersect H| + 1_{b in T}.
```

The same packet has cost `Lambda|H|+r_b<Lambda|H|+1`, and every integral
cover costs at least `Lambda|H|+1`. Now suppose a positive Lehman core with
row sum `r` is lifted through unit-weight contractions and retains this
strict cost bound. Any rich-row overcoverage—whether from overlapping
contractions, a surviving column hitting a contracted row, or a noncore
row—has size at least `1/r`. Since `r<=q<Lambda`, that one excess alone adds
more than one unit of scaled cost. Thus all rich rows are automatically
exact; disjointness and survivor avoidance follow. The remaining cost is the
gaining-player load below one, so contracted columns have no gaining label,
and transport removes their losing labels too.

Accordingly, a reduction preserving the single scaled objective gap would
simultaneously solve both lifting requirements. What remains open is whether
classical MNI reduction, or an appropriate cost-aware extension, preserves
this particular objective gap.

The manuscript statements are `thm:lx-unit-gap-set-cover` and
`cor:lx-scale-separated-exactness` in `paper3/sections_leximin.tex`.
