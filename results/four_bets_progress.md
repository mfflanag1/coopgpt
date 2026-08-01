# Four-bet research ledger

All statements below distinguish proved results, exact certificates, and open
steps.

## Bet 1: proper-coalition capacity versus slack

New theorem (proved): if a star-failure dual has one or two residual levels on
the bumped coalition \(S\), then \(d_v^*(S)\leq \phi(S)-v(S)\).

For the two-level case, normalize the maximizing face weights to \(1\) on
\(C\) and \(R>1\) on \(H=S\setminus C\). On the exact face
\(F_C=\{x:x(C)=v(C)\}\), put \(h=\phi(C)-v(C)\). Weighted maximality gives
\(-h+R(x(H)-\phi(H))\leq0\), hence
\[
x(S)-\phi(S)\leq-h+h/R\leq0.
\]
Thus \(F_C\) is the capacity certificate. Every two-player coalition is
covered automatically.

Exact frontier witness: results/pair_certificate_invariants.json. No singleton
inside \(S=\{1,3,4\}\) certifies, but the residuals are \((2,1,1)\), and
the theorem selects the full minimum-residual class \(C=\{3,4\}\). It is
exactly the observed same-stratum pair certificate.

New theorem (proved): write \(P=N\setminus S\), choose nonempty proper
\(C\subset S\), and put \(T=P\cup C\). If the slack of \(T\) at \(\phi\) is
no larger than the slack of \(C\), then \(F_C\) certifies the capacity bound.
Indeed, for \(x\in F_C\),
\[
x(S)+x(T)=x(N)+x(C),
\]
so core feasibility at \(T\) gives
\[
x(S)\leq v(N)+v(C)-v(T)
=\phi(S)+[\phi(T)-v(T)]-[\phi(C)-v(C)]\leq\phi(S).
\]
A \(\phi\)-tight off-side carrier is therefore an immediate sufficient
condition, but tightness is not necessary.

This resolves the canonical three-residual-level witness
`WITNESS_KEY_FALSE_n6`: for \(S=\{1,3,4,5\}\), the tight carrier
\(T=\{1,2,6\}\) selects \(C=\{1\}\) and gives the exact face bound
\(22<\phi(S)=71/3\). Its older union-of-cover candidate fails with bound
\(24>71/3\), so this is a genuinely different certificate.

Remaining case: a proper coalition with at least three members, a failure dual
with at least three distinct residual levels, and no off-side carrier whose
slack is dominated by that of its trace. This is now the only
capacity-versus-slack case needing a new face construction.

The new condition survived a targeted screen of all 141 saved hard
star-failure cases at \(n=6,7\), plus 744 fresh binding star failures from
random exact lower-envelope games at \(n=4,5,6\), with zero uncovered cases.
This is evidence, not a proof; see `results/off_side_carrier_screen.json`.
The corresponding sharp conjecture is now: exactness, binding at \(S\), and
failure of \((\star_S)\) force an off-side slack-dominating carrier. Proving it
would close the capacity-versus-slack implication without any restriction on
the number of residual levels.

New theorem (proved): the carrier conjecture holds for every exact game that is
the lower envelope of two common-sum additive allocations. If \(p(S)>\phi(S)\)
is the binding generator, star failure makes
\(C=\{i\in S:p_i>\phi_i\}\) nonempty and proper. Singleton feasibility yields
\(p(C)-q(C)\geq\phi(P)-p(P)\), hence
\(v(P\cup C)-v(C)\geq\phi(P)\), exactly the off-side slack inequality.
This explains why targeted deformations of the closest positive-slack witness
could reach carrier equality only when the relevant slack collapsed, but could
not cross it. The remaining capacity frontier therefore requires at least
three genuinely active lower-envelope generators (or equivalent richer core
geometry).

New exact boundary experiment: a third generator can cross the carrier
inequality, but the canonical crossing immediately restores the star condition.
Starting from the sharp equality fixture, transfer (a=1/10) from the off-side
player 5 equally to the five members of
(S=\{1,2,3,4,6\}). The resulting three generators are all genuinely active
(they are unique minimizers of (29,16,15) proper coalitions). The leximin
point remains ((1,4,3,5,7,4)), the minimum carrier comparison is now
(1/50>0), but an explicit core point raises (x(S)) from (17) to
(429/25), so \((\star_S)\) holds with opening (4/25). Thus the carrier
escape and star opening occur in the ratio (1:8) in this exact anchor. A
495-point simplex-grid screen of redistributions found no deformation retaining
star failure (float evidence only). See
`src/verify_three_generator_boundary_escape.py` and
`results/three_generator_boundary_escape.json`.

This changes the best proof target. Merely controlling which generator minimizes
the carrier cannot suffice once three generators are active. The useful local
statement would instead be a quantitative alternative: either some off-side
carrier has dominated slack, or every attempted carrier escape supplies a
core direction nonnegative on (S). Proving that alternative for
lower-envelope cores would establish the conjecture by contraposition.

That alternative now has a sharp formulation. Define

\[
\gamma_S=\min_{\varnothing\ne C\subsetneq S}
 \{\operatorname{slack}(P\cup C)-\operatorname{slack}(C)\},\qquad
\eta_S=\max\{x(S)-\phi(S):x\in\operatorname{core}(v),\ x_S\ge\phi_S\}.
\]

New lemma (proved): exactness at each carrier (P\cup C) supplies a core
point (z^C) with
(z^C(S)-\phi(S)\ge
\operatorname{slack}(P\cup C)-\operatorname{slack}(C)).
Thus the unresolved issue is purely coordinatewise: combine these total-gain
points without lowering any member of (S).

New theorem (proved, sharp): if (|S|=2), then
(\eta_S\ge\gamma_S), for every core point (phi), not only the leximin
point. Carrier-tight points for the two complementary cosingletons maximize
opposite player coordinates; their segment crosses the northeast orthant while
preserving total gain at least (gamma_S). Exact examples attain equality.

New general conjecture: (\eta_S\ge\gamma_S) at the leximin point of every
exact game. Six screens covering 3,650 exact lower-envelope games, 35,629
binding pairs, and 746 positive-(gamma) cases found no violation; each
screen's minimum ratio was recomputed exactly and equalled one. This remains
evidence, not proof. The coefficient-one claim is false under balancedness
alone: an exact rational five-player nonexact control has
(gamma_S=7/2), (eta_S=1/2) at its leximin point. See
`src/mine_carrier_star_ratio.py`,
`src/verify_quantitative_carrier_frontier.py`, and
`results/carrier_star_ratio_screen.json`.

