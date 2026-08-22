# Hostile external review packet — invariant sparse-fidelity circuits

Reviewed base: `7dcf839da0af52b9f8f19257366ea0cf6ad597ec`.
Repaired checkpoint: current head of `codex/pxc107-canonical-circuits`.
Review PXC101--PXC108 in
`paper5/divergence.tex`. Do not treat verifier output as proof of the general
theorem.

## Claimed result

Fix an exact singleton-normalized game, its selected points `x=Lmin(v)` and
`z=Lmax(v)`, exactly two Lmax-top players, a fixed complete proper-row `Cx`,
and the finite set `B` of qualifying extreme normalized top covers. For each
cover `R`, let `D_R` be the union of all exact PXC92b later-stage descent cones
for the `Cx union R` lift.

Define the invariant graph

```text
R -> R'  iff  some d in D_R and some Q in R' satisfy d(Q)<0.
```

The claims are:

1. Every cover lift fails iff every `D_R` is nonempty.
2. If `intersection_R D_R` is nonempty, a full-game z-tight blocker lies
   outside the union of every cover support and therefore has coefficient zero
   in every top cover (PXC101/PXC103 branch).
3. If the intersection is empty, the invariant graph has positive outdegree
   at every vertex and no loops. It therefore has a directed cycle; every
   shortest directed cycle is chordless. PXC104 is the minimal two-cycle.
4. If `eta>0`, an extreme cover's non-top incidence columns are independent,
   so its support is at most `n-2`. Support `n-2` pins the entire non-top face
   and is faithful at every later Lmax stage; a failing positive-ambient cover
   therefore has support at most `n-3`. The only eta-zero support in the stated
   singleton-normalized two-top setting is the tight top pair.
5. After eliminating the two top coefficients, append the ambient column when
   positive and the distinguished normalization target. Each extreme cover
   support becomes a represented oriented-matroid circuit. A blocker direction
   is a covector sign pattern. The entire obstruction cycle is not claimed to
   be one larger circuit, an indecomposable semi-balanced system, or an
   exact-cone facet.
6. Exact recognition follows by enumerating covers and solving rational staged
   tangent LPs for cover failure, a union-common direction, and each ordered
   cover/target-row edge, followed by shortest-cycle search.

The graph is invariant, but a symmetric graph may have several shortest
cycles. “Deletion-minimal” refers to the displayed common or cyclic
certificate, not to arbitrarily deleting genuine extreme covers from the
original quantified problem.

## Conventional proof obligations

The reviewer should independently check:

- Positive cover weights plus efficiency and fixed earlier/top strata force
  every supported row derivative to zero, not merely nonnegative.
- If an `R`-descent is nonnegative on the union of all cover supports, dotting
  it with every normalized cover identity forces it to vanish on every
  support, hence makes it common to all lifts.
- A full-game Lmax blocker for a local descent may be chosen z-tight; inactive
  inequalities impose no infinitesimal restriction.
- The invariant graph has no self-loop and positive outdegree in the
  no-common universal-failure branch.
- A shortest directed cycle is induced/chordless in the directed sense used in
  the manuscript.
- For `eta>0`, `1_U` lies in `col(A_R)`; extremality plus the one normalization
  row really forces `rank(A_R)=|R|`. Check degeneracy and the derived top-alpha
  inequalities carefully.
- Full outsider rank kills every later-stage direction, including unequal and
  zero lower strata.
- In the eta-zero argument, positive row weights and nonnegative incidence
  force all supported rows to omit non-top players, and singleton
  normalization excludes top singletons with positive Lmax payoff.
- The active augmented cover columns are independent and represent the target
  with all nonzero coefficients, so adjoining the negative target is genuinely
  a minimally dependent signed set.
- The recognition LPs include active common-Cx inequalities, active
  nonnegativity normals, all earlier coordinate pins, every later stratum, and
  every designated player.

## Repairs to PXC105--PXC106

PXC105 now prints explicit feasible endpoint minimizers for all sixteen
`rh union U` traces at both `A=4` and `A=11/2`. Affine interpolation gives an
attaining allocation throughout `4<A<11/2`; both primary and independent
verifiers emit the points. Explicit marginal coalitions prove every player is
non-null.

PXC106 now gives a dimension-free minimizer. For a proper trace `U`, put its
claimed value `L` on `r`, zero every selected non-top coordinate, put `A` on
omitted `a`, put `(16-L)_+` on omitted `b`, and concentrate each non-full
block's maximum row deficit on one omitted member. The displayed case bound
shows used mass is at most the total; unused mass goes to any omitted
coordinate. The independent verifier tests the recipe on 7,415 trace classes
over a rational `p,q,A` grid. Completing block `J` at player `i` raises the
coalition value by `p>0` (and analogously by `q` in `K`), so cloned players are
not null.

## Exact artifacts and reproduction

From `coopgames/`:

```bash
"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc108_invariant_cover_blocker_circuits.py \
  --output /tmp/pxc108.json
cmp verifiers/divergence/pxc108_invariant_cover_blocker_circuits.json \
  /tmp/pxc108.json

"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc108_invariant_cover_blocker_circuits_independent.py \
  --output /tmp/pxc108-independent.json
cmp verifiers/divergence/pxc108_invariant_cover_blocker_circuits_independent.json \
  /tmp/pxc108-independent.json

"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc105_cross_cover_family.py \
  --output /tmp/pxc105.json
cmp verifiers/divergence/pxc105_cross_cover_family.json /tmp/pxc105.json

"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc105_cross_cover_family_independent.py \
  --output /tmp/pxc105-independent.json
cmp verifiers/divergence/pxc105_cross_cover_family_independent.json \
  /tmp/pxc105-independent.json

"${PAPER5_PYTHON}" verifiers/divergence/verify_pxc106_cross_cover_dimension_lift_independent.py \
  --output /tmp/pxc106-independent.json
cmp verifiers/divergence/pxc106_cross_cover_dimension_lift_independent.json \
  /tmp/pxc106-independent.json
```

