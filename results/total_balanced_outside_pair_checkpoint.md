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

Exact `n = 7` searches for target sizes 3, 4, and 5 were stopped before
completion at this checkpoint and produced no result artifacts.  Accordingly,
there is no exact seven-player theorem or seven-player outside-pair
counterexample claimed here.