New exact frontier reduction: a proof-producing primal--dual audit covers all
141 saved three-or-more-level star failures (106 at n=6 and 35 at n=7). In
141/141, some minimum-residual singleton certifies the capacity bound; in
141/141, some minimum-residual player also satisfies the simple singleton
carrier inequality
\(\operatorname{slack}(P\cup\{k\})\le
\operatorname{slack}(\{k\})\). Across 367 individual minimum-residual
candidates, 282 singleton faces certify and the carrier test explains 280,
with zero false-positive carrier certificates. The two unexplained
seven-player singleton certificates occur in cases where another
minimum-residual player does have a carrier certificate. An unconditional
singleton-carrier conjecture is nevertheless false: the exact two-level
witness in `results/symbolic_invariants_default_full.json` has no certifying
singleton and requires its minimum-residual pair.  This initially suggested a
dichotomy between the proved one-/two-level certificate and existential
singleton selection in the genuinely multilevel branch.  The whole-class
carrier audit below supersedes that target: it uses the complete
minimum-residual class (K) and removes singleton selection.  Exact audit files:
`results/min_residual_singleton_audit_n6_full.json` and
`results/min_residual_singleton_audit_n7_full.json`.
The saved corpus initially suggested a canonical selector: in all 141 cases,
a carrier-certifying player could be chosen to maximize
\(\phi_i-v(\{i\})\) within the minimum-residual class. The exact mutation
audit below falsifies this refinement, so it must not be used as a proof
target.

The direct residual-normal proof route has now been tested and ruled out in
full exact arithmetic. For a normalized minimum-residual singleton face,
maximality gives
\[
[x(S)-\phi(S)]+\sum_{i\in S\setminus\{k\}}(r_i-1)(x_i-\phi_i)\le0.
\]
Thus nonnegativity, not nonpositivity, of the weighted correction is a
sufficient condition for the face certificate; it is not equivalent to that
certificate. A proof-producing audit finds such a highest-gain player in
139/141 cases, but two exact seven-player cases fail. In
`WITNESS_KEY_CX_n7_s303_1491`, the correction is identically \(-3/2\) on
both highest-gain singleton faces even though both faces and their carrier
comparisons certify. Therefore the residual normal alone cannot close the
multilevel branch; the remaining proof must exploit the off-side carrier
slack comparison or another exactness-specific exchange. See
`results/min_residual_singleton_audit_n6_weighted.json` and
`results/min_residual_singleton_audit_n7_weighted.json`.
The related common-face shortcut is also nonuniversal: the selected carrier
faces have a common core point in 118/141 cases (and all minimum-residual
carrier faces do so in only 61/141). See
`results/joint_highest_gain_carrier_audit.json`.

The adversarial mutation audit is more informative. It generated 534 further
exactly certified multilevel records (505 distinct game--coalition pairs) by
mutating common-sum lower-envelope generators around mixed hard cases. Some
minimum-residual carrier exists in 534/534 records; across 1,602
minimum-residual candidates, 1,334 are carriers,
and every candidate is a carrier in only 266 cases. In contrast, some
highest-gain carrier exists in 520/534 cases, and even a highest-gain
singleton face certifies in only 533/534. Tight-hypergraph centrality and
cover-weighted adjacency carrier selectors succeed in only 517 and 520 cases,
respectively.

The sharp counterexample is the exact lower envelope of
\[
\begin{aligned}
p&=(-6,4,18,-4,11,-10),&q&=(-1,4,24,-4,0,-10),\\
a&=(-1,-2,19,-4,6,-5),&b&=(-6,0,20,0,9,-10),
\end{aligned}
\]
with \(S=\{1,2,3,4,6\}\). Here
\(\phi=(-3,0,20,-2,6,-8)\), the minimum-residual class is
\(K=\{1,2,3\}\), and its gains are \((3,2,2)\). The unique highest-gain
player 1 has carrier slack 4 and gain 3, and its singleton-face maximum is
8 while \(\phi(S)=7\); it fails even the full face certificate. Players 2
and 3 have carrier slack equal to gain 2 and certify. Thus the viable theorem
target is genuinely existential: prove that *some* minimum-residual player is
a carrier, without a gain ranking. Adding independent fresh three-, four-,
and five-generator screens and deduplicating all corpora gives 669 distinct
exact multilevel game--coalition pairs (702 certified records), with zero
violation. See
`src/hunt_seeded_selector_mutations.py`,
`src/audit_mutation_minimum_residual.py`, and
`results/mutation_minimum_residual_audit.json`. The deduplicated combined audit
is `results/combined_minimum_residual_carrier_audit.json`.

New proved reduction: for every \(k\in S\),
\[
\operatorname{slack}_\phi(P\cup\{k\})
-\operatorname{slack}_\phi(\{k\})
=\phi(P)-[v(P\cup\{k\})-v(\{k\})].
\]
Thus the carrier condition is exactly the game-marginal inequality
\[
v(P\cup\{k\})-v(\{k\})\ge\phi(P).
\]
This removes the two apparently unrelated slack terms. More importantly, if
this inequality failed for every \(k\) in the minimum-residual class \(K\),
exactness would put every point of every face \(F_{P\cup\{k\}}\) strictly
above \(\phi(S)\). Failure of \((\star_S)\) would then force a nonzero
nonnegative normal strictly separating the convex hull of those faces from
the upper orthant at \(\phi_S\). This avoids any false canonical selector.

New theorem (proved): the carrier-face separator has an exact finite LP-dual
form.  Writing \(T_k=P\cup\{k\}\), a common separator \(w\geq0\) exists if
and only if, for every failed candidate \(k\), there are
\(\theta_U^k\geq0\), \(a_k\), and \(b_k>0\) with
\[
w^S=a_k\mathbf1+b_k\mathbf1_{T_k}-\sum_U\theta_U^k\mathbf1_U,
\qquad
\sum_U\theta_U^k\operatorname{slack}_\phi(U)
 <b_k\operatorname{slack}_\phi(T_k).
\]
This expresses the separator as a finite rational system involving only
coalition incidence vectors and slacks.

