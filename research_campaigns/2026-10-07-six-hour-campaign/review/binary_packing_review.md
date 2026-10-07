**Provisional verdict: no findings in reviewed scope.** The most important observation is a coverage gap rather than an error: the Section 5 application claims (simple-path technologies on cyclic directed graphs, multicommodity terminal pairs, "dual vertices = minimal structural cuts") are not exercised by any test technology in `binary_packing.py`; all eleven specifications are abstract small clutters.

## Findings

**F1 (Low, scope) — Section 5 untested.** `binary_packing.py:362-374` contains no technology built from s–t simple paths of a cyclic digraph or from multicommodity terminal pairs. The claim at `BINARY_PACKING_EXTENSION.txt:101-104` (vertices of Q are exactly minimal-cut indicator vectors) is argued only by a one-sentence sketch. I checked the argument independently: recession cone of Q is the orthant, so every vertex is the unique minimizer of some nonnegative objective, hence coincides with an integral min cut; conversely a minimal cut C with objective 1 on C and large M elsewhere is uniquely minimized at 1_C (minimality gives a path meeting C only at each e). The sketch is correct but should be written out. Verification: add a 3–4 arc cyclic digraph with path recipes and compare enumerated dual vertices to the minimal cut list; add one 2-commodity instance with a fractional vertex.

**F2 (Low, scope) — Clutter restriction in tests.** `Technology.__init__` (line 132) rejects non-clutter families, while the theorem admits arbitrary nonempty families. Nothing in the proof uses the clutter property, but nested recipes are untested. Verification: drop the clutter `require` for one technology such as `((0,),(0,1))`.

**F3 (Info) — Degenerate K=1 wording.** Line 30 states `(e+o(1))F log K`, which is 0 at K=1; the text correctly defers to the explicit bound (1) of the Bernoulli file, which is positive at K=1. No error, but the headline form should say "for K≥2" or cite (1).

## Checked and found sound
- Vertex bound 0≤w_e≤1 (lines 22-25): correct; relies on w≥0 making all e-containing covers strictly slack.
- D_e via restricted duals (`effective`, line 158-163) equals max usage because non-e recipes only consume; cross-checked by independent primal enumeration (line 302-317).
- Polytope identity (2) and strict-support (3): mixture argument valid; verifier checks both at reports {1/3,1,2,5/2} against u=5/2.
- Conditioned-zero invariance (lines 60-68): increment decomposition is exact; verifier checks the whole family and the exact characterization (lines 284-289).
- Domination (lines 71-76): the two optimality inequalities hold for *any* optimal pair, so the verifier's stronger all-optima test is legitimately implied.
- Coverage: weak duality on D·1_S, correct.
- Budget: a_e∈[0,1] holds; unmasked min = F(D)=T by (2); Chernoff/convexity/tail integration consistent with the audited Bernoulli file.
- Circularity: dual and primal vertices are enumerated from active-constraint subsets independently (`solve_square`), F is compared across both; `require` is exception-based, so `-O` does not disable checks (confirmed by calibration at lines 339-344).

## Scope limitations
Cannot execute; relied on reported 573/191 counts. Instances are n≤5, ≤5 recipes, two q values; asymptotic coefficient e is analytic only. No test distinguishes circulation-based from path-packing D on cyclic graphs (the warning at lines 105-107 is prudent but unverified numerically).

## Verdict
No findings in reviewed scope; two low-severity coverage gaps (F1, F2) recommended before closing the audit.
