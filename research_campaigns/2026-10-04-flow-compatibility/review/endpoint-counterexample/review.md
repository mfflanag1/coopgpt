**Provisional verdict: no findings in reviewed scope.** I re-derived every step of the note by hand and found no invalid step or counter-coalition; the refutation holds as written, given that parallel arcs are in scope. Nothing was executed.

## Findings

No correctness findings. Two minor presentation notes (Low):

- **Lines 86–90:** "eight subsets" yield seven identities because PGM only defines k0. The note says this; no error.
- **Lines 68–69:** z_i ≥ 0 for the other sources is weaker than what the deletion argument gives (z_i ≥ 1). Harmless, since the bound is unused.

## What was manually checked

- **Data:** a and b each sum to 98; capacities total 197 and 196; T = 196; U and V each total 196.
- **No-subset-sum-61 lemma (lines 38–45):** C0 totals 153 and D0 totals 40. D0 has no subset summing to 2, 7 or 10, hence none summing to 38, 33 or 30. The case split on the two 31s, 28 and 23 is exhaustive. The corollary for 92 = 153 − 61 and the "A and B both or neither" consequence follow.
- **U and V in the core:** worth is min(2a(S)+δ, 2b(R0)).
  - For d ≤ −1 the source side binds strictly; U's slack is −d−δ ≥ 0 and V's is −d−1_A ≥ 0.
  - For d ≥ 1 the slacks are d and d+1_B−1_A ≥ 0.
  - For d = 0 the map W = S ∪ (sinks∖R0) has weight exactly 98, so the lemma gives V slack 0.
  - Signs and the complement map are correct; degenerate coalitions are covered.
- **Loss variables:** (E) is correct, and z_P ≥ 1 follows from deleting P.
- **Tie identities:** the coalition and its complement have worths summing to 196, so both are tight, giving z(S) − t(R0) = 1_B. With {A,B} ∪ K this gives θ(K) = p+g+m.
  - All eight weight-55 sums are correct.
  - All seven identities and the solution (I) are correct.
  - θ(C0) = −4p+19q+20r and Σt = 12q+13r−3p, so (II) and (III) hold.
- **Weight-54 inequalities:** d = −1 gives worth c(S) even with B present, so θ(W) ≤ Σt and (L) holds.
  - K1 has weight 54 and θ(K1) = 8q+6r, giving r−q ≥ p+1.
  - K2 has weight 54 and θ(K2) = 5q+8r−p, giving r ≤ 2q−1.
  - Together these give q ≥ p+2 and r ≥ 2p+3.
- **Individual ideals:**
  - {B,M,L,P} has weight 97 and gives α ≥ r+1 ≥ 6.
  - {A} ∪ C0∖{M,N} has weight 97 and gives β ≥ −p+4q+5r+1 ≥ 37.
  - g ≥ 23, m ≥ 31 and p ≥ 1 follow from (I) and (B).
  - U attains the bounds for P, A, G, M and V attains B, so H_source = (1,6,23,31,38), summing to 99.
- **Source support:** Σz ≥ 35p+64 ≥ 99, since the coefficients of q and r are positive, so the maximum source total is 98, attained by U. Also α+β ≥ 44, so x_A + x_B ≤ 43 < 44.
- **Sinks:** H_j ≤ c_j, and (0; c_sinks) is in the core.
- **Real-valued bridge:** no payoff integrality is used anywhere. Integrality enters only through the weights (d ∈ ℤ and the subset-sum lemma), which is legitimate.
- **C2 distinction:** U is an efficient core point with U ≥ H/3 coordinatewise (37 ≥ 38/3; b_j ≥ c_j/3), which supports s_(1/3) = 0.

## Scope limitations

- The exact definitions of s_(1/3) and of "source-ideal core point" are not in the packet. I assumed the standard readings: the minimal subsidy making x ≥ H/3 core-feasible, and a core point giving every s-incident arc its ideal H_e.
- The example needs parallel arcs. Its validity against the frozen target rests on the CONTRACT clarification (lines 34–37). The obvious subdivision into a simple DAG adds players and is not covered here.
- Not checked: the Isbell citation, novelty or priority, and consistency with the registered solver cases. An independent exact LP check of the five source ideals and the support value 98 would be a cheap confirmation.

## Verdict

No findings in reviewed scope.
