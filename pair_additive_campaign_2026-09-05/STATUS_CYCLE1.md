# Proof state after the first bounded campaign cycle

September 5, 2026. Campaign started at the user's request. The full cyclic target remains open in this work; no claim of a field-level breakthrough, global novelty, or completed external review is made.

## Exact frontier

For complete equal-sector strict triple markets w=A+B+C with nonnegative pair entries and nonempty full core:

    0 <= c_pair <= 5/18,
    4/3 <= d_pair <= 2.

The nontrivial upper bound on c_pair follows from the nine-player counterexample. The lower bound on d_pair comes from the already established player-additive family; the new counterexample has distance only 11/24. Neither c_pair=0 nor d_pair>4/3 has been established.

For the strict chain subclass w_ijk=P_ij+Q_jk, the campaign proves

    c_chain = 1/3,
    d_chain = 4/3,

where d_chain is a supremum over opposing full selectors. The stronger inequality ||x-y||_1/T<=4/3 holds for every core point y and is finitely attained, including in the one-team simplex. The opposing-selector sharpness family approaches 4/3. This proof uses a classical partial slack-balancing framework and a potentially classical core representation; its chain-specific priority is not certified. See literature/NOVELTY_CHAIN.md.

## Proof and verification ledger

| ID | Statement or route | Evidence / decision |
|---|---|---|
| C0 | Frozen domain, integral T, full selectors and all players | CAMPAIGN.md; unchanged target |
| S0 | Classical model and source boundary | literature/SOURCE_GATE.md; original Quint/Lucas and newer extreme-core source gaps retained |
| W1 | Pair-additive 1/3 guarantee is false | COUNTEREXAMPLE.md; ordinary proof, exact matching/cover and ideal witness; min fraction5/18 |
| V1 | W1 independently checked | literature/AUDIT.md; 36 perfect matchings and 512 coalition checks per displayed point; exact full minimax face |
| V2 | All reduced-witness ideals and selector stages | 35 saved rational primal/dual identities plus independent sorted-rank SMT checks; experiment/EXPERIMENT.md |
| T1 | Strict-chain whole-core representation | theory/CHAIN_FOLLOWUP.md §1; exact difference constraints, no productive pairs added |
| T2 | Sharp strict-chain protection and distance | theory/CHAIN_FOLLOWUP.md; per-player cycle with three payoff arcs; independent experiment/CHAIN_AUDIT.md |
| N1 | Stable core implies compatible bilateral optima | False: published Atay–Núñez2019 Example5, independently recalculated for strict core |
| N2 | Generalized bilateral core composition equals strict core | False even with one player per sector; source gate records explicit examples |
| N3 | Block-diagonal replication amplifies W1 | False: experiment/COMPOSITION_CHECK.md proves repeated selectors and ideals; fraction unchanged |
| N4 | Scale two large entries on W1's sparse support | Intended budget also imposes H_v0<=a+f+d-b; theory/THEORY.md; route blocked without a new way around incidental triple constraints |

The proof of T2 has a concrete certificate: each player's ideal is bounded by three leximin payoffs no larger than its own. The simple-cycle argument fails to extend automatically when all three pair matrices are present. This is a substantive structural distinction, not proof that every positive guarantee fails under cycles.

## Next bounded obligation

The most direct unresolved construction target is a genuinely coupled two-block pair-additive gadget with:

1. a certified integral matching value and full covering allocation;
2. an explicit ideal-attaining point keeping a designated player's H bounded below after normalization;
3. a complete lexicographic-face proof giving a strict contraction of its payoff relative to an input block;
4. every incidental and mixed triple inequality checked symbolically; and
5. a composition rule that can be iterated without adding unverified constraints or changing the modeled player set.

An alternative useful outcome is a uniform bound derived from the pair-additive slice constraints that prevents this contraction. Continue only with a reusable coupling, a new structural restriction, or a substantive reduction. Another isolated improvement of5/18, more clean samples, or repeated disjoint copies is insufficient. The strict-chain route is now a completed control theorem and should not absorb a new broad search.

## Research and app state

The old specialist-review stage remains pending externally. The user's September5 instruction authorized this new research campaign despite that earlier sequencing gate. The goal tool returned: “cannot create a new goal because this thread has an unfinished goal; complete the existing goal first.” The prior goal was not falsely marked complete. This repository records the new objective and its progress, while the app tracker still holds the earlier blocked goal.
