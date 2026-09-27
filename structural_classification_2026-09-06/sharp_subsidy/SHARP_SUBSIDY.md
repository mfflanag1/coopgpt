# Frozen-ideal subsidy: active research checkpoint

**September20 audit update:** [independent audit and exact local refinement](audit_20260920/AUDIT.md). The global bound survives scoped model review with an explicit all-leaf-case repair. The local coefficient improves to13/18; global sharpness and novelty remain unresolved.

Date: 2026-09-08 UTC. Status: **sharp constant unresolved; uniform improvement internally checked.**

The current internally checked conventional bounds are **1/3 <= S_3 <= 39999/100000**. The [core-compatibility proof](CORE_COMPATIBILITY_UPPER.md) gives the uniform improvement below 2/5, with [exact verification and an internal audit](CORE_COMPATIBILITY_AUDIT.md). External specialist review and novelty confirmation remain pending. The lower bound uses a new family structurally distinct from the earlier triangle chain. Neither optimality nor novelty is established. Finite exact checks supplement the following all-parameter argument. The subsequent [exact reductions](REDUCTIONS.md) reduce the unresolved upper bound to connected sparse markets supported on two matchings and certify zero subsidy at two players per sector. The [leaf obstruction theorem](LEAF_AND_DELETION.md) now excludes every associated reduced obstruction with at most three leaf labels from exceeding one-third; five fixed configurations also have all-coefficient deletion certificates.

## Frozen target

There are three equally sized sectors. Pair matrices are nonnegative. Only full three-sector teams are productive, with value A_ab+B_ac+C_bc. Coalition worth is the maximum integral matching value within that coalition. Original grand worth T is positive and the original entire core C is nonempty. H_i=max_{x in C} x_i is frozen before any subsidy. Minimize s subject to y>=0, sum y=T+s, original coalition inequalities, and y_i>=H_i/3. S_3 is the supremum of s/T over this class. No original proper-coalition worth changes.

Nonnegative payoffs cover every coalition iff they cover every full team: sum the team inequalities over any matching and use nonnegativity on unmatched players.

## A family approaching one-third

For q>=1 set m=2q+1, with labels 0,...,2q in each sector. Initialize all three pair matrices to the identity matrix. For s=0,...,q-1 let

    e_s=(s, q+s, s-1) for s>0;
    e_0=(0, q, 2q).

