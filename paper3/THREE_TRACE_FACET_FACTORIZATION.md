# Two-facet factorization of the three-trace obstruction

Let the rich block be the disjoint union `H=C union A union B`, with poorer
players `a,b`, and define

```text
T1=C union A,          T2=C union B,
T3={b} union A union B,
U=H union {a},         D=A union B.
```

The rooted three-trace identity splits into

```text
1_T3 + 1_U - 1_D = 1_N,                 (complementary diamond)
1_T1 + 1_T2 + 1_D - 2 1_H = 0.          (internal triangle)
```

Adding them eliminates `D` and gives

```text
1_T1+1_T2+1_T3+1_U-2 1_H=1_N,
```

which is the rooted obstruction atom.

Both factors are indecomposable minimal semi-balanced systems.  This is
proved without player enumeration by collapsing equal incidence rows:

- The internal system has the three block types `C,A,B`; its supported
  proper sets are the three edges of the triangle and their union `H`.  Its
  unique dependence is `(1,1,1,-2)`, and none of the three singleton block
  unions can be a new exceptional set.
- The complementary system has row types
  `X={a} union C`, `Y={b}`, and `Z=A union B`, with incidence patterns
  `(0,1,0)`, `(1,0,0)`, and `(1,1,1)` in columns `(T3,U,D)`.  Testing the
  eight unions of these three row types leaves only the empty set, the three
  supported sets, and `N`; no decomposition exists.

By the published exact-cone facet criterion, both factors define facets.

At the displayed Lmin point, `T1,T2,T3` are tight and `s(H)=1`.  Exact
balancedness therefore gives

```text
2 s(H) <= s(D) <= s(U).
```

The construction has `s(U)=2`, so `s(D)=2` and both facet inequalities are
saturated.  Consequently the rooted three-trace obstruction is exactly a
sum of two active facet atoms.  The five-player rooted broken diamond is a
single facet atom, so the first two obstruction tiers admit saturated facet
decompositions of lengths one and two.

The exact-cone facet criterion and the underlying three-cycle balanced
system are prior art.  The candidate contribution is the Lmin-specific
rooting and the exact saturated factorization of the full three-trace
obstruction family.
