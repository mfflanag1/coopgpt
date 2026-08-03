# Seven-player all-shapes threshold frontier

Bounded dynamic-cut probes now cover every disjoint arm-size geometry on seven players, up to exchanging the two arms:

\[
(2,2,3),\ (3,2,2),\ (3,3,1),\ (4,2,1),\ (4,3,0),\ (5,2,0).
\]

Each search was capped after four exact circuit orbits. The collection is therefore a representative frontier, not an exhaustive seven-player census.

| arm shape | exact circuit orbits | transported supports | deficient orbits |
|---|---:|---:|---:|
| `(2,2,3)` | 4 | 96 | 1 |
| `(3,2,2)` | 4 | 84 | 3 |
| `(3,3,1)` | 4 | 81 | 2 |
| `(4,2,1)` | 4 | 120 | 2 |
| `(4,3,0)` | 4 | 264 | 4 |
| `(5,2,0)` | 4 | 720 | 3 |
| **total** | **24** | **1365** | **15** |

The ordinary balanced-recoloring capacities among these 24 orbits are

\[
1\quad(9\text{ orbits}),\qquad
\frac34\quad(1),\qquad
\frac23\quad(6),\qquad
\frac12\quad(8).
\]

Thus 15 of the 24 representative orbits are deficient under ordinary recoloring. Nevertheless, every deficient orbit satisfies the exact two-top-set identity

\[
\max\{\sigma_{P_1},\sigma_{P_2}\}=1,
\]

where \(P_g=\operatorname{argmax}_i u_{g,i}\) is the top level set of the capacity-dual player potential for bumped game \(g\), and \(\sigma_U\) is the generalized single-witness recoloring capacity at coalition \(U\).

The identity survives the stronger restrictions \(\mu_0=0\) and
\(\delta_1+\delta_2=0\): in every deficient orbit one of the two top sets
admits a zero-sum transfer using only the two bumped games.

After eliminating the redundant base color from the ordinary capacity LP,
one zero-sum dual potential \(z\) remains. Its maximum and minimum coordinate
classes give a canonical pair of witnesses. Across the full 31-case corpus,
each extreme succeeds in 29 cases and the pair covers all 31 exactly.
The four failures are pure support-nullspace gauge artifacts. Orthogonally
projecting the potential onto the support-nullspace complement preserves the
dual objective and makes both extremes succeed in all 31 cases, for 62/62
individual capacities equal to one.

Together with the five- and six-player cases, the current deficient corpus contains 31 exact circuit orbits. All 31 satisfy the same identity. This reduces the conjectural threshold-existence theorem to a two-cut alternative: one need only prove that at least one of the two canonical potential top sets has full single-witness capacity.

## Evidence

- Raw probes: `disjoint_n7_{223,322,331,421,430,520}_milp_probe15.json`
- Ordinary capacities: corresponding `*_recoloring_capacity.json` files
- Exact two-top-set capacity audit: `top_single_witness_capacity_audit.json`
- Canonical reduced audit: `canonical_extreme_box_capacity_audit.json`
- Support-nullspace quotient audit: `quotient_canonical_extreme_audit.json`
- Inclusion-minimal witness decompositions: `potential_guided_minimal_tights.json`
