# Fourth bounded cycle: one-sixth protection is false

The [21-player construction and conventional proof](root/ONE_NINTH_COUNTEREXAMPLE.md) give a player full leximin payoff **1/3** and true maximum core payoff **3**, hence ratio **1/9**. It is a complete strict three-sector assignment game with seven players per sector, 16 nonzero nonnegative pair entries, and total worth 15. The target is fixed throughout the entire positive first optimal face. The one-sixth guarantee proposed in the previous cycle is therefore false.

The cycle's [research contract](CAMPAIGN.md) is resolved by disproof. The current class-wide frontier is `0 <= c_pair <= 1/9`; whether any positive universal guarantee exists remains open. The selector-distance frontier stays `4/3 <= d_pair <= 2`. No minimal player count, sharpness of 1/9, infinite family, global novelty, or field-level breakthrough is asserted.

## Evidence and mechanism

- [Explicit proof](root/ONE_NINTH_COUNTEREXAMPLE.md) and [independent reconstruction](root/verify_compact_proof.py): seven matching equalities minus six triple covers yield a nine-coefficient budget fixing the target on the first face.
- [Experiment report](experiment/EXPERIMENT.md): inverse LP reweights the previously studied 65-entry support. The first of six planned LPs attains the exact budget ceiling; the other five were not run. A deterministic seven-team restriction yields the compact example. The earlier fixed-weight composition certificates remain valid.
- [Canonical data](experiment/reduced_candidate.json) and [stdlib checker](experiment/verify_reduced.py): every induced triple is checked at both rational core witnesses. The saved floor witness is not presented as the whole final selector.
- [Independent raw audit](zero_face/COMPACT_AUDIT.md): 686 exact covers and three raw full-core UNSAT queries establish the floor, target pinning, and ideal without the generated budget. The original 63-player audit is preserved separately.
- [Inverse certificate formulation](root/INVERSE_CERTIFICATE_DESIGN.md): a reusable classical LP interface; no methodological novelty claim.
- [Residual partial-matching lemma](theory/RESIDUAL_PARTIAL_MATCHING.md): valid dual reduction, with the proposed universal six-deficit bound disproved. An explicit sharp nine-deficit certificate is checked on the original input.
- [Zero-face reduction](zero_face/ZERO_FACE_REDUCTION.md): exact projection needs generalized singleton/pair/triple production; a strict same-class replacement is impossible in the given 12-player example.
- [Bounded primary-source check](theory/SOURCE_CHECK.md): no directly matching result identified in the inspected sources; original-source gaps and external specialist review remain open.

## Replay

Run the saved conventional certificates using Python's standard library:

```sh
bash build.sh
```

For the additional independent raw-core exclusions, use Python with `z3-solver==5.1.0.0`:

```sh
COOPGT_PYTHON=/path/to/python bash build.sh --full
```

The source data and certificates are fixed. Builds do not restart discovery. Optional LP regeneration needs NumPy 2.5.2 and SciPy 1.18.1; see the experiment report. Calibration results preserve replays of the previous finite one-sixth example and both fixed two-ninths compositions. `BUILD.log`, `PROVENANCE.json`, and `SHA256SUMS` record the package verification.

The useful next question is whether the nine-unit mechanism can be made into a parameterized family with ratios tending to zero, or whether a proved structural obstruction forces a positive universal bound. Increasing the certificate mass alone is insufficient: every mixed triple, matching worth, first-face claim, and ideal must still be controlled. This cycle stops after the certified counterexample.

The app goal tracker remains attached to the old unfinished external-review goal. The user authorized this bounded research in the task; the external review was not marked complete and no outreach was sent.
