# Six-player generator-normal-form census checkpoint

Date: 2026-08-09

## Result at this checkpoint

The strict-failure census now has a decisive solver verdict for every one of
the 3,350 six-player Lmin/Lmax stratum-table configurations that survived the
previously audited hand net:

```text
SAT (strict L1 distance > 2/3):       0
UNSAT:                             3350
UNKNOWN:                              0
```

At total one, strict L1 distance `>2/3` is equivalent to hybrid overlap
`<2/3`.  Combined with the existing exact four-generator equality examples,
this is strong computer-assisted evidence for the sharp statement

```text
sum_i min(Lmin_i,Lmax_i) >= 2/3
```

on six-player singleton-normalized exact games.

It is not yet presented as an unconditional paper theorem.  The accepted
artifact records exact QF_LRA solver verdicts, not independently replayed
rational infeasibility certificates.  Equality classification is now complete
at the same solver-evidence level and is documented separately in
`S6_EQUALITY_CLASSIFICATION.md`; hostile external review remains incomplete.

## Dependency map

The computational conclusion has five dependencies.

1. **Finite-generator normal form.**  By
   `CORE_CLOSURE_REDUCTION.md`, any relevant pair `(Lmin,Lmax)` from an exact
   singleton-normalized `n`-player game is preserved by a lower envelope of at
   most `n+2` common-total nonnegative generators whose zero sets cover the
   players.
2. **Stratum/table universe.**  `nsix.compositions` and `nsix.tables` enumerate
   all ordered Lmin strata, ordered Lmax strata, and their contingency tables
   up to relabeling.  The audited universe has 37,277 configurations.
3. **Hand exclusions.**  The previously reviewed dimension-free lemmas exclude
   24,795 unique-Lmax-top configurations and the hand net excludes 9,132 more,
   leaving exactly 3,350 survivors.  These exclusions are recorded in
   `triage32.json` and audited in `AUDIT_S6.txt`, `coverage32.py`, and its
   regenerated `coverage32.json` output.
4. **Full staged optimality.**  The encoding carries a separate Farkas
   certificate for every player at every Lmin and Lmax stage, with old pinned
   levels imposed recursively.  It therefore does not substitute the false
   paired-first-stage relaxation documented in
   `TWO_PACKET_EXACTIFICATION_BOUNDARY.md`.
5. **Exact solver census.**  Every survivor is tested against strict L1
   distance `>2/3` using rational linear arithmetic and shared support
   eligibility markers.

If any dependency fails review, the census is not a proof.

## Run structure and timeout discipline

The exploration used three existence-equivalent encodings while the normal
form was being simplified:

```text
initial core-closure rows:              873  (866 UNSAT, 7 capped UNKNOWN)
one-way-support closure rows:           187  (177 UNSAT, 10 capped UNKNOWN)
direct generator-normal-form rows:     2300  (2300 UNSAT)
isolated generator reruns:               17  (17 UNSAT)
```

Some adjacent shards overlap because a process was allowed to finish its
current row before a safer encoding replaced it.  The merger accepts duplicate
rows only if their decisive verdicts agree, or if a decisive isolated rerun
replaces `UNKNOWN`; conflicting `SAT`/`UNSAT` verdicts are fatal.  The final
map covers every authoritative survivor index exactly once.  Twenty-three
indices had benign duplicate or resolution records.

The direct generator pass had no timeout.  All 17 capped rows from the earlier
encodings resolved `UNSAT` in isolated generator-normal-form reruns with a
120-second cap.  No solver process remains active at this checkpoint.

## Accepted artifact

The stable, timing-free accepted output is

```text
verifiers/s6/core_generator_census.json
```

It lists all 3,350 configurations, their authoritative survivor index, and the
final verdict.  The merger

```text
verifiers/s6/merge_core_closure_census.py
```

checks complete index coverage, exact configuration identity against
`triage32.json`, duplicate consistency, timeout replacement, and the final
tally.  Raw timing shards remain execution logs rather than proof objects.

## Sharpness and equality geometry

The independently encoded reconstruction control

```text
verifiers/s6/audit_core_closure_reconstruction.py
```

now reads the complete equality-with-triple census, reconstructs both SAT
models, compresses their singleton witnesses, and recomputes both selections
with two independently formulated exact rational LP implementations.  The two
surviving support types are

```text
index 1408: Lmin (4,2), Lmax (2,4), table ((2,2),(0,2));
index 2236: Lmin (5,1), Lmax (2,4), table ((2,3),(0,1)).
```

Both obtain overlap exactly `2/3` and the dispersion-optimal Lmax certificate

```text
theta=1/3, eta=0, alpha=(0,0,0,1/3,1/3,1/3), support={56}.
```

The complete equality split is now

```text
with a tight Lmax-top triple:       2 SAT / 3348 UNSAT / 0 UNKNOWN
without a tight Lmax-top triple:    0 SAT / 3350 UNSAT / 0 UNKNOWN.
```

Within the two surviving types, independently checked CPC proofs show that
the displayed payoff pairs are forced and exclude both absence of a tight top
triple and over-cover dispersion below `1/3`.  Thus equality anchor geometry
is rigid conditional on the finite classification.  The 3,348 type exclusions
remain census verdicts rather than individually checked proof objects.

An independently checked proof-object lane is now frozen under
`verifiers/s6/certificates/`.  Z3 and cvc5 agree on one representative strict
failure exclusion and all eight rigidity/common-triple/anchor negations for the two realizable
equality types.  With trusted proof steps disabled, cvc5 emits exact CPC proof
bodies that the separately built Ethos checker accepts as `correct`.  The
equality lane covers both surviving equality types; the strict-failure lane is
still representative rather than coverage for all 3,350 configurations.

## Required next checks

Before promoting the bound to a main paper theorem:

1. replace the 3,350 strict and 3,348 equality-type UNSAT verdicts by a human
   structural reduction or checked proof-object coverage;
2. attack the local tangent/normal-cone barrier at the two rigid equality
   profiles described in `S6_EQUALITY_CLASSIFICATION.md`;
3. obtain hostile external review of the normal-form theorem, staged Farkas
   signs, universe coverage, and artifact merger; and
4. search the literature before making a novelty claim for the
   selection-preserving `n+2` reduction.
