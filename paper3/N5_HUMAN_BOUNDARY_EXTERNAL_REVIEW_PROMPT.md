# Hostile external review prompt — human two-poorer boundary threshold

Please review the human proof of the sharp `2|3` versus `2|4` richer-side
threshold for Lmin boundaries of singleton-normalized exact games.  Treat all
novelty and correctness claims as untrusted.  The new contribution claimed is
the structural lower-bound proof, not the already known theory of minimal
balanced collections and not the earlier finite verifier.

## Commit and paths

Review the commit identified in the accompanying pull request, especially:

- `coopgames/paper3/sections_leximin.tex`, Lemma “strict richer-side cover”
  and Theorem “human two-poorer boundary threshold”;
- `coopgames/paper3/N5_N6_SMALL_POORER_THRESHOLD.md`;
- `coopgames/paper3/GENERAL_BOUNDARY_OBSTRUCTION.md`;
- `coopgames/src/verify_n5_small_poorer_suffix.py` and
  `coopgames/results/n5_small_poorer_suffix.json` only as an independent
  computational audit;
- `coopgames/src/verify_n6_two_poorer_suffix_counterexample.py` and
  `coopgames/results/n6_two_poorer_suffix_counterexample.json` for the sharp
  fixed example.

## Claims to attack

1. Derive the individual-pinning LP dual from scratch and verify every sign
   and coefficient in the strict richer-side cover, separately for tied poor
   players and successive poor levels.  In the successive case, check that
   the large-`M` combination really controls the earlier player's coalition
   load without silently constraining its equality multiplier.
2. Check that the aggregate strict-cover inequality really rules out two
   nonnegative poor-player displacements, including after normalization and
   deletion of coalitions with empty rich trace.
3. Check that deleting coalitions with empty rich trace, normalizing the rich
   load, and decomposing the resulting balanced collection into minimal
   balanced packets preserves the strict poor-player undercoverage needed by
   the proof.
4. Verify the refinement from trace packets to deterministic packets of
   original tight coalitions.  Look specifically for a hidden convexity or
   coupling gap in the product decomposition across trace slots.
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
8. Confirm the scope: the theorem handles one poorer player in every
   dimension and exactly two poorer players with at most three richer players;
   it does not settle the strips with three or more poorer players.
9. Search the exact-game, Lorenz/Lmin, exact-partition, and minimal-balanced-
   collection literature for this particular sharp rich-side threshold or an
   argument that subsumes it.  Do not credit the manuscript with inventing
   minimal balanced collections.
10. Replay both exact-rational verifiers and compare their JSON output byte for
    byte, but treat those results as audit conveniences rather than independent
    proof evidence.

Please report the first invalid inference or missing hypothesis before giving
any overall assessment.  If the proof survives, distinguish mathematical
correctness, novelty, and field significance; do not infer any of them from
the others.
