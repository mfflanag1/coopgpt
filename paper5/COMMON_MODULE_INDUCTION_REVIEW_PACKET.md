# External review packet: common-module role induction

## Claim to review

Let `P_r` be the atomic overlap target for every nonnegative exact weighted
game on at most `r` roles, with positive integer role weights of total `n`
with `n>=6` and zero singleton worth on every unit-weight role.  Assume
`P_(r-1)`.

If an `r`-role instance has a nontrivial set of roles `H` that is a tight-face
module at both weighted Lmin and weighted Lmax, and the per-capita selector
coordinates are constant on `H` at each selector, then the instance satisfies
the target.  Hence a counterexample minimal in its number of roles has no
common selector module.

This closes the contraction arm of objective B.  It does not prove the
remaining separator/direct/marked-facet selection theorem.

## Human proof

Contract `H` to one role of weight

```text
h_* = sum_(i in H) h_i.
```

The previously proved common-module contraction theorem gives a nonnegative
exact quotient.  The projections of the two selectors are its weighted Lmin
and weighted Lmax; total payoff and hybrid overlap are unchanged.  Every
unit-weight role outside `H` retains zero singleton worth.  The new role has
weight at least two, so its possibly positive singleton worth is allowed by
the weighted statement.

The quotient has `r-|H|+1 <= r-1` roles and the same total atomic weight `n`.
Applying `P_(r-1)` therefore gives exactly the target for the original
instance.  Weighted coincidence through three roles and the atomic weighted
four-role theorem establish the induction base `P_4`.

The important logical point is that the quotient does not need a new local
affordability analysis: the whole smaller-role theorem is the strong
induction hypothesis.  The selection theorem at the current role count still
needs a weighted formulation retaining block multiplicities and prices.

## Consequence for carrier cycles

A carrier cycle is already a tight-face module at Lmin.  If no Lmax-tight
coalition splits it, it is a common selector module and the induction above
applies.  Thus, whenever the current-role selection machinery produces a
carrier cycle inside a role-minimal counterexample, some Lmax-tight coalition
must split that cycle.  Its complement supplies the previously proved strict
comparison payment.  The unresolved problem is to normalize and aggregate
those payments with the staged Lmin packet without double charging a payoff
layer.

## Exact regression

Run from the repository root in the pinned paper environment:

```bash
PYTHONPATH=coopgames/verifiers/divergence:coopgames/src \
  /tmp/coop-paper5-review/bin/python \
  coopgames/verifiers/divergence/audit_carrier_separator_payment.py \
  coopgames/verifiers/s6/harvest6_601.json \
  coopgames/verifiers/s6/harvest6_602.json \
  --output /tmp/carrier-separator-payment.json

cmp coopgames/verifiers/divergence/carrier_separator_payment.json \
  /tmp/carrier-separator-payment.json
```

On the 228 archived six-player all-unaffordable rows, the audit finds 420
carrier cycles: 251 common modules and 169 split by the Lmax face.  At the row
level, 163 have at least one inductively contractible common module.  The 65
rows with no common module all have a splitting Lmax row.  These counts audit
the structural handover only; the archive is not a census and does not prove
the all-dimensional selection theorem.

Among those 65 role-irreducible rows, 62 are already closed by a tight direct
packet using the cycle itself.  In each of the remaining three, the unique
splitting-row complement contains every gainer and so violates the direct
identity's proper-gainer-packet hypothesis.  An Lmin-tight repair replaces at
least one gainer with one additional upper nongainer and has cardinality base
`4/5`.  This three-row separator-rotation pattern is the next falsification
target, not a proved general lemma.

There is one additional human reduction.  If a nongainer carrier cycle has
strict loss `a-b>0`, then every gainer `j` is omitted by some Lmin-tight
coalition containing the cycle.  Otherwise `j` would be a carrier of a cycle
member, so carrier monotonicity would give `x_j>=a`; maximum-overlap geometry
instead gives `x_j<=b<a`.  This proves proper-packet support in the strict
branch, but not the residual inequality.  It also does not cover the tied
case `a=b`.

The cardinality inequality is independently automatic.  If the direct
nongainer block contains a carrier cycle, its atomic multiplicity is at least
two.  For any proper gainer packet, the direct base satisfies

```text
1-gp/[(g+h)(p+g-s)] >= 4n/[n^2-(n mod 2)].
```

Monotonicity reduces the worst case to `s=g-1,h=2`; the resulting quadratic
has negative discriminant for even `n>=8` and odd `n>=7`, while `n=6` has the
unique equality parameters `(p,g,h,s)=(2,2,2,1)`.  Accordingly strict-loss
carrier cycles leave only the normalized residual-sum selection problem.

That apparent label problem cancels in the exact direct identity.  With
`B=g/(p+g-s)`, comparison payment `Delta(J)-L_H`, and residual budget `U_s`,

