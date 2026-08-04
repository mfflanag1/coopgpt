# Property I versus the strict richer-side cover

## Bottom line

The tight-coalition characterization of Lmin/Lmax is not new. Arin, Kuipers,
and Vermeulen (2008, Definition 3 and Lemma 1, journal pages 569--570) prove
that `x=Lmax(v)` exactly when their hierarchical tight-coalition system has
**property I**, meaning that zero is its unique feasible direction. Mauri
(2018, Definitions 11--12 and Lemma 3, thesis pages 43--45) applies
antiduality to state the corresponding Lmin characterization with the reversed
payoff partition and complement-tight coalitions.

The present strict richer-side cover is therefore positioned only as a
quantitative LP-dual consequence/refinement of this known optimality
structure. The literature inspected does not display the simultaneous cover
or the later trace-integrality theorem. Specialist review must still decide
whether the cover is already implicit enough in property I that even the
word “refinement” is too strong.

## Primary-source statements

Arin--Kuipers--Vermeulen define property I for an ordered partition
`I=(I_1,...,I_p)` and a coalition collection `T`. Zero must be the unique
vector `z` satisfying:

```text
z(N)=0;
z(S)>=0 for every S in T;
at block k, if z is zero on all earlier blocks, then z_i<=0 on I_k.
```

Their Lemma 1 says that `(I(x),T(v,x))` has property I exactly when
`x=Lmax(v)`. Their proof is a qualitative feasible-direction argument.

Mauri reverses the payoff blocks and replaces tight coalitions by
complement-tight coalitions. Since `z(N)=0`, a complement-tight inequality
`z(N\T)>=0` is equivalent to `z(T)<=0` for the original tight coalition `T`.
This gives the Lmin form of the same qualitative criterion.

## Exact comparison

| Feature | Property I | Strict richer-side cover | Trace obstruction |
|---|---|---|---|
| Domain | Any balanced game/core point | Lmin of a balanced game | Lmin of an exact game |
| Object | Hierarchical cone of feasible directions | One nonnegative tight-coalition incidence combination | Projection of that combination to an exact-cover polytope on `H` |
| Conclusion | Zero is the unique lex-compatible direction | Common positive load on every `h in H`, strict underload on every `i in L` | Slack with two poorer players forces nonintegrality and an odd trace cycle |
| Extra input | Tight coalitions and ordered payoff blocks | Explicit individual-pinning LP dual plus backward combination | Exact `H`-face witness and Berge's balanced-matrix theorem |
| Novelty treatment | Established prior art | Candidate quantitative consequence/refinement; do not call a new characterization | Candidate new bridge; external review pending |

For a strict boundary `N=L disjoint-union H`, the new certificate is

```text
lambda_T>=0 on proper phi-tight T,
c_i=sum_{T contains i} lambda_T,
c_h=alpha>0 for h in H,
c_i<alpha for i in L.
```

Equivalently, after normalizing `alpha=1`, the rich traces of the positively
weighted coalitions form a fractional exact cover of `H`, while every poor
player is covered with total weight strictly below one. Property I itself
does not state this single simultaneous incidence identity.

## What is and is not being claimed

Not claimed as new:

- Lmin or Lmax;
- the tight-coalition feasible-direction criterion;
- property I or its antidual Lmin form;
- minimal balanced collections or balanced matrices.

Candidate new content, pending specialist review:

- extracting one simultaneous strict-deficit cover at every strict Lmin
  boundary;
- combining it with exact coalition-face witnesses to obtain balanced-trace
  transport;
- forcing nonintegrality of the active trace exact-cover polytope, and hence
  an odd balanced-matrix obstruction, at every two-poorer slack boundary.

## Reviewer question that remains open

Is the simultaneous strict cover a standard theorem-equivalent Farkas dual of
property I that should be cited merely as a reformulation, or is its
all-poor-player strictness a genuinely additional quantitative consequence?
Either answer leaves the later exact-face projection and integrality
obstruction to be assessed separately.

## Sources

- Javier Arin, Jeroen Kuipers, and A. J. Vermeulen (2008), [*An axiomatic
  approach to egalitarianism in TU-games*](https://doi.org/10.1007/s00182-008-0133-6),
  *International Journal of Game Theory* 37, 565--580.
- Llúcia Mauri Masdeu (2018), [*Essays on egalitarianism-based solution
  concepts for cooperative TU-games*](https://repositori.urv.cat/estatic/TDX0011/en_TDX2707.html),
  doctoral thesis, Universitat Rovira i Virgili.
