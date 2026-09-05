# Request for specialist correctness and priority review

Proposed paper: **Sharp asymptotic separation of opposing egalitarian core selections**.
Author: Maxwell Flanagan. Draft dated 5 September 2026.

The attached manuscript proves that, over singleton-normalized exact TU
games with `n` players and positive total, the supremum `s_n` of normalized
L1 distance between full leximin and full decreasing-sort-minimizing core
allocations satisfies

\[
\lim_{n\to\infty}n(2-s_n)=2,
\qquad 2-s_n=2/n+O(\log n/n^2).
\]

The upper bound is a short convexity argument for arbitrary nonnegative
constant-total feasible sets. The lower construction is the minimum of
two additive games. Complementary coalition equalities force its **entire
core** to be a Fibonacci-parameterized segment, and both first optimal
faces are singletons. The construction covers all sufficiently large player
counts. No fixed-n attainment theorem or historical computational census
is required.

We would value an independent opinion on these concrete questions:

1. **Correctness:** Do the directional overlap witnesses, complementary
   coalition equalities, and matrix invertibility establish the stated
   universal bound and full-core realization without hidden assumptions?
2. **Selector convention:** Are the full individual-payoff sorting directions
   and the singleton-normalization scope unambiguous and consistent with
   the established literature?
3. **Asymptotics:** Does the all-integer-n parameter choice prove the exact
   first-order coefficient, rather than only a subsequence or a loose rate?
4. **Priority:** Is this coefficient or an equivalent distance theorem known?
   The revised packet credits the older bifocal framework, entire-core
   segments and Fibonacci–Isbell voting matrices. Is the specific sufficient
   embedding lemma subsumed by Rosenmüller’s finite MIN-game theory, or has
   this application of the known matrices already appeared?
5. **Significance and attribution:** Which parts, if any, merit an independent
   contribution claim? Which primary references and venue/audience should
   govern the presentation?

For a quick audit, read Theorem 1, Lemmas 2–3, and Proposition 4. The package
also includes `CLAIMS_AND_SOURCES.md`, recording a bounded source screen and
its access limits. Established selectors, exactness, and general
lower-envelope facts are not claimed as new.

The conventional proof has undergone internal adversarial review. The
portable exact verification command is

```sh
python verification/run_checks.py
```

It checks all coalitions for five small cases and an off-segment perturbation
control. Those checks corroborate the proof; they do not replace it. This
request does not assert that any human specialist has already reviewed or
endorsed the result. An adverse finding, a missing citation, or a conclusion
that the result is known or too limited would be useful.
