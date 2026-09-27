# Completion and proof audit

The mathematical goal is resolved by the permitted counterexample outcome. The conjecture rho≥1/K fails at K=3, q=1, and the all-q formula rho=1/(2q+3) rules out every positive K-only guarantee at K=3. Zero-sector extension gives the same conclusion for arbitrary K≥3. The sharper graph statement has R(G)=1/K on trees and zero on cyclic allowed graphs.

## Load-bearing checks

1. **Integral worth:** an explicit diagonal integral matching and a complete nonnegative cover have equal total 6q+1. Both inequalities establishing worth are present.
2. **Entire core:** every full-team inequality is covered; core-to-simplex necessity follows from identical weak a rows, diagonal tightness and E/N triples. Sufficiency checks weak-a cases and all four strong-a two-edge cases. No face restriction or fractional matching substitution is used.
3. **Ideals:** explicit distinct simplex vertices attain every claimed coordinate maximum; upper bounds follow from the simplex parameter budget and diagonal equalities. No simultaneous sector attainment is assumed.
4. **Optimality:** the unmatched budget proves the upper bound for every core allocation, and a positive rational core witness attains exactly the same normalized floor.
5. **Graph transfer:** only old-coordinate ideal lower witnesses are preserved. Every retained high-ideal player remains unmatched, and the residual budget stays one. No preservation of the whole ideal vector or selector is needed.
6. **Quantifiers:** a zero infimum across growing markets is separated from positive finite-market rho. The poorly protected player may depend on the allocation. Productive proper-sector coalitions, unequal sector sizes and strictly positive entries on every edge are outside the theorem.
7. **Prior ingredients:** the matrices, tree theorem and subdivision transfer are existing project results. The new whole-core simplex representation and simultaneous-protection analysis are identified separately.

## Evidence

- `BUILD.log` and `VERIFICATION.json`: combined build PASS with 2,553,912 exact full-team cover evaluations.
- Triangle vertices and optimal witnesses: q=1..8. Every enumerated simplex vertex is checked against the raw matrix-generated full-team constraints, and vertex coordinate maxima match the claimed ideals.
- Six cyclic/embedding cases, including relabeled cycles, zero chords, and added sectors: actual lower-ideal lifts and a strictly positive cover are checked; their partial matchings are verified disjoint with shortfall one.
- 16 independent raw-core SMT questions at q=1..4 return UNSAT: both directions of the compact-core representation, ideal upper violations, and improvement of the claimed optimum. Unknown/timeout outcomes fail the verifier.
- Three corrupted inputs are rejected: an inflated ideal, an inefficient cover, and an overlapping partial matching. Verification uses explicit exceptions and still runs under Python `-O`.
- Discovery separately optimized every individual ideal and rho with exact Z3 at q=1..6. Those observations motivated the proof; the delivered certificate replay does not rely on the discovery optimizer.

The all-parameter result is a conventional proof, not an inference from finite enumeration. The new proof has not received an external specialist or cross-model review; no separately paid consultation was invoked under the free-only constraint. Previously reviewed dependencies do not confer reviewed status on this strengthening.

## Research decision

The original universal-bound route is disproved, so broad random searches for another counterexample are unnecessary for this goal. No claim is made about the sharp finite-size minimum over all markets or the exact rho of longer-cycle extensions. Those questions were not needed to decide existence of a size-independent bound.

Historical novelty is unconfirmed after a bounded free-source audit. In particular, the bilateral half-optimal core is established prior art, and the three old full-original access gaps remain. This package is ready for a specialist to assess; it is not an endorsement or a submission.
