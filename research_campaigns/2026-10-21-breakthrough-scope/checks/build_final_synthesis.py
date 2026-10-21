from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[1]
header='''UNBOUNDED FUNDING INFLATION OF THE OWN-REPORT MINIMUM-NORM ENVELOPE
CoopGPT three-hour research campaign,21 October2026
Internal theorem draft; external correctness and priority review pending.

MAIN STATEMENT.
For every C>0 and N0, there exist N>=N0 fixed actual owners,2N resource
coordinates, one finite minimum F of nonnegative linear forms with binary
coefficients, and fixed full bundles b_i=e_i+e_(N+i), such that T=F(sum b_i)=1
and the TRUE own-report envelope satisfies

                 sum_i M_i^F(b) > C sqrt(N) T.

The same class has unbounded sum_i M_i^F(b)^2/T^2, and an unbounded ratio
between envelope funding and full-profile raw minimum-norm funding.
Along an explicit owner-count sequence the funding is at least

        (1/40) sqrt(N) (log N/log log N)^(1/3) T.

This is an architecture-specific obstruction. Every example admits the
simple efficient rule that pays all output to its common veto owner on
the fixed-bundle underreport domain. The theorem is therefore NOT a lower
bound for arbitrary mechanisms, a result for activity arity three, or a
solution of the unrestricted optimal-mechanism owner/resource gap.

CONTRACT.
For any real profile b define v_b(S)=F(sum_(i in S)b_i). Let q(v) minimize
sum_i x_i^2 subject to x>=0 and x(S)>=v(S) for every coalition. There is
NO efficiency equality. Define
 M_i^F(b)=sup{q_i(v_(a_i,b_-i)):0<=a_i<=b_i coordinatewise}.
This is the actual supremum over all real unilateral underreports, not
an endpoint surrogate. It covers all coalitions because M>=q(v_b).
It is nondecreasing in each owner's own report because the supremum's
domain expands, with other owners fixed. These are payment-only individual
incentives, not coalition-proofness, outside-option protection, or private-
cost truthfulness. At each profile an active supporting form of F gives
an efficient nonnegative cover. Thus each underreport's q coordinate is
at most T and every envelope is finite. The number of supporting forms
can be exponential; polynomial-time computation is not asserted.

PROOF ROADMAP.
Part I constructs a transitive family of binary cover rows. For each
owner, deleting only some of that owner's incident rows makes its local
minimum-norm coordinate equal the total multiplier mass. The normalized
aggregate grows without limit as the alphabet Q grows.
Part II adds a common veto and realizes ALL selected unilateral report
comparisons in ONE production function with the SAME owners and bundles.
Part III derives the finite and asymptotic funding consequences. Neither
numerical feasibility nor a finite search substitutes for the all-Q proof.

PART I. FINITE Q-ARY ROW CONSTRUCTION
The following construction follows the frozen reviewed source, with the\nexplicit full-cover KKT bridge requested by the reviewer added below.
Its original word 'candidate' records provenance; see the final audit
ledger for the current verification state. Symbols here are local: n is
base owner count, N later denotes amplified actual owner count.

'''
qary=(R/'proofs/activation_qary_cube_proof.txt').read_text()
# Preserve the construction, then add the explicit cover KKT bridge requested by review.
qary=qary[qary.index('1. PARAMETERS'):qary.index('SCOPE.')]
qary=qary.replace('Therefore the full cover\nis z=(1/k)1 and rho=n/k^2. Translate the focal witness to each owner.', 'For the full cover, the uniform vector z=(1/k)1 is feasible. Let alpha\nbe the translation-orbit distribution of any row. Its mean is(k/n)1,\nso lambda_R=(n/k^2)alpha_R gives A^T lambda=z, and every row is tight\nat z. These explicit KKT multipliers prove z is the full cover projection\nand rho=n/k^2. Translate the focal witness to each owner.')

