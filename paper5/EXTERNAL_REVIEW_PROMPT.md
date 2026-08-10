# Hostile review — maximal divergence of Lmin and Lmax in exact games

> **Update, 2026-08-10.** The six-player upper bound is no longer open in the
> current branch: a new direct table-free computer-assisted theorem proves
> `s(6)=2/3`. Review that claim first using
> `EXTERNAL_REVIEW_S6_DIRECT_BOUND.md`. Where this older prompt says that
> `s(6)` is open or only enumerated, the focused prompt and current manuscript
> supersede it. All novelty and correctness claims remain conditional on
> hostile external review.

Please review the standalone manuscript:

```text
paper5/divergence.pdf    (30 pages)
paper5/divergence.tex
```

Repository branch: `codex/fixed-n-handover-facets`.  Record the exact reviewed
`HEAD` in the report rather than relying on an embedded historical commit.
The companion manuscript is `paper4/threshold.pdf`; this paper cites it for
the four-player rigidity and reuses its lower-envelope technique, but is
otherwise self-contained. Both papers are under preparation simultaneously.

Take an adversarial stance throughout. The author's own assessment is that
this is specialist work whose novelty is conditional on review, not a
breakthrough; treat every "new" claim as a claim to be broken.

## Main claim

For a singleton-normalized exact TU game put

```text
rho(v) = ||Lmin(v) - Lmax(v)||_1 / v(N),
s(n)   = sup { rho(v) : v exact on n players, v(N) > 0 }.
```

Then `rho <= 2` always, `s(n) = 0` for `n <= 4`, and `sup_n s(n) = 2`: the two
canonical egalitarian core selections can have asymptotically disjoint
supports. The witnesses are an explicit two-parameter family `G(p,k)` with

```text
rho(G(p,k))     = 2(p(k-1)-1) / (k(p+1)),
2 - rho(G(p,k)) = 2n / (k(p+1)),        n = p+1+k,
s(n)           >= 2 - 8n/(n^2 - (n mod 2)).
```

The ratio reaches `1` at eight players and exceeds it from nine on. At `n=5`
the family is not sharp: the true two-generator maximum is `1/2`.

## Priority targets

These are where the author most expects to be wrong. Spend your effort here
before anything else.

### 1. The master family: closed forms and membership (Theorem 13, Lemma 14)

Everything numerical in the paper stands on these two.

- **Leximin (§4.2).** From the key cap (KC) `x_1 + ... + x_p + x_b <= p` for
  every `b ∈ B`, the proof gets `mu <= p/(p+1)`, then argues that equality
  forces *all* of `x_1,...,x_p` and *every* `x_b` to `p/(p+1)`, then fixes the
  head by efficiency. Check the "for every `b`" quantifier step, the arithmetic
  `x_0 = p^2(k-1)/(p+1)`, and — this is the load-bearing move — the inference
  "the max-min allocation is unique, and a unique max-min allocation is a
  fortiori the leximin allocation". Is that inference valid as stated?
- **Leximax-min (§4.3).** The two-case analysis on `M <= p-s` versus
  `M > p-s`, the inequality (4)
  `pk <= M + s + k·min(M, p-s)`, and then the claim that equality can occur
  *only* in Case A **with every inequality used tight**, forcing `x_0 = M`,
  `x_b = M` for all `b`, and `s = p/k`. Verify that "every inequality used
  tight" is a legitimate reading of (4) rather than an assumption, and check
  the consistency computation `p - s = p(k-1)/k = M`.
- The **next leximax stage**: minimizing the maximum of the "ones" subject to
  their sum being `p/k` has unique optimum `1/k` each. Check that the earlier
  stages are genuinely settled before this one — i.e. that the ones really do
  occupy the last `p` positions of the decreasing rearrangement (the paper
  cites `p/k <= p(k-1)/k` for `k >= 2`, note equality at `k = 2`).
