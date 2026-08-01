# Three-game Farkas frontier

Fix a base-plus-two-arm family with edges \(b\to t_A\) and \(b\to t_B\).
For fixed \(n,A,B\), the family LP matrix is fixed; only its right-hand side
depends on the three games. Its Farkas cone is therefore the correct finite
object for the three-game theorem.

## Sensitivity reduction

Only two inequality rows contain changed worths:

- the core row for coalition \(A\) in game \(t_A\);
- the core row for coalition \(B\) in game \(t_B\).

A Farkas ray using neither row reduces to balancedness of the base after
substitution. A ray using only one changed row is already present in the
corresponding two-game family, which is feasible by assigning one endpoint
core point to both games. Therefore an infeasible three-game family requires
an extreme Farkas ray with positive weight on both changed rows.

This gives a precise finite target:

> Classify the extreme rays simultaneously sensitive to \(t_A(A)\) and
> \(t_B(B)\), and prove their right-hand-side inequalities from exactness when
> \(A\cap B=\varnothing\).

## Positive-circuit reduction

Eliminate the three free efficiency multipliers by subtracting, within each
game block, the stationarity equation of a reference player. The projected
Farkas cone is
\[
\{\lambda\geq0:D\lambda=0\},\qquad \operatorname{rank}D=3(n-1).
\]
Its extreme rays are exactly the support-minimal positive circuits of \(D\).
Together with the sensitivity reduction, absence of a positive circuit
containing both bump columns implies feasibility for every balanced endpoint
triple with those arm labels.

`src/search_both_sensitive_circuits.py` samples fundamental circuits directly.
It recovered the overlapping positive control as an exact nullity-one circuit
with unit coefficients. Across the canonical disjoint shapes it found no
both-sensitive circuit in 600,000 targeted random bases:

- \(n=4\), two-pair partition: 200,000 bases sampled;
- \(n=5\), \((|A|,|B|,|R|)=(2,2,1)\): 200,000;
- \(n=5\), \((3,2,0)\): 200,000.

This was stronger discovery evidence than random normalized-cone objectives,
but it was still misleading: the sparse-support search below subsequently
found exact disjoint circuits at \(n=5\).

Two exact support eliminations reduce that claim further:

- a both-sensitive circuit must contain at least one monotonicity column on
  each arm (otherwise the endpoint block with no transfer columns is already
  a positive core-only subdependency);
- it cannot contain both core rows \(T\) and \(N\setminus T\) in the same
  game, since their eliminated columns sum to zero and form a two-row positive
  subcircuit.

`src/minimize_both_sensitive_support.py` encodes these reductions in a sparse-
support MILP. It recovers an exact nine-row unit circuit for the overlapping
control. For the disjoint (n=4) two-pair shape, it enumerated all 120
solver-visible candidate supports of sizes 9 and 10; every one had exact
nullity at least 3, and the next support size was 11. Since the matrix rank is
9, an actual circuit has at most 10 rows. This is a finite diagnostic check,
not an exact enumeration certificate, because the MILP uses floating-point
tolerances; the paper's independent four-player theorem already settles that
case.

## Disjoint-circuit correction and exactness neutralization

At \(n=5\), the stronger core-subcircuit cuts expose both-sensitive disjoint
circuits immediately. For the partition
\(A=\{1,2,3\}, B=\{4,5\}\), one exact nullity-one circuit has unit weights on

- base core: \(\{3,5\}\);
- \(t_A\) core: \(A,\{1,4,5\},\{2,4,5\}\);
- \(t_B\) core: \(\{1,3\},\{2,3\},\{1,2,4\},B\);
- monotonicity: player 3 on the \(A\)-edge and player 5 on the \(B\)-edge;
- efficiency: \((0,2,2)\).

This refutes the proposed no-common-positive-circuit theorem. The circuit can
be negative on balanced endpoints: `src/verify_disjoint_balanced_family.py`
checks a rational family with exact Farkas right-hand side \(-1\). Its base is
exact, but its two bumped endpoints are not.

