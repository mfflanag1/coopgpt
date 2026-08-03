# Capacity-one root absorption

This note records the first result in the glued program that is uniform over
the first leaf.  It explains why the ratio-five Peleg leaves break the
dimension-free \(9/8\) constant but do not threaten capacity one.

## Abstract absorption lemma

Let \(q^0,q^1,q^2\) be the root, first-leaf, and second-leaf core
collections after matching the two monotonicity coefficients \(m_A,m_B>0\).
Write \(a\) and \(b\) for the selected players on the two arms and suppose
\[
\deg(q^0)=\alpha_0\mathbf 1+m_Ae_a+m_Be_b,
\]
\[
\deg(q^1)=\alpha_1\mathbf 1-m_Ae_a,
\qquad
\deg(q^2)=\alpha_2\mathbf 1-m_Be_b.
\]
The distinguished retention requirements are
\[
x=q^1_A,\qquad y=q^2_B.
\]

Fix a nonempty proper witness \(U\).  Suppose there is a subcollection
\(z\le q^0+q^2\) such that
\[
\deg(z)=\beta\mathbf 1+m_Ae_a+\delta\mathbf 1_U,
\qquad z_B\le q^0_B.
\]
Then the glued fixed-\(U\) capacity is at least one.

Indeed, put \(w=q^1+z\).  It is a subcollection of
\(q=q^0+q^1+q^2\), and
\[
\deg(w)=(\alpha_1+\beta)\mathbf 1+\delta\mathbf 1_U.
\]
Moreover \(w_A\ge q^1_A=x\), while
\[
(q-w)_B=q^0_B+q^2_B-z_B\ge q^2_B=y.
\]
Thus \(w\) is the required two-level exactness recoloring at capacity one.
The proof uses no information about the support or arm mass of \(q^1\).

## Dual cancellation at the unit threshold

The same mechanism is visible in the canonical dual.  For a feasible ray
\((r_A,r_B;\gamma)\), put
\[
H_r(q)=r_Bq_B+
\sum_Tq_T[\gamma(T)+r_A\mathbf 1_{T=A}-r_B\mathbf 1_{T=B}]_+.
\]
If \(u=q^1_A/m_A\) and \(v=q^1_B/m_A\), positive-part subadditivity gives
\[
\frac{H_r(q^1)-r_Aq^1_A}{m_A}
\ge r_Bv+[-\gamma_a+r_Au-r_Bv]_+-r_Au
\ge-\gamma_a.
\]
The coefficient \(u\) cancels exactly when the target is one.  This is why
no dimension-free bound on \(q^1_A/m_A\) is needed, and why the same argument
cannot preserve a universal target strictly above one.

After this cancellation, the remaining expression is
\[
R_r(q^0,q^2)=
r_Bq^0_B+
\sum_T(q^0_T+q^2_T)
[\gamma(T)+r_A\mathbf 1_{T=A}-r_B\mathbf 1_{T=B}]_+
-m_A\gamma_a.
\]
Root absorption is equivalently the assertion \(R_r\ge0\) for every
feasible ray.

## Exact root--second-leaf theorem

For the certified lifted \((3,2,1)\) geometry on seven players, there are 56
root rays and three second-leaf rays.  Every one of the 168 pairs admits an
exact absorber \(z\) of the form above for the fixed witness \(U=\{3\}\).
The absorbers are stored explicitly and checked coefficientwise in
`results/unit_root_absorption_n7.json`.

An independent exact primal--dual minimization of \(R_r\), normalized by
\[
m_Ar_A+m_Br_B=1,
\]
gives the histogram
\[
\begin{array}{c|rrrr}
\min R_r&1/3&1/2&2/3&1\\ \hline
\text{pairs}&30&102&9&27.
\end{array}
\]
In particular, the stronger uniform inequality
\[
R_r(q^0,q^2)\ge\frac13(m_Ar_A+m_Br_B)
\]
holds on all 168 pairs.  This is not merely nonnegativity: the root and
second leaf supply a strict reserve before the first leaf is attached.

Since the three second leaves have \(q^2_B/m_B=2\), every compatible first
leaf obeys
\[
\boxed{
\tau_U\ge
1+\frac{1}{3\max\{q^1_A/m_A,2\}}.
}
\]
For the ratio-five Peleg leaves this gives the dimension-free-in-the-leaf
bound \(\tau_U\ge16/15>1\).  The exact global optimum \(13/12\) is stronger,
but the new bound explains structurally why all four ratio-five leaf orbits
survive.  As the first-leaf ratio grows, the displayed reserve tends to
zero, identifying one as the natural universal threshold.

