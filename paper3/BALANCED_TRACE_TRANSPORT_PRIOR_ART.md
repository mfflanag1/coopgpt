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
- every underloaded two-poorer packet has a proper rich-side trace of
  cardinality at least three, via a real-valued odd-cycle overload;
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
- the two-sided Lehman label residual extends from singleton rows to arbitrary
  dual-row subsets, where its aggregate value gives a quantitative slack
  budget for the corresponding rich face;
- without the label-density hypothesis, averaging dual rows still exposes a
  canonical proper internal rich face governed by the exact-face overload
  budget, suggesting a recursive minor-lifting invariant;
- an underloaded packet violates an explicit integral set-cover objective at
  the unit threshold, with column cost `|T intersect H|+1_{b in T}`;
- after adjoining the two poor incidences as rows and singleton dummy
  columns, the packet gives a nonintegral set-partitioning point and hence a
  label-aware odd balanced-matrix obstruction;
- the degenerate-projective-plane MNI exception is incompatible with the
  required poor-load ordering, while a positive Lehman minor lift needs only
  preserve the scalar gaining-player deficit: that condition automatically
  makes every contracted column poor-label-free;
- noncore MNI rows can be retained in the dual-row density test because every
  blocker-core row transverses them; the linear total-excess penalty
  `s|W|-n` bounds selectors that hit such a row more than once;
- alternatively, scaling rich incidence above the active-column count makes
  one noncore excess cost more than the entire remaining unit gap, so a
  cost-preserving Lehman lift is automatically exact on every rich row;
- standard clutter parallelization converts that weighted gap exactly into
  an unweighted cardinality gap, but an arbitrary MNI minor of the
  parallelization need not retain the original global threshold after lift;
- at the first feasible four-player richer suffix, every failure has the
  four-co-singleton `1/3` vertex, the unique surviving fractional packet;
- projective-plane incidence packets satisfying the overlap-sensitive bound
  `b(q+2-b)>cd+binom(d,2)` or the local bound `d<2(q+2-b)` are eliminated by
  a safe star rounding, where `c=|A intersect B|` and
  `d=|A setminus B|`; this includes
  every such packet of order at most six; a two-sided convex Lehman-row
  interpolation eliminates every finite projective-plane packet in every
  order, without a Desarguesian assumption;
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
   row becomes a forbidden exact-game rooted cover. The unit-gap and
   deficit-preserving calculations should likewise be treated as proposed
   bridges to this classical theory, not as extensions of Lehman's theorem
   unless specialist review confirms that characterization.
   Király and Pap (2016),
   [*An extension of Lehman's theorem and ideal set functions*](https://doi.org/10.1016/j.dam.2015.07.035),
   give a minor-compatible extension combining covering and packing
   inequalities and a separate theory of ideal unit-increasing set
   functions. Their framework is a serious candidate antecedent or tool for
   the present cost/label augmentation; no claim of separation from it should
   be made until a specialist checks whether the unit-gap system embeds in
   their pair or set-function constructions.
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
rules out rank-two packets by combining one-cycle alternating rounding with
the real-valued exact-face budget.

The later targeted search inspected Cornuéjols--Guenin--Tunçel's primary
Lehman-matrix paper and the classical minimally-nonideal theorem it records.
That source supplies the matrix identity and regularity, not the poor-label
density argument, the two-sided label residual, its subset face budget, or
the bridge to exact-game tight faces.  Király--Pap's full primary paper was also checked: its
minor-compatible pair-of-clutters theorem and ideal set functions do not
state the two-label interpolation or the residual conservation law, although
their framework may still be relevant to the unresolved cost-aware minor
lift.  These are absence findings rather than a definitive novelty
determination.

A targeted finite-geometry search found adjacent theory of semiarcs, tangent
blocking, and secant-avoidance.  Earlier drafts used Segre's arc-extension
theorem for the Desarguesian order-seven case.  The current proof no longer
depends on that theorem: at a point on exactly one gaining line, a two-sided
Lehman interpolation normalizes whichever poor load yields the applicable
exact-face inequality.  This closes every finite projective plane in every
order.  The manuscript claims neither the projective-plane incidence
identities nor positive Lehman matrices as new.  The candidate contribution
is the exact-face interpolation and its labeled-packet exclusion.  No source
found in this pass states that combination; the absence is not a definitive
novelty result.

## Defensible novelty statement

Pending expert review, the strongest defensible formulation is:

> We combine stagewise Lmin duality with exact coalition-face witnesses to
> show that every slack richer suffix in an exact game induces a minimal
> balanced trace-transport certificate.  This dimension-free obstruction
> yields a human exact-partition classification through four players and a
> sharp `2|3` versus `2|4` richer-side threshold.  Every two-poorer failure
> moreover forces a nonintegral active trace hypergraph, hence an odd
> balanced-matrix obstruction, and graph-like underloaded packets are ruled
> out by a real-valued singleton overload. Exact singleton faces more
> generally forbid every safe rooted
> integer fibre of the supported tight-coalition semigroup, unifying the
> subsequent rounding arguments. Positive Lehman cores canonically generate
> those fibres.  A two-sided label residual extends to arbitrary dual-row
> subsets and converts aggregate residual into a quantitative rich-face slack
> budget; it contains both singleton exclusions and canonical internal-face
> amplification.  A two-label density test subsumes the odd-cycle and coarse
> projective-plane roundings; the co-singleton survivor lies on the
> opposite-sign side. At four rich players the unique surviving
> fractional packet is
> the co-singleton `1/3` cover. A projective-plane star-rounding argument
> further excludes every incidence packet satisfying a simple-point density
> inequality, including every such packet of order at most six; a two-sided
> Lehman-row interpolation excludes every finite projective-plane packet in
> every order. Three
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