- **Lemma 14 (membership).** Independently recheck all four cases
  (`eps = 0, j = 0`; `eps = 0, j >= 1`; `eps = 1, j <= k-1`; `eps = 1, j = k`)
  for **both** allocations, including every divide-by-`(k-1)` and
  divide-by-`k` step, and the claim that the tight coalitions are **exactly**
  (T1), (T2), (T3) — the exactness of that list, not just its validity.
- **Edge cases.** `p = 1`; `k = 2`; `D = p(k-1) - 1 = 0` (i.e. `G(1,2)`,
  Remark 18, where `rho = 0`); and whether any step silently assumes `k >= 3`
  or `p >= 2`. An earlier version of this work is recorded as having had a
  membership gap in a "proved for all `(p,k)`" claim; assume the repair may be
  incomplete.

### 2. The deficit identity (Corollary 15, Remark 16)

- The algebra `2 - 2(p(k-1)-1)/(k(p+1)) = 2(k+p+1)/(k(p+1))`.
- Remark 16 rederives the same identity from Lemma 3 (ceiling and overlap) by
  computing the coordinatewise minima. Do the two derivations agree, and is
  the displayed overlap sum
  `p(k-1)/k + p/k + kp/(p+1) = p + kp/(p+1)` correct? Check in particular
  that the coordinatewise minimum at the head is `p(k-1)/k` and at each member
  of `B` is `p/(p+1)` — i.e. that the comparison goes the way the paper says
  at every coordinate, for all `p, k` in range.
- **Theorem 17** then optimizes `k(p+1)` at fixed sum `n`. Check the balanced
  split satisfies the constraints `k >= 2`, `p >= 1` for every `n >= 4`, and
  check Table 1 entry by entry.

### 3. The two-generator duality (Theorem 6)

- Identity (1), `T - v(S) = f(N \ S)`, from modularity and the common total,
  and the complementation involution that turns lower bounds into upper caps.
- The claim that `x >= 0` is *exactly* the family of singleton inequalities.
- **Novelty question, and the sharpest one in the paper.** The text concedes
  that "the duality is fully general: for *any* singleton-normalized game,
  setting `f(S) := T - v(N\S)`, the same complementation gives
  `Core(v) = {x >= 0 : x(N) = T, x(S) <= f(S)}`". That general statement is
  the standard identity between the core of `v` and the anticore of the dual
  game `v*(S) = v(N) - v(N\S)`. **Is the paper's disclosure adequate, or
  should the dual game be named and cited?** And is the residual
  two-generator content — the computation `f = max(g,h)` — of any weight at
  all, or is it immediate from Lemma 4?
- Lemma 4 (support disjointness) and the deletion of null players: is the
  reduction to `A ∪ B = N`, `A ∩ B = ∅` harmless for both selections?

### 4. The `n = 5` flat-split hand proof (Theorem 21)

This is the paper's only nontrivial hand computation on a specific game, and
it carries Conjecture 22 and much of §5.

- Recompute `w = min(g^1, g^2)` for `g^1 = (1,0,0,1,2)`, `g^2 = (0,1,3,0,0)`
  on all 32 coalitions.
- Verify both flat splits: `w({1,2}) = 1` with `w({3,4,5}) = 3`, and
  `w({2,4}) = 1` with `w({1,3,5}) = 3`, each summing to `w(N) = 4`; and hence
  that `x_1 + x_2` and `x_2 + x_4` are constant on the core, giving (6):
  `x_1 = x_4 = s`, `x_2 = 1-s`, `x_3 + x_5 = 3-s`, `s ∈ [0,1]`.
- **Leximin.** `min_i x_i <= min(s, 1-s) <= 1/2` with equality forcing
  `s = 1/2` — check that the *first* leximin stage is genuinely settled at
  `1/2` and that the continuation splitting `5/2` evenly over players 3 and 5
  is forced rather than merely feasible.
