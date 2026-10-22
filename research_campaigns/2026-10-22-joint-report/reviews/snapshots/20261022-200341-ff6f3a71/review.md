**Provisional verdict: no substantive findings in reviewed scope; one precision gap in the written proof (trivially repairable), no missing hypothesis found.**

## Findings

**1. (Low) root/UNRESTRICTED_RESUME_GATE.txt lines 59–70 — the proof as written establishes attainment at B\*, but not the stated "reverse inequality".**
The intervals are taken as [0, B\* T_p] and the FIP argument uses beta(P) ≤ B\*. Let B' = sup_P beta(P). The easy direction (line 55) gives B' ≤ B\*. To prove B\* ≤ B', the product must be built from [0, B' T_p], using beta(P) ≤ B' — which holds identically, so the same argument goes through verbatim. As written, the step concludes only "there is a global rule with factor B\*", i.e. attainment, and then asserts "the reverse inequality" without the substitution. Suggested fix: replace B\* by sup_P beta(P) in lines 59, 65–67, then conclude B\* ≤ B' and hence equality plus attainment. No change to any bound.

**2. (Informational) Line 52–53 disclaimer is correct and necessary.** Tychonoff over an uncountable product (all real profiles × owners) uses choice; the resulting rule is a pure existence object. The text correctly claims neither algorithm nor measurability.

**Checked and found correct:**
- Zero technology: all v_p(S)=0, so every beta(P)=0 and B\*=0; intervals degenerate to {0}; zero rule feasible (lines 57–58). Non-zero f: at a profile with T_p>0, coverage of N forces beta ≥ 1 (line 57). Upper n via x_ip = T_p, own-monotone since T_p is monotone (line 56; theory file line 20).
- Closedness: coverage, own-monotonicity (x_i(a_i,b_-i) ≤ x_i(b)), and budget are finite linear inequalities in finitely many coordinates, hence closed cylinders; T_p<∞ gives compactness (lines 59–63). Monotonicity constraints on T_p=0 profiles are consistent since v_p(S) ≤ T_p = 0.
- FIP step: any finite constraint set names a finite P; the LP on P with all comparable within-P pairs covers every named constraint; x_ip ≤ beta(P)T_p ≤ B'T_p keeps the point inside the product; zero elsewhere is harmless because unmentioned coordinates are unconstrained (lines 63–68).
- Finite LP attainment: beta∈[0,n], x_ip∈[0,nT_p], nonempty compact feasible set, continuous objective (lines 64–65).
- Route A quantifier (line 19, "EVERY such finite P"): correct — a uniform dual bound gives beta(P) ≤ g for all P via strong duality, hence B\* ≤ g by the bridge. Transport form (lines 13–16) matches theory/dual_flow_formulation.txt lines 24–26: same owner, same-others fiber, p_i ≤ q_i, source equality, sink capacity ≤ mu_q. The Hall/upper-set derivation there (lines 30–33) is sound: for an upper set U, within-U flow cancels, no flow leaves U, so Σ_U ell ≤ Σ_U mu.

## Scope limitations
Snapshot only; no tools run. I did not verify the claimed existing rates, the owner/dimension lower bounds, or any route B/C material. I did not reprove the dual sign derivation beyond spot-checking the upper-set inequality.

## Verdict
Findings (one low-severity write-up imprecision, finding 1). The bridge is otherwise a correct standard FIP/Tychonoff argument with the stated hypotheses sufficient; route A's quantifier and transport constraints are correctly stated.
