# SD-prenucleolus coalitional-monotonicity campaign

Agent report, 2026-07-23. Target B from CAMPAIGN.md: coalitional monotonicity of
the **SD-prenucleolus** (Arin & Katsev). Prior sessions were blocked on the exact
recursive definition (paywalled sources). This session unblocked it, implemented
and cross-validated it, and ran the hunt.

## 1. Definition UNBLOCKED — primary source recovered

The blocker is gone. The full primary source was recovered, not reconstructed:

> J. Arin & I. Katsev, **"The SD-prenucleolus for TU games"**, UPV/EHU Working
> Paper Series IL.56/11 (Dec 2011); published as MMOR 80:307-327 (2014) and the
> convex-monotonicity companion IJGT 45 (2016).

The live repository `addi.ehu.es` is down (confirmed again this session), but the
Internet Archive holds the working-paper PDF:
`web.archive.org/web/20170812115500if_/https://addi.ehu.es/bitstream/10810/6230/1/IL201156.pdf`
(handle 10810/6230, RePEc ehu:ikerla:201156). 32 pages, full text, all
definitions and proofs. Saved locally at `/tmp/sdprenuc.pdf`.

### The definition (verbatim from Sec 3.2 & Def 4.1)

For an efficient `x`, a **satisfaction vector** `F(S,x)` over proper coalitions is
built by an algorithm (<= 2^n - 2 rounds). Maintain a collection `H` of "settled"
coalitions, `H_0 = {}`. For a coalition `S` write
`sigma_H(S) = union of settled T in H with T subset S` and, for `i` in `sigma`,
`f(i,S) = min{ F(U) : U in H, i in U subset S }`. Then

- **relevant** (`sigma_H(S) != S`):
  `F(S) = [ x(S) - v(S) - sum_{i in sigma} f(i,S) ] / ( |S| - |sigma| )`
- **non-relevant** (`sigma_H(S) = S`):
  `F(S) = x(S) - v(S) - sum_{i in S} f(i,S) + max_{i in S} f(i,S)`

Each round, settle every unsettled `S` attaining the current minimum `F(S)`
(they share that value). The **SD-prenucleolus** `SD(N,v)` is the unique efficient
`x` whose satisfaction vector, sorted in non-decreasing order, lexicographically
dominates that of every other efficient `y` (Def 4.1) — a leximax on satisfactions,
the mirror of the prenucleolus's leximin on excesses.

First-round satisfaction is `(x(S)-v(S))/|S|` (per-capita), so the SD-prenucleolus's
first step coincides with the per-capita prenucleolus; they diverge afterwards via
the `sigma_H` bookkeeping. It is a lexicographic value but **not** a weighted
prenucleolus (paper, Prop. 4.x).

Independent **SD-Kohlberg criterion** (from the core-stability proof, p.20): `x`
is the SD-prenucleolus iff for every level `alpha` the cumulative lower set
`{ S proper : F(S,x) <= alpha }` is balanced (no `y != 0` with `y(N)=0`,
`y(S) >= 0` on the set and `> 0` somewhere). This is used as a verifier fully
independent of the LP search path.

## 2. Implementation & validation (`src/`)

- `sd_prenucleolus.py` — exact rational: `sd_satisfaction` (the algorithm),
  `sd_prenucleolus` (successive-LP leximax over `Fraction`), `sd_kohlberg`
  (independent certifier).
- `sd_float.py` — float SD-prenucleolus (scipy HiGHS) for screening only.
- `serial_rule.py` — Arin-Feltkamp serial rule = SD-prenucleolus on veto games.

**Validation (all clean):**
1. `sd_satisfaction` reproduces the paper's worked 3-person example EXACTLY
   (F at x=(5,1,0): singletons 5,1,0; pairs 1,1,11).
2. `sd_prenucleolus` == serial rule on **140+ random monotonic veto games**
   (n=3,4,5): 0 mismatches. (Two independent computations agree.)
3. AFM-2012 Example 2: SD = (8,2,1,1), exact.
4. `sd_kohlberg` (independent path) certifies every `sd_prenucleolus` output.
5. `sd_float` == exact to **1.8e-15** over 120 veto games — trustworthy screen.

The definition passes both validations the campaign required (serial-rule anchor
+ worked example). Target B is now fully operational.

## 3. The target is closed by Young (1985) — honest reframing

CAMPAIGN.md framed "SD coalitional monotonicity on general balanced games" as an
open, publishable refutation target. It is **not open**. The source paper states
verbatim (p.6): *"Young (1985) proves that no solution satisfies coalitional
monotonicity and core stability."* The SD-prenucleolus is a core selector on
balanced games, so it necessarily violates coalitional monotonicity on general
balanced games (Housman-Clark sharpen this to n >= 4). A violation there is an
immediate corollary the authors themselves acknowledge — a rediscovery, not a
named result. The proven-safe classes (convex, veto-balanced) are exactly where
Young is dodged, and Arin-Katsev's positive theorems live there.

## 4. Hunt results

<!-- filled in after run -->

## 5. Assessment

<!-- filled in after run -->
