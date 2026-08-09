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
rational infeasibility certificates.  Equality classification and hostile
external review also remain incomplete.

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
   `triage32.json` and audited in `AUDIT_S6.txt` and `coverage32.py`.
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

constructs a fresh equality model, compresses it to four generators, and
recomputes both selections with two independently formulated exact rational LP
implementations.  It obtains overlap exactly `2/3` and the dispersion-optimal
Lmax certificate

```text
theta=1/3, eta=0, alpha=(0,0,0,1/3,1/3,1/3), support={56}.
```

This verifies sharpness and one equality instance.  It does not prove that
every equality case has the same anchor.  The prepared equality searches must
still exclude (i) equality without a tight triple of Lmax-top players and
(ii) equality with an over-cover of dispersion strictly below `1/3`.

An independently checked proof-object lane is now frozen under
`verifiers/s6/certificates/`.  Z3 and cvc5 agree on one representative strict
failure exclusion and the two equality negations for the realizable boundary
configuration at survivor index 2236.  With trusted proof steps disabled,
cvc5 emits exact CPC proof bodies that the separately built Ethos checker
accepts as `correct`.  These controls validate the exporter and proof-checker
path; they are not yet certificate coverage for all 3,350 configurations.

## Required next checks

Before promoting the bound to a main paper theorem:

1. rerun a clean all-generator census or independently cross-check the accepted
   configurations with a second exact QF_LRA implementation;
2. extract replayable proof evidence—preferably rational LRA certificates—from
   the Boolean support branches rather than treating unsat cores as proof;
3. complete the two equality censuses and extract the surviving equality
   support types up to permutation;
4. obtain hostile external review of the normal-form theorem, staged Farkas
   signs, universe coverage, and artifact merger; and
5. search the literature before making a novelty claim for the
   selection-preserving `n+2` reduction.
