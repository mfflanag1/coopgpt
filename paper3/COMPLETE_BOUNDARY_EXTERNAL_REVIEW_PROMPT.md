# Hostile review — complete Lmin boundary-cardinality phase theorem

Please conduct a hostile, line-by-line mathematical and novelty review of the
new complete boundary-cardinality classification on draft PR #11.

## Exact review target

- Repository: `mfflanag1/counterexample-hunt`
- PR: `https://github.com/mfflanag1/counterexample-hunt/pull/11`
- Branch: `codex/human-n5-boundary-proof`
- Commit: `c097e2f`

Primary files:

- `coopgames/paper3/wrapper.pdf`, Theorem 5.50 and Corollary 5.51
  (numbers may shift);
- `coopgames/paper3/sections_leximin.tex`, labels
  `thm:lx-three-poorer-family` and `cor:lx-boundary-shape-phase`;
- `coopgames/paper3/COMPLETE_BOUNDARY_SHAPE_CLASSIFICATION.md`;
- `coopgames/src/verify_three_poorer_boundary_family.py`;
- `coopgames/results/three_poorer_boundary_family.json`.

The broader dependency chain is the strict-cover lemma, balanced-trace
transport theorem, unique-richest theorem, human two-poorer theorem, and
internal-sacrifice family immediately preceding the target theorem in the
paper.  Audit those dependencies if any cited implication is unclear.

## Claims to rederive rather than trust

1. For every `m>=3,h>=2`, check that every displayed generator in `(TH)` has
   total `m+3h+1`, and that the lower envelope is an exact game.
2. Check singleton normalization player by player, especially the endpoint
   `h=2` where `H\{r1,rh}` is empty and `Q` may also be empty.
3. Recompute all four values in `(TH-T)` directly from every generator; do
   not infer them from the verifier.
4. Audit the progressive Lmin proof:
   - complement faces pin every `j in Q` at one;
   - `H+p3` pins `p1,p2` at one;
   - `H+p1` pins `p3` at two;
   - efficiency equalizes `H` at three.
   Look for any implicit assumption that all poorer players belong to one
   payoff stratum; they do not.
5. Rederive the proposed Lmax point with `epsilon=1/(h+1)`.  In its
   dimension-free core-feasibility proof, verify

   ```text
   phi(S)-z(S) = (t-hy)/(h+1),
   a(S)-z(S)   = epsilon(y+t)+2u-3
   ```

   and confirm that deleting the common `Q` coordinates and ignoring the
   `q^j` rows is logically valid for proving core feasibility.
6. Check every successive Lmax forcing step:
   - `H+p3` forces ceiling `3-epsilon` on `p3` and `H`;
   - `H+p1` forces `p1=2-epsilon` at the next ceiling;
   - `H+p1+j` forces every `j in Q` to one;
   - efficiency fixes `p2=epsilon`.
   Confirm uniqueness and the distance `||Lmin-Lmax||_1=4h/(h+1)`.
7. Audit indecomposability separately:
   - for `Q` nonempty, a fixed `j in Q` has pair worth one with every other
     player;
   - for `Q` empty, positive pairs connect everyone except `p2`, and
     `v({p1,p3,rh})=4<5=v({p1,p2,p3,rh})` attaches `p2`.
8. Audit the complete phase diagram as an exhaustive quantifier argument:

   ```text
   m_min(1)=4,
   m_min(2)=m_min(3)=3,
   m_min(h)=2 for h>=4.
   ```

   Verify that the opposing-sign theorem excludes all `m=1`; the
   unique-richest theorem excludes exactly the remaining `h=1,m<=3`; the
   human two-poorer theorem excludes exactly `m=2,h<=3`; and the three
   indecomposable families cover every admitted pair.

## Independent reproduction

From `coopgames/` run:

```bash
python src/verify_three_poorer_boundary_family.py \
  --max-poorer-side 6 --max-richer-suffix 6 \
  --exact-replay-through-players 6 \
  --output /tmp/three_poorer_boundary_family.json
cmp /tmp/three_poorer_boundary_family.json \
  results/three_poorer_boundary_family.json
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```

Please independently implement at least the `(m,h)=(3,2),(3,3),(4,2)` games
if possible.  Solver agreement is corroboration, not a substitute for the
human universal proof.

## Novelty questions

Search exact games, exact-partition games, egalitarian/core Lmin and Lmax,
minimal exact-balanced collections, balanced hypergraphs, Kohlberg-type
criteria, and replication/indecomposability terminology.  Determine whether
any prior source contains:

- a classification of exact-partition failure by the cardinalities on the two
  sides of an Lmin payoff boundary;
- the staircase `4,3,3,2` above;
- the universal indecomposable `m>=3,h>=2` family;
- its closed-form Lmax;
- the balanced-trace transport bridge used for the lower bounds.

Do not credit novelty merely because keyword search fails.  The paper already
acknowledges as prior art the exact-partition condition, its Lorenz
consequence, Lmin/Lmax, exact balancedness, and minimal balanced collections.

## Requested verdict

Return separate verdicts for:

1. universal-family correctness;
2. Lmin proof;
3. Lmax proof;
4. indecomposability;
5. exhaustive phase classification;
6. novelty/significance.

Use `verified`, `verified with qualifications`, or `not verified`; give exact
file and line references for every objection, and label each issue fatal,
repairable, or expository.  State every command and independent computation
actually performed.