- **Leximax-min.** `max_i x_i >= (x_3+x_5)/2 = (3-s)/2 >= 1`, equality forcing
  `s = 1` and then `x_3 = x_5 = 1`. Check that `(1,0,1,1,1)` is in the core
  and that no other core point achieves ceiling `1`.
- Confirm `||Lmin - Lmax||_1 = 2` and `rho = 1/2`.

### 5. The two finite-check theorems (Theorems 24 and 25)

**These are declared proof dependencies**, not bug audits — see the
Reproducibility note and the §7 heading "Proved by exhaustive finite check".
Review them as proofs, and hold them to the standard of proofs.

**Theorem 24 (one-coalition certificates at five players: `mu = lambda` and
`M = nu`).**

- The LP-duality reduction: `M = nu` fails iff some fractional cover `w` has
  `sum_S w_S h(S) < h(N)` with `h(S) = nu|S| - v(S) >= 0`; likewise for `mu`
  with `f'(S) = f(S) - lambda|S|`. Derive both reductions yourself.
- The attainment argument: "both objectives are nonnegative on the cover
  polyhedron, which is pointed with recession cone the nonnegative orthant, so
  each minimum is attained at a vertex". Check pointedness, check that the
  recession cone is what is claimed, and check that nonnegativity of the
  objective is what rules out the unbounded direction.
- The count: **2287 vertices** of the five-player cover polyhedron, each of
  support at most five. Recompute this number independently — it is a
  standalone combinatorial fact and a cheap place to catch an error.
- The exactness encoding: **280 inequalities** obtained by applying all
  permutations to the sixteen indecomposable min-semi-balanced systems on five
  players from Studený–Kratochvíl. Is that the correct facet description of
  the cone of exact games on five players? Is 280 the right count after
  deduplication? The paper says the description "was validated in both
  directions against independent exactness tests" — check that claim.
- The reduction to **1142 symmetry classes** of (vertex, anchor) pairs per
  side, and the claim that each is infeasible in exact rational arithmetic.
  Is the symmetry reduction sound (does the group act as claimed on both the
  vertex and the anchor)? Is fixing "a coalition attaining `nu` (resp.
  `lambda`)" as an anchor a complete case split?
- The homogeneity step `v(N) = 1` "free by homogeneity".
- The calibration remark: deleting the 280 exact-cone inequalities makes 361
  (resp. 339) over-covering classes feasible — so exactness, not the shape of
  the certificate, is what forces the property.

**Theorem 25 (the extremal configuration is pinned: `f({j}) >= T/8`).**

- The hypotheses: `Lmin` strata pattern `(3,2)`, `Lmax` strata pattern
  `(1,4)` with the singleton stratum at zero, at player `j`.
- The step "By the size bound from the `Lmax` vector's core membership, every
  other coalition has `f(S)/|S| >= T/8`" — reconstruct it.
- The invocation of Theorem 24 to place `mu = f({j}) < T/8`, and the
  unexplained "**two-line argument** forces `j` into the poor stratum".
  **That argument is not written out. Please supply it or report that it
  cannot be supplied** — it is a gap in a stated proof.
- The dual certificate: **354 vertices** of a dual polyhedron "involving no
  game data", and **10,974** exact programs, all infeasible. Is the claim that
  the dual polyhedron involves no game data correct? Is the enumeration
  complete?
- The **ablation** claim: the check goes through from core membership of the
  `Lmax` vector, core membership of the `Lmin` vector, and the pinning alone —
  so a direct argument exists that uses neither the facet description nor the
  `M`-side of Theorem 24. If so, why is the direct argument not given?

For both theorems, judge whether the write-up is sufficient for a reader to
*reconstruct* the check, or only to *believe* it. Say which.

### 6. The conditional corollary and its two hypotheses (Corollary 26)

The corollary closes the extremal configuration at `n = 5` **modulo two
hypotheses**: (a) the starved player is `Lmin`-poor, and (b) some coalition
attaining `nu` has three players.

