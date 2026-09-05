# Claims, sources, and priority boundary

Audit date: 2026-09-05. The comparison below separates facts verified in
primary sources from mathematical claims proved in this manuscript.

## Claim-level inventory

| Claim | Evidence in this package | Current status and boundary |
|---|---|---|
| The two selections are established fairness concepts | Primary sources S1 and S2 below; definitions repeated explicitly | Not claimed as new. `Lmax` here means decreasing-sort **minimization**. |
| Full selectors exist and are unique on compact convex sets | Short compactness/midpoint proof in §1; S2 Lemma 3 is a prior leximin uniqueness statement | Background, reproved for self-containment. |
| Every opposing maximin/minimax pair in the nonnegative constant-total simplex overlaps by at least `T/(n-1)` | Lemma 2 and its directional proof | Conventional proof checked; exactness and later stages are unnecessary. No equivalent quantitative result identified in the bounded screen. |
| The stated matrix construction is an entire-core segment | Lemma 3: complementary coalition equalities plus invertibility, and converse generator feasibility | Conventional all-parameter proof. Lower-envelope exactness alone is not enough. |
| Fibonacci family has `2-rho=2/(F_{m+1}+1)+2/(r-m+1)` | Proposition 4; exact incidence recurrence and unique first-stage optima | Conventional proof plus five raw-core finite replays. |
| `lim n(2-s_n)=2` with `2/n+O(log n/n^2)` deficit | Theorem 1; explicit construction for every `n>=128` and universal bound | Main candidate contribution. Supremum attainment, finite-n sharpness, and an exact second-order term are not asserted. |
| Polynomially bounded integer generators are possible | Final paragraph of Theorem 1 proof | Representation uses two vectors. Listing all coalition values is still exponential. |
| Code corroborates the manuscript | Five cases, closure negative control, arithmetic identities; explicit proof gates | Finite rational checks, not proof-assistant certification or a global computational census. |

## Primary-source comparison

All URLs were accessed on 2026-09-05. No paywall was bypassed. No theorem
in this manuscript depends on an inaccessible proof.

**S1. Arin and Iñarra (2001), _Egalitarian solutions in the core_.**
International Journal of Game Theory 30, 187–193.
[Publisher page and abstract](https://link.springer.com/article/10.1007/s001820100073).
The publisher abstract explicitly identifies the leximin stable allocation
as a core selection and relates it to egalitarian and Lorenz concepts.
Access here: publisher abstract and metadata only; the article body is
subscription content. The manuscript cites S1 for the established concept,
not for an unchecked theorem or a quantitative separation bound.

**S2. Vazirani, arXiv:2402.11437, version 6 (2025), _Fair Core Imputations
for the Assignment Game: New Solution Concepts and Efficient Algorithms_.**
[Versioned full text](https://arxiv.org/html/2402.11437v6).
Relevant locations: §1.2 states the opposing max-min/min-max aims; §5 gives
examples and uniqueness (Lemma 3); Theorem 9 gives a strongly polynomial
algorithm. This is assignment-core algorithmic work, not an unrestricted
exact-game distance theorem. Nomenclature qualification: the second sentence
of v6 Definition 11 says lexicographically largest for the decreasing sort,
inconsistent with §1.2's min-max description. Our sorting direction is
defined explicitly. This source is neither treated as originating all
egalitarian core ideas nor as proving the new distance claim.

**S3. Gangam, Garg, Shahkar, and Vazirani, arXiv:2403.06037, version 3,
11 February 2025, _Equitable Core Imputations for Max-Flow, MST and
b-Matching Games_.**
[Versioned full PDF](https://arxiv.org/pdf/2403.06037v3).
Relevant locations: abstract, printed pp. 1–3, and §6.2/§7.2. The paper
studies fair allocations in these combinatorial games; its constructive
algorithms use Owen sets, which may be proper subsets of the full core.
This is adjacent algorithmic context. Our theorem optimizes over the
**entire** core and ranges over unrestricted exact TU games.

**S4. Amarante, Maccheroni, Marinacci, and Montrucchio (May 2006),
_Cores of Non-Atomic Market Games_, Carlo Alberto Notebook 13.**
[Institutional primary PDF](https://www.carloalberto.org/wp-content/uploads/2018/11/no.13.pdf).
Relevant location: §2.2, printed p. 3 (PDF page 6), equations (1)–(2) and
the following paragraph. It records exactness as a lower-envelope property
and explicitly observes that the core may strictly contain the generating
convex hull. Its broader measure-theoretic framework is background;
the finite-dimensional realization needed here is proved directly.

**S5. Studený and Kratochvíl (2022), _Facets of the cone of exact games_.**
Mathematical Methods of Operations Research 95, 35–80.
[Primary arXiv abstract and journal metadata](https://arxiv.org/abs/2103.02414),
[journal DOI](https://doi.org/10.1007/s00186-022-00770-4).
The abstract describes the facet characterization using indecomposable
semi-balanced systems. Access here: primary abstract and bibliographic
record; attempted arXiv PDF/HTML retrievals failed in the browser tool.
The manuscript cites this as adjacent structural work and does not import
its facet theorem as a proof dependency or infer fixed-n attainment from it.

## Bounded fresh novelty search

The following twelve query strings were searched in three batches:

1. `leximin leximax core allocations maximum distance separation exact games`
2. `"leximin" "exact games" "Arin"`
3. `"sharp asymptotic separation" egalitarian core`
4. `"leximin" "leximax" "distance" core`
5. `Arin Iñarra 2001 Egalitarian solutions in the core pdf`
6. `"exact games" "lower envelope" additive games`
7. `"maximin" "minimax" "overlap" convex allocation`
8. `"leximin" "leximax" "Fibonacci"`
9. `"leximin" "leximax" "separation" cooperative`
10. `"leximin" "leximax" "norm" core`
11. `"egalitarian" "core" "Fibonacci"`
12. `"maximin" "minimax" "constant sum" convex set distance`

The useful results led to S1–S5 and to adjacent algorithmic, lower-envelope,
and strict-Chebyshev literature. This bounded screen did not identify an
equivalent asymptotic formula or the stated quantitative segment family.
That is a search outcome, **not** a proof of absence or a novelty certificate.

Additional leads, not incorporated as proved comparisons, include
_Neighbour Games and the Leximax Solution_ (institutional PDF retrieval
failed) and the June 2026 author software/thesis artifact
[Lluc24/leximin](https://github.com/Lluc24/leximin), which concerns an
assignment-game implementation. The latter was passed to the integration
task as a priority lead; it was not independently evaluated here.

## Questions left for genuine specialist review

1. Is the compact-convex overlap inequality already known under another
   name or in strict-Chebyshev/lexicographic optimization literature?
2. Is the asymptotic coefficient an immediate consequence of an existing
   exact-core representation theorem with quantitative dimension control?
3. Is this two-generator Fibonacci whole-core realization already present
   in the literature, or equivalent to a known construction?
4. Does the quantitative result add enough to existing fairness/core
   research to support a focused paper, and which audience is appropriate?

No specialist response has been received as part of this package. The
integration task handles any authorized outreach and its evidence record.