The primary PXC108 recognizer uses the project exact rational LP engine. The
independent verifier uses standalone `Fraction` row reduction and imports no
project LP, selector, cover, graph, PXC107, or PXC108 implementation. It checks
the common blocker, two-cycle, cover circuits, and PXC90 full-rank control,
but the symbolic theorem remains a human proof.

## Six-player classification boundary

Discovery artifacts, not global theorem evidence:

- `search_archive/pxc108_both_top_complete.json` exhausts all
  `8*(2^15-1)` ordered-stratum/menu cells when every row contains both tops,
  no active Cx trace is present, and all outsider traces are nonempty. It finds
  29,420 cyclic universal-failure cells, all with a two-cycle, and 13,020
  common-by-sink cells.
- `search_archive/pxc108_general_n6_cycles.json` includes all 766
  nonsingleton extreme covers and arbitrary top decorations for strict positive
  outsider strata. Among the 98 potentially failing support-at-most-three
  covers, the complete 367-edge asymmetric subgraph is a DAG. Consequently
  every cycle in this scoped incidence graph contains a reciprocal two-cycle.
  A 50,000-union exact-cover-closed probe found 10,445 two-cycle controls and
  no longer pure cycle.

These do not jointly exhaust active common-Cx inequalities, zero-coordinate
normals, every outsider stratum shape under mixed decorations, comparison
with x, singleton witnesses, or exact-game realizability. Do not call them a
complete six-player exact-game classification.

## Prior-art comparison to check

| Source | Established object | Current distinction |
|---|---|---|
| Reijnierse--Derks (1998), “Note on the core of a collection of coalitions” | Exact covers and coalition collections with one-point core | No ordered Lmax stages, fixed Cx, or two selected core points |
| Lohmann--Borm--Herings (2012), “Minimal exact balancedness” | Minimal exact balanced collections; one exceptional negative weight; three generation types | The augmented top-cover circuit is positive with a distinguished ambient/normalization column and is not identified with those types |
| Studený--Kratochvíl (2022), “Facets of the cone of exact games” | Indecomposable semi-balanced systems correspond to exact-cone facets | PXC108 is selector-cell dependent; facet status requires a separate projection and indecomposability test |
| Björner--Las Vergnas--Sturmfels--White--Ziegler (1999), *Oriented Matroids* | Standard circuits, covectors, cocircuits, and oriented-matroid programming | Circuit/covector language is prior art; only the selector-specific cover--blocker coupling could be new |

Relevant links:

- <https://doi.org/10.1007/s001820050084>
- <https://doi.org/10.1016/j.mathsocsci.2012.01.002>
- <https://doi.org/10.1007/s00186-022-00770-4>
- <https://doi.org/10.1017/CBO9780511586507>

## Hostile questions

1. Is PXC108 stronger than PXC107 mathematically, or only a cleaner invariant
   repackaging of the same finite outdegree argument?
2. Does “canonical circuit representation” overstate nonuniqueness of shortest
   cycles or the fact that the whole obstruction is not one matroid circuit?
3. Can a descent be in each union `D_R` at incompatible stages, invalidating
   the common-direction intersection argument?
4. Does any active zero-coordinate normal or common-Cx inequality invalidate
   the cover-row equality step?
5. Are the support/rank bounds valid for degenerate cover vertices or when a
   top-alpha inequality is active?
6. Is the eta-zero uniqueness argument complete when zero-valued outsider
   singleton rows are allowed in a dual representation?
7. Does every invariant edge admit the simultaneous homogeneous normalization
   `d_i<=-1` and `d(Q)<=-1` used by the recognizer?
8. Does the shortest-cycle chord argument use the correct directed notion of
   chord?
9. Is there a known name—basis-exchange graph, circuit pivot graph,
   complementary-slackness cycle, oriented-matroid program cycle, or otherwise—
   for exactly this cover-dependent blocker mechanism?
10. Can the entire obstruction be projected to one indecomposable
    semi-balanced system, contradicting the manuscript's negative statement?
11. Do the 32 PXC105 points satisfy every defining row and attain the correct
    trace objectives at both endpoints?
12. Is the PXC106 mass-budget inequality correct in every `p,q,A` chamber,
    including partial block traces and the all-but-one-player cases?
13. Do the displayed marginal coalitions really establish non-nullness under
    the lower-envelope formula?
14. Can mixed top decorations, active Cx, or zero normals produce a genuine
    three-cycle at six players despite the two scoped negative searches?
15. What is the strongest publication-level significance justified here:
    structural mechanism theorem, exact recognition lemma, or primarily a
    formalization of complementary slackness plus a finite graph cycle?

## Restrained significance statement

Correctness would give a useful structural and algorithmic theorem for this
sparse-fidelity problem: it replaces an arbitrary witness graph by an
invariant exact object, proves a common/cyclic obstruction alternative, gives
sharp rank support gates, and isolates the precise oriented-matroid interface.
It is not by itself a major field breakthrough. The finite-cycle step is
elementary once the cover collapse lemma is known, and the circuit terminology
is standard. A larger result would require either a full six-player incidence/
exactness classification, a dimension-free restriction on possible cycle
types, or a genuine projection theorem connecting these selector obstructions
to new exact-cone facets.
