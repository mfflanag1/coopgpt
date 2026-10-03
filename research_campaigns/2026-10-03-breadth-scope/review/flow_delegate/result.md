# C2 independent report: positive subsidy exists; s ≤ T/3 proved for unit capacities only; general capacities UNKNOWN

No universal-zero theorem holds: there is an exact 7-arc witness with s = 1/3 = T/6. For unit capacities I have a complete proof that s ≤ T/3, and an exact family with s = (T−1)/3, so no constant below 1/3 works. For general rational capacities C2 remains unresolved, with a precise obstruction. Everything below is hand-derived; no solver was run, no source was consulted, and nothing here is a novelty claim.

## 1. Exact witness of positive subsidy (unit capacities, T = 2)

- **Network:** nodes s, u1, u2, w1, w2, t. Arcs, all capacity 1: a_i = s→u_i, b_i = u_i→w_i, c_i = w_i→t (i = 1, 2), and d = u2→w1.
- **Paths:** the only s–t paths are P1 = {a1,b1,c1}, P2 = {a2,b2,c2}, Q = {a2,d,c1}, all of length 3.
- **Worth:** v(S) = 2 iff S ⊇ P1∪P2 (the only arc-disjoint pair); v(S) = 1 iff S contains some path but not P1∪P2; otherwise 0. So T = 2.
- **Entire core:** x ≥ 0, x(N) = 2, x(P1) ≥ 1, x(P2) ≥ 1 force x_d = 0 and x(P1) = x(P2) = 1. Hence C = {x ≥ 0 : x_d = 0, x(P1) = 1, x(P2) = 1, x_a2 + x_c1 ≥ 1}.
- **H:** H = 1 on all six a, b, c arcs and H_d = 0. Witnesses, each paired with any one of the others:
  - on P1: x_a1 = 1 or x_b1 = 1 needs x_a2 = 1; x_c1 = 1 works with anything on P2;
  - on P2: x_b2 = 1 or x_c2 = 1 needs x_c1 = 1; x_a2 = 1 works with anything on P1.
- **Lower bound:** the floors are 1/3 on six arcs. Any feasible y has y(Q) ≥ 1 and y ≥ 1/3 on b1, a1, b2, c2, so y(N) ≥ 1 + 4/3 = 7/3.
- **Attained:** y ≡ 1/3 on all seven arcs gives every path weight 1 and P1∪P2 weight 2.
- **Result:** s = 1/3 = T/6 > 0, exactly.

## 2. Exact family with s = (T−1)/3

- **Network:** for i = 1..T take a_i, b_i, c_i as above, plus d_i = u_i→w_{i+1} for i = 1..T−1. All capacities are 1.
- **Paths:** P_i and Q_i = {a_i, d_i, c_{i+1}}, all of length 3.
- **Entire core:** x ≥ 0, x_d = 0, x(P_i) = 1, x_{a_i} + x_{c_{i+1}} ≥ 1. Sufficiency holds because any coalition's integral max flow splits into arc-disjoint paths, each of x-weight at least 1.
- **H:** H = 1 on all 3T path arcs and 0 on the d arcs. Witnesses: all a = 1; all c = 1; for b_i take b_i = 1, a_k = 1 for k < i, c_j = 1 for j > i.
- **Lower bound:** the Q_i are pairwise disjoint, and T+2 floored arcs (all b_i, a_T, c_1) lie outside them. So y(N) ≥ (T−1) + (T+2)/3 = (4T−1)/3.
- **Attained:** y ≡ 1/3 on all 4T−1 arcs.
- **Result:** s = (T−1)/3, so s/T → 1/3 from below. The bound T/3 is asymptotically tight here; whether s = T/3 is ever attained is unresolved.

## 3. Theorem (unit capacities): s ≤ T/3

**Statement.** For a DAG with multi-arcs allowed, all capacities 1, and every s–t path of at most 3 arcs, the least subsidy at floors H/3 (H taken over the entire core) is at most T/3.

**Proof.**

1. Fix an integral max flow f, decomposed into T arc-disjoint paths. Let S0 be the set of nodes residual-reachable from s, and S1 the complement of the set of nodes that residual-reach t. Then K0 = δ⁺(S0) and K1 = δ⁺(S1) are min cuts with S0 ⊆ S1.
2. The indicators 1_K0 and 1_K1 are core points, since K∩S is a cut of S's subnetwork. So x = ½(1_K0 + 1_K1) is in the core.
3. Put y = max(x, H/3). Then y ≥ x covers every coalition, and the cost is at most Σ_{e ∉ K0∪K1} H_e/3, because x_e ≥ 1/2 ≥ H_e/3 on K0∪K1.
4. H_e ≤ f_e (the coordinator's control argument), so only flow arcs can pay.
5. Each flow path P = (e_1, …, e_m), m ≤ 3, with nodes n_0 = s, …, n_m = t, crosses K0 exactly once, at e_k say, and K1 exactly once, at e_l with l ≥ k.
6. **Claim:** H_{e_j} = 0 for j < k.
   - Take a simple residual path R from s to n_{k−1} ∈ S0.
   - R uses no forward arc of P, since those are saturated.
   - R uses no reverse of e_j for j ≥ k, since the tail n_j lies outside S0.
   - R does not use the reverse of e_{k−1}, since that leaves the endpoint n_{k−1}.
   - The only other reverse arc (k = 3, j = 1) enters s, which a simple path from s cannot do.
   - So R avoids P. Delete P's unit of flow and augment along R followed by e_k, …, e_m. This gives a flow of value T using none of e_1, …, e_{k−1}.
   - Hence v(N∖e_j) = T and H_{e_j} ≤ T − v(N∖e_j) = 0.
7. Symmetrically, by reversing the graph, H_{e_j} = 0 for j > l.
8. So on each flow path the only arc that can pay lies strictly between e_k and e_l. There is at most one such arc, and it pays at most 1/3. Therefore s ≤ T/3. ∎

**Whole core versus Owen set.** The proof uses only that two min-cut (Owen-set) points lie in the core, and it bounds H over the entire core via H_e ≤ T − v(N∖e). It does not use the remembered result that the core equals the hull of min cuts for unit capacities, which I did not verify against a source.

## 4. General rational capacities: UNKNOWN

- **Where the proof breaks.** Step 6 gives only H_e < f_e, not H_e = 0, when capacities differ. Arcs on the source side of K0 can carry positive whole-core H.
- **Concrete illustration.** A single path with capacities (2, 2, 1) has T = 1, core equal to the simplex, and H = (1, 1, 1). The only min cut is arc 3. The construction max(x, H/3) with x the Owen point costs 2/3, yet the true s is 0, with y = (1/3, 1/3, 1/3) a non-Owen core point.
- **What is missing.** A proof needs core points outside the Owen set, or a direct y certified by a length function with y(S) ≥ v(S). I found neither.
- **Why splitting does not help.** Replacing a capacity-c arc by c unit arcs changes the player set, the core and H, so it is not a valid reduction.
- **No counterexample found.** A refutation needs a dual certificate above 4T/3. Since ΣH/3 ≤ T always, that means path or coalition deficits totalling more than T/3. In my unit constructions, cyclic cross-links force H_b = 0, which caps the deficit at (T−1)/3. I did not find a capacity gadget that evades this.

## Limitations

- The supplied coordinator checks cite Gangam et al. 2403.06037v3 and Vazirani 2402.11437v6; I did not open either, so those citations and the published nonempty-core baseline remain unverified by me.
- The unit-capacity proof and both examples should be re-derived independently before any campaign claim. The family in section 2 is a symbolic derivation, not a solver-certified instance.
