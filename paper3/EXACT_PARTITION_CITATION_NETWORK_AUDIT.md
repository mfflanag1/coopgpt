# Citation-network audit — exact partition games and the Lmin phase theorem

## Bottom line

Search date: 2026-08-04.

The citation network of Llerena and Mauri (2017), *On the existence of the
Dutta--Ray's egalitarian solution*, contains important prior art on exact
partition games, the equal split-off set, antiduality, consistency,
nontransferable-utility extensions, and PES stability.  It also contains one
low-dimensional fact that must be stated prominently:

> Dietzenbacher (2021) proved that exact games with at most four players are
> PES stable.

That is not the theorem proved in the present draft.  The new draft proves the
strictly sharper structural assertion that every exact game with at most four
players is **exact partition at its Lmin allocation**, and derives it from a
dimension-free balanced-trace transport obstruction.  It then classifies all
possible cardinalities on the two sides of a slack strict Lmin boundary by the
sharp staircase

```text
m_min(1)=4,  m_min(2)=m_min(3)=3,  m_min(h)=2 for h>=4.
```

No equivalent statement, proof mechanism, staircase, or universal
indecomposable witness family was found in this citation audit.  This is
evidence of apparent novelty, not proof of novelty.  One directly relevant
2023 paper is closed access, bibliographic databases are incomplete, and a
specialist must still check terminology and uncited antecedents.

The subsequent Lmin uncrossing theorem adds a different dimension-free
claim: supermodularity restricted only to pairs of coalitions tight at Lmin
forces exact partition, while every failure produces a crossing tight pair
with a strict local supermodularity defect.  Focused searches on 2026-08-04
for combinations of `exact partition game`, `Lmin`, `tight coalitions`,
`supermodular`, `uncrossing`, and `laminar` found the established convex-game
domain and standard egalitarian-solution literature, but no local-at-Lmin
statement.  This is preliminary negative evidence only.

## Reproducible citation query

