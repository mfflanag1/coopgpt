# Arm-ratio exchange program

This note separates proved statements, falsified conjectures, exact evidence,
and the next proof target for Bet 3.

## Proved scalar and ceiling reductions

Write
\[
a=\frac{q_A}{\lambda_{1,A}},\qquad
b=\frac{q_B}{\lambda_{2,B}}.
\]
The scalar subcollection \(w=tq\) gives the exact lower bound
\[
\rho\ge \rho_0=\frac{ab}{a+b}
=\frac1{\lambda_{1,A}/q_A+\lambda_{2,B}/q_B}.
\]
Hence
\[
\frac{\lambda_{1,A}}{q_A}
+\frac{\lambda_{2,B}}{q_B}\le1
\quad\Longrightarrow\quad \rho\ge1.
\]

For fixed-witness capacity, the exclusive-arm ceiling gives
\[
T\ne A\Longrightarrow \tau_T\le a,\qquad
T\ne B\Longrightarrow \tau_T\le b.
\]
Thus an exclusive arm pins every successful distinct witness at capacity
exactly one.

## The corpus pattern and its exact counterexample

Across the original 695-circuit corpus, every circuit obeyed
\[
\rho_0\ge1\quad\hbox{or}\quad a=1\quad\hbox{or}\quad b=1.
\]
All 31 circuits with \(\rho<1\) lay in the exclusive-arm branch.  Put
\[
x=\lambda_{1,A},\quad y=\lambda_{2,B},\quad
U=q_A-x,\quad V=q_B-y.
\]
The scalar condition is \(UV\ge xy\).  All 97 nonexclusive circuits in the
old corpus satisfied it; 73 were on the boundary and 24 were strict.  They
also satisfied the stronger linear pattern
\[
U\ge y,\qquad V\ge x.
\]

Both patterns are false in dimension six.  Let
\[
A=\{1,2,3\},\qquad B=\{4,5\}.
\]
Use the monotonicity column for player 1 on the \(A\)-edge and player 4 on
the \(B\)-edge.  The game-block core supports, in bit-mask notation, are
\[
\{24,3,45\},\qquad
\{7,58,60\},\qquad
\{7,24,35,37,54\}.
\]
All rows have weight one except the game-2 row at coalition 24, which has
weight two.  Each local block is a nullity-one positive circuit.  Matching
the two shared monotonicity weights gives a global 13-column dependence of
rank 12, hence a support-minimal positive circuit.  Its arm masses are
\[
(x,y,U,V)=(1,2,1,1),
\]
so
\[
U-y=-1,\qquad UV-xy=-1,\qquad
\frac1a+\frac1b-1=\frac16.
\]

## Non-scalar repair

The forbidden ratio does not create a deficient circuit.  Its aggregate
balanced collection is
\[
q_3=1,\quad q_7=2,\quad q_{24}=3,\quad
q_{35}=q_{37}=q_{45}=q_{54}=q_{58}=q_{60}=1.
\]
The subcollection
\[
w_7=w_{24}=w_{37}=w_{58}=1
\]
has degree two at every player, while \(q-w\) has degree four.  It retains
one copy of \(A\) and two copies of \(B\), exactly the two distinguished
requirements.  Therefore \(\rho\ge1\).  An exact dual potential gives the
matching upper bound, so \(\rho=1\).

Fixed-witness reoptimization at masks 16 and 14 gives capacities \(4/3\)
and \(9/7\).  Thus the circuit is not a fragile boundary repair: canonical
non-scalar witnesses have positive room.

The construction, local ranks, primitive global circuit, arm masses, and
primal--dual capacity certificates are independently verified in
results/forbidden_ratio_glued_circuit_n6.json by
src/construct_forbidden_ratio_glued_circuit.py.

## Direct nonexclusive recoloring also fails

