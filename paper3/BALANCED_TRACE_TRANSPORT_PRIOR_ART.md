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
- every two-poorer slack boundary is genuinely hypergraphic: some active
  rich-side trace has cardinality at least three;
- every safe rooted integer fibre of a tight trace semigroup is forbidden by
  an exact singleton face, a dimension-free mechanism unifying the rounding
  exclusions below;
- more generally, a real tight cover with rich overload `q 1_D` charges the
  slack of the internal exact face `D` to uncovered poorer-player payoff;
  its singleton specialization is also the protector-packing budget behind
  the sharp unique-richest four/five threshold;
- positive Lehman trace packets carry canonical rooted fibres through the
  classical identity `A B^T=J+kI`; a new two-label density test rules out
  such packets and unifies the odd-cycle and coarse projective-plane
  roundings, while the co-singleton survivor has the opposite sign;
- at the first feasible four-player richer suffix, every failure has the
  four-co-singleton `1/3` vertex, the unique surviving fractional packet;
- projective-plane incidence packets satisfying the overlap-sensitive bound
  `b(q+2-b)>cd+binom(d,2)` or the local bound `d<2(q+2-b)` are eliminated by
  a safe star rounding, where `c=|A intersect B|` and
  `d=|A setminus B|`; this includes
  every such packet of order at most six; the only remaining order-seven
  count is also eliminated in `PG(2,7)` by Segre's arc-extension theorem;
- the complete boundary-cardinality phase diagram
  `m_min(1)=4`, `m_min(2)=m_min(3)=3`, and `m_min(h)=2` for `h>=4`.

This is evidence of apparent novelty, not a definitive novelty opinion.
Citation-chain review by specialists in exact games and egalitarian solutions
remains required.

## Established ingredients that must not be claimed as new

1. **Lmin and egalitarian-core blocking.** Arin and Iñarra (2001),
   *Egalitarian solutions in the core*, introduce Lmin and characterize the
   relevant tight-coalition blocking structure.