Exactness neutralizes this circuit. Encoding, for each proper coalition in
each game, a core point tight at that coalition gives a linear exactness model.
Maximizing the circuit's supported worth over that model returns exactly 4,
equal to its total efficiency weight. The sparse rational dual in
`src/verify_disjoint_circuit_exactness_bound.py` verifies the coefficient
identity and the bound using exact fractions. Consequently this circuit can
never certify infeasibility for an exact endpoint triple.

The arm-preserving group $S_3\times S_2$ generates six distinct Type-I
supports, and the transported exactness dual verifies all six exactly. Orbit
blocking then exposes a second symmetry-inequivalent ten-row unit circuit:

- base core: $\{1,5\}$;
- $t_A$ core: $A,\{2,4,5\},\{3,4,5\}$;
- $t_B$ core: $\{1,2\},\{2,3\},\{1,3,4\},B$;
- monotonicity: player 1 on the $A$-edge and player 5 on the $B$-edge.

Its orbit has twelve supports. Unlike Type I, Type II is neutralized by
balancedness alone. The two exact balanced collections recorded in
`src/verify_disjoint_minimal_circuit_types.py` have total weights $5/2$ in
$t_A$ and $3/2$ in $t_B$; their sum reproduces the circuit inequality.
Blocking both orbits makes the sparse MILP advance from support size 10 to 11.
Thus the solver-visible minimum-support frontier has exactly two symmetry
types, though the floating-point MILP is not a completeness proof.

The first support-eleven type found has unit weights on base row $\{3,5\}$;
$t_A$ rows $A,\{4\},\{2,5\},\{1,4,5\}$; $t_B$ rows
$\{1,2\},\{1,3\},\{2,3,4\},B$; and the same player-3/player-5 transfer rows
as Type I. Its orbit has twelve supports. Three exact balanced collections of
total weights $1/2,2,3/2$ in the base, $t_A$, and $t_B$ reproduce the circuit
inequality, so this Type III is also neutralized without exactness. Among the
first three symmetry types, only Type I is dangerous on balanced endpoints.

`src/enumerate_disjoint_circuits_exact.py` now replaces the floating-point
minimum-support claim. Since the eliminated matrix has rank 12, a circuit has
at most 13 columns. Primitive coefficients are minors of a
\(\{-1,0,1\}\)-matrix, so Hadamard's bound gives the exact normalized floor
\(1/(13\cdot12^6)\). Z3 therefore decides the Boolean support problem in exact
linear rational arithmetic without excluding a small positive coefficient.

## Balanced recoloring reduction

There is a uniform algebraic explanation for the neutralization certificates.
For a circuit with core multipliers \(\lambda_{g,S}\) and efficiency weights
\(a_g\), forget the game colors and put
\(q_S=\sum_g\lambda_{g,S}\). Summing stationarity across the three games
cancels every monotonicity transfer, so

\[
\sum_{S\ni i}q_S=\sum_g a_g\quad\text{for every }i.
\]

Thus the uncolored circuit rows always form a balanced collection. If this
collection can be fractionally recolored into three balanced collections
\(\mu_g\), while keeping
\(\mu_{1,A}\geq\lambda_{1,A}\) and
\(\mu_{2,B}\geq\lambda_{2,B}\), summing the three balancedness inequalities
proves the circuit inequality. Strict inequality at a distinguished row is
paid for by \(d_A,d_B\geq0\). The classifier is exactly a search for this
recoloring, followed by rational verification.

This compresses 608 of the 609 five-player circuit orbits into one lemma. The
only orbit whose aggregate balanced collection cannot be recolored with the
required lower bounds is Type I; its separate endpoint-exactness dual closes
the gap. A dimension-free recoloring theorem, possibly with a finite family
of exactness exceptions, is now the cleanest general proof target.

