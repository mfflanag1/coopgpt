# Varying P weights: a live route beyond the mixed donor bound

Date: 2026-09-07. Global bounds remain 1/3 <= S_3 <= 2/5. This note supplies a useful exact restriction of the next proof search, not a universal one-third theorem.

## 1. What the comparison establishes

The current mixed donor construction gives each P-team weight 1/h in every deletion row. Its balanced-junction capacity obstruction prevents simply raising its parameter above 4/5.

That limitation can be overcome on three specified junction patterns while retaining transfers only in the deleted player's sector. VARIABLE_P_CERTIFICATES.json contains exact one-third deletion certificates for junctions(2), junctions(4), and junctions(8), with m=11,19,35 respectively. The family junctions(b) is the existing construction in universal_template.py.

The independent verifier checks:

- every deleted-player exclusion and player capacity;
- aggregate pair coverage (u-4)mu+3P;
- exactly three aggregate copies of each P-team;
- every non-P triple has its other two sector labels equal, so its transfer changes only the deleted player's sector;
- connectedness, acyclicity and the specified junction counts.

All 4,177 retained rational entries pass. Therefore varying P-team weights across deletion rows, together with flexible diagonal transfers in that same sector, suffices for these patterns. Cross-sector transfers are not necessary for these fixed examples. No conclusion for every junction count or every connected pattern follows.

This observation redirects the next proof effort toward the distribution of P weights. It does not rule out cross-sector methods as another route.

## 2. Discovery and exact recovery

The floating support comparison allowed only P-teams, diagonal teams, and triples with two equal labels. It compared all transfer sectors with only the deleted player's sector. At b=2,4,8 both modes returned parameters approximately 1+1/m. These numerical optima are not asserted as exact optima.

The exact certificates use parameter 1, leaving room for rational recovery. P-team coefficients are rounded to denominator 10^12 and balanced so each P-team's aggregate is exactly 3. Other coefficients are rounded down, then scaled uniformly by the minimum exact remaining-player-capacity ratio. P-teams are disjoint, so their balanced row weights lie in [0,1]. The final independent verifier accepts the resulting coefficients without using the floating solver status, objective, or tolerances.

The optional discovery generator is discovery/coupling_probe.py. Run discovery/round_coupling.py after it to recover the three rational certificates alongside those discovery files, then place the generated JSON alongside a copy of verify_variable_p.py for independent checking. The canonical exact JSON is already included; no solver is needed for verification.

A fixed local rule with baseline 1/(u-2) failed numerical feasibility at b=2. Allowing its baseline to optimize, or using baseline 4/(5h), passed the one-third target at the tested small junction sizes. These are discovery observations only, not general formulas or certified impossibility results. The unrestricted exact certificates above are the retained mathematical evidence.

## 3. A transportation lemma for a general construction

The following gives a smaller, explicit proof obligation for the same-sector route. It is ordinary fractional transportation and max-flow reasoning, not a claimed new matching theorem.

Fix a deletion row i in sector s. Choose P-team weights p_{i,e} in [0,1]. A used player's P load is the weight of its unique P-team; an unmatched player's P load is zero. Let

    A_a = 1 - Pload(sector-s player a), except A_label(i)=0,
    B_j = min(1-Pload(other-sector player j),
              1-Pload(third-sector player j)).

Here B_j is the capacity of the diagonal pair in the two sectors other than s. Choose a diagonal mass d_j and pair-block mass q_j satisfying

    0<=d_j<=min(A_j,B_j),   d_j<=q_j<=B_j.

Put r_j=A_j-d_j, c_j=q_j-d_j, R=sum r_j and C=sum c_j. There exists a nonnegative matrix X_{a,j} with diagonal exactly d_j, row sums at most A_a and column sums exactly q_j **if and only if**

    C<=R,        c_j<=R-r_j for every j.                 (1)

To prove this, remove the diagonal d. The residual transportation graph connects source a to every destination j except j=a, with source capacities r_a and destination demands c_j. A singleton destination j can receive at most R-r_j. Any set of at least two destinations has all sources as neighbors, so its demand is at most C<=R. These are every cut condition for the bipartite fractional-flow problem, proving sufficiency by max-flow/min-cut. Necessity is immediate. The one-label case is also covered by c_1<=0.

Interpreting X_{a,j} as the triple with sector-s label a and the other two labels j gives a feasible fractional deletion matching after adding the chosen P weights. For rational input, ordinary exact rational flow constructs the coefficients.

## 4. The remaining universal obligation

For every unmatched row i choose p_{i,e}, d_{i,j}, q_{i,j} satisfying the preceding constraints and (1). It would suffice to arrange

    sum_i p_{i,e} >= 3                       for each e in P,

and, for every label j and pair missing sector r,

    sum_i d_{i,j}
      + sum_{i in U_r}(q_{i,j}-d_{i,j}) >= u-4.          (2)

Indeed a diagonal mass covers all three diagonal pairs; an off-diagonal transfer covers the diagonal pair missing its moving sector. Formula (2), together with three copies of P, proves exactly the required pair domination, including overlaps counted additively. Any additional non-diagonal pair coverage is harmless because weights are nonnegative.

Thus a universal assignment of these row marginals would settle the one-third upper bound constructively. The transportation realization itself is now explicit; selecting the marginals uniformly is the unresolved mathematical step. This is a sufficient route, not a redefinition of the original research goal or a claim that an LP restatement completes it.

One practical reason to work with the marginals is that every row of the current mixed donor construction uses m-1 teams and saturates all sector-s players other than i. Unused donor partners therefore cannot be recovered by simply adding more full triples to that row. A repair must rearrange existing loads, as variable P weights permit in the fixed certificates.

The next task is to derive such weights and marginals from general connected incidence structure, while continuing to search for actual markets above 1/3. The current 2/5 theorem, frozen original ideals, and free-only novelty constraints remain unchanged.

The [single-baseline local rule](LOCAL_RULE_NO_GO.md) is now exactly excluded on junctions(16), even after optimizing its common baseline. The unrestricted marginal model remains live; global selection of its P weights is still unproved.
