# Initial paired synthesis

The four initial registered supports were optimized once each. All full-model certificates passed the independently authored raw-matrix checker. CW-05 and CW-06 remain reserved and unoptimized. CW-01 and CW-04 are selected for interpretation because they have matching exact primal/dual bounds and distinct incidence structures.

| Support | Full-model lower | Certified upper | Verified relaxed feasible value |
|---|---:|---:|---:|
| CW-01 | 5/18 | 5/18 | 20/51 |
| CW-02 | 5/18 | <278/1000 | 47/130 |
| CW-03 | 5/18 | <278/1000 | 9583/24411 |
| CW-04 | 4/17 | 4/17 | 2467/7083 |

The exact rational bounds for CW-02/CW-03, with positive gaps approximately9.12e-11 and5.87e-11, are retained in paired/INITIAL_RESULTS.json. Their rounded display is an upper bound, not an asserted exact optimum. Every full-model upper is below1/3; every displayed relaxed point is above1/3. Relaxation values are feasible lower bounds only, not certified relaxation maxima. These are fixed-P all-weight results, not whole-market subsidy upper bounds or a new global theorem.

Solves ran sequentially; the driver elapsed2.596seconds. No retries were used. Reproduction driver: src/run_initial.py; it intentionally refuses to overwrite existing initial outputs. The generator/checker source hashes and registry digest are embedded in every paired artifact. The frozen registry was not modified.

The next gate requires a reusable parametrically stated relation and exact derivation. More below-threshold cases or a routine fixed-support LP dual do not suffice. Interpretation is testing whether elementary original-core propagation or a sector-cycle relation explains the relaxation gap. Established deletion/duality consequences will be labelled as such.
