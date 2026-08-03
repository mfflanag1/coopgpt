# Reviewer packet: the exact four-player Lmin--Lmax bridge

Prepared 2026-08-03 and revised after a hostile external review of commit
`5376a76`.  That review returned "verified with qualifications," reproduced
the finite theorem from scratch, and found no mathematical error.  The
qualifications concerned prior-art attribution, reproducibility, and
exposition; this packet incorporates those corrections.  This remains one
external technical review, not journal peer review or a definitive novelty
opinion.

## Result under review

Let `v` be an exact TU game with at most four players and normalize its
singleton values to zero.  If `phi=Lmin(v)` and its payoff strata, from poor to
rich, are `B_1,...,B_k`, then every richer suffix

```text
H_j = B_(j+1) union ... union B_k
```

is tight at every strict payoff gap: `phi(H_j)=v(H_j)`.  This says exactly that
`v` is an exact partition game in the sense of Llerena--Mauri (2017), witnessed
at `phi`.  Their published theory gives the Lorenz-dominating core allocation;
in the present notation `phi=Lmax(v)`.  Published results then give
`Lmax=PES` and coalitional monotonicity on this domain.  Together with the
five-player exact Lmin counterexample, this makes dimension five sharp.

The contribution under review is the sharp classification "exact and
`n<=4` implies exact partition at Lmin" and its sharp failure at five.  Neither
the exact-partition definition nor its Lorenz consequence is claimed as new.

The manuscript now gives a structural human proof.  The two exact-rational
encodings remain independent audits of the conclusion and sign conventions;
they are no longer the proof of the classification.  The new argument has not
yet received external review.

## Dependency map

```text
exactness + zero singleton values + Lmin stage optimality
                         |
                         v
       exact n<=4 is exact partition at Lmin (new sharp classification)
                         |
                         v
       Dutta--Ray exact-partition theory      (Llerena--Mauri 2017)
                         v
           Lmin Lorenz-dominates Core(v), hence Lmin=Lmax
                         |
        exact n<=4 -> large core              (Biswas et al. 1999)
        large core -> egalitarian stable      (Dietzenbacher 2021)
        PES=Lmax and PES coalitionally monotone on that domain
                         |
                         v
       normalized Lmin coalitionally monotone through n=4
                         |
             exact five-player counterexample
                         v
                dimension five is sharp
```

Singleton bumps use the manuscript's separate translation lemma and theorem;
all other one-coalition bumps leave the singleton normalization vector fixed.

## Structural proof: protector coalitions

At a completed Lmin stratum, fix the poorer coordinates and retain the current
floor constraints.  If `i` is in the current stratum and `h` is richer, the
dual of `max x_i` on this stage face has tight-coalition coverages satisfying

```text
coverage(h)-coverage(i)=1+floor_multiplier(i)>0.
```

Hence some tight **protector coalition** contains `h` and omits `i`.  Combining
these protectors with the exact core point that attains a singleton value zero
closes the low-dimensional geometry:

1. A unique richest player would give, for each poorer player `i`, a nonempty
   protector `{r} union Q_i` omitting `i`.  At the exact witness with `z_r=0`,
   the displacements satisfy `a(L)=phi_r` but `a(Q_i)>=phi_r`.  An elementary
   three-vertex argument shows this is impossible when there are at most three
   poorer players.
2. A unique poorest player globally maximizes its coordinate at Lmin, so its
   complement is tight by exactness.
3. The only remaining four-player boundary is `2|2`.  Protector coalitions
   either force both poor-player complements, force a complement plus a cross
   pair (which overallocates an exact singleton witness), or force all four
   cross pairs (which creates a core segment raising both poorest players).

This exhausts the geometry without enumerating payoff compositions or tight
sets.  The five-player base witness escapes in a `3|2` boundary: its tight
coalitions `{3,4,5}` and `{1,3,5}` protect the three poorer players while
leaving the richer pair `{3,5}` slack.

The full proof is in `paper3/sections_leximin.tex`; an expanded proof audit is
in `paper3/N4_LMIN_LMAX_HUMAN_PROOF.md`.

## Encoding A: symbolic KKT/exact-face certificate

File: `src/verify_n4_exact_lmin_pes_bridge.py`.

Write `s(T)=phi(T)-v(T)`.  Exactness is encoded from its definition: for every
proper coalition `C`, a displacement `d^C` satisfies

```text
d^C(N)=0,
d^C(C)=-s(C),
d^C(T)>=-s(T) for every proper T.
```

At each progressive Lmin stage, the verifier includes the dual of the common-
level program and the dual of the individual pin program for every player in
the current stratum.

### KKT sign audit

For the common-level maximization, write it as minimization of `-t`, with
constraints