Dividing the separator identity for each $k\in K$ by its necessarily positive
face multiplier $b_k$ and summing gives a still smaller obstruction.  There
must be $c>0$, $A\in\mathbb R$, $w\geq0$, and one nonnegative coalition
collection $\eta$ with
\[
\mathbf1_K=cw^S-A\mathbf1-|K|\mathbf1_P+
\sum_U\eta_U\mathbf1_U,
\qquad
\sum_U\eta_U\operatorname{slack}_\phi(U)
 <\sum_{k\in K}\operatorname{slack}_\phi(P\cup\{k\}).
\]
This aggregated separator identity is a useful compressed form, but the new
residual-gap theorem below shows that it cannot be eliminated against the
star-failure cover merely by treating the two normals as independent.

The new exact solver `src/analyze_carrier_face_separator_dual.py` constructs
these certificates directly.  On the 80 saved multilevel cases having at
least one failed minimum-residual candidate, the failed candidates alone have
a strict common separator in 80/80 cases, with minimum normalized margin
\(1/3\); 79 optima are coordinate unit vectors and one uses two coordinates.
Adding the carrier candidates collapses the strict margin in only 7/80 cases,
so the easy equivalence ``carrier exists iff the common separator disappears''
is false.  See
`results/carrier_separator_boundary_audit.json`.

New theorem (proved): the star-failure cover itself supplies the common
separator.  Let
\[
 r_0=\min_{i\in S}r_i,\qquad K=\{i:r_i=r_0\},\qquad
 H=S\setminus K,\qquad D=\sum_{i\in H}(r_i-r_0).
\]
For every core displacement \(d=x-\phi\), tightness of the cover gives
\[
 r_0d(S)+\sum_{i\in H}(r_i-r_0)d_i\le0.
\]
If a candidate \(k\in K\) fails its carrier inequality by \(\gamma_k>0\),
then every \(x\in F_{P\cup\{k\}}\) has \(d(S)\ge\gamma_k\).  Consequently
\[
 \sum_{i\in H}\frac{r_i-r_0}{D}(x_i-\phi_i)
 \le-\frac{r_0}{D}\gamma_k<0.
\]
Thus the normalized residual gap is automatically a strict common separator,
supported entirely on the higher-residual class.  The earlier proposed goal
of excluding coexistence of the two normals was therefore impossible: their
coexistence is forced algebraically.  The corrected proof target is primal.
The exact residual-gap escape criterion is: if some (k\in K) has

\[
\max_{x\in F_{P\cup\{k\}}}
\sum_{i\in H}\frac{r_i-r_0}{D}(x_i-\phi_i)\ge0,
\]

then (k) must satisfy the carrier inequality, by contraposition of the
displayed separator bound.

The stronger coordinatewise-mixture route is false.  In the exact instance
`WITNESS_KEY_CX_n6_s201_10919`, an exact homogenized face-mixture LP gives
optimal common higher-residual displacement (-1/20), even though two
minimum-residual players are carriers (both carrier margins are (-3/4)).
The next natural target is therefore scalar: force escape from the
normalized residual-gap separator on at least one carrier-tight face, not
coordinatewise neutralization of every higher-residual coordinate.  See
`results/carrier_face_mixture_neutralization_counterexample.json` and
`src/audit_carrier_face_mixture_neutralization.py`.

The scalar target survives the complete saved hard corpus in exact arithmetic:
all 141 records have an escape face.  Of 367 minimum-residual faces, 277 escape
and 280 satisfy the carrier inequality.  Every one of the 87 failed carriers
has strictly negative residual-gap maximum (the least-negative value is
(-1/28)); three valid carriers do not escape, but another candidate escapes in
each of those records.

It nevertheless fails the adversarial mutation test.  After deduplication,
only 123/505 exact mutation cases have an escape face, although 505/505 have a
minimum-residual carrier.  The first exact counterexample is trial 0 of
`seeded_face_selector_mutations_t1`: (K={1,2,3}), the normalized gap has
weights (2/3,1/3) on players 5 and 6, carrier margins are (-2,0,1), and the
corresponding face maxima are (-1/3,-1/3,-4/3).  Thus fixed-cover escape is a
useful sufficient certificate, not the missing universal theorem.  A
residual-based proof must select the failure cover jointly with the carrier,
or else use a cover-independent exactness exchange.  See
`results/residual_gap_escape_face_audit.json`,
`results/residual_gap_escape_face_mutation_audit.json`, and
`src/audit_residual_gap_escape_face.py`.

New breakthrough target: use the *whole* minimum-residual class (K) of a
suitably chosen failure cover, not a selected singleton.  The exact
class-carrier inequality is

\[
\operatorname{slack}_\phi(P\cup K)
\le \operatorname{slack}_\phi(K),
\qquad\text{equivalently}\qquad
v(P\cup K)-v(K)\ge\phi(P).
\]

This immediately gives the required capacity face by the proved off-side
slack-domination proposition with (C=K).  It bypasses every failed singleton
selector and every failed residual-gap escape route.  A deduplicated exact
audit covers all 702 stored multilevel records, representing 669 distinct
game--coalition pairs: 669/669 satisfy the class-carrier inequality, 644
strictly and 25 at equality, with exact margins from (-28) to (0).  This
includes all 505 adversarial mutation pairs.  The sharp current theorem target
is therefore to prove that the multilevel failure dual admits a cover whose
minimum-residual class satisfies this carrier inequality.  See
`results/minimum_residual_class_carrier_audit.json` and
`src/audit_minimum_residual_class_carrier.py`.

A targeted counterexample hunt then screened 3,000 new six-player,
four-generator exact lower-envelope games in nearby, composition, and signed
modes.  It found 1,123 star failures and 25 genuinely multilevel failures, with
no positive class-carrier margin.  The closest float boundary had margin zero
and exactified to zero.  This is discovery evidence, not an exactification of
all 25 cases.  Artifacts:
`results/class_carrier_hunt_n6_nearby_1000.json`,
`results/class_carrier_hunt_n6_composition_1000.json`, and
`results/class_carrier_hunt_n6_signed_1000.json`.

The proof program is now an induction over residual levels.  Write the failure
cover levels as (r_0<r_1<\cdots<r_m) and let
(C_j=\{i\in S:r_i\le r_j\}), beginning with (C_0=K).  If the class-carrier
inequality failed, exactness at (P\cup K) would give a core point with
strictly larger (S)-sum, while the cover identity forces its weighted loss
onto higher residual layers.  Exactness supplies nonempty faces for every
nested prefix (C_j).  The remaining lemma is to combine those prefix-face
points so that the highest residual loss is removed one level at a time; the
result would dominate (phi) on (S), contradicting star failure.  This
nested-class exchange is cover-independent at the coalition level and is now
the most direct route to a proof.

