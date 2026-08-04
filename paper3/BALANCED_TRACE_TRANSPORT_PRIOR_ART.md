# Prior-art audit — balanced-trace transport at Lmin boundaries

## Scope and conclusion

Search date: 2026-08-04.

For the reproducible forward-citation audit of the 2017 exact-partition paper,
including all 12 OpenAlex citing records and the closest known four-player
result, see [`EXACT_PARTITION_CITATION_NETWORK_AUDIT.md`](EXACT_PARTITION_CITATION_NETWORK_AUDIT.md).

This audit targets the dimension-free theorem now called the **balanced-trace
transport obstruction**: at any slack richer suffix of Lmin in an exact game,
stagewise Lmin dual covers project to a convex mixture of minimal balanced
collections on the richer side, every lifted packet transports the suffix
slack through the poorer side, and the average poor load is coordinatewise
strictly below one.

The search found each ingredient separately, but no source stating this bridge
or any of the following sharp consequences:

- exact games through four players are exact partition at Lmin;
- with exactly two poorer players, a slack richer suffix is impossible for at
  most three richer players and possible for every richer-block size at least
  four;
- the complete boundary-cardinality phase diagram
  `m_min(1)=4`, `m_min(2)=m_min(3)=3`, and `m_min(h)=2` for `h>=4`.

This is evidence of apparent novelty, not a definitive novelty opinion.
Citation-chain review by specialists in exact games and egalitarian solutions
remains required.

## Established ingredients that must not be claimed as new

1. **Lmin and egalitarian-core blocking.** Arin and Iñarra (2001),
   *Egalitarian solutions in the core*, introduce Lmin and characterize the
   relevant tight-coalition blocking structure.
2. **Low-dimensional large cores.** Biswas, Parthasarathy, Potters, and
   Voorneveld (1999), *Large cores and exactness*, prove that exact games with
   at most four players have large cores.  Dietzenbacher's egalitarian-stability
   paper explicitly records the consequence that these games are egalitarian
   stable; this is weaker than exact partition at Lmin.
3. **Exact partition games.** Llerena and Mauri (2017),
   [*On the existence of the Dutta--Ray's egalitarian solution*](https://doi.org/10.1016/j.mathsocsci.2017.07.002),
   introduce exact partition games and prove the Lorenz conclusion.  The
   condition and implication are prior art.
   Dietzenbacher (2021) also proved that exact games with at most four players
   are PES stable.  That is the closest published low-dimensional result found;
   it is weaker than proving that Lmin itself satisfies the exact-partition
   tightness conditions.
4. **Antiduality and later exact-partition theory.** Dietzenbacher and
   Yanovskaya (2020),
   [*Antiduality in exact partition games*](https://doi.org/10.1016/j.mathsocsci.2020.04.006),
   extend the theory; they do not supply the dimensional classification here.
5. **Exact balancedness.** Csóka, Herings, and Kóczy (2011) characterize exact
   games by exact balancedness.  Lohmann, Borm, and Herings (2012),
   [*Minimal exact balancedness*](https://doi.org/10.1016/j.mathsocsci.2012.01.002),
   classify minimal exact-balanced collections.
6. **Minimal balanced collections.** Peleg's generation theory and the
   Bondareva--Shapley role of minimal balanced collections are classical.
   Laplace Mermoud, Grabisch, and Sudhölter (2025),
   [*Minimal balanced collections and their applications to core stability and
   other topics of game theory*](https://arxiv.org/abs/2507.05898), give a
   modern enumeration and applications.  The present paper does not claim to
   invent these packets or their three-player classification.
7. **Balanced matrices.** Berge (1972),
   [*Balanced matrices*](https://doi.org/10.1007/BF01584535), proves the
   classical integrality theorem for set-partitioning polytopes of balanced
   zero--one matrices.  The paper cites this result; the candidate new bridge
   is that a slack two-poorer Lmin boundary forces the active trace matrix to
   violate balancedness.
8. **Lmin/Lmax comparisons and monotonicity.** Dietzenbacher (2021),
   [*Monotonicity and egalitarianism*](https://doi.org/10.1016/j.geb.2021.03.006),
   compares Lmin, Lmax, and PES on broader domains and records prior
   monotonicity failures.  It does not state the exact-game boundary-transport
   result found here.

## Search protocol

Exact-phrase and conjunction searches included:

```text
"exact partition game" Lmin exact games
"Lmin" "exact games" cooperative game
"egalitarian solution" "exact games" four players
"minimal balanced collections" Lmin egalitarian exact
"exact partition" "at most four players" game
"exact games" "at most four players" "exact partition"
"Lmin solution" "minimal balanced"
"lexmin solution" exact partition games
cooperative game "balanced trace" coalition
cooperative game "transport" "minimal balanced collection" egalitarian
"minimal balanced collection" "egalitarian core"
"exact balanced" Lmin Lorenz
"exact partition games" egalitarian solution richer coalition tight suffix
"exact partition" "Lmin" cooperative games
"egalitarian solution" exact games payoff classes coalition union
"egalitarian solution" "balanced matrix" cooperative game
"Lmin" hypergraph cooperative game balanced
"exact partition game" hypergraph "balanced matrix"
"minimal balanced collection" "set partitioning" egalitarian
```

The searches were followed through the references and discussion sections of
the papers above, including the 2017 exact-partition paper, the 2020
antiduality paper, the 2021 monotonicity paper, the 2012 minimal
exact-balancedness paper, the 2025 minimal-balanced-collection survey, and
Berge's classical balanced-matrix paper.  No source found in this search
forces nonintegrality or an odd trace cycle from a slack Lmin boundary.

## Defensible novelty statement

Pending expert review, the strongest defensible formulation is:

> We combine stagewise Lmin duality with exact coalition-face witnesses to
> show that every slack richer suffix in an exact game induces a minimal
> balanced trace-transport certificate.  This dimension-free obstruction
> yields a human exact-partition classification through four players and a
> sharp `2|3` versus `2|4` richer-side threshold.  Every two-poorer failure
> moreover forces a nonintegral active trace hypergraph, hence an odd
> balanced-matrix obstruction.  Three explicit universal
> families then give a complete classification of the boundary-side
> cardinalities compatible with slack.  We do not claim the Lmin solution,
> exact partition games, their published Lorenz consequence, exact
> balancedness, or minimal balanced collections as new.

## Remaining novelty gate

Send the theorem and proof to researchers familiar with the Arin--Iñarra,
Llerena--Mauri, and exact-balancedness literatures.  Ask specifically whether
the hierarchical dual-cover lemma or the projection of its tight coalitions
to minimal balanced rich-side packets appears under different terminology
(normal cones, balanced hypergraphs, Kohlberg-type criteria, or reduced-game
consistency).  Also ask whether any paper classifies failure of the exact
partition condition by the cardinalities of the cumulative poorer and richer
sides.  The available exact-partition sources define the condition and derive
solution-theoretic consequences, but this search found no such phase theorem.
Absence from keyword search alone is not enough.
