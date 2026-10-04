# Static review of result.md: mixed inequality (M) and its obstruction

**Verdict: revise.** This review is static: I read only the supplied text, ran nothing, and opened no files. The mathematical checks below are my own hand derivations.

Inequality (M) appears to be true, but the proof given for it is invalid. The obstruction is correct but narrower than its "exact"/"insufficient" labels suggest. The UNKNOWN status is honest and should stay.

## Findings

### 1. Major: the proof of (M) fails at the middle-term indicator inequality

The proof crosses the cuts as (X∩X′, Y∪Y′) and (X∪X′, Y∩Y′) and claims a pairwise indicator inequality "by direct inspection". That inequality is false.

- **Failing case:** take i ∈ X∖X′ and j ∈ R∩R′ with j ∈ Y∖Y′. The left side is 0+0. The right side has second term 1, because i ∈ X∪X′ and j ∈ (R∩R′)∖(Y∩Y′).
- **Concrete instance:** one row i and one column j, Q=Q′={i}, R=R′={j}, r_i=c_j=1, p_ij=p≥1. Both ({i},{j}) (value c=1) and (∅,∅) (value r=1) are minimum cuts. The candidate's crossed cuts are (∅,{j}) with value r+c=2 and ({i},∅) with value p. Their sum is 2+p, which exceeds 2.

So the step "sum of the two original minimum-cut values ≥ sum of the two crossed-cut values" is false for arbitrary minimizers, which is what the proof chooses. Identities (2) and (3) are correct; only the middle term breaks.

### 2. The statement (M) itself looks correct and is repairable

The correct uncrossing is the ordinary one on source-side sets: intersection for (Q∩Q′, R∪R′) and union for (Q∪Q′, R∩R′). It needs the unrestricted cut formula, with X⊆I and Y⊆J:

w(Q,R) = min [ r(Q∖X) + p(X, J∖Y) + c(Y∩R) ]

Absent columns then sit on the source side at zero cost. With cuts (X∩X′, Y∩Y′) and (X∪X′, Y∪Y′), I checked three termwise inequalities:

- **Rows:** 1[Q∖X] + 1[Q′∖X′] ≥ 1[(Q∩Q′)∖(X∩X′)] + 1[(Q∪Q′)∖(X∪X′)].
- **Columns:** 1[Y∩R] + 1[Y′∩R′] ≥ 1[Y∩Y′∩(R∪R′)] + 1[(Y∪Y′)∩R∩R′].
- **Middle:** p(X, J∖Y) is submodular in the source-side set in the usual way.

Within the candidate's restricted formula (1), naive (X∩X′, Y∩Y′) also fails. The Y-set for (Q∩Q′, R∪R′) must be (Y∩Y′)∪(Y∖R′)∪(Y′∖R). A revision must write this out in full; my sketch is a repair direction, not a substitute for the candidate's proof.

### 3. Moderate: the definition of w is misstated

As written, flows f_ij for i∉Q or j∉R are constrained only by p_ij. Absent players are therefore unconstrained rather than excluded. Formula (1) matches the intended definition (f_ij=0 unless i∈Q and j∈R), so the two disagree as stated.

### 4. Moderate: (M) is essentially classical, which bears on the "NEW mechanism" target

(M) says that same-side players are substitutes and cross-side players are complements. To my recollection this is Shapley's 1962 assignment result, with flow versions via Topkis-style parametric min-cut arguments and Gale–Politof or Granot–Veinott. I have not checked these sources.

The candidate disclaims novelty, which is appropriate. But the brief forbids recycling "separate substitutes", and (M) adds only the well-known cross-side complementarity. Calling it "the natural bimatroid inequality" is unsupported: no linking-system or bimatroid rank axioms are stated or checked.

### 5. The obstruction example is arithmetically correct but shallow

- **Arithmetic:** w(i,j₁)+w(i,j₂)=2 against w(i,{j₁,j₂})+w(i,∅)=1 is right. The point (1;0,0) is in the core and both pair coalitions are tight. The reverse inequality is indeed false.
- **Scope:** a submodular-direction inequality never uncrosses tight lower-bound core constraints, so this was predictable. The example's own core trivially has directed source projection.
- **What it establishes:** one proof route fails. It does not show (M) is insufficient in the sense the criteria ask for. That would need an abstract game satisfying (M) with a non-directed projection, analogous to examples A and B in the substitutes file.
- **Wording:** "exact obstruction" and "insufficient for tight-set closure" should be narrowed to "the standard tight-set uncrossing route fails".

### 6. Gap: the twisted and complementary forms are not explored

Under column complementation, (M) becomes ordinary submodularity of (Q,R̄) ↦ w(Q, J∖R̄). This matches the h=(y,−z) window identity in BUNDLE_OBSTRUCTION.txt and the upper-bound constraints x(A) ≤ T−v(N∖A). The candidate does not test whether uncrossing the upper constraints in that form yields anything, so the proposed slack target Δ is unanchored.

### 7. Minor points

- "I found no error in the supplied transfer or embedding arguments" is an unsupported aside with no audit shown.
- The link to the coordinatewise-max obstruction is loose. That example has parallel source ports, so it sits outside the unique-port transportation reduction.
- checks.json and the patch are empty, which is consistent with a report-only task. Compliance with the time limit and no-delegation rule cannot be verified statically.

## Assessment against the criteria

- **Fully stated mixed lemma with checked hypotheses:** not met. The statement is true but the proof is invalid and the definition is defective.
- **Concrete new implication for directedness:** none, and the candidate admits this.
- **Conventional counterexample to the mechanism:** partial. It refutes only the reverse inequality and the tight-set route.
- **No overclaiming of novelty or universality:** met, apart from the "exact"/"insufficient" wording.

## Required revisions

1. Replace the proof with the corrected uncrossing, written out in full.
2. Fix the definition of w so that absent players carry no flow.
3. Downgrade the obstruction's label to "the standard tight-set uncrossing route fails".
4. Acknowledge the classical status of (M).
5. Either analyse the complemented upper-constraint form or list it as explicitly untested.