- Check the derivation chain: `M = 1/4` from the `Lmax` pattern; `f(S) >=
  (|S| - [j ∈ S])/4 >= |S|/8` for `S ≠ {j}` from core membership; `f({j}) >=
  1/8` from Theorem 25; hence `lambda >= 1/8`. Then the `M`-side of
  Theorem 24 gives `nu = M = 1/4`, a three-player `nu`-attaining `S_0` has
  `v(S_0) = 3/4` and `f(N \ S_0) = 1/4` on two players, so `lambda <= 1/8`.
- **The step `mu <= T/6`** appears without derivation in the final sentence.
  Where does it come from, and is it needed?
- The telescoping `||Lmin - Lmax||_1 = T - 4mu = T/2`. Verify it is forced by
  the strata, the floor and the totals, and that the two displayed allocations
  are indeed the unique consistent pair.
- **The status of (a) and (b).** The paper says both hold in "every
  configuration game examined (53 of 53)", that (a) "is automatic in the proof
  of Theorem 25 itself, where it is derived under the failure assumption", and
  separately that an `Lmin`-rich starved player was "never observed, 0 of 68".
  Is the (a)-is-automatic claim consistent with (a) being listed as an open
  hypothesis? And do `53` and `68` refer to the same population? Report any
  circularity you find between Theorem 25 and Corollary 26.
- The paper states that dropping the `(3,2)` pinning makes the same programs
  satisfiable, with models that are genuine exact games having
  `T - v(N \ {i}) = T/16` but `Lmin = Lmax`. Check that this really shows the
  hypothesis is essential rather than that the bound is an artifact of it.

### 7. Enumeration-scope caveats

The paper's central honesty commitment is the identity
**complete-to-total-`T` = complete-to-denominator-`T`**. Audit it.

- §5.1 "What is complete": because `rho` is scale-invariant, every
  two-generator game with rational generators has a unique primitive integer
  representative, so enumeration to `T_max` is complete exactly for rational
  shapes of denominator at most `T_max`, and says nothing about finer
  denominators or irrational generators. **Is the primitive-representative
  argument correct, and is the conclusion drawn the strongest available?**
- Consequently Table 2's entries are **maxima over the enumerated range, not
  values of `s_2(n)`**. Check that no later statement upgrades a table entry
  to a supremum. In particular check the phrase "the bound is attained on the
  two-generator class at `n = 6,7,8` by complete enumeration" in §1 and the
  "live candidate" formulation in §5.1.
- The hill-climbing probes (resolutions `1/60`, `1/56`, `1/64`), the seeded
  `c`-space climbs (Lemma 20), and the explicit admission that unseeded
  `c`-space restarts reach only `1/3` at `n = 6` and "certify nothing". Is
  the local-optimality claim at `n = 5,6,7` stated at the right strength?
- Observation 10's "smallest counterexample" claim rests on the enumeration,
  not on a proof. Is that flagged everywhere it is used?
- The `n = 5` extremal-class structure (§5.3): stratum compositions `(3,2)`
  and `(1,4)`, `|supp(Lmax)| = 4`, uniqueness up to permutation, the
  refutation of the flat-split "seesaw" invariant (76 of 107 have a flat
  split; 31 attain `1/2` with none). All computational over 360 profiled
  games; none proved. Check that the text never treats them as more.

### 8. The claims ledger (§7)

§7 sorts every statement into **Proved / Proved by exhaustive finite check /
Enumerated, not proved / Conjectured / Not claimed**. For each entry, decide
whether the label is correct, and flag anything that is:

- labelled *proved* but depends on a computation, or vice versa;
- missing from the ledger entirely;
- claimed in the abstract or introduction at a strength the ledger does not
  support. Compare the abstract sentence by sentence against the ledger —
  especially "we prove that at five players **both** egalitarian levels are
  certified by single coalitions" and "the complete two-generator enumeration
  finds nothing above it".

