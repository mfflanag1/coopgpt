# Two-hub block reduction and exact nonuniform certificates

Date: 2026-09-07. Structural reduction of a restricted certificate model, plus six exact certificates. Global bounds remain 1/3 <= S_3 <= 2/5. Arbitrary two-hub feasibility, novelty, and external review remain unresolved.

## 1. Scope and block classification

Use the label/P incidence tree of LEAF_DILATION_THEOREM.md. Let g be the number of degree-three labels (hubs). Consider same-sector deletion certificates with E_i=0, three aggregate copies of every P-team, sector balance (one copy from each deletion sector), and zero P weights in every degree-two-root row. This restriction has not been proved without loss for the original subsidy problem.

Section 8 of that theorem forces equal row weights on P-teams connected through a degree-two label. Contract these connections into blocks. The resulting block/hub graph is a tree with 2g+1 blocks. In a block b let r_b count P-teams, L_bs count leaves used in sector s, and H_bs count hub ports in sector s. Put c_b=sum_s H_bs and ell_b=sum_s L_bs. Then

    r_b = ell_b+c_b-2,
    N_bs = L_bs+H_bs-1 >= 0,

where N_bs counts internal degree-two labels missing sector s. Indeed a block has r_b-1 internal labels. Counting its sector-s players gives r_b=(r_b-1)-N_bs+L_bs+H_bs. Counting all incidences gives the first identity.

For g=2 there are five blocks. The unique path between the hubs contains a single central block; the remaining four blocks are terminal. The central ports either have the same sector or different sectors, giving two cases up to sector permutations and permutation of the hubs/terminal blocks. A terminal block has one port and minimally two leaves, one in each other sector. A central block with different ports minimally has one leaf in the third sector and one P-team. A central block with equal ports minimally has two leaves, one in each other sector, and two P-teams joined through a degree-two label missing the repeated port sector.

These minima are sufficient for realizability of the block data. Each additional leaf of chosen sector s can be inserted using the P-node split of LEAF_DILATION_THEOREM.md Section 2. The split preserves all external ports and adds one internal label missing s. Thus every integer array satisfying L_bs >= max(0,1-H_bs) is realizable for either of the two port patterns. This classifies block data, not internal tree isomorphism types.

## 2. A finite-dimensional certificate criterion

The following system is sufficient for every tree with the specified block data, regardless of its internal degree-two arrangement. This is a parametric feasibility criterion, not a proof that the system is always feasible.

For each leaf type (b0,t) with L_b0,t>0 and each deletion sector s != t, introduce a row type k=(b0,t,s), of multiplicity n_k=L_b0,t. Its variables are p_kb, f_kb, h_kv, z_k, all nonnegative. Here p is the P weight per team in block b; f is extra opposite-pair mass per sector-s-used destination leaf in block b; h is extra pair mass at hub v; z is extra pair mass at the row's own root. Let a_v(s) be the block at hub v's sector-s port and let b_v(k) be the block adjacent to v toward b0. Let k*=(b0,t,s*) use the other missing sector.

Require:

1. 0 <= p_kb <= 1 and p_k,a_v(a) <= p_k,b_v(k) for every port a.
2. 0 <= f_kb <= p_kb; set f_kb=0 when L_bs=0.
3. 0 <= h_kv <= p_k,b_v(k)-p_k,a_v(a) for both a != s.
4. 0 <= z_k <= 1-p_k,b0 and z_k+p_k,b0+p_k*,b0 >= 1.
5. z_k + sum_b L_bs f_kb + sum_v h_kv <= sum_b r_b p_kb.
6. For every b,s: sum_{k with deletion sector s} n_k p_kb = 1.
7. For every b,t with L_bt>0: sum_{k with deletion sector t} n_k f_kb + p_(b,t,s),b + p_(b,t,s*),b >= 1, where s,s* are the other sectors.
8. For every hub v and sector s:

       sum_k n_k p_k,b_v(k)
       - sum_{k with deletion sector s} n_k h_kv <= 4.

