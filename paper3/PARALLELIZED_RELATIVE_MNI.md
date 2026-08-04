# Parallelized relative-MNI reduction

Let `C` be the active rich-row clutter on lifted tight-coalition columns and
let `c` be a positive integral column cost. Replace every column `T` by
`c_T` clones and every clutter member by all choices of one clone from each
of its original elements. Denote the resulting parallelization by `C^c`.

The weighted and unweighted covering numbers agree exactly:

```text
tau(C^c)   = tau^c(C),
tau_f(C^c) = tau_f^c(C).
```

For integer covers, every original member must contain a clone class selected
in its entirety; otherwise one can choose an unselected clone from every
class and obtain an uncovered parallel member. Partial classes are useless.
For fractional covers, averaging over permutations within clone classes
preserves feasibility and cardinality and produces a symmetric point whose
common class values are precisely a weighted fractional cover of `C`.

Apply this to the scale-separated cost

```text
c_T = Lambda |T intersect H| + 1_{b in T}.
```

The parallelized clutter is nonideal for the ordinary all-ones objective.
This is an exact unweighted restatement of the scaled objective gap.

Ordinary nonideality guarantees an MNI minor but does not guarantee this
global threshold after lifting. There is a second, more serious obstruction:
MNI core rows in the parallelized clutter are clone-variant covering
constraints, not original rich players. Averaging a lifted MNI point within
clone classes maps it back to a weighted original cover, but introduces
denominators `c_T r`. The `1/r` excess quantum behind scale-separated
exactness is then unavailable. Thus one cannot apply the scaled Lehman lift
after clone averaging.

General set-cover facets are not exhausted by ordinary minor inequalities;
even circulant work introduces generalized minor inequalities beyond the
basic family. Therefore parallelization is a useful exact reformulation but
not a solution. A proof must exploit the exact-game player-incidence and
label structure before taking an MNI minor. The manuscript statement is
Proposition `prop:lx-parallelized-relative-minor`.
