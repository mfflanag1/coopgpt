# Bounded repeated-label unicyclic audit

2026-09-07. Evidence: exhaustive finite support classification plus exact rational primal-dual certificates. No novelty or external-review claim. Global bounds remain 1/3 <= S_3 <= 2/5.

For m=4 and a partial matching P of two teams, consider connected incidence **multigraphs** on four diagonal-label vertices and two P-team vertices. Each sector occurrence contributes one edge, including parallel edges when a team repeats a diagonal label. There are six edges and six vertices, so connectedness gives cycle rank one. Require at least one repeated-label team.

**Bounded result.** For each support in this class, the supremum of the fixed-P obstruction

    J(M,P)/T = w(P)/T + sum_{i outside P} H_i/(3T) - 1

is exactly 1/6 over all nonnegative supported pair weights having a nonempty original core with the diagonal optimal. This is not a statement that every such market has subsidy at most T/6: other fractional packings remain possible.

## Exhaustive support classification

Enumerate all unordered pairs from the 64 ordered triples on labels 0,1,2,3. Require different labels within each sector across the two teams (P is a matching), union of used labels equal to all four, and intersection of the two label sets nonempty (connectedness). Retain a repeated-label team. There are 216 labeled patterns. Simultaneous label permutations and sector permutations preserve the market class and objective. Minimizing the tuple representation over these 24*6 transformations leaves exactly two representatives:

    ((0,0,1),(1,2,3))
    ((0,0,1),(2,3,0)).

Thus both ways of attaching the distinct-label team to the repeated-label team must be checked. This classification does not silently replace parallel incidence edges by simple edges.

## Exact all-weight verification

For each representative normalize the diagonal worth to T=1. Include all supported pair entries as variables and a separate nonnegative original-core witness for each of the six unmatched players. Every witness covers every original full team and totals one. The objective is w(P) plus one third of the six selected witness coordinates minus one. Compactness allows witnesses attaining actual H_i, so maximizing this system computes the supremum of J. Conversely every feasible witness system describes an admissible market and witnesses bounded by its actual ideals. Bounds 0<=variables<=1 are valid: diagonal tightness bounds payoffs, while a team containing each supported pair bounds that pair by T.

The retained certificates have exact feasible primal objective 1/6 and exact dual upper objective 1/6, with zero residual correction. They use respectively 36 and 40 nonzero team-inequality multipliers. The standard-library checker reconstructs all team constraints and uses rational/integer arithmetic. It independently reenumerates the 216 supports and rejects missing-orbit and empty-dual negative controls. It does not trust recorded solver objectives or verification fields.

Run `python3 -O verify_repeated_unicycle.py`. Discovery uses the existing full-team LP, not the rejected ideal-difference relaxation. Discovery scripts and their relevant dependencies are retained in discovery/repeated_unicycle_archive.zip.

## Consequence and stopping gate

This closes the smallest repeated-label branch at two P-teams; it is a calibration, not an all-unicyclic proof or an improved global bound. It supplies no cycle-opening boundary inequality. Do not expand this into a larger enumeration campaign without a structural hypothesis that the next computation can falsify. The load-bearing next obligation remains control of original-ideal changes under cycle opening, including arbitrary attached trees and heterogeneous weights.

Independent Claude review is not completed: the last authentication check reported logged out. A prepared packet is not review. No sources were purchased and no outreach was performed.