## Scope and next lift

The theorem is uniform over every first leaf satisfying its local degree
identity; it is therefore strictly stronger than the four-orbit census.  Its
remaining finite input is the set of 56 roots and three second leaves.  The
next dimension-free step is to replace their 168 stored absorbers by a
structural sufficient condition on a root--second-leaf pair, or to generate
an exact pair outside this class that violates absorber feasibility.

There is now an exact minimal-balanced encoding for that search.  Let
\(\bar a=N\setminus\{a\}\) and \(\bar b=N\setminus\{b\}\).  The root degree
identity implies that
\[
\mathcal C_0=q^0+m_Ae_{\bar a}+m_Be_{\bar b}
\]
is balanced, while the second-leaf identity implies that
\[
\mathcal C_2=q^2+m_Be_{\{b\}}
\]
is balanced.  Conversely, removing the two displayed cosingletons from
\(\mathcal C_0\), or the displayed singleton from \(\mathcal C_2\), recovers
the respective defective degree identities.  Exact incidence-rank checks
show that all 56 regularized roots and all three regularized second leaves
are minimal balanced collections.  Thus adversarial root--second discovery
can be carried out inside the Peleg census machinery already used for the
first-leaf breakthrough, filtering for two cosingletons in the root and one
singleton in the second leaf.

Within the current root census, 33 of 56 roots already admit an absorber
without using the second leaf.  The remaining 23 are exactly the roots with
\(q^0_A=0\), \(q^0_B=1\), and \(m_B\ge2\); all are repaired after the second
leaf is included.  This isolates the first genuinely adversarial
root--second stratum for the next search.

The first targeted lift of that stratum is also complete within the certified
parent family.  Applying Peleg cases 1--4 to the 56 regularized roots and
retaining descendants with both distinguished cosingletons and the root
coalition \(B\) gives 604 distinct seven-player roots: 159, 113, 104, and
228 raw decoded descendants from cases 1, 2, 3, and 4, respectively.  Of
these, 275 do not absorb without the second leaf.  Nevertheless, all
\(604\cdot3=1{,}812\) root--second pairs admit an exact absorber.  There are
zero failures.  Exact dual minimization on all 1,812 pairs also preserves the
same normalized reserve \(1/3\); every Peleg case contains equality pairs.
See `results/root_absorption_descendants_n7.json` and
`src/hunt_root_absorption_descendants_n7.py`.

This makes Peleg-closure of absorber feasibility the next proof target.  The
screen is exhaustive for all four constructions whose parent or parents lie
in the certified 56-root family; it does not yet include fourth-case unions
in which the two distinguished cosingletons come from different non-root
parents.

## Peleg case-1 closure theorem

The first Peleg case is now closed analytically.  Normalize the regularized
root MBC \(\mathcal C_0\) to degree one, and let \(I\subseteq\mathcal C_0\)
be a case-1 marking.  Thus \(\lambda(I)=1\); the new player is attached to
exactly the coalitions in \(I\).  Retaining the root geometry forces
\[
N\setminus\{a\},N\setminus\{b\}\in I,
\qquad B\notin I.
\]
Because the incidence columns of \(\mathcal C_0\) are independent, there is
a player potential \(v\) satisfying
\[
v(T)=\mathbf1_{\{T\in I\}}
\qquad(T\in\mathcal C_0).
\]
Balancedness gives
\[
v(N)=\sum_{T\in\mathcal C_0}\lambda_Tv(T)=\lambda(I)=1.
\]
The two marked cosingletons then give \(v_a=v_b=0\), and the unmarked
coalition \(B=\{b,u\}\) gives \(v_u=0\).

If the parent root already has a root-only absorber \(z\), transform every
coalition of \(z\) according to \(I\).  Its new-player degree is
\[
\sum_{T\in I}z_T
=\sum_Tz_Tv(T)
=\beta v(N)+m_Av_a+\delta v_u=\beta,
\]
so it is a child root-only absorber.  This proves direct closure for all 93
admissible markings of the 33 root-only parents.

For a genuinely adversarial parent, write the child's old-player potential
as \(g\) and its new coordinate as \(s\), and put \(h=g+sv\).  The preceding
identities make \(h\) a feasible parent fixed-witness potential.  Root hinge
values are transported exactly.  If \(v(T)\ge0\) on the second-leaf support,
then
\[
[g(T)+sv(T)+c_T]_+
\le[g(T)+c_T]_++v(T)[s]_+.
\]
Since \(\deg(q^2)=\alpha_2\mathbf1-m_Be_b\),
\[
\sum_Tq^2_Tv(T)=\alpha_2v(N)-m_Bv_b=\alpha_2.
\]
The privately lifted second leaf contains the new singleton with coefficient
\(\alpha_2\), so its singleton hinge pays exactly for the second term.
Consequently the child remainder dominates the parent remainder and inherits
the same \(1/3\) reserve.

