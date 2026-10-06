**Static review only — no tools were run, no files inspected on disk; line references to TWO_POOL_THEOREM.txt could not be verified and are treated as the candidate's claims.**

## Arithmetic verification of the counterexample

Rechecked by hand, k=r=2, N₁=(1,3/4), N₂=(1,1/2):

- Before: C₁=7/4, z₁=7/8, z₂=3/4. Own-pool term (1−7/8)(3/4)=3/32; outside term z₂/(k−1)=3/4. Average (3/32+24/32)/2 = 27/64 = 108/256. ✔
- After: C₁=15/8, z₁=15/16. Own-pool term (1/16)(7/8)=7/128; outside term unchanged 3/4=96/128. Average 103/256. ✔
- Drop of 5/256. ✔ Both endpoints have exactly two altered pools. ✔
- Derivative of c_i(1−(A+c_i)/r) is 1−(A+2c_i)/r. ✔

Coverage sketch: payment under R^j is ≥ (1−z_j)s + z_j·n ≥ min(s,n) since z_j∈[1/r,1]⊂[0,1]; the outside count bound ∑_{l≠j}|S∩N_l| ≥ n holds; auxiliary-to-actual monotonicity of v is correct. ✔ Budget identity R^j(N)=C_j(2−C_j/r) ✔.

The counterexample is exact, rational, and correctly refutes the precisely stated candidate.

## Findings

1. **Mislabelled relation to the existing boundary (needs correction).** The result says the candidate "uses … R^j when only j is altered" as if this were the existing one-pool rule. It is not. The theorem's R^j pays low owners a_h=(δ_h−z_h)₊/(r−h), whereas the generalized vector pays (1−z_h)/r. Example r=2, h=1: a₁=0 but (1−3/4)(1/2)=1/8. So the refuted candidate is a *new* rule that also alters the one-altered boundary, not an interpolation of the proven assignment. The obstruction remains valid for the rule as literally defined, but the framing "natural extension" overstates its connection to the frozen theorem. Say explicitly that the candidate does not reduce to the proven binary assignment.

2. **Budget not addressed.** For two altered pools, (R^j+R^l)(N)/2 ≤ C_j+C_l, which is not ≤ C·T uniformly (the non-minimal pool can have total up to r while T≥1). The result correctly makes no uniform-budget claim, but should state that even absent the monotonicity failure, this candidate would not meet the budget criterion.

3. **No scope inflation.** The closing paragraph correctly limits the conclusion to the equal-mixture generalized-R rule and leaves the real-capacity target open. The reading of the binary jump {1/r→1} as the load-bearing restriction is consistent with Lemma 3's structure as supplied (every edge advances h by one), though line numbers are unverifiable here.

4. **Depth.** The obstruction is essentially a one-line derivative observation on a candidate the author constructed; it supplies no structural reduction or partial positive result toward the target. Acceptable under the criteria's "or" clause, but thin.

5. checks.json is empty and changes.patch is empty — consistent with a pure research note; nothing to verify there.

## Verdict: **revise** (minor)

The exact counterexample is correct and precisely scoped. Required fix: remove the implication that the candidate preserves the existing one-altered rule (Finding 1) and note the budget gap (Finding 2). With those two edits this would be acceptable as a bounded negative result; it does not resolve the arbitrary-real target, which the note itself acknowledges.
