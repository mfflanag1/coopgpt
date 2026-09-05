# Independent carrier-threshold audit

Date: 2026-09-05. Bounded follow-up to the unrestricted asymptotic audit.
Original source files were read only.

## Verdict and contribution

The carrier theorem withstands this independent hand-proof audit:

> For every exact TU game with at most six players, every core reference
> point `psi`, and every proper nonsingleton target `S`, one has
> `eta_S(psi) >= gamma_S(psi)`. An exact seven-player game violates the
> inequality even when the reference is normalized Lmin.

Here, with `P=N\S` and slack `s_psi(T)=psi(T)-v(T)`,

\[
\gamma_S(\psi)=\min_{\varnothing\ne C\subsetneq S}
      \bigl(s_\psi(P\cup C)-s_\psi(C)\bigr),
\]
\[
\eta_S(\psi)=\max\{x(S)-\psi(S):x\in\operatorname{Core}(v),
                                     \ x_i\ge\psi_i\ (i\in S)\}.
\]

This is a substantive, separately identifiable structural contribution:
it gives an exact dimension threshold for simultaneous coordinatewise
improvement under a quantitative coalition-slack condition. The statement
is stronger than a claim solely about one selected allocation because it
holds at every core reference. It is **not** a characterization of coalitional
monotonicity. In this project that property can fail at five players;
the carrier threshold is seven. Its wider significance depends on uses of
this carrier objective beyond the attempted monotonicity proof. This audit
does not establish novelty or a field-level impact claim.

## Source and proof chain checked

The main source is `coopgames/paper3/sections_leximin.tex`:

| Location | Result checked | Verdict |
|---|---|---|
| Lines 646–692 | Definitions, translation/scaling, exact carrier lift | Sound |
| Lines 786–829 | Indicator witnesses and exclusion of two-level separators | Sound |
| Lines 833–928 | Codimension-one lift, pair bound, through-four corollary | Sound |
| Lines 1011–1063 | Eta dual and target-conditioned minimal balanced collections | Sound |
| Lines 1142–1270 | Rank-six three-level classification | Hand argument checked; reduced exact replay passes |
| Lines 1272–1338 | Through-six theorem | Sound; see the small proof-dependency clarification below |
| Lines 1342–1459 | Seven-player exact counterexample and normalized Lmin | Hand proof checked; both exact replays pass |

The retrospective claims in `EXTERNAL_REVIEW_RESPONSE.md` and
`GOAL_COMPLETION_AUDIT.md` helped locate the proof. I did not treat their
reported external-review verdicts as independent evidence for this audit.

### Indicator witnesses and the dual reduction

For any nonempty proper `A` inside `S`, choose an exact core point tight at
`P union (S\A)`. Its displacement `d` satisfies both
`d(A)>=gamma` and `d(S)>=gamma`. For `A=S`, an arbitrary nonempty proper
carrier coalition supplies the same total bound. Consequently every
nonnegative two-level weight vector `w=a 1_S+b 1_A` has a positive value
on at least one such displacement when `gamma>0`.

This rules out any two-level normal separating
`K={d_S:d in Core(v)-psi, d(S)>=gamma}` from the nonnegative orthant.
Compactness, nonemptiness, and the sign of a separating normal are all
accounted for. The pair argument's stronger uniform split follows because
every nonnegative two-dimensional normal has this form. For a singleton
outside set, the explicitly uniform displacement satisfies every coalition
constraint, including the outside singleton via exact-game superadditivity.

The eta LP dual has the balance identity

\[
\mathbf1_S+\sum_T\lambda_T\mathbf1_T+
\sum_{i\in S}w_i e_i=(1+\rho)\mathbf1_N,
\qquad \lambda,w,\rho\ge0.
\]

The nonnegative slack objective is `sum lambda_T s(T)`. A target column
or target singleton charged through `lambda` can instead be moved to the
zero-cost floor multipliers `w`. On the resulting face, vertex duals
correspond to minimal balanced collections containing `S`. Such a support
has at most `n` linearly independent coalition incidence columns. The
normalization and slice argument in the text are valid; recession directions
with zero target coefficient do not create additional vertices.

If `eta=L<gamma`, this identity gives
`w dot d_S <= L-d(S)<0` on `K`. Thus the selected dual floor vector must
have at least three levels. This is the precise link between the game and
the short incidence classification, not an assumption based on the census.

### Why the six-player classification closes

Adjoin `S` and its `q` positive target singleton columns to the residual
`r` columns. Linear independence implies some target floor is zero and
`r<=5-q`; three levels require `q>=2`, so `r<=3`.

In the `3+3` split, necessarily `q=2`; quotienting out the target span
leaves independent outside binary columns. Positive normalized weights
solving outside degree one can only be `(1)`, `(1,1)`, `(1,1,1)`, or
`(1/2,1/2,1/2)`. Below a zero-floor subset height `h<1`, there is at most
one distinct lower height, preventing three floor levels.

In the `4+2` split, `q=3` similarly leaves at most two outside columns and
cannot support positive floors. For `q=2`, one or two residual columns again
leave too few lower subset heights. With three columns, independence in
the quotient `(x_3-x_4,x_5,x_6)` yields two independent equal-subset-sum
relations among three positive weights. After cancellation, a relation is
either an equality of two weights or a sum of two equal to the third.
Two independent sum relations contradict positivity. Two equality relations
give equal weights and insufficient lower heights. The mixed case forces
weights `(1/3,1/3,2/3)` and zero-floor height `2/3`.

Reconstruction gives, up to the stated permutations, only

\[
\mathbf1_{1234}+e_1+2e_2+\mathbf1_{35}+
\mathbf1_{136}+2\mathbf1_{456}=3\mathbf1_N.
\]

