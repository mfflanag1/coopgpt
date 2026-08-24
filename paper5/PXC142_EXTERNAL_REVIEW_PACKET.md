# Hostile external review packet — PXC142 saturation lock

Review target: the PXC142 block in paper5/divergence.tex and the exact
artifacts listed below. No external specialist has reviewed this result.
Do not treat verifier output as a proof; reconstruct the symbolic argument
and audit the rational certificates directly.

## Claimed results

1. For any feasible zero-diagonal stationary flow with center y, convex
   interpolation with the PXC137 product flow gives
   tau_* <= inf_F0 max_i q_i/(q_i+a_i), where
   a_i=|x_i-z_i|/2 and q_i is the distance from y_i to the selector interval.
2. The exact 34/35 blend of the sharp control and scaled PXC139 has the
   displayed rational selectors, is exact and singleton-normalized, and lies
   strictly on the spectral-failure side:
   B_*=559/210 < 8/3, while O=47/15.
3. The identities x_2=z_2=1/35 and v(N\{2})=139/35 force every
   overlap-attaining stationary flow to use its full product diagonal at
   player 2, hence tau_*=1.
4. A feasible rational t=1/4 primal and feasible rational t=0 dual imply
   e_0 >= 1678344132/2126609611 > 7/15=O-c_6T.
   Therefore the proposed universal PXC140e product estimate is false.
5. This is not a counterexample to the corrected n>=6 hybrid-overlap
   inequality; the main inequality remains open.

## Exact files

- paper5/divergence.tex — PXC142a--e and conventional proofs.
- verifiers/divergence/verify_pxc142_saturation_lock_product_no_go.py
- verifiers/divergence/pxc142_saturation_lock_product_no_go.json
- verifiers/divergence/verify_pxc142_saturation_lock_product_no_go_independent.py
- verifiers/divergence/pxc142_saturation_lock_product_no_go_independent.json
- paper5/MECHANISM_PRICE_PROGRAM.md
- paper5/PROTECTED_RESULTS_LEDGER.md

## Reproduction

From the repository root:

~~~bash
python3 verifiers/divergence/verify_pxc142_saturation_lock_product_no_go.py \
  --output /tmp/pxc142.json
cmp verifiers/divergence/pxc142_saturation_lock_product_no_go.json \
  /tmp/pxc142.json

python3 \
  verifiers/divergence/verify_pxc142_saturation_lock_product_no_go_independent.py \
  --output /tmp/pxc142-independent.json
cmp verifiers/divergence/pxc142_saturation_lock_product_no_go_independent.json \
  /tmp/pxc142-independent.json
~~~

The primary verifier replays the explicit release primal and dual with
Fraction arithmetic. The standalone SMT verifier independently checks all
64 exactness witnesses, every selector stage, the spectral enumeration, and
the lock. It only cross-checks the release numbers; it is not represented as
a second optimization proof.

## Hostile questions

1. Does convex interpolation preserve every stationary-flow, conditional-core,
   diagonal-cap, and bridge-objective requirement used in PXC142a--b?
2. Is the coordinate-entry threshold exactly q_i/(q_i+a_i), including
   a_i=0 boundary cases?
3. Does overlap attainment really force the center coordinate to equal q
   when x_i=z_i=q, or is an unmentioned coupling constraint needed?
4. Does complement tightness imply w_i<=q for every core row with the
   inequality direction used in the lock proof?
5. Verify the release LP primal and dual sign conventions independently.
   Do their one-sided bounds have the directions required for the chord
   lower bound on e_0?
6. Does concavity alone justify e_0 >= 4(Psi_(1/4)-Psi_0) at a possibly
   nondifferentiable endpoint?
7. Is the blend exact for the stated conventional reason, and do the staged
   selector claims survive an independent exact LP implementation?
8. Is any equivalent complement-tight saturation-lock or
   slope-times-saturation obstruction already known in cooperative-game,
   parametric-LP, or transport-polytope literature?

Please separate correctness, significance, and novelty, and classify each
finding as critical, major, minor, or presentational.
