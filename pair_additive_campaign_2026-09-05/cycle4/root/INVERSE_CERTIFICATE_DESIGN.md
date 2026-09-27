# Inverse design from a fixed core certificate

This is an application of classical linear programming and core cover certificates, not a claim of a new optimization method. It explains why varying the old composition's weights made progress after its fixed weights had failed.

Fix an equal-sector strict assignment market's player set, a perfect matching M, a set of permitted nonnegative pair entries W, and nonnegative multipliers alpha on triple covers. Choose matching-equality multipliers beta so that the incidence identity

    c = sum_M beta_m 1_m - sum_E alpha_e 1_e >= 0

has c_i>0 at a designated target. The associated right side

    B(W) = sum_M beta_m w_m(W) - sum_E alpha_e w_e(W)

is linear in W. Any full-core point obeys c.p<=B(W), whenever M is optimal. Let C=sum(c)>0.

Normalize B(W)=C and solve for pair entries W and two allocations u,y subject to

    W>=0 on the permitted support, W=0 elsewhere;
    u>=1, y>=0;
    u and y cover every induced full triple;
    each matching team is tight at u and y.

Maximize y_i. This is a finite linear program: all induced triple values and both sets of cover constraints are linear. Perfect matching plus a complete nonnegative cover establish the true integral worth and a nonempty full core for every feasible design. The fixed certificate then forces the first global floor to equal 1, and fixes every c-positive coordinate to 1 on the entire first optimal face. Adding those coordinate equalities to the LP is redundant but can simplify its formulation. The target's full leximin payoff is therefore 1.

For every feasible design, nonnegativity bounds H_i<=C/c_i. A saved y gives H_i>=y_i. Thus y_i>6 already disproves the proposed one-sixth bound; if y_i=C/c_i, both the ideal and the objective ceiling are certified exactly without trusting floating solver optimality. No fixed-total constraint is needed: T(W)=sum_M w_m(W) varies linearly, and the matching equalities enforce efficiency.

In this cycle C=9 and the six selected targets had c_i=1. Exactly 65 pair positions were free, inherited from the earlier orientation201 composition. The first of six planned targets reached y_i=9, and the search stopped. The exact whole-core witnesses and budget survived independent verification and deterministic reduction to 21 players. This is a bounded search within one certificate/support cone, not an exhaustive survey of pair-additive markets.

The previous fixed-weight compositions remain correctly certified at their old ratios. Their failure did not exclude this weight cone. A useful future problem is to construct a repeatable family of feasible incidence identities and covers with increasing C/c_i and attained ideals, while controlling every mixed triple. Merely increasing certificate mass does not prove a smaller ratio: the pair-additive cover constraints and ideal witness must remain feasible. No such infinite family is established here, and no conjecture that 1/9 is sharp is proposed.
