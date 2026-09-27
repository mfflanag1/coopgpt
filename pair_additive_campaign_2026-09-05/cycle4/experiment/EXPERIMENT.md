# Exact1/9 witness from a bounded inverse-design gate

The first inverse-design LP produced an exact counterexample to the proposed positive-first-level bound `H_i<=6 tau`. A deterministic restriction gives a **21-player complete strict pair-additive game**, with seven players per sector, pair entries in `{0,1,2,3}`, and nonempty core. One player's full ascending leximin payoff is **1/3**, and its actual ideal is **3**, yielding **1/9 < 1/6**.

This is a finite counterexample to the1/6 protection conjecture. It does not establish the optimal universal constant, an infinite amplification family, or priority over existing literature. No further targets or constants were pursued after certification.

## Declared gate and actual coverage

`manifest.json` was saved before optimization. The design fixed the first-floor dual certificate from the earlier seven-block composition in sector orientation201, while freeing exactly its **65 positive pair-entry positions**. All other entries stayed zero; all full triples remained available. The normalized critical budget had seven positive coefficients summing9, with six target coefficients1 and one coefficient3. The six coefficient1 targets were the complete planned parameter set. The coefficient3 target was excluded because its exact budget cap3 cannot violate6.

The inverse LP used191 variables:65 pair entries,63 payoffs in a first-floor witness u, and63 payoffs in an ideal witness y. Both points obeyed all **9,261 triple-cover inequalities**, all matching equalities, and nonnegativity. Additionally u>=1, each positive-budget coordinate of u equaled1, and the primitive budget right side was normalized to9. There was no fixed-total normalization: matching values varied linearly with the pair entries, and matching efficiency determined each point's total. The nonnegative budget bounded each selected objective by9, so the relevant optimization objective was bounded despite possible unused recession directions.

The first target, original index6 (a2), attained the exact budget ceiling9. The run stopped immediately after **one of six** planned LPs; the other five were not run. The floating optimization took approximately0.021 seconds. Raw rationalized outputs and LP multipliers are in `records.json`; the original63-player points and matrices are frozen in `candidate.json`. The LP ceiling9 is independently justified by the retained nonnegative budget, and its attainment is independently checked in rational arithmetic, so no floating optimality claim is needed for the result.

Calibration replays confirmed the old finite1/6 witness and both earlier exact2/9 compositions. Their saved standard-library verifiers ran in this cycle's owned `calibration/` directory. The replay hashes and outcomes are in `calibration_summary.json`. These replays occurred after initial discovery and before final certification/reporting; the source certificates themselves predated this gate.

## Canonical21-player instance

Use zero-based names `a0,...,a6`, `b0,...,b6`, `c0,...,c6` for the three sectors. Every triple has value `A_ij+B_ik+C_jk`; only full triples are productive. All unspecified pair entries are zero. The **16 nonzero entries** are:

```text
A01=2, A21=2, A55=1, A56=1
B00=2, B03=2, B12=1, B25=2, B33=3, B54=1, B55=2
C11=2, C13=2, C44=1, C64=1, C66=1
```

The seven matching triples, in order, are

```text
(0,0,0), (1,2,2), (2,1,1), (3,3,3),
(4,4,4), (5,5,5), (6,6,6).
```

Their weights are `2,1,4,3,1,3,1`, summing to **T=15**. The following payoffs cover every one of the343 triples and sum to15:

```text
u_A = (4,1,4,1,1,7,1)/3
u_B = (1,7,1,1,1,1,1)/3
u_C = (1,1,1,7,1,1,1)/3

y_A = (2,0,0,3,0,1,0)
y_B = (0,4,0,0,0,0,1)
y_C = (0,0,1,0,1,2,0)
```

The point u is a first-floor witness; it is **not claimed to be the complete leximin selector**. A face argument below proves the target's value in the complete selector. The matching and either whole cover certify the true integral optimum and core nonemptiness. Summing triple covers along a coalition's matching supplies every coalition inequality.

## Ordinary proof of the target

Every core point obeys the seven matching equalities. Take three copies of the first matching equality and one of each other matching equality. Their right sides sum to19. Subtract the six valid triple-cover inequalities

```text
(a0,b1,c3) >= 6
(a0,b4,c0) >= 2
(a0,b5,c0) >= 2
(a1,b3,c2) >= 1
(a2,b2,c5) >= 2
(a5,b6,c4) >= 3.
```

The right sides subtracted sum to16, and the exact coefficient identity gives the whole-core budget

```text
a3 + a4 + a6 + 3 b0 + c0 + c1 + c6 <= 3.
```

Its nonnegative coefficients sum to9. Therefore any common payoff floor t satisfies `9t<=3`. The saved u attains t=1/3, so this is the true positive first leximin level. On its entire first optimal face, every positive-budget coordinate must equal1/3, including **a3**. Subsequent leximin stages cannot change that coordinate, so the complete selector has `x_a3=1/3`.

The target's matching equality `a3+b3+c3=3`, together with nonnegativity, gives `H_a3<=3`. The saved whole-core point y attains a3=3, proving `H_a3=3`. Thus `x_a3/H_a3=1/9`, and `H_a3=3>6(1/3)=2`.

## Reduction and verification scope

The original63-player witness was restricted to the seven matching teams used by its budget: original matching indices `0,3,4,6,9,13,15`. Every proof triple uses only players in that union. Restricting each saved point therefore preserves all remaining triple covers; its total equals the selected matching's weight. The budget, positive first-floor witness, and ideal attainment survive. Dividing pair weights and payoffs by3 gives the instance above. **No claim is made that the whole core, all ideals, or full selectors are preserved by deleting players.**

`reduced_candidate.json` stores the matrices, matching, both witnesses, six proof triples, budget multipliers, and explicit original-sector embedding. `verify_reduced.py` uses only the Python standard library. It rebuilds all343 triple values, checks both complete covers (686 checks), matching efficiency and nonnegativity, and the nonnegative budget coefficient identity. `verify_candidate.py` separately verifies the original63-player construction with18,522 triple checks. Both pass under `python3 -O`; assertions are not used as proof gates.

Replay the final certificates from this directory:

```sh
python3 -O verify_reduced.py
python3 -O verify_candidate.py
python3 -O calibrate.py
```

Optional regeneration uses the supplied NumPy/SciPy environment:

```sh
python inverse_design.py
python reduce_candidate.py
```

The generation environment was `/private/tmp/coopgt-research-20260904/.venv/bin/python`. Parent-campaign paths resolve relatively when packaged under `cycle4/experiment`, with the recorded scratch source as fallback. The inverse LP is a use of standard linear programming and primal/dual certificates; no claim of methodological novelty is made.
