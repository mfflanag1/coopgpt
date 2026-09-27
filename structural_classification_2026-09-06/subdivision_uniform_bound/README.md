# Uniform protection in the diagonal-subdivision family

The [conventional proof](UNIFORM_BOUND.md) establishes x_i/H_i>=1/676 for every depth q>=1, every positive bonus M, and every player in the specified construction. The bound is conservative, not claimed sharp. It closes the different-target/shrinking-bonus region left open by the [previous checkpoint](../diagonal_subdivision/README.md).

The mechanism has two parts: short partial matchings cap every weak player's ideal at3M; a four-coordinate terminal replacement protects the remaining players at full leximin. The previously established floor M/4 handles weak players and the larger-bonus regime.

This does not establish a positive lower bound for general C4. The main campaign still has0<=c(C4)<=5/44, and its goal remains active. No novelty or field-level breakthrough is claimed; the source-family floor and fixed-bonus floor are prior project ingredients. The three unpaid/unread original-source comparisons remain unresolved. No purchase, outreach or submission occurred.

## Reproduce

```sh
bash build.sh
COOPGT_PYTHON=/absolute/path/to/z3/python bash build.sh --smt
```

The standard checker validates exact affine-in-M partial-matching certificates for q=1 through12 and exhaustively classifies all teams for q=1 through4. Optional SMT queries use the raw entire-core inequalities, with variable M (the terminal query additionally receives the weak bounds proved by the preceding query and the tight diagonal equalities implied by efficiency), to seek a violating weak ideal at ANY M>0 and a failed terminal replacement anywhere in0<M<=1/42, for q=1,2,3. UNSAT is required; unknown/timeouts fail. The all-q conclusion rests on the conventional proof, not finite queries.

[Small-bonus profiles](SMALL_BONUS_PROFILES.json) are exploratory exact full-leximin/ideal calculations at M=1/100 and q=1,2,3,4. Their minimum ratios are1/4,1/6,5/36,1/8. Recompute with `python probe_small_bonus.py` in the Z3 environment. These profiles suggested the mechanism but do not prove an asymptotic formula or the theorem. They are not repeated by the main build.

See [verification](VERIFICATION.json), [review disposition](REVIEW_RESPONSE.md), and [status](STATUS.json). SHA256SUMS records the delivered checkpoint; rebuilding generated records can change hashes.
