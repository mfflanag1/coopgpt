# External review request: fixed-n overlap and constructive packet extraction

Please audit the research checkpoint on branch
`codex/fixed-n-handover-facets`.  Treat every novelty statement as provisional.
The two principal notes are:

```text
paper5/FIXED_N_UPPER_BOUND_PROGRAM.md
paper4/ALGORITHMIC_PACKET_THEOREM.md
```

The computational bug audit is:

```text
verifiers/divergence/audit_overlap_bound.py
verifiers/divergence/overlap_audit.json
```

## Questions requiring hostile review

1. Verify the identities
   `||Lmin-Lmax||_1=2(T-sum_i min(Lmin_i,Lmax_i))` and the equivalence of
   the proposed sharp fixed-`n` bound with the hybrid-cut inequality `(H_n)`.
2. Audit the null-player reduction carefully: does a coordinate that vanishes
   throughout the core of an exact game really imply
   `v(S)=v(S\{i})` for every coalition, with both Lmin and Lmax preserved on
   deletion?
3. Recheck the closed-form crossover proof for the starved family `C_n` and
   balanced `G(p,k)`: starved wins at five, the families tie at six, and `G`
   wins from seven onward.  Assess whether the claimed structural explanation
   is genuinely informative or merely a restatement of the formulas.
4. Try to refute the surviving hybrid-overlap conjecture.  In particular, do
   not assume the comparison cut is balanced: the archived exact six-player
   equality examples explicitly disprove that stronger route.
5. Audit the direct packet-extraction argument.  Check boundedness of `C_H`,
   positivity of some `G_j`, passage to an optimal basic feasible solution,
   the inference from independent positive trace columns to a minimal balanced
   collection, and the `|N|-1` support count.
6. Check that feasibility system `(D)` is exactly the established
   decomposability notion for minimal semi-balanced systems, including the
   scaling of the negative coefficient and the exclusions on `E`.
7. Search specifically for prior work containing an equivalent
   Lmin-boundary two-LP extraction or linear-size rooted obstruction.  The
   exact-cone facet equivalence itself is explicitly treated as prior art.

## Reproduction

Run from `coopgames/..` (the repository root):

```bash
python3 -m py_compile coopgames/verifiers/divergence/audit_overlap_bound.py
python3 coopgames/verifiers/divergence/audit_overlap_bound.py \
  --output /tmp/overlap-audit-current.json \
  coopgames/verifiers/divergence \
  coopgames/verifiers/s6 \
  coopgames/results/n5_exact_lmin_lmax_large_core.json \
  coopgames/results/n5_unique_richest_boundary.json \
  coopgames/results/n6_two_poorer_suffix_counterexample.json
cmp coopgames/verifiers/divergence/overlap_audit.json \
  /tmp/overlap-audit-current.json
```

Expected audit totals are 701 parsed pairs, 375 at `n=6`, no violation of the
global candidate among archived `n>=6` pairs, three failures of the stronger
cut-size claim, and five exact `n=6` equality records.  These counts are only
reproducibility and bug-finding evidence; they are not a proof of `(H_6)`.

Please separate your verdict into: proved as written; repairable gap; false;
novelty unclear; and prior art.  The most important outcome is whether the
packet LP theorem is correct and whether the hybrid-overlap reduction exposes
a plausible route to a genuine fixed-dimension theorem.

## Addendum: sparse Lmax over-cover checkpoint

Also audit the subsequent files:

```text
paper5/LMAX_OVERCOVER_COUPLING.md
verifiers/divergence/audit_lmax_overcover.py
verifiers/divergence/lmax_overcover_audit.json
```

In particular, check:

1. every sign in the first-stage Lmax dual and the objective identity
   `M=sum lambda_A v(A)-eta T`;
2. the `n`-coalition support bound and its preservation when dispersion
   `theta=min max alpha_i` is optimized;
3. the deduction `alpha.Lmin>=M` and the spectral excess condition (4);
4. the direction of the rearrangement inequality used in `(SA)`;
5. the first-stage Lmin under-cover companion `(UC)`, including its signs and
   `n-1` support count;
6. whether the five equality certificates really justify describing the
   three-player dispersed anchor as a common equality geometry;
7. the precise remaining gap: the archive audit is not an exhaustive
   six-player theorem, and the abstract spectra in §6 rule out silently
   replacing exact-game realizability by arbitrary equal-sum vectors.