The 2017 paper has DOI
[`10.1016/j.mathsocsci.2017.07.002`](https://doi.org/10.1016/j.mathsocsci.2017.07.002)
and OpenAlex work ID [`W2737075353`](https://openalex.org/W2737075353).  On the
search date, the following query returned 12 citing records:

```text
https://api.openalex.org/works?filter=cites:W2737075353&per-page=200
```

Those records represent 11 distinct intellectual works because the discrete
side-payment paper appears once as an arXiv record and once as its journal
version.  The count is a database snapshot, not an exhaustive citation count.

## Citation-network triage

| Year | Citing work | Inspection | Relevance to the new theorem |
|---:|---|---|---|
| 2020/21 | Dietzenbacher and Yanovskaya, [*Consistency of the equal split-off set*](https://doi.org/10.1007/s00182-020-00713-5) | Full text | Defines and axiomatizes the ESOS on exact-partition and arbitrary games; no boundary-cardinality classification found. |
| 2020 | Dietzenbacher and Yanovskaya, [*Antiduality in exact partition games*](https://doi.org/10.1016/j.mathsocsci.2020.04.006) | Full text | Proves antidual closure and self-antidual solution results; no dimensional threshold or transport theorem found. |
| 2021 | Dietzenbacher and Yanovskaya, [*Self-antidual extensions and subsolutions*](https://doi.org/10.1016/j.mathsocsci.2021.08.004) | Metadata/abstract and citation context | Concerns self-antidual extensions and subsolutions; no matching phase theorem visible. |
| 2022/23 | Dietzenbacher and Peters, [*The equal split-off set for NTU-games*](https://doi.org/10.1016/j.mathsocsci.2022.10.004) | Full text | Generalizes exact partition and ESOS to NTU games; no player-cardinality threshold found. |
| 2019 | Calleja, Llerena, and Sudhölter, [*Welfare Egalitarianism in Surplus-Sharing Problems and Convex Games*](https://doi.org/10.2139/ssrn.3355484) | Full text | Axiomatic work on welfare egalitarianism and convex games; no exact-game boundary theorem found. |
| 2020/21 | Otsuka, [*Egalitarian solution for games with discrete side payment*](https://doi.org/10.15807/jorsj.64.87) | Full text; arXiv and journal records deduplicated | Studies integral payoffs, M-convexity, and Lorenz-stable sets; no exact-partition phase theorem found. |
| 2021 | Calleja, Llerena, and Sudhölter, [*Axiomatizations of Dutta--Ray's egalitarian solution on the domain of convex games*](https://doi.org/10.1016/j.jmateco.2021.102477) | Full text | Axiomatizes the solution on convex games; no exact-game threshold found. |
| 2023 | Yanovskaya, [*Rich Extensions of the Core and the Equal Split Off Set*](https://doi.org/10.1142/S0219198923500056) | Abstract only; full text closed | Directly relevant to ESOS, rich cores, Lorenz-undominated allocations, and Lmax.  The abstract reports a bound on the number of allocations, not the present boundary theorem; full-text review remains an explicit gap. |
| 2025 | Pisch, [*A New Algorithm for Constructing a Characteristic Function*](https://doi.org/10.1007/s10614-025-10883-7) | Full text | Applied characteristic-function construction; the citation is not used for a comparable exact-partition result. |
| 2025 | *Aufgaben und Lösungen* | Metadata only | A book exercise/solution record; no relevant theorem identified. |
| 2025 | Dietzenbacher, [*Population monotonicity and egalitarianism*](https://doi.org/10.1007/s00182-025-00966-y) | Full text | Most relevant later synthesis.  It records exact `n<=4` PES stability and characterizes total exact-partition games via total PES stability, but does not state the Lmin exact-partition classification or staircase. |

## Claim-by-claim novelty matrix

| Claim or ingredient | Status after audit | Treatment in the paper |
|---|---|---|
| Exact-partition condition | Established prior art (Llerena--Mauri 2017) | Cite; do not rename or claim. |
| Lorenz/Dutta--Ray consequence of exact partition | Established prior art | Cite; do not claim. |
| ESOS/core intersection characterization and consistency | Established prior art | Cite Dietzenbacher--Yanovskaya. |
| Antiduality and self-antiduality theory | Established prior art | Cite; distinguish from the present obstruction. |
| Property-I characterization of Lmax, and its antidual Lmin form | Established prior art (Arin--Kuipers--Vermeulen 2008; Mauri 2018) | Cite prominently; do not claim the qualitative tight-coalition criterion. |
| Exact games with at most four players are PES stable | Established prior art (Dietzenbacher 2021) | State as the closest known low-dimensional result. |
| Every exact game with at most four players is exact partition at Lmin | Not found | Present as apparent new strengthening, pending specialist review. |
| Hierarchical dual covers plus exact-face witnesses yield balanced-trace transport | Not found | Present as the apparent new proof mechanism, pending terminology review. |
| The exact-face overload specialization unifies the unique-richest packing budget and trace roundings | Not found; the inequality follows directly from the paper's boundary-cover form of published exact balancedness | Present the unification and structural use as candidate new, not the underlying inequality or exactness characterization. |
| Exact singleton faces forbid safe rooted integer fibres of tight trace semigroups | Not found; affine-semigroup, normality, and Hilbert-basis theory are classical | Present only the bridge to exact-game tight packets as a candidate new general mechanism, pending specialist review. |
| Positive Lehman dual rows become forbidden rooted trace covers; the two-poor-label density test links odd cycles and projective planes | Lehman pairs and their role as cores of minimally nonideal matrices are classical (Cornuéjols--Guenin--Tunçel 2009) | Cite the classical identity prominently; claim only the exact-game bridge and labeled density exclusion as candidate new. |
| The two-sided Lehman residual and subset face budget unify singleton row exclusions with canonical internal-face amplification | Not found; this is an algebraic exact-face application of the classical Lehman identity | Present as a candidate new recursive invariant, not as an extension of Lehman's structural theorem, pending specialist review. |
| The label residual obeys `A^T F=k[(r-p)1_V-(r-ell)1_U]`, so every label-free trace has zero total residual | Not found; it is an algebraic consequence of the classical transpose Lehman identity | Claim only the labeled residual formulation and its exact-game use, not the underlying matrix identity. |
| Every three columns of a positive Lehman dual have a row meeting exactly one; hence every labeled packet with at most three gaining columns is excluded | Not found; the transpose Lehman identity and regularity are classical | Present the capacity-parity deduction and exact-game residual application as candidate new, pending a Lehman-matrix specialist search. |
| Every thin four-gaining-label survivor has overlap at most one and one of six local neutral-trace load tiles | Not found; odd-multiplier parity and the transpose Lehman identity are classical ingredients | Present as a candidate structural reduction, not as an exclusion or classification of Lehman matrices. |
| In the thin four-label survivor, all three-losing-label rows have disjoint primal supports and every four-label-simple row forces at least `r-5` `(1,3)`--`(3,0)` neutral traces | Not found; the Lehman triple-intersection property is classical | Claim only the labeled packing and forced-star consequence, not the underlying intersection bound; do not call it a global exclusion. |
| All heavy losing-label rows in the thin four-label survivor form exactly one canonical dual column; consequently no dual-cubic thin core survives | Not found; regularity, nonsingularity, and the Lehman identities are classical | Present the majority-column identification and dual-cubic exclusion as candidate new labeled consequences, pending specialist review. |
| Every two-poorer failure forces a nonintegral active trace polytope/odd trace cycle | Not found; Berge's matrix-integrality theorem is classical | Present only as a new bridge from Lmin geometry to known balanced-matrix theory. |
| Every two-poorer underloaded packet has a proper trace of size at least three | Not found; half-integrality of graph exact covers is standard | Present as a candidate exact-game bridge; clarify that multiple odd cycles require the real overload budget, not an integer fibre. |
| At `|H|=4`, every two-poorer failure has the four-co-singleton `1/3` vertex | Not found; four-row exact-cover classification is elementary | Present as a candidate first-obstruction uniqueness theorem, pending specialist review. |
| Projective-plane trace packets obey overlap-sensitive density and local `A setminus B` barriers; a two-sided convex Lehman-row theorem excludes them in every finite order without a Desarguesian assumption | Not found; positive Lehman identities and the simple-point incidence count are classical | Present only the exact-face interpolation and realization exclusion as candidate new, pending finite-geometry and game-theory specialist review. |
| Complete boundary staircase `4,3,3,2` | Not found | Present as apparent new classification. |
| Universal indecomposable family for every `m>=3,h>=2` | Not found | Present as apparent new sharpness construction. |
| Closed-form Lmax and distance `4h/(h+1)` for that family | Not found | Present as an additional explicit result, not the core novelty claim. |
| Supermodularity only on Lmin-tight pairs forces exact partition; every failure has a minimum-energy crossing pair with positive uncrossing defect | Not found; uncrossing and convex-game egalitarian results are classical | Present the local-at-Lmin domain and converse defect as candidate new; do not claim uncrossing, supermodularity, or the convex-game consequence themselves. |
| Along an integral uncrossing, signed local supermodularity defects telescope exactly to final weighted core slack and quantitatively bound target-face slack | Not found; slack telescoping and uncrossing energy are elementary/classical mechanisms | Present the exact-face defect budget as a candidate new bridge, not a new uncrossing identity, pending submodular-optimization and exact-game review. |
| Every nontrivial payoff-oriented broken tight diamond needs five players in a singleton-normalized exact game, and both minimal four-cell shapes admit one binary lower-envelope realization | Not found; tight-set lattices, lower envelopes of core polytopes, and uncrossing are classical | Present the sharp capacity argument and universal realization as a candidate structural explanation of the four/five threshold, pending exact-game and lattice-specialist review. |
| Every two-column strict Lmin failure has meet exactly equal to the failed suffix and obeys the exterior-slack budget `s_phi(H)<=s_phi(R)`; the arbitrary-level lower-envelope converse is sharp | Not found; the incidence identity is an elementary exact-balanced collection | Present the normal form, its Lmin interpretation, and sharp converse as the candidate contribution; do not claim the underlying exact-balanced identity as new. |
| The minimum poorer-side coalition-slack cost of completing a strict Lmin cover's deficit bounds target slack; zero completion cost is equivalent to membership in the poorer tight-set cone; the support-two and support-three families saturate the bound | The incidence identity and inequality are established semi-balanced/exact-balanced theory (Studený--Kratochvíl 2022; Lohmann--Borm--Herings 2012). The Lmin-selected restricted functional and equality-case unification were not found. | Claim only the Lmin selection, minimum-cost invariant, cone criterion, and unification of equality cases as candidates; explicitly attribute the semi-balanced inequality and standard covering LP. |
| Every rooted Lmin relation is linearly equivalent to a coupling of a uniform rich-trace cover and a singleton-completed uniform poor-trace cover, with exceptional coefficient `gamma=alpha-beta+tau`; support-minimal relations become extreme coupling rays | Not found as a named Lmin obstruction cone; the coordinate restriction and general polyhedral extreme-ray correspondence are elementary | Present the normal form as a structural reduction, not a difficult standalone theorem.  Claim broader significance only if the resulting coupling rays receive a nontrivial classification or forbidden-minor theorem. |
| Every slack Lmin boundary selects either a pure block star or one rooted circuit whose non-spoke rich traces are exactly a single minimal balanced collection; the convex canonical excess `delta(r)` eliminates mixtures | Not found in the inspected exact-partition, egalitarian-core, or minimal-balanced-system literature; exact-cover extreme-point decomposition and Jensen's inequality are classical | Present the Lmin-specific pruning, canonical rooted completion, and single-packet reduction as the candidate contribution.  Require hostile review of repeated-trace degeneracies and a specialist search before calling it a new general theory. |
| Every slack richer Lmin suffix in every exact game has a one-player extension with strictly larger slack, equivalently a strict marginal deficit on an adjacent coalition-lattice edge; with two poorer players a selected packet gives factor `(1-r_a)/(r_b-r_a)>1` | Not found; the semi-balanced inequality is classical, but the simultaneous strict cover from Lmin and its universal canonical completion were not found as a slack-ascent theorem | Present the dimension-free universal ascent and local-witness theorem as candidate new content, applying to both star and trace branches; require hostile review of the exact-balancedness orientation and a search for equivalent exact-game or egalitarian slack-gradient results. |
| For every compact convex efficient allocation set, interval face deficits equal maximum positive variation on the complementary coordinates; at a strict leximin boundary a positive root deficit forces a strictly larger one-player extension, and all interval maximizers/exactifiers are classified by sign cells | The positive-variation equality is an elementary support-function calculation.  A focused search found adjacent leximin/dec-min theory and the classical coincidence of inc-max and dec-min on (contra-)polymatroid base polyhedra, but no equivalent cover-free face-ascent or sign-cell theorem. | Do not claim a new support-function identity. Present the segment argument, terminal sign-cell correspondence, and exact-game bridge as candidate contributions only; require convex-optimization and polymatroid specialist review. |
| Maximizing slack on the Boolean interval above any failed Lmin suffix produces a proper payoff-inverted punctured suffix; every exactifier weakly lowers its included poorer players, weakly raises its excluded poorer players, obeys a deficit-weighted transport budget, and satisfies `q_E s_phi(C)<=sum_D q_d s_phi({d})` | Not found in the inspected exact-partition thesis/paper, exact-cone facet paper, or citation network. Interval neighbor signs are elementary once the maximizer is chosen; the Lmin-selected terminal cut, strict-cover budget, and forced payoff inversion are the candidate contribution. | Present as a structural corollary of universal ascent plus exactness, not as a new exact-balancedness inequality. Require hostile review of the tied-stratum leximin argument and specialist terminology search. |

## Why the known four-player theorem does not subsume this one

PES stability is a solution-stability property.  Exact partition at Lmin is a
coalitional tightness property: every cumulative richer block of the ordered
Lmin payoff partition attains its worth at Lmin.  Published work establishes
that exact-partition games are PES stable, but the converse is false in
general.  Therefore the known implication

```text
exact and n<=4  =>  PES stable
```

does not by itself yield

```text
exact and n<=4  =>  exact partition at Lmin.
```

The draft supplies the second implication directly and explains the sharp
failure pattern beyond four players.  This logical distinction should remain
explicit in the abstract, introduction, theorem discussion, and reviewer
packet.

## Search terms and adjacent terminology

Full-text and metadata searches included combinations of:

```text
exact partition; exact game; at most four players; five players
PES stable; procedural egalitarian solution; equal split-off set
Lmin; Lmax; Lorenz maximal; ordered payoff partition
richer players; poorer players; rich coalition; rich core
minimal balanced collection; exact balancedness; balanced hypergraph
transport; trace; normal cone; Kohlberg criterion
terminal slack coalition; slack maximizer; punctured suffix; payoff inversion
adjacent marginal deficit; exactifying displacement; singleton sacrifice budget
dimension; cardinality; indecomposable; replication
balanced matrix; set partitioning; active trace; odd cycle
property I; hierarchical tight-coalition criterion; complement-tight coalition
fractional matching; rank-two trace; graph exact cover; odd-cycle rounding
inc-max; dec-min; base polyhedron; polymatroid; contra-polymatroid
support function; positive variation; subset-sum polytope
uncrossing tight coalitions; laminar core constraints; local supermodularity
supermodular only on binding coalitions; lattice of tight coalitions
```

The full texts inspected include Arin--Kuipers--Vermeulen (2008), Definition 3
and Lemma 1, and Mauri's 2018 thesis, Definitions 11--12 and Lemma 3. They
establish the qualitative property-I criterion but do not state the
simultaneous strict cover, the active-trace polytope, or the odd-cycle
necessity theorem. The other full texts inspected were the consistency, antiduality, NTU,
population-monotonicity, convex-game axiomatization, welfare-egalitarianism,
discrete-side-payment, and characteristic-function papers listed above.
The exact-partition section of Mauri's thesis was re-inspected specifically
for terminal coalitions, slack maxima, marginal-deficit edges, sign-separated
exactifiers, and sacrifice budgets.  It gives the ordered-partition
definition, marginal-game construction, and Lorenz argument, but no matching
terminal-cut statement was located.  Studený--Kratochvíl's full-text exact-cone
paper was also searched for `slack`, `terminal`, `leximin`, and `marginal`;
no matching selector-specific theorem was located.  These negative keyword
results narrow the comparison but remain weaker than specialist review.

## Limits and reviewer gate

1. The 2023 *Rich Extensions* full text was not openly accessible.  Its
   abstract does not advertise the present result, but that is not a substitute
   for full-text inspection.
2. Citation indexing can omit books, working papers, non-English sources, and
   papers that use different terminology without citing the 2017 paper.
3. Keyword absence is weak evidence.  A specialist should check whether the
   simultaneous strict-cover lemma is merely a theorem-equivalent dual form of
   property I and whether balanced-trace transport is implicit in normal-cone,
   balanced hypergraph, exact-balancedness, or Kohlberg-type arguments.
4. The mathematical proof and verifier have internal checks, but no independent
   external correctness verdict has yet been incorporated for the complete
   phase theorem.
5. The uncrossing theorem especially needs a cooperative-game or submodular
   optimization specialist to decide whether its local-tight-set formulation
   is implicit in a known lattice/uncrossing theorem.
6. The binary broken-diamond result has a short elementary proof.  That makes
   it readily checkable, not automatically novel; a specialist must search
   for the same four-cell capacity argument under core-polytope, tight-set,
   balanced-hypergraph, or exact-balancedness terminology.
7. The two-column exterior budget is algebraically close to published exact
   balancedness. A specialist must distinguish any novelty in the oriented
   Lmin normal form and sharp converse from the elementary slack inequality
   once the four-cell identity has been written down.
8. The deficit-completion inequality itself is elementary after its incidence
   identity is displayed and is encompassed by published semi-balanced-system
   theory. Any significance must come from the Lmin-selected restricted LP,
   its zero-cost domain, and a nontrivial classification of its positive-cost
   extreme rays—not from repackaging exact balancedness.

Accordingly, the defensible current claim is **a credible, apparently new
structural classification in a specialized part of cooperative game theory**.
The integral-trace theorem broadens the contribution beyond the staircase: it
gives a dimension-free forbidden-pattern result for the tight-coalition
hypergraph of every two-poorer failure.  That strengthens the general-theory
case, but does not remove the need for specialist review.
“Major field breakthrough” remains premature until correctness and novelty
survive hostile specialist review.
