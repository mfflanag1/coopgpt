# Four-player Lmin minimality program

## Sharp theorem (exact symbolic certificate)

The five-player exact lower-envelope pair in the manuscript is
dimension-minimal.  A hostile external review independently reproduced the
classification and counterexample and found no mathematical error, while
requiring substantial attribution and reproducibility revisions:

> If `|N| <= 4`, normalized Lmin is coalitionally monotone on every pair of
> exact games that differ by increasing the worth of one coalition.

Singleton bumps are already covered in every dimension.  For four players,
proper two-player targets are structurally controlled by the pair theorem in
the manuscript.  The only unresolved shape is therefore `|S|=3`, `|P|=1`.
By efficiency, raising `v(S)` is exactly the operation of tightening an upper
bound on the one outside player's payoff.

## Prior-art correction and the sharp classification

After translating singleton values to zero, the manuscript's selector is the
ordinary Lmin solution.  Biswas, Parthasarathy, Potters, and Voorneveld (1999,
Theorem 3) prove that every exact game with at most four players has a large
core.  Dietzenbacher (2021, Lemmas 3.2--3.3 and Theorem 3.5) proves that large
core games are egalitarian stable and that PES=Lmax is coalitionally
monotone on the egalitarian-stable domain.

Llerena and Mauri (2017) define an exact partition game as a balanced game
having a core allocation whose cumulative richest payoff strata are tight.
They show that the Dutta--Ray solution on this class is the Lorenz-dominating
core allocation.  Dietzenbacher and Yanovskaya (2020) develop its
antiduality.  Thus suffix tightness and its Lorenz consequence are established
prior art.

The formerly missing statement is now verified in exact linear rational
arithmetic:

> **New sharp classification.** Every singleton-normalized exact game with at
> most four players is an exact partition game witnessed at Lmin.  Consequently
> `Lmin = PES = Lmax` on that domain.

The distinction remains load-bearing: Lmin and Lmax can differ on general
egalitarian-stable games, so largeness alone does not identify them.  The
primary verifier `src/verify_n4_exact_lmin_pes_bridge.py` establishes the
bridge by showing that every richer-player suffix at a strict Lmin payoff gap
is tight.  It checks all 1, 3, and 7 nonconstant ordered payoff-stratum
compositions for two, three, and four players.  Seven patterns are impossible
already; in the other four the positive-suffix-slack query is nonvacuously
infeasible.  Removing either the exact-face witnesses or the
individual-pinning dual programs opens satisfiable negative-control cases.

The second verifier
`src/verify_n4_exact_lmin_pes_bridge_primal.py` formulates Lmin optimality
without KKT multipliers or complementarity.  It shares the exact-face system,
normalization, and Z3 solver with the primary encoding.  It enumerates the
tight-coalition set, excludes primal
leximin-improving tangent directions at every stratum, and then asks whether
the remaining pattern has a definition-level exact realization.  It gives the
same eleven-case classification.  A third exact-LP checker,
`src/verify_n4_exact_lmin_pes_bridge_witnesses.py`, independently replays a
small integer exact game for every realizable stratum pattern.

The classification is dimension-sharp on the known witness.  Exact
acceptable-polyhedron vertex enumeration proves that both five-player games
have large cores.  For the base game,

```
Lmin = (1,1,13/2,5,13/2),
PES  = (2,0,6,6,6),
```

whereas at the two-generator endpoint both selections equal
`(2,0,6,6,6)`.  Thus the counterexample can be read as a transition from an
Lmin/PES disagreement to agreement.  Lmax remains `(2,0,6,6,6)` across the
bump, and the base Lmin point has strict richer-suffix slack
`phi({3,5})=13>12=v({3,5})`.  Largeness alone therefore does not imply the
exact-partition property, and sharpness holds for the classification itself.

## Exact and targeted evidence

The deterministic screen in
`src/audit_n4_exact_lmin_minimality.py` constructs exact pairs by adjoining a
common-sum allocation that lowers only `S={2,3,4}`.  Its full campaigns found:

| endpoint generators | draws | only-S pairs | binding pairs | exact drops |
|---|---:|---:|---:|---:|
| exactly 2 | 500,000 | 912 | 545 | 0 |
| 2 through 6 | 750,000 | 8,055 | 1,948 | 0 |

The observed labeled target sign patterns were even more rigid than mere
monotonicity.  In the two-generator run they were `+++` (468), `0+0` (38),
`+00` (31), and `00+` (8).  In the broader run they were `+++` (1,775),
`0+0` (85), `+00` (81), and `00+` (7).  No pattern containing a minus sign
appeared.  All six player-mergings of the five-player witness also remove the
drop.  In a separate exact-rational check of 100 randomly generated,
singleton-normalized exact four-player games, Lmin and PES agreed in every
case.

These random campaigns remain discovery evidence, not the proof.  The theorem
evidence is now two exhaustive exact encodings: the symbolic KKT/exact-face
certificate and the independently formulated primal Lmin-optimality test above.

## Structural clue from trying to compress the witness