```text
v(T)-x(T) <= 0,          multiplier lambda_T >= 0,
t-x_i <= 0,              multiplier mu_i >= 0,
x(N)=v(N),               free multiplier nu,
x_i=phi_i (earlier pins), free multiplier pi_i.
```

The Lagrangian derivatives are

```text
dL/dt   = -1 + sum_i mu_i = 0,
dL/dx_i = -sum_(T contains i) lambda_T - mu_i + nu + pi_i = 0.
```

For individual pin `i`, the objective is `-x_i`, the stage level is a fixed
constant, and stationarity becomes

```text
-1_(h=i) - sum_(T contains h) lambda_T - mu_h + nu + pi_h = 0.
```

These signs match the implementation.  Core complementarity is
`lambda_T=0 or s(T)=0`.  A later-stratum floor is strictly inactive and its
`mu` is set to zero; current-stratum floors are active and their nonnegative
multipliers remain free.  Earlier coordinates are equality-pinned.

### Normalization audit

- Modular translation by singleton values sends `Core(v)` to `Core(v)-m` and
  preserves exactness.
- Every strict payoff gap can be scaled to at least one because the complete
  feasibility system is positively homogeneous.
- In Encoding A, positive suffix slack remains a strict exact-rational query;
  no floating tolerance is used.
- The script aborts under `python -O`.

For each of the four realizable stratum patterns,
`src/verify_n4_exact_lmin_pes_bridge_cores.py` extracts an unsatisfiable subset
of the original suffix-slack query, greedily reduces it to local
irreducibility, rechecks the reduced unlabelled formula, and verifies that
every single-assertion deletion is satisfiable.  The retained sizes are 15,
59, 40, and 64 assertions, from full formulas containing 158, 470, 472, and
510 assertions.  These are audit conveniences using the same Z3 query.  They
are not Farkas linear-combination proofs, hand-checkable certificates, or an
independent source of verification.

## Encoding B: independently formulated Lmin-optimality test

File: `src/verify_n4_exact_lmin_pes_bridge_primal.py`.

This verifier uses no KKT multiplier and no complementarity constraint for
Lmin optimality.  It shares Encoding A's definition-level exact-face system,
singleton normalization, gap normalization, and Z3 engine.  It enumerates the
tight proper-coalition set `A`.  At `phi`, its exact tangent
cone is

```text
d(N)=0,  d(T)>=0 for T in A.
```

At a stratum `B_j`, after earlier strata are fixed, a lexicographic
improvement exists exactly when some tangent direction satisfies

```text
d_i=0 for every earlier player,
d_i>=0 for every i in B_j,
d_h>0 for at least one h in B_j.
```

Convexity proves the equivalence: a better core point supplies its displacement
from `phi`; conversely, a sufficiently small positive multiple of any such
direction preserves every inactive inequality because its slack is positive.
Homogeneity replaces `d_h>0` by `d_h>=1`.

For each tangent pattern that passes these primal tests, a separate exact
linear system asks whether slacks and definition-level exact-face witnesses
realize it.  Singleton tightness has only two possibilities: the entire first
payoff block is at level zero, or no singleton is tight.  This reduces the
four-player enumeration to exactly `2*2^10=2048` active sets per composition.

The two encodings agree:

| players | composition | status |
|---:|:---:|:---|
| 2 | `1+1` | impossible |
| 3 | `2+1` | impossible |
| 3 | `1+2` | realizable; suffix tight |
| 3 | `1+1+1` | impossible |
| 4 | `3+1` | impossible |
| 4 | `2+2` | realizable; suffix tight |
| 4 | `2+1+1` | impossible |
| 4 | `1+3` | realizable; suffix tight |
| 4 | `1+2+1` | impossible |
| 4 | `1+1+2` | realizable; both suffixes tight |
| 4 | `1+1+1+1` | impossible |

The seven impossible patterns are exactly the patterns with a unique richest
player.  This is a corollary of the theorem, not separate evidence: if the
unique richest player were `r`, exact-partition tightness would give
`phi_r=v({r})=0`, contradicting a strictly positive richest level in a
nonconstant singleton-normalized allocation.

## Concrete realizability witnesses

Encoding B emits a small integer game for every realizable pattern.  A third
program, `src/verify_n4_exact_lmin_pes_bridge_witnesses.py`, independently:

1. minimizes every proper coalition over the core and confirms exactness;
2. recomputes Lmin with the project's exact rational Maschler implementation;
3. checks every richer-suffix equality.

The resulting Lmin vectors are:

```text
n=3, 1+2:     (1,2,2)
n=4, 2+2:     (1,1,2,2)
n=4, 1+3:     (1,2,2,2)
n=4, 1+1+2:   (1,2,3,3)
```

