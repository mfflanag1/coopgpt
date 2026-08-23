# Hostile specialist review — PXC109–PXC111 exact-cone projection

Checkpoint date: 2026-08-22. Review the current head of
`codex/pxc107-canonical-circuits`, starting from the frozen PXC108 checkpoint
`c1abcefb0c327ca09c437f95e7956f3af3ac63af`.

Do not treat the verifier outputs as proofs of the general statements. Check
the projection argument, semi-balanced indecomposability proof, exact-cone
facet interpretation, and negative counterexample independently.

## Claims to review

### PXC109 — cellwise rational-polyhedral projection

Fix `n`, the ordered equality strata of `x=Lmin(v)` and `z=Lmax(v)`, their
active core rows, a fixed complete `Cx`, active zero-coordinate normals, every
qualifying extreme top-cover support, and the PXC108 edge/nonedge pattern.
The corresponding realization set in `(v,x,z)` is a relatively open rational
polyhedral cone. The fixed-`n` sparse-fidelity failure locus is a finite union
of its projections to game-value space.

The load-bearing point is that, once active menus and strata are fixed, every
staged selector condition is the PXC92b rational tangent/Farkas test and every
cover/graph condition is incidence-only. Projection may destroy a convenient
irredundant description, but not rational polyhedrality.

### PXC110 — partition-star facets

For a proper coalition `T` and a partition

```text
N\T = B_1 disjoint-union ... disjoint-union B_m,   m >= 2,
```

the identity

```text
sum_i 1_(T union B_i) - (m-1) 1_T = 1_N
```

is an indecomposable min-semi-balanced system and therefore defines an
exact-cone facet by Studený–Kratochvíl. The conventional exceptional-set
proof forces a prospective exceptional coalition to be constant on every
block and reduces its nonnegative coefficients to

```text
u_i = c + e_i,
u_T = -(m-1)c + e_T - sum_i e_i.
```

Only `empty`, `N`, `T`, and the supported `T union B_i` survive.

### PXC111 — sharp relationship to PXC108

- PXC101: the positive cover plus the tight top pair is one partition-star
  facet. The forced-zero row `rj` lies outside its support. This is a
  facet–blocker flag, not a new facet.
- PXC104/PXC105: the two positive covers complete to two indecomposable
  catalogue-type-33 exact-cone facets. `rhaj` belongs only to the second and
  blocks the first cover; `rhak` belongs only to the first and blocks the
  second. The PXC108 obstruction is exactly a minimal two-facet dependency
  cycle.
- PXC106: the two partitions are
  `{b}|J|({a} union K)` and `{b}|({a} union J)|K`, giving the same two-facet
  cycle for all nonempty blocks and every admitted dimension.
- The universal facet correspondence is false. In PXC88 the unique cover
  rows `0134,0125,16` and indispensable blockers `0126,0136`, together with
  the constant target column, have rank six on six columns. Hence no subset
  of the natural obstruction rows has any constant incidence dependence and
  none can be semi-balanced. Unequal top coefficients `(1/3,2/3)` prevent the
  top-pair shear.

The current result does **not** say PXC88 is globally the smallest projection
failure; it is the smallest certified unequal-top example in this record.

## Exact ranks and scope

The complete published six-player catalogue has 7,006 distinct labelled
facet normals after permutation and deduplication.

- Generic PXC101 anchor `(M,q,J,K)=(15/4,3,2,1)`: 552 tight facets, normal
  rank 54, minimal exact-face dimension 9.
- PXC105 anchors `A=17/4,5,21/4`: 835 tight facets, normal rank 53, minimal
  exact-face dimension 10 at each anchor.
- The conic PXC105 family has dimension 2 inside that face.

These ranks show that the selector obstruction is finer than exact-face
membership. They do not by themselves prove the dimension-free theorems.

## Files

- Manuscript: `paper5/divergence.tex`, displays PXC109a–PXC111b.
- Protected ledger: `paper5/PROTECTED_RESULTS_LEDGER.md`.
- Program note: `paper5/FORCED_ZERO_BLOCKER_PROGRAM.md`.
- Primary verifier:
  `verifiers/divergence/verify_pxc109_exact_cone_projection.py`.
- Independent verifier:
  `verifiers/divergence/verify_pxc109_exact_cone_projection_independent.py`.
- Adjacent pinned JSON files have the same stems.

## Reproduction

