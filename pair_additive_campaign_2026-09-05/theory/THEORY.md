# Pair-additive strict triples: first theory cycle

Date: 5 September 2026. Scratch-only independent theory lane. The full labeled nine-player core is retained; no smaller coalition receives direct production value. No claim below is a priority certification.

## Concrete outcome: the additive 1/3 constant is false

The computation lane's reduced nonnegative pair matrices are

A = [[0,0,0],[2,0,1],[0,1,0]],
B = [[0,0,1],[1,0,0],[0,0,0]],
C = [[0,1,0],[3,0,0],[2,0,0]].

Write players (a,b,c;d,e,f;g,h,i), and w_ijk=A_ij+B_ik+C_jk. The matching (a,f,i), (b,d,h), (c,e,g) has respective values 1,3,4. The displayed leximin vector below covers every triple and totals 8, so T=8 and these matching inequalities are equalities at every core point.

Thus a+f+i=1, b+d+h=3, c+e+g=4. The first common floor is at most 1/3; the feasible candidate attains it, fixing a=f=i=1/3. The cross triple (b,f,g) has value 4. On the remaining face,

b+f+g >= 4  implies  c+d+e+h <= 3+f = 10/3.

The second common floor is therefore at most 5/6. Equality fixes c=d=e=h=5/6, after which b=4/3 and g=7/3. This proves uniqueness and full leximin directly:

x=(1/3,4/3,5/6;5/6,5/6,1/3;7/3,5/6,1/3).

The entire-core point (0,0,0;3,1,1;3,0,0) covers all 27 triples and has total 8, attaining H_d=3; matching efficiency gives the reverse bound. Hence x_d/H_d=5/18<1/3. The computation lane additionally certifies full descending selection and rho=11/24. This does not prove vanishing protection or distance approaching two.

### Mechanism worth attempting to scale

A saturated small-total matched team fixes an early fairness level. A cross triple then reserves surplus for two players belonging to other matched teams, imposing a four-coordinate budget on the remaining low-payoff players. This is an exact mechanism inside the pair-additive class, unlike the earlier unrestricted recurrence construction.

The next question is whether these crossed budgets can be chained so that a target's ideal stays macroscopic while its leximin payoff decreases geometrically. Every new pair coefficient creates a whole slice of triple values; checking only the intended cross triple is invalid. That is the precise unresolved interface.

A simple failed scaling calculation illustrates the obstruction. Parameterize this sparse support by A_10=a, A_12=b, A_21=c, B_02=d, B_10=e, C_01=f, C_10=g, C_20=h, all other pair entries zero. Intended matching values are d,a+f,c+g. If its first-stage floor fixes the small team at d/3, the cross budget yields a prospective second floor

t = (a+f+c+g-b-e-h+d/3)/4.

But the incidental triple (first-sector player1, second-sector player2, third-sector player1), in zero-based indices, has value b. Combining its inequality u_1+v_2+w_1>=b with u_1+v_0+w_1=a+f and v_2<=d gives

H_{v_0} <= a+f+d-b.

Thus increasing a and b together to keep t small also removes the hoped-for growth in the ideal payoff. A scalable construction must address these slice constraints explicitly, not merely concatenate the displayed budget inequality.

## Exact structural lemma for the cycle-free strict subclass

Consider w_ijk=P_ij+Q_jk with both matrices nonnegative and m players in each sector. Choose optimal perfect matchings in P and Q. They are simultaneously realizable as triples by joining through the middle sector. Relabel so both matchings are diagonal; let s_j=P_jj+Q_jj. Their sum T=sum_j s_j is optimal for the triple market because any triple matching projects to feasible bilateral matchings.

The entire strict-triple core is exactly the set

u_j>=0, z_j>=0, v_j=s_j-u_j-z_j>=0,
u_i-u_j >= P_ij-P_jj for all i,j,
z_k-z_j >= Q_jk-Q_jj for all j,k.

Proof: matching efficiency gives the v formula. Triple (i,j,j) yields the first difference inequality and triple (j,j,k) yields the second. Conversely their sum is precisely every triple inequality. No direct bilateral coalitional constraints have been added.

This exact representation is useful as a control, not a new theorem claim; it may be implicit in classical locally additive assignment results. It distinguishes a chain of bilateral sectors from a triangle of pair interactions. The two-coordinate difference-constraint representation is lost when the third pair matrix is present. A fairness constant for this representation remains to be proved, and its existence must not be assumed from the ordinary bilateral bound.

## No-go observations

1. Balancedness does not force one optimal triple matching to project to optimal matchings in all three bilateral matrices. The source lane's Atay–Núñez2019 Example5 already refutes that premise (T=24, sum bilateral optima=29).
2. At a core point p, the slack tensor r_ijk=p_i+p_j+p_k-w_ijk is nonnegative and has zero third mixed difference. Consequently a tight four-corner parity class in any 2x2x2 cube forces all eight corners tight. More generally collections with identical pairwise marginals have equal total slack. This is standard linear algebra / marginal-polytope structure, not independently substantial novelty.
3. Nonnegative pair-additive slack need not be a sum of nonnegative pair slacks. The binary triangle potential r=#equal pairs-1 is nonnegative, zero on six states and two on the two constant states, and frustrates that decomposition. Do not silently replace strict-triple feasibility by three independent bilateral cores.
4. The 5/18 example falsifies only the benchmark 1/3. It supplies neither c_pair=0 nor d_pair=2. Those targets must stay separate.

## Next bounded proof obligation

Produce either (i) a reusable pair-additive block whose complete slice inequalities admit a certified two-input/one-output budget transfer while preserving an ideal witness, with a composition rule covering every mixed triple; or (ii) a dimension-independent inequality showing why those slice inequalities bound the possible amplification. Another isolated improvement of 5/18 is insufficient progress toward the stated structural objective.
