# Second bounded cycle: a coupled family approaching one-sixth

The campaign now proves **c_pair<=1/6**. For every q>=3, the [coupled construction](theory/AMPLIFICATION_FAMILY.md) has9q players, integral total8q, nonnegative pair weights at most3, and designated players whose full leximin payoff and entire-core ideal satisfy

    x_e=1/3+1/q,  H_e=2,  x_e/H_e=1/6+1/(2q).

This is an all-parameter conventional proof with independent internal audit. It establishes an upper limit on any universal guarantee, not a guarantee that all pair-additive markets protect everyone at one-sixth. Neither a zero limiting fraction nor a new opposing-selector distance bound has been established. Priority remains unresolved.

## Main artifacts

- [Canonical family proof](theory/AMPLIFICATION_FAMILY.md): all local/mixed/coupler triples, integral matching and cover, first two full-lexicographic faces, exact ideal witnesses.
- [Independent mathematical audit](audit/AUDIT.md): proof obligations, exact raw checks, and verification limits.
- [Experiment and second audit](experiment/EXPERIMENT.md): the finite11/45 coupling that exposed the mechanism, rejected ideal3 guesses, and independent affine-type verification.
- [Cloning reduction](structure/STRUCTURE.md): coordinate replication preserves selectors and ideal fractions; the global distance supremum reduces to a local matched-team distance supremum.
- [Shrinking-small-team obstruction](theory/DELTA_CHAIN_OBSTRUCTION.md): internal target fractions in that proposed route remain at least1/6; zero ideals are not counterexamples.
- [Ring obstruction](RING_NO_GO.md): closing the transfer path restores the designated fraction1/3 by reducing its ideal.
- [Bilateral factorization obstruction](theory/CYCLIC_FACTOR_OBSTRUCTION.md): a difference-constraint/negative-cycle characterization; a structural diagnostic rather than a fairness theorem.
- [Bounded source follow-up](SOURCE_CHECK.md): classical equal-treatment precedent and unclosed priority gaps.

`COUPLED_CHAIN_THEOREM.md` is a retained duplicate of the candidate inspected by one review lane; it is not a separate result or paper. Use `AMPLIFICATION_FAMILY.md` as the canonical proof.

## Reproduction

From this directory run:

```sh
bash build.sh
```

This uses only Python's standard library. It replays the finite coupling certificate, all-size cover inequalities reduced to finite affine types, and independent raw-array corroboration through216 players. The conventional proof supplies the all-q assertion; a numerical census does not replace it.

Optional solver-backed discovery and checks use the versions in `../experiment/requirements.txt`:

```sh
python experiment/coupling.py
python experiment/zero_chain.py
python experiment/fixed_one_chain.py
python structure/check_cloning.py
python audit/check_amplification.py
```

The saved raw records distinguish exact acceptance from floating screening, fixed-total infeasibility from empty-core claims, and rejected from accepted ideal witnesses. Scratch paths in the reports identify original execution locations. Published drivers use relative campaign paths. Build logs and hashes preserve the packaged evidence.

## Next decision

The new construction makes a positive1/6 universal bound a concrete candidate to challenge, not an assumption. A further campaign should seek either a general lower bound or a different coupling that beats this family's limit. Repeating blocks, closing this path into a ring, shrinking its small teams for the same internal coordinates, or optimizing another finite instance on this support does not establish vanishing protection. The distance problem can be investigated separately through the proved local-team reduction.