The local normal form supports a factorized adversarial search.  For the
same six-player geometry and selected monotonicity players, exact enumeration
finds 56 root circuits, 626 first-leaf circuits, and three second-leaf
circuits with crossed-\(A\) coefficient below the distinguished-\(B\)
coefficient.  Matching shared weights produces 59,304 distinct
product-forbidden global circuits.

Exact capacity was computed for the 5,000 smallest scalar lower bounds and
for one representative of every arm-ratio pair, 5,035 circuits in total.
Twenty-one are genuinely deficient and nonexclusive. Their capacities are
\(3/4\), \(5/6\), \(7/8\), or \(11/12\).

The strongest support found has
\[
(x,y,U,V)=(2,2,1,1),\qquad \rho=\frac34.
\]
An ordinary dual optimum has
\[
z=\frac14(1,-1,-1,-1,2,0).
\]
Its maximum set \(\{5\}\) and minimum set \(\{2,3,4\}\) have exact
fixed-witness capacities \(5/4\) and \(3/2\). Across all 21 deficient
circuits, both canonical extremes repair: the fixed capacities range from
\(11/10\) to \(3/2\).

The fixed-witness frontier is now much stronger than that selected screen.
Fix mask 16, the singleton containing the member of \(B\) not used by the
monotonicity column. Exact reoptimization of all 59,304 product-forbidden
gluings gives
\[
\tau_{16}\ge\frac98>1.
\]
There are 45 equality cases, 21 distinct capacity values, 19 projective
dual rays selected by the LP solver, and 18 potential weak-order types. The
solver selects two rays on the \(9/8\) frontier, but exact enumeration of the
full dual hyperplane arrangement gives 87 feasible rays, of which four are
sharp in three symmetry orbits. All
\(87\cdot59{,}304=5{,}159{,}448\) ray--circuit evaluations satisfy the
\(9/8\) bound, and arrangement minimization exactly reproduces the LP
capacity histogram. The local enumeration is fully exact:
rational rank is computed modulo 61, which is valid because every local
minor has absolute value below 56 by Hadamard, and every primitive positive
kernel is recovered from signed integer cofactors. Thus this is an
exhaustive result for the stated factorized local pattern, not merely a
selected capacity screen. The exact audit is
`results/glued_product_forbidden_fixed16_audit_n6_321.json`; the proof
program and the three sharp-orbit inequalities are in
`results/fixed16_glued_theorem_program.md`. The arrangement certificate is
`results/glued_fixed16_dual_arrangement_n6_321.json`.

The arrangement proof now factors locally.  For each dual ray, the
cross-multiplied \(9/8\) margin is a root score plus the matched root weights
times one first-leaf rate and one second-leaf rate.  Independently minimizing
the 626 and three leaf rates, then checking 56 roots, proves all 87 ray
inequalities with 59,595 exact local comparisons.  There are no negative
local margins, and the four zero-margin rays are exactly the global sharp
rays.  Since the local and arrangement coalition universes coincide, this
proves the bound for all 105,168 raw gluing triples in the pattern, not only
the product-forbidden subset.  See
`results/glued_fixed16_local_factorization_n6_321.json`.

Positive-part subadditivity reduces the first leaf further to its two
normalized arm masses.  Its bound is minimized at
\((q_A/m_A,q_B/m_A)=(3,0)\), giving
\(8[-\gamma_1+3r_A]_+-27r_A\).  A degree-only root bound over 12 mass types
then proves 86 arrangement rays; the sole exceptional ray needs three exact
root-incidence checks, with positive margins \(10,2,2\).  The complete
fixed-pattern proof now uses 1,047 root comparisons.  See
`results/glued_fixed16_analytic_compression_n6_321.json`.