The sharper invariant is the **recoloring capacity** \(\rho\): maximize the
common fraction of the original \(A\)- and \(B\)-row masses retained in their
distinguished colors. `src/analyze_balanced_recoloring_capacity.py` verifies
both the primal coloring and its dual exactly. Across all 609 five-player
orbits, \(\rho\geq1\) except for Type I, where \(\rho=1/2\). The first
six-player \((2,2,2)\) probe finds a new obstruction with \(\rho=2/3\), but a
sparse exactness dual again proves zero minimum Farkas margin (indeed, it
proves the circuit inequality with an extra \(d_B/3\) term). The capacity
dual consists of coalition prices and player-potential vectors; its threshold
sets provide a concrete route for generating the needed tight exactness
witnesses. This connects the Bet 3 obstruction directly to Bet 1's
residual-level/carrier machinery.

There is now a sharp dimension-free lower bound. If
\(a=q_A/\lambda_{1,A}\) and \(b=q_B/\lambda_{2,B}\), optimally mixing the
all-\(A\) and all-\(B\) colorings gives
\(\rho\geq\rho_0=ab/(a+b)\geq1/2\). An explicit dual for Type I proves
equality at \(1/2\). Equivalently, every balanced-endpoint circuit has margin
at least
\((\rho_0-1)(\lambda_{1,A}d_A+\lambda_{2,B}d_B)\).

The manuscript now proves the corresponding dual characterization. For a
fixed circuit, nonnegativity on every exact endpoint triple is equivalent to
expressing its inequality as a sum of two-level exactness blocks
\(\alpha\mathbf1+\delta\mathbf1_U\), plus nonnegative multiples of the two
bump inequalities. Necessity follows by grouping the exactness LP dual by its
coalition-tight witness variables; cancellation of each witness's coordinates
forces precisely a two-level coverage vector. Hence the open general theorem
has been reduced to existence of this explicit combinatorial decomposition.

The representative \(n=6\) frontier now touches every disjoint arm-size
shape. Across \((2,2,2)\), \((3,3,0)\), \((3,2,1)\), and \((4,2,0)\), it
contains 62 distinct exact circuit orbits and 1,127 transported supports.
Every subunit-capacity circuit has exact endpoint optimum zero and a verified
rational two-level dual. This is not an exhaustive \(n=6\) result, but it has
yet to reveal any certificate mechanism outside the characterization above.

A direct-construction experiment now links the two duals. Restricting
exactness witnesses to weak and strict level sets of the two bumped-game
recoloring-dual potentials certifies all 31 deficient circuits tested through
all six seven-player geometries, with exact rational primal and dual checks.
In every case, one common threshold coalition suffices and at most one block
per game is used. It also compresses the five-player Type-I exception to two
blocks, both tight at \(\{1\}\). The next theorem target is an uncrossing
argument proving this single-threshold phenomenon.

In fact the threshold search reduces to the two maximum-potential sets
\(P_g=\operatorname{argmax}u_g\): at least one of \(P_1,P_2\) yields an exact
single-witness certificate in all 31 tested obstructions. This is now the
preferred dimension-free formulation.

The reduced dual recession cone is the support nullspace
\(K(q)=\{h:h(N)=0,\ h(S)=0\text{ on }\operatorname{supp}(q)\}\). If
\(h(U)\neq0\), shifting the dual potential along \(h\) enforces the witness
equation at no cost, proving \(\tau_U=\rho\). Exact rank calculations identify
four and only four flexible canonical extremes in the 31-case corpus; these
are exactly the four failed extremes. No case has both extremes flexible, and
all 58 rigid extremes have capacity one.

Projecting the potential orthogonally onto the support nullspace preserves the
ordinary dual objective and makes the gauge canonical. The exact quotient
audit then gives full capacity at both extremes in every case, 62/62. Thus the
current conjecture is that both extremes of a support-orthogonal optimal
potential repair every disjoint both-sensitive circuit.
Across all 609 exhaustive five-player circuits and 86 representative
six-/seven-player circuits, exact rank calculations find no support-nullspace
direction except swaps of support-twin players. Thus every potential level set
is rigid after quotienting in all 695 audited circuits.

