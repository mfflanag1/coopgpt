**Verdict: UNKNOWN.** I neither proved nor refuted the lemma in the time limit. I have a complete proof for the sub-case where the core equals the min-cut (Owen) hull, one explicit game showing why that proof does not extend, and the precise missing step.

**Read scope:** only the two supplied files. No web sources, no solvers, no file edits. All arithmetic below is hand-derived and should be rechecked.

## 1. Proved sub-case: core equals the convex hull of min-cut allocations

This covers all unit-capacity games, assuming the Kalai–Zemel "simple flow game" theorem (core = hull of min-cut allocations), which I cite from memory and did not re-read today.

- **Setup.** Each min cut δ⁺(U) gives the allocation x_e = c_e on cut arcs and 0 elsewhere. So H_e = c_e if e lies in some min cut, and H_e = 0 otherwise.
- **Lattice step.** Source sides of min cuts are closed under intersection and union (standard cut submodularity). Let U₀ be the intersection of all min-cut source sides; it is itself a min cut.
- **Source arcs.** An arc (s,u) lies in δ⁺(U₀) iff u ∉ U₀ iff u ∉ U for some min cut U iff (s,u) lies in some min cut. So the U₀ allocation attains H_e on every source arc at once.
- **Sink arcs.** The union U₁ of all min-cut source sides does the same for arcs entering t.
- **Scope.** No path-length bound is used, and parallel arcs are fine.

This lattice step is not circular, but it only works because every core vertex is a cut. It says nothing once the core is strictly larger than the Owen set, and I do not present it as a proof of the lemma.

## 2. Why the general case is different: H is neither the Owen maximum nor the marginal

Explicit game, all paths of length 2: source arcs a1 (capacity 3) and a2 (capacity 1) from s to v; sink arcs b1 (capacity 2) and b2 (capacity 1) from v to t. T = 3.

- v({a1,b1,b2}) = 3 = T forces x_{a2} = 0.
- Then {a2,b1} and {a2,b2}, each worth 1, force x_{b1} ≥ 1 and x_{b2} ≥ 1, so x_{a1} ≤ 1.
- The point (a1,a2,b1,b2) = (1,0,1,1) satisfies every coalition inequality: {a1,b1} gives 2 ≥ 2, {a1,b2} gives 2 ≥ 1, {a1,a2,b1} gives 2 ≥ 2, and the rest are slack.
- So H_{a1} = 1. The unique min cut is {b1,b2}, giving Owen maximum 0. The deletion marginal is T − v(N−a1) = 3 − 1 = 2.

So 0 < H < marginal. Any proof that goes through "min cut nearest s" or "marginals are attained" fails here. Joint attainment itself still holds in this game: (1,0) on the source arcs, and b = (1,1) on the sink side.

## 3. Hand-checked one-middle-vertex games (witnesses only, no refutation found)

In each case the source-side joint attainment holds, sometimes degenerately.

| Source capacities | Sink capacities | Core finding | Source H jointly attained? |
|---|---|---|---|
| {3,2} | {2,2} | x_{a1} = x_{a2} = p ∈ [0,1], each b = 2 − p | Yes, at p = 1 |
| {3,2} | {2,1,1} | core is the single point b = (2,1,1) | Yes, trivially (both 0) |
| {4,3} | {2,2,1} | x_{a2} = 0 forced | Yes |
| {3,3} | {2,2} and {3,1} | (1,1) on source arcs is feasible | Yes |

For that last row the feasibility of the joint point (1,1) is checked, but I did not separately verify that 1 is the maximum for each arc beyond the marginal bound.

Every attempt to make two source arcs trade off collapsed the smaller arc's H to 0. These are examples, not evidence of a theorem.

## 4. Two partial facts, and what a counterexample must look like

- **Marginals alone cannot obstruct.** With other arcs fixed, max-flow is submodular in the set of source arcs. So T − v(N−e1−e2) ≥ m₁ + m₂ ≥ H₁ + H₂.
- **Two disjoint coalitions cannot obstruct.** If A contains e2 but not e1, B contains e1 but not e2, and A and B are disjoint, then v(A) + v(B) ≤ T by superadditivity, so both constraints fit in the remaining T − H₁ − H₂.

A counterexample therefore needs overlapping coalitions sharing non-source players, at least a three-way interaction. It also needs non-integral or slack capacities, so the core is strictly larger than the Owen set. I did not find one. Length-3 cross-arc topologies with non-unit capacities (the F08–F10 type) are where I would look, and I did not analyse them by hand.

## 5. The precise missing proof step

Take core points x attaining H_{e1} and y attaining H_{e2}, with e1 and e2 leaving s. Needed: a core point z with z_{e1} = x_{e1} and z_{e2} = y_{e2}.

The natural construction takes the coordinate-wise maximum on source arcs and repairs the non-source coordinates so the total is T. That requires an additive w on the non-source arcs R with, for every R' ⊆ R and every set Q of source arcs:

  w(R') ≥ v(R' ∪ Q) − Σ_{e∈Q} H_e, and w(R) = T − Σ_{source} H_e.

So the missing step is to show that the reduced game g(R') = max_Q [ v(R' ∪ Q) − H(Q) ] on R has an additive majorant of total exactly T − H(source arcs), i.e. that g is balanced at that grand value. Asserting this directly is exactly as strong as joint attainment. That is the circularity; I stop that route here.

Submodularity in Q does not deliver it. The cut that determines v(R' ∪ Q) changes with R', so there is no single lattice to uncross over, unlike section 1.

## Limitations and unverified items

- No complete proof and no counterexample.
- Kalai–Zemel is cited from memory.
- I recall that core membership for general-capacity flow games is co-NP-complete (Fang, Zhu, Cai, Deng, c. 2002). If so, no simple closed form for H should be expected in general, though the length ≤ 3 class may be easier. This is recollection only and was not checked.
- Section 3 covers only one-middle-vertex (length-2) games.
