I found no original theorem or counterexample that settles source-side or sink-side endpoint compatibility for the frozen class. The Kalai–Zemel originals are now recovered and read, and the closest two-sided literature explicitly calls the analogous whole-core question open.

## Sources actually read (page images viewed directly)

**K1. Kalai–Zemel, "On Totally Balanced Games and Games of Flow", Discussion Paper 413, January 1980** (precursor of Math. Oper. Res. 7(3), 1982).
URL: https://www.kellogg.northwestern.edu/~/media/files/research/math/papers/413.pdf (this replaces the 404 URL in S13).
- Model (printed pp. 5–6): directed network, arbitrary nonnegative real capacities, each arc labelled with one owner; a player may own several arcs; no public arcs, no acyclicity or path-length assumption.
- Theorem 1 (p. 4): totally balanced iff minimum of finitely many additive games. Theorem 2 (p. 7): totally balanced iff flow game.
- Core content (p. 8): only that a fixed min cut gives a core point. Nothing on core maxima or endpoint optimality.
- Quote (p. 9): "the connection between core allocations and cuts in the network G is deeper than what is revealed by the proof of Theorem 2".

**K2. Kalai–Zemel, "Generalized Network Problems Yielding Totally Balanced Games", Discussion Paper 425, June 1980** (precursor of Oper. Res. 30(5), 1982).
URL: https://www.kellogg.northwestern.edu/~/media/files/research/math/papers/425.pdf
- Theorem 2 (pp. 15–16): for LP games, optimal dual solutions give core points (the Owen-type inclusion).
- Example 1 (pp. 16–17): the converse fails with unequal capacities. Arc a (capacity 2) feeds parallel arcs b, c (capacity 1 each), one player per arc; (1,1,0) is in the core but is not dual-optimal. This is inside the frozen class and predates Gangam et al. Example 5.4 (S5).
- Section V "Simple Networks" (pp. 18–24): every result there assumes unit capacities and one distinct owner per arc. Proposition 1 (p. 19): core = efficiency + path inequalities + nonnegativity. Theorem 3 (p. 22): every core point is an optimal dual. Theorem 4 (pp. 23–24): core extreme points are exactly min-cut indicators.
- Quote (pp. 18–19): "simple, if u_j = 1 for every j ∈ L and if each arc is owned by a different player".
- Remark 3 (p. 20) says Proposition 1 fails for non-simple networks such as Example 1.
- Example 3 (pp. 24–25): arc a (capacity 3) into parallel d, e (capacity 1). It lists the min-cut core point plus three additional extreme points; the scan prints one coordinate as "v", which I read as 1.
- Example 4 (p. 25): raising d's capacity to 2 puts (1,1,1,0,0) in the core.
- No statement on simultaneous coordinate maxima of source or sink arcs anywhere in the paper.
- The draft has numbering slips (two sections numbered IV; a proof cites "proposition 3" for Proposition 2). Published theorem numbers may differ; I did not see the journal versions.

**M1. Atay–Bahel–Solymosi, "Matching markets with middlemen under transferable utility", arXiv:2109.05456v2 (24 Jan 2022).**
URL: https://arxiv.org/pdf/2109.05456
- Model: buyers, sellers (unit demand/supply) and middlemen who can mediate many pairs; players are nodes, values are weighted; whole core.
- Theorem 3 (p. 11): buyer-optimal and seller-optimal core allocations exist, with every buyer (seller) at marginal contribution.
- Example 3 (pp. 12–13): no middleman-optimal core allocation; y1 + y2 ≤ 6 while individual maxima are 2 and 6.
- Quote (p. 13): "there is no core allocation at which all middlemen can achieve their maximum core payoffs (which are their marginal contributions) simultaneously".
- This is the closest three-layer comparison: endpoint sides compatible, middle side not. It is not a max-flow game: endpoints have unit capacity and the Theorem 3 proof reduces to a one-to-one assignment game.

**M2. Atay–Núñez–Solymosi, many-to-one assignment markets (S15 source, 19 April 2022, marked preliminary).**
URL: https://gtcenter.org/wp-content/uploads/2022/04/ANS_StonyBrook.pdf
- Pages 7 and 9: firm-optimal and worker-optimal whole-core allocations exist when one side has unit capacity, via Sotomayor (2002)'s lattice on workers' payoffs.
- Quote (p. 9), on that existence: "which is not known to be true for the general many-to-many assignment games".
- Page 7 also says the core need not equal the dual solutions and opposition of interests fails, attributed to Sánchez-Soriano et al. (2001) and Sotomayor (2002); that is secondary attribution.

**M3. Pérez-Castrillo–Sotomayor, "Comparative Statics in the Multiple-Partners Assignment Game", Barcelona GSE WP 1036, April 2018.**
URL: https://bw.bse.eu/wp-content/uploads/2018/04/1036-file.pdf
- Page 3: stable outcomes form a complete lattice; the core is larger and not always a lattice (attributed to Sotomayor 1992/1999).
- Quote (p. 4): "the existence of the optimal core allocations is an open problem (see Sotomayor, 1992)".
- This is direct evidence that stable-set or competitive side-optima must not be imported as whole-core maxima.

**M4. Núñez, lecture slides, Budapest 2013 (secondary, not a theorem source).**
URL: https://archive.illc.uva.nl/COST-IC1205/documents/Budapest-2013-Slides/Nunez.pdf
- Transportation-type model (capacities are units supplied or demanded), PDF pp. 37–41: core strictly contains the dual solutions, and the core is not a lattice (one firm of capacity 2, two unit workers, values 3, 3).
- Quote (PDF p. 40): "It is an open problem the existence of a core element that is optimal for each side of the market."
- The same slide says there may be no worst core element for a side; the next says the many-to-one case does have side-optimal core allocations.

