# PXC101 forced-zero-blocker family and classification program

Status: theorem checkpoint, 2026-08-22. The conventional family theorem is
`PXC101--PXC103` in `divergence.tex`. It strengthens the isolated PXC98
counterexample to a positive-dimensional rational chamber in every dimension
`n>=6` and gives an exact criterion for the common-direction version of the
forced-zero mechanism.

## Frozen object class

- exact singleton-normalized TU games;
- exactly two Lmax-top players `r,h`;
- a fixed complete proper-row Lmin certificate `Cx`;
- normalized extreme covers of original z-tight proper rows, with positive
  support weights and positive coefficients on both top players;
- selector fidelity tested at every later Lmax stratum, not only the first
  ceiling.

The strong statement is universal over fixed complete `Cx`; the weak statement
may choose `Cx`. PXC101 refutes both because its complete certificate is unique.

## The parametric chamber

For `k=n-4>=2`, let `O={j,o1,...,o_(k-1)}` and choose rational

```text
M>q>J>K>0,
q+(k-1)K>=M,
(k+2)q+(k-1)K>(2k+1)J.
```

Use total `T=2M+2q+J+(k-1)K` and the four lower-envelope rows

```text
rha  >= 2M+q
rhb  >= 2M+q
rj   >= M+J
rhO  >= 2M+J+(k-1)K.
```

Then

```text
u=(q+J+(k-1)K)/(k+1)
p=(T-(k+2)u)/2
Lmin=(p,p,u^(k+2))
Lmax=(M,M,q,q,J,K^(k-1)).
```

The proper x-tight pool is exactly `{rha,rhb}`, and both rows are
indispensable. The proper z-tight menu is exactly
`{rh,rha,rhb,rj,rhO}`. Every normalized top cover lies on

```text
A_rha=A_rhb=A_rhO=eta,
A_rj=0,
2 A_rh + 4 eta = 1.
```

Thus its two extreme supports are `{rh}` and `{rha,rhb,rhO}`. Both omit `rj`
and replace `(J,K^(k-1))` by its uniform average. The integer specialization
`(M,q,J,K)=(4,3,2,1)` gives one explicit game for every `n>=6` with total
`T=n+11`; this is not null-player padding.

## Structural theorem and its boundary

Let `U_z` be the union of all rows that appear positively in some qualifying
extreme cover. A fixed later-stage descent direction is tangent to every
`Cx union R` lift if and only if it respects the common `Cx`/zero normals and
vanishes on every row in `U_z`. Full-game Lmax optimality then forces a
z-tight blocker outside `U_z`; by definition it has coefficient zero in every
top cover.

This is an iff characterization of **common-direction** failure, not of
arbitrary all-cover failure. PXC104 shows sharply that distinct covers can
leave distinct descent directions. PXC107 replaces the false universal
promotion by the exact common-direction/cross-cover-cycle dichotomy.

## Hard no-go ledger

- Full outsider-rank positive covers are faithful by PXC97c; they cannot
  generate this failure.
- First-ceiling certificates alone are insufficient; PXC92b later-stage
  tangents are mandatory.
- Null-player extension is not accepted as the dimension theorem because it
  changes the sparse-lift incidence and can create zero-coordinate normals.
- PXC101 gives a genuine growing outsider block and keeps every payoff in the
  displayed full-game selector positive.
- A generic one-row blocker pivot into a positive cover is false: a transverse
  blocker can be forced to coefficient zero by outsider balance.
- The second pinned six-player generator control has five failing covers and
  a common blocker `0125`. It was useful evidence for the common branch, but
  PXC104 proves that common-direction universality is false.

## Verification graph

Primary:

```bash
python3 verifiers/divergence/verify_pxc101_forced_zero_family.py \
  --output verifiers/divergence/pxc101_forced_zero_family.json
```

This uses the project rational simplex, checks the generic normal-cone
classification, and recomputes every coalition minimum, both selectors, every
complete Cx subset, every extreme cover, and both reduced lifts at `n=6,7,8`.

Independent:

