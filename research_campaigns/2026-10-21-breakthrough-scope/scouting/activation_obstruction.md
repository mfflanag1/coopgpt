# Activation scout: exact obstruction and remaining loophole

Read-only source checked: canonical `coalition_withholding/manuscript.tex`, projective construction and fixed-arity appendix; cross-model scout result `20261021-003443-9e4b3f1c/result.md`. This note makes no claim about the unrestricted frontier beyond the existing manuscript. No external literature claim is needed for these deductions.

## 1. A support hypergraph that handles mixed and shared bundles

For a fixed report profile b, let H(b) be the finite hypergraph of inclusion-minimal owner coalitions E with F(b_E)>0. In an arity-r nonnegative packing technology every edge has size at most r. Indeed, a positive feasible production plan has a positive-profit activity run at positive level. For each of its at most r consumed resource rows choose one owner supplying a positive amount of that row. The resulting coalition of at most r owners can run that activity at some positive level; inclusion-minimality gives the claim. This does not require pure ownership, disjoint supports, unit coefficients, unit capacities, or unit profits.

Call an owner productive-active if it belongs to an edge of H(b). This is essential-participation activity, not merely membership in a chosen payment orbit. An owner supplying a redundant bundle can be outside all minimal positive coalitions even when its report is nonzero.

If only owner x increases its report from b to b', the edges not containing x are exactly the same in H(b) and H(b'). Both positivity of a coalition avoiding x and positivity of every proper subset of that coalition are unchanged.

Any actual institution automorphism stabilizing b' induces an automorphism of H(b'). In particular, members of one transitive owner orbit have equal incidence degrees in this finite hypergraph.

## 2. Equal-stars activation lemma

Let S be a transitive owner orbit at b', with the restoring owner x in S. Let D consist of x and any unchanged owners in S that were productive-inactive at b. Assume x was inactive at b as in a restoration from zero. Every edge of H(b') through d in D\{x} contains x; otherwise that same edge existed before. Thus star(d) is a subset of star(x). Transitivity gives equal finite degrees, so star(d)=star(x). Consequently

> Every edge through x contains all of D.

