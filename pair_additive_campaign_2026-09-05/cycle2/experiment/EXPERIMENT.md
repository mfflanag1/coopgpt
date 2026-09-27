# Bounded coupling experiment and independent family audit

5 September2026. This lane wrote only inside `/private/tmp/coopgt-pairadd-cycle2/experiment`; prior campaign and release files were preserved.

The cycle found a genuine transfer inequality between two reduced gadgets, then independently checked the corrected all-size path family supplied by the theory lane. The resulting internal-player ratio is `1/6+1/(2q)`, tending to1/6. This is an upper bound on the possible uniform protection constant, **not** a proof that the constant vanishes. No new opposing-selector distance theorem is established here.

## Frozen first gate and complete visited-cell record

Start with two block-diagonal copies of the reduced nine-player gadget. There are54 directed cross-block matrix entries across `A,B,C`. The predetermined increment grid was `{1/2,1,2,3}`, at most216 cells, ordered by matrix, row, column and increment. Every game retained the six original matching triples, whose total is16. A feasible nonnegative covering allocation at total16 certifies both the integral optimum and nonempty entire core. An infeasible total16 cell is recorded only as infeasible at that fixed total; this does not assert that its actual-total game has empty core.

The baseline exactly reproduced coordinate fraction5/18 and normalized distance11/24. The search stopped at its first exactly certified contraction after27 cells:21 feasible at fixed total and6 infeasible in the floating screen. The other189 planned cells were not visited. `manifest.json` records the entire prescribed entry list/grid; `single_entry_records.json` records every visited cell, including negative cells and complete selector stages. This is bounded negative evidence, not exhaustive coverage of all cross entries or a classification over continuous increment parameters.

For all21 already-computed feasible cells, the six original matching-team local distances were computed without additional LPs. None exceeded4/3 beyond floating tolerance; see `local_team_ratios.json`. No two-entry scan was undertaken.

## Finite exact coupler

The first contraction adds only `A_{c_0,d_1}=2` between the two blocks, where each block is named `(a,b,c;d,e,f;g,h,i)`. Total16 remains certified. Exact progressive optimization gives the complete two selectors and all18 ideals in `candidate_exact.json`; the minimum ratio is11/45 and the normalized selector distance is91/240. One target is `d_0`, with full leximin payoff11/15 and ideal3.

The mechanism is short. Matching equalities give `b_1+d_1+h_1=3`; the new triple `(c_0,d_1,h_1)` also has worth3. Hence

```
c_0 >= b_1.
```

At the first leximin floor, all small matched triples fix `a_s=f_s=i_s=1/3`. Each original block obeys the budget `c_s+d_s+e_s+h_s<=3+f_s`. The second block also has `b_1>=c_1+e_1-f_1`. Summing these with the transfer inequality gives

```
c_1+e_1+d_0+e_0+h_0 <= 3+f_0+f_1 = 11/3.
```

Thus the next common floor is at most11/15. The saved cover attains it with all five displayed terms equal, so `d_0=11/15` is forced throughout the second optimal face and cannot change at later full lexicographic stages. The matching equality bounds `d_0<=3`. Repeating the old core point `(0,0,0;3,1,1;3,0,0)` across both blocks still covers every new triple and attains `d_0=3`.

`verify_finite_coupler.py` checks these proof inputs using only standard-library `Fraction`: all648 triple inequalities for the saved two selector points and ideal witness, the matching certificate, coefficient cancellation and attained two-stage bound. It explicitly does not pretend that the displayed descending selector's full optimality follows from a mere feasibility check; that came from the separate exact staged computation.

The six exact local matching-team ratios for this witness are `(4/3,8/45,23/60,4/3,4/45,4/15)`. Hence it does not supply the above4/3 local-team signal needed for the separate cloning/distance route.

## Zero-small-team diagnostic: proposed amplification fails

At the coordinator's request, a bounded diagnostic deleted the within-block entry `B_ai=1`, retained the same directed link and tested precisely1,2,3 blocks, at fixed totals7,14,21. Complete exact `x,z,H` are saved in `zero_chain_1.json` through `zero_chain_3.json`.

| Blocks | Exact minimum coordinate fraction | First-block d payoff / ideal |
|---|---:|---:|
|1|3/8|(3/4)/2|
|2|1/3|(2/3)/2|
|3|1/3|(2/3)/2|

The three-block middle `e` player becomes fixed at zero with ideal zero. Full leximin correctly treats it as a fixed coordinate and continues to later levels. Thus an apparent floor recurrence that counted that player as having a positive ideal was invalid. These finite checks corroborate the theory lane's structural obstruction; they do not support an all-size vanishing ratio. No zero-small-team cases beyond three blocks were searched.

## Fixed-small-team path: exact controls and corrected ideal