The exact support-restricted separator audit has
80/80 strict certificates on \(S\setminus K\) (minimum margin \(1/3\)) and
0/80 on the known carrier candidates.  Artifacts:
`results/carrier_separator_residual_gap_audit.json` and
`src/audit_carrier_separator_residual_gap.py`.

## Bet 2: grand-coalition resource monotonicity

Settled negatively by an exact five-player game. Let
\[
p=(0,0,7,0,7),\qquad q=(2,10,0,2,0),
\]
and set \(v(T)=\min\{p(T),q(T)\}\) for proper \(T\), \(v(N)=14\). The
game is exact because both points lie in the core and one is tight at every
proper coalition. For \(0\leq\epsilon\leq3/2\),
\[
\phi(v^{2+\epsilon})=
(3+\epsilon/3,\,4-\epsilon/3,\,3+\epsilon/3,\,
 3+\epsilon/3,\,3+\epsilon/3).
\]
Player 2 loses payoff while only \(v(N)\) rises. The entire path remains exact.
Exact symbolic verifier: src/verify_grand_resource_counterexample.py.

The failure mechanism is a higher-stratum donor pinned by two pair constraints
while four lowest-stratum players are raised together.

## Bet 3: three-game exact families

New theorem (proved): a singleton bump arm is transparent. Given any base core
allocation \(x\), an endpoint core allocation maximizing the bumped singleton
coordinate dominates \(x\) on that coordinate. This needs only balancedness.

Together with the existing overlapping-arm theorem, every base-plus-two-bump
family is feasible unless the two bumped coalitions are disjoint and both have
size at least two. Consequently all such families on at most three players are
settled by these local lemmas. The first remaining local shape is a two-pair
partition at \(n=4\), but the paper's global four-player selection theorem
settles it. The genuinely open two-arm frontier begins at \(n=5\), where a
nonempty remainder is also possible.

Remaining theorem target: disjoint \(A,B\) with \(|A|,|B|\geq2\). The
existing exactness-chaining proposition already kills the partition-value
obstruction when \(N\setminus(A\cup B)\neq\varnothing\), but not every
Farkas support. The current sharper route is to classify only extreme Farkas
rays simultaneously sensitive to both changed worth rows. See
results/family_farkas_notes.md.

New exact reduction: after eliminating efficiency multipliers, the Farkas cone
is the nonnegative kernel of a rank-\(3(n-1)\) matrix \(D\), and its extreme
rays are the support-minimal positive circuits of \(D\). Thus absence of a
positive circuit containing both bump columns would prove feasibility, but a
new sparse-support search shows that this sufficient condition is false:
disjoint both-sensitive unit circuits already exist at \(n=5\). The earlier
600,000-basis nonfinding was a sampling failure, not structural evidence.

Two further exact eliminations show that any such circuit must use a
monotonicity column on each arm and cannot contain a complementary pair of
core columns in one game block. A sparse-support MILP with these cuts recovers
the overlapping unit circuit and rules out every solver-visible support of
admissible circuit size for the already-settled \(n=4\) disjoint shape. The
search finds a ten-row unit circuit for the disjoint partition
\(A=\{1,2,3\},B=\{4,5\}\). Its inequality is violable by balanced endpoints;
an exact rational example has Farkas right-hand side \(-1\), with the base
exact but both arms nonexact. However, a separate exact dual built from one
coalition-tight core witness for every coalition proves that this same circuit
has nonnegative right-hand side for every exact endpoint triple. The sharp
next theorem is therefore circuit-by-circuit neutralization by exactness.

Symmetry reduction now sharpens the minimum-support frontier. The dangerous
circuit above has a six-support orbit under $S_3\times S_2$, and its exactness
dual transports to all six supports. Orbit blocking finds one second type,
with a twelve-support orbit; two explicit balanced collections of total
weights $5/2$ and $3/2$ already neutralize that type. Once both orbits are
blocked, the sparse MILP advances from support size 10 to 11. The remaining
classification problem therefore begins with larger circuits, subject to the
caveat that this minimum-support exhaustion is a floating-point diagnostic.
The first support-eleven type has a twelve-support orbit and is again
neutralized by balancedness, through collections of total weights
$1/2,2,3/2$ in the three games. Hence only the six Type-I supports among the
first three symmetry types require endpoint exactness.

The floating-point frontier has now been replaced completely by an exact
Boolean--linear-rational enumeration. The rank is 12, so every circuit has
support at most 13. Hadamard's determinant bound gives a rigorous normalized
coefficient floor of

\[
1/(13\cdot12^6)=1/38{,}817{,}792,
\]

which makes the Boolean support model exhaustive rather than epsilon-
diagnostic. For the partition shape \((3,2,0)\), terminal UNSAT after orbit
blocking leaves exactly 420 both-sensitive orbits (4,914 transported
supports): 2, 24, 83, and 311 orbits at support 10, 11, 12, and 13. Exact
balanced-collection identities neutralize 411 orbits (4,812 supports), eight
more (96 supports) are implied by balancedness together with
\(d_A,d_B\geq0\), and the six-support Type-I orbit is neutralized by endpoint
exactness.

For the remainder shape \((2,2,1)\), terminal UNSAT leaves 189 orbits (756
supports): 9, 27, and 153 at support 11, 12, and 13. Balancedness alone
neutralizes 117 orbits (468 supports), and balancedness plus bump
nonnegativity neutralizes the remaining 72 (288 supports). There is no
counterexample orbit.

This closes Bet 3 at the minimal open player count: together with the
overlapping-arm and singleton-arm lemmas and the known four-player selection
theorem, every base-plus-two-bump exact family on at most five players is
feasible. The next structural target is no longer another \(n=5\) batch. It
is to extract a dimension-free neutralization theorem from the two exact
certificate mechanisms, or to enumerate the first genuinely new shapes at
\(n=6\).

The first \(n=6\) probe now sharpens that target. For the symmetric
\((2,2,2)\) shape, a dynamic exact-subcircuit-cut MILP exposed five distinct
support-11 unit-circuit orbits. Four admit balanced recolorings. The fifth is
the first verified failure of recoloring beyond Type I, but it is again
neutralized by endpoint exactness: an exact rational dual using three tight
endpoint witnesses proves circuit-supported worth
\(+d_B/3\leq4b(N)\). Thus the promising dimension-free alternative is now:
every circuit either recolors, or the dual obstruction to recoloring produces
a sparse exactness certificate. See `results/disjoint_n6_222_breakthrough.md`.

