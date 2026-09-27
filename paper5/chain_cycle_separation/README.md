# Chain–cycle separation: manuscript and certificate package

Current presentation: [Acyclicity and simultaneous protection of individual core maxima](../graph_core_protection/README.md) incorporates this manuscript and the later graph and simultaneous-protection results. This older version is preserved as history.

Prepared September 6, 2026. This package contains an anonymous, journal-neutral technical manuscript and a concise specialist review packet. **Release status: technical manuscript and supplement complete, ready for specialist review; novelty remains qualified because three original-source comparisons are unresolved.** The user requested skipping paid access to those originals. Author/journal metadata must be supplied for a named submission. No paper or message has been submitted.

The proved separation is `c_chain=1/3` and `c_pair=0` for full ascending sorted leximin over the entire strict assignment-game core. The main cyclic construction uses three equal sectors, pair values in `{0,1,2}`, and a strictly positive core allocation. Historical ingredients are credited explicitly; novelty is not presented as confirmed.

## Files to read

- [Manuscript](paper/manuscript.pdf), with [editable LaTeX](paper/manuscript.tex).
- [Two-page specialist packet](review/specialist_packet.pdf), with [editable LaTeX](review/specialist_packet.tex).
- [Current original-source comparison](sources/ORIGINAL_COMPARISONS.md): the 2023 full text was recovered; Quint, Lucas and Stuart still require licensed access.
- [Independent model review](review/claude/review.md) and [response to findings](review/REVIEW_RESPONSE.md).
- [Unsent outreach draft](review/OUTREACH_DRAFT.md).
- [Portable specialist sharing archive](sharing/chain_cycle_review.zip).

## Reproduce

The default checks require Python 3.10 or later and no external Python packages:

```sh
bash build.sh
```

They check four frozen cyclic inputs and an independent reconstruction, with **7,208 exact triple-cover inequalities in each route**, matching/cover totals, partial-matching disjointness, target pinning certificates, ideal attainment, and analytic chain controls. The full all-parameter statements are proved in the manuscript; finite checks are not extrapolated to a theorem.

For exact raw-core LP/satisfiability checks, use a Python environment with `z3-solver==5.1.0.0`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r certificates/requirements-smt.txt
COOPGT_PYTHON=.venv/bin/python bash build.sh --smt
```

This excludes three stronger cyclic-target claims at q=4 using only the raw full-core constraints. It also computes full leximin by successively identifying **all coordinates forced on each optimal face**, computes every ideal separately, and reconstructs a three-payoff-arc certificate per player in three selected chain markets. These finite cases illustrate the universal proof; they are not an exhaustive census of chain markets.

To rebuild both PDFs as well, install a conventional LaTeX distribution with `latexmk` and run:

```sh
COOPGT_PYTHON=.venv/bin/python bash build.sh --full
```

`certificates/RESULTS.json` is a generated result and is overwritten by each run. Failures exit nonzero. Recorded release results and environment information are in `VALIDATION.json`; `SHA256SUMS` describes the frozen delivered files. Rebuilding changes generated files and can therefore change their hashes; PDF timestamps need not reproduce byte-for-byte.

## Scope of the chain controls

The one-team unit simplex has full leximin `(1/3,1/3,1/3)`, each ideal one, and distance `4/3` to a vertex. The second control uses `P=[[1,0],[0,0]]`, `Q=0`: its full core is `(t,0;1-t,0;0,0)`, `0<=t<=1`. The zero diagonal team fixes three coordinates; the mixed triple through the other zero outer player fixes the fourth. The remaining unit segment has full leximin at t=1/2, while its endpoints are first-stage max-min optima that fail the protection claim for one player. This makes full lexicographic refinement essential.

## Evidence and provenance

The independent cyclic verifier and frozen inputs were copied from the previously audited campaign; extraction/adaptation of the portable frozen verifier is documented in `certificates/SOURCE_PROVENANCE.json`. The manuscript was then reviewed through a frozen Claude snapshot. Claude had no tools and did not execute certificates or read external sources. Its review is not a human specialist assessment. Its three precision comments were addressed and the final build was checked separately.

The specialist sharing archive contains the manuscript, brief, own source comparison and minimal certificate files. Third-party originals, temporary signed download URLs and private browser data are excluded. Author name, affiliation and journal formatting should be supplied before submission. Final priority clearance requires the three remaining originals; an external assessment of significance is still advisable.