```text
B[Delta(J)-L_H]+R_x+R_z = B(U_s-L_H),
U_(s+1)-U_s = [z(G)-x(G)]/g >= 0.
```

Thus the best proper packet has size `g-1`, its labels are irrelevant, and
the only remaining direct condition is the scalar nongainer-block budget
`U_(g-1)>=L_H`.  On all 65 role-irreducible archive rows, taking `H` to be
the full nongainer maximum-overlap root block passes this budget; the cycle
alone passes on 63.  This was only an `n=6` pattern, and the exact
seven-player control below disproves its dimension-free extension.

Writing `M` for maximum overlap, `H` for all nongainer roots, `P` for the
other nongainers, and

```text
U=sum_(P)(M-z_i),  R=sum_(G)(M-x_j),  D=z(G)-x(G),
```

the full-root-block budget is exactly

```text
U_(g-1)-L_H
 =[g(g+h)U-gpR-[g+h(p+1)]D]/[g(g+h)].
```

The identity is correct, but its proposed sign is false.  The exact lower
envelope of

```text
(6,7,1,0,2,0,1), (7,0,0,0,0,10,0), (0,0,0,5,4,6,2)
```

has

```text
x=(3,7/2,1,3,2,7/2,1),
z=(14/5,16/5,2/5,13/5,16/5,16/5,8/5).
```

Roots `{1,5}` are mutually locked and unaffordable, while Lmax-tight rows
`33,101` split them.  For the full root block,

```text
M=16/5, P={0,2,3}, G={4,6}, U=19/5, R=17/5, D=9/5,
RBB numerator=-8, scalar margin=-1.
```

The main target is unharmed: `O/T=76/85>7/12`.  The unique target-reaching
direct packet uses tight coalition `59` and

```text
P={2}, G={4,6}, H={0,1,3,5}, J={4},
base=5/6, scalar margin=17/30.
```

Thus the surviving conjecture is selected tight-support congestion or a
separator/marked-facet alternative, not full-root-block nonnegativity.  A
new human support lemma helps: every positive-loss source in a gainer's
sign-coherent Lmin transport satisfies `x_i<=x_j<M`, so it lies among the
nonroot nongainers, and

```text
M-z_i >= (M-x_j)+(x_i-z_i).
```

What remains unproved is the necessary joint column-congestion bound.

Reproduce the counterexample and its independently formulated staged
optimality checks with

```bash
python3 coopgames/verifiers/divergence/verify_n7_root_block_budget_counterexample.py \
  --output /tmp/n7-root-block-budget-counterexample.json

cmp coopgames/verifiers/divergence/n7_root_block_budget_counterexample.json \
  /tmp/n7-root-block-budget-counterexample.json
```

## Hostile questions

1. Does exactness descend under contraction for every quotient coalition,
   including coalitions containing the new weighted role?
2. Is the local selector-lifting argument sufficient to identify the
   quotient projections with the full weighted lexicographic selectors?
3. Does the unit-role singleton hypothesis survive exactly as stated, without
   silently normalizing the positive singleton worth of the contracted role?
4. Is total atomic weight, rather than role count, correctly retained in the
   target constant?
5. Is strong induction on role count logically valid without rerunning the
   affordability/carrier machinery inside the contracted instance?
6. Does the carrier-cycle consequence remain explicitly conditional on a
   weighted current-role selection theorem, rather than claiming that theorem
   has already been proved?
7. Do either balanced seven-player equality orientation or the `G(p,k)` sharp
   family get incorrectly removed by the minimal-counterexample reduction?
8. Does the strict-loss carrier-monotonicity argument prove omission by a
   proper tight coalition, including boundary cases with no initially listed
   rooted proper row?
9. Is the monotone reduction in the cardinality lemma valid when `p,g,h,s`
   are atomic block multiplicities rather than role counts?
10. Does comparison--residual cancellation legitimately remove the need for
    an Lmin-tight comparison row, or is some earlier use of tightness hidden
    in the master identity?
11. Is the new seven-player control fully role-irreducible at the carrier
    cycle, and do the dual staged certificates and primal Z3 direction checks
    independently establish the displayed selectors within their stated
    shared-core boundary?
12. Does root-exclusion transport follow for every sign-coherent staged lift,
    including tied Lmin stages, without assuming unit-box coefficients?
13. What additional labelled Hall/congestion condition forces some
    cycle-containing tight support to satisfy `(CTS2)` without reintroducing
    the refuted full-root-block, cycle-only, or one-extra-player rules?
14. When the selected-support congestion condition fails, does the splitting
    Lmax packet necessarily expose an already classified mixed rooted-pair
    facet, or can a genuinely new indecomposable class occur?

No novelty or external validation is claimed.