For the fixed original entry `B_ai=1`, the theory lane proposed `q>=3` linked blocks and second full leximin floor `t=1/3+1/q`. Exact checks were made only for `q=3,4`, fixing the small matched triples at the first optimum1/3, optimizing the next floor, and maximizing the target coordinate over that whole second optimal face. This certifies the target's **full** leximin payoff even though the remaining later coordinates were not computed.

| q | Exact second floor / target payoff | Exact internal e ideal | Target ratio |
|---|---:|---:|---:|
|3|2/3|2|1/3|
|4|7/12|2|7/24|

The initially proposed ideal3 witness was rejected: it puts a target-block `a=i=0` alongside a prefix-block middle-sector player of payoff0, violating a mixed triple of value1. The corrected records retain all violated rows of that rejected witness, alongside actual exact ideal-attaining points. The final proposed prefix/target/suffix witness with ideal2 was then independently validated for all block counts by finite type checks below. No ideal3 statement is retained for incoming-link e players.

## Independent audit of the all-size theorem

The audited statement is `../theory/COUPLED_CHAIN_THEOREM.md`. Its conclusion is for every internal `e_s`, `s>=1`: exact full-lex payoff `1/3+1/q` and exact entire-core ideal2. This does **not** assert that its displayed floor cover is already the whole final leximin vector.

The second-floor proof is valid. At first floor1/3, small matching equalities force the three named anchors in every block. A local triple gives `c_0<=4/3`. The link and local cross inequalities give `c_{s-1}>=c_s+e_s-1/3`. Their sum bounds the next floor by `1/3+1/q`; the supplied cover attains it. Equality forces all incoming-link e coordinates, as well as the terminal c coordinate, at that floor, regardless of subsequent lexicographic stages.

The entire-core ideal upper bound is also valid and materially uses mixed triples. If `mu` is the minimum first-sector payoff, every within-block `C_eg=3` pair combined with that player implies `c_r<=1+mu`. An incoming link therefore gives `b_s<=1+mu`. The local crossing inequality gives `e_s<=b_s-c_s+f_s`; use `c_s>=mu` and `f_s<=1` to conclude `e_s<=2`.

The explicit floor cover and ideal-attaining witness were checked independently without enumerating an arbitrary number of blocks. In `verify_family_finite_types.py`:

- The first floor block is checked directly. All internal floor blocks are affine in `u=1/q,v=s/q`, in the polygon `0<=u<=1/3, u<=v<=1-u`; each of its four vertices passes every original triple and every sector-minimum mixed-pair inequality. Affineness therefore proves coverage for every permitted internal block.
- Every noncoupler mixed triple contains at most one positive pair entry. The pair inequalities together with the global sector minima cover all such triples, including triples spanning three different blocks.
- For a link, the source c row of B is zero and the only possible extra C contribution is the target's `C_dh=1`. The two resulting interface inequalities follow at the endpoints of `b_next in[1/3,4/3]` and hence throughout this interval.
- The ideal witness uses the three block types `P=(0,1,1;1,1,1;2,1,0)`, `E=(0,1,0;1,2,1;2,1,0)`, `D=(0,0,0;2,1,1;3,1,0)`. All local triples and mixed-pair conditions pass. All four allowed transitions `P→P,P→E,E→D,D→D` cover the new link triples exactly where required.

The standard-library verifier passed216 original-triple checks and216 mixed-pair checks across eight finite affine/ideal types, plus all interface cases. This is a finite symbolic reduction for all q, not a numerical census with an unproved extrapolation. The positive integral matching and covering allocation both total8q, proving the correct integral grand value and entire-core admission. All9q players remain present.

No defect was found in the corrected all-size theorem. It proves `c_pair<=1/6`; it leaves `c_pair>0` versus `c_pair=0`, the sharp constant, and the opposing-selector distance problem unresolved. Priority was not investigated by this experimental lane.

## Commands and artifacts

Original working directory: `/private/tmp/coopgt-pairadd-cycle2/experiment`.

```
/private/tmp/coopgt-research-20260904/.venv/bin/python coupling.py
/private/tmp/coopgt-research-20260904/.venv/bin/python zero_chain.py
/private/tmp/coopgt-research-20260904/.venv/bin/python fixed_one_chain.py
python3 verify_finite_coupler.py
python3 verify_family_finite_types.py
```

The first three discovery/check drivers reuse the reviewed campaign's progressive selector and exact optimizer; paths and hashes are recorded in `manifest.json`. They require the existing NumPy/SciPy/Z3 environment. The last two verifiers use only Python's standard library and saved exact input artifacts. Log files preserve completed outcomes. No broad random continuation, interface constant optimization, full2^n coalition census, or additional block-count search was used.