Reproduce the new artifact with:

```bash
python3 coopgames/verifiers/divergence/audit_lmax_overcover.py \
  --output /tmp/lmax-overcover-current.json \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  coopgames/verifiers/divergence/summary2.json
cmp coopgames/verifiers/divergence/lmax_overcover_audit.json \
  /tmp/lmax-overcover-current.json
```

## Addendum: exactification boundary and generator normal form

The next checkpoint materially changes the completion route.  Audit these
files before accepting any computer-assisted six-player claim:

```text
paper5/TWO_PACKET_EXACTIFICATION_BOUNDARY.md
paper5/CORE_CLOSURE_REDUCTION.md
verifiers/s6/audit_two_packet_exactification.py
verifiers/s6/two_packet_exactification_audit.json
verifiers/s6/core_closure_pipeline.py
verifiers/s6/audit_core_closure_reconstruction.py
verifiers/s6/core_closure_reconstruction_audit.json
verifiers/s6/run_core_closure_census.py
verifiers/s6/rerun_core_closure_unknowns.py
verifiers/s6/merge_core_closure_census.py
paper5/S6_GENERATOR_CENSUS_CHECKPOINT.md
verifiers/s6/core_generator_census.json
```

Hostile questions:

1. Confirm that the two first-stage incidence supports and both individual
   cross inequalities really permit the displayed unnormalized overlap `1/2`.
   Confirm independently that adjoining the three singleton witnesses preserves
   those supports but changes the first Lmin pinned set and restores overlap
   exactly to `2/3`.
2. Check the individual floor-pinning dual `(IP1)--(IP2)` in both directions,
   including every sign and the complementary-slackness restriction to
   trial-tight coalitions.
3. Audit the core-closure lemma: for
   `cl_C(S)=min_{y in C}y(S)`, is `Core(cl_C)=C`, is compactness justified,
   and do six zero-coordinate core witnesses suffice for singleton
   normalization?
4. Audit the stronger certificate-preserving finite exactification theorem.
   Given Lmin `x`, Lmax `z`, and one singleton witness per player, does their
   lower envelope always preserve every coalition used by the staged Farkas
   certificates and therefore preserve every lexicographic stage?  Try to find
   a counterexample to the claimed `n+2`-generator normal form.
5. Compare `pipeline2_core_closure` with
   `pipeline2_generator_normal_form`.  The latter removes `v(S)` entirely and
   marks a coalition support-eligible at `x` only when all other displayed
   generators have at least the `x` coalition sum (and mirrors this at `z`).
   Verify that this is existence-equivalent, not a strengthening.
6. Hostilely recheck the full staged Farkas signs inherited from `nsix.py`, the
   order of the Lmax blocks, the strict stratum inequalities, the contingency
   table convention, and the equivalence between L1 distance `>2/3` and overlap
   `<2/3` at total one.
7. Treat every current SMT count as solver evidence only.  A completed census
   still needs exact coverage reconciliation, isolated reruns of every timeout,
   independent proof evidence or rational infeasibility certificates, equality
   classification, and specialist review.
8. Audit the completed accepted-output merge: it reports all 3,350 survivors
   `UNSAT`, with no `SAT` or `UNKNOWN`.  Verify that every survivor index is
   present, each stored configuration equals `triage32.json`, all overlapping
   decisive rows agree, and all 17 earlier timeouts have decisive isolated
   generator-normal-form reruns.  Do not treat the merged JSON as an
   independently replayable infeasibility certificate.

Reproduce the two exact reconstruction controls from the repository root:

```bash
python3 coopgames/verifiers/s6/audit_two_packet_exactification.py \
  --output /tmp/two-packet-current.json
cmp coopgames/verifiers/s6/two_packet_exactification_audit.json \
  /tmp/two-packet-current.json

python3 coopgames/verifiers/s6/audit_core_closure_reconstruction.py \
  --output /tmp/core-closure-reconstruction-current.json
cmp coopgames/verifiers/s6/core_closure_reconstruction_audit.json \
  /tmp/core-closure-reconstruction-current.json
```

The second control constructs a fresh equality model, compresses its singleton
witnesses, forms the finite lower envelope, and recomputes both selections with
two independently formulated exact rational LP implementations.  It is a
normal-form control, not evidence that every strict-failure configuration is
infeasible.