```bash
python3 verifiers/divergence/verify_pxc101_forced_zero_family_independent.py \
  --output verifiers/divergence/pxc101_forced_zero_family_independent.json
```

This imports no project LP, game, selector, cover, or family code. It uses a
rational active-set implementation for the six-player anchor and independently
checks the dimension-free formulas through `n=44`.

Calibration requirements:

- `k=2` reproduces PXC98 byte-for-byte at the selector/menu/cover level;
- PXC90 remains the faithful full-rank control in the existing release suite;
- the PXC101 primary and independent outputs regenerate byte-identically;
- paper release remains byte-identical across two builds.

## Dated literature audit

Search date: 2026-08-22. Primary-source searches covered exact games, exact
partition games, large cores, the exact-game facet cone, and leximin/leximax
core imputations. The nearest structural sources located were:

- Biswas, Parthasarathy, Potters and Voorneveld (1999), *Large Cores and
  Exactness*, DOI `10.1006/game.1998.0686`;
- Llerena and Mauri (2017), *On the existence of the Dutta--Ray's egalitarian
  solution*;
- Dietzenbacher and Yanovskaya (2020), *Antiduality in exact partition games*,
  DOI `10.1016/j.mathsocsci.2020.04.006`;
- Studeny and Kratochvil (2022), *Facets of the cone of exact games*,
  DOI `10.1007/s00186-022-00770-4`, arXiv `2103.02414`;
- Vazirani (2024), *Equitable Core Imputations via a New Adaptation of the
  Primal-Dual Framework*, arXiv `2402.11437`.
- Reijnierse and Derks (1998), *Note on the core of a collection of
  coalitions*, DOI `10.1007/s001820050084`, whose distinct prior notion of an
  `exact cover` prevents using that phrase as new terminology here;
- Lohmann, Borm and Herings (2012), *Minimal exact balancedness*, DOI
  `10.1016/j.mathsocsci.2012.01.002`, which classifies minimal exact balanced
  collections but does not state the staged selector-fidelity obstruction;
- Arin, Kuipers and Vermeulen (2003), *Some characterizations of egalitarian
  solutions on classes of TU-games*, DOI
  `10.1016/S0165-4896(03)00051-9`, for the prior lexmax/large-core solution.

No searched source states the sparse-cover fidelity problem, the forced-zero
later-blocker criterion, the cross-cover dependency cycle, or either
all-`n>=6` family. That is a dated negative
search result, not proof of novelty. A cooperative-game specialist must still
check terminology, unpublished work, and whether the construction is an
unrecognized reformulation of a known exact-game example.

The PXC112--PXC114 follow-up additionally checked lexicographically perturbed
multiparametric LP, oriented-matroid programming, and oriented-matroid linear
complementarity. Jones--Kerrigan--Maciejowski (2007) confirms that degenerate
critical-region descriptions need not be unique or facet-to-facet;
Fukuda--Terlaky (1992) treats complementary solutions and criss-cross pivots;
standard oriented-matroid-program cycles concern program pivots and
Euclideaness. None uses the selector-specific graph between distinct positive
cover circuits or states the descent-set inclusion potential. This remains a
negative search, not an expert novelty verdict.

## Live classification frontier

The third item in the original frontier has now been achieved.  PXC104 is an
exact six-player counterexample with three failing covers and no common
direction.  Its two positive-ambient covers cross-block one another: `rhaj`
cuts the descent left by `{rhb,rhj,rhak}` and belongs positively to
`{rhb,rhaj,rhk}`, while `rhak` cuts the reverse descent and belongs positively
to the first cover.  Thus no load-bearing blocker is forced zero in every
cover.  The exact game has unique complete `Cx={rha,rhb}`, so both Cx
quantifiers fail.

PXC105 upgrades this point to a positive-dimensional rational family.  For
every `4<A<11/2`, the six defining rows
`rha,rhb>=16`, `rhj,rhk>=13`, and `rhaj,rhak>=13+A`, at total `18+A`,
have

```text
Lmin = ((46-A)/6)^2, ((A+2)/3)^4
Lmax = (6,6,A,4,1,1).
```

