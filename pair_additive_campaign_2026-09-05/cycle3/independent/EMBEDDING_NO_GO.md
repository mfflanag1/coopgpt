# Six-player obstruction to faithfully completing the unrestricted recurrence

5 September2026. Independently derived conventional proof; finite raw checks recorded separately. This is a bounded no-go for a specified encoding route, not a universal lower bound for pair-additive markets. No source-priority claim is made.

**Conclusion.** For every recurrence depth L>=2, the unrestricted sparse triple example cannot be converted to a nonnegative pair-additive market by retaining its players, preserving its full labeled payoff core, and increasing/completing its triple values. The obstruction survives arbitrary auxiliary players if the old coordinate projection still contains two specified original core allocations and the two critical original productive triples retain their values. In fact pair coefficients may even be signed: only pair-additivity and nonnegative induced triple values are needed.

## The six-player lemma

Take two players per sector, denoted `(U,K; V,G; D,J)`. Suppose a complete pair-additive triple tensor w is nonnegative. Suppose two allocations satisfying all its triple covers have the following restrictions to these six players:

| Allocation | U | K | V | G | D | J |
|---|---:|---:|---:|---:|---:|---:|
| p^0 | 0 | 0 | 1 | 0 | 0 | 0 |
| p^1 | 1 | 1/2 | 0 | 0 | 0 | 1/2 |

Then it is impossible that both `w(U,V,D)>=1` and `w(K,V,J)>=1`.

Proof. At p^0, every triple in the G slice, with first player U or K and third player D or J, has zero payoff sum. Its weight is therefore zero by nonnegativity. Pair-additivity gives the rectangular identity

`w(U,V,D)+w(K,V,J)-w(U,V,J)-w(K,V,D)`
` = w(U,G,D)+w(K,G,J)-w(U,G,J)-w(K,G,D) = 0`.

This identity is the cancellation of the twelve pair coefficients in a2×2×2 cube. The two retained clauses give a lower bound2 on the first two terms. The p^0 cover gives `w(U,V,J)<=1`, while p^1 gives `w(K,V,D)<=1/2`. Hence2<=3/2, a contradiction. No matching, efficiency, or auxiliary-player assumption enters the lemma itself.

More generally the second allocation can have K and J payoffs theta and any nonnegative value, respectively; the proof only uses K=theta<1, V=D=0. The upper bound becomes1+theta<2. Thus the same obstruction applies to an exact complementary sum gate whose inputs can be zero at one point and strictly less than one while the output reaches one at another, with the stated zero slice and retained clauses.

## Apply it to the original all-depth construction

Use the recurrence market in the original assignment manuscript, with no top copies required. Its full core has `U_(ell,i)=q_(ell,i)` for ell>=1, `V_(ell,i)=1-q_(ell,i)`, `q_ell=(J-I)^ell q_0`, root offsets as given there, and all D/G payoffs zero.

Both `q_0=0` and `q_0=2^(-L)*(1,1,1)` are valid full-core parameters. The latter has every top U equal to1 and every preceding U equal to1/2. Fix a top index i. Let U and V be its own top matched pair and D its local zero dummy. Of the two previous-level U players in the reverse recurrence triple, call J the one of D's color and K the one of U's color. The parity-dependent coloring guarantees exactly one of each. Let G be the global fixed-zero player of V's color.

The two full-core allocations restrict to the table in the lemma. The original local triple `(U,V,D)` and reverse recurrence triple `(K,V,J)` both have value1 because L>=2. A pair-additive completion dominating the old weights would retain both clauses, yet all its triple covers would need to hold at both old core points. The lemma rules this out.

This argument is independent of root offsets, number of top copies, normalization, and any additional agents. Any faithful auxiliary extension whose projection contains these two original payoff points and whose old triples still carry the two required values is equally impossible. Preserving the full old core is more than is needed for the contradiction.

## Exact scope of the obstruction

The rejected route was: choose nonnegative pair matrices such that induced weights dominate all original productive triples while every original core point remains feasible. Were that possible, old matching/cover duality would give an exact full-core embedding with no hidden auxiliary freedom, transferring the bad selectors and ideals. The six-player lemma disproves even its two-point necessary condition.

This does **not** rule out an encoding that lowers/replaces an original productive clause and enforces its effect through different auxiliary constraints; an encoding that adds payoff offsets, changes the original zero coordinates, or applies a more general coordinate map; or a direct pair-additive amplifier with different core geometry. Those routes must separately control the full payoff vector, nonempty integral core, complete mixed triples, and the selectors. The present result is therefore a concrete obstruction to a natural proposed representation, not evidence that a1/6 universal guarantee holds.

## Independent checks

`check_completion_obstruction.py` reconstructs the original recurrence from player names and colors without importing any package scientific module. At L=2,3,4 it directly verifies the two displayed original core covers and totals. A raw linear-real-arithmetic feasibility query rejects completion on all triples. The six-player subquery also returns UNSAT with signed pair coefficients and only nonnegative triple values. A solver-free incidence calculation verifies the cube identity exactly; the rational contradiction gap is1/2. Any status except UNSAT raises an error. Results are in `completion_checks.json`.

The proof applies to all L>=2; the finite solver results corroborate its transcription rather than certify all depths. No original package or other worker file was edited, and no broad literature search was performed.