Also check the five open problems as stated, and whether any of them is in
fact settled by material already in the paper.

## Further questions to answer hostilely

9. Lemma 1 (lower-envelope generation) **and its converse**. The converse
   asserts every exact singleton-normalized game is a lower envelope of its
   core vertices. Check it, including the nonnegativity and common-total
   claims.
10. Lemma 3 (ceiling and overlap) and the equality case: `rho = 2` iff
    disjoint supports.
11. Theorem 7 (`mu <= lambda`) and Conjecture 8. The LP-duality reduction to
    the fractional-cover inequality (2), and Proposition 9 proving (2) for
    balanced covers. Is the displayed over-covering residual
    `max(sum_A g_i e_i, sum_B h_i e_i) - lambda sum_N e_i` correct, and is the
    diagnosis of why it does not close ("each inner sum dominates `lambda`
    times its *own* block's excess but not the other block's") accurate?
12. Observation 10 and the empty-part convention. The paper spells out that a
    pair `(P,Q)` with an empty part contributes `min(·,0) = 0` and is inactive,
    and warns that reading an empty part as `+infinity` gives a different and
    wrong value. Confirm the stated convention is the one used in the proof,
    in the displayed counterexample, and in the claim that the right-hand side
    of (3) equals `nu` on two-generator games.
13. Verify the smallest counterexample at `n = 6`, `T = 5`:
    `g = (3,2,0,0,0,0)`, `h = (0,0,2,1,1,1)`, `Lmin = (1, 2/3, 4/3, 2/3, 2/3,
    2/3)`, `Lmax = (6/5, 4/5, 6/5, 3/5, 3/5, 3/5)`, `M = 6/5` against a bound
    of `1`. Also check the second class `g = (3,1,1)`, `h = (2,2,1)`.
14. Proposition 23 (covering obstruction) and the accompanying claim that **no
    balanced collection can witness `M > nu`**. Check the computation
    `sum_S w_S (nu|S| - v(S)) >= nu·n - T` and the use of core-nonemptiness.
    Check the worked instance: the four `nu`-tight sets `{2,3}, {1,3,4},
    {1,3,5}, {1,3,6}` covering `N` with per-player excess `(2,0,3,0,0,0)`, and
    player 2 blocking every balanced subfamily.
15. §6.2: the failure of `||Lmin - Lmax||_1 <= 4(n-4)mu` from `n = 9`, and the
    structural reason offered (`mu = p/(p+1) < 1` bounded while the gap grows
    like `2T`). Recompute the four table rows.
16. §6.3: the majorization non-monotonicity counterexample at `n = 7`, `T = 10`
    (`g = (0,5,0,3,2,0,0)`, `h = (1,0,2,0,0,5,2)`, `rho = 1/5`; smoothing
    `(5,2) -> (4,3)` collapses `rho` to `0`). Recompute both games and both
    allocation pairs. Does a single verified counterexample really close the
    route, or only the naive form of it?
17. The introduction's footnote deriving leximin- and leximax-optimality from
    Lorenz domination with equal totals (partial sums and their complements).
    Check it.

## Prior art

Treat as prior art, and do not credit the paper with any of it: exactness
theory and the exact cone; lower-envelope exactification; the
characterizations of the egalitarian core selections (Arin–Iñarra,
Arin–Kuipers–Vermeulen); the large-core/PES chain (Biswas et al.,
Dietzenbacher); exact partition and its Lorenz consequence
(Llerena–Mauri, Sánchez-Soriano et al.); Dutta–Ray; the facet description of
the exact cone (Studený–Kratochvíl); and the standard core/anticore dual-game
identity underlying the general form of Theorem 6.

**Search specifically for:**

- any prior quantitative comparison of `Lmin` and `Lmax` (or of leximin and
  min-max / "lexicographically smallest decreasing rearrangement") on TU
  games — a bound, an example of divergence, or a supremum. Under any
  terminology: leximin core, egalitarian core, lexicographic maximin,
  min-max core selection, `mu`-value-style bottleneck arguments.
- whether `sup_n s(n) = 2` (asymptotic support disjointness of two
  egalitarian selections) is anticipated anywhere in fair-division or
  cost-allocation literature, where the analogous phenomenon for other pairs
  of solutions is studied.
- whether the one-coalition-certificate property (`mu = lambda`, `M = nu`) is
  known under bottleneck / minimum-ratio / covering terminology, and whether
  its failure at six players is recorded.
- whether the family `G(p,k)` or its cap structure coincides with a known
  family (glove markets, assignment games, bankruptcy-style caps).

The candidate new content, as the paper states it: the two-generator core
duality **with its one-sided floor certificate**; the family `G(p,k)` with
closed forms and deficit identity; the evaluation `sup_n s(n) = 2`; the
identification of the `n = 5` anomaly with a hand proof; the one-coalition
certificate theorem and the pinned extremal configuration at five players;
and the two closed routes of §6.

## Exact reproduction

From `coopgames/` at commit `3587e55`:

```bash
cd paper5
pdflatex -interaction=nonstopmode -halt-on-error divergence.tex
pdflatex -interaction=nonstopmode -halt-on-error divergence.tex
```

**Status of the programs.** Everything in `../src` and `../results` is a bug
audit, not proof evidence — **except** the two finite exact checks described
in the proofs of Theorems 24 and 25, which are declared proof dependencies.
Their drivers and outputs, together with the two-generator and
three-generator enumeration drivers behind Table 2 and §5.3, are supplied
with this packet as a separate archive. If any is missing, say so in your
report and downgrade the corresponding statement rather than assuming it.

Independently, please:

- recompute `Lmin` and `Lmax` for every displayed game in the paper, in exact
  rational arithmetic, by a method of your own choosing;
- recompute the closed forms of Theorem 13 and the tight-set list of
  Lemma 14 for a spread of `(p,k)` including `(1,2)`, `(1,3)`, `(2,3)`,
  `(3,4)`, `(4,5)`;
- reconstruct the 2287-vertex and 354-vertex counts of §5.4 from scratch.

The paper reports that one library simplex implementation cycles on these
degenerate programs and was not used for any reported number, and that at
least two methods agree on every displayed allocation. If your own solver
disagrees with any displayed value, report the disagreement before assuming
it is yours.

## What to deliver

Return separate verdicts for:

1. the two-generator duality and the floor certificate (Theorems 6, 7,
   Proposition 9) **and the adequacy of the generality disclosure**;
2. the master family: closed forms and membership (Theorem 13, Lemma 14);
3. the deficit identity and the supremum (Corollary 15, Remark 16,
   Theorem 17, Table 1);
4. the `n = 5` hand proof (Theorem 21);
5. the `M`-side asymmetry and its smallest counterexample (Observation 10,
   Proposition 23);
6. the one-coalition certificate theorem (Theorem 24) **as a proof**;
7. the starvation bound and the pinned configuration (Theorem 25,
   Corollary 26) **including the two hypotheses and the missing two-line
   argument**;
8. the enumeration-scope caveats and Table 2 (§5.1);
9. the two closed routes (§6.2, §6.3);
10. the honesty of the claims ledger (§7);
11. novelty and field significance.

Use `verified`, `verified with qualifications`, or `not verified` for each.
Classify every issue as **fatal**, **repairable**, or **expository**, and
cite exact file lines (`divergence.tex:NNN`). Where you find a repairable
error, state the repair. Where you find a fatal one, state what survives.

Finally: is the paper's own self-assessment in §7 calibrated, over-claimed,
or under-claimed? And is the open upper bound a fatal weakness for
publication or an acceptable one, given that the lower side is exact?