From `coopgames/`:

```bash
"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc109_exact_cone_projection.py \
  --output /tmp/pxc109.json
cmp verifiers/divergence/pxc109_exact_cone_projection.json /tmp/pxc109.json

"${PAPER5_PYTHON}" \
  verifiers/divergence/verify_pxc109_exact_cone_projection_independent.py \
  --output /tmp/pxc109-independent.json
cmp verifiers/divergence/pxc109_exact_cone_projection_independent.json \
  /tmp/pxc109-independent.json
```

The primary verifier uses the bundled n=6 Studený–Kratochvíl catalogue and
the project exact-rational LP only to reconstruct the PXC101 lower envelope.
The independent verifier is solver-free and imports no project LP, selector,
cover, catalogue, semi-balanced, PXC108, or PXC109 implementation.

## Hostile questions

1. Does fixing active rows and ordered strata really make every staged
   selector statement incidence-only, including active nonnegativity and
   degenerate ties?
2. Is the image of each relatively open rational cone stated with the correct
   topology, and is “finite union” justified without silently fixing a bound
   on certificate support beyond finite `n`?
3. Does PXC109 quantify over all complete `Cx` choices or only one fixed
   certificate, and is that consistent with PXC108?
4. In PXC110b, are all possibilities for the common load `c` and a candidate
   exceptional set covered, including `empty` and `N` conventions?
5. Does the exceptional-set calculation prove indecomposability under the
   exact definition in Studený–Kratochvíl, rather than only support minimality?
6. Is the partition-star family already named or classified explicitly in
   Lohmann–Borm–Herings, Studený–Kratochvíl, or subsequent catalogues?
7. Is equal top weight genuinely necessary for a canonical top-pair shear, or
   can an unequal cover project to a semi-balanced system after adding a
   different coalition not in the obstruction support?
8. Do the two PXC104 facet supports form a minimal union in the precise sense
   claimed, and does their circuit–covector incidence graph have exactly the
   two directed cross edges?
9. Does the PXC106 proof remain valid when either block has size greater than
   one, including internal exchange tangents?
10. Does augmented rank six for PXC88 rule out every natural support-preserving
    semi-balanced projection, or only the most literal one? Is the manuscript's
    qualification narrow enough?
11. Are the 7,006-normal census, active counts, and rank computations using the
    correct inequality orientation and full exact-cone coordinates?
12. Could PXC101/PXC104 lie on a lower-dimensional selector-augmented facet in
    a meaningful canonical cone even though they are not new facets of the
    exact-game cone?
13. Is “facet-dependency cycle” established terminology elsewhere, and if not,
    is it appropriately presented as descriptive rather than prior-art novelty?
14. Does oriented-matroid programming already package this exact circuit–
    covector/facet-cycle coupling under a standard pivot-cycle theorem?
15. Is the significance best described as a dimension-free exact-cone
    interpretation of two families plus a sharp boundary theorem, rather than
    a general classification of PXC108 obstructions?

## Prior-art baseline

- Studený and Kratochvíl, *Facets of the cone of exact games*, DOI
  `10.1007/s00186-022-00770-4`: indecomposable semi-balanced systems are in
  one-to-one correspondence with exact-cone facets.
- Lohmann, Borm and Herings, *Minimal exact balancedness*, DOI
  `10.1016/j.mathsocsci.2012.01.002`: minimal exact balanced collections and
  their three generation types.
- Reijnierse and Derks, *Note on the core of a collection of coalitions*, DOI
  `10.1007/s001820050084`: the distinct cooperative-game notion of exact
  covers.
- Björner et al., *Oriented Matroids*, DOI
  `10.1017/CBO9780511586507`: circuits, covectors, and oriented-matroid
  programming are standard prior art.
- Multiparametric LP critical-region theory: optimal active-set regions are
  polyhedral; PXC109's possible novelty is the selector/cover specialization,
  not that general fact.

## Restrained significance

If correct, PXC109–PXC111 is a substantial structural advance over PXC108:
it gives an explicit rational-polyhedral failure locus, proves a
dimension-free exact-cone facet interpretation for the two all-dimension
families, and identifies the exact boundary where the facet interpretation
fails. It is still not a classification of all obstruction graphs or all
exact-cone faces, and the partition-star facet itself is likely existing
semi-balanced theory. External specialist confirmation is required before any
novelty or field-breakthrough claim.
