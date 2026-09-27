# Independent adversarial audit of the strict-chain theorem

5 September2026. Audited `/private/tmp/coopgt-pairadd-20260905/theory/CHAIN_FOLLOWUP.md`, SHA256 `dc97b0ba971213def771bba1cdfbd9b9ade48c1787820eb63b5abc9fbaaf7350`. This audit did not edit the candidate and does not establish novelty. No further random search or numerical census was used.

**Verdict:** no mathematical defect found in the stated entire-core theorem for complete strict-triple markets of equal sector size with `w_ijk=P_ij+Q_jk`, nonnegative matrices and positive integral total. The directed-cycle argument proves `H_i<=3x_i`, including fixed-zero players, and consequently bounds distance from full leximin to every core point by4/3. There is one wording refinement concerning two different notions of sharpness below.

## Checked proof obligations

1. **Integral grand value and labeling, candidate lines22–30.** Every strict triple matching projects to matchings in `P` and `Q`. Conversely independent optimal perfect matchings join through their common middle indices. Completeness, equal sector sizes and nonnegative entries ensure that partial matchings can be completed without loss. The two relabelings act independently on the outer sectors, so both selected matchings can be diagonal simultaneously. Their union value is exactly the integral grand value.

2. **Entire-core representation.** Summing diagonal triple inequalities at an efficient allocation forces each matched triple equality separately: every slack is nonnegative and their sum is zero. Substituting these equalities into triples `(i,j,j)` and `(j,j,k)` yields the two claimed differences. Adding those differences recovers each arbitrary triple inequality. Nonnegativity plus every triple inequality implies every coalition inequality by summing over each coalition's disjoint matching. Thus no larger coalition or hidden core face was omitted. A bilateral optimal nonnegative covering dual for each matrix gives a nonnegative triple covering allocation at the summed optimum, so nonemptiness is automatic under the stated matrix conditions.

3. **Potential and arc orientation, lines62–77.** With `q_Uj=u_j`, `q_Zj=-z_j`, the structural arc `Z_j->Z_k` has slack `Q_jj-Q_jk-z_j+z_k`, exactly the required inequality. The other structural orientation and all three player orientations also agree. Structural constants can be negative; the argument needs nonnegative *slacks*, not nonnegative constants. The matched-player arcs telescope to each fixed matched value, so potential perturbations automatically preserve the matching equalities and total efficiency.

4. **Cut perturbation, lines38–47.** For the backward-reachable set of the target's tail, an arc entering the set from outside would contradict its definition. Hence the0/1 direction is nondecreasing on the slack of every selected arc; the target slack strictly increases. Subtracting the anchor component fixes the anchor without changing any difference. All omitted structural constraints have strictly positive slack, and all omitted player payoffs lie strictly above the target level. Finiteness supplies one sufficiently small feasible step. The use of `<=alpha`, rather than `<alpha`, correctly protects every tied payoff. No player at or below the target level decreases, at least one increases, and every decreasing larger payoff stays above that level, giving a strict sorted lexicographic improvement.

5. **Disconnected, degenerate and fixed-zero cases.** Neither backward reachability nor the common anchor shift assumes connectedness of the selected graph. Zero-weight matched triples, zero bilateral matrices and repeated optimal matching choices cause no difficulty: the representation still holds and tight zero-player arcs enter the selected graph. At target level zero the resulting cycle has total constant zero; nonnegative slacks force the target to stay zero in every feasible allocation. No positive lower bound or strict interior assumption is being used. The excluded `T=0` case has only the all-zero core point; only normalized distance is undefined there.

6. **Simple cycle and player count, lines49–81.** A simple head-to-tail path cannot use the target arc: doing so would reach the tail before the path ends or repeat the head. Appending the target therefore gives a simple cycle. Structural arcs preserve the `U` or `Z` layer. Any cycle containing a player arc must pass from `Z` to `U` using one middle-player arc, then through the anchor using one first-sector and one third-sector arc. Another such transition would revisit the anchor, contradicting simplicity. Thus exactly three player arcs occur, even when the chosen target lies in an outer sector. Telescoping at any other feasible point gives the claimed upper bound because all structural slacks are nonnegative; they vanish at the leximin point. This justifies the uniform factor3.

7. **Full leximin and the distance implication.** Compact convex entire-core geometry supplies the unique labeled full leximin vector. The perturbation proof uses its complete sorted optimality, not just the largest achievable minimum. From `y_i<=3x_i` and nonnegativity, `min(x_i,y_i)>=y_i/3`. Efficiency then yields exactly `||x-y||_1<=4T/3`. The proof is stronger than a statement concerning only the opposite lexicographic selector.

## Explicit negative control for first-stage-only replacements

Take `m=2`, `P=[[1,0],[0,0]]`, and `Q=0`. The integral total is1. The entire core consists of

```
(u1,u2;v1,v2;z1,z2) = (t,0;1-t,0;0,0), 0<=t<=1.
```

Every core point is a first-stage maximin optimum because the four other players are fixed at zero. Yet `(1,0;0,0;0,0)` violates the proposed1/3 guarantee for player `v1`, whose ideal is1. The full leximin point `(1/2,0;1/2,0;0,0)` satisfies the theorem. This exact control confirms that the candidate's explicit full-lexicographic hypothesis is substantive and cannot be weakened to first-stage optimality.

## Sharpness wording to clarify

Candidate line16 says that the distance supremum need not be attained by one finite market. There are two distinct statements:

- **Distance to an arbitrary core point:**4/3 is attained in a finite chain market. For `m=2`, take `P_ij=1` and `Q_jk=0`. Every triple has weight1, `T=2`, full leximin is the six-coordinate vector with every entry1/3, and `y=(1,1;0,0;0,0)` lies in the core. Their normalized distance is exactly4/3. Every coordinate ideal is1, so the1/3 bound is sharp here too.
- **Distance between the two full lexicographic selectors:** the cited player-additive family has distance `4m/[3(m+2)]` and approaches4/3 as `m` grows. In the preceding constant-weight finite example the two selectors coincide, so that example does not settle attainment for the opposing-selector problem.

Recommended refinement: say explicitly that the arbitrary-core distance constant is attained already in a finite market, while the displayed family proves the opposing-selector supremum4/3 by a limit. No core theorem or proof needs alteration for this distinction.

## Scope of acceptance

The proof establishes the chain-class bound, not a bound for cyclic pair-additive matrices and not a general classification of interaction structures. The sparse cyclic counterexample invalidates1/3 outside the chain subclass, but leaves open every smaller universal positive constant and the cyclic-class4/3 distance question. The network-slack max-min certificate may be classical or a direct specialization of earlier results; priority review remains separate from this correctness verdict.

## Coordinator response

The finite-attainment distinction was corrected in the opening statement, and a targeted primary-source comparison added explicit attribution to classical partial slack balancing. The mathematical proof body was unchanged. Current proof SHA256: `62353e40c8c5510dcdbadc0460378c56163f2dfb1998e7daa32fb5a79e007152`. This response is by the coordinating agent, not a new external review.