The resumable probe now covers 25 distinct exact support-11 orbits (200
transported supports) in the \((2,2,2)\) shape. Twenty-four have exact
recoloring capacity one; the unique observed exception remains the
\(\rho=2/3\) orbit neutralized above. This layer is not yet exhaustive, but
the exception has remained isolated across two additional seeded batches.

The next six-player shape, the symmetric partition \((3,3,0)\), produces a
richer but still favorable frontier. Two seeded batches give 20 distinct exact
unit-circuit orbits (441 transported supports): 11 have recoloring capacity
one, while five have capacity \(1/2\), one has \(2/3\), and three have
\(3/4\). All nine subunit-capacity orbits have exact endpoint optimum zero and
coefficientwise rational two-level duals; no exact family counterexample
appears. Several exceptions compress to only three or four blocks. See
`results/disjoint_n6_330_breakthrough.md`.

The initial asymmetric-remainder \((3,2,1)\) batch adds seven exact circuit
orbits (78 transported supports): six recolor, while one has capacity
\(2/3\), exactly saturating the universal mixture lower bound. Its exact
endpoint optimum is again zero, with a seven-block rational two-level dual.
Thus all 52 six-player orbits exposed across the three shapes are
neutralized; none yields an exact-family counterexample. See
`results/disjoint_n6_321_frontier.md`.

The remaining disjoint shape \((4,2,0)\) adds ten support-10 exact circuit
orbits (408 transported supports). Six recolor fully; three have capacity
\(1/2\), and one has capacity \(3/4\). All four deficient circuits have exact
endpoint optimum zero and rational two-level duals. The representative
six-player frontier therefore covers all four disjoint shapes, 62 exact
circuit orbits, and 1,127 transported supports, all neutralized. These probes
are deliberately nonexhaustive; they support a structural theorem rather than
an \(n=6\) census. See `results/disjoint_n6_420_frontier.md`.

New general theorem (proved): for any fixed both-sensitive circuit, validity
on all exact endpoint triples is equivalent to a decomposition of its circuit
inequality into finitely many two-level exactness inequalities
\(\alpha\mathbf1+\delta\mathbf1_U\), plus nonnegative bump terms. This is
the exact LP-dual characterization, not merely a sufficient template.
Balanced recoloring is its \(\delta=0\) subcase. Automatic compression shows
that the new six-player obstruction uses only three blocks (two balanced, one
genuine two-level block). A potential-guided reoptimization improves the
five-player Type-I exception from an eight-block machine dual to a two-block
hand proof at a common singleton witness: one \(t_A\) block has coverage
\(\mathbf1+\mathbf1_{\{1\}}\), and one \(t_B\) block has coverage
\(3\mathbf1-\mathbf1_{\{1\}}\); their singleton worths cancel. The
remaining breakthrough is therefore an existence theorem for
such decompositions across all circuits, ideally constructed directly from
the recoloring-capacity dual potentials.

Exact source ablation has now isolated the conjectural construction. Across
the five-player Type-I orbit, all 15 deficient six-player representatives,
and 15 deficient circuits across all six seven-player geometries,
the nontrivial weak/strict superlevel sets of the two bumped-game capacity-dual
potentials \(u_1,u_2\) alone suffice for a rational two-level certificate
(31/31). More sharply, every case has a certificate using one common threshold
coalition \(U\) and at most one block per game: 28 use two blocks and three use
three. Pairwise-difference thresholds also give 31/31, whereas circuit support
alone gives only 9/31 and support plus complements only 16/31. The target is
therefore a single-threshold/uncrossing theorem, not a finite support identity.
See `results/potential_guided_uncrossing_program.md`.

The candidate set has since collapsed to two coalitions. If
\(P_g=\operatorname{argmax}u_g\), then \(P_1\) succeeds in 24/31 cases and
\(P_2\) in 16/31, and at least one succeeds in every case. Indeed the direct
single-witness capacities obey \(\max\{\sigma_{P_1},\sigma_{P_2}\}=1\)
throughout the corpus. The best theorem
target is now the two-top-set alternative: failure of the fixed-witness system
at both \(P_1\) and \(P_2\) should contradict optimality of the capacity dual.

The latest exact restriction audit strengthens this once more: all 31 cases
admit a successful top-set repair with \(\mu_0=0\) and
\(\delta_1+\delta_2=0\). Equivalently, the certificate is determined by one
subcollection \(0\leq w\leq q\) whose degree vector has only two levels,
\(\alpha\mathbf1+\delta\mathbf1_U\); the other color is \(q-w\). The remaining
existence theorem is therefore a two-dimensional section of a weighted degree
zonotope, with two distinguished-coordinate bounds.

The base color is also redundant in the ordinary capacity problem: absorb any
fraction of its balanced mass into the first bumped color and the remainder
into the second. The reduced dual has one zero-sum potential \(z\), so the
canonical candidates are its maximum and minimum coordinate classes
\(P^+,P^-\). Exact reoptimization gives 29/31 successes for each extreme and
31/31 for their union, always with
\(\max\{\tau_{P^+},\tau_{P^-}\}=1\). This replaces the earlier
gauge-dependent two-potential conjecture by an intrinsic one-potential
separation theorem target.
The 62 individual extreme capacities obey the exact dichotomy
\(\tau_{P^\pm}\in\{\rho,1\}\): four failures remain at \(\rho\), and all
others jump to full repair. This optimal-face dichotomy is the strongest
current clue for a proof.
The four failures have now been characterized exactly by the support
nullspace: a zero-sum player direction vanishes on every coalition carrying
aggregate weight but not on the failed extreme set, so the fixed-witness dual
equation can be imposed without changing the objective. No tested circuit has
both extremes flexible, and every support-rigid extreme reaches one. This
splits the remaining theorem into a support-span lemma and a rigid-extreme
capacity lemma.
Orthogonal projection onto the support-nullspace complement removes that
gauge freedom without changing the dual objective. After this canonical
projection, both extremes repair in all 31 cases, so all 62 individual
capacities equal one. The preferred theorem target is now stronger: prove
both extremes of a support-orthogonal optimal potential are rigid and reach
full capacity.
An exact rank audit across 717 circuits strengthens the first half: all 609
exhaustive five-player circuits and all 108 representative or glued
six-/seven-player circuits have support nullspace generated solely by swaps of players with
identical support incidence. Fourteen nullspaces are nontrivial, all of
dimension one, and none contains a non-twin direction. Consequently every
level set of the support-orthogonal potential is rigid throughout the corpus.

