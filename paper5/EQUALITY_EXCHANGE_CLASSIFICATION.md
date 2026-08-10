# Table-free six-player equality classification by exactness exchanges

Date: 2026-08-09

## Result and status

Let `v` be a singleton-normalized exact game on six players, let

```text
x = Lmin(v),        z = Lmax(v),        x(N)=z(N)=1,
```

and suppose `||x-z||_1=2/3`.  Then, up to a common permutation of the
players, `(x,z)` is one of exactly two payoff pairs:

```text
starved:  x=(1,1,1,1,4,4)/12,   z=(0,0,1,1,1,1)/4;
positive: x=(1,1,1,1,1,4)/9,    z=(1,1,4,4,4,4)/18.
```

This is now a **table-free computer-assisted theorem**.  It does not use the
37,277-row support/table universe, the `n+2`-generator normal form, staged
Farkas variables, or the 3,348 equality-type exclusions.  Its finite split is
only the fifteen possible cardinality triples of

```text
P={i:x_i>z_i},   M={i:z_i>x_i},   E={i:x_i=z_i}.
```

The proof is exact QF_LRA.  Every one of the fifteen minimized formulas is
UNSAT in Z3 and cvc5; cvc5 emits a trust-disabled CPC proof with no forbidden
markers, and Ethos checks every proof as `correct`.  The aggregate CPC size is
54,629,176 bytes.  This has not yet received external specialist review, and
the finite formulas should not be described as a hand proof.

## 1. The two elementary lemmas behind the encoding

Exactness supplies, for every player `i`, a core point `q^i` with
`q^i_i=v({i})=0`.  These six points give the only exactness data used below.

Three selection anchors are automatic:

1. `z` has at least two maximum coordinates.  If its maximum were unique at
   `i`, moving a short distance from `z` toward `q^i` would lower that unique
   maximum and improve the decreasing lexicographic vector.
2. Some `z`-top player satisfies `x_i>=z_i`.  Otherwise a short move from `z`
   toward `x` would lower every old top coordinate.
3. Some `x`-bottom player satisfies `z_i<=x_i`.  Otherwise a short move from
   `x` toward `z` would raise every old bottom coordinate.

All moves stay in the core by convexity, and the strict gaps to the next
stratum make the corresponding lexicographic improvement valid for a
sufficiently short step.

The second lemma is the **exactness blocker lemma**.  Let `y` be either
selection and let `h(N)=0` be a direction which improves the relevant sorted
lexicographic vector.  Optimality implies that some proper coalition `S`
tight at `y` has `h(S)<0`; otherwise a sufficiently short step `y+epsilon h`
would remain in every core halfspace and improve the selection.  If `y=x`,
core membership of `z,q^0,...,q^5` then gives

```text
z(S)>=x(S),       q^i(S)>=x(S) for every i.             (E-min)
```

If `y=z`, the analogous inequalities are

```text
x(S)>=z(S),       q^i(S)>=z(S) for every i.             (E-max)
```

Thus every tested improving direction must have a negative coalition which
is simultaneously eligible against the opposite selection and all six
singleton witnesses.  Tightness itself is not encoded, so these necessary
conditions are a relaxation of the game problem; proving that the relaxation
is infeasible is sound.

## 2. The complete fifteen-case split

Because `x` and `z` have the same total and are distinct, `|P|,|M|>=1`.
Relabel the players so that `P`, then `M`, then `E` are consecutive.  There
are exactly fifteen triples `(p,m,e)` with `p,m>=1` and `p+m+e=6`.
Moreover

```text
||x-z||_1 = 2 sum_{i in P}(x_i-z_i),
```

so equality is a single rational linear equation in each case.

The audit begins with all efficiency-preserving integer directions whose
coefficients lie in `[-1,1]`.  Eleven cases are already impossible.  Four
residual cases need stronger exchanges:

- `(p,m,e)=(2,3,1)` and `(3,3,0)` use coefficients in `[-2,2]`;
- `(3,2,1)` and `(4,2,0)` add all permutations of
  `(-1,-1,-1,0,1,2)` to the coefficient-one pool;
- the two strict cases exclude, respectively, the positive and starved
  canonical payoff profile.  Their UNSAT verdict therefore proves rigidity,
  not nonexistence.

For each direction, the formula asserts the blocker implication only when a
simple sufficient lex-improvement predicate holds.  On the Lmin side, the
lowest affected payoff level has a positive coefficient and no negative
coefficient; on the Lmax side, the highest affected level has a negative
coefficient and no positive coefficient.  These predicates were formulated
symbolically and are independent of the older rank-table encodings.

