# Four-player Lmin minimality program

## Sharp theorem (exact symbolic certificate)

The five-player exact lower-envelope pair in the manuscript is
dimension-minimal, subject to external review of the new symbolic lemma:

> If `|N| <= 4`, normalized Lmin is coalitionally monotone on every pair of
> exact games that differ by increasing the worth of one coalition.

Singleton bumps are already covered in every dimension.  For four players,
proper two-player targets are structurally controlled by the pair theorem in
the manuscript.  The only unresolved shape is therefore `|S|=3`, `|P|=1`.
By efficiency, raising `v(S)` is exactly the operation of tightening an upper
bound on the one outside player's payoff.

## Literature bridge and the new missing-link theorem

After translating singleton values to zero, the manuscript's selector is the
ordinary Lmin solution.  Biswas, Parthasarathy, Potters, and Voorneveld (1999,
Theorem 3) prove that every exact game with at most four players has a large
core.  Dietzenbacher (2021, Lemmas 3.2--3.3 and Theorem 3.5) proves that large
core games are egalitarian stable and that PES=Lmax is coalitionally
monotone on the egalitarian-stable domain.

The formerly missing statement is now verified in exact linear rational
arithmetic:

> **Four-player bridge.** On every singleton-normalized exact game with at
> most four players, `Lmin = PES = Lmax`.

The distinction remains load-bearing: Lmin and Lmax can differ on general
egalitarian-stable games, so largeness alone does not identify them.  The new
verifier `src/verify_n4_exact_lmin_pes_bridge.py` establishes the bridge by
showing that every richer-player suffix at a strict Lmin payoff gap is tight.
It checks all 1, 3, and 7 nonconstant ordered payoff-stratum compositions for
two, three, and four players.  Seven patterns are impossible already; in the
other four the positive-suffix-slack query is nonvacuously infeasible.
Removing either the exact-face witnesses or the individual-pinning dual
programs opens satisfiable negative-control cases.

The bridge is dimension-sharp on the known witness.  For the five-player base
game,

```
Lmin = (1,1,13/2,5,13/2),
PES  = (2,0,6,6,6),
```

whereas at the two-generator endpoint both selections equal
`(2,0,6,6,6)`.  Thus the counterexample can be read as a transition from an
Lmin/PES disagreement to agreement.

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

These remain discovery evidence and independent stress tests, not the proof.
The theorem evidence is the symbolic KKT/exact-face certificate above.

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
3. Completed: prove all richer-player suffixes tight in all eleven stratum
   patterns; deduce Lorenz dominance and `Lmin=Lmax`.
4. Completed: combine the bridge with Biswas et al. and Dietzenbacher to prove
   monotonicity through four players and sharpness at five.
5. Remaining: obtain an independent hostile audit of the symbolic encoding and
   the literature bridge; ideally extract small Farkas certificates for the
   eleven infeasible systems.

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
- Llerena--Mauri (2016), a reduced-game route to Lmax on a class containing
  large-core games;
- Dietzenbacher (2021), proving PES=Lmax and coalitional monotonicity on the
  egalitarian-stable domain and explicitly observing that exact games through
  four players lie in that domain.

None of those sources identifies Lmin with Lmax on four-player exact games.
This is a focused search, not a definitive MathSciNet/zbMATH novelty opinion;
the manuscript should retain cautious language until a specialist referee has
checked adjacent terminology such as lexicographically minimal/maximal,
Lorenz-stable, and exact-partition games.