New structural lemma (proved): fixed-witness capacity has the arm ceilings
\(\tau_U\le q_A/\lambda_{1,A}\) for \(U\ne A\), and symmetrically for
\(B\). Thus an exclusive arm \(q_A=\lambda_{1,A}\) pins every successful
distinct witness at capacity exactly one. In the original 696-circuit audit,
all 31 deficient circuits had an exclusive arm. Both
support-orthogonal extreme sets differed from an exclusive arm in all 31
cases, so the 62 exact repairs were explained as sharp equalities. The
factorized local-circuit search below expands the audit to 717 circuits and
adds 21 deficient nonexclusive examples. Thus deficiency does not force
an exclusive arm; the surviving dimension-free target is the
support-rigid extreme-set repair theorem.

New structural lemma (proved): if a support-minimal global circuit uses
exactly one monotonicity column on each arm, then each of its three incident
game-block supports is itself a nullity-one local circuit. Core columns in
each block must be independent, since a core-only kernel would be a second
global kernel direction. The two leaf dependencies are therefore unique;
scaling them to match an arbitrary root-kernel vector gives a linear
isomorphism between the root kernel and the global kernel. All 717 audited
circuits satisfy the one-row hypothesis. This puts the revised Bet 3 problem
in a three-local-ray normal form.

The old census suggested a four-mass proof. Put
\(x=\lambda_{1,A}\), \(y=\lambda_{2,B}\),
\(U=q_A-x\), and \(V=q_B-y\). Scalar recoloring reaches one exactly when
\(UV\ge xy\). Among the 97 nonexclusive circuits, 73 lie on the product
boundary and 24 have strict positive gap. Seeded one-/two-column circuit
mutations over 60,000 six-player bases recovered 317 exact circuit records
without a forbidden product gap. This initially pointed to a two-sided
circuit-cofactor/exchange
inequality; see `results/arm_ratio_exchange_program.md`.

The targeted local-block construction falsifies both that product law and
its apparent linear strengthening. At \(n=6\), with
\(A=\{1,2,3\}\) and \(B=\{4,5\}\), three nullity-one local positive
circuits glue along one monotonicity column per arm to give a 13-column,
rank-12 global circuit with
\[
(x,y,U,V)=(1,2,1,1).
\]
Thus \(U-y=-1\) and \(UV-xy=-1\). The scalar lower bound is only \(6/7\).
Nevertheless the non-scalar subcollection supported on masks
\(\{7,24,37,58\}\), each with weight one, has constant degree two; its
complement has constant degree four and retains the second distinguished
coefficient. Exact primal--dual reoptimization gives capacity one, while
fixed witnesses 16 and 14 give \(4/3\) and \(9/7\). The ratio conjecture is
therefore dead. See the exact construction and verifier in
results/forbidden_ratio_glued_circuit_n6.json.

The direct nonexclusive-recoloring target is also false. Exact enumeration of
56 root local circuits, 626 first-leaf circuits, and three coefficient-
violating second-leaf circuits produces 59,304 distinct product-forbidden
global gluings. Capacities were exactly recomputed for the 5,000 smallest
scalar bounds plus every arm-ratio class (5,035 circuits). Twenty-one are
deficient and nonexclusive, with ordinary capacities \(3/4\), \(5/6\),
\(7/8\), or \(11/12\). The strongest case has
\((x,y,U,V)=(2,2,1,1)\) and ordinary dual potential
\[
z=\tfrac14(1,-1,-1,-1,2,0).
\]
Its maximum and minimum sets, masks 16 and 14, have fixed-witness capacities
\(5/4\) and \(3/2\). Both extremes repair all 21 deficient gluings, with
fixed capacities between \(11/10\) and \(3/2\). This is the strongest evidence
yet for the two-extreme-set exactness theorem: it survives precisely where
ordinary balanced recoloring fails. See
results/glued_local_circuit_hunt_n6_321.json.

The support side is stronger still. An exact rank audit over all 59,304
product-forbidden gluings finds 57,425 distinct aggregate supports, every one
of full player rank. Thus this entire adversarial family has no
support-nullspace gauge freedom: both canonical extreme sets are rigid before
any fixed-witness capacity is solved. See
`results/glued_product_forbidden_support_structure_n6_321.json`.

The capacity side is now exhaustive for this factorized pattern as well.
Fixing mask 16, the singleton consisting of the unselected member of the
two-player arm \(B\), and exactly reoptimizing all 59,304 product-forbidden
gluings gives
\[
\tau_{16}\ge\frac98.
\]
All capacities are strictly above one; 45 attain \(9/8\). The complete
spectrum has 21 values and the returned exact optima use only 19 projective
dual rays and 18 potential weak-order types. The solver selects two rays on
the minimum frontier. Exact enumeration of the full dual arrangement gives
87 feasible projective rays (57 symmetry orbits); 21 rays can be optimal,
and four attain \(9/8\) in three symmetry orbits. All 5,159,448 exact
ray--circuit evaluations satisfy the bound, and minimizing over the
arrangement reproduces the full LP histogram exactly. The local circuit
enumeration no longer has a floating rank or
sign gate: rank over \(\mathbb Q\) is computed modulo 61, justified by the
Hadamard bound \(5^{5/2}<56\), and primitive kernels are recovered from
signed integer cofactors. This proves the \(9/8\) bound for the stated
three-local-ray gluing pattern. It does not yet prove the dimension-free
support-rigid extreme-set conjecture. See
`results/glued_product_forbidden_fixed16_audit_n6_321.json` and
`results/fixed16_glued_theorem_program.md`. The independent arrangement
certificate is `results/glued_fixed16_dual_arrangement_n6_321.json`.

The global exhaustion has now been compressed to a root--leaf theorem.
For every arrangement ray, its cross-multiplied \(9/8\) margin is exactly a
root contribution plus the two matched root weights times independently
minimizable leaf rates.  Checking 626 first leaves, three second leaves, and
56 roots for each of the 87 rays takes 59,595 exact local comparisons and
leaves no negative margin.  The only four zero rows are the known sharp rays
in three symmetry orbits.  Since the local coalition universe equals the
arrangement universe, the proof covers all 105,168 raw local gluing triples,
strictly more than the 59,304 product-forbidden distinct circuits.  This is
the first genuine proof compression of the glued frontier; the next step is
to replace its 51 numerical local types by a few symbolic incidence
inequalities.  Exact certificate:
`results/glued_fixed16_local_factorization_n6_321.json`.