It follows immediately that |D|<=r. More sharply, if H(b') has an edge E meeting S with |E intersect S|<=k, then |D|<=k. Map a member of E intersect S to x by an automorphism preserving S; its image is an edge through x with exactly |E intersect S| private-orbit owners, and it must contain D.

The lemma only bounds genuinely new productive owners. It does not bound owners who were already productive but enter a larger symmetry orbit after the restoration.

## 3. Rooted cap consequence: Delta<=r-1, including mixed bundles

Suppose the cap owner p is outside S and every positive coalition contains p (equivalently F(b'_{N\{p}})=0). Every edge of H(b') then contains p, so an edge through a private owner has at most r-1 members of S. The sharpened lemma gives Delta<=r-1. At arity three, Delta<=2.

For pure unit row ownership the familiar graphical interpretation is exact: remove p from the minimal-support hyperedges to obtain a private-pair graph (allowing singleton edges for activities using fewer owners). A newly active unchanged private vertex can only be adjacent to the restored vertex. Regularity under transitivity forces degree one in the pair-only case, giving a matching and one newly active partner. The owner-support argument above is more general and avoids an unjustified restriction to pure rows.

## 4. Persistent seed anchor: private-only production need not be excluded

The root-veto assumption can be weakened. Suppose a fixed minimal positive coalition E from an earlier rung survives unchanged, meets the nested private orbit, and contains at most r-1 private-orbit owners at every later rung. Then it is an anchor for the sharpened lemma, so Delta<=r-1 at every later rung. The reports of E must remain unchanged; this is automatic when each restored owner was previously zero and outside all preceding active owners.

The manuscript-style seed supplies such an anchor even if private-only production is allowed. Let C={p,a,b} be a positive seed coalition at arity three; assume the seed stabilizer acts transitively on C, a,b remain in every later private orbit S, and p remains outside S. Take a minimal positive E0 subset C. If E0 touches a or b, use it. If E0={p}, a seed automorphism sends it to {a} or {b}. Thus there is a minimal positive E subset C touching a seed private owner and having at most two private owners. Since none of its members is a later restorer, E remains minimal positive forever. Therefore Delta<=2 at every later genuine-activation step, even with arbitrary mixed/shared bundles and private-only production elsewhere.

For general arity the same argument uses a seed coalition C of size at most r, with p outside the later private orbit and all its other owners inside that orbit. Seed transitivity supplies an anchor with at most r-1 private members.

This is an architecture theorem. It does not establish K_3(s)=O(sqrt(s)) or an upper bound on arbitrary lower-bound certificates.

## 5. Saturated non-rooted case and its production cost

Without an anchor, Delta=r forces all edges through x to equal D. Hence x has degree one. Transitivity implies degree one for every member of S, and the edges meeting S partition S into disjoint r-member productive blocks contained in S. Their coalition production values are equal by symmetry, say f. Superadditivity gives F(b'_N)>=(|S|/r) f.

If an old block keeps its reports through subsequent rungs, its positive value remains fixed; averaging its symmetry orbit yields the same linear lower bound on total production at later rungs. Thus a single fixed institution cannot sustain an arbitrarily long constant-output nested transitive ladder with that fixed positive block. This alone is not a uniform impossibility for M-indexed families: the block's value could shrink with M. The persistent seed-anchor argument is stronger when its hypotheses hold.

A useful general averaging inequality: if a group acts transitively on S, and C subset S, then F(b_N)>=(|S|/|C|)F(b_C). Average the orbit of b_C to obtain (|C|/|S|)b_S, use concavity and invariance, then monotonicity. This needs no uniform unit-resource assumptions.

## 6. Why the proposed q>2 projective pencil does not improve the exponent directly

Take projective lines span(v,e_j) over F_q, all meeting at [v], with independent branch directions. Put capacity one on the root and all q other points of each of m lines, and zero elsewhere. Include all collinear point triples as activities. A triple involving private points from distinct branches is not collinear: a nontrivial combination has two distinct branch coordinates. Thus every supported triple lies on a single branch line.

For q>=3 there are supported triples of three private points on each branch. The root-price-one dual is invalid. In fact F=(qm+1)/3 exactly. The row-count upper bound is immediate. For the matching lower bound, give root-containing triples equal weights so each branch uses root capacity 1/m, hence each private point uses 2/(qm) capacity; fill its remaining capacity uniformly with private triples on that branch. All q private points have the same residual capacity and q>=3 makes this feasible. Total consumption is qm+1, three per unit of output.

For q=2 there are only two private points per branch, no private-only triple, and F=1 as in the manuscript. Increasing q therefore introduces linear-in-m production rather than free activation.

If fewer points are reported, a newly supplied third point on a branch activates only itself and the one previously present private point. If two private points were already present with the root, those owners were already productive before restoration. This is precisely the distinction between genuine activation and orbit merging.

## 7. What the scout's proposed A_lambda still needs

The cross-model scout does not construct a family. Its A_lambda conditions omit a precise definition of "active," do not explicitly require the old payment orbit to be a nested subset of the new one, and do not state that the restorer belongs to the new common-payment orbit. Those facts are needed by its recurrence. Also, a supported three-owner activity is not automatically worth the full normalized aggregate production.

If all lambda private owners have the same seed payment, and cap exchange joins p to that orbit, the generated seed symmetry is transitive on lambda+1 owners. For a three-owner seed coalition C, orbit averaging gives F(b_N)>=(lambda+1)F(b_C)/3. Thus the claimed q1>=1/3 after normalizing aggregate production to one is unavailable for lambda>=3: it would require F(b_C)=F(b_N). A smaller positive constant seed might still preserve a fixed-lambda exponent, so this corrects the asserted prefactor rather than independently ruling out every proposed family.

The concrete escape not covered by the activation theorem is a larger orbit absorbing owners that were already productive at earlier rungs, perhaps with small production values depending on M. Then their old support stars need not vanish after deleting the restorer, and the key inclusion fails. A bare graph example is K_{t-1,t} becoming K_{t,t} when one vertex is inserted: the smaller-side orbit of t-1 vertices becomes a transitive orbit of 2t vertices. It is not a manuscript-compatible ladder from the cap-exchange seed; it merely shows why productive-inactivity cannot be dropped from the lemma.

## Assessment for the 150-minute target

The direct larger-field projective suggestion fails for an explicit reason, and the natural rooted-cap activation architecture has an exact Delta<=r-1 obstruction substantially stronger than the pure-row argument. This is a valid bounded negative deliverable. It is not evidence that the unrestricted arity-three frontier has square-root growth.

A credible new exponent still requires a genuinely new mechanism: demonstrate nested payment-orbit merging of already productive owners with constant aggregate output and a uniform seed, or abandon this one-restorer/common-payment ladder. No such family has been constructed here. The current recommendation should not be advertised as high-probability breakthrough work on the strength of changing the field alone.

## 8. Parent's punctured-affine-block orbit-merging family

Let U be k-dimensional over F2, Q=2^k, V=U direct-sum span(e_1,...,e_M), and use all binary projective triples. Root rows U\{0} have capacity one. At C_m, the first m affine blocks e_j+U have all Q points present and the remaining blocks have Q-1 points present, missing e_j. Every displayed positive row belongs to a separate pure owner. Supported triples are root-root-root or root plus a same-block private pair; there are no private triples. Completing a punctured block by restoring its missing owner merges all Q block owners into the full-block orbit. This is genuine orbit merging: the old Q-1 points were already productive.

The full-block private orbit is transitive, but the proposed seed fails. Incidence degrees are

- root row: (M+1)(Q/2-1)+m;
- full-block private row: Q-1;
- punctured-block private row: Q-2.

For M>=2,k>=2, roots have strictly higher degree than either private type. Thus no profile-stabilizing technology automorphism exchanges a root and full-block private row. At k=2,M=2,m=1 the three orbit sizes are 3,4,3 and their degrees are 4,3,2. The linear stabilizer has 24 elements: GL(U) of size 6, and the four translations e_1 -> e_1+u; the missing point e_2 is fixed. The remaining five zero-capacity rows form a singleton and a four-point orbit.

For M>=2 and m>=1, F(C_m)=Q-1 exactly. Root prices one give the upper bound. If one block is full and one punctured, put 1/(Q-1) on every pair activity within those two blocks. Each root is consumed Q/[2(Q-1)]+(Q-2)/[2(Q-1)]=1; each full private point is consumed once and each punctured private point (Q-2)/(Q-1). If two blocks are full, put 1/Q on each pair activity in both; root consumption is again one and private consumption (Q-1)/Q. These attain Q-1.

Consequently the restrictions consisting ONLY of C_1,...,C_M, their all-coalition coverage rows, and their internal withholding comparisons admit factor one: pay every root owner one, every private owner zero. The full-technology root-plus-zero-row dual verifies coverage. Root payments remain constant and private coalition sums are zero along the displayed transitions. This statement is not a globally feasible rule and does not dispose of additional seed-transfer profiles.

A seed profile with only one full block and no punctured blocks has root/private symmetry, but transferring its private payments into C_1 allows the restored punctured owners to absorb them. It does not directly force q_1>0 for the full-block orbit. Any campaign using this family must supply a new seed-transfer certificate that rules out that absorption. Simple scalar seed-sum constraints allow a constant-total private-payment schedule: q_m=c/(QM) on full-block owners and r_m=c/((Q-1)M) on punctured-block owners, giving Qm q_m+(Q-1)(M-m)r_m=c. Completion of one punctured block respects the coalition sum Q q_m=(Q-1)r_{m-1}. This does not check every conceivable profile constraint; it shows that a total seed mass plus the obvious completion inequalities cannot by themselves yield a divergent bound.

### Explicit constant-factor counter-schedule with the natural seed included

The preceding finite-constraint escape can include the obvious symmetric seed D, where only the roots and block 1 are reported; every other block is zero. At D the 2Q-1 positive rows form the full binary projective geometry on U+span(e_1). Its production is (2Q-1)/3, witnessed by uniform fractional packing and the all-rows price 1/3. Pay each positive-row owner 1/3 and every zero reporter zero.

At each C_m, set

- every root owner's payment to 1;
- every full-block private payment q=1/(3M);
- every punctured-block private payment r=Q/[3(Q-1)M];
- every zero reporter's payment to 0.

Total private payment is Q/3 and total funding factor is 1+Q/[3(Q-1)], independent of M (13/9 for Q=4). All-coalition coverage holds by the root dual, plus nonnegative private payments. At D coverage holds by the all-rows price 1/3.

Every displayed withholding comparison satisfies TCWM, even without a coalition-size limit. In C_{m-1}->C_m, the required restorer gains q, and each of the Q-1 previously present private owners of the completed block loses r-q=q/(Q-1). Any coalition's losses are therefore at most the restorer's gain. Multiple completed blocks add these nonnegative inequalities. In D->C_m, the restored owners receive total Q/3-Qq. If the protected coalition contains a of the Q old private owners, its old-to-new loss from them is a(1/3-q), at most Q/3-Qq. Included root owners gain 2/3 each. Thus the comparison holds. Since all withheld bundles in these displayed comparisons are root-free, and no supported private-only activity exists, their outside-production term is zero; full OUT also holds for these comparisons.

This is an exact feasible assignment for coverage plus all comparisons among D,C_1,...,C_M. It is not an extension to the full real report domain or to all symmetry-orbit profiles. Any useful lower certificate for this family needs additional profiles/comparisons beyond the natural symmetric seed and displayed completion ladder.
