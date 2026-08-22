# Paper 5 review environment

The Python verifiers target Python 3.10 and use exact rational arithmetic.
Create an isolated environment from the repository root, then install the one
non-standard Python dependency:

```text
python3.10 -m venv /tmp/coop-paper5-review
/tmp/coop-paper5-review/bin/python -m pip install \
  -r coopgames/paper5/requirements-review.txt
PAPER5_PYTHON=/tmp/coop-paper5-review/bin/python
```

Use `"${PAPER5_PYTHON}"` for every Python command in the review packet.  The
frozen coefficient-two formulas and the PXC100 cell censuses were replayed
with Z3 5.0.0 (`z3-solver==5.0.0.0`). The coefficient-formula bytes are
version-insensitive, while the pinned package also reproduces the solver-version
provenance recorded in both 3,840-cell artifacts.

The proof-object lane additionally requires:

- cvc5 1.3.3, tag `cvc5-1.3.3`, commit
  `8ff882e3e42f046867d2ac2e33e92b3d026144ae`;
- Ethos commit `59e9ea6a077e1fd73dfc3107966b9f5603896c86`;
- the `proofs/eo/cpc/` signature tree from that cvc5 checkout; and
- pdfTeX from TeX Live 2025 or later for the release build.

Point the replay commands at those binaries and signatures:

```text
PAPER5_Z3=/path/to/z3
PAPER5_CVC5=/path/to/cvc5
PAPER5_ETHOS=/path/to/ethos
PAPER5_CPC_SIGNATURES=/path/to/cvc5/proofs/eo/cpc
```

The exact solver replay command is recorded next to the coefficient-two
certificate discussion in `coopgames/verifiers/s6/certificates/README.md`.
`verify_independent_bound_two.py` is deliberately an offline
regeneration/hash/status audit; it does not execute cvc5 or Ethos.

For the complete local release gate run:

```text
coopgames/paper5/verify_release.sh "${PAPER5_PYTHON}"
```
