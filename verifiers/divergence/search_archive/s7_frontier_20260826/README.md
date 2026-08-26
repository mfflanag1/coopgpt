# s7 frontier search archive (2026-08-25/26)

Discovery tooling behind PXC144/PXC145 (scratchpad copies; not release-replayed).

- `exactsel.py` — from-scratch exact staged selectors (Fraction simplex; float HiGHS only proposes active rows, every row is re-checked exactly).  Independently reproduced PXC143 before any search.
- `fastsel.py`, `search.py`, `alternate.py` — float hill-climb on the true selector distance (integer transfer moves, generator copy/remove) alternated with the exact tangent LP.
- `tangent_lp.py` — the cell-frozen tangent LP: freeze attaining generator per coalition, tight rows, payoff weak orders, zero pattern; maximize distance over generator entries; integerize; re-verify from scratch.
- `certs.py` — extracts the staged Farkas identities (dual LPs) that the PXC144/PXC145 primary verifiers replay.
- `family.py` — closed-form check of `H_m` (m=1,2,3 verified; larger m pending).
- `cegar_opt.py` + `cegar_thr_p3m4.{json,log}` — s6-style exchange relaxation at threshold 56/65 in the (3,4) sign cell with tangent-separator CEGAR: still SAT after two rounds (180 s, 587 s); killed at the end of the session.  No upper bound claimed.
- `n7_polished_56_65_raw.json`, `n8_best_raw.json`, `n9_best_raw.json` — raw search outputs before gcd reduction and generator pruning.

Laws: a first-crossing threshold witness is not the supremum — polish it; twin-split (halve a column) to lift dimension, never duplicate a column; re-verify every pruned generator set from scratch (dropping generators can change the game).
