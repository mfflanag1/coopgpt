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

Remaining case: a proper coalition with at least three members and a failure
dual with at least three distinct residual levels. This is now the only
capacity-versus-slack case needing a new face construction.

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

## Bet 4: symbolic certificate discovery

src/mine_symbolic_invariants.py is an exact, single-instance invariant
extractor. It records:

- exact leximin strata;
- tight coalitions classified as inside, outside, or crossing \(S\);
- exact star value and residual-cover dual;
- residual level count and minimum-residual class;
- exact capacity, limiting faces, and all face certificates;
- minimum global and inside-\(S\) certificate sizes;
- the face predicted by the two-level theorem.

This deliberately replaces broad frequency summaries with proof objects. The
default six-player run recovers the pair certificate above exactly.

## Current breakthrough boundary

The original hoped-for global leximin selection theorem is false because of
the grand-coalition counterexample. The proper-coalition program remains alive
and is now concentrated on two independent gaps:

1. construct a face certificate for three-or-more-level failure duals;
2. prove the parametric path lemma after the star condition is available.

The finite-family program is independent of that failed selector and remains
concentrated on disjoint nonsingleton two-arm stars.
