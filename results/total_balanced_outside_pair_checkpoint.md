# Total-balanced outside-pair checkpoint

This checkpoint records the completed result and the exact boundary of the
unfinished search.  It does not claim a dimension-free theorem.

## Completed exact result

For `n = 6`, `|S| = 4`, and `|P| = 2`, the subgame-witness cone audit covers
all 619 undominated eta-dual vertex orbits.  Every saved exact rational lower
bound is at least one; the minimum is exactly one and occurs for two orbits.
Thus the finite six-player carrier bound continues to hold under total
balancedness for the outside-pair shape.

Artifacts:

- `n6_s4_totally_balanced_eta_dual_vertex_audit.json`: exact audit and dual
  certificates.
- `n6_s4_totally_balanced_eta_dual_vertex_audit_verification.json`:
  optimizer-free replay of all 619 certificates.

Reproduction:

```sh
python src/audit_n6_eta_dual_vertices.py \
  --census results/n6_eta_dual_vertex_census.json \
  --witness-mode subgame --s-size 4 \
  --output results/n6_s4_totally_balanced_eta_dual_vertex_audit.json
python src/verify_n6_eta_dual_vertex_audit.py \
  --audit results/n6_s4_totally_balanced_eta_dual_vertex_audit.json \
  --output results/n6_s4_totally_balanced_eta_dual_vertex_audit_verification.json
```

## Seven-player boundary evidence

The two `n = 7` alternating-search artifacts are finite computational evidence,
not exhaustive certificates:

- `n7_s5_balanced_cone_carrier_ratio.json` (`|P| = 2`) completed 100 requested
  restarts and found minimum upper ratio one, with no violation.
- `n7_s4_balanced_cone_carrier_ratio.json` (`|P| = 3`) found a zero-ratio
  violation in the larger total-balanced cone.  This is a boundary control for
  the outside-pair conjecture, not a counterexample to the `|P| = 2` claim.

The broad exact `n = 7` searches for target sizes 3, 4, and 5 were stopped
before completion and produced no result artifacts.  A subsequent structural
test of the outside-pair matching reduction did, however, isolate an exact
integer counterexample to the *totally balanced* extension at `n = 7`,
`|S| = 5`, and `|P| = 2`.  It has `gamma_S = 1`, `eta_S = 0`, and singleton
full core.  The solver-free integer certificate is
`src/verify_n7_total_balanced_outside_pair_counterexample.py`.

This establishes that the six-player totally balanced outside-pair result is
dimension-sharp.  The counterexample is not an exact game, so it neither
disproves nor proves sharpness of the unrestricted exact-game theorem.

## Exact-game sharpness

A separate three-generator lower-envelope construction resolves that remaining
question.  At `n = 7`, `S = {1,2,3}`, and `P = {4,5,6,7}`, the exact game

```text
v(T) = min{0, a(T), b(T)},
a = (-3,1,3,-1,2,-1,-1),
b = (3,-2,0,-1,-1,-1,2)
```

has exact leximin point `phi=a/4` with `gamma_S(phi) = 3/4` and
`eta_S(phi) = 0`.  At the reference point zero it has
`(gamma_S(0),eta_S(0))=(1,0)`.  Hence the leximin-specific unrestricted
quantitative carrier conjecture is false, and the exact theorem through six
players is dimension-sharp.  The solver-free structural certificate is
`src/verify_n7_exact_carrier_counterexample.py`; the exact-rational leximin
replay is `src/verify_n7_exact_carrier_counterexample_leximin.py`.
