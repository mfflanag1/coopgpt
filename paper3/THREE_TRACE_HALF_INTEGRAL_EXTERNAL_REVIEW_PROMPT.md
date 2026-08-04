# Hostile external review request: complete three-column obstruction tier

## Non-novel component and claimed contribution

Do not assess the three pair traces or their half weights as a novelty claim.
They are classical minimal-balanced-collection geometry (the blown-up
three-cycle); minimal and minimal exact-balanced collections are treated by
Lohmann--Borm--Herings (2012) and Laplace
Mermoud--Grabisch--Sudhölter (2025). The candidate contribution submitted
for review is the bridge from that geometry to Lmin transport: the forced
poorer-player labeling, the exact-singleton-face proof of the sharp atom
thresholds, and the converse exact-game realization for every admissible
triple. Please look specifically for prior formulations of that combined
statement.

Please review this as a potentially false theorem, not as exposition to be
polished.  Try to break both directions: the abstract classification of every
underloaded three-column packet and the converse exact-game realization.
Also audit both lexicographic solution claims, the complete tight-coalition
classification, half-integrality, and the claimed consequence for the
proposed universal co-singleton-minor conjecture.

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
  --max-central-block 2 \
  --max-block 4 \
  --output results/three_trace_half_integral_family.reproduced.json
cmp results/three_trace_half_integral_family.json \
    results/three_trace_half_integral_family.reproduced.json
cd paper3
latexmk -pdf -interaction=nonstopmode -halt-on-error wrapper.tex
```

The staged exact Lmin/Lmax replay for the seven-player base case is slow; a
run of roughly two minutes is expected.

## Abstract classification claims to audit

Under balanced-trace transport at a slack two-poorer Lmin boundary, take a
lifted extreme packet with gaining-player load below one and exactly three
positive tight-coalition columns.  Please verify or refute:

1. Every rich row corresponds to a nonempty subset of three positive cover
   weights whose sum is one.  Singleton patterns force integrality; a triple
   pattern forces rank one; hence fractional rank three forces exactly the
   three pair patterns and weights `(1/2,1/2,1/2)`.
2. The transport inequality implies `r_a<r_b<1`.  Half-integrality then
   forces `r_a=0,r_b=1/2`, so no supported coalition carries the losing poor
   player and exactly one carries the gaining player.
3. Writing the pair-pattern atoms as `C,A,B` and labeling the `A union B`
   column by the gaining player, `|A|=1` or `|B|=1` produces a safe rooted
   tight cover forbidden by exact singleton faces.  Therefore
   `|C|>=1,|A|>=2,|B|>=2` and five rich players are necessary.
4. These arguments really classify every support-three underloaded packet;
   identify any missing degeneracy, repeated row type, full trace, or
   alternative poor labeling.

## Converse realization claims to audit

Let `N={a,b} disjoint-union H`, where
`H=C disjoint-union A disjoint-union B`, `|C|>=1`, and `|A|,|B|>=2`.
Define `P` by

```text
x>=0, x(N)=2+2|H|,
x(C union A)>=2(|C|+|A|),
x(C union B)>=2(|C|+|B|),
x({b} union A union B)>=1+2(|A|+|B|),
```

and define `v(S)=min_{x in P}x(S)`.

Please verify or refute each item separately:

5. Every singleton has minimum zero, including when `|C|>1`; `core(v)=P`,
   and compact attainment
   makes `v` exact.
6. Adding the three inequalities yields `2x_a+x_b<=3`, which proves
   `Lmin(v)=(1,1,2,...,2)` by the stated two-stage argument.
7. The displayed exact-`H` point proves `v(H)=2|H|-1`, so the richer suffix
   has slack one.
8. The average-two face and subsequent forcing prove
   `Lmax(v)=(1,1,2,...,2)`.
9. Normal-cone duality at the positive point `phi` proves that the three
   defining coalitions are the complete list of proper `phi`-tight
   coalitions.  Check the sign convention for the efficiency multiplier and
   whether degeneracy can add a zero-one normal omitted by the proof.
10. The three rich traces have unique exact-cover weights
   `(1/2,1/2,1/2)` and form a support-minimal circuit.
11. The exact-balanced identity

   ```text
   1_(C union A)+1_(C union B)+1_({b} union A union B)
   +1_{a}-1_H=1_N
   ```

   is correct and its slack budget is saturated.
12. At a vertex, at most one coordinate per exchangeable block is positive,
   and every relevant nonsingular subdeterminant has absolute value one or
   two.  Therefore scaling by two really produces an integral exact game.
13. Under the intended trace-minor operations (row deletion/contraction and
   column deletion/identification), a three-column active system cannot
   contain the four-column co-singleton packet.  Flag any nonstandard or
   undefined use of “minor.”
14. Determine whether either the support-tier classification, the exact-game
    realization, or its Lmin/Lmax behavior is
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
