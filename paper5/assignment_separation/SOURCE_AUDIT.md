# Primary-source audit - 4 September 2026

Scope: sorted-payoff fairness in the entire core of weighted bipartite assignment games. This is a bounded source audit, not a novelty certificate. No external contact was made.

## Current starting point and conventions

[Vazirani, arXiv:2402.11437v6](https://arxiv.org/html/2402.11437v6), revised 20 November 2025, is the latest version listed by arXiv at retrieval. The [author's homepage](https://ics.uci.edu/~vazirani/) lists the paper at EC 2026. The operational definitions maximize the ascending payoff profile and minimize the descending profile. Definition 11's use of “largest” for the latter conflicts with the introduction and descending algorithm; we state our convention explicitly. Omitting core-identically-zero agents from sorting gives the same full selections. Its geometric questions are related motivation, not a located quantitative separation conjecture.

### Exact calibration of the displayed example

Figure 1 displays six edges:

    u1-v1 136; u2-v2 76; u3-v3 68; u4-v4 118;
    u1-v2 140; u3-v4 56.

Our independently computed selectors for that graph, in order (u1,u2,u3,u4;v1,v2,v3,v4), are

    Lmin = (100,36,34,59;36,40,34,59),
    Lmax = (70,6,34,59;66,70,34,59).

The total is 398 and normalized distance is 60/199. The printed vectors are feasible but strictly lexicographically suboptimal for the displayed graph. This is an inference from exact reconstruction, not an author-confirmed correction. The lower component's pairwise equal splits (34,59;34,59) satisfy its cross constraint 34+59>=56 and explain the discrepancy directly.

The [public replication fixture](https://github.com/Lluc24/leximin/blob/main/tests/fixtues.py) independently uses the same six weights and the corrected leximin. Its [project README](https://github.com/Lluc24/leximin) describes Vazirani's supervision. `verify_published_example.py` checks the full coalition core, both reconstructed selectors, and both strict improvements over the printed vectors. This local discrepancy does not establish a failure of the paper's general algorithms. The new theorem uses its own proof and attaining family.

## Established results that constrain the contribution

| Source | Relevant established content and boundary |
|---|---|
| [Klijn et al., Neighbour Games and the Leximax Solution (2003)](https://pure.uvt.nl/ws/files/533861/110.pdf) | Path assignment games already have an alternating-adjustment characterization and polynomial leximax algorithm. Sorted fairness is not a new concept here. No quantitative comparison matching our claim was located in this paper. |
| [Llerena, The pairwise egalitarian solution for the assignment game (2012)](https://doi.org/10.1016/j.orl.2011.11.011) | Feasible pairwise equal splits supply a Lorenz-best allocation; dominant-diagonal structure is an established agreement subclass. |
| [Solymosi-Raghavan, Assignment games with stable core (2001)](https://doi.org/10.1007/s001820100072) | Exactness has established dominant/doubly-dominant diagonal characterizations. [Hoffmann-Sudholter, Theorem 3.2](https://www.sdu.dk/-/media/files/om_sdu/institutter/ivoe/disc_papers/disc_2005/edp4_2005.pdf) records that result. Our short side-coalition argument gives the relevant equality implication without importing the classification. |
| [Solymosi, Sensitivity of fair prices in assignment markets (2023)](https://doi.org/10.1016/j.mathsocsci.2023.09.003) | The fair-price/tau allocation is the midpoint of the two side-optimal allocations, hence already achieves at least half each player's maximum core payoff. Our potentially new claim concerns this guarantee for full leximin. |

[The Extreme Core Allocations of the Assignment Game, Property 2](https://diposit.ub.edu/bitstreams/fc07f047-8b43-40fb-ba86-20ae5516814b/download) attributes maximum core payoff equaling marginal contribution to Demange (1982) and Leonard (1983). That identity gives a possible economic interpretation, but the manuscript's proof and formal statement do not depend on it.

[Gangam et al., arXiv:2403.06037](https://arxiv.org/abs/2403.06037) studies equitable Owen-set computations for other combinatorial games. Those sets must not be substituted for entire cores without proof. The 2017 paper *Lexicographic allocations and extreme core payoffs: the case of assignment games* concerns fixed player priorities, a different lexicographic object.

## Domain and search conclusions

Assignment games need not be exact. With one buyer and seller opportunities of weights 2 and 1, the buyer receives at least 1 at every core point although its singleton worth is zero. This case is included in the exact calibration.

The search combined assignment game/core with leximin, leximax, distance, separation, bound, half, twice, factor, guarantee, utopia and marginal contribution. It did not locate either the coordinatewise half-maximum guarantee specifically for leximin in arbitrary assignment games, or the sharp k/(k+1) normalized distance to minimax points. Older egalitarian and alternating-adjustment theory remains the principal prior-art risk. Specialist review is required before asserting novelty or field-level significance.
