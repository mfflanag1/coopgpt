# Independent coefficient-two review

Date: 2026-08-10

Status: **passed an independent internal hostile review; not an external
specialist endorsement.**

The reviewer reconstructed both coefficient-two rows without importing the
production encoder and found no fatal mathematical defect in the
counterexample-to-formula interface.

## Mandatory traces

- `(2,3,1):a72`: direction `(-2,-1,1,1,1,0)`, activation
  `min(x2,x3,x4) < min(x0,x1)`, 24 negative cuts (`2+8+14`) and 168 blocker
  comparisons.  The independent formula and the frozen production assertion
  have UNSAT XOR.
- `(3,3,0):a74`: direction `(-2,0,-2,1,1,2)`, activation
  `min(x3,x4,x5) < min(x0,x2)`, 26 negative cuts (`12+14`) and 182 blocker
  comparisons.  The independent formula and the frozen production assertion
  have UNSAT XOR.

Every cut has the required orientation: it selects a coalition on which the
direction is negative and requires the opposite allocation together with all
six singleton-exactness witnesses to be at least the selected allocation.

The two row-level XOR checks are included in the 458 assertion-equivalence
checks of the third formulation.  Reproduce them, together with every other
row, using the pinned interpreter from `ENVIRONMENT.md`:

```text
"${PAPER5_PYTHON}" coopgames/verifiers/s6/verify_third_bound_two.py \
  --output /tmp/third_bound_two_verification.json
cmp /tmp/third_bound_two_verification.json \
  coopgames/verifiers/s6/third_bound_two/verification.json
```

## Independent checks passed

- all 15 production formulas byte-regenerate and their proof records verify;
- both coefficient-two bases are SAT and both full systems are UNSAT;
- the third formulation gives 458 assertion-level equivalences;
- both mutations are detected on exactly 85 of 85 rows;
- the semantic interface gives 1,332 equivalences, 4,722 negative-cut
  instances, and 33,054 reconstructed blocker comparisons; and
- the lex-improvement audit gives 15,079,260 comparisons with zero mismatch.

## Review findings repaired

1. `verify_third_bound_two.py` now requires exactly 85 detections for each
   targeted mutation rather than merely requiring a nonzero count.
2. `ENVIRONMENT.md` and `requirements-review.txt` now pin the Python/Z3 review
   environment and define one Python entry point for all reproduction commands.
3. The certificate README now labels `verify_independent_bound_two.py` as an
   offline regeneration/hash/status audit and supplies a separate fresh
   cvc5/Ethos replay command.
4. The manuscript now limits the three-template statement to the reduced
   nineteen-orbit formulation; it no longer attributes that restriction to
   the original large direction menus.

Correctness and novelty remain separate gates.  This review supports the
coefficient-two proof interface only; it does not establish that the theorem
is new in the cooperative-game literature.