There are at most 6(2g+1) row types and 5g+3 variables per row type. For g=2 this is at most 390 variables, independent of sector size. The retained discovery program also bounds f,h,z by one, already implied by these conditions.

## 3. Proof of sufficiency

A degree-two-root row uses every diagonal except its own with mass one. A leaf row uses its type's p_kb on every P-team in block b, and maximal nonroot diagonal masses. Ordering (1) makes weights decrease away from the root, so E_i=0 and its total remaining source supply equals sum_b r_b p_kb.

Give the leaf row extra pair mass z_k at its root, f_kb at each sector-s-used leaf in b, and h_kv at hub v. All other destinations have zero extra mass. The capacities are exactly (2)-(4). At a nonroot label j, write d_j=1-max_a Pload_a(j). Its residual source capacity is 1-Pload_s(j)-d_j; its residual opposite-pair capacity is 1-max_{a!=s}Pload_a(j)-d_j. At most one is positive. The root has zero source capacity. Hence every positive source can supply every positive destination without a forbidden same-label transfer. Condition (5) allows rational greedy transportation to realize the demands. This proves every deletion row is a fractional packing.

By (6), each P-team receives three aggregate copies. At a degree-two label, both incident team weights agree, its own deletion row has zero P weights, and total diagonal coverage is u-4. At a leaf j in block b used in t, aggregate diagonal coverage is

    u-5 + p_(b,t,s),b + p_(b,t,s*),b.

Its two used-player pairs receive their own-root extras, covered by (4). Its remaining pair receives extras from all deletion-sector-t rows, covered by (7). At hub v, diagonal coverage is u-sum_k n_k p_k,b_v(k), and the pair missing sector s receives the sector-s hub extras. Condition (8) supplies u-4. Thus all required diagonal pairs receive u-4 and all P-pairs receive three. The existing deletion argument gives the one-third fixed-obstruction bound for every admissible market on this support, with original entire-core ideals unchanged.

This proof uses only block data. It gives the same existence conclusion for any internal realization of those data, provided the displayed system has a feasible solution. We do not need, or claim here, equivalence of this symmetric compressed system to every unsymmetrized certificate in the restricted model.

## 4. Exact finite evidence and reproduction

TWO_HUB_BLOCK_PARAMETERS.json stores six rational solutions. Their full packing realizations are in TWO_HUB_BLOCK_CERTIFICATES.json. The same-port central configuration includes an internal degree-two label already at its minimal size; it is not covered by the previous no-degree-two stationary seed construction.

| Central ports | m | Full rational entries |
|---|---:|---:|
| Different | 11 | 344 |
| Different | 61 | 9317 |
| Different | 55 | 7369 |
| Same | 13 | 452 |
| Same | 63 | 9811 |
| Same | 57 | 7928 |

Run `python3 -O two_hub_block_certificate.py`, then `python3 -O verify_two_hub_blocks.py`. Realization and checking need only the standard library. The verifier imports no compressed-model or realization routines: it checks every player capacity, deletion exclusion, and pair coefficient directly, then checks topology, the central port case, sector balance, block constancy, maximal diagonals and E=0. Two negative controls reject empty coefficients and incorrect inventory. Total: 35,221 entries.

Optional discovery/two_hub_blocks.py uses SciPy to locate a candidate and SymPy to solve its active affine system over rationals. Every parameter constraint is checked exactly there. Acceptance of the retained full packing certificates does not depend on that discovery program's correctness or solver status.

## 5. Remaining composition obligation

The next mathematical obligation is feasibility for every admissible leaf-count array in both port cases, followed by a joining rule that preserves the same inequalities when a new hub is attached. The interface must track sector-specific P weights, hub capacities, root deficits and row supply simultaneously. Feasible isolated examples or a reformulation as the above LP do not discharge this obligation. An exact infeasible instance would refute this sufficient model on that instance; it would not itself refute S_3=1/3. Cyclic supports remain a separate unresolved part of the original target.