The remaining sign condition is now a five-template check.  Across the 66
case-1 markings of the 23 non-root-only parents, the interpolation potentials
are
\[
\begin{array}{c|r}
v&\text{multiplicity}\\ \hline
(0,0,0,0,0,1)&20\\
(0,0,1,0,0,0)&21\\
(0,1,-1,0,0,1)&1\\
(0,1,0,0,0,0)&22\\
(0,1,1,0,0,-1)&2.
\end{array}
\]
Each is nonnegative on the complete second-support universe
\(\{7,24,35,37,38,51,53,54\}\).  Hence all 159 admissible case-1 markings
preserve unit absorption, and the adversarial 66 preserve the normalized
\(1/3\) reserve.  The exact sign certificate is
`results/peleg_case1_absorption_closure.json`, generated by
`src/audit_peleg_case1_absorption_closure.py`.

## Peleg case-2 closure theorem

Case 2 is now closed by an explicit correction.  Let
\(t=\lambda(I)<1\) and \(\kappa=1-t\), the coefficient of the new singleton.
The interpolation equations force
\[
v(N)=1-\kappa,\qquad
v_a=v_b=-\kappa,\qquad v_u=\kappa.
\]
Put
\[
d=e_a+e_b-e_u,
\qquad \widetilde v=v+\kappa d.
\]
Then
\[
\widetilde v(N)=1,
\qquad \widetilde v_a=\widetilde v_b=\widetilde v_u=0,
\]
so if the child's old-player potential is \(g\) and its new coordinate is
\(s\), the potential \(h=g+s\widetilde v\) is parent-feasible.

On the root support, the parent hinge differs from the transported child
hinge by \(\kappa s d(T)\).  Whenever \(d(T)\ge0\),
\[
[x+\kappa s d(T)]_+
\le[x]_++\kappa d(T)[s]_+.
\]
The normalized root degrees give
\[
\sum_Tq^0_Td(T)
=\deg(q^0)_a+\deg(q^0)_b-\deg(q^0)_u=1,
\]
so the new root singleton of weight \(\kappa\) pays exactly for this term.
On the second leaf, whenever \(\widetilde v(T)\ge0\), the same inequality
applies and
\[
\sum_Tq^2_T\widetilde v(T)
=\alpha_2\widetilde v(N)-m_B\widetilde v_b=\alpha_2;
\]
the privately lifted second-leaf singleton pays exactly \(\alpha_2[s]_+\).
Thus the child remainder dominates the parent remainder and inherits its
unit bound and normalized \(1/3\) reserve.

Both sign conditions hold on every one of the 113 admissible case-2
emissions:
\[
d(T)\ge0\quad(T\in\operatorname{supp}q^0),
\qquad
\widetilde v(T)\ge0\quad(T\in\operatorname{supp}q^2).
\]
There are zero exact sign failures.  Hence Peleg cases 1 and 2 are now
structurally closed for the certified root family.  The classification and
sign audit are in `results/peleg_case23_absorption_closure.json`, generated by
`src/audit_peleg_case23_absorption_closure.py`.

## Peleg case-3 closure theorem

Case 3 is now closed on the certified root family.  Let
\(\kappa=1-\lambda(I)\), let \(D\) be the split coalition of parent weight
\(\lambda_D>\kappa\), and put \(\theta=\kappa/\lambda_D\).  The split
interpolation potential is defined on the parent MBC by
\[
 w(T)=1\quad(T\in I),\qquad w(D)=\theta,\qquad w(T)=0
 \quad\hbox{otherwise}.
\]
Balancedness gives \(w(N)=1\), while convexity gives the exact split-column
transport
\[
 \lambda_D[g(D)+s w(D)]_+
 \le (\lambda_D-\kappa)[g(D)]_+
      +\kappa[g(D)+s]_+.
\]

There are 104 decoded emissions, split by role as follows:
\[
\begin{array}{c|rrr}
D&\bar a&\bar b&B\\ \hline
\text{emissions}&21&62&21.
\end{array}
\]
If \(D=\bar a\), the interpolation identities force
\(w_a=1-\theta\) and \(w_b=w_u=0\).  The ordinary root columns transport
exactly, and the changed coefficient plus the unsplit remnant reduce to
\[
 (m_A-\kappa)\bigl([g(\bar a)]_+-g(\bar a)\bigr)\ge0.
\]
The potential is nonnegative on the complete second-leaf support in all 21
emissions, so the private second singleton pays the remaining transport term.