Its cost is `s(35)+s(136)+2s(456)>=2gamma`: the carrier comparison for
`C={4}` gives `s(456)>=gamma+s(4)`, and all slacks are nonnegative.
This contradicts a cost below `gamma`. I checked the equal-subset-sum case
split literally; I found no missing positive-weight case.

### Clarify the remaining n=5 dependency

As written, the through-six proposition first invokes the earlier
computer-assisted through-five theorem. Thus the assembled written chain
does still refer to the 43-orbit five-player calculation, although it no
longer depends on the much larger 1,489-orbit six-player audit.

For **exact games**, this computational dependency can be removed by the
following elementary argument. Add a zero dummy outside `S` to a five-player
game and define `v'(T)=v(T intersect N)`. The new core is exactly
`Core(v) times {0}`: the new singleton has lower bound zero and the original
grand-coalition constraint and efficiency force its coordinate to zero.
Exactness is preserved, and both `gamma` and `eta` are unchanged. A
five-player `3+2` violation would therefore give a six-player `3+3`
violation, which the hand argument above excludes independently of the
five-player theorem. More generally one can first pad to six outside `S`.

This is a proof-dependency clarification, not a mathematical defect in the
stated theorem. It does **not** establish the separate five-player
strengthening from exactness to total balancedness; that strengthening still
uses the archived 43-orbit calculation, which I did not replay here.

## Seven-player failure checked independently

Let `S={1,2,3}`, `P={4,5,6,7}` and

\[
a=(-3,1,3,-1,2,-1,-1),\quad
b=(3,-2,0,-1,-1,-1,2),\quad
v(T)=\min\{0,a(T),b(T)\}.
\]

All three generators have total zero and attain the lower envelope, so
the game is exact. The six proper nonempty carrier differences all equal
one at zero. The zero-valued coalitions
`13456,457,3467,567` satisfy

\[
\mathbf1_S+\mathbf1_{13456}+\mathbf1_{457}+
\mathbf1_{3467}+\mathbf1_{567}+e_1+2e_2=3\mathbf1_N.
\]

For a core point nonnegative on `S`, every term on the left has nonnegative
payoff while the right is zero. Thus its `S` total is zero, proving
`eta_S(0)=0<1=gamma_S(0)`.

The singleton floors are `m=(-3,-2,0,-1,-1,-1,-1)`. The manuscript's
three-stage argument for **gains above these floors** is correct:
`v(125)=0` bounds the first floor by `3/4` and fixes players `3,4,6,7`;
`v(13)=v(27)=0` then bounds player 5's gain by `3/2`; efficiency bounds the
remaining common gain by `9/4`. The point `phi=a/4` attains every bound
and belongs to the core as a convex combination. All six carrier
differences are `3/4` there, and the four zero-cost coalitions are also
`phi`-tight, giving `eta_S(phi)=0` by the same identity.

The word "leximin" here means the normalized selector `m+Lmin(v-m)`;
it is not the raw-payoff leximin selector on a game with unequal singleton
floors. This nomenclature is disclosed in `EXTERNAL_REVIEW_RESPONSE.md`.
Subtracting the additive vector `m` produces a singleton-normalized exact
game with total 9 and ordinary Lmin

\[
(9/4,9/4,3/4,3/4,3/2,3/4,3/4).
\]

Both carrier quantities are invariant under this additive translation, so
the seven-player failure also has a standard normalized formulation.

## Fresh exact computation and harness issue

Executed with assertions enabled under the supplied exact Python runtime:

| Script | Result | Fresh artifact in this scratch directory |
|---|---|---|
| `verify_n6_three_level_matrix_classification.py` | PASS; rational elimination, reduced patterns only, no optimization solver | `n6_carrier_matrix_replay.json` |
| `verify_n7_exact_carrier_counterexample.py` | PASS; all 128 coalition values and the degree identity | `n7_carrier_replay.json` |
| `verify_n7_exact_carrier_counterexample_leximin.py` | PASS; rational staged Lmin and hand certificate | `n7_carrier_lmin_replay.json` |

The reduced matrix verifier was read before running. Its full-rank tests
justify discarding repeated quotient columns; it enumerates all reduced
binary row patterns and recovers precisely the exceptional orbit. Its
`-O` rejection is present. The seven-player scripts were also read before
running, and their scientific identities agree with the hand proof above.

However, contrary to the broad harness statement in
`EXTERNAL_REVIEW_RESPONSE.md`, these **two seven-player scripts** use
assertions without an optimized-Python guard in the audited originals.
This does not invalidate the runs above, but an `-O` invocation is not a
meaningful validation run because its checks disappear.

Per the parent's follow-up request, I prepared minimal guarded copies in
`guarded_carrier/`, without editing originals. The early check is
`if sys.flags.optimize: raise SystemExit(...)`. The patch is
`guarded_carrier/assertion_guards.patch`. Both ordinary guarded runs produce
exactly the same scientific JSON as the originals. All eight optimized
invocations—`-O`, `-OO`, `PYTHONOPTIMIZE=1`, and `PYTHONOPTIMIZE=2` for each
script—exit 1 before scientific output. Results are in
`guarded_carrier/guard_test_results.json`.

## Boundaries of this audit

I did not rerun the 1,489-orbit exact-cone census, the 65,133-support scan,
the five-player total-balancedness strengthening, the later outside-triple
seven-player classification, the robust parameter families, or the complete
paper-three release. Their archived presence is not included in this audit's
PASS verdict. The compact proof and the base sharp witness are sufficient
for the exact-game six/seven threshold audited here.