A subsequent reduction removes the gauge dependence in that statement. The
base color is redundant in the ordinary recoloring LP, so it is equivalent to
choosing one balanced subcollection \(0\leq w\leq q\). Its dual has a single
zero-sum potential \(z\), with objective
\[
 \Phi(r_A,r_B,z)=r_Bq_B+
 \sum_Sq_S[z(S)+r_A1_{S=A}-r_B1_{S=B}]_+.
\]
Fixing a two-level witness \(U\) adds only the equation
\(z(U)+r_A1_{U=A}-r_B1_{U=B}=0\). For a computed ordinary minimizer, the
maximum and minimum coordinate classes of \(z\) repair 29/31 cases each and
31/31 jointly. This intrinsic two-extreme-set alternative is now the
preferred dimension-free formulation.

The enumeration is now complete through the rank bound for both five-player
disjoint shapes. For \((|A|,|B|,|R|)=(3,2,0)\), it finds 420 symmetry
orbits (4,914 transported supports), with orbit counts 2, 24, 83, and 311 at
support 10, 11, 12, and 13. Of these, 411 orbits (4,812 supports) are
neutralized by exact balanced-collection identities, eight (96 supports) by
balancedness plus \(d_A,d_B\geq0\), and the six-support Type-I orbit by the
coalition-tight endpoint-exactness dual.

For \((2,2,1)\), the exact terminal query finds 189 orbits (756 supports):
9, 27, and 153 at support 11, 12, and 13. Balancedness neutralizes 117
orbits (468 supports), and balancedness plus bump nonnegativity neutralizes
the remaining 72 (288 supports). No exactness-specific exception occurs.

Thus the corrected proof target is achieved at \(n=5\): every both-sensitive
positive-circuit inequality for disjoint arms follows from balancedness, bump
nonnegativity, or endpoint exactness. Combined with the overlapping and
singleton reductions and the known four-player theorem, this proves every
base-plus-two-bump exact family on at most five players feasible. The next
target is structural: derive the recurring neutralization identities without
enumerating circuits, or use the completed certificate corpus to identify the
first genuinely new mechanism at \(n=6\).

## Positive control

The known balanced, non-exact overlapping-arm obstruction at \(n=4\),
\(A=\{1,2,3\}\), \(B=\{2,3,4\}\), has exactly such a ray. Its active
inequalities, all with weight one, are

- base core: \(\{2,3\}\);
- \(t_A\) core: \(A,\{1,4\},\{2,4\}\);
- \(t_B\) core: \(\{1,3\},\{1,4\},B\);
- monotonicity: player 3 on the \(A\)-edge and player 2 on the \(B\)-edge;
- efficiency weights \((0,2,2)\).

Its stationarity matrix has nullity one, so this is an extreme ray, and its
exact Farkas right-hand side is \(-1\). This validates the sensitivity test.

## Disjoint-arm evidence

For the canonical open shape
\[
n=5,\quad A=\{1,2\},\quad B=\{3,4\},\quad R=\{5\},
\]
the new miner src/mine_family_farkas_rays.py sampled normalized cone vertices
under random and bump-focused objectives. This is discovery evidence only, not
a complete enumeration.

An independent family screen generated balanced, generally non-exact bases by
lowering arbitrary worths beneath the lower envelope of two to four common-sum
points. Both disjoint bumps were taken to the largest values certified balanced
by those points. Across 28,361 such families:

- infeasible families: 0;
- exactly boundary-slack families (within float tolerance): 4,292;
- minimum family slack: numerical \(-0.0\).

The new partition circuit and rational balanced counterexample refute that
stronger statement. The zero-hit screen is therefore another warning that
generic balanced-family sampling can miss the small normal cone of the actual
obstruction. Exact-game feasibility remains open because the counterexample's
two bumped endpoints are nonexact and the circuit inequality is provably
nonnegative when all endpoints are exact.
