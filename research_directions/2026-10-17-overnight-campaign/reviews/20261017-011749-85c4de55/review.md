**Provisional verdict: no findings in reviewed scope.** I checked the derivative inequality (1), the cross-component cover step, boundary regularization, the residual-plan floor, and the rational/real transfers; each step is correct given the source Huber lemmas. The most important point to record is that the critical step does not depend on tight-edge structure of the withheld bundle at all: it only needs z to be a feasible cover of G, which Lemma 1/2 of the source guarantees.

## Findings

**1. (Verified, no defect) Derivative step, root lines 43–59.**
Component payment aB/A+b with a'=l, b'=h, A'=l, B'=h gives exactly (B/A)(1−a/A)l+(1+a/A)h; both terms ≥0 because 0≤a≤A, B>0, so ≥h. The KKT side-sum 2tA=B uses only tight edges, which stay inside the tight component (positive-λ edges are tight), so A,B are correctly component sums. z is a cover: a strict-low neighbor forces price >1/2 (feasibility); a half-price vertex’s tight neighbors are half-price; strict-high vertices have a tight low neighbor (Lemma 1), so every nonisolated vertex is classified. Hence derivative ≥ Σ_high d+Σ_half d ≥ z·d ≥ F(d) by weak duality on d over all of G, including cross-component edges. Integration across finitely many pattern points is valid since P(t) is continuous (p continuous, c>0) and rational with denominators A(t)≥min_v c_v(t)>0 on each piece.

**2. (Verified) Boundary, lines 66–77.** With c+ε1 all vertices are positive, so z covers all of G; a≤A_ε still holds; endpoint payments converge because a_v=0 wherever c_v=0 and q∈[0,1], while positive-coordinate prices converge to the unique induced minimizer (Lemma 5). No gap.

**3. (Verified) Floor, lines 80–91.** λ′≥0 since t≤1; vertex v uses ≤(1−t_v)Σλ_e≤c_v−b_v; loss Σλ_uv max(t_u,t_v)≤Σ_v t_v(Σ_{e∋v}λ_e)=Σ_v t_v c_v q_v=b·q, using the KKT identity Σ_{e∋v}λ_e=c_v h′(p_v)=c_v q_v (box multipliers vanish by interiority; h′(1/2)=1 both sides). Holds at zero coordinates trivially.

**4. (Minor, documentation) Line 20 “previously proved … lower”.** energy/PARTIAL_OUTSIDE_FLOOR_FRONTIER.txt lines 2–3 label itself “independent audit pending”. I re-derived its Section 3 (floor at boundary ⇒ X≥θ; OUT with F(d)=0 ⇒ monotone; coverage x_j+y≥1 averaged ⇒ y≥1−X/m; total ≥1+θ(1−1/m)) and it is correct, but the root should not cite it as “previously proved” until its audit status is updated. Note the lower bound needs the floor at a boundary profile; Section 4 of the root covers boundaries, so the match is legitimate.

**5. (Minor) Lines 103–110.** The real-weight limit needs the field OUT inequality at arbitrary (c,a,d) with a≤c; this is OUT with two owners (a and c−a), consistent with the source’s all-profile construction. Fine, but the root should state the two-owner instantiation explicitly as the source does for (i)–(iii).

## Suggested verification
Exact rational sweep on small nonbipartite graphs (triangle, K4, odd cycle plus pendant) with random mixed owners: check Σ_v c_v q_v=2F(c), OUT for all coalitions/withholdings including zero-capacity endpoints, and b_i·q≥F(c)−F(c−b_i); include profiles crossing low/high flips.

## Scope limitations
Tool-free; source Lemmas 1–5 and the weighted-lift identity accepted as audited inputs, not re-proved beyond the KKT and complementary-slackness steps I rechecked. Novelty and historical priority not assessed.

**Verdict: no findings in reviewed scope** (two minor documentation items, no mathematical defect or counterexample found).