The factorization identity has a dimension-free form for an arbitrary target
capacity \(c\): the global gap is the root objective plus the matched edge
weights times two normalized leaf gaps.  This is a genuine local-to-global
lemma, not a census statement.  In the fixed witness geometry the entire
second-leaf family also collapses symbolically: its three collections differ
only by adding or deleting the witness player from masks 35, 37, and 38, and
\(\gamma(U)=0\) makes those hinge values equal.  Hence the remaining
dimension-free burden is now localized to a first-leaf lower bound and its
absorption by the root relation.

A positive-part inequality compresses that burden much further.  The first
leaf depends only on normalized arm masses \(u=q_A/m_A\), \(v=q_B/m_A\);
its coarse rate is minimized at \(v=0\) and decreases with \(u\).  The exact
local cone has \(u\le3\) and contains \((3,0)\), giving the closed lower
bound \(8[-\gamma_1+3r_A]_+-27r_A\).  The roots have only 12 mass types.
Those degree-only bounds prove 86 of 87 arrangement rays; the remaining
sharp ray needs exact incidence at only three roots, with margins \(10,2,2\).
The finite proof is therefore down to 1,047 root comparisons plus transparent
convexity, from 5.16 million global comparisons.  Exact artifact:
`results/glued_fixed16_analytic_compression_n6_321.json`.

The proposed dimension-free circuit coefficient lemma
\(q_A\le |A|m_A\) is now disproved.  Exhaustion through six players had found
no violation, but Peleg's second construction produces 186 exact
seven-player violations from the certified six-player sources.  A sharp
minimal balanced collection has primitive weights
\[
(1,4,1,1,2,2,3)
\]
on \(\{7\},\{1,7\},\{1,2,3\},\{2,4\},\{3,4,5\},\{3,4,6\},
\{2,5,6\}\), respectively.  Its incidence rank is seven and
\(q_{\{1,7\}}/m_{\{7\}}=4>2\).  Peleg's first construction lifts this to an
eight-player three-member arm with the same ratio four, disproving the exact
cardinality-three bound used as the proposed dimension-free replacement for
the 626-leaf enumeration.  Exact artifacts:
`results/peleg_coefficient_ceiling_escape_n7.json` and
`src/hunt_peleg_coefficient_ceiling_escape.py`.

The preliminary ratio-four family landed exactly on the global \(9/8\)
frontier, but the source screen was incomplete.  A full implementation of all
four Peleg cases starts from the exactly enumerated 1,292 five-player minimal
balanced collections and reproduces the published total of 200,214
six-player collections; 172,776 arise from the missing two-parent fourth
case.  Extending the complete source family gives 1,320 seven-player leaves
with a three-player arm ratio five, in four distinguished-arm symmetry
orbits.  One has primitive weights
\[
(2,2,4,1,1,1,5)
\]
on \(\{1,2\},\{1,3\},\{2,3,4\},\{1,4,5\},\{1,4,6\},
\{7\},\{5,6,7\}\), respectively, and incidence rank seven.

This gives a genuine negative breakthrough for the stronger constant.  All
168 gluings of one ratio-five leaf with the lifted 56 roots and three second
leaves are exact nullity-one circuits; 21 have fixed-\(\{3\}\) capacity below
\(9/8\), with exact minimum \(13/12\).  Repeating the audit on one canonical
representative of each of the four leaf orbits checks 672 circuits: every
orbit breaks \(9/8\), none breaks one, and the minimum remains \(13/12\).
Thus the fixed six-player \(9/8\) theorem is sharp only for its stated
pattern; it has no dimension-free extension.  The surviving Bet 3 target is
the original unit-repair threshold.  Exact artifacts:
`results/full_n5_peleg_escape_n7.json`,
`results/ratio5_bad_leaf_gluing_n7.json`, and
`results/ratio5_leaf_orbit_gluings_n7.json`.

New positive breakthrough: capacity one is now proved uniformly over the
first leaf for the entire certified root--second-leaf pattern.  If a
subcollection \(z\le q^0+q^2\) satisfies
\[
\deg(z)=\beta\mathbf1+m_Ae_a+\delta\mathbf1_U,
\qquad z_B\le q^0_B,
\]
then \(w=q^1+z\) repairs every compatible first leaf, irrespective of its
arm coefficient.  Exact absorbers exist for all 168 root--second pairs.  A
separate exact dual audit gives the uniform reserve
\[
R\ge\frac13(m_Ar_A+m_Br_B),
\]
and hence
\[
\tau_U\ge1+\frac1{3\max\{q^1_A/m_A,2\}}.
\]
For ratio five this gives \(16/15\), explaining the four-orbit survival
without inspecting any first-leaf support.  This removes the adversarial
Peleg leaf entirely from the remaining proof burden: only the structural
classification of root--second absorber feasibility remains.  Exact
artifacts: `results/unit_root_absorption_n7.json` and
`results/unit_root_absorption_program.md`.

The minimal-balanced encoding also supports an adversarial root lift.  All
four Peleg constructions from the 56 certified regularized roots yield 604
distinct seven-player roots retaining the two cosingletons and root \(B\).
Although 275 fail root-only absorption, every one of their three second-leaf
pairings succeeds: 1,812 exact absorber LPs, zero failures.  This converts the
next Bet 3 step into a concrete closure theorem: prove that Peleg extension
preserves absorber feasibility.  The normalized dual reserve also remains
exactly \(1/3\) in every Peleg case.  Exact artifact:
`results/root_absorption_descendants_n7.json`.

Peleg case 1 is now proved closed.  The marking indicator on a regularized
root is represented by a player potential \(v\); balanced weight one, the two
marked cosingletons, and unmarked \(B=\{b,u\}\) force
\(v(N)=1\) and \(v_a=v_b=v_u=0\).  This directly lifts all 93 markings of
root-only absorbers.  The other 66 markings have only five interpolation-
potential types, each nonnegative on the full second-leaf support, so
positive-part subadditivity transports the parent's \(1/3\) dual reserve.
Thus all 159 admissible case-1 markings preserve unit absorption.  Exact
artifact: `results/peleg_case1_absorption_closure.json`.

