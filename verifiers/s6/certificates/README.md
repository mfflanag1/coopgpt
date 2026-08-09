# Exact CPC certificate controls

Date: 2026-08-09

These files exercise an independently checked proof-object path for three
representative six-player generator-normal-form queries.  They do not replace
the complete 3,350-configuration census and do not by themselves prove the
global bound.

| Formula | Survivor | Query | Verdict |
|---|---:|---|---|
| `failure_index0000.smt2` | 0 | strict distance `>2/3` | UNSAT |
| `equality_no_triple_index2236.smt2` | 2236 | distance `=2/3`, no tight triple of Lmax-top players | UNSAT |
| `equality_subthird_index2236.smt2` | 2236 | distance `=2/3`, Lmax over-cover dispersion `<1/3` | UNSAT |

Index 2236 is the stratum/table configuration

```text
Lmin composition (5,1)
Lmax composition (2,4)
table ((2,3),(0,1)).
```

The separate reconstruction audit supplies a realizable equality model in
this configuration.  Thus the last two queries are nonvacuous controls: the
base equality query is SAT, while each asserted negation of the observed
anchor geometry is UNSAT.

## What is checked

`export_core_closure_smt.py` rebuilds each formula from `triage32.json`.  Its
small serializer emits the QF_LRA/Boolean AST without Z3-specific unary sums
or local `let` aliases and names every premise.  The frozen formula is then:

1. decided independently by Z3 5.0.0 and cvc5 1.3.3;
2. proved UNSAT by cvc5 with `--proof-pedantic=1` and
   `--no-proof-allow-trust`; and
3. checked as an exact CPC proof by Ethos, which returns `correct`.

The `.cpc` files contain the path-independent proof bodies.  The JSON files
bind each formula and proof body to SHA-256 hashes and record both solver
verdicts and the Ethos result.  CPC arithmetic is exact rational arithmetic.
This is stronger evidence than an unsat core: no unsat core is treated as a
proof, and the proof checker validates the complete proof body against the
official CPC signatures.

This is still a representative certificate lane, not exhaustive proof
coverage.  A paper theorem requires either a checked proof object for every
remaining support/configuration type or a human structural reduction that
makes most of those objects unnecessary.

## Pinned checker sources

- cvc5 tag `cvc5-1.3.3`, commit
  `8ff882e3e42f046867d2ac2e33e92b3d026144ae`, including
  `proofs/eo/cpc/`;
- Ethos commit `59e9ea6a077e1fd73dfc3107966b9f5603896c86`.

Both are official cvc5 repositories.  Build Ethos from that commit with

```text
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

## Reproduction template

Run from the repository root, replacing the three tool paths:

```text
PYTHON=.../python3
Z3=.../z3
CVC5=.../cvc5
ETHOS=.../ethos
CPC_SIGNATURES=.../cvc5/proofs/eo/cpc

$PYTHON coopgames/verifiers/s6/export_core_closure_smt.py \
  --index 2236 --mode equality-no-triple \
  --output /tmp/equality_no_triple_index2236.smt2

$PYTHON coopgames/verifiers/s6/replay_core_closure_smt.py \
  --formula /tmp/equality_no_triple_index2236.smt2 \
  --z3 $Z3 --cvc5 $CVC5 --ethos $ETHOS \
  --cpc-signatures $CPC_SIGNATURES --timeout-seconds 120 \
  --cpc-proof /tmp/equality_no_triple_index2236.cpc \
  --output /tmp/equality_no_triple_index2236.json
```

The analogous modes are `failure` at index 0 and `equality-subthird` at
index 2236.  Compare the regenerated formula/proof hashes and the final
`PASS`/`correct` fields with the committed JSON records.

An offline integrity check of all committed formula/proof pairs is:

```text
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
```
