# Joint transfer cuts are necessary for a composition proof

Date: 2026-09-07. Exact counterexample to an insufficient weight-selection criterion, with a constructive flow criterion and full-packing positive control. Global bounds remain 1/3 <= S_3 <= 2/5. No arbitrary-tree existence, sharp global constant, novelty, or external review is established.

## 1. Fixed block weights on the minimum-root-mass face

Use the leaf-only, E=0, sector-balanced block model of TWO_HUB_BLOCK_REDUCTION.md. There are B=2g+1 blocks, with g>=1 hubs. Fix rational P weights p_kb for each row type k=(b0,t,s) of multiplicity n_k=L_b0,t. Assume rooted monotonicity, 0<=p<=1, sector balance, and R=g+2.

For a leaf type (b,t), write

    delta_bt=1-p_(b,t,s),b-p_(b,t,s*),b,

where s,s* are its two missing sectors. Require delta_bt>=0. Require every hub load A_v<=4; ROOT_MASS_BALANCE.md then gives total hub slack one. Equality forces all root extras to equal their delta and all nonroot extra destinations to be leaves.

After its own-root payment, row type k has remaining supply per individual row

    a_k = sum_b r_b p_kb - delta_b0,t.

Require a_k>=0. In deletion sector s, its capacity per sector-s-used leaf in block b is p_kb. A block's demand is L_bs delta_bs.

The total row supply and demand agree in each sector. Indeed, summing a_k with multiplicities over deletion sector s gives r-(ell-L_s)+R-R_used_s, where R_used_s is the root mass at leaves used in s. Since R=ell-r, this equals L_s-R_used_s, the total leaf demand.

## 2. Necessary and sufficient block-cut criterion

For every deletion sector s and subset T of blocks, define

    D_s(T) = sum_{b in T} L_bs delta_bs,
    C_s(T) = sum_{k: deletion sector s} n_k
               min(a_k, sum_{b in T} L_bs p_kb).

**Fixed-weight criterion.** Subject to Section 1's assumptions, the weights admit an equality-face deletion certificate if and only if

    D_s(T) <= C_s(T)                               (C)

for every s,T. For two hubs, this requires at most 96 cut checks (32 per sector), regardless of sector size. This is an application of classical capacitated-flow theory, not a proposed novel max-flow theorem.

Necessity: row k can send at most its supply a_k into T, and at most the sum of its individual leaf capacities there. Add these limits over its n_k identical rows and all row types.

For sufficiency, use a network with source-to-row-type capacity n_k a_k, row-type-to-block capacity n_k L_bs p_kb, and block-to-sink capacity L_bs delta_bs. Minimizing a cut over which row nodes lie on each side gives exactly (C). Thus a flow saturating all block demands exists. The max-flow/min-cut theorem is established in Ford and Fulkerson's original [Maximal Flow Through a Network (1956)](https://www.cs.yale.edu/homes/lans/readings/routing/ford-max_flow-1956.pdf), retrieved freely on 2026-09-07.

Divide each row-to-block flow equally over the n_k rows and L_bs leaves of that type; zero multiplicities are omitted. This yields nonnegative f_kb<=p_kb with the exact required row and column totals. Root extras delta obey their pair caps because delta<=1-p at that root. Maximal diagonals make positive source and destination capacities disjoint, so rational greedy transportation realizes each individual row as in TWO_HUB_BLOCK_REDUCTION.md. Together with the P weights and diagonals, these are the required full packings. Rational data admit a rational construction, for example by scaling capacities to integers before max-flow.

The criterion specifies the remaining weight-selection problem; it does not prove that such weights exist for every tree. A restatement as these cuts is not completion of the active sharp-subsidy goal.

## 3. Exact failure of hub balance plus singleton/full cuts

COMPOUND_CUT_COUNTEREXAMPLE.json gives rational weights on an explicit m=27 tree with r=13, g=2 and block data

    r = [9,1,1,1,1],
    L = [[8,0,1],[1,0,1],[1,1,0],[0,1,1],[1,1,0]].

The full matching is retained in the data file. It is obtained from the different-port two-hub seed by eight chosen-sector leaf insertions in the central block.

The retained weights satisfy all of the following exactly:

- bounds and rooted monotonicity;
- sector balance and R=4;
- nonnegative leaf deficits and row supplies;
- A_1=A_2=7/2, hence hub slacks 1/2 each;
- every singleton block cut and the full-set cut, in every sector.

Nevertheless, in sector 0 the union T={0,1} has

    D_0(T) = 51250273/6677550,
    C_0(T) = 24053341/3338775,
    D_0(T)-C_0(T) = 285781/607050 > 0.

Thus these P weights have no transfer completion. Passing every individual block-capacity test and the total-capacity test is insufficient, even after satisfying the root-mass and hub-slack identities. Because the full-set cut passes and total supply equals total demand, each row also has enough total leaf capacity; the obstruction is genuinely a joint destination cut.

This is a counterexample to a certificate-selection criterion, not to S_3=1/3. COMPOUND_CUT_CONTROL.json supplies a different exact R=4 certificate on the same support, with 1,995 full rational packing entries. The control passes all 96 cuts and independent full-packing verification.

## 4. Reproduction and evidence levels

Run `python3 -O compound_cut_certificate.py` to reconstruct the positive control from its retained rational parameters, then `python3 -O verify_compound_cut.py`.

The verifier independently reconstructs topology, block counts and row types; checks all rational weight conditions; evaluates all 96 cuts directly with exact min operations; confirms the positive gap; checks all full-packing constraints in the positive control; extracts its block weights from those packing entries and checks all 96 cuts again. It imports no discovery optimizer or active-set reconstruction. An invalid zero-weight negative control is rejected.

Optional discovery/compound_cut_probe.py obtains the witness by enforcing singleton and full cuts, then maximizing a linear lower bound on one union-cut violation. Active affine equations are recovered over rationals and every discovery constraint is rechecked. Acceptance ultimately depends on the separate exact verifier, not solver status.

## 5. What the exploratory routes showed

A common proportional rescaling of surviving old weights worked numerically for the symmetric one-hub seed, with an optimum near 10/11, but failed on the retained two-hub seeds. Seeking seed weights with positive P weights, positive deficits and positive root-supply margins did not repair those extensions. These are numerical observations; no general impossibility theorem for proportional scaling is claimed.

A different trial used leaf-absorbing harmonic probabilities on the block tree, with one adjustable conductance per hub. Tuning each hub load to 7/2 passed six balanced/nonuniform calibration cases numerically, but failed a more unequal case. Allowing an unequal split of hub slack did not repair that case in the numerical search. This is not a theorem against all variable-conductance constructions. Retire these particular tuning rules rather than continuing near-identical variants.

The exact counterexample in Section 3 was subsequently constructed directly in the weight polytope. It is not claimed to have a harmonic representation, and its correctness does not depend on any conductance or scaling experiment.

## 6. Revised proof obligation

A useful composition rule must choose and rebalance P weights while preserving the full sector cut functions C_s(T)-D_s(T), or prove a smaller sufficient cut family from additional structure. The scalar hub-slack invariant, row supply bounds, and singleton/full cuts cannot replace that obligation. This points toward a global convex or dual-cut argument rather than another scalar rescaling or prescribed normalization.

The full three-sector target, original entire-core ideals, all original coalition worths, and free-only novelty requirements remain unchanged. Cyclic supports remain unresolved. No purchases or outreach occurred.
