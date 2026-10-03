# Candidate formulation 1: residual-budget propagation

Frozen before strengthened-relaxation solves, 2026-10-03. This is a consequence of established inequalities, with no priority claim.

Let mu be an optimal diagonal matching in the frozen three-sector model, C its nonempty entire core, P any player-disjoint partial matching, U its unmatched players, k=m-|P|>=1, T=worth(mu), R=T-worth(P), and u_(s,a) the sum of the two diagonal pair entries incident to player(s,a). Write H_i=max_C x_i.

For each i in U,

    k H_i <= R+(k-1)u_i.                                  (RP)

Proof. At every original core point, the opposite diagonal pair at a, completed by any sector-s player b, together with diagonal tightness yields x_(s,b)>=x_i-u_i. For a witness attaining H_i, summing this inequality over the k-1 other sector-s players in U, and including x_i itself, gives x(U)>=k H_i-(k-1)u_i. The disjoint P-team covers give x(U)<=R. Combine. Nonnegativity of all other coordinates is essential. If k=1 the statement is H_i<=R; there is no division by zero. No connectedness, distinct-label or sparse-support hypothesis is required.

This exactly coincides with a previously available elementary fractional deletion packing: P at mass1/k; every diagonal except the target label at mass1-1/k; and the opposite pair at the target label completed equally over the k-1 other unmatched players in that sector. For k=1 use P alone. Thus (RP) is NOT promoted as a new deletion theorem or, by itself, a successful new mechanism. Its use here is a diagnostic of information lost by the old ideal-vector relaxation.

CW-01 relaxed point: R=4/51,k=6,u_A6=1/51, but h_A6=4/51. (RP) requires H_A6<=1/34; violation=5/102. CW-04 also violates (RP). These separations do not certify the full subsidy of either fixed diagnostic market.

Bounded next test: add all (RP) rows to the same frozen ideal-difference relaxation on CW-01 and CW-04, one initial solve each. Check any recovered point exactly. If a point remains above1/3, record a precise failure of this added necessary condition. If no such point is found, numerical success alone is not a theorem. CW-05/CW-06 remain unoptimized.
