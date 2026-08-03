# Four-player Lmin minimality program

## Candidate sharp theorem

The five-player exact lower-envelope pair in the manuscript may be
dimension-minimal:

> If `|N| <= 4`, normalized Lmin is coalitionally monotone on every pair of
> exact games that differ by increasing the worth of one coalition.

Singleton bumps are already covered in every dimension.  For four players,
proper two-player targets are structurally controlled by the pair theorem in
the manuscript.  The only unresolved shape is therefore `|S|=3`, `|P|=1`.
By efficiency, raising `v(S)` is exactly the operation of tightening an upper
bound on the one outside player's payoff.

## A promising literature bridge, and its precise missing link

After translating singleton values to zero, the manuscript's selector is the
ordinary Lmin solution.  Biswas, Parthasarathy, Potters, and Voorneveld (1999,
Theorem 3) prove that every exact game with at most four players has a large
core.  Dietzenbacher (2021, Lemmas 3.2--3.3 and Theorem 3.5) proves that large
core games are egalitarian stable and that PES=Lmax is coalitionally
monotone on the egalitarian-stable domain.

This does **not** yet prove the candidate theorem.  The missing statement is

> **Four-player bridge.** On every singleton-normalized exact game with at
> most four players, `Lmin = PES = Lmax`.

The distinction is load-bearing: Lmin and Lmax can differ on general
egalitarian-stable games, and largeness by itself has not been shown here to
identify them.  The current manuscript must not cite the two known theorems
as a proof until this bridge is established.

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

These are discovery facts, not theorem evidence.  The screen deliberately
labels itself finite and sends any floating drop flag to an exact replay.

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

## Proof tasks

1. Derive the complete four-player Maschler active-set alternatives after the
   outside-player cap becomes binding.
2. Show that every alternative containing a target decrease forces the
   `ac`/`bc` configuration above, or an equivalent exactness contradiction.
3. Alternatively, prove the four-player bridge `Lmin=PES` directly from the
   exactness inequalities used in Biswas et al.'s Theorem 3.
4. Once proved, combine it with Dietzenbacher's coalitional monotonicity of
   PES/Lmax to state the sharp dichotomy: valid through four players and false
   from five players onward (the latter by null-player extension of the
   five-player witness).
