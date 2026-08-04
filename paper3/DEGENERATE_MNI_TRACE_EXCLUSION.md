# Degenerate minimally-nonideal traces are impossible

Lehman's minimally-nonideal theorem has one exceptional family besides
positive Lehman cores: the degenerate projective planes. Their trace matrix
can be written with rows `h_0,...,h_t` and columns

```text
R_0 = {h_1,...,h_t},
R_i = {h_0,h_i},              1 <= i <= t.
```

The unique fractional exact cover gives `R_0` weight `(t-1)/t` and every
leaf column weight `1/t`.

Let `u_0,v_0` be the losing/gaining labels of `R_0`, and let `u,v` count
the corresponding labeled leaf columns. The poor loads are

```text
r_a = [(t-1)u_0+u]/t,
r_b = [(t-1)v_0+v]/t.
```

At an underloaded packet, the transport inequality forces

```text
r_a < r_b < 1.
```

There are two cases.

- If `v_0=0`, then `1<=v<=t-1`, while strict load ordering forces `u_0=0`
  and `u<v`. Some gaining-labeled leaf `R_i` is not losing-labeled.
- If `v_0=1`, underload forces `v=0`, while strict load ordering forces
  `u_0=0` and `u<=t-2`. Some leaf `R_i` is losing-unlabeled.

In both cases, selecting `R_0` and that `R_i` gives rich load

```text
1_H + e_{h_i}
```

and a nonzero zero-one poor load. This is a forbidden safe rooted tight
cover. Hence no lifted degenerate-projective-plane packet can carry the
required underload.

This removes the exceptional branch of the classical MNI theorem. A
deficit-preserving MNI reduction must therefore reach a positive Lehman core,
where `LEHMAN_MINOR_LIFTING.md` applies.

The manuscript proof is Theorem `thm:lx-degenerate-mni-exclusion` in
`paper3/sections_leximin.tex`.
