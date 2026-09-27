# Universal one-sixth pilot: exact certificate gate and a sharp factorization lemma

5 September 2026. Bounded independent theory cycle. The universal inequality H_i<=6*x_i remains unproved. This file records concrete certificates, a sharp feasibility lemma, and a failed transfer principle. Standard LP and difference-constraint ingredients receive no novelty claim; the triangle-cover argument needs literature comparison before any novelty language.

## 1. Exact ideal and floor LP certificates

Fix an optimal perfect triple matching. Let M be its player-incidence matrix and s its vector of team values; let E contain all triple incidence rows and w their values. The entire core is

K={p>=0: M p=s, E p>=w}.

Completeness, equal sector sizes, and nonnegative values allow an optimal matching to be completed to a perfect one. Nonempty K with total T>0 is compact, so all the following optima are attained and ordinary finite LP duality applies.

An ideal-payoff certificate for player i consists of unrestricted matching multipliers beta, nonnegative triple multipliers alpha, and

r=M^T beta-E^T alpha >= unit_i.

It proves H_i<=beta.s-alpha.w. Conversely minimizing that expression over such certificates gives H_i exactly. If sigma=E x-w is the slack vector at full leximin x and ell=r-unit_i>=0, then the certificate value is

x_i + ell.x + alpha.sigma.

The last term is material: an optimal ideal certificate need not use only triples tight at x. Requiring alpha.sigma=0 would add an unjustified restriction.

For a leximin stage, let F be previously frozen players and J its remaining players. The LP maximizes t subject to K, p_F=x_F, and p_j>=t for j in J. A dual uses alpha>=0, beta unrestricted, signed multipliers kappa for fixed coordinates, and theta>=0 supported on J with sum theta=1, satisfying

M^T beta-E^T alpha+kappa_F >= theta.

Its objective is beta.s-alpha.w+kappa.x_F. At an optimal stage, complementary slackness makes positive theta concentrate on binding floor coordinates, alpha on tight triples, and nonnegative residual coordinate multipliers on zero payoffs. The signed fixed-coordinate coefficients must be retained: they cannot silently be treated as nonnegative cover weights.

The productive transfer question is now precise: can one construct an ideal certificate of value<=6*x_i from the stage geometry and pair-additive identities, allowing non-tight triple inequalities? A proof that merely rescales theta_i to1 is insufficient because theta_i can decrease with the size of a critical budget.

## 2. The two required controls use different certificates

### Strict chain control

For w=P_ij+Q_jk, the established potential representation and partial-slack argument supplies a simple directed cycle containing exactly three player arcs, all with x payoff at most x_i. Its structural arcs are tight at x. Summing around this cycle gives a core-valid bound

y_i<=sum_{three cycle players j} x_j<=3*x_i.

This is an ideal certificate of bounded size; no large-dimensional floor-dual coefficient is divided through. The method is an application of classical slack balancing rather than a generic new algorithm.

### The existing all-q family

For an incoming-link target e_s, use five ordinary full-core inequalities/equalities:

c_{s-1}+e_{s-1}+g_{s-1}=4,
c_s+e_{s-1}+g_{s-1}>=3,
c_{s-1}>=b_s,
e_s<=b_s-c_s+f_s,
f_s<=1.

The first two give c_{s-1}-c_s<=1. Combining the remaining inequalities gives e_s<=1+f_s<=2, independently of q. The explicit whole-core ideal witness attains2. At full leximin the first mixed triple above has slack1-1/q, so this short ideal certificate is not a certificate consisting only of tight constraints at x.

In contrast, the second-floor budget follows by summing a path:

sum_{s=1}^{q-1} e_s+c_{q-1} <=1+a_0+sum_{s=1}^{q-1} f_s.

On the first-stage face, a_0=f_s=1/3; normalizing gives a floor dual with q equal target coefficients1/q. Used directly on the whole core with only anchor bounds a_0,f_s<=1, it gives a bound of order q, although the actual ideal is2. Thus direct rescaling of this natural floor certificate demonstrably loses precisely the size independence the desired theorem needs. The successful certificate uses an incidental mixed triple to bypass the entire path.

## 3. A sharp three-halves factorization lemma

**Lemma.** If nonnegative p=(u,v,z) covers every strict triple with nonnegative pair matrices A,B,C, then (3/2)*p admits a payoff-preserving split into three feasible bilateral dual covers, permitting real component payoffs. The multiplier3/2 is best possible for this assertion.

This lemma does not require efficiency; it applies in particular to every full-core point.

### Exact factor graph

For any proposed total payoff vector h=(U,V,Z), seek pair components

A: alpha_i,beta_j;
B: U_i-alpha_i,gamma_k;
C: V_j-beta_j,Z_k-gamma_k.

Their sums at every labeled player are exactly h. The required pair covers are

alpha_i+beta_j>=A_ij,
U_i-alpha_i+gamma_k>=B_ik,
V_j-beta_j+Z_k-gamma_k>=C_jk.

Set potentials a_i=alpha_i, b_j=-beta_j, c_k=gamma_k. These inequalities become difference constraints on a directed graph with three layers and arcs/costs

I_i->J_j: -A_ij,
J_j->K_k: V_j+Z_k-C_jk,
K_k->I_i: U_i-B_ik.

They are feasible exactly when every directed cycle has nonnegative cost. The cycle cost is total h-payoff of the players on that cycle minus the sum of its pair-edge values.

