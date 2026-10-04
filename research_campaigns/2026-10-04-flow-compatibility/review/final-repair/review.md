**Provisional verdict: no material findings in reviewed scope.** The corrected proof of (M), the G01 certificate and the limited stopping conclusion all hold by hand-check; the verifier logic is sound by inspection. I executed nothing, and the reported pass counts are the coordinator's.

## Findings

**1. Low — wording of "tight-set closure" (MIXED_UNCROSSING_OBSTRUCTION.txt:64-67, 93-94)**
- The exhibited pair shows failure of closure under the *mixed* crossing only. Its ordinary intersection ({a1},{b3}) (worth 1, pay 1) and union (N, worth 5, pay 5) are both tight at z.
- The stopping conclusion survives, since (M) supplies only the mixed crossing.
- Suggested fix: say "mixed-crossed closure". If ordinary lattice closure is also meant, a different pair shows it by hand: ({a1},{b1,b3}) and ({a2},{b2,b3}) are tight, but their intersection (∅,{b3}) has pay 1 against worth 0.

**2. Low — model scope mismatch (lines 7-9 vs INSTANCES.json G04–G08)**
- (M) is proved for *public* middle arcs. In the registry and verifier, middle arcs of G04–G08 are players (256 = 2^8 coalitions).
- G01 has no middle arcs, so the certificate is unaffected, but the note should say (M) does not describe the registered G04–G08 games.

**3. Low — negative-control coverage (verify.py:173-176, 208-213)**
- The "incomplete without obstruction" branch has no control. By inspection `cases[:7]` would be rejected at line 160-162, but this is untested.
- Certificate controls touch only the protected certificate, hitting objective, floor and index range. Nothing exercises a dual-coefficient mismatch, a negative weight, or an ideal/endpoint certificate.
- This is a robustness gap, not a soundness gap.

**4. Informational — hash binding (verify.py:169-170)**
- The hashes show DISCOVERY.json is consistent with the current registry and script, not where it came from. This is harmless, because the verifier recomputes all values and optimality itself.

## Hand-checked and correct

- **(M) proof (lines 16-34):** U∩V and U∪V are valid cuts on the full vertex set. The source inequality a·u+a'·v ≥ (a∧a')max(u,v)+(a∨a')min(u,v) and its sink analogue hold in all cases. Middle-cut submodularity is standard, and weak duality closes the argument.
- **G01 (lines 53-65):**
  - z is efficient and in the core.
  - Both originals are tight (3 = 3).
  - Crossed worths are 3 and 1 against payments 5 and 1.
  - This agrees with DISCOVERY's sink witness [0,0,2,2,1] and the EXACT_FEASIBLE endpoint statuses.
- **Complemented form (lines 79-86):** complements are {a2,b2} and {b1}, bounds 2 and 2; the crossed sets are {a2} (0 ≤ 2) and {b1,b2} (4 ≤ 4); the bound total rises 4→6. The sign derivation is correct.
- **Logical scope (lines 3, 68, 94-96):** the note correctly separates failure of one proof technique from an insufficiency claim and from an endpoint counterexample.
- **verify.py, coalition values:** the flow is validated for capacity and conservation, absent arcs must carry zero flow, and the cut is recomputed separately and must equal the flow value.
- **verify.py, LP certificates:** `verify_lp` is a correct weak-duality certificate (nonnegative weights and floor prices, efficiency price free only when efficient, exact equality of primal, dual and stated objective).
- **verify.py, guards:** the prefix and obstruction-terminal checks are right, and `require` is used rather than `assert`, so `-O` strips nothing.
- **Spot checks:** the G01 ideal-0 and protected certificates, and the G04 protected dual (v(239) = 4), check out by hand.

## Scope limitations

- The raw delegate report was not supplied, so the counter-pattern at lines 73-75 is unverified.
- The literature attribution (lines 37-42) is unverified.
- Line 87-88 (column complementation gives no base polyhedron) is asserted, not proved; it is plausible and labelled as a sign transformation.
- I did not hand-verify cover feasibility over all 1440 coalitions, the remaining certificates, or any SHA-256 value.

## Verdict

No findings that undermine the claims in reviewed scope; three low-severity clarity and coverage items.
