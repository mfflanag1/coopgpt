**Provisional verdict: no invalid step found in reviewed scope; two definitional gaps (minor).** Most important: SCALE_ENVELOPE's headline ("cannot satisfy C·U(K)·T") is only an obstruction if U(K)=o(K), and U(K) is never defined in the packet.

## Findings

**1. (Low) SCALE_ENVELOPE_OBSTRUCTION.txt lines 16, 53 — U(K) undefined.** The lower bound 5K/8 is correctly derived (I rechecked (1)–(4): g_j−g_i=(j−i)²/4K², g_i=1−(K−i)²/4K²≥3/4, variance ≤1/12N+1/48KM, Chebyshev total exactly 1/12K+1/12≤1/6, strict win on the complement since mean gap 1/8K²=2η). But the conclusion is vacuous if the single-scale budget U(K) is itself Θ(K). Verification: cite the uniform-tail lemma and its growth rate.

**2. (Low) SCALE_ENVELOPE line 29 vs scale_envelope.py line 15.** Text uses b_j/N ≤ r_1/2 (needs N ≥ 4K²M; holds with equality, N=256K⁶=4K²·64K⁴). Script only asserts b_j/N ≤ r. Harmless, but the script does not check the stated inequality. No check of the probabilistic claim (acknowledged in `scope`).

**3. (Info) ANTICHAIN_REDUCTION §1 bypass-path argument is valid but compressed.** The written proof needs two unstated facts: (a) every vertex of G_A is "before" or "after" some A-edge (vertices on an A-path are before/at-tail or at-head/after that edge), and (b) s is before-only and t after-only (s has no in-edges, t no out-edges). With these, the transition edge of any s–t path in G_A goes from a before-vertex to an after-vertex; if it were not in A, its membership on an A-path forces either its head before or its tail after some A-edge, giving a vertex both before and after → two A-edges on one path or a cycle. Correct. Also R(A\{e}) = maxflow of G_A−e holds because paths of G_A avoiding e still meet A\{e}.

**4. (Info) Endpoint-marginal vs full mincut distinction (ANTICHAIN_REDUCTION lines 26–31, 70–71).** Correctly handled: the local cut C0 excludes e and blocks every e-containing path, so flow on e-paths in any max flow ≤ Σ_{h∈C0} D_h U_h, mean ≤R(A)/2. This avoids the invalid claim B_e ≤ score(C0). The hinge (line 47) is correct: single-edge maxflow is min(B, A+t) with R(A\{e})=min(A,B), so it equals min(R(A), R(A\{e})+t). Disjointness of C* from A and the joint-profile cut inequality Y(B)+R(A\B) ≥ Y(A) > R(A) check out.

**5. (Info) CONSTANT_VALUE_CROSS_OBSTRUCTION — arithmetic verified.** q_h = 5/6 + h/12(1+h)² (using 2+3h+2h² = 2(1+h)²−h); q_1−q_{.1}=27/1936; Var(Rscore)=147/16N; Chebyshev 49/27N; (0.9)^100≈2.66e−5<1/30000; 27/1936−1/2000 = 1627/121000. Cut enumeration and effective caps (D_b=1+h) correct. The refutation is sound and scoped correctly (does not touch endogenous joint-y-target condition).

## Unverified dependencies
- z_e as expected endpoint marginal E min(d,(B−A)_+), y_e attainment, D-preservation of flows, "y=z on TTSP": all from CONTRACT.txt / DAG_BASELINE.txt, not supplied.
- "Conditional clamp" monotonicity underlying SCALE truthfulness (line 10) accepted as dependency.

## Scope limitations
Static review only; no execution of scale_envelope.py; no simulation of the ≥5/6 win probability or z_e(h) values.

## Verdict
**No findings of invalid steps in reviewed scope.** Findings 1–2 are presentation/definitional gaps that should be fixed before the Ω(K) obstruction is cited.
