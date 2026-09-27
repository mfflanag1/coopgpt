# Fifth cycle: vanishing protection and a deeper priority audit

The [all-parameter proof](root/VANISHING_FAMILY.md) establishes **c_pair=0**. For every q>=1, a complete strict three-sector pair-additive market has 9q+3 players and a target whose full-leximin payoff-to-ideal ratio is **1/[3(q+1)]**. Every pair value is in {0,1,2}; total worth is 6q+1. The target is fixed on the entire positive first max-min face, and its actual whole-core ideal is 1.

This resolves the mathematical vanishing-family target in the [authorized goal](CAMPAIGN.md). The [priority audit](NOVELTY_LEDGER.md) does **not** confirm novelty. It credits the earlier protection criterion, sorted-selector methods, and broader vanishing examples, and identifies the narrower constrained-realization claim that survives the inspected comparisons. Original-source gaps and external specialist review remain pending.

## Proof and verification

A diagonal perfect matching has value 6q+1. A second, partial matching has value 6q and leaves 3q+3 players unmatched. Its core inequality limits their total payoff to one. An explicit positive floor cover equalizes all of them at 1/[3(q+1)], forcing the target throughout the first optimal face. A second full-core cover gives that target its exact ideal 1. Four pair-pattern cases establish every mixed-triple cover for all q.

- [Root proof](root/VANISHING_FAMILY.md): explicit matrices, both covers, all-parameter mixed-triple classification, and the short partial-matching argument.
- [Construction route](recurrence/RECURRENCE.md): original serial-gate derivation, the algebraic rejection of its first proposed gate, the corrected family, pre-test manifest, and exact finite calibration.
- [Independent proof](independent/INDEPENDENT_FAMILY_PROOF.md): separate symbolic audit plus a differently labeled raw construction.
- [Fixed-size certificate bound](root/FIXED_SIZE_CERTIFICATE_BOUND.md): a classical LP/determinant consequence proving that positive-first-face vanishing requires unbounded player count. It is a supporting observation, not a new method.
- [Source and scope audit](NOVELTY_LEDGER.md): historical originals, modern equivalent terminology, two clarified extreme-core papers, and a relabeling-invariant exclusion from the inspected supermodular classes.

The four declared finite depths are q=1,2,3,4, giving 12,21,30,39 players and ratios 1/6,1/9,1/12,1/15. Each independent construction checks 7,208 raw triple inequalities across its two witnesses and these four depths. Three additional raw-core UNSAT queries at q=4 check the higher-floor, first-face-target, and ideal exclusions. The infinite conclusion follows from the symbolic proof, not those finite checks. No full vector of either selector or selector-distance limit is asserted.

Replay frozen certificates using only the standard library:

```sh
bash build.sh
```

For the extra raw-core queries, use Python with z3-solver 5.1.0.0:

```sh
COOPGT_PYTHON=/path/to/python bash build.sh --full
```

The default build does not regenerate the discovery manifest or change the declared depth set. Source PDFs and read/access ledgers are retained for the user's research audit; their presence does not mean every historical paper was obtained or every proof re-proved. `BUILD.log`, `PROVENANCE.json`, and `SHA256SUMS` record verification and integrity.

The opposing-selector distance frontier remains 4/3<=d_pair<=2. Global novelty, field-level significance, minimum market size, and optimal finite-size fractions are not established. This cycle stops after the all-parameter theorem and its bounded priority audit.

The app rejected the new create-goal call because the older external-review goal is unfinished. The working objective and outcome are recorded here, but the app tracker was not changed or falsely marked complete. No outreach was sent.
