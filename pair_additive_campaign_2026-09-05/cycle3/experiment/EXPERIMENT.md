# Bounded overlapping-interface pilot and composition gate

The initial deterministic 401-cell screen found a finite 27-player game attaining protection ratio **1/6 exactly**. This improves the earlier path family's asymptotic attainment of that upper bound. It does not prove a universal 1/6 lower bound or produce a smaller ratio. The same finite example refutes the proposed stronger same-sector spread inequality `R_i <= 3 x_i`.

A subsequent, explicitly authorized seven-block composition gate tested exactly two sector orientations. Both are now exactly certified: their minimum coordinate ratio is **2/9**, and the intended new central target has ratio **4/9**. This precise composition does not amplify the finite example. Mixed triples raise the child outputs while reducing the common first floor.

## Contract and calibration

There are three sectors of equal size. Every full triple has value `A_ij+B_ik+C_jk`, with nonnegative integer pair entries; every triple, including mixed triples, is available. Coalition worth is the maximum weight of an integral disjoint-triple matching. All players are retained. The core uses nonnegative payoffs, total integral optimum T, and all triple inequalities. A triple cover certifies every coalition inequality by summing along a matching. An equal-value integral matching and covering point certify T and core nonemptiness.

`x` is the complete ascending leximin selector. `z` is the complete descending-sorted lexicographic minimum. `H_i` is the actual coordinate maximum over the whole core. The initial screen computes both full selectors and every ideal. The composition gate computes the full ascending selector and every ideal; no claim about its opposing selector or distance is made.

Exact controls in `calibrations.json` reproduce:

- The old nine-player gadget: minimum ratio 5/18, complete x and z, and all H.
- The three-block path: designated internal e has x=2/3, H=2, ratio 1/3.

The source gadget in each block `(a,b,c;d,e,f;g,h,i)` is

```text
A = [[0,0,0],[2,0,1],[0,1,0]]
B = [[0,0,1],[1,0,0],[0,0,0]]
C = [[0,1,0],[3,0,0],[2,0,0]]
```

Its matching teams `(a,f,i)`, `(b,d,h)`, `(c,e,g)` have weights 1,3,4. The source-file hashes read by the initial run are saved in `manifest.json`.

## Complete initial parameter set and negative evidence

The run is deterministic: **no random seed is used**, and there is no random search. The declared cap was 401 cells or 900 seconds, with early stopping at an exact ratio below 1/6. All 401 cells completed in 106.097 seconds. Every parameter cell and output is preserved in `manifest.json` and `records.json`.

1. **81 closed three-interface cells:** choose roles i,j,k in `{0,1,2}`, and strength in `{1,2,3}`. Add equal-strength entries A(block0_i,block1_j), B(block0_i,block2_k), C(block1_j,block2_k).
2. **320 fork-plus-entry cells:** start with A(c0,d1)=2 and A(c0,d2)=2. Add one of the 160 remaining cross-block entries, at increment 1 or 2.

The covering LP supplies an admission check; 378 cells had an integral optimal covering dual matching, and 23 used an integral MILP matching of the same value. Every admitted cell computes the true matching total witnessed this way, which can exceed the uncoupled total 24. No fixed-total infeasibility is interpreted as global core emptiness. All 401 were admitted in floating arithmetic. Their minimum observed ratio was 1/6; none was below it. This is bounded numerical negative evidence, not an exact certification of all 401 cells or a universal theorem. Saved matching-team local selector-distance ratios also did not exceed 4/3 in the floating diagnostics.

## Exact finite attainment and failed spread bridge

Cell 7, `triangle_roles002_weight1`, adds only

```text
A(a0,d1)=1, B(a0,i2)=1, C(d1,i2)=1.
```

The new triple `(a0,d1,i2)` has value 3. The original nine-team matching has value T=24. Complete rational outputs, all ideals and both full-selector stage lists are in `finite_attainment_exact.json`.

Blocks 0 and 2 retain the old gadget's ascending selector and ideals. The descending selector changes and is saved separately. At the ascending selector, block 1 is

```text
(1/3,1/3,1/3; 7/3,1/3,1/3; 10/3,1/3,1/3).
```

Its ideals are `(1,2,3/2; 3,2,1; 4,1,1)`. In particular, b1 has `x=1/3`, `H=2`, ratio `1/6`; e1 also attains 1/6. The complete selector distance is 5/9.

There is a short proof of the target, independent of the optimizer. Unit-team matching equalities give a0<=1 and i2<=1. The new triple gives d1>=1, and `b1+d1+h1=3` gives b1<=2. The following whole-core point attains b1=2:

```text
block0 = (1,2,0; 0,2,0; 2,1,0)
block1 = (0,2,1; 1,0,0; 3,0,1)
block2 = (0,2,1; 0,0,0; 3,1,1)
```