The five-player certificate first pins the outside player and target player 1
at a common two-player bottleneck.  Three target coordinates remain.  A
tight coalition involving player 1 pins one of those three, and the last two
equalize; when player 1 rises, that intermediate cap relaxes, allowing the
previously lower coordinate to rise while the two previously higher
coordinates fall.

With four players, the same first bottleneck leaves only two target
coordinates.  An attempted inverse construction would need tight coalitions
`ac` and `bc` at the old Lmin point, with `c` above the outside player.  Exact
attainment of singleton `c` would then give a core point `z` with `z_c=0` and

```
z_a >= v(ac) = phi_a + phi_c,
z_b >= v(bc) = phi_b + phi_c,
z_p >= 0.
```

Their sum exceeds efficiency whenever `phi_c>phi_p`.  This explains why the
obvious four-player compression is incompatible with exactness and suggests
the final proof: show from the two Maschler stage sequences that any target
drop forces precisely these two tight coalitions (up to relabeling).

## Completed proof route and remaining audit tasks

1. Completed: encode exactness definitionally by a core displacement attaining
   every proper face.
2. Completed: encode every progressive Lmin common-level program and every
   individual pin by exact KKT multipliers.
3. Completed: prove all richer-player suffixes tight, first by exact finite
   encodings and now by a structural protector-coalition argument; identify
   this as exact-partition structure and invoke the Llerena--Mauri Lorenz
   theorem to obtain `Lmin=Lmax`.
4. Completed: combine the bridge with Biswas et al. and Dietzenbacher to prove
   monotonicity through four players and sharpness at five.
5. Completed internally: re-audit every KKT sign, complementarity condition,
   homogeneity normalization, and the suffix-tightness-to-Lorenz deduction;
   add an independently formulated primal Lmin-optimality test, explicit
   witness replay, and
   locally irreducible unsatisfiable cores for the four nonvacuous suffix-slack
   cases (15, 59, 40, and 64 assertions, down from 158--510).
6. Completed: hostile external audit independently recomputed exactness, Lmin,
   Lmax, the eleven-case classification, witnesses, and five-player sharpness.
   It found no mathematical error and required the attribution and
   reproducibility changes recorded here.
7. Completed internally: replace the finite enumeration as the theorem proof
   by a human argument using the published egalitarian-core transfer-blocking
   property, a dimension-free fractional protector-packing inequality, exact
   singleton witnesses, and the three possible four-player boundary
   geometries.
8. Remaining: obtain hostile external review of the new human proof and
   complete MathSciNet/zbMATH and expert citation-chain review of the narrower
   classification claim.  Reduced cores remain same-solver audit conveniences,
   not standalone Farkas proofs.

The self-contained reviewer packet is
`paper3/N4_LMIN_LMAX_REVIEW_PACKET.md`.  The theorem now has a structural
human proof; the prior computer-assisted classification remains as an
independent exact-rational audit.

No claim is made that the five-player failure extends to every higher
dimension by null players: a naive null extension changes several coalitions,
not a single coalition, and therefore does not preserve the required bump
pair.

## Focused novelty check (2026-08-03)

Exact-phrase and terminology searches for `exact games + Lmin + Lmax`, `Lmin
solution + exact games + four players`, and `leximin stable allocation + exact
game` located the standard defining and neighboring papers but no statement of
the bridge above.  The closest results inspected were:

- Arin--Iñarra (2001), introducing Lmin on balanced games;
- Arin--Kuipers--Vermeulen (2003), defining Lmax and characterizing it on
  large-core games;
- Llerena--Mauri (2017), defining exact partition games and proving that the
  Dutta--Ray solution gives their Lorenz-dominating core allocation;
- Dietzenbacher--Yanovskaya (2020), developing antiduality on that class;
- Dietzenbacher (2021), proving PES=Lmax and coalitional monotonicity on the
  egalitarian-stable domain and explicitly observing that exact games through
  four players lie in that domain.

The exact-partition condition and its Lorenz consequence are therefore not
new.  None of the inspected sources states the narrower inclusion that every
exact game through four players is exact partition at Lmin.  This remains a
focused search, not a definitive MathSciNet/zbMATH novelty opinion.

After obtaining the structural proof, a direct citation check identified the
protector property as prior art: it is the transfer-blocking characterization
of the egalitarian core in Arin--Iñarra (2001), applied here to Lmin.
Additional exact-phrase searches for
`Lmin + exact partition`, `Lmin solution + exact games + four players`,
`leximin + protector coalition`, and `exact game + unique richest + Lmin`
again returned the standard exact-partition/antiduality and monotonicity papers,
but no structural proof of the four/five threshold or combination with exact
singleton witnesses.  This raises only the plausibility that the
low-dimensional classification and proof mechanism are new; it still does not
replace expert citation-chain, MathSciNet, or zbMATH review.

The fractional protector-packing inequality (FP) was derived after that
search.  Its algebra is dimension-free, but its novelty has not been checked
against the hypergraph-packing, balanced-collection, or egalitarian-core
literatures.  It must therefore be presented as a candidate structural tool,
not as an established new theorem of independent significance.