All coalition values are included in
`results/n4_exact_lmin_pes_bridge_primal.json`.

## Published exact-partition consequence

Llerena--Mauri (2017) prove that the Dutta--Ray allocation of an exact
partition game is its Lorenz-dominating core element.  The following short
argument only translates their consequence into the manuscript's upper-tail
convention.  At a boundary where `H` comprises
the `r` richest coordinates of `phi`, every `x` in the core satisfies

```text
sum_(i=1)^r x_i^down >= x(H) >= v(H) = phi(H)
                       = sum_(i=1)^r phi_i^down.
```

Between consecutive stratum boundaries, the cumulative sum of the decreasing
rearrangement of `x` is concave in `r`, while the corresponding cumulative sum
for `phi` is linear across its tied block.  The boundary inequalities therefore
imply every intermediate upper-tail inequality.  Equal totals convert these
upper-tail inequalities into Lorenz dominance.  In particular, `phi` is the
unique lexicographic minimizer of descending payoffs, namely Lmax.

## Exact reproduction commands

Run from `coopgames/`:

```sh
python src/verify_n4_exact_lmin_pes_bridge.py \
  --output results/n4_exact_lmin_pes_bridge.json
python src/verify_n4_exact_lmin_pes_bridge_cores.py \
  --output results/n4_exact_lmin_pes_bridge_cores.json
python src/verify_n4_exact_lmin_pes_bridge_primal.py \
  --output results/n4_exact_lmin_pes_bridge_primal.json
python src/verify_n4_exact_lmin_pes_bridge_witnesses.py \
  --output results/n4_exact_lmin_pes_bridge_witnesses.json
python src/verify_n4_exact_lmin_pes_artifacts.py
python src/verify_n5_exact_leximin_monotonicity_counterexample.py \
  --output results/n5_exact_leximin_monotonicity_counterexample.json
python src/verify_n5_exact_lmin_lmax_large_core.py \
  --output results/n5_exact_lmin_lmax_large_core.json
```

Expected failure-safety check:

```sh
python -O src/verify_n4_exact_lmin_pes_bridge.py
python -O src/verify_n4_exact_lmin_pes_bridge_cores.py
python -O src/verify_n4_exact_lmin_pes_bridge_primal.py
python -O src/verify_n4_exact_lmin_pes_bridge_witnesses.py
```

Each optimized-mode command fails immediately.  This is defensive execution
policy; these programs do not currently rely on Python `assert` statements.

## Known limitations

1. The protector-coalition proof is new in this revision and has not yet been
   checked by an external human reviewer.  Its load-bearing points are the
   stage-face pinning claim, the LP-dual coverage sign, and the exact-singleton
   contradictions in the `2|2` case.
2. Both exhaustive encodings use Z3's exact linear-rational engine, although
   they formulate Lmin optimality differently.  The concrete witnesses are
   replayed by the project's separate exact-LP implementation.
3. The reduced unsatisfiable cores and Z3's internal proof objects are not
   standalone Farkas certificates.  Three four-player cores retain 40--64
   assertions because complementarity branches heavily.  The exhaustive
   2048-tight-set primal enumeration independently formulates Lmin optimality,
   but shares the exactness system and solver and is not a compact hand proof.
4. One hostile external review found no mathematical error and independently
   reproduced the claims.  It is not a substitute for peer review.
5. Exact-partition games and their Lorenz-dominating Dutta--Ray allocation are
   prior art.  The narrower classification of exact games through four players
   appears new, but MathSciNet/zbMATH and expert citation-chain review remain
   outstanding.

## Questions for the external reviewer

1. On the Maschler-stage face, does final membership `i in B_j` indeed imply
   `max x_i=phi_i`, including degenerate faces?  Is the short-segment argument
   sufficient?
2. With the manuscript's minimization convention, is the protector identity
   `w_h-w_i=1+mu_i>0` signed correctly, and does complementary slackness yield
   a tight coalition containing `h` and omitting `i`?
3. Is the three-player displacement argument excluding a unique richest
   player complete for every choice of nonempty `Q_i subseteq L\{i}`?
4. In the tied `2|2` case, do the protector disjunctions cover every coalition,
   and do the all-cross-pairs equalities really produce the displayed
   max-min-improving segment?
5. Does suffix tightness imply all upper-tail inequalities exactly as stated,
   including indices inside tied blocks?
6. Does the published chain `exact n<=4 -> large core -> egalitarian stable ->
   PES=Lmax and coalitional monotonicity` have any missing domain-closure
   hypothesis when two exact games differ at one coalition?
7. Is the narrower inclusion "exact games through four players are exact
   partition games at Lmin" already known in the exact-partition or
   Lorenz-stable literature?