If \(D=B\), then \(w_a=w_b=0\) and \(w_u=\theta\).  The witness-corrected
potential
\[
 \widetilde w=w+\theta(e_b-e_u)
\]
has \(\widetilde w_u=0\).  Its root interpolation error and all its values on
the second support are nonnegative in every one of the 21 emissions.  The
root and second correction masses telescope exactly against the private
second singleton.  The split \(B\)-hinge can lose at most \(\kappa r_B\).
For the seven distinct parent markings and three second leaves, an exact
primal--dual audit proves the sharp strengthened parent inequality
\[
 R(q^0,q^2)\ge\kappa r_B;
\]
all 21 normalized minima are zero.  Hence every \(B\)-split preserves unit
absorption.

For \(D=\bar b\), 50 of the 62 children already admit a root-only absorber.
Only 12 descendants remain.  They are closed by a split-aware primal lemma.
Move the unsplit mass \((m_B-\kappa)e_{\bar b}\) into the old root core and
scale the second leaf to coefficient \(\kappa\).  If separated
subcollections \(z^0,z^2\) and \(0\le t\le\alpha_2\) satisfy
\[
 \deg(z^0+z^2)=\beta\mathbf1+m_Ae_a+\delta e_u,
 \qquad z^0(I)+t=\beta,
 \qquad (z^0+z^2)_B\le q^0_B,
\]
then attach the new player to the marked columns of \(z^0\), retain \(z^2\),
and add \(t\) units of the private new singleton.  The old degrees are
unchanged and the new degree is exactly \(\beta\), so this is a child
absorber.  Exact rational certificates exist for all \(12\cdot3=36\)
residual root--second pairings, with zero failures.

Thus Peleg cases 1--3 preserve unit root absorption throughout the certified
family.  Case 4 is now the sole remaining Peleg-closure step.  The full
case-3 certificate is `results/peleg_case3_split_transport.json`, generated
by `src/audit_peleg_case3_split_transport.py`.

## Peleg case-4 closure theorem

Case 4 is now closed as well.  Let \(\mu\) and \(\nu\) be two normalized
parent MBCs whose union has a one-dimensional balancing kernel, and let
\[
 \omega=(1-t)\mu+t\nu,
 \qquad 0<t<1,
 \qquad \omega(I)=1.
\]
The child attaches the new player to the columns in \(I\).  Remove the two
marked cosingletons from \(\omega\) to obtain the mixed source root
\(q^\omega\), with coefficients \(m_A,m_B\), and match the source second
leaf to \(m_B\).

The same split-aware primal condition used in the residual part of case 3 is
now sufficient without any interpolation potential.  Suppose separated
subcollections \(z^0\le q^\omega\), \(z^2\le q^2\), and a private-singleton
mass \(0\le s\le\alpha_2\) satisfy
\[
 \deg(z^0+z^2)=\beta\mathbf1+m_Ae_a+\delta e_u,
 \qquad z^0(I)+s=\beta,
 \qquad (z^0+z^2)_B\le q^\omega_B.
\]
Attach the new player to precisely the marked columns of \(z^0\), leave
\(z^2\) on the old players, and add \(s\) units of the private new singleton.
The old-player degrees retain the displayed absorber form, while the new
player has degree \(z^0(I)+s=\beta\).  The \(B\)-retention inequality is
unchanged because decoded descendants require \(B\notin I\).  Hence the
lifted subcollection is a child absorber.

The exact census contains 324 rank-one parent unions.  Of these, 201 parent
pairs produce 228 decoded case-4 emissions, all distinct; 90 already absorb
from the child root alone.  For every emission and each of the three second
leaves, the split-aware source system above is feasible: 684 exact rational
certificates, zero feasibility failures, and zero coefficientwise failures
after mapping them into the seven-player child.  The mixing parameters are
\(3/7,1/2,5/9,4/7,3/5,5/8,2/3\).

Consequently all four Peleg constructions preserve unit root absorption on
the certified 56-root family.  The finite closure burden has been eliminated;
the next Bet-3 target is to promote the split-aware condition itself from
these exact certificates to a dimension-free sufficient theorem.  The
case-4 artifact is `results/peleg_case4_split_aware_closure.json`, generated
by `src/audit_peleg_case4_split_aware_closure.py`.

The audit is generated by `src/audit_unit_root_absorption_n7.py` using exact
rational reconstruction and independently stored primal absorbers.