The proof-discovery pass used assumption-literal UNSAT cores to discard
irrelevant direction clauses.  Those cores are not proof evidence.  Each
retained menu was rebuilt without assumptions and checked UNSAT.  The frozen
formulas contain 314 labeled directions in total; sign-preserving symmetry
compresses their description to 80 orbit signatures.

| sign counts `(p,m,e)` | retained directions | sign-preserving orbits | conclusion |
|---|---:|---:|---|
| `(1,1,4)` | 1 | 1 | impossible |
| `(1,2,3)` | 1 | 1 | impossible |
| `(1,3,2)` | 1 | 1 | impossible |
| `(1,4,1)` | 1 | 1 | impossible |
| `(1,5,0)` | 0 | 0 | impossible from anchors/signs |
| `(2,1,3)` | 2 | 2 | impossible |
| `(2,2,2)` | 16 | 7 | impossible |
| `(2,3,1)` | 17 | 6 | impossible |
| `(2,4,0)` | 8 | 1 | impossible |
| `(3,1,2)` | 2 | 2 | impossible |
| `(3,2,1)` | 51 | 17 | impossible |
| `(3,3,0)` | 111 | 26 | canonical positive profile only |
| `(4,1,1)` | 2 | 2 | impossible |
| `(4,2,0)` | 96 | 12 | canonical starved profile only |
| `(5,1,0)` | 5 | 1 | impossible |

The labels in the frozen formulas are fixed only after the sign-preserving
relabeling.  No contingency-table choice occurs.

## 3. Proof-object boundary

The certified implication is:

```text
exact game + normalized selections + distance 2/3
    => six singleton witnesses
    => anchors and every applicable exchange blocker
    => one of the two canonical payoff pairs.
```

The first two arrows are the elementary arguments above.  The last arrow is
the fifteen-case exact proof-object family.  The CPC objects independently
certify their displayed QF_LRA formulas; they do not certify that the prose
translation, the definitions of Lmin/Lmax, or the first-crossing argument in
`S6_EQUALITY_CLASSIFICATION.md` is correct.  Those interfaces remain explicit
human-review obligations.

An attempted single unlabeled formula, containing all 3,220 blocker clauses
and the 150 permuted canonical alternatives, returned `unknown` on both the
no-eligible-triple and noncanonical branches at a five-minute Z3 timeout per
branch.  No conclusion is drawn from those timeouts.  The sign-count split is
the current proof architecture because it is exact, exhaustive, and small
enough to certify independently.

## 4. Reproduction

The offline integrity check is

```text
python3 coopgames/verifiers/s6/reproduce_equality_exchange_classification.py
```

It byte-regenerates all fifteen SMT-LIB formulas from
`equality_exchange_direction_cores.json`, compares them with the frozen
files, and verifies all recorded hashes and proof controls.

To regenerate the proofs themselves, use
`generate_equality_exchange_certificates.py` with explicit paths to Z3 4.15.3,
cvc5 1.3.3, Ethos 0.2.3, and cvc5's `proofs/eo/cpc` signatures.  The generation
script enables `--proof-pedantic=1` and `--no-proof-allow-trust`.

The relevant paths are:

```text
coopgames/verifiers/s6/audit_equality_universal_exchange_relaxation.py
coopgames/verifiers/s6/minimize_equality_exchange_directions.py
coopgames/verifiers/s6/equality_exchange_direction_cores.json
coopgames/verifiers/s6/audit_equality_exchange_orbits.py
coopgames/verifiers/s6/equality_exchange_sign_orbits.json
coopgames/verifiers/s6/export_equality_exchange_classification_smt.py
coopgames/verifiers/s6/generate_equality_exchange_certificates.py
coopgames/verifiers/s6/reproduce_equality_exchange_classification.py
coopgames/verifiers/s6/verify_equality_exchange_classification_certificates.py
coopgames/verifiers/s6/certificates/equality_exchange_*.{smt2,cpc,json}
```

## 5. Consequence for the six-player program

The old 3,348-row equality-exclusion census is no longer a logical dependency.
Together with the already-checked table-free barriers in the contiguous
refinement neighborhoods of the two canonical profiles, this leaves the
first-crossing bridge—not equality classification—as the principal obstacle
to a computer-assisted proof of `s(6)=2/3`.

The next highest-value audit is therefore hostile verification of:

1. continuity of both staged lexicographic selections along the exact-game
   path from the unanimity game;
2. existence of a first `2/3` crossing before any strict counterexample;
3. the inference that a sufficiently nearby ordered payoff pattern is a
   contiguous refinement of the canonical equality strata; and
4. the mapping from every such refinement into the positive or starved
   table-free exchange theorem.

Until those interfaces are reviewed, the correct claim is a new
computer-assisted equality classification and a nearly closed route to the
six-player upper bound—not a field-level breakthrough.
