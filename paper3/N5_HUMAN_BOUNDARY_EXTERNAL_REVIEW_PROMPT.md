# Hostile external review prompt — human two-poorer boundary threshold

Please review the human proof of the sharp `2|3` versus `2|4` richer-side
threshold for Lmin boundaries of singleton-normalized exact games.  Treat all
novelty and correctness claims as untrusted.  The new contribution claimed is
the structural lower-bound proof, not the already known theory of minimal
balanced collections and not the earlier finite verifier.

## Commit and paths

Review the commit identified in the accompanying pull request, especially:

- `coopgames/paper3/sections_leximin.tex`, Lemma “strict richer-side cover,”
  Theorem “balanced-trace transport obstruction,” and Theorem “human
  two-poorer boundary threshold”;
- `coopgames/paper3/N5_N6_SMALL_POORER_THRESHOLD.md`;
- `coopgames/paper3/GENERAL_BOUNDARY_OBSTRUCTION.md`;
- `coopgames/paper3/BALANCED_TRACE_TRANSPORT_PRIOR_ART.md`;
- `coopgames/paper3/PROPERTY_I_STRICT_COVER_AUDIT.md`;
- `coopgames/paper3/RANK_TWO_TRACE_EXCLUSION.md`;
- `coopgames/paper3/H4_FIRST_OBSTRUCTION_CLASSIFICATION.md`;
- `coopgames/src/verify_n5_small_poorer_suffix.py` and
  `coopgames/results/n5_small_poorer_suffix.json` only as an independent
  computational audit;
- `coopgames/src/verify_n6_two_poorer_suffix_counterexample.py` and
  `coopgames/results/n6_two_poorer_suffix_counterexample.json` for the sharp
  fixed example.

## Claims to attack

1. Derive the individual-pinning LP dual from scratch and verify every sign
   and coefficient in the dimension-free strict richer-side cover.  Check the
   displayed primal and stationarity equation `(SC-D)`, including the sign of
   the efficiency multiplier and the complementary-slackness support.  Check the
   backward large-coefficient induction across arbitrary poorer payoff strata,
   including that it controls earlier coalition loads without silently
   constraining their equality multipliers and preserves later deficits.
   Compare the result explicitly with property I in Arin--Kuipers--Vermeulen
   (2008), Lemma 1, and its antidual Lmin form in Mauri (2018), Lemma 3.
   Determine whether the simultaneous strict cover is a standard equivalent
   dual formulation or an additional quantitative consequence; do not count
   the qualitative tight-coalition criterion as new.
2. Check that the aggregate strict-cover inequality really rules out two
   nonnegative poor-player displacements, including after normalization and
   deletion of coalitions with empty rich trace.
3. Check the full balanced-trace transport theorem: deleting coalitions with
   empty rich trace, normalizing the rich load, decomposing into normalized
   minimal balanced packets, and recovering coordinatewise strict average
   poor-player undercoverage.
4. Verify the refinement from trace packets to deterministic packets of
   original tight coalitions.  Look specifically for a hidden convexity or
   coupling gap in the product decomposition across trace slots.  Also verify
   that the extreme points of the displayed bounded polytope `P_H` are exactly
   normalized minimal balanced collections.
5. Independently classify normalized minimal balanced collections on one,
   two, and three players.  Confirm that the only nonpartition case on three
   players is the half-weight pair triangle.
6. Audit the packet inequality
   `-s + r_a Delta_a + r_b Delta_b >= 0`, the integer argument for partition
   packets, and the half-integer carrier argument for the triangle.
7. Check that the forced tight coalitions can indeed be relabeled as
   `{c,d}`, `{c,e}`, `{b,d,e}`, and that exactness of singleton `{d}` yields
   the stated strict efficiency contradiction using only singleton
   normalization and the strict payoff boundary.
8. Audit the corrected dimension-free rank-two trace exclusion. Check the
   extreme-point support classification for singleton/pair traces, including
   singleton columns and disconnected or multiple odd-cycle components.
   Verify the deduction `r_b=1/2,r_a=0`, alternating only the uniquely labeled
   cycle, and retaining all other components at their original weights.
   Check the real load `1_H+e_d+e_b` and the budget contradiction
   `phi_d<=phi_a`; do not treat it as an integer fibre with multiple cycles.
9. Independently derive the five fractional exact-cover vertices on four
   rich players and audit the first-obstruction uniqueness theorem. Treat the
   list in `(FO-2)` as untrusted; verify exhaustiveness by hand, all safe root
   roundings, and the type-D scaled poor-load case split. Confirm that the
   theorem forces the four-co-singleton `1/3` vertex itself.
10. Confirm the scope: the theorem handles one poorer player in every
   dimension and exactly two poorer players with at most three richer players;
   it does not settle the strips with three or more poorer players.
11. Search the exact-game, Lorenz/Lmin, exact-partition, and minimal-balanced-
   collection literature for this particular sharp rich-side threshold or an
   argument that subsumes it.  Do not credit the manuscript with inventing
   minimal balanced collections.
12. Replay both exact-rational verifiers and compare their JSON output byte for
    byte, but treat those results as audit conveniences rather than independent
    proof evidence.

Please report the first invalid inference or missing hypothesis before giving
any overall assessment.  If the proof survives, distinguish mathematical
correctness, novelty, and field significance; do not infer any of them from
the others.
