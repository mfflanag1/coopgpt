# Pair-additive assignment research campaign

The [fifth bounded cycle](cycle5/README.md) proves **c_pair=0**: an explicit family with 9q+3 players and pair entries in {0,1,2} has full-leximin payoff-to-ideal ratio **1/[3(q+1)]**, tending to zero. An all-parameter proof and independent exact audits are included. The [deeper priority audit](cycle5/NOVELTY_LEDGER.md) identifies clear precedents for the metric and broader phenomenon; novelty of this restricted realization remains unconfirmed. Earlier cycles and finite examples remain preserved. Read the [current status](STATUS.md) for exact claims and remaining obligations. The [September 6 priority follow-up](priority_confirmation_2026-09-06/REVIEW.md) finds no exact antecedent and gives stronger exclusions of inspected chain and representation routes; its four original-text gaps are historical. The [new manuscript and review package](../paper5/chain_cycle_separation/README.md) resolves the 2023 original comparison and supplies complete chain–cycle proofs, exact certificates and a two-page specialist brief. Three full-original comparisons and external specialist review remain open; paid access was skipped at the user’s request.

The user authorized this campaign on September 5, 2026. The [contract](CAMPAIGN.md) fixes the exact target and stopping rules. The first bounded pilot proves that the player-additive one-third leximin guarantee fails in the broader nonnegative pair-additive strict-triple class: a nine-player example gives **5/18**. A follow-up proves the sharp **1/3** guarantee for strict chain interactions using a potential-network argument. That original open question is now resolved by cycle5: no positive uniform guarantee survives the cyclic class. The cyclic opposing-selector distance target is also unresolved. All priority claims remain provisional.

- [Conventional counterexample proof](COUNTEREXAMPLE.md): complete selectors, an ideal-attaining allocation, and the matching/cover certificate.
- [Proof state and next obligation](STATUS.md): established facts, failed routes, and continuation gate.
- [Primary-source gate](literature/SOURCE_GATE.md): exact model boundaries and explicit original-source gaps; no novelty certification.
- [Theory route](theory/THEORY.md): the finite mechanism, a failed scaling calculation, and a strict-chain control representation.
- [Sharp strict-chain guarantee](theory/CHAIN_FOLLOWUP.md): the full proof by per-player directed-cycle certificates, with [adversarial review](experiment/CHAIN_AUDIT.md).
- [Composition obstruction](experiment/COMPOSITION_CHECK.md): block-diagonal repetition preserves the old fraction and distance, so it cannot amplify the failure.
- [Experiment report](experiment/EXPERIMENT.md): bounded search, exact inputs, calibration, and rational certificates.

Run the latest vanishing-family certificates with `bash cycle5/build.sh` (see its README for the independent raw-core audit).

Run the original pilot's saved witness and 35 rational certificate checks using only Python's standard library:

```sh
bash build.sh
```

The discovery screen is optional. In a Python environment with the versions in `experiment/requirements.txt`, run from this directory:

```sh
python experiment/pilot.py --per-size 192 --seed 20260905
python experiment/refine.py
python experiment/rational_certificates.py
python experiment/verify_saved_rationals.py
```

The copied `verification_dependency/exact_three.py` is unchanged from the reviewed assignment package; provenance and hashes are retained. The discovery driver was adapted to use this local dependency and clear stale discovery-success artifacts on restart. Saved exact certificates do not require the discovery dependencies or a solver. The experiment report's scratch paths describe the original run; commands above are portable.

The app goal tracker rejected replacement of the earlier unfinished external-review goal. Research has started under the user's new instruction, but the tracker has **not** been switched. External specialist review of the existing three paper packages remains pending; this campaign does not certify it or supersede their preserved review evidence.