The complete-Cx and cover triangle are constant throughout the chamber.  The
three reduced selectors are `(6,6,4,4,(A-2)/2,(A-2)/2)`,
`(6,6,4,4,1,A-3)`, and its outsider swap.  The endpoints are sharp for this
proof cell: the `a,b` strata merge at `A=4`, and the long cross rows become
x-tight at `A=11/2`.

PXC106 also completes the all-dimension cross-cover lift.  Split the low
outsiders into nonempty blocks `J,K` of sizes `p,q`.  The cover rows become
`rhb,rhJ,rhaK` and `rhb,rhaJ,rhK`; both partition the non-top players.
Under the explicit chamber inequalities in the manuscript, every complete-Cx
and cover statement survives.  The specialization
`p=1,q=n-5,A=4+1/(n-3)` supplies a non-null counterexample for every `n>=6`.

PXC107 supplies the exact obstruction dichotomy. Universal-cover failure is
equivalent to a nonempty staged descent cone for every extreme cover. A
common direction is the PXC103 case. Without one, every cover descent is cut
by a row in the cover-eligible union, and the resulting finite
cover-dependency digraph contains a directed cycle. A direction nonnegative
on the whole union would be forced to vanish on every cover by the positive
cover identities and would therefore be common; there is no third
cover-local forced-zero branch.

The revised frontier is:

1. Exhaust the minimal six-player incidence types modulo safe label symmetry,
   now allowing both forced-zero and cross-cover cycles.
2. Classify the minimal directed cycles and common-direction incidence types
   realizable at six players.
3. Classify which directed cover-blocker graphs are realizable by exact games;
   PXC106 supplies the two-cycle in every dimension.
4. Relate cover eligibility and cross-blocking to an oriented-matroid
   deletion/minor criterion.
5. Derive an algorithm deciding sparse fidelity from tight-menu incidence and
   staged polar data, with exact certificates.

The finite incidence driver finds the smallest abstract two-cover/no-common-ray
menu at five rows; exact realization requires six defining rows because one
Lmin row is z-slack.  The exactifier searched the symmetric two-row-Cx integer
cell through top payoff nine and found PXC104 after two faithful near-misses.
These searches explain discovery and minimality within their stated cells;
they are not a global six-player incidence classification.

## Exact-cone projection result (PXC109--PXC111)

The facet question is now resolved in both directions.

- For every fixed selector/active-menu/cover-graph signature, the realization
  locus is a relatively open rational polyhedral cone in `(v,x,z)`.  The
  fixed-`n` failure locus is a finite union of its projections to game-value
  space.  This is the correct parametric-LP interpretation of PXC108.
- If `N\T` is partitioned into nonempty blocks `B_i`, then
  `sum_i 1_(T union B_i) - (m-1)1_T = 1_N` is an indecomposable
  semi-balanced system.  The exceptional-set proof is dimension-free, so it
  defines a full exact-cone facet for every block size.
- The PXC101 positive cover plus the tight top pair is one such facet; the
  forced-zero blocker lies outside it.  The mechanism is a facet--blocker flag,
  not a facet characterization.
- The two PXC104 positive covers, completed with the top pair, are two
  catalogue-type-33 facets.  Each cross blocker belongs to the opposite facet,
  so the PXC108 two-cycle is exactly a minimal two-facet dependency cycle.
  PXC106 promotes this statement to every `n>=6` and every nonempty `J,K`.
- The unrestricted facet correspondence is false.  In PXC88 the unequal-top
  cover rows and its two indispensable blockers have augmented incidence rank
  six on six columns.  They contain no constant dependence and hence no
  semi-balanced subsystem.  This is the smallest certified unequal-top
  projection failure in the current record, not a proof of `n=7` minimality.

The exact six-player face computation gives codimension 54 for the generic
PXC101 anchor and codimension 53 for the PXC105 chamber.  Therefore the
selector mechanisms live well inside high-codimension exact faces; they are
not new exact-cone facets merely because their cover supports expose known
partition-star facets.

## Certificate fiber and descent-set potential (PXC112--PXC114)

