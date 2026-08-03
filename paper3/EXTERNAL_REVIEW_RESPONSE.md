# Response to the external hostile audit

This note responds to `review_findings.md`, received 2026-08-03.  That audit
examined an earlier manuscript revision centered on the then-numbered
Propositions 5.22 and 5.23.  It predates both the rank-reduced six-player proof
and the sharp outside-triple leximin family now in the paper.

## Mathematical verdict

The reviewer found both commissioned propositions **sound**.  More
importantly, the verdict was not based on reading our outputs: the reviewer
independently reconstructed the full six-player census, all 1,489 rational
lower-bound certificates, the real-game Farkas transfer, the primal
attainment checks, the two-generator proof, the seven-player identity, and
the leximin calculation.  No counterexample or invalid inference was found in
the commissioned theorem chain.

The current paper is stronger than the audited revision.  Its six-player
theorem now follows from the two-level separator theorem and a hand-checkable
classification of two equal-subset-sum relations among three positive
weights; the 65,133-support scan and 1,489-orbit computation are retained only
as independent redundancy.  At seven players the paper now
gives an exact leximin counterexample with three outside players, proves that
two outside players are impossible at seven, and embeds the obstruction in a
relatively open two-parameter family.

The post-review revision also contains a new monotonicity-bridge theorem.  It
exhibits an exact seven-player game with `gamma=36>35=eta` and binding exact
bump capacity `d*=10>sigma=9`, yet computes the entire admissible leximin path
and proves it coalitionally monotone.  This result was not within the external
review's scope and should be audited separately.

The monotonicity question has since been settled negatively by a still newer
result, also outside the audit's scope.  A five-player exact lower-envelope
pair differs only by the bump `v(1345):18 -> 20`, but its leximin points are
`(1,1,13/2,5,13/2)` and `(2,0,6,6,6)`: target players 3 and 5 each lose
`1/2`.  A solver-free verifier checks both games from their common-total
generators and proves the complete affine path.  This theorem requires a new
external audit; none of the review verdicts above should be read as covering
it.

## Write-up findings

All sixteen write-up findings were accepted.

1. The six-player proof now explicitly observes that `eta >= 0`, so a
   violation necessarily has positive `gamma`.
2. The support bound now includes the dependence-perturbation proof that a
   minimal balanced collection has linearly independent incidence columns.
3. A translation-and-positive-scaling lemma now states exactness preservation
   and the common homogeneity of `gamma` and `eta`.
4. The six-player proof now states that the adjoined target and target-floor
   columns have zero slack cost.
5. TU game, core, balanced game, exact game, balanced collection, and minimal
   balanced collection are now formally defined.
6. “Gain cannot exceed `m_i+s`” is corrected to “payoff cannot exceed
   `m_i+s`.”
7. The ambiguous “binding by 5/3” is replaced by the explicit core-expansion
   margin `max_core x(S)-phi(S)=5/3`.
8. The two-generator proposition now assumes a proper nonsingleton target.
9. The compensation condition is explicitly described as a sufficient
   one-way screen, not an equivalence.
10. The text distinguishes the general reference-point identity from the
    `psi=phi` capacity application.
11. The leximin point is now described as belonging to the game, not to the
    chosen target coalition.
12. The mask-80 dual now explains that complementary slackness is at the
    displayed face optimizer, not at `phi`.
13. The unit-triple proof now discloses the harmless three-orbit degeneracy:
    thirteen literal orbits plus one repeated-coalition and two dominated
    singleton cases.  Bounding the superset is stronger.
14. The pair-separation proof now states nonemptiness, compactness, and why
    the separating normal is nonnegative.
15. The codimension-one proposition now states `|S|>=2` locally.
16. The total-balancedness note now makes the correct dimension-seven claim;
    it no longer says that total balancedness fails whenever the outside set
    has size two.

## Verification-harness findings

The load-bearing path has been hardened as follows.

- Critical certificate scripts now reject `python -O` outright, preventing
  assertion stripping from producing a false green run.  Converting every
  historical exploratory script away from assertions remains desirable, but
  those scripts are not part of the current proof chain.
- The n=6 replay now requires exactly 870 and 619 orbits, and the n=7 replay
  requires exactly 34 and 5.  Both also require the complete expected split
  set.  The legacy n=6 structural checker pins the raw and orbit counts rather
  than laundering arbitrary input headlines.
- The focused rank-six verifier performs its own complete enumeration in the
  same run; the old full-census checker remains explicitly redundant rather
  than the logical source of coverage.
- The outside-triple verifier now derives the eta upper bound from the
  balanced identity and zero face costs and matches it to a feasible lower
  bound, instead of merely printing a literal conclusion.
- The paper no longer claims that its replay script reads saved primal
  certificates.  It accurately distinguishes replayed dual lower bounds from
  saved primal attainment points; the external audit independently checked
  both.
- `exact_linprog` now rejects float inputs.
- The unit-triple producer requires an explicit `--output` path and therefore
  cannot silently overwrite the checked artifact.
- `Game` validation now uses explicit exceptions, one-player balancedness is
  handled correctly, and the primary lower-envelope constructor rejects
  generators without a common total.

The reported `exactlp_cegar.py` relaxation-status defect is not present in
this focused branch.  If that experimental module is restored, an unbounded
outer relaxation must not be reported as proof that the full LP is unbounded.

## Bottom line

The external review substantially raises confidence in the six-player
theorem: it is an independent reproduction with no mathematical defect found,
not merely a stylistic review.  Its strongest criticism was that several
correct steps and verification assumptions were too implicit.  Those points
have now been made explicit, while the current proof has also reduced its
dependence on the large computation.

This is still not journal peer review.  The highest-priority next review is a
domain referee checking the new five-player monotonicity counterexample and
its Maschler-stage proof.  The rank-reduced six-player proof and seven-player
outside-triple family should also be checked, since all three results postdate
the external audit.
