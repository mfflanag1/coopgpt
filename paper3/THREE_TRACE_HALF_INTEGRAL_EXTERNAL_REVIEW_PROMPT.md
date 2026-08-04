# Hostile external review request: three-trace half-integral obstruction

Please review this as a potentially false theorem, not as exposition to be
polished.  Try to break the construction, the exactness argument, both
lexicographic solution claims, the complete tight-coalition classification,
the half-integrality assertion, and the claimed consequence for the proposed
universal co-singleton-minor conjecture.

## Authoritative files

- Human theorem and proof:
  `coopgames/paper3/THREE_TRACE_HALF_INTEGRAL_OBSTRUCTION.md`
- Manuscript version, Theorem `thm:lx-three-trace-obstruction`:
  `coopgames/paper3/sections_leximin.tex`
- Compiled paper:
  `coopgames/paper3/wrapper.pdf`, Theorem 5.81 near pages 64--65
- Exact verifier:
  `coopgames/src/verify_three_trace_half_integral_family.py`
- Reproducible output:
  `coopgames/results/three_trace_half_integral_family.json`
- Prior first-obstruction theorem whose proposed converse is affected:
  `coopgames/paper3/H4_FIRST_OBSTRUCTION_CLASSIFICATION.md`
- General obstruction context:
  `coopgames/paper3/INTEGRAL_TRACE_OBSTRUCTION.md`

## Reproduction

From `coopgames/`:

```bash
PYTHONPATH=src python src/verify_three_trace_half_integral_family.py \
  --max-block 4 \
  --output results/three_trace_half_integral_family.reproduced.json
cmp results/three_trace_half_integral_family.json \
    results/three_trace_half_integral_family.reproduced.json
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```

The staged exact Lmin/Lmax replay for the seven-player base case is slow; a
run of roughly two minutes is expected.

## Claims to audit

Let `N={a,b} disjoint-union H`, where
`H={c} disjoint-union A disjoint-union B` and `|A|,|B|>=2`.  Define `P` by

```text
x>=0, x(N)=2+2|H|,
x({c} union A)>=2(|A|+1),
x({c} union B)>=2(|B|+1),
x({b} union A union B)>=2|H|-1,
```

and define `v(S)=min_{x in P}x(S)`.

Please verify or refute each item separately:

1. Every singleton has minimum zero, `core(v)=P`, and compact attainment
   makes `v` exact.
2. Adding the three inequalities yields `2x_a+x_b<=3`, which proves
   `Lmin(v)=(1,1,2,...,2)` by the stated two-stage argument.
3. The displayed exact-`H` point proves `v(H)=2|H|-1`, so the richer suffix
   has slack one.
4. The average-two face and subsequent forcing prove
   `Lmax(v)=(1,1,2,...,2)`.
5. Normal-cone duality at the positive point `phi` proves that the three
   defining coalitions are the complete list of proper `phi`-tight
   coalitions.  Check the sign convention for the efficiency multiplier and
   whether degeneracy can add a zero-one normal omitted by the proof.
6. The three rich traces have unique exact-cover weights
   `(1/2,1/2,1/2)` and form a support-minimal circuit.
7. The exact-balanced identity

   ```text
   1_({c} union A)+1_({c} union B)+1_({b} union A union B)
   +1_{a}-1_H=1_N
   ```

   is correct and its slack budget is saturated.
8. At a vertex, at most one coordinate per exchangeable block is positive,
   and every relevant nonsingular subdeterminant has absolute value one or
   two.  Therefore scaling by two really produces an integral exact game.
9. Under the intended trace-minor operations (row deletion/contraction and
   column deletion/identification), a three-column active system cannot
   contain the four-column co-singleton packet.  Flag any nonstandard or
   undefined use of “minor.”
10. Determine whether the exact-game realization or its Lmin/Lmax behavior is
    already in the exact-partition, exact-balancedness, egalitarian-core, or
    balanced-hypergraph literature.  The underlying blown-up odd triangle is
    classical and must not itself be presented as new.

## Calibration requested

Please end with one of:

- mathematically false;
- correct but materially overstated;
- correct candidate theorem needing a terminology/literature revision;
- correct and plausibly novel subject to a definitive literature search.

Also state whether this is merely a useful counterexample to one research
route or a material structural advance for the paper.  Do not call it a major
field breakthrough without a separate novelty assessment.
