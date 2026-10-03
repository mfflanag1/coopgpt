**Provisional verdict: findings.** The U≠∅ formulation and the dual bound hold up on a by-hand check (nothing was executed), but three statements need tightening and two rest on assumptions outside the packet.

## Findings

**1. Medium — FORMULATION.md L7, L9: perfect P is unsound without the extra witness, and the box hides it.**
- With U=∅ and no witness the LP is unbounded.
- Counterexample: m=2, P={(a0,b1,c0),(a1,b0,c1)}. The four off-diagonal P entries (AB01, AB10, BC10, BC01) are unconstrained.
- If the generator still applies 0≤z≤1, it returns a spurious finite J=4+1−1=4, since the box is only valid when a witness exists.
- Correction: "Always include at least one witness; if U=∅, add one with zero objective coefficient, or reject. The box bounds may be used only when a witness is present."
- With the witness, U=∅ gives J≤0 trivially, because P is a matching of worth ≤1.
- Verify: the checker must reject a certificate for perfect P that lacks a witness block.

**2. Low/Medium — L5: the nonemptiness sentence is ambiguous and false under one reading.**
- "Assigning their value among their endpoints" fails if a triple's value is spread freely over its three players.
- Counterexample: m=2, w_AB,00=1, all paid to c0. Then (a0,b0,c1) has worth 1 and payoff 0.
- Correction: "split each diagonal pair entry between that pair's two endpoints."

**3. Medium — L5: "covers every coalition" assumes only full triples have worth.**
- If two-player coalitions earn their pair entry, constraints x_a+x_b≥w_ab are missing and the LP is a relaxation, not exact.
- "Strict" in REDUCTIONS.md L9 suggests the assumption holds, but the packet does not define it.
- Verify against the frozen hypotheses.

**4. Medium — L9: the refutation claim depends on facts outside the packet.**
- It needs s_3≥J(M,P) with floors H_i/3, and the witness market must satisfy every frozen hypothesis.
- REDUCTIONS.md L3–5 points to newer bounds elsewhere; the 2/5 upper bound is dated September 7.
- An exact J above the current proven upper bound should be treated as a pipeline bug, not a discovery.

**5. Low — L9, L11: certificate row identity is unspecified.**
- The solver may omit zero-worth triples while the checker rebuilds all |U|·m³ rows.
- λ must be keyed by (witness, triple), not row index; ν likewise by name.
- A variable shared by the diagonal and P (e.g. AB_ii in both) must be one variable, with coefficient 3 in c and one entry in the diagonal row.
- Verify with a P that shares a diagonal pair.

## Confirmed by hand (U≠∅)

- **Core equivalence:** a total-1 nonnegative cover of all triples forces diagonal optimality, and the witness set for fixed w is exactly the core under the assumption in finding 3.
- **Compactness:** x≤1, and each w_e≤1 through any triple containing it; the set is closed.
- **Exactness:** witnesses decouple and each has positive coefficient 1/3, so the LP maximum equals max over w of J(M_w,P), and it is attained.
- **Primal lower bound:** any feasible point gives x^i_i≤H_i, so its objective is at most J(M_w,P).
- **Dual bound:** c·z = r·z + λ·Az + ν·Bz ≤ Σmax(r_j,0) + Σν for any λ≥0 and free ν. It holds for any rationalised (λ,ν), so clipping negative λ to 0 is safe.
- **Empty P:** feasible, and J≤0 because diagonal triples are tight, so H_i≤v_i. For m=1 the value is exactly 0, which is a usable calibration.

## Scope limitations

No code, certificates, frozen hypotheses or CORE_COMPATIBILITY_UPPER.md were supplied. I did not check that the September code matches this text.

## Verdict

Findings. The formulation is correct for U≠∅ under triple-only worth; apply the corrections in findings 1, 2 and 5 and confirm the assumptions in 3 and 4.
