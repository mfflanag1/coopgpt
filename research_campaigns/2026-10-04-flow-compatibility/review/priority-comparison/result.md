**Result: explicit priority gap, no precise match.** In the free sources I could open, I found neither a counterexample nor a theorem on whether v(S,R)=min(c(S),c(R)) always has a source-optimal entire-core allocation. This is a statement about what I read, not evidence of novelty; the most likely locations of prior art were not freely retrievable.

## Models to keep separate

- **Target game (endpoint example).** Each player holds a positive quantity of exactly one of two commodities, and v=min of the two totals. In Apartsin–Holzman's terminology this is a *singular, non-uniform* glove-market game with m=2. This is the literature name to search under.
- **Unitary glove / "Ocean" game.** Same game with every holding equal to 1. Here the core is fully known and is the convex hull of the minimal-side measures, so no side-optimality failure is possible.
- **Transportation game.** Capacities p_i, q_j are units, with x_ij ≥ 0 unbounded per pair and weights a_ij. This is "Model 2" in Núñez's 2013 slides, attributed there to Thompson 1981, Crawford–Knoer 1981 and Sotomayor 2002. Setting a_ij≡1 gives the target game; that embedding is my inference from the definitions, and no source I read states it.
- **Multiple-partners game.** Sotomayor 1992, "Model 1" in the slides: x_ik ∈ {0,1}, with quotas counting distinct partners. The target game does not embed here without splitting players, which the contract says changes the model.

## Verified by direct reading

1. **Apartsin–Holzman, IJGT 32 (2003) 189–204**, pp. 189–199 and references. https://holzman.net.technion.ac.il/files/2012/09/ijgtglove.pdf
   - Observation 2.2 (p. 193): the core contains Conv{b_j : j∈J}, the minimal-total rows.
   - Theorem 3.2 (p. 195): equality holds for unitary games, proved via Kalai–Zemel 1982b mincut extreme points.
   - Example 4.1 (p. 196): B=[[1,0],[0,2]], attributed to Owen 1975; the core is the segment [(1,0),(0,1)], larger than the competitive set. Both side-optima exist. This is the same phenomenon as ledger K2 Example 1.
   - Example 4.3 (pp. 196–197): B=(2,2,0,0,0 ; 0,0,1,1,1), from Postlewaite–Rosenthal 1974; the core is the single point (0,0,1,1,1).
   - There is no theorem or example about side-optimal core points in singular games.
   - Section 5 (p. 198) cites Owen 1975, Rosenmüller 1982 and Samet–Zemel 1984 for the core shrinking to the dual set under replication.

2. **Rosenmüller–Sudhölter, "Formation of cartels in glove markets and the modiclus"** (working paper), printed pp. 1–12 only. https://webdoc.sub.gwdg.de/ebook/e/bielefeld/formation.pdf
   - p. 8: orthogonal min-of-measures model, restricted to uniform holdings.
   - p. 9: for Ocean games the core is the convex hull of the measures with minimal mass.
   - Nothing on non-uniform cores in the pages read.

3. **Núñez, "The assignment game: core, competitive equilibria and multiple partnership"**, Budapest summer school slides, June 2013, slides 1–40. https://archive.illc.uva.nl/COST-IC1205/documents/Budapest-2013-Slides/Nunez.pdf
   - Model 2 slides: the core strictly contains the dual solutions (one firm r=2, one worker s=1, a=4).
   - "The core is not a lattice": one firm r=2, two workers s=1, a=(3,3); (5;1,0) and (4;0,2) are in the core but their join (5;0,0) is not.
   - Verbatim: "It is an open problem the existence of a core element that is optimal for each side of the market."
   - "There may not be a worst core element for one side": r=(2,2), s=(1,3), a=[[4,1],[4.5,1.5]].
   - This is an open-status claim for the *weighted transportation* model, not only for multiple-partners. It is a 2013 secondary source (slides) and establishes historical status only.

4. **Atay–Núñez–Solymosi, arXiv:2404.04847v1** (7 Apr 2024), pp. 1–6. https://arxiv.org/pdf/2404.04847
   - pp. 2–3: distinguishes multiple-partners (Sotomayor 1992) from the transportation game (Sánchez-Soriano et al. 2001).
   - For many-to-many, citing Sotomayor 2002 and 2007: "some core allocations may not be supported by competitive prices and the core may not be a lattice."
   - Side-optimal existence is asserted only for many-to-one.
   - It contains neither an "open problem" sentence nor a non-existence claim for many-to-many.

## Abstract-level or tool-summarised only (not verified text)

- **Atay–Núñez–Solymosi, J Global Optim 2026** (ledger M1). https://link.springer.com/article/10.1007/s10898-026-01632-7 The fetch tool extracted introduction sentences matching the 2024 arXiv wording, with no openness or non-existence statement for many-to-many. A search-engine summary asserted "it remains an open problem" for this paper; the page extraction did not confirm it. Treat that as unverified.
- **Aparicio–Gonçalves-Dosantos–Sánchez-Soriano, "The game of agents in transportation problems", Ann Oper Res, 14 Oct 2024** (paywalled). https://link.springer.com/article/10.1007/s10479-024-06341-6 The tool-extracted abstract says the complete characterisation of the transportation-game core "continues to be an open problem". That concerns core structure in general, not side-optimal existence specifically.
- **arXiv:2109.05456** (abstract only): "In general, the core does not exhibit a middleman-optimal matching." This is a three-sided model and not comparable. https://arxiv.org/abs/2109.05456

## Unread originals

- Sánchez-Soriano–López–García-Jurado 2001, "On the core of transportation games" (Math Soc Sci 41:215–225): paywalled, and RePEc has no abstract.
- Llorca et al. 2004 on the Owen set: the UC3M copy returned 403.
- Sotomayor 1992, 1999, 2002: not found free. Sotomayor 2007: the free host refused the connection.
- Thompson 1981; Owen 1975; Rosenmüller 1982; Samet–Zemel 1984; Postlewaite–Rosenthal 1974: not retrieved.
- The remainder of the Rosenmüller–Sudhölter working paper beyond p. 12.
- I did not re-inspect Isbell 1959.

## Unresolved comparisons

1. **Does the example settle the 2013 open problem?** The example's game is a_ij≡1 "Model 2". If its proof survives independent review, it would be a negative instance of the question the 2013 slides call open. I cannot certify that the question was still open after 2013: Sotomayor's later papers and the 2024 Annals paper are unread.
2. **Perez-Castrillo–Sotomayor 2018 is not the same question.** Their statement (ledger M2) concerns multiple-partners with per-pair capacity 1; the example does not address that model.
3. **Singular glove-market literature.** A source-optimality failure could already sit in Owen 1975, Rosenmüller 1982, Samet–Zemel 1984 or Sánchez-Soriano et al. 2001. None of these was readable, so priority there is undetermined.
4. **Known results nearby are weaker.** Lattice failure, absence of a worst element, and core strictly larger than the Owen set are all established with tiny examples (Owen 1975 via Apartsin–Holzman; Núñez 2013). None of those examples lacks a side-optimal point, so they neither anticipate nor contradict the endpoint claim.

## Limitations

- Bounded web session, free sources only.
- PDFs were read as page images.
- I ran no computation and did not check the example's mathematics.
- I edited no files.
