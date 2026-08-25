# n=7 exchange/tangent CEGAR pause checkpoint

Status: discovery only; paused by user after a completed exact separation round.
No theorem or game counterexample is claimed.

## Frozen cell

- seven players, total normalized to one;
- three coordinates satisfy `x_i>z_i`, four satisfy `z_i>x_i`, with no ties;
- candidate violation `||x-z||_1>5/6`, equivalently overlap below `7/12`;
- dimension-free selector anchors and seven singleton-zero exactness witnesses;
- every retained lex-improving direction requires an exactness-compatible tight
  coalition blocker.

The `0,+1,-1` menu is insufficient: its full 784 side-specific implications
admit a rational relaxation model.  The exact lower envelope of every model
tested so far fails at least one staged selector tangent test, so there is no
counterexample yet.  Conversely, the retained menu remains SAT, so there is
no UNSAT cell theorem yet.

The exact tangent CEGAR completed 20 rounds in
`n7_exchange_exact_tangent_cegar_rounds_00_19.json`, then two more completed
rounds in `n7_exchange_exact_tangent_cegar_rounds_20_21_pause.json`.  The final
row is deliberately `UNKNOWN/canceled`: it records the user-requested pause,
not a solver result.  The last completed round added

- Lmin direction `(1,-2,-2,1,1,0,1)`;
- Lmax direction `(2,-2,-1,1,1,-1,0)`.

The restart state contains 195 non-base side-specific directions, in addition
to the 84 ordered one-for-one base implications.  Exact separator coefficients
seen in the completed CEGAR rounds have absolute value at most four.  Several
intermediate models already had exact Lmax and only one missing Lmin tangent;
none had both selectors.

## Resume

From the repository root:

```bash
python3 verifiers/divergence/search_archive/n7_exchange_exact_tangent_cegar.py \
  --seed-menu verifiers/divergence/search_archive/n7_exchange_p3n4_seed_menu.json \
  --extra-direction 'min:-1,-3,0,2,1,2,-1' \
  --resume-cegar verifiers/divergence/search_archive/n7_exchange_exact_tangent_cegar_rounds_00_19.json \
  --resume-cegar verifiers/divergence/search_archive/n7_exchange_exact_tangent_cegar_rounds_20_21_pause.json \
  --rounds 40 --timeout-ms 600000 \
  --output /private/tmp/n7_exchange_exact_tangent_cegar_resume.json
```

A terminal `EXACT_N7_COUNTEREXAMPLE` is promotable only after an independent
exact reconstruction of all coalition values and both staged selectors.  A
terminal `UNSAT_CELL_CLOSED_BY_RETAINED_MENU` excludes only this sign-count
cell and still requires an unguarded replay and an independently formulated
certificate before promotion.
