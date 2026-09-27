# C4 vanishing protection: four-sector milestone complete

The [all-q proof](C4_VANISHING.md) gives a strict four-sector cycle market with sector size3q+1, pair entries in {0,1,2}, positive entire core, and

    full-leximin target = 1/[4(q+1)], entire-core target ideal = 1.

Thus c(C4)=0. Together with the prior tree and triangle-containing results, this completes all six connected four-sector graph types. The broader graph-classification goal remains active pending the general cyclic transfer.

The key is selective diagonal subdivision: bonuses are positive only on labels consumed by the critical partial matching. Its shortfall stays1, while its unmatched set grows to4(q+1). All pairwise diagonal matchings are simultaneously optimal; incompatibility is unnecessary.

## Reproduce

```sh
bash build.sh
COOPGT_PYTHON=/absolute/path/to/z3/python bash build.sh --smt
```

The standard checker verifies474,150 full-team cover inequalities for q=1..6, exact integral perfect/partial matching certificates, ideal attainment, and four corrupted-record rejections. The optional nine raw-core queries at q=1..3 exclude a higher common floor, a larger target on the entire first face, and an ideal above1. Unknown/timeouts fail. [Certificates](CERTIFICATES.json) are explicit and use rational arithmetic. Finite checks corroborate the symbolic proof; they do not prove the limit by extrapolation.

[Review disposition](REVIEW_RESPONSE.md), [source audit](SOURCE_STATUS.md), [milestone decision](MILESTONE.md), and [verification](VERIFICATION.json) state the evidence and limits. Correctness received a model review, not specialist review. Novelty remains qualified; Quint, Lucas and Stuart originals remain unresolved under the no-purchase instruction. No purchase, outreach or submission occurred.