2. **Property I is the known qualitative optimality criterion.** Arin,
   Kuipers, and Vermeulen (2008), [*An axiomatic approach to egalitarianism in
   TU-games*](https://doi.org/10.1007/s00182-008-0133-6), Lemma 1 characterize
   Lmax by uniqueness of the zero direction in a hierarchical system formed
   from its payoff partition and tight coalitions. Mauri (2018),
   [*Essays on egalitarianism-based solution concepts for cooperative
   TU-games*](https://repositori.urv.cat/estatic/TDX0011/en_TDX2707.html),
   Lemma 3 explicitly transports this result by antiduality to Lmin, the
   reversed payoff partition, and complement-tight coalitions. The present
   strict-cover lemma must therefore be described as a quantitative LP-dual
   consequence/refinement of this known optimality structure, not as a new
   tight-coalition characterization of Lmin. Neither source states the single
   cover regular on all of `H` and strictly deficient on every member of `L`,
   nor its projection to an active-trace exact-cover polytope.
3. **Low-dimensional large cores.** Biswas, Parthasarathy, Potters, and
   Voorneveld (1999), *Large cores and exactness*, prove that exact games with
   at most four players have large cores.  Dietzenbacher's egalitarian-stability
   paper explicitly records the consequence that these games are egalitarian
   stable; this is weaker than exact partition at Lmin.
4. **Exact partition games.** Llerena and Mauri (2017),
   [*On the existence of the Dutta--Ray's egalitarian solution*](https://doi.org/10.1016/j.mathsocsci.2017.07.002),
   introduce exact partition games and prove the Lorenz conclusion.  The
   condition and implication are prior art.
   Dietzenbacher (2021) also proved that exact games with at most four players
   are PES stable.  That is the closest published low-dimensional result found;
   it is weaker than proving that Lmin itself satisfies the exact-partition
   tightness conditions.
5. **Antiduality and later exact-partition theory.** Dietzenbacher and
   Yanovskaya (2020),
   [*Antiduality in exact partition games*](https://doi.org/10.1016/j.mathsocsci.2020.04.006),
   extend the theory; they do not supply the dimensional classification here.
6. **Exact balancedness.** Csóka, Herings, and Kóczy (2011) characterize exact
   games by exact balancedness.  Lohmann, Borm, and Herings (2012),
   [*Minimal exact balancedness*](https://doi.org/10.1016/j.mathsocsci.2012.01.002),
   classify minimal exact-balanced collections.
7. **Minimal balanced collections.** Peleg's generation theory and the
   Bondareva--Shapley role of minimal balanced collections are classical.
   Laplace Mermoud, Grabisch, and Sudhölter (2025),
   [*Minimal balanced collections and their applications to core stability and
   other topics of game theory*](https://arxiv.org/abs/2507.05898), give a
   modern enumeration and applications.  The present paper does not claim to
   invent these packets or their three-player classification.
8. **Balanced matrices.** Berge (1972),
   [*Balanced matrices*](https://doi.org/10.1007/BF01584535), proves the
   classical integrality theorem for set-partitioning polytopes of balanced
   zero--one matrices.  The paper cites this result; the candidate new bridge
   is that a slack two-poorer Lmin boundary forces the active trace matrix to
   violate balancedness.
9. **Minimally nonideal matrices and Lehman pairs.** Cornuéjols, Guenin, and
   Tunçel (2009),
   [*Lehman matrices*](https://doi.org/10.1016/j.jctb.2008.06.009), study
   square zero--one pairs satisfying `A B^T=J+kI` and explain their classical
   role as cores of nondegenerate minimally nonideal matrices. The manuscript
   now cites this identity as prior art. Its candidate new contribution is
   the two-poor labeling count and the observation that each positive dual
   row becomes a forbidden exact-game rooted cover.
10. **Lmin/Lmax comparisons and monotonicity.** Dietzenbacher (2021),
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
"Lehman matrix" egalitarian cooperative game
"minimally nonideal" Lmin exact game
"Lehman matrix" two labels rooted cover
"minimal balanced collection" "set partitioning" egalitarian
"property I" Lmin Lmax tight coalitions
"property I" egalitarian TU-games
"complement tight" Lmin lexmin
"Lmin" "odd cycle" cooperative game exact
"lexmin" "fractional matching" cooperative game
"egalitarian" "balanced matrix" TU game
"exact partition game" hypergraph trace
```

The primary texts inspected include Arin--Kuipers--Vermeulen (2008), especially
Definition 3 and Lemma 1, and Mauri's 2018 thesis, especially Definitions
11--12 and Lemma 3. The searches were also followed through the references and discussion sections of
the papers above, including the 2017 exact-partition paper, the 2020
antiduality paper, the 2021 monotonicity paper, the 2012 minimal
exact-balancedness paper, the 2025 minimal-balanced-collection survey, and
Berge's classical balanced-matrix paper.  No source found in this search
forces nonintegrality or an odd trace cycle from a slack Lmin boundary, or
rules out every rank-two active trace system by combining odd-cycle rounding
with exact singleton faces.

The later targeted search inspected Cornuéjols--Guenin--Tunçel's primary
Lehman-matrix paper and the classical minimally-nonideal theorem it records.
That source supplies the matrix identity and regularity, not the poor-label
density argument or the bridge to exact-game tight faces. This is still an
absence finding rather than a definitive novelty determination.

A targeted finite-geometry search found adjacent theory of semiarcs, tangent
blocking, and secant-avoidance. In particular, Csajbók--Héger--Kiss study
small point sets whose tangents lie in a small number of pencils
(https://arxiv.org/abs/1310.7207), and Thas gives a short proof that every
odd-order `q`-arc in `PG(2,q)` extends to a `(q+1)`-arc
(https://doi.org/10.1016/0021-8693(87)90007-X). The manuscript therefore
claims neither the projective-plane incidence counts nor Segre's arc theorem
as new. The candidate contribution is their exact-face use to rule out
Lmin trace packets. No source found in this pass states the two-set
tangent-versus-secant condition in the form needed here; that absence is not
a definitive novelty result.

## Defensible novelty statement

Pending expert review, the strongest defensible formulation is:

> We combine stagewise Lmin duality with exact coalition-face witnesses to
> show that every slack richer suffix in an exact game induces a minimal
> balanced trace-transport certificate.  This dimension-free obstruction
> yields a human exact-partition classification through four players and a
> sharp `2|3` versus `2|4` richer-side threshold.  Every two-poorer failure
> moreover forces a nonintegral active trace hypergraph, hence an odd
> balanced-matrix obstruction, and graph-like trace systems are ruled out
> entirely. Exact singleton faces more generally forbid every safe rooted
> integer fibre of the supported tight-coalition semigroup, unifying the
> subsequent rounding arguments. Positive Lehman cores canonically generate
> those fibres, and a two-label density test subsumes the odd-cycle and coarse
> projective-plane roundings; the co-singleton survivor lies on the
> opposite-sign side. At four rich players the unique surviving
> fractional packet is
> the co-singleton `1/3` cover. A projective-plane star-rounding argument
> further excludes every incidence packet satisfying a simple-point density
> inequality, including every such packet of order at most six; a dual-arc
> argument closes the final extremal count in `PG(2,7)`. Three
> explicit universal families then give a complete classification of the
> boundary-side cardinalities compatible with slack.  We do not claim the Lmin solution,
> exact partition games, their published Lorenz consequence, exact
> balancedness, or minimal balanced collections as new.

This statement also does not claim the qualitative property-I characterization
of Lmin/Lmax. The candidate new mechanism begins with the simultaneous strict
cover, then projects it to trace packets and combines it with exact-face
witnesses.

## Remaining novelty gate

Send the theorem and proof to researchers familiar with the Arin--Iñarra,
Arin--Kuipers--Vermeulen, Llerena--Mauri, and exact-balancedness literatures.
Ask specifically whether the simultaneous strict-cover lemma is already an
explicit theorem-equivalent reformulation of property I, or only a derived
quantitative certificate, and whether the projection of its tight coalitions
to minimal balanced rich-side packets appears under different terminology
(normal cones, balanced hypergraphs, Kohlberg-type criteria, or reduced-game
consistency).  Also ask whether any paper classifies failure of the exact
partition condition by the cardinalities of the cumulative poorer and richer
sides.  The available exact-partition sources define the condition and derive
solution-theoretic consequences, but this search found no such phase theorem.
Absence from keyword search alone is not enough.