Peleg case 2 is now also proved closed.  With new-singleton coefficient
\(\kappa\), correct the marking potential by
\(\widetilde v=v+\kappa(e_a+e_b-e_u)\).  This restores the parent equations
\(\widetilde v(N)=1\) and
\(\widetilde v_a=\widetilde v_b=\widetilde v_u=0\).  The correction has total
root mass one and total second-leaf mass \(\alpha_2\), so the new root and
second singletons pay the two positive-part error terms exactly.  Both needed
sign conditions hold in all 113 case-2 emissions, with zero failures.  Exact
artifact: `results/peleg_case23_absorption_closure.json`.  The remaining
one-parent obstruction was case 3, whose 104 descendants split a distinguished
cosingleton or \(B\); none has an alternate case-1/2 representation.

Peleg case 3 is now closed on the certified family.  Its emissions divide
into 21 \(\bar a\)-splits, 62 \(\bar b\)-splits, and 21 \(B\)-splits.  A
split interpolation potential with value
\(\theta=\kappa/\lambda_D\) on the split column transports that column by
convexity.  In the \(\bar a\) role, the coefficient defect collapses to the
nonnegative hinge
\((m_A-\kappa)([g(\bar a)]_+-g(\bar a))\), and all 21 potentials are
nonnegative on the full second support.  In the \(B\) role, the correction
\(w+\theta(e_b-e_u)\) restores the witness equation and has nonnegative root
error and second-support values.  Its only possible loss is \(\kappa r_B\);
21 exact primal--dual certificates prove the sharp parent inequality
\(R\ge\kappa r_B\), with minimum zero.  Of the 62 \(\bar b\)-splits, 50
children absorb from the root alone.  The remaining 12 descendants admit
split-aware absorbers for all three second leaves: 36 exact systems, zero
failures.  Hence Peleg cases 1--3 preserve unit root absorption; case 4 is
the sole remaining closure step.  Exact artifact:
`results/peleg_case3_split_transport.json`.

Peleg case 4 is now closed on the certified family by a source-side
split-aware absorber.  For the mixed parent collection
\(\omega=(1-t)\mu+t\nu\) with \(\omega(I)=1\), keep root and second
allocations \(z^0,z^2\) separate and choose private-singleton mass \(s\) so
that
\[
 \deg(z^0+z^2)=\beta\mathbf1+m_Ae_a+\delta e_u,
 \qquad z^0(I)+s=\beta,
 \qquad (z^0+z^2)_B\le q^\omega_B.
\]
Attaching the new player to the marked root allocation and adding \(s\) of
the private singleton gives a child absorber coefficientwise.  The 56 roots
have 324 rank-one parent unions; 201 parent pairs yield 228 distinct decoded
emissions.  All \(228\cdot3=684\) split-aware systems are feasible in exact
rational arithmetic, and all 684 mapped child absorbers verify exactly.
There are zero failures.  Thus all four Peleg cases preserve unit absorption
on the certified root family.  Exact artifact:
`results/peleg_case4_split_aware_closure.json`.

New universal quantitative theorem (proved, sharp): put
\(a=q_A/\lambda_{1,A}\) and \(b=q_B/\lambda_{2,B}\). Every three-game
circuit has recoloring capacity at least
\(\rho_0=ab/(a+b)\geq1/2\), obtained by optimally mixing the all-
\(A\)-color and all-\(B\)-color decompositions of the aggregate balanced
collection. Type I has an explicit exact dual attaining \(1/2\). Consequently
every balanced-endpoint circuit margin satisfies the sharper bound
\[
M_C\geq(\rho_0-1)(\lambda_{1,A}d_A+\lambda_{2,B}d_B).
\]
In particular, endpoint exactness never needs to repair more than half of the weighted
bump contribution. This is the first dimension-free bound over all circuit
obstructions and gives a quantitative bridge back to Bet 1's bump-capacity
program.

## Bet 4: symbolic certificate discovery

src/mine_symbolic_invariants.py is an exact, single-instance invariant
extractor. It records:

- exact leximin strata;
- tight coalitions classified as inside, outside, or crossing \(S\);
- exact star value and residual-cover dual;
- residual level count and minimum-residual class;
- exact capacity, limiting faces, and all face certificates;
- minimum global and inside-\(S\) certificate sizes;
- the face predicted by the two-level theorem;
- every off-side slack comparison and its induced exact face bound.

Bet 4 has now produced a structural counterexample rather than another
regression. The local-circuit gluing construction composes three exact
nullity-one block relations, matches their shared monotonicity weights, and
then asks the reduced capacity solver for a sparse non-scalar repair. This
workflow found the forbidden-ratio circuit above and its four-coalition
capacity-one certificate. The reusable generator is
src/construct_forbidden_ratio_glued_circuit.py.

The generator has now been lifted to an enumerative symbolic engine:
src/hunt_glued_local_circuits.py independently enumerates local positive
circuits, glues them by exact rational edge-weight matching, filters on the
symbolic product gap, and exactifies the resulting capacity and fixed-
witness duals. This is the first Bet 4 workflow to discover a qualitatively
new deficient frontier rather than merely explain a saved example.

Bet 4 now also has a proof-directed separator engine for Bet 1.
`src/analyze_carrier_face_separator_dual.py` solves and exactifies the finite
dual system of Proposition `lx-carrier-separator-dual`; the batch audit
`src/audit_carrier_separator_boundaries.py` verifies the dual reduction on 80
saved partial-failure configurations and isolates positivity of every
face multiplier as the essential all-failed signature.

This deliberately replaces broad frequency summaries with proof objects. The
default six-player run recovers the pair certificate above exactly.

## Current breakthrough boundary

The original hoped-for global leximin selection theorem is false because of
the grand-coalition counterexample. The proper-coalition program remains alive
and is now concentrated on two independent gaps:

1. construct a face certificate for three-or-more-level failure duals with no
   slack-dominating off-side carrier;
2. prove the parametric path lemma after the star condition is available.

The finite-family program is independent of that failed selector. At \(n=5\),
the exact rank-12 classification is now complete for both disjoint shapes:
609 symmetry orbits and 5,670 transported supports, all neutralized. This is
the full three-game exact-family theorem at \(n=5\), not merely a larger
computational frontier.

The two highest-upside theorem targets are therefore:

1. prove the quantitative alternative (eta_S\geq\gamma_S) for general
   exact games, which would close the proper-coalition capacity step and
   expose the remaining parametric path lemma cleanly;
2. mine the completed \(n=5\) certificates for a uniform
   balancedness/exactness neutralization identity, then test that identity on
   the first \(n=6\) circuit geometries.