part2='''
PART II. COMMON VETO AND EXACT FIXED-OWNER REALIZATION

A. KKT amplification with binary deletions.
Let a base have n coordinates, full unit-demand projection z with norm
squared rho, and for each i a binary incident-row deletion witness q^i
with nonnegative KKT multipliers lambda^i. In our construction its focal
coordinate and total multiplier mass both equal ell=1/t. Complementarity
implies ||q^i||^2=ell: all positive multipliers are on retained unit rows.
Since deletion enlarges the feasible region, ell<=rho.

Take B disjoint base copies and one common owner u. For every base row R
in each block impose x_u+x(R)>=1. Then N=Bn+1 and minimum total cover T=1:
paying1 to u suffices and any generator requires total at least1. The full
minimum-norm cover has
 u_full=B rho/(1+B rho),    x_full=z/(1+B rho) in every block.
This follows by minimizing u^2+(1-u)^2 B rho over0<=u<=1, or by KKT.

For a focal private owner i in one block, keep every off-i row at demand1,
retain the supported own rows at1 and delete other own rows to0. All
other blocks retain full demand1. Put
 eta=1/[1+(B-1)rho+ell],    u_i=1-eta.
Use eta q^i in the focal block and eta z in every other block. Retained
rows are feasible because u_i+eta=1, and supported retained rows are tight.
Deleted rows have RHS0 and zero multiplier. Scale each base multiplier
by eta. Their sum is eta[(B-1)rho+ell]=u_i, so veto stationarity also holds.
This certifies the unique projection of this binary relaxed system.
The final construction deletes all unsupported own rows. One independent
audit instead retains additional own rows whose potential is already
at least t; that alternative has the same projection and certificate but
defines a different selected game. Either choice is valid; we use the
support-based choice consistently in this final proof.
Every private focal coordinate is therefore
                 p=ell/[1+(B-1)rho+ell].
All changed rows contain i. Translation ensures one such witness for
EVERY private owner. These are separate own-report comparisons at the
same full institution, not simultaneous deviations by different owners.

B. Turn the entire family of comparisons into one production function.
Let G be the full generator family, each containing u. For any selected
binary demand array a_R define the coalition game
 g_a(S)=max({a_R:R in G,R subset S} union{0}).
For nonnegative payments its cover is exactly the generator cover. The
full game v has every a_R=1. Let w^j be each owner's selected relaxed game,
and set w^u=v. Then0<=w^j<=v<=1; all these games vanish without u; and
w^j(S)=v(S) whenever j is absent from S.

For any such game g and nonempty coalition A define h^(g,A) on N resources:
 h_i=1 if i is outside A;
 h_u=g(A) if u is in A;
 h_i=0 for every other i inside A.
Every coefficient is0 or1. For every coalition S, h^(g,A)(S)>=g(S): if S
has an element outside A its contribution1 suffices; otherwise S subset A
and monotonicity plus the common veto give the inequality. Equality is
attained with A=S for nonempty S. The empty coalition has value0. Thus
                         g(S)=min_A h^(g,A)(S).

Use N base resources X and N control resources Z. Define ONE function on
ALL nonnegative real vectors by
 F(X,Z)=min{h^(v,A) dot X;
            h^(w^j,A) dot X+Z_j: j in V, nonempty A subset V}.
This finite min-linear function is nonnegative, monotone, continuous,
concave and positively homogeneous. Give owner j the FIXED full bundle
b_j=e_j in X plus e_j in Z.

At full reports the induced game equals v. For a coalition containing j,
the j-family has its control cost1 and cannot reduce v<=1. For a coalition
not containing j, the j-family equals v by w^j=v off j. The baseline family
attains v. If only j hides its control coordinate, its family becomes
w^j exactly. Every other present owner's family still costs at least1,
and an absent owner's family equals v on that coalition. Therefore the
entire coalition game becomes exactly w^j. The same owners and bundles
are used in every comparison. In particular the actual all-real envelope
includes every certified private p and the full veto coordinate.
At the full aggregate F=v(V)=1.

No characterization of every additional real underreport is necessary for
this LOWER bound: they are allowed and can only increase the supremum.
The stronger all-real coordinate caps, when needed for exact limits, are
proved separately in CONSOLIDATED_THEOREM.txt Section5 and its audits.

C. Scope control: an efficient competing rule exists here.
For N>=2 the baseline form with A=V\\{u} is X_u, hence F<=X_u everywhere.
Within the fixed bundles' underreport domain, coalitions without u have
value0. Paying the grand output entirely to u covers every coalition,
is efficient, and is own-report monotone for every owner. Consequently
this proof isolates the failure of the chosen minimum-norm envelope.
It cannot be promoted to an impossibility theorem for all mechanisms.

PART III. FUNDING CONSEQUENCES

A. A finite all-Q lower bound.
Use d=16Q(Q-1)(Q+2), all Part I parameters, and B=floor(1/rho).
The complement mixture w has focal1, at most Qd focal-or-neighbor coordinates
in[0,1], and all remaining coordinates b=1-beta. Since beta<(Q-1)/Q,
b>1/Q. Its coordinate sum is k, and every coordinate is at least b, so
k>=nb. Moreover t=||w||^2<=nb^2+Qd. The exponential size bound from Part I
implies nb^2>Qd. Therefore
 rho=n/k^2<Q^2/n<1/2,
 ell/rho=k^2/(nt)>=nb^2/(nb^2+Qd)>1/2.
Let c=B rho. Then1/2<c<=1, B>=1, and N=Bn+1<=2Bn. Since ell<=rho, the
private witness denominator is at most1+B rho<=2. The selected private
funding P=Bn p satisfies
 P/sqrt(N)>=ell sqrt(Bn)/(2 sqrt(2))
  =(ell/rho)*sqrt(c*n*rho)/(2 sqrt(2))
  >(Q-1)/8,
using sqrt(n*rho)=n/k>Q-1. This proves no universal constant-times-sqrt(N)
funding bound. To impose N>=N0 simultaneously, increase Q until both this
coefficient exceeds C and N>=N0; N>=Q^d grows without limit. Alternatively,
Part B fixes Q and increases d.

For the explicit quantitative statement, d<=18Q^3 for every Q>=3 and
N<=n^2 (because B<=k^2/n and k<=n-1). Hence
 log N<=2d log Q<=36Q^3 log Q.
Also N>=n implies log N>=d log Q>Q, so log log N>log Q. Thus
 (log N/log log N)^(1/3)<=36^(1/3)Q.
Since Q-1>=2Q/3 and12*36^(1/3)<40,
 P>(1/40)sqrt(N)(log N/log log N)^(1/3).
All logarithms are natural. The claim is along this explicit sequence of
finite owner counts, not for every integer N. Subtracting the unit output
changes total funding to subsidy by1 and preserves the asymptotic order.

B. Fixed alphabet, increasing dimension.
For fixed Q let d run multiples of16Q(Q-1)(Q+2), with h=d/[2(Q+2)]. Every
Part I bound persists; h delta is now at least2 rather than exactly2.
Put b0=1-beta0. Then
 beta->beta0, k/n->b0, t/n->b0^2,
 rho~1/(b0^2 n), ell/rho->1, B rho->1, N~b0^2 n^2.
Therefore the SELECTED certificate values satisfy
 P/sqrt(N)->1/(2b0)>(Q-1)/2,
 u_full^2+Bn p^2 ->(1+b0^(-2))/4.
These give lower limits for the actual envelopes, without exchanging a
fixed-base limit with a growing-alphabet limit. Letting Q grow makes both
funding coefficients and squared-diagonal limits unbounded.

The full raw projection has total
 (B rho+B n/k)/(1+B rho),
whose ratio to sqrt(N) tends1/2. Hence the selected envelope/raw funding
ratio tends1/b0>Q-1. No universal aggregate factor2, or ANY fixed factor,
can bound this envelope by the raw full-profile projection. This closes
the sufficient route proposed earlier in RAW_PROJECTION_BASELINE.txt.
The elementary STATIC raw-projection bound there remains valid.

EVIDENCE AND PRIORITY.
The local combinatorial construction, finite rational transport existence,
all-Q scalar estimates and exact KKT are mathematical proofs. Checkers use
integer/Fraction arithmetic and small local exhaustive enumeration. They
do not enumerate the astronomically large final cover or transport network,
and this is not proof-assistant formalization. See the campaign review
ledger for independent native and cross-model findings and adjudication.
Known ingredients include projection optimality, KKT, quadratic gauge
identities, finite maxflow/mincut, fixed-cardinality convex decomposition,
and minimum-of-additive representations. Novelty of the combined envelope
obstruction remains unconfirmed; no human specialist review has occurred.
'''
text=header+qary+part2
(R/'proofs/FINAL_ENVELOPE_OBSTRUCTION.txt').write_text(text)
print('Wrote FINAL_ENVELOPE_OBSTRUCTION.txt:',len(text),'characters')
print('Frozen q-ary SHA256:',hashlib.sha256((R/'proofs/activation_qary_cube_proof.txt').read_bytes()).hexdigest())
