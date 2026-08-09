# Exact CPC certificate controls

Date: 2026-08-09

These files exercise an independently checked proof-object path for twenty-five
six-player generator-normal-form queries.  They do not replace the complete
3,350-configuration census and do not by themselves prove the global bound.

| Formula | Survivor | Query | Verdict |
|---|---:|---|---|
| `failure_index0000.smt2` | 0 | strict distance `>2/3` | UNSAT |
| `equality_noncanonical_index1408.smt2` | 1408 | distance `=2/3`, payoff pair differs from the displayed canonical pair | UNSAT |
| `equality_noncanonical_index2236.smt2` | 2236 | distance `=2/3`, payoff pair differs from the displayed canonical pair | UNSAT |
| `equality_no_common_triple_index1408.smt2` | 1408 | distance `=2/3`, no Lmax-top triple tight at both selections | UNSAT |
| `equality_no_common_triple_index2236.smt2` | 2236 | distance `=2/3`, no Lmax-top triple tight at both selections | UNSAT |
| `equality_no_triple_index1408.smt2` | 1408 | distance `=2/3`, no tight triple of Lmax-top players | UNSAT |
| `equality_no_triple_index2236.smt2` | 2236 | distance `=2/3`, no tight triple of Lmax-top players | UNSAT |
| `equality_subthird_index1408.smt2` | 1408 | distance `=2/3`, Lmax over-cover dispersion `<1/3` | UNSAT |
| `equality_subthird_index2236.smt2` | 2236 | distance `=2/3`, Lmax over-cover dispersion `<1/3` | UNSAT |
| `positive_lmax_direction_index0040.smt2` | 40 | positive critical residue plus a blocker to direction `(0,0,0,-1,0,1)` | UNSAT |
| `positive_lmax_direction_index0200.smt2` | 200 | representative `N(1,1),P(-2,-2,-1),r=3` Lmax direction blocker | UNSAT |
| `positive_lmax_direction_index0504.smt2` | 504 | representative distance-sensitive `N(-1,1),P(0,0,0),r=0` Lmax direction blocker | UNSAT |
| `positive_lmax_boundary_n_l.smt2` | abstract | blocker `{n,l}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_j_k_r.smt2` | abstract | blocker `{n,j,k,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_j_l_r.smt2` | abstract | blocker `{n,j,l,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_boundary_n_k_l_r.smt2` | abstract | blocker `{n,k,l,r}` plus distance `>2/3` | UNSAT |
| `positive_lmax_critical_boundary.smt2` | abstract | shared 16-row critical order plus distance `>2/3` | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_low.smt2` | abstract | `NNPPPR`, low common pair | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_outer.smt2` | abstract | `NNPPPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_nnpppr_high.smt2` | abstract | `NNPPPR`, high common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_low.smt2` | abstract | `NPNPPR`, low common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_outer.smt2` | abstract | `NPNPPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_npnppr_high.smt2` | abstract | `NPNPPR`, high common pair | UNSAT |
| `positive_lmin_critical_boundary_nppnpr_outer.smt2` | abstract | `NPPNPR`, outer common pair | UNSAT |
| `positive_lmin_critical_boundary_nppnpr_high.smt2` | abstract | `NPPNPR`, high common pair | UNSAT |

Indices 1408 and 2236 are the two equality-feasible stratum/table
configurations left by the complete staged census:

```text
index 1408: Lmin (4,2), Lmax (2,4), table ((2,2),(0,2));
index 2236: Lmin (5,1), Lmax (2,4), table ((2,3),(0,1)).
```

The separate reconstruction audit supplies and independently recomputes a
realizable equality game in each configuration.  Thus all eight equality
queries are nonvacuous: each base equality query is SAT; every equality payoff
pair in the type is the displayed canonical pair; a common tight top triple is
forced; and both asserted negations of the observed anchor geometry are UNSAT
in each surviving type.

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

The equality rigidity/negation lane now covers both solver-surviving equality types,
but the strict-bound lane remains representative rather than exhaustive.
A paper theorem still requires either checked proof objects for all excluded
support/configuration types or a human structural reduction that makes most
of those objects unnecessary.

The three positive-handover controls represent the three role-normalized Lmax
direction templates.  Each base critical-triple system is SAT.  The added formula says
that at least one coalition blocks the displayed lexicographically improving
Lmax direction, with the blocker required to be eligible at `z` for `x` and
for all six singleton-exactness witnesses.  Its UNSAT proof therefore checks
one genuinely nonvacuous direction argument per template.  They do **not**
certify the other 106 single-direction rows, the 230 rows killed by critical algebra, or
any Lmin direction-menu row.

The four abstract boundary controls no longer encode a contingency table.
They assume only the shared weak orders of the eight distance-sensitive rows,
the two common-triple equalities, six simplex witnesses satisfying all three
critical-triple inequalities, one displayed blocker, and distance `>2/3`.
Their checked UNSAT proofs show that each blocker shape forces distance at
most `2/3`.  A separate finite audit is still needed to map the eight refined
support types to exactly these four shapes.

The abstract critical-boundary control similarly removes all contingency
tables.  It assumes the shared weak order of the sixteen critical rows that
survive every single premise ablation, their forced common pair, all six
critical witnesses, and distance `>2/3`.  Its checked UNSAT proof covers the
abstract implication; the finite dependency audit separately verifies that
the sixteen rows have the required order and common pair.

The eight abstract Lmin critical-boundary controls use the **global** weak
Lmin order, recorded as an `N/P/R` role word.  This distinction matters: a P
player can lie between the two poor players.  Each formula retains only that
role word, one common excluded-player pair, one Lmax relation, the critical
witness system, and distance `>2/3`.  The separate map covers 342 rows and 470
feasible-pair instances; it must be audited together with these proof objects.

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
  --index 1408 --mode equality-no-triple \
  --output /tmp/equality_no_triple_index1408.smt2

$PYTHON coopgames/verifiers/s6/replay_core_closure_smt.py \
  --formula /tmp/equality_no_triple_index1408.smt2 \
  --z3 $Z3 --cvc5 $CVC5 --ethos $ETHOS \
  --cpc-signatures $CPC_SIGNATURES --timeout-seconds 120 \
  --cpc-proof /tmp/equality_no_triple_index1408.cpc \
  --output /tmp/equality_no_triple_index1408.json
```

The analogous modes are `failure` at index 0, and all four equality modes
(`equality-noncanonical`, `equality-no-common-triple`, `equality-no-triple`,
`equality-subthird`) at indices 1408 and 2236.  Compare the regenerated
formula/proof hashes and the final `PASS`/`correct` fields with the committed
JSON records.

An offline integrity check regenerates every formula from the current exporter
and `triage32.json`, checks byte identity, and then verifies all committed
formula/proof hashes and recorded Ethos verdicts:

```text
python3 coopgames/verifiers/s6/verify_frozen_certificates.py
python3 coopgames/verifiers/s6/verify_positive_handover_certificates.py
```