The unit teams bound the first leximin floor by 1/3, and the saved full selector attains that floor. On its entire first optimal face, a0=i2=1/3, so d1>=7/3. Therefore b1+h1<=2/3; each is at least 1/3, forcing b1=h1=1/3. Thus the target value belongs to the full selector, not merely to an arbitrary max-min point.

For `R_i=max_{j in same sector} max_{p in core}(p_i-p_j)`, the same ideal witness has b1=2 and c0=0. Nonnegativity and H_b1=2 give the reverse bound, hence `R_b1=2 > 3x_b1=1`. This refutes that proposed bridge without refuting the 1/6 conjecture. `verify_bridge_counterexample.py` uses only the standard library, verifies all 1,458 triple covers for the two saved points, and checks the exact ingredients of the ordinary proof.

## Two seven-block composition cases: exact obstruction

Blocks 0,1,2 form the left finite gadget above. Blocks 3,4,5 form a copy whose original sector I is rotated to global sector K. Block 6 is an old base gadget. The three new interfaces, each of weight 1, join left output b1, central d6, and right output b4. Two right-sector maps were tested: `(I,J,K)->(K,I,J)` and `(K,J,I)`. This is the complete composition parameter set; no other rotations or broader recursive scans were run.

The 21 original matching teams give total 56 in both cases. All 9,261 triples are present; 1,301 have positive value. Zero-worth rows may be omitted in the LP because all payoffs are nonnegative, but all 9,261 are checked for every saved primal witness.

Both orientations have the following **exact**, fully certified values:

| Quantity | Value |
|---|---:|
| Integral optimum T | 56 |
| Common first leximin floor | 2/9 |
| Complete ascending leximin stages | 13 |
| Each child output b1,b4 | 8/9 |
| Minimum over all63 positive-ideal coordinate ratios | 2/9 |
| New central target b6 | 10/9 |
| True ideal H_b6 | 5/2 |
| New central target ratio | 4/9 |

The minimum 2/9 occurs, for example, at a2 with H_a2=1. The naive inherited child values 1/3 fail the mixed triple `(b1,f1,b4)`, which has value 2 in orientation 201. The true first floor is even lower than the preliminary 1/4 bound suggested by that one mixed triple.

A readable exact upper bound for orientation 201 is

```text
3 f0 + i0 + h1 + a2 + f3 + f5 + a5 <= 2.
```

All terms on the left are at least the common floor t, so `9t<=2`. To obtain this inequality, sum three copies of the unit-team equality in block0 and one copy of the unit-team equalities in blocks1,2,3,5 and the weight3 matching equalities in blocks1,4. This sum has right side 13. Subtract the following six triple inequalities, whose right sides sum to 11:

```text
(a0,d1,i2) >= 3
(a0,i3,i0) >= 1
(a0,h4,i0) >= 1
(a1,f2,i1) >= 1
(b1,f1,b4) >= 2
(d4,i5,a3) >= 3
```

Names here refer to original within-gadget roles; right-gadget roles use the stated sector map. Each displayed triple still contains one player from each global sector. The saved exact x attains 2/9 at every coordinate in the resulting inequality. This identifies the actual mixed-triple obstruction to simply transferring the child mechanism.

`composition_exact.json` and `composition_210_exact.json` save the complete rational x, all63 H values, all63 ideal witnesses, a rational dual for every ideal bound, and a rational dual for each forced coordinate at every full leximin stage. `verify_composition.py` imports no solver or candidate-generation code: it reconstructs the pair-additive tensor, checks the integral matching, all primal triple covers, and each dual coefficient identity and sign. Each orientation passes **592,704 triple checks and127 rational dual certificates**. Its first-stage and later-stage tests establish the complete ascending selector: on each saved optimal face the next listed group is forced, while the final saved x witnesses attainability and strictly higher values for later groups.

The composition does not support recursive amplification. The accurate conclusion is a no-go for these two specified finite templates, with an explicit mixed-triple mechanism. No impossibility theorem for other compositions is claimed.

## Reproduction

Run the commands below from this directory. The generation environment used Python3.13.5, NumPy2.5.2, SciPy1.18.1 and Z3 5.1.0 at `/private/tmp/coopgt-research-20260904/.venv/bin/python`. The three saved-certificate verification commands require only a standard Python3 installation and do not rerun searches.

```sh
python3 verify_bridge_counterexample.py
python3 verify_composition.py 201
python3 verify_composition.py 210
```

To regenerate discovery and exact solver outputs in the supplied dependency environment:

```sh
python pilot.py
python certify_attainment.py
python composition.py 201
python certify_composition.py 201
python composition.py 210
python certify_composition.py 210
```

Generation reuses the reviewed source gadget and exact selector implementation from the parent campaign. `pilot.py` first resolves the campaign relative to a packaged `cycle3/experiment` directory and retains the recorded local canonical path as a scratch-run fallback. Verification is entirely relative to this directory. Generated records are reproducible artifacts, not unpublished-priority certification; novelty comparison is handled separately by the parent campaign.