### Cover every cycle by actual triples

It suffices to inspect simple directed cycles: every closed directed walk decomposes into simple directed cycles, with both costs and multiplicities preserved. A simple cycle has length3r because its arcs move I->J->K->I. Around it take the3r consecutive three-vertex windows (each window follows two consecutive arcs), wrapping at the end. Each is an actual feasible strict triple with one vertex from each sector.

Every cycle vertex appears in exactly three windows, so summing their covering inequalities gives left side3*sum_cycle p. Every pair edge of the directed cycle appears as a consecutive edge in exactly two windows. The remaining, chord pair term in each window is nonnegative, by the hypothesis on A,B,C. Therefore

3*sum_cycle p >= sum_window triple_value >= 2*sum_cycle pair_edge_value.

Repeated windows in a three-arc cycle cause no problem: the inequality counts windows with their multiplicities. Thus for h=(3/2)*p every simple-cycle cost is nonnegative. Hence every directed cycle cost is nonnegative and the split exists.

### Explicit construction of the split

Adjoin a source with a zero-cost edge to every graph node. With no negative cycles, shortest-path distances d are finite and satisfy d_head-d_tail<=edge_cost. Take

alpha_i=d_{I_i}, beta_j=-d_{J_j}, gamma_k=d_{K_k},

and fill the other components by the payoff-preserving formulas above. These values satisfy all three bilateral cover systems. There is no guarantee that each component is nonnegative; imposing that restriction would be a different assertion.

### Sharpness

Take two players in every sector. Each of A,B,C has value1 for unequal indices and0 for equal indices. Every nonconstant binary triple has value2, and the two constant triples have value0. Uniform p_i=2/3 covers all triples. A complementary pair of nonconstant triples has total4, so p also belongs to the entire core and is its full leximin point.

The three opposite-index pair matchings form one directed six-cycle of total pair value6. The sum of p on its six players is4. Scaling by a factor lambda<3/2 leaves this cycle cost4*lambda-6<0. Thus no such factorization exists below3/2. This proves the multiplier is sharp.

## 4. A tempting transfer principle is false

The factorization lemma is a statement about feasible covers after increasing their total. It does not preserve the efficient slice, the full lexicographic optimum, or the chain structure: the factor graph now has cycles of arbitrary length3r.

In particular one cannot multiply the chain1/3 guarantee by the inverse factor2/3 and conclude universal protection2/9. The already proved q=10 coupled family has

x_e/H_e=1/6+1/20=13/60 <2/9.

Thus such an approximation-to-fairness inference is explicitly false, not merely unproved. Even a sharp and constructive dimension-independent approximation between covering descriptions is insufficient by itself to transfer full leximin guarantees.

## 5. New finite attainment supplies a literal six-coordinate certificate

The computation lane subsequently supplied a 27-player example: three old blocks, with added pair entries A_{a_0,d_1}=B_{a_0,i_2}=C_{d_1,i_2}=1. These make the new strict triple (a_0,d_1,i_2) worth3. The original block matching remains available with total24, and the separately checked full-core covers certify that value. No representation change or player deletion is involved.

The new inequality and the middle block's matched team give

b_1+d_1+h_1=3,
a_0+d_1+i_2>=3,
therefore b_1+h_1<=a_0+i_2.

Use the two small matched teams a_0+f_0+i_0=1 and a_2+f_2+i_2=1. Eliminating the two connector anchors gives the entire-core inequality

b_1+h_1+f_0+i_0+a_2+f_2 <=2.

This is a literal six-coordinate payoff budget. On a feasible common floor1/3, all six coordinates must equal1/3. In particular the full leximin payoff b_1 is fixed at1/3 in the first stage. On the whole core, nonnegativity gives H_{b_1}<=2; the independently certified ideal vector attains2. Thus the finite example attains exactly1/6.

This certificate is tight at x and involves six low-payoff players. The old path-family ideal certificate remains non-tight at x, so its lesson about permitting non-tight inequalities remains applicable. One example having a tight certificate does not justify requiring every ideal certificate to have that form.

The same finite example refutes the proposed stronger spread bridge

R_i=max_{y in K}(y_i-min_{j in same sector} y_j) <=3*x_i.

Its saved core vector z has b_1=2 and a_2=0, in the same first sector. Hence R_{b_1}>=2. Since H_{b_1}=2, R_{b_1}=2, while3*x_{b_1}=1. The bridge is false by a factor2; it is not merely unproved. This is recorded from /private/tmp/coopgt-pairadd-cycle3/experiment/finite_attainment_exact.json and can be checked by its ordinary matching/triple inequalities.

## 6. Bounded-cycle status

This cycle establishes the exact ideal/floor certificate interface, shows why the natural long-path floor certificate is the wrong object to rescale, and proves a sharp3/2 feasibility-factorization lemma. The new finite attainment has an especially transparent six-coordinate certificate. These findings do not establish H_i<=6*x_i universally.

A genuine proof still needs to show that arbitrary critical floor geometry admits an ideal certificate costing at most6*x_i; the long-path example demonstrates why simply bounding the number of active floor constraints is the wrong route. The approximation-to-fairness inference and the normalized-spread bridge have explicit counterexamples and should not be revisited as if they were viable lemmas. No broader search or manuscript edit was performed in this theory lane.
