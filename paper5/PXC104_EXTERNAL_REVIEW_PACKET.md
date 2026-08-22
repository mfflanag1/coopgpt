# Hostile external review — PXC104--PXC107 cross-cover obstruction

Checkpoint date: 2026-08-22. Review `PXC104--PXC107` in
`paper5/divergence.tex` and the exact verifier artifacts below. These results
are intended to refute the
proposed *universal* forced-zero-blocker explanation, not PXC103's correctly
scoped common-direction iff.

## Claimed theorem

The compact nonnegative total-23 polytope has rows

```text
rha>=16, rhb>=16, rhj>=13,
rhaj>=18, rhk>=13, rhak>=18.
```

Its lower-envelope game is exact and singleton-normalized, with

```text
Lmin = (41/6,41/6,7/3,7/3,7/3,7/3)
Lmax = (6,6,5,4,1,1).
```

The only proper x-tight rows are `rha,rhb`; their pair is the unique complete
proper-row `Cx`. The proper z-tight menu is exactly
`rh,rhb,rhj,rhaj,rhk,rhak`. Its normalized cover polytope has exactly three
vertices:

```text
{rh}                         weight 1/2, eta 0
{rhb,rhj,rhak}               weights 1/4, eta 1/4
{rhb,rhaj,rhk}               weights 1/4, eta 1/4
```

The three reduced Lmax selectors are respectively

```text
(6,6,4,4,3/2,3/2)
(6,6,4,4,1,2)
(6,6,4,4,2,1).
```

There is no common staged descent: after the top block is fixed, the union of
the cover supports has zero kernel. Instead `rhaj` blocks the first positive
cover's descent and belongs to the second cover; `rhak` blocks the reverse
descent and belongs to the first. No load-bearing blocker has coefficient zero
in every cover.

PXC105 replaces the fixed payoff `a=5` by any rational `4<A<11/2`, changes
the total to `18+A`, and changes the two long bounds to `13+A`. It proves

```text
Lmin = (((46-A)/6)^2,((A+2)/3)^4)
Lmax = (6,6,A,4,1,1)
```

with the same unique Cx, tight-menu incidence, and cover triangle. The three
reduced Lmax selectors become

```text
(6,6,4,4,(A-2)/2,(A-2)/2)
(6,6,4,4,1,A-3)
(6,6,4,4,A-3,1).
```

PXC106 replaces the two low outsiders by nonempty blocks `J,K` of sizes
`p,q`.  Its two positive covers partition the non-top players in opposite
ways, and the explicit specialization `p=1,q=n-5,A=4+1/(n-3)` gives a
non-null cross-cover counterexample for every `n>=6`.

## Exact reproduction

From the repository root:

```bash
python3 verifiers/divergence/verify_pxc104_cover_dependent_counterexample.py \
  --output /tmp/pxc104-primary.json
cmp verifiers/divergence/pxc104_cover_dependent_counterexample.json \
  /tmp/pxc104-primary.json

python3 verifiers/divergence/verify_pxc104_cover_dependent_counterexample_independent.py \
  --output /tmp/pxc104-independent.json
cmp verifiers/divergence/pxc104_cover_dependent_counterexample_independent.json \
  /tmp/pxc104-independent.json

python3 verifiers/divergence/verify_pxc105_cross_cover_family.py \
  --output /tmp/pxc105-primary.json
cmp verifiers/divergence/pxc105_cross_cover_family.json \
  /tmp/pxc105-primary.json

python3 verifiers/divergence/verify_pxc105_cross_cover_family_independent.py \
  --output /tmp/pxc105-independent.json
cmp verifiers/divergence/pxc105_cross_cover_family_independent.json \
  /tmp/pxc105-independent.json

python3 verifiers/divergence/verify_pxc106_cross_cover_dimension_lift.py \
  --output /tmp/pxc106-primary.json
cmp verifiers/divergence/pxc106_cross_cover_dimension_lift.json \
  /tmp/pxc106-primary.json

python3 verifiers/divergence/verify_pxc106_cross_cover_dimension_lift_independent.py \
  --output /tmp/pxc106-independent.json
cmp verifiers/divergence/pxc106_cross_cover_dimension_lift_independent.json \
  /tmp/pxc106-independent.json

python3 verifiers/divergence/verify_pxc107_obstruction_alternative.py \
  --output /tmp/pxc107.json
cmp verifiers/divergence/pxc107_obstruction_alternative.json \
  /tmp/pxc107.json
```

