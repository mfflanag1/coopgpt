**Provisional verdict: no blocking findings in reviewed scope.** Most important concrete finding: the five negative controls never exercise the soundness-critical checks (`uncancelled positive payment coefficient`, `positive budget coefficient`); all five are caught by schema/range validation before any arithmetic runs.

## Findings

**1. Medium — controls do not test the cancellation logic** (`verify.py:62-77`)
Mutations are: negative weight, bad histogram sum, claimed-bound +1, cover count `m+1`, mono `h=m`. Each raises before or independent of the summation at lines 52-53. A certificate corrupted so that a payment coefficient becomes positive (the one failure mode that would admit a false lower bound) is never tested. Verification: add controls that (a) raise `rows[3]['weight']` from `1/3` to `1/2` (leaves `a_((1,2,0),1)` at `+1/3`, must reject with `uncancelled positive payment coefficient`), and (b) delete all `budget` rows (must reject with `positive budget coefficient`).

**2. Low — cover rows with `(a,b)=(0,0)` for a present type are accepted** (`verify.py:39-44`)
ENCODING §Coverage says a coalition takes members from *each* pool; the verifier permits taking nobody from some type. This is sound (min cap becomes 0, RHS 0, row trivially valid) but is an undocumented widening of the row class relative to `discover.py` (which enforces `u+v≥1` via `options`). Document or tighten.

**3. Low — `separation_complete` depends on a leaked loop variable** (`discover.py:78-96`)
`a` after the state loop is the last state processed; `a==len(states)-1` is correct only because the time-break at line 91 occurs after a state is fully scanned. Correct today, fragile. No mislabeling risk observed: `status` is hardcoded `DISCOVERY_ONLY`, and no code path emits an upper-bound claim.

**Verified by hand (calibration certificate):** states `(1,2,0)`,`(2,1,0)`, both `T=2`. Summing the 7 weighted rows: B coefficient `2/3+1/3=1`; every payment variable cancels to exactly 0 (e.g. `a_((2,1,0),0)`: `−2/3 −1/3 +1/3 +2/3 = 0`); constant `1/3+1/6+1/3+1/3 = 7/6`. Certificate is valid for B ≥ 7/6.

**Confirmed correct:**
- Averaging argument (ENCODING 11-18): budget, coverage, nonnegativity are linear and relabel-invariant; an own-report increase maps to an own-report increase under the group action; invariant payment indexing `(s,h,low/high)` is exactly the orbit of `(owner, profile)`.
- Budget/cover/mono rows in `verify.py` match the stated constraints; mono row moves exactly one low owner in a type-`h` pool to high in a type-`(h+1)` pool of `s−e_h+e_{h+1}`.
- Cancellation sign (`verify.py:52-54`): `coeff·B + Σ d_v y_v ≥ q` with `d_v≤0`, `y_v≥0` ⇒ `coeff·B ≥ q`. Correct direction.
- Repair (`discover.py:105-113`): adding weight `max_j residual_j/multiplicity_j` of the state's budget row zeroes or negates all residuals at that state and only increases the B coefficient; it weakens but cannot invalidate. Verifier re-derives independently.
- Separation completeness argument (ENCODING 47-51): per-type cheapest eligible choice repeated across copies costs no more than any coalition of worth ≥ t.

## Scope limitations
- Game definition (worth = min over pools of selected report sum; monotonicity = own payment non-decreasing in own report) is asserted in ENCODING, not in the packet. If the research property has the opposite sign, mono rows flip.
- "Known 7/6" and the solver/verifier run outputs are not in the packet; I only hand-checked the certificate file.
- Fixed k,m,H pool structure is a specific instance family; the bound is a lower bound on worst case only.

## Verdict
Findings (one medium test-coverage gap, two low); no correctness defects found in the certificate or verifier logic within the reviewed scope.
