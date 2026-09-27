# A fixed slack budget for same-sector certificates on incidence trees

Date: 2026-09-07. All-size necessary structural identity for the certificate model. Global sharp bounds remain 1/3 <= S_3 <= 2/5; this is not a universal existence proof.

## Setting

Let the label/P incidence graph be a tree, with r>=1 P-nodes, m=2r+1 labels, h=r+1 unmatched players per sector, and u=3h deletion rows. Every P-team uses three distinct labels. Consider feasible deletion matchings consisting only of P-teams and triples whose other two labels coincide in the deleted player's opposite sectors. Assume exactly three aggregate copies of each P-team.

For row i, let p_(i,e) denote the P-team coefficients, d_(i,j) the diagonal coefficients, and q_(i,j) the total mass of non-P triples whose two opposite-sector labels are j. Put

    P_i=sum_e p_(i,e),    D_i=sum_j d_(i,j),    Q_i=sum_j q_(i,j).

Root the incidence tree at the deleted player's label. Each nonroot label j has a unique parent P-node e_i(j). Each P-node has exactly two child labels. Let M_(i,j) be the maximum of the incident P weights at label j.

## Nonnegative losses

Define

    E_i = m-1-D_i-2P_i,
    L_i = m-1-Q_i-P_i.

Both are nonnegative.

For L_i this follows by summing capacities of the deleted player's sector: at most m-1 total triples are possible, and their total mass is P_i+Q_i.

For E_i, each nonroot label has diagonal capacity at most 1-M_(i,j), while M_(i,j)>=p_(i,e_i(j)). Every P-node is counted at its two child labels. Hence

    D_i <= m-1-sum_{j nonroot} M_(i,j) <= m-1-2P_i.

More precisely,

    E_i = sum_{j nonroot} [1-M_(i,j)-d_(i,j)]
        + sum_{j nonroot} [M_(i,j)-p_(i,e_i(j))].

The first sum measures loss from non-maximal diagonal placement. The second measures violations of the condition that P weights decrease away from the root. Each summand is nonnegative. Thus E_i=0 if and only if all nonroot diagonals are maximal and the parent P-weight is at least every child P-weight at each nonroot label. The deleted label's diagonal is zero by exclusion.

## Identity

Let C_(j,s) be aggregate coverage of the diagonal pair at label j missing sector s, counting only non-P triples. Suppose each C_(j,s)>=u-5+t, and define

    G_t = sum_(j,s) [C_(j,s)-(u-5+t)] >= 0.

A diagonal triple contributes three diagonal pairs; every other allowed non-P triple contributes exactly one. P-teams contribute none because their labels are distinct. Therefore

    sum_(j,s) C_(j,s) = sum_i (2D_i+Q_i).

Substitution gives

    2D_i+Q_i = 3(m-1)-5P_i-2E_i-L_i.

Since sum_i P_i=3r, m=2r+1 and u=3r+3, subtraction of the target coverage yields the exact identity

    G_t + 2 sum_i E_i + sum_i L_i = 3 + 3m(1-t).       (1)

In particular every one-third certificate, whose target is t=1, obeys

    G_1 + 2 sum_i E_i + sum_i L_i = 3.                (2)

This budget is independent of tree size. In particular sum E_i<=3/2 and sum L_i<=3. A positive fraction of deletion rows cannot each incur a fixed positive E_i as the tree grows.

Also, this certificate model necessarily satisfies

    t <= 1+1/m.

Equality forces G_t=0, every E_i=0, and every L_i=0: every pair hits its target exactly, all nonroot diagonals are maximal, P weights decrease away from each deletion root, and every row saturates all available players in its deletion sector. These conditions are necessary; their simultaneous feasibility is not proved here.

## Interpretation and scope

Earlier CUT_TRANSPORT.md proved E_i=0 for its specific inverse-component weights. The identity above applies to arbitrary P weights and arbitrary feasible same-sector diagonal transfers on every incidence tree. It explains why abandoning maximal diagonals offers only a bounded total allowance, rather than an extensive repair budget.

For each root, weights that decrease away from that root can also be decomposed by their level sets: for 0<a<=1, select all P-nodes with p_(i,e)>=a. Each selected node includes every ancestral P-node, so adjoining the root and intermediate labels produces a connected rooted subtree (or just the root when no node is selected). Integrating these indicators recovers p. This standard level-set decomposition supplies a different representation for the remaining design problem; it is not itself a coverage certificate or a proof of feasibility.

The next proof question is whether root-monotone P weights and maximal diagonals suffice at t=1 for every incidence tree, with three aggregate copies of each P-team and the necessary transportation capacities. The original broader goal also includes cyclic incidence patterns and arbitrary fractional obstructions. Neither is replaced by this tree subproblem.

## Verification

verify_tree_slack.py reconstructs row P, diagonal, and opposite-pair masses directly from retained exact packing certificates. It independently roots each tree, verifies the two nonnegative components of E_i, checks aggregate coverage and capacities through the established coefficient verifier, and verifies (2) exactly. The checks corroborate the conventional all-size derivation, and do not extend the checked certificates to arbitrary trees.


## Bounded discovery following the identity

Six 24-edge random trees passed the t=1 target numerically with sector-balanced P totals. These tests do not prove that sector balance is without loss. In two further tests (12 edges, seed 0; 24 edges, seed 2), imposing E_i=0 directly by the equalities d_(i,j)+p_(i,e_i(j))=1 at every nonroot label still attained the numerical ceiling 1+1/m. The existing capacity constraints enforce root monotonicity under these equalities. Exact universal feasibility remains unproved.

The independent slack verifier checks seven retained certificates, 315 deletion rows and 25,855 rational packing entries. The inverse-component constructions spend the entire budget on unused sector capacity (L=3, E=G=0). The numerically optimized and exactly rounded certificates spend almost all of it on extra coverage (G near 3), with tiny rounding losses. These exact measurements help distinguish two different ways to use the same total allowance.