The primary verifier uses the project exact rational simplex and exhausts all
complete-Cx subsets and qualifying extreme covers. The second verifier uses a
solver-free rational active-set engine and imports no project LP, selector,
game, cover, family, or PXC103 code.

Discovery-only provenance:

- `verifiers/divergence/search_archive/search_pxc103_incidence_second_mechanism.py`
  finds the minimal five-row abstract no-common-ray menu;
- `verifiers/divergence/search_archive/search_pxc103_exact_second_mechanism.py`
  exactifies the obstruction and records the faithful boundary near-misses;
- their JSON artifacts are finite discovery evidence, not theorem proof.

## Hostile questions

1. Does the two-row Lmin inequality really prove the full staged Lmin, including
   the final top tie, and does it justify uniqueness of the complete Cx?
2. Does the ceiling-six argument pin all of z, rather than merely the first
   Lmax stratum?
3. Is the cover-polytope reduction in PXC104d complete, including eta-zero and
   all boundary supports?
4. Do the three displayed reduced selectors follow from the retained rows at
   every later Lmax stage?
5. Does the zero common kernel use precisely the active Cx, cover, efficiency,
   and nonnegativity constraints required by PXC92b?
6. Is either cross-blocking row secretly forced zero under a different valid
   definition of qualifying cover?
7. Are empty/grand/singleton or redundant rows being improperly counted in the
   complete-Cx or cover quantifiers?
8. Does this genuinely refute only the universal forced-zero characterization,
   while leaving PXC103's common-direction iff intact?
9. Is this cross-cover cycle already a named phenomenon in exact games,
   balanced collections, or oriented-matroid treatments of core selectors?
10. Does the affine lower-envelope formula in PXC105d cover all sixteen
    outsider traces, and do the endpoint minimizers legitimately interpolate
    through the entire interval?
11. Are `A=4` and `A=11/2` exactly the asserted boundary degeneracies, or is
    an additional selector/menu wall hidden inside the open chamber?
12. In PXC106, do internal exchanges inside a tied block create a common
    staged Lmax descent, or does nonpositivity plus zero block sum rule them
    out exactly as claimed?
13. Does the all-dimension specialization satisfy both strict cross-row slack
    inequalities for every `n>=6`, including the `n=6` endpoint case?
14. Is the PXC107 dichotomy genuinely exhaustive after quantifying over all
    later stages and all directions in each cover cone?
15. Does dotting a union-nonnegative direction with each positive cover
    identity really force vanishing on every support and therefore collapse
    the apparent cover-local third branch to the common-direction case?

## Scope and novelty discipline

PXC104 is one exact second mechanism, and PXC105 promotes it to the rational
family `4<A<11/2`; neither is a classification of all six-player failures nor
an all-dimension classification. PXC106 does give an all-dimension
cross-cover family by replacing the low outsiders with two nonempty blocks;
it does not prove that these are the only obstruction graphs. The literature search for
PXC101--PXC103 did not locate this sparse-fidelity problem, but that negative
search is not proof of novelty. The 2026-08-22 follow-up explicitly checked
Reijnierse--Derks's prior `exact cover`, Lohmann--Borm--Herings's minimal exact
balanced collections, and Arin--Kuipers--Vermeulen's lexmax/large-core
solution. None of those located sources states the staged cover-dependency
obstruction, but a cooperative-game specialist must still check terminology,
unpublished work, and prior art before any novelty claim.