The certificate-blind version of the proposed canonical obstruction graph is
false.  Add the row `rhaj>=13` to the total-17 PXC98 lower-envelope
presentation.  The resulting exact singleton-normalized six-player game keeps

    Lmin = (9/2,9/2,2,2,2,2)
    Lmax = (4,4,3,3,2,1),

but has three complete proper-row certificates:

    C1={rha,rhb}, C2={rhb,rhaj}, C3={rha,rhb,rhaj}.

The same two extreme top covers have faithful-cover sets respectively empty,
the positive-ambient cover alone, and both covers.  Thus one fixed game and
selector pair realizes the universal common-blocker branch, a mixed
cover-dependent branch, or no failure according to the retained complete
certificate.  The independent verifier exhausts all eight subsets of the
full x-tight menu, both extreme covers, every reduced selector, and explicit
bad directions.

The strongest canonical replacement is the finite certificate fiber.
We call certificates equivalent when they generate the same staged tangent
cones at both selectors.  Equivalent certificates remain equivalent
after intersecting with any fixed active cover rows, so they have the same
candidate-selector fidelity outcomes, PXC92b descent sets, and PXC108 graph.
The local quotient does not claim equality of the eventual altered selector
when fidelity fails, and it is not claimed to be the coarsest possible
graph-preserving quotient.  In extended
`(v,x,z)` space, the exact/core/efficiency cone cut by the central
active-menu, payoff-order, zero-coordinate, and common-tight hyperplanes gives
a finite rational fan.  Discarding faces on which `x,z` are not the claimed
selectors leaves a canonical union-of-open-faces stratification on which the
complete tangent-cone classes, extreme covers, and graph fiber are constant.
The surviving cells need not form a subfan.  Projection to game space is
therefore finite polyhedral but not single-valued unless this discrete fiber
is retained.

On the strict residual arm with no active common-Cx normals, PXC113 gives a
dimension-free theorem.  For a positive balanced outsider matrix A and
K=ker(A^T), the polar of the lex-negative half of K is
col(A)+R_{<=0}e_p, where p is the first free coordinate.  Positivity of the
balancing weights then proves

    A -> B and not(B -> A)  implies  col(A) proper-subset col(B).

Outsider rank is consequently a strict potential on asymmetric edges.  Every
directed cycle contains a reciprocal pair, so every shortest cyclic
obstruction in this arm has length two.  For partition covers, an edge occurs
exactly when the target partition splits a source block; one-way edges are
strict refinements and reciprocal edges are incomparable partition pairs.
This identifies the PXC104--PXC106 cross-cover pattern as the primitive
partition generator without claiming novelty for the partition-star facets.

Exact audits enumerate all positive independent rank-deficient 0/1 supports
through five outsiders and all partition pairs through six outsiders.  The
u=5 graph has 315 supports, 89,610 edges, and 4,600 asymmetric edges, all
strictly rank-increasing.  An independently formulated Z3/Fraction audit
reconstructs the complete u=4 graph.

PXC114 closes the first two items and supplies the dimension-free
decomposition.  If R' has no edge to R, positivity of the R-cover identity
forces every R-row derivative to vanish on every direction in D(R').  All
other tangent and stage conditions are common inside the certificate fiber,
so D(R') is contained in D(R).  A one-way edge makes this inclusion strict.
Consequently an asymmetric-only cycle is impossible even with payoff ties,
active common-Cx inequalities, zero-coordinate normals, or eta-zero covers.
Combined with PXC107, universal failure is generated at the mechanism level
by either a common descent and outside-union blocker or a reciprocal two-cover
cycle.

The remaining frontier is representational rather than graph-theoretic:

1. determine whether the two mechanism types admit a useful oriented-matroid
   minor operation beyond the proved circuit--covector coupling;
2. classify deletion-minimal coalition-incidence realizations inside each
   mechanism, without confusing that optional refinement with the now-proved
   all-dimension decomposition;
3. complete specialist novelty review of the fibered-selector fan and
   descent-set potential terminology.

The active-Cx size-three search remains discovery provenance.  Its 576-cell
null result motivated PXC114 but is not needed as theorem evidence.
