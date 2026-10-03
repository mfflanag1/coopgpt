## Verdict: no mathematical error or counterexample found in reviewed scope

The findings below are proof-completeness and verification-coverage issues only. I re-derived every step by hand and executed nothing.

**Most important finding:** the third-cut step that sharpens T/3 to (T-1)/3 is correct on paper but has zero computational coverage.

## Findings

**1. Medium (coverage) — `verify_initial.py` 48–113 vs `UNIT_FLOW_BOUND.txt` §2–5**
- `flow_case` builds only the chain family for n = 1, 2, 3, and certifies a hand-chosen `y` (lines 99–101), not y = max(z, H/3).
- Nothing exercises S0/S1, the rerouting lemma, r ≤ T, or the K2 construction.
- No instance has parallel arcs, paths of length 1 or 2, unused arcs in a minimum cut, or r < T.
- The 2312 coalitions support equality at T ≤ 3 only, not the upper bound.
- Verification: brute-force small random DAGs with path length ≤ 3, including parallel arcs. Compute H and s by exact LP, assert s ≤ (r-1)/3, and assert all H = 1 arcs outside K0 ∪ K1 are middle arcs.

**2. Low–Medium (proof completeness) — `FOUR_SECTOR_BASELINE.txt` 50–53**
- "LP duality after y=H/K+z" skips the reduction from coalition dual weights to full-team packings.
- It is fillable: replace each coalition S by the teams of an optimal packing; since H ≥ 0, the objective v(S) − H(S)/K does not decrease and loads do not increase.
- The dual value is then max V/K − T, which should be written out.
- W ≤ T at k = 0 (line 45) also silently uses a nonnegative core point.

**3. Low (scope) — `FOUR_SECTOR_BASELINE.txt` 6**
- The "approved strict full-team nonnegative pair-additive model" and s_(1/K) are not defined in the packet.
- My confirmation assumes one player per sector per team, team value equal to the sum of nonnegative pair values, and coalition value equal to the best disjoint team packing.
- This file has no computational check at all.

**4. Low (coverage) — `verify_initial.py` 116–146**
- The assignment check verifies core membership, H and one coupling control.
- It does not assert the claimed minima (0,0,0;0,5,0), the exact core description, or leximin optimality and uniqueness.
- The last is disclosed as analytic.
- Negative controls are a single damaged vector per case and never test `certify`'s witness or lower-bound branches.

**5. Low (stale text) — `FLOW_CHAIN_CANDIDATE.txt` 30–32, `UNIT_FLOW_BOUND.txt` 2**
- Both still refer to a "T/3" conjecture or proof and "does not prove that upper bound".
- Reconcile with the (T-1)/3 theorem to avoid misciting.

## Confirmed by hand

**UNIT_FLOW_BOUND**
- **§1:** cut indicators are core points, H_e ≤ f_e, and H_e = 1 iff e lies in a minimum cut (the reinsertion argument is valid).
- **§2:** S0 ⊆ S1, both are residual-closed, both cuts have capacity T, each flow path crosses each once, and k ≤ l.
- **§3:** R0 avoids P in both directions. The case split is exhaustive because k ≤ 3. The augmented flow has value T and is zero on e1..e_(k-1). The reversal is legitimate.
- **§4:** an arc in B needs k < j < l, so k = 1, j = 2, l = 3, giving at most one per path and r ≤ T.
- **§5:** z is a core point, the uncovered positive-ideal arcs lie in B\{e}, and the total is T + (r-1)/3 at most. The r = 0 case is fine.
- **Unequal-capacity example:** the (2,2,1) arithmetic is right and correctly scoped; it neither proves nor refutes C2.

**Chain family**
- T = n. The S_i boundary is {a_j : j < i}, b_i, {c_j : j > i} with capacity n, and no d_j leaves S_i.
- Lower bound: n-1 + (n+2)/3. Upper allocation total: n + (n-1)/3.
- Path coverage implies coalition coverage in the unit case.
- Equality holds for every n ≥ 1, including n = 1 with subsidy 0. Here K0 is the a-arcs, K1 the c-arcs, and r = n.

**FOUR_SECTOR_BASELINE**
- **Coefficient counts:** (K-1) on d, (K-1)(K-2) on u, and K·ΣH − ΣH^Σ are correct. The H coefficient Σ_(b≠a) q_(b,j) is correct.
- **Repeated labels:** harmless; the differences are 0 ≤ u.
- **(A) and (B):** (A) gives (3K-4)T. (B) needs only q ≥ 0, k ≥ q_i and x ≥ 0.
- **Weights:** they sum to 1, beta cancels, and the T coefficient is K + 2(K-2)/(K-1).
- **Strictness:** it holds in all three cases: C2 > 0; C2 = 0, which forces beta = 0; and k = 0.
- **Integral variant:** the weights sum to 1 and beta cancels using C2 = beta. This gives 2(K-2)(k-1)T/[K(k(K-1)-1)], which is (k-1)T/(3k-1) at K = 4.
- **Budget B variant:** the arithmetic checks.

**GEOMETRY_BRIDGE**
- T = 14 for both games. The cores are 0 ≤ p ≤ 4, 0 ≤ q ≤ 5, with q − p ≤ 1 added for B.
- Maxima (4,5,0;4,10,0) and minima (0,0,0;0,5,0) are identical.
- Leximin forces p = 2. A then gives (2,5,0;2,5,0) and B gives (2,3,0;2,7,0), each unique.

**Verifier code**
- Coalition count: 8 + 128 + 2048 + 64 + 64 = 2312. Controls: 3 + 0 + 1 = 4.
- Operator precedence in the mask expressions is correct, and `require` raises, so `-O` does not disable checks.
- The cut-enumeration and path-packing values are computed independently.
- `certify` soundly pins the exact subsidy, given the deletion cap plus an attaining witness.

## Scope limitations

- The model definitions for the four-sector file and the Vazirani citation are not in the packet.
- The claimed PASS output was not supplied and is not confirmed.
- The file header attributes the original T/3 proof to "Fable". I am a Fable-family model, so treat my independence from that author as limited.
- General rational-capacity C2 remains unresolved, and nothing here bears on it.
- No novelty assessment was made.
