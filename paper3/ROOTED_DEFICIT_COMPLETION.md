# Rooted deficit completion and the facet bridge

## Stronger completion inequality

Let `v` be exact, `phi` a core point, and `N=H disjoint-union L`.  Suppose
`phi`-tight protectors have load `alpha` on `H` and loads `c_i<=beta<alpha`
on `L`.  Put `d_i=beta-c_i`, and let nonnegative weights `nu_Q` on nonempty
`Q subseteq L` cover `d` exactly.  Write `tau=sum_Q nu_Q`.

Then

```text
(alpha-beta+tau)s_phi(H) <= sum_Q nu_Q s_phi(H union Q),
```

or, equivalently,

```text
(alpha-beta)s_phi(H)
  <= sum_Q nu_Q [s_phi(H union Q)-s_phi(H)].          (RMC)
```

The proof is the substitution

```text
1_Q = 1_{H union Q} - 1_H
```

in the deficit-completion incidence identity, followed by exact
balancedness.

For disjoint `H,Q`, the rooted marginal cost is

```text
s_phi(H union Q)-s_phi(H)
  = s_phi(Q)-[v(H union Q)-v(H)-v(Q)].               (RMS)
```

Exact games are totally balanced and hence superadditive on disjoint
coalitions.  The bracketed term is therefore nonnegative: rooting subtracts
the full superadditivity surplus from the earlier completion charge.

## Rooted completion functional

Define

```text
kappa^H_phi,L(d)
  = min sum_Q nu_Q [s_phi(H union Q)-s_phi(H)]
    subject to sum_Q nu_Q 1_Q=d, nu_Q>=0.
```

Then every strict tight cover satisfies

```text
(alpha-beta)s_phi(H) <= kappa^H_phi,L(d) <= kappa_phi,L(d).
```

It also has the marginal-worth gap representation

```text
kappa^H_phi,L(d) = d dot phi_L
  - max sum_Q nu_Q [v(H union Q)-v(H)]
    subject to sum_Q nu_Q 1_Q=d, nu_Q>=0.
```

Thus the obstruction cost is the gap between the deficit's payoff price and
the maximum fractional marginal worth that poorer coalitions can create when
joined to the failed suffix.  A nonpositive rooted cost forces `H` tight.

## Rooted atomic reduction

Use singleton completion and replace every deficit singleton `{i}` by the
proper rooted coalition `H union {i}`.  Properness follows because a slack
boundary must have at least two poorer players.  Conformal circuit
decomposition then gives a pure minimal semi-balanced circuit:

- its exceptional coalition is `H`;
- it has at most `n` coalitions;
- every positive coalition is either an Lmin-tight protector or a rooted
  singleton `H union {i}`;
- at least one rooted singleton is slack.

This quotients out the forced union triangle responsible for the universal
decomposability of the raw atom.

## What the examples show

For the five-player broken diamond, rooting the exterior singleton produces

```text
1_A + 1_B + 1_{H union R} - 2 1_H = 1_N.
```

The rooted circuit is indecomposable in the Studeny--Kratochvil sense and
therefore corresponds to an exact-cone facet.

For the seven-player three-trace obstruction, rooting the losing poorer
singleton again gives a minimal circuit and a sharp rooted budget, but the
system still has one decomposition.  Hence rooting is not a universal facet
correspondence.  It is a canonical bridge whose residual decompositions
measure obstruction complexity beyond the five-player diamond.

The exact-game incidence inequalities and indecomposable-facet criterion are
prior art.  Candidate novelty is limited to the Lmin-selected rooting, the
marginal completion functional, the rooted atomic reduction, and the
five-versus-seven comparison.  Specialist review is required.

## Reproduction

```bash
PYTHONPATH=src python src/verify_rooted_deficit_completion.py \
  --output results/rooted_deficit_completion.json
PYTHONPATH=src python src/probe_lmin_atom_indecomposability.py \
  --output results/lmin_atom_indecomposability_probe.json
```