For every e=(a,b,c), set A_ab=2, B_ac=1, C_bc=2. All three labels within each e are distinct. The e_s are disjoint as actual teams (each sector's labels are distinct). Their label hypergraph has a tree incidence graph: consecutive edges share one label, each edge has a private b label, and the endpoints have the remaining private labels.

**Claim.** T=3m, every original ideal is 3, and s_3=2q. Consequently s_3/T=2q/[3(2q+1)] tends to 1/3.

### Original core and individual ideals

Root the label incidence tree at an arbitrary label r, and assign r an arbitrary color k in {A,B,C}. Traverse outward. When a special edge is reached through its already colored parent label, color its two new labels by their designated sectors in that edge. Each edge therefore has at least two labels whose color equals their designated sector. There are no conflicting assignments because the incidence graph is a tree.

For this coloring c define x_{j,v}=1_{j=k}+2*1_{c(v)=j}. Each diagonal triple receives 3 and the entire vector sums to 3m. At the chosen coordinate (k,r), the payoff is 3.

Here is a complete check of all full-team inequalities. Every team receives a baseline of 1. Two positive off-diagonal pair entries can occur together only in a special edge: their shared actual player belongs to at most one special edge. Such an edge has worth 5 and at least two designated color matches, so receives at least 5. Two diagonal pair entries force all three labels equal; those teams have worth and payoff 3. All other teams have at most one off-diagonal entry and at most one diagonal entry. An off-diagonal entry of value 2 is on AB or BC. At least one endpoint has its designated color, because at least two of the three labels of its special edge match; the team therefore receives at least 3, covering its worth of at most 3. For the off-diagonal AC entry of value 1, the same endpoint argument applies, covering its worth of at most 2. Teams without off-diagonal entries have worth at most 1 unless diagonal, already handled. This exhausts the cases.

Thus x covers all coalitions. The diagonal matching has value 3m, and x covers all matchings with total 3m, proving T=3m and x in the original core. Every core vector must make each diagonal team tight; nonnegativity gives each coordinate at most 3. Since r and k were arbitrary, H_i=3 for every player.

### Exact subsidy

Every protected payoff has y_i>=1. The q special teams form a partial matching of total worth 5q. Its 3m-3q unmatched players require at least 3m-3q. Hence sum y>=3m+2q, giving s>=2q.

Conversely start with y_i=1 for all players and add 2 to the A player of every special team. Each special team then receives 5. Every other team has value at most 3 by the preceding classification and receives at least 3. This covers all original coalitions, meets all frozen floors, and totals 3m+2q. Thus s=2q.

The exact standard-library verifier tree_certificate.py constructs all 3m original-ideal witnesses separately, checks every team, verifies the matching lower bound and subsidy allocation, and rejects damaged allocations. For q=1,...,12 it passes 3,603,804 integer team checks and 12 negative controls. This is bounded computational corroboration; the preceding rooting argument supplies the all-q proof. No external review has occurred.

## Earlier generic upper bound: two-thirds

Choose an optimal perfect matching. An integral optimal matching can be extended to a perfect matching because sizes agree and weights are nonnegative. For any original core point p, each of its matched teams e is tight, so sum_{i in e}p_i=w_e. This tightness holds throughout the original core, implying H_i<=w_e for i in e.

Set y_i=max(p_i,H_i/3). Coordinatewise increase preserves all original coalition inequalities. On each matched team,

    sum_{i in e} y_i <= sum_{i in e} max(p_i,w_e/3) <= 5w_e/3.

The second inequality follows by maximizing a convex function over the nonnegative three-coordinate simplex of total w_e: at a vertex its value is 5w_e/3. Summing gives sum y<=5T/3. This proves S_3<=2/3 and gives an explicit allocation method. This older bound does not exploit pair additivity. It is superseded by [the improved universal bound](MIXED_DONOR_UPPER.md).

## Exact unresolved inequality

Let lambda_t>=0 be any fractional partial matching: d_i=sum_{t containing i}lambda_t<=1. Linear programming duality gives

    s_3 = max_lambda [sum_t lambda_t*w_t + (1/3)*sum_i (1-d_i)*H_i - T].

The floor vector need not cover teams; the dual remains valid after substituting y=H/3+z with z>=0. A sharp upper bound of one-third would follow precisely from

    3*sum_t lambda_t*w_t + sum_i (1-d_i)*H_i <= 4T

for every such lambda and every market in the frozen class. This statement is a target, not an established lemma. Proving it, or producing a certified counterexample, is the primary live task. Establishing it only for integral partial matchings at a fixed size does not suffice. However, the replication theorem in REDUCTIONS.md shows that an all-size integral-partial-matching proof is sufficient, and sparsification further reduces the relevant class.

## Prior family and route ledger

The earlier triangle family has exact s=2q/3 and T=6q+1; reducing its positive AB/AC entries from 2 to 1 leaves s unchanged and reduces T to 4q+1. Its ratio therefore improves from an asymptotic 1/9 to 1/6, but remains below the new construction. The original simplex certificates are checked in verify.py for both variants, q=1,...,8, including eight optional SMT checks of ideal upper bounds for q<=4. These finite checks alone are not their all-size proof.

Floating random screening tested 1,600 arbitrary or compatible diagonal markets without exceeding the already known lower bound. LP synthesis instead optimized pair entries and independent core witnesses for uncovered players for fixed partial matchings; 700 such trials found the new construction. Neither campaign is exhaustive. Discovery scripts and JSON outputs are retained under discovery/ and may refer to scratch dependencies; the certificate build is self-contained.

Next: attack the fractional inequality using pair-additive structure, while extending synthesis to genuinely fractional obstruction supports. After two failed variants of one mechanism, record the failure and pivot. Do not generalize K or rewrite the goal to declare completion of these bounds.

## Free-source and priority status

External grand-coalition payments and minimum-subsidy LPs are established ingredients: see Bachrach et al., [The Cost of Stability and Its Application to Weighted Voting Games](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/01/sagt2009_submission_17.pdf). Its ordinary cost is zero whenever the original core is nonempty; the present objective additionally imposes frozen original-ideal floors. This distinction alone does not establish a new theorem's priority.

The individual-core-maximum protection criterion also has prior bilateral literature: Núñez and Rafels, [Bargained stable allocations in assignment markets](https://www.bse.eu/sites/default/files/working_paper_pdfs/153.pdf), contains the half-optimal core. See the previous simultaneous_protection/SOURCE_STATUS.md for the detailed comparison already performed. Claims-constrained and resource-cooperative models still require a full comparison; [Resource Based Cooperative Games: Optimization, Fairness and Stability](https://people.umass.edu/yzick/papers/resource.coopgames.comsoc2018.pdf) is a retrieved lead, not a completed comparison.

Searches on 2026-09-07 did not certify priority. The prior Quint, Lucas and Stuart original-source gaps remain open under the no-purchase instruction. No purchases, paid consultations, specialist outreach, submission or established-novelty claim accompanies this checkpoint.