The coefficient-three input is not dimension-free, and neither is the
resulting \(9/8\) constant.  Complete Peleg generation reproduces all 200,214
six-player minimal balanced collections and yields 1,320 seven-player leaves
with three-player arm ratio five.  Gluing one representative to all 56 roots
and three second leaves gives 168 exact global circuits, 21 below \(9/8\),
with minimum fixed-witness capacity \(13/12\).  All four leaf symmetry orbits
break \(9/8\), while none of the 672 canonical-orbit gluings falls below one.
Thus the replacement target is unit root absorption, not a dimension-free
improvement above one.  Exact certificates are
`results/full_n5_peleg_escape_n7.json` and
`results/ratio5_leaf_orbit_gluings_n7.json`.

The unit threshold is now proved uniformly over the first leaf for this
root--second-leaf pattern.  At target one, positive-part subadditivity gives
the exact cancellation
\[
\frac{H_r(q^1)-r_Aq^1_A}{m_A}\ge-\gamma_a,
\]
with no dependence on \(q^1_A/m_A\).  Equivalently, if
\(z\le q^0+q^2\) has
\[
\deg(z)=\beta\mathbf1+m_Ae_a+\delta\mathbf1_U,
\qquad z_B\le q^0_B,
\]
then \(w=q^1+z\) is a capacity-one recoloring for every compatible first
leaf.  Exact absorbers exist for all \(56\cdot3=168\) root--second-leaf
pairs.  The dual remainder is in fact at least
\((m_Ar_A+m_Br_B)/3\), which yields
\[
\tau_U\ge1+\frac1{3\max\{q^1_A/m_A,2\}}.
\]
Thus every ratio-five leaf has the structural bound \(16/15\), independently
of its orbit.  See `results/unit_root_absorption_program.md` and
`results/unit_root_absorption_n7.json`.

Thus balanced recoloring is not the general theorem. The missing positive
mechanism is precisely the one-witness, two-level exactness correction.
The factorized search and exact records are in
results/glued_local_circuit_hunt_n6_321.json.

## Why the random searches missed it

Earlier seeded basis searches found 317 exact circuit records and only
recovered the nonexclusive ratio pair \((2,2)\).  The explicit glued circuit
shows that these searches missed a small normal cone.  Their nonfinding was
correctly classified as discovery evidence rather than exhaustion.

Adding the glued circuits gives a 717-circuit audit:

- 52 circuits have capacity below one;
- 31 have an exclusive arm and 21 do not;
- 22 nonexclusive circuits violate both the scalar product and linear
  cross-arm conditions;
- the first has ordinary capacity one, while 21 require exactness-specific
  fixed-witness repair.

## Column identities that remain useful

Let \(c_{g,T}\) be the eliminated core column and let \(m_i^A,m_i^B\) be
the star-edge monotonicity columns.  The matrix has the exact identities
\[
c_{1,A}=c_{0,A}+\sum_{i\in A}m_i^A,\qquad
c_{2,B}=c_{0,B}+\sum_{i\in B}m_i^B.
\]
A positive circuit cannot contain every column of either signed identity,
because that would put a second dependence inside its support.  The glued
counterexample shows, however, that these qualitative exclusions do not
imply any universal arm-mass inequality.

## Revised theorem target

The direct nonexclusive-recoloring statement is false. The viable theorem is
the two-extreme-set repair conjecture for the exactness-extended capacity.
A first gluing lemma is proved: when a
support-minimal global circuit uses one monotonicity column on each arm, its
three incident block supports are all nullity-one local circuits.  Indeed,
core-only kernels would give additional global directions; the leaf
relations are therefore unique, and their scalable shared coefficients make
the root kernel isomorphic to the global kernel.  All 717 audited circuits
satisfy this one-row hypothesis.

For the certified root--second pattern, the absorber theorem now describes
the one-witness box polytope uniformly over the first local ray.  The desired
general alternative remains:

1. ordinary balanced recoloring has capacity one; or
2. an extreme coordinate set of an optimal support-orthogonal potential
   supplies a two-level exactness correction reaching capacity one.

This is a weighted degree-zonotope separation theorem, not an arm-ratio
inequality. The new deficient circuits show that the exactness correction is
not a technical afterthought; it is necessary.