## Read only through the fetch tool's summary (not verified by me)
- Atay–Núñez–Solymosi, arXiv:2404.04847v1 (7 Apr 2024), https://arxiv.org/html/2404.04847v1. Reported: firms with capacity above one may not reach marginal contribution in the core (its Example 3: maximum 9 against marginal 11). Treat as a lead.
- Xiao–Zhang–Fang, "A Complete Characterization of Convexity in Flow Games", https://arxiv.org/html/2604.04729. Reported: one player per arc, arbitrary capacities, convexity iff acyclicity plus two bottleneck conditions. If accurate, endpoint compatibility is trivial in that subclass, since convex games attain all marginals of a chain; this does not cover the frozen class.
- Aparicio–Gonçalves-Dosantos–Sánchez-Soriano, "The game of agents in transportation problems", Ann. Oper. Res., https://link.springer.com/article/10.1007/s10479-024-06341-6. Abstract level only; reported to call the transportation-game core structure "an open problem".

## Claim-specific comparison with the frozen class

| Source | Ownership | Capacities | Object | Bearing on endpoint compatibility |
|---|---|---|---|---|
| K1 | several arcs per player allowed | arbitrary | core nonempty | none |
| K2 Section V | one arc per player | unit only | whole core = duals = hull of min cuts | settles the unit case only |
| K2 Examples 1, 3, 4 | one arc per player | unequal | whole core strictly larger than Owen set | in-class instances; no general statement |
| M1 | node players, three layers | unit endpoints, unlimited middle | whole core | endpoints yes, middle no; not max-flow |
| M2 | node players, two sides | one side unit | whole core | side-optimal exists; many-to-many "not known" |
| M3, M4 | node players, two sides | quotas on both sides | whole core versus stable or competitive | reported open; lattice fails |

My own inferences, not from any source:
- In K2 Example 3, from the listed extreme points, the single source arc has maximum 2 and the sink arcs d, e both reach 1 at (0,1,1). That instance is endpoint-compatible and is not a counterexample.
- A max-flow game with only endpoint players and free middle arcs would be a 0/1-valued transportation game, where whole-core side-optimality is reported open. The frozen class instead makes middle arcs players, so neither a positive nor a negative transportation result would transfer without a proved lifting lemma. I did not prove one.
- M1 suggests any flow obstruction is more likely for middle arcs than for endpoints, but that is a heuristic only.

## Originals not obtained (no purchases)
- Kalai–Zemel 1982 journal versions (INFORMS): not accessed; only the 1980 discussion papers were read.
- Sánchez-Soriano–López–García-Jurado, "On the core of transportation games", Math. Soc. Sci. 41 (2001): paywalled.
- Llorca et al., "On the Owen set of transportation situations": halweb.uc3m.es copy returned 403.
- Sotomayor 1992 ("The multiple partners game", book chapter): not located free. This is the cited origin of the open problem, so the "open" status rests on M3 and M4's attribution.
- Sotomayor 2002/2003 (IJGT 31): paywalled. Sotomayor 2007 (JET 134): pareto.uab.es copy refused connection.
- Stuart 1997 (supplier–firm–buyer game) and Atay–Núñez 2019 (multi-sided games on m-partite graphs): not read. The MSS 2019 note I opened is a different paper and not relevant.
- Reijnierse et al. 1996: unchanged from S12, no new lead.

## Unresolved
- Endpoint compatibility for the frozen class remains UNKNOWN on the sources read. Search silence is not evidence of novelty or of current openness.
- The "open problem" statements date from 2013, 2018 and 2022 and concern weighted many-to-many markets with node players. I did not check whether they have since been resolved, nor whether the 0/1-valued (max-flow) special case is easier.
- The published 1982 Kalai–Zemel texts could contain remarks absent from the 1980 drafts.

Sources:
- [Kalai–Zemel DP 413](https://www.kellogg.northwestern.edu/~/media/files/research/math/papers/413.pdf)
- [Kalai–Zemel DP 425](https://www.kellogg.northwestern.edu/~/media/files/research/math/papers/425.pdf)
- [Kellogg Math Center discussion papers index](https://www.kellogg.northwestern.edu/academics-research/mathematical-studies/discussion-papers/)
- [Atay–Bahel–Solymosi, arXiv:2109.05456](https://arxiv.org/pdf/2109.05456)
- [Atay–Núñez–Solymosi 2022 preliminary](https://gtcenter.org/wp-content/uploads/2022/04/ANS_StonyBrook.pdf)
- [Atay–Núñez–Solymosi, arXiv:2404.04847](https://arxiv.org/abs/2404.04847)
- [Pérez-Castrillo–Sotomayor, BGSE WP 1036](https://bw.bse.eu/wp-content/uploads/2018/04/1036-file.pdf)
- [Núñez 2013 slides](https://archive.illc.uva.nl/COST-IC1205/documents/Budapest-2013-Slides/Nunez.pdf)
- [Xiao–Zhang–Fang, arXiv:2604.04729](https://arxiv.org/html/2604.04729)
- [Aparicio et al., Annals of OR](https://link.springer.com/article/10.1007/s10479-024-06341-6)
- [Atay–Núñez 2019 MSS note](https://ataatay.github.io/webpage/Atay_Nu%CC%81n%CC%83ez_2019_MSS.pdf)
