# Reserved-support tests after the frozen conjecture

The residual-propagation sufficiency conjecture was saved and hashed at17:00:14UTC before either reserved support was optimized. Statement SHA256:51154b5ac224dd80446f0671c5bf7af2fca7955ea187dc8ceee8b93b2025c448. The six-support registry is unchanged.

| Support | Full-model lower | Certified full-model upper | Old relaxed feasible J | RP-enriched feasible J |
|---|---:|---:|---:|---:|
| CW-05 | 5/18 | <278/1000 | 11084/30573 | 110/381 |
| CW-06 | 95/402 | 95/402 | 2257/6501 | 2454/9337 |

Every full certificate passed the independent rational checker. CW05 has a positive rational recovery gap; its exact upper is retained in heldout/RESULTS.json. No exact optimum claim is made there. The old and enriched diagnostic points passed their semantic rational checks, including every RP row for the latter.

The enriched numerical solves did not find a violation of1/3. Their exact feasible values are NOT upper certificates. Thus the all-size RP-sufficiency conjecture survives these two bounded discovery tests but remains unproved, including absence of exact enriched upper certificates for these finite supports. The full-model certificate cannot substitute for that missing weaker-relaxation upper.

All six registered supports are now used. Do not generate more supports in this campaign. No retries have been used. Heldout driver elapsed1.283seconds, ran sequentially, and is retained as src/run_heldouts.py. The only justified next action is a bounded analytic/dual aggregation attempt on the frozen conjecture. The cycle-projection restatement is retired unless a concrete new cancellation is found; it does not pass the mechanism gate.
