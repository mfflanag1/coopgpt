# Fractional P weights are necessary for a sector-balanced tree construction

Date: 2026-09-07. All-size impossibility theorem for a restricted certificate construction, with a fractional positive control. This does not disprove the one-third subsidy conjecture. Global bounds remain 1/3 <= S_3 <= 2/5.

## Statement

Use the incidence-tree setting and notation of TREE_SLACK_IDENTITY.md. Impose:

1. P weights decrease away from each deletion root, and every nonroot diagonal mass is maximal, so E_i=0.
2. For every P-team e and sector s, sum_{i in U_s} p_(i,e)=1.
3. Each p_(i,e) is either zero or one.

Allow arbitrary feasible fractional same-sector transfers; their coefficients need not be integral.

**Theorem.** If the incidence tree has at least four degree-two label nodes, no certificate satisfying these restrictions reaches t=1.

Thus assigning each P-team wholly to one deletion row per sector cannot be the desired universal construction. This restriction includes sector-wise integral rooted-territory assignments. The theorem does not rule out fractional root-monotone weights, unrestricted sector totals, or other certificate supports.

## 1. Every selected join involving the deletion sector consumes capacity

Fix deletion row i in sector s. Let S_i be the set of P-teams with coefficient one. Root monotonicity implies that S_i, with its intervening labels, is connected to the deletion root whenever it is nonempty. Let B_i count labels at which a selected P-team uses the sector-s player and at least one other selected P-team uses another player.

We claim L_i>=B_i, where L_i=m-1-Q_i-P_i is the unused deletion-sector capacity.

If S_i is empty, B_i=0 and L_i>=0. Otherwise a selected team touches the deletion root and uses one of its other two players, since the deleted player is globally unmatched by P. The opposite pair at the root then has no residual capacity. At a nonroot label touched by S_i, maximal diagonal mass is zero. Its opposite pair has residual capacity one exactly when a selected team uses its sector-s player and no selected team uses either other player. At all untouched nonroot labels, diagonal mass is one, so there is no residual pair capacity beyond that diagonal.

The selected sector-s players occupy P_i distinct labels. Exactly B_i of these labels have another selected player. Hence total additional opposite-pair capacity beyond the diagonals is P_i-B_i. Therefore

    Q_i-D_i <= P_i-B_i.

Since E_i=0 gives m-1-D_i=2P_i, this implies

    L_i = P_i-(Q_i-D_i) >= B_i.                       (1)

## 2. A degree-two label forces at least one such join

Let label j have its sector-a player used by P-team e, its sector-b player used by P-team f, and its sector-c player unmatched. Write i0 for this latter player.

The diagonal pair missing sector c receives only diagonal coverage in this restricted construction. For a sector-c row other than i0, its maximum opposite-pair capacity equals its maximal diagonal mass, since j has no used sector-c player. For row i0, the root diagonal is zero. If S_i0 is nonempty, root connectivity puts a selected team at j and removes the opposite pair's capacity. If S_i0 is empty, R_i0=0 and no transfer can supply that pair. Thus its total coverage is sum_i d_(i,j).

Put

    O = sum_i p_(i,e)p_(i,f),
    M = max(p_(i0,e),p_(i0,f)) <= 1.

Since binary maxima obey max(x,y)=x+y-xy and each P-team has total coefficient three,

    sum_i d_(i,j) = u-7+O+M.

The target t=1 requires this to be at least u-4, giving O>=2. But sector balance limits the overlap from sector-c deletion rows to

    sum_{i in U_c} p_(i,e)p_(i,f) <= sum_{i in U_c} p_(i,e)=1.

Consequently at least one overlap comes from a deletion row in sector a or b. For that row, j is counted in B_i. Summing this conclusion over all degree-two labels gives

    sum_i B_i >= n_2,                                (2)

where n_2 is their number. Multiple labels counted for the same row remain separate terms in B_i.

## 3. Contradiction with the global slack budget

Equations (1) and (2) imply sum_i L_i>=n_2. But the exact identity at t=1, with E_i=0, says

    G_1 + sum_i L_i = 3,

and G_1>=0. Therefore n_2<=3 is necessary. This proves the theorem.

## 4. Independent calibration

Take r=5, m=11 and P_j=(6+j,j,j+1), j=0,...,4. This chain has exactly four degree-two labels. The existing closed-form uniform construction supplies a fractional certificate at t=1, with p_(i,e)=1/6 in every row, maximal diagonals, and sector totals exactly one. Thus the obstruction concerns binary weights; the fractional construction actually works on the same instance.

verify_tree_integrality.py reconstructs this control, checks every packing coefficient with the independent pair-domination checker, and verifies the additional sector-balance and maximal-diagonal conditions. It exhausts all 32 binary P assignments in each of the 18 deletion rows, retaining the 148 assignments satisfying root monotonicity, and checks the row-capacity lower bound exactly in every retained case. With --smt, the displayed fractional witness is checked against all original transportation constraints and must be SAT. A separate Boolean SMT model checks the necessary overlap and global capacity inequalities after this row elimination and must be UNSAT. The latter is a reduced check, not a claim that the monolithic binary transportation model returned UNSAT. That earlier monolithic attempt was stopped after the reduced verification succeeded. A timeout or unknown result from either retained check fails verification. These bounded checks corroborate the conventional all-size proof above.

Run `python3 -O verify_tree_integrality.py`; optionally add --smt using Python with z3 installed. Both variants are included through the package build's existing option.

## Research decision

Retire integral sector-wise assignment as a universal construction. Continue with fractional root-monotone weights and the capacity constraints. Three further random 48-edge trees (m=97, seeds 0,1,2) reached the numerical model ceiling 1+1/m under maximal diagonals and root monotonicity; those are discovery observations only and do not establish universal feasibility. The one-third upper theorem and cyclic cases remain unresolved. No novelty or field-level breakthrough is claimed.
