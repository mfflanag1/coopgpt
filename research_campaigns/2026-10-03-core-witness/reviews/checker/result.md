Both files are written but nothing has been executed — I had no way to run code here, so the test suite and the `-O` behaviour are unverified until the controller runs them.

## What was implemented

**`src/check_certificate.py`**
- `check(data) -> dict` rebuilds everything from `m`, `P` and the raw matrices: the P disjointness check, unmatched set, support, off-support zeros, diagonal total, witness targets (dummy `[-1]` when P is perfect), coverage of all m³ triples per witness, `primal_J`, and the exact residual dual bound.
- Every check raises `CertificateError` (a `ValueError` subclass); there are no `assert` statements.
- The result gives `lower`, `upper` and `gap` as exact rational strings, an `equal` flag and dimensions. It does not require `upper < 1/3` or `lower == upper`, and it ignores extra fields such as metadata.
- The CLI is `python check_certificate.py CERT.json`: exit 0 with a JSON result, 1 with `REJECTED` on stderr, 2 on usage error. The loader also rejects `NaN`/`Infinity` and duplicate JSON keys.

**`src/test_check_certificate.py`**
- Uses `unittest` with hand-computed fixtures only: m=1 perfect, m=1 empty P, m=2 empty P, an m=2 off-diagonal P, and three lambda cases.
- Covers every malformed-data case the contract lists, plus float/bool rejection.
- Includes subprocess tests that run the CLI under `python -O`.

## Conflicts and interpretations to confirm

- **Contract's m=2 example says "objective0"; I get −1/3.** With AB diagonal entries 1/2 and the described witnesses, the four A/B targets each get 1/2 and the two C targets get 0, so J = 2/3 − 1 = −1/3. The test uses `primal_J = "-1/3"` with upper 1; I did not alter the formula to force 0.
- **Rational strings are stricter than "anything `Fraction` accepts".** I accept only `±int`, `±int/int` and plain decimals. Exponent forms, underscores, whitespace and strings over 4000 characters are rejected. If the generator emits something like `"1e-3"`, the checker will reject it and this needs relaxing.
- **Matrix indexing is my reading.** I took `matrices[0][a][b]`, `matrices[1][a][c]`, `matrices[2][b][c]`, with team worth as the sum of those three and global ID as sector·m + label. If the generator uses another orientation, valid certificates will be rejected.
- **Diagonal normalization row.** It puts coefficient 1 on each diagonal pair only; P pairs get the objective coefficient 3 per occurrence.
- **Exact types.** Lists must be JSON lists (tuples are rejected) and integers must be exactly `int`.

## Limitations

- Coverage checking costs targets × m³ exact rational operations, with no guard against very large `m`.
- `lower`, `upper` and `gap` are strings, not `Fraction` objects, so that the result is JSON-serializable; callers need `Fraction(result["upper"])` to compare.
- An accepted certificate bounds the fixed-support LP only, as the formulation states.
