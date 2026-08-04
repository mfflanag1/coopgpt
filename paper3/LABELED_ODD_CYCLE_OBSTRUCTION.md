# Labeled odd-cycle obstruction

The ordinary rich-trace matrix forgets exactly the information that makes
minor lifting difficult: which tight coalitions contain the losing and
gaining poor players. The labels can instead be turned into matrix rows.

Start with an underloaded lifted packet at a slack two-poorer boundary. Its
poor loads satisfy

```text
r_a < r_b < 1.
```

Build an augmented zero-one matrix with rows `H union {a,b}`:

- every original column is the full incidence vector of its lifted tight
  coalition on those players;
- add dummy singleton columns `e_a,e_b`.

Give the dummies weights `1-r_a,1-r_b`. Together with the packet weights,
this is a fractional exact cover of every augmented row.

It cannot be a convex combination of integral exact covers. Every integral
exact cover selects original columns that partition `H` and load each poor
row at most once. If it selected dummy `e_b`, none of its original columns
would contain the gaining player. Their summed displacement would be

```text
-[phi(H)-v(H)] + q_a Delta_a < 0,
```

contradicting tightness and core feasibility. Thus every integral exact cover
has `e_b=0`, whereas the fractional point has `e_b=1-r_b>0`.

The augmented exact-cover polytope is therefore nonintegral. By the classical
balanced-matrix theorem, the augmented incidence matrix contains an odd-order
square submatrix with exactly two ones in every row and column. A dummy
column cannot occur in that submatrix because it has only one nonzero entry.
Hence the obstruction consists entirely of original lifted tight coalitions,
but now it retains any poor-player rows it uses.

In fact both one-label augmentations are nonbalanced separately. On rows
`H union {b}`, positive dummy `e_b` weight is incompatible with every
integral exact cover. On rows `H union {a}`, integrality would decompose the
packet into partitions, every one of which has integer gaining load at least
one, contradicting their average gaining load below one. Thus there is an odd
cycle on rows contained in `H union {a}` and another on rows contained in
`H union {b}`; both use only original columns.

This is a dimension-free, label-aware strengthening of the earlier rich-only
odd-cycle necessity. It does not yet guarantee that the odd cycle spans all
rich rows or contains both poor rows; those are the remaining lifting issues.
The balanced-trace packet mixture always contains an underloaded packet, so
the obstruction is unconditional at every slack two-poorer boundary.

The manuscript proof is Theorem `thm:lx-labeled-odd-cycle` in
`paper3/sections_leximin.tex`.
