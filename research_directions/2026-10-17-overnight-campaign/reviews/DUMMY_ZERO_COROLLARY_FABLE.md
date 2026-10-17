**Provisional verdict: no load-bearing findings in reviewed scope.** The min2 Huber rule (1), its TCWM derivative proof, dummy characterization, and the pointwise report-adaptive representation all check out by hand; the min3 example arithmetic is correct. The most notable gap is evidentiary, not mathematical: the "accepted raw min3 integral price" formula is asserted, not derivable from the packet.

## Findings

**1. (Low) `DUMMY_ZERO_FINAL_GATE.txt` §3 lines 83–85 / `DUMMY_ZERO_FINAL_CHECK.py` line 59 — min3 price formula is unverifiable here.** The script only confirms `(1/5)·(1−1+1/3)=1/15`, i.e. the arithmetic of a stated integrand. Whether `(1/5)∫(1−t)²dt` is actually the resource-1 price of the accepted min3 rule at aggregate (5,1,1) is not shown in the packet. The negative conclusion ("netting + integral rule fails dummy-zero") depends on it. Verification: cite the specific rule file/formula and recompute A's payment from it.

**2. (Informational) Full-OUT dummy-zero for the logarithmic rule (lines 52–55) rests on argument only.** The script exercises only rule (1). The argument is sound: for V=0, r=0, p_A=c·r=0, and a pure-A dummy has b_i=0, so π_i=0; continuity at zero totals (cone file line 199) is consistent. No defect, but a small exact check of the log rule on the same grid would close the asymmetry.

**Verified items (no issues):**
- Identities: T=S+min(U,V); F(b(S))=f(S)+min(u(S),v(S)); total π=V(3/2−V/(2U))≤3V/2 ⇒ Σy≤3T/2. Coverage needs κ≥1 ✓.
- Derivatives: W=v+(u−v)V/(2U); W_u=V(U−u+v)/(2U²)∈[0,1]; W_v=1+(u−v−V)/(2U)∈[0,3/2] using v≤V≤U, u≤U. Restoration cases (W_u≥0 or 3/2−W_v≥0) correct; symmetric half-plane gives W_v≤1 so the 3/2 slack is not needed there. Continuity at U=V (p=q=1/2) ✓.
- Dummy characterization: pure-A dummy ⇔ all others a_j≥b_j (singleton necessity, summation sufficiency); then V=0, p=0, f_i=0 ⇒ y_i=0 ✓. Mixed-positive owners have positive singleton marginal, so "pure on one side" is right.
- Isomorphism to cone theorem: t=(a+b)/2, x=(a−b)/2 gives F=min(a,b), f_i matches, and homogeneity of prices turns κf_i+2∫π_i(u/2,v/2) into κf_i+π_i(u,v) ✓. Full-OUT contract matches cone line 9–10/§7.
- Min3 example: R-values 0,0,0,1 with and without A ✓.
- Script counts: 729·7=5103 covers; 729·6·(2/3)·4=11664 restorations; dummy checks 675 = 3·(81+72+72), matching the characterization independently (script uses raw marginals) — good corroboration.
- §2 representation is trivially correct (y_i>0 ⇒ non-dummy ⇒ some Δ>0); scope disclaimers (no boundedness/efficiency) appropriate. Consistency with Root 64: for r=2 the fixed-weight bound s/2 is unbounded in s, so rule (1) at 3/2 is correctly outside that class; no contradiction.

**Classification:** This is a routine corollary (dummy-zero property of an already-accepted sharp rule plus a tautological representation), not a new unrestricted rate improvement. The file states this correctly (lines 2, 74–75, 88–91).

## Scope limitations
- Did not run the script; counts verified by hand only.
- Lower bounds (root 3/2, energy 1+c, Root 64) trusted per instructions.
- The accepted min3 integral rule and the "scaled-Bernoulli r·n^(r−1)" claim are outside the packet.
- Did not re-audit the cone theorem's full-OUT inequality (8) beyond confirming it is invoked, not reproved, here.

## Verdict
**No findings in reviewed scope** (one low-severity evidentiary gap on the min3 price formula; no mathematical errors found).
