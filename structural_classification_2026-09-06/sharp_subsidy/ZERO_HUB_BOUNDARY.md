# The zero-hub-value boundary has obstruction at most one eighteenth

2026-09-08 UTC. This is progress inside the active two-hour original-core
compatibility phase, not a uniform improvement for the full market class.
Independent specialist review and novelty assessment remain incomplete.

## Statement

Fix a connected diagonal/P incidence support with at least one degree-three
label, with every label of degree one or three. P is a partial matching.
Assume all degree-three labels have diagonal worth zero. In the original strict
three-sector nonnegative pair-additive model with nonempty entire core and T>0,

    J(M,P) <= T/18.                                      (1)

The support may contain cycles or repeated hub labels in a team. This statement
concerns the fixed obstruction J; no same-market assertion about every other
partial matching, or about the full subsidy, follows without applying its
hypotheses to those obstructions too.

## 1. Zero players and decomposition

All players at zero-worth diagonal labels have payoff zero in every original
core allocation, by tightness of the optimal diagonal matching. There is at
least one such player in every sector. Every original core therefore satisfies
every pair inequality: complete the pair with any zero-payoff player in the
missing sector. This conclusion uses the core constraints of the original full
teams; it does not change the coalition worth of a pair.

No P-team can consist of three leaves: its three labels would have degree one
and form an isolated incidence component, contradicting connectedness and the
presence of a hub. Thus each P-team contains zero, one, or two leaf labels.
Every leaf label belongs to exactly one P-team. Partition the leaf labels by
that team. Groups contain at most two labels.

For a group, retain its leaf diagonal pairs and its P-team pairs. Represent the
hub players of that P-team by zero-payoff dummy players of the corresponding
sectors. Form a three-label market with diagonal matching, the distinguished
team P0=(1,2,0), and diagonal worth zero at label 0. For two leaves, labels 1 and
2 represent the leaves after permuting sectors and diagonal labels. For one
leaf, one of these two labels is also zero. All other pair weights are zero.
All-hub teams have worth zero, since they are covered by zero-payoff players,
and can be omitted.

The entire original core, restricted to leaf players, is the Cartesian product
of these local original cores (with their zero coordinates omitted).

Forward inclusion: restrict an original core allocation to a group. Its total
is the sum of the group's diagonal worths. Every retained local full-team
inequality either maps to an original triple with the corresponding hub players,
or has only a retained pair and a dummy completer, in which case original pair
coverage proves it. Nonnegativity and zero dummy payoffs are preserved.

Reverse inclusion: combine any local core allocations and give every hub player
zero. The total is T. Every supported pair belongs to one group, except a
hub-hub pair, which has weight zero. A player incident to two nonzero supported
pairs places both in the same group: a leaf player has only its own diagonal
and its unique P-team edges; a hub player has only its unique P-team edges,
because its diagonal pairs have weight zero. Hence a triple with two or three
nonzero pairs lies in one group after dummy identification. A triple with just
one nonzero pair is covered by that group's pair inequality, available by its
zero diagonal. A zero-value triple is covered by nonnegativity. Thus every
original full-team constraint holds, proving the reverse inclusion.

This also proves that each original leaf coordinate ideal is exactly its local
core ideal. Separate attainment witnesses remain separate. The decomposition
is asserted at the exactly-zero boundary only.

## 2. Exact three-label module certificate

For every nonnegative pair-additive market supported on the diagonal and
P0=(1,2,0), with diagonal label 0 worth zero and nonempty original core,

    w(P0)+sum_{i not in P0}H_i/3-T0 <= T0/18.              (2)

`ZERO_HUB_MODULE.json` and `verify_zero_hub_module.py` certify the all-weight
bound exactly. The normalized synthesis LP uses T0=1, variable pair weights,
and a separate original-core allocation for each of the six unmatched players.
Its constraints use the already-proved sector-minimum projection of the entire
core. A final inequality makes the three nonnegative diagonal-0 pair weights
sum to at most zero. The stored rational dual has nonnegative inequality
multipliers, free equality multipliers, and exact coefficient domination for
every nonnegative primal variable. Its objective is 19/18 before subtracting
T0=1. No rounding correction or floating feasibility tolerance is used.

An integer primal example at T0=18 has six feasible core witnesses, all checked
against all 27 original teams, and obstruction at least 1. Its lower value and
the all-weight dual upper coincide. Therefore its actual original ideals give
exactly J/T0=1/18, even though diagonal-cap attainment is not assumed. The
verifier rejects an empty inequality dual. This is a finite parametric theorem,
not a sampled weight search.

## 3. Sum the modules

Every original unmatched player is either one of the two unused players at a
leaf, or absent from consideration at a degree-three hub. The local modules
have precisely these unmatched leaf players plus zero-ideal dummy players.
Their P-team worths sum to w(P), and their diagonal worths sum to T. By the
core product equality, their J values sum to the original J. Summing (2) proves
(1). Zero-total modules contribute zero and require no normalization.

## 4. What this leaves open

The preceding CORE_SLACK_LOCALIZATION.md forces low hub value on any putative
near-2/5 sequence in leaf/hub trees. Equation (1) excludes its exactly-zero
boundary, including cyclic supports. The missing step is a SIZE-INDEPENDENT
quantitative estimate when hub worth is positive but small. No continuity or
Lipschitz estimate is assumed: original ideals can respond discontinuously
across changing markets, and previously documented cycle weakening examples
make an unsupported perturbation argument unsafe.

Discovery on b=2,4,8 chain-of-hub supports, with normalized hub value capped at
0, .10 and .16, gave numerical maxima respectively

    b=2:  .05555556, .20032051, .27666667;
    b=4:  .05555556, .18611111, .26000000;
    b=8:  .05555556, .17916667, .25166667.

These positive-cap results are numerical evidence only. They suggest testing a
quantitative extension, but certify neither a common formula nor an all-size
upper bound. The exact zero-boundary theorem rests on the product-core proof
and rational module dual, not these larger numerical instances.
