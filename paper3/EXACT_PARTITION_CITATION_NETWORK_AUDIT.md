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
| Every two-poorer failure forces a nonintegral active trace polytope/odd trace cycle | Not found; Berge's matrix-integrality theorem is classical | Present only as a new bridge from Lmin geometry to known balanced-matrix theory. |
| Rank-two packet dichotomy: a proper rank-three trace or at least two odd cycles with transversal-face budgets | Not found; half-integrality of graph exact covers is standard | Present as a candidate exact-game bridge, and explicitly retract the earlier all-rank-two exclusion. |
| At `|H|=4`, every two-poorer failure has the four-co-singleton `1/3` vertex | Not found; four-row exact-cover classification is elementary | Present as a candidate first-obstruction uniqueness theorem, pending specialist review. |
| Projective-plane trace packets obey overlap-sensitive density and local `A setminus B` barriers, are excluded through order six, and are also excluded in `PG(2,7)` | Not found; the incidence counts and Segre's `q`-arc extension theorem are classical | Present only the exact-face application as a candidate new realization exclusion, pending finite-geometry and game-theory specialist review. |
| Complete boundary staircase `4,3,3,2` | Not found | Present as apparent new classification. |
| Universal indecomposable family for every `m>=3,h>=2` | Not found | Present as apparent new sharpness construction. |
| Closed-form Lmax and distance `4h/(h+1)` for that family | Not found | Present as an additional explicit result, not the core novelty claim. |

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
dimension; cardinality; indecomposable; replication
balanced matrix; set partitioning; active trace; odd cycle
property I; hierarchical tight-coalition criterion; complement-tight coalition
fractional matching; rank-two trace; graph exact cover; odd-cycle rounding
```

The full texts inspected include Arin--Kuipers--Vermeulen (2008), Definition 3
and Lemma 1, and Mauri's 2018 thesis, Definitions 11--12 and Lemma 3. They
establish the qualitative property-I criterion but do not state the
simultaneous strict cover, the active-trace polytope, or the odd-cycle
necessity theorem. The other full texts inspected were the consistency, antiduality, NTU,
population-monotonicity, convex-game axiomatization, welfare-egalitarianism,
discrete-side-payment, and characteristic-function papers listed above.

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

Accordingly, the defensible current claim is **a credible, apparently new
structural classification in a specialized part of cooperative game theory**.
The integral-trace theorem broadens the contribution beyond the staircase: it
gives a dimension-free forbidden-pattern result for the tight-coalition
hypergraph of every two-poorer failure.  That strengthens the general-theory
case, but does not remove the need for specialist review.
“Major field breakthrough” remains premature until correctness and novelty
survive hostile specialist review.
