# Sharp graph classification for leximin protection

For every fixed connected allowed sector graph G on K>=2 vertices, in the stated strict full-team, equal-sector, nonnegative-pair model,

    c(G) = 1/K for trees, and 0 for graphs containing a cycle.

The [complete conventional proof](GRAPH_DICHOTOMY.md) combines the [tree clipping theorem](ALL_TREES.md) with selective edge subdivision and a unit-shortfall partial matching. For every cyclic G and every q>=1 it constructs a positive-core market with3q+1 players per sector, pair entries in {0,1,2}, target ideal1 and full-leximin target1/[K(q+1)]. Every ideal is over the entire core, and every coordinate remains in the selector. Zero matrices on allowed edges are permitted.

The [four-sector milestone](../selective_c4/MILESTONE.md) was completed before the general cyclic extension. The new [model review](review/review.md) found no load-bearing defect; [verified responses](REVIEW_RESPONSE.md) address its two clarifications. No field-level or unconditional novelty claim is made: [source comparisons](SOURCE_STATUS.md) remain qualified.

## Reproduce

```sh
bash build.sh
COOPGT_PYTHON=/absolute/path/to/z3/python bash build.sh --smt
COOPGT_PYTHON=/absolute/path/to/z3/python bash ../build.sh --smt
```

The package checks822,002 full-team cover inequalities across13 cycle/embedding instances, with cycles through length8 and selected depths through3. It independently verifies integral matching and partial-matching values, target ideal bounds/attainment, positive floor and first-face pinning. Four corrupted records must fail. The optional12 raw-core queries test five/six-sector cases and a cycle embedded in six sectors. The root command additionally replays all prior tree and source dependencies.

The generator's graph embedding is checked over every edge mask on3..6 vertices:33,864 masks,27,474 connected graphs, including26,034 cyclic graphs. These are support/embedding checks, NOT full cover enumeration for every graph. The universal graph conclusion rests on the proof that every cyclic graph contains a simple cycle and on the proved transfers.

[Explicit certificates](CERTIFICATES.json) and [verification results](VERIFICATION.json) use exact rational arithmetic. [Full C5 leximin replay](FULL_LEXIMIN_C5_Q1.json) computes all levels and ideals independently; rerun with `python replay_full_lex.py` in the pinned Z3 environment. The target is1/10 with ideal1. This separate exploratory replay is not repeated by the package build.

See the [goal completion audit](COMPLETION_AUDIT.md) and [specialist review packet](REVIEW_PACKET.md). SHA256SUMS records the delivered checkpoint. No purchases or outreach were made.
