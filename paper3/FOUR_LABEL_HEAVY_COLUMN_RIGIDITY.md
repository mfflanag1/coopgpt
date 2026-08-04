# Four-label heavy-row column rigidity

This note extracts a global exact incidence from the thin four-label local
normal form.

## Theorem

Assume `k=1`, `|V|=4`, `|U|=3`, `r>=6`, and neither singleton residual band
applies.  Define the heavy losing-label rows by

```text
H_U={d:u_d>=2}.
```

Then there is a unique label `a_* in U` such that

```text
|H_U|=s,
1_(H_U)=B 1_{a_*}.
```

Thus a `B`-row contains `a_*` exactly when it contains at least two of the
three losing labels.

## Proof

Every `A`-column outside `U` has total `U`-load three.  On a neutral column,
the six-tile normal form contains exactly one row of load two or three.  On a
column in `V setminus U`, three rows of `U`-load one would each have `V`-load
at least two, exceeding the available total `V`-load five.  Hence every
column outside `U` contains exactly one heavy row.

Every column of `U` has total `U`-load four, so it contains at most two heavy
rows.  It cannot contain none: four `U`-simple rows would have total `V`-load
at least eight, whereas a `U`-column has `V`-load four or five.  Thus each of
the three `U`-columns contains one or two heavy rows.

Let `t` count the `U`-columns containing two heavy rows.  Since every heavy
row lies in `r` columns of `A`, double counting gives

```text
r|H_U| = (n-3)+(3+t) = rs-1+t.
```

Here `0<=t<=3` and `r>=6`.  Divisibility forces `t=1` and `|H_U|=s`.  If
`a_*` is the unique doubled column, then

```text
A^T 1_(H_U)=1+1_{a_*}=A^T B 1_{a_*}.
```

Nonsingularity of `A` yields `1_(H_U)=B1_{a_*}`.

## Dual-cubic exclusion

The theorem rules out the entire `s=3` branch.  A surviving `(w,u)=(1,3)`
row has only three entries, so the label overlap is one and this row is
exactly `U`.  It is the unique `u=3` row because `B` has distinct rows.  The
heavy set has size `s=3`, leaving two `u=2` heavy rows.  The residual row
types permit only `w=0,3,4` for such a row.  Size three rules out `w=4`, and
`w=3` would put the entire row in `V`, which contains only one `U` label.
Thus both remaining heavy rows have `w=0` and contain the two noncommon
columns of `U`.  Together with the `u=3` row, this makes those two `B`-columns
identical, contradicting nonsingularity.  Therefore every survivor has

```text
s>=4.
```

## Structural interpretation

The six local trace types do not assemble freely.  They force one of the
three losing labels to act as an exact majority gate: it is present in a row
if and only if that row contains a majority of `U`.  The remaining problem is
to combine this canonical column with the disjoint-support and companion-star
packing in `FOUR_LABEL_SIMPLE_ROW_PACKING.md`.  No global contradiction is
claimed here.
