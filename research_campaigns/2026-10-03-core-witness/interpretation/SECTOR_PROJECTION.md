# Exact sector projection and a five-label path-plus-loop certificate

3 October 2026. Bounded first pass. Conventional algebraic proof and solver-free rational checks; independent review pending. This note reads only CW-01/CW-04 campaign cases, not CW-05/CW-06. No support LP, ideal LP, or other optimizer was run. All calculations use original-core payoffs and frozen original ideals.

**Outcome.** Exact sector projection produces an explicit five-label ideal upper bound separating CW-01's saved relaxed vector: `H_A,2 <= 1/51 < h_A,2 = 4/51`. The projection proof exposes the lost coupling. However, this particular bound is exactly a four-team integral deletion certificate. All 570,240 instances of the same motif on CW-04 fail to separate its saved vector. The result is a useful technical basis and precise bounded obstruction, not a new general mechanism or sufficient phase-2 progress by itself.

## 1. Entire-core projection, for arbitrary size

Let `W(a,b,c)` be a full team's worth, let `d_j=W(j,j,j)`, and suppose the diagonal matching has original grand worth `T=sum_j d_j` and the original entire core is nonempty. For pair-additive markets, `W=AB+AC+BC`; the following elimination actually needs only the full-team cover description and nonnegative payoffs.

Every core point makes each diagonal tight: their cover inequalities sum to the total-payoff equality, so no diagonal can have slack. Fix the A-sector vector `z_j=x_A,j`. Write

    x_B,j = b_j,       x_C,j = d_j - z_j - b_j.

Then z is the A-sector projection of an original core point if and only if `z>=0` and there exist b satisfying

    0 <= b_j <= d_j-z_j,                                      (1)
    b_b-b_c >= W(a,b,c)-d_c-z_a+z_c   for every a,b,c.           (2)

Necessity follows by substitution. Conversely these equations make all payoffs nonnegative, give total T, and cover every full team. Summing covers along any disjoint matching covers every original coalition, so the reconstructed payoff lies in the entire original core. This is exact; it neither fixes one common coordinate maximizer nor approximates ideals.

For a fixed z, form a directed multigraph on the m labels and an anchor `*`, with a potential `b_*=0`. Add

    * -> j  of weight 0;
    j -> *  of weight z_j-d_j;
    c -> b  of weight W(a,b,c)-d_c-z_a+z_c, for every a,b,c.

Every arc `u->v` imposes `b_v>=b_u+weight(u,v)`. Parallel arcs and self-loops are retained.

**Projection theorem.** A nonnegative z is feasible exactly when this graph has no directed cycle of positive total weight.

*Proof.* Feasible potentials telescope to nonpositive weight on every cycle. Conversely, if all cycles are nonpositive, define b_j as the maximum weight of a walk from `*` to j. All labels are reachable through the zero-weight anchor arcs. Removing nonpositive cycles never decreases a walk's weight, so maxima exist among finitely many simple paths. The empty walk has weight zero and every closed walk from the anchor has weight at most zero, hence `b_*=0`. Appending an arc proves every difference inequality. The two anchor arcs give (1), and the triple arcs give (2). Reconstruct the core point as above. This also proves that simple directed cycles, including loops, suffice. ∎

No external theorem is needed for this proof. Its underlying difference-constraint/assignment technique is established, not a novelty claim.

## 2. Explicit cycle inequalities in z

For distinct labels `v_0,...,v_(k-1)` and triples `(a_i,v_(i+1),v_i)` with indices modulo k, the unanchored cycle inequality is

    sum_i (z_v_i-z_a_i)
      <= sum_i d_v_i - sum_i W(a_i,v_(i+1),v_i).               (3)

For a simple path `v_0 -> ... -> v_k`, close it through the anchor. Its exact inequality is

    sum_(i=0)^k z_v_i - sum_(i=0)^(k-1) z_a_i
      <= sum_(i=0)^k d_v_i - sum_(i=0)^(k-1) W(a_i,v_(i+1),v_i). (4)

The zero-length path gives `z_j<=d_j`; an unanchored loop gives the familiar completion comparison `z_c-z_a<=d_c-W(a,c,c)`.

**Attainment caution.** One cannot substitute H for z in a general (3) or (4): several positive coordinates may attain their maxima at different original core points. This is precisely the issue the campaign must retain. For a valid inequality `sum c_j z_j<=K`, choosing a core point attaining `H_t`, dropping other nonnegative terms, and bounding negative-coefficient coordinates by their ideals gives the valid but possibly weaker inequality

    c_t H_t + sum_(c_j<0) c_j H_j <= K       when c_t>0.        (5)

The much stronger option is to combine projected constraints until the remaining left side is one coordinate. The next example does so, without any common-attainment assumption.

## 3. One explicit all-size five-label motif

Choose five distinct labels `a,b,c,d,e` in any market satisfying Section 1's hypotheses. Use four full teams

    t1=(a,b,c), t2=(b,d,e), t3=(d,c,d), t4=(e,a,a).

Define

    Delta = d_a+d_b+d_c+d_d+d_e - W(t1)-W(t2)-W(t3)-W(t4).

Then

    H_A,c <= Delta.                                          (6)

The B/C graph has a path `e -> d -> c -> b`, using t2,t3,t1, and a loop `a -> a`, using t4. Equation (4) for the path gives

    z_c+z_e-z_a <= d_b+d_c+d_d+d_e-W(t1)-W(t2)-W(t3).         (7)

The loop gives

    z_a-z_e <= d_a-W(t4).                                    (8)

Adding proves `z_c<=Delta` at every original core point; maximization proves (6). The statement is invariant under sector permutation and label relabeling, and its size is independent of the ambient m. Pair values outside the motif need not vanish.

An equally short direct proof identifies its limitation: the four teams are player-disjoint, and among the fifteen players on the five diagonal labels they omit precisely `A_c,B_e,C_b`. Thus diagonal tightness and the four core inequalities give

    x_A,c+x_B,e+x_C,b <= Delta.

Nonnegativity proves (6). Therefore this motif is an integral deletion bound written as one anchor cycle plus one loop. It is not a new mathematical substitute for the existing deletion/attainment machinery.

## 4. Exact CW-01 separation and the lost coupling

Take `(a,b,c,d,e)=(0,1,2,3,4)` in `CW-01_relaxed.json`. The four teams and their exact worths are

| Team | Worth |
|---|---:|
| (0,1,2) | 8/51 |
| (1,3,4) | 7/51 |
| (3,2,3) | 1/51 |
| (4,0,0) | 5/51 |

The five diagonal values are `(6,4,4,4,4)/51`, totaling `22/51`. Thus `Delta=(22-21)/51=1/51`.

More revealingly, (7) and (8) become

    z_2+z_4-z_0 <= 0,
    z_0-z_4 <= 1/51.

Their sum gives the claimed upper bound. The saved hypothetical ideals have `h_A,0=5/51`, `h_A,4=4/51`, `h_A,2=4/51`. The difference comparison at the two boundary labels can be satisfied, while the supposedly attainable extra `4/51` at A2 cannot be paid in the same witness. The multi-coordinate path inequality is the lost coupling; removing its nonnegative z2 term turns it into a weaker difference condition and discards the obstruction.

The raw exact checker confirms this hypothetical vector satisfies every old completion, range and P-induced comparison, the original-core dominance condition, diagonal and unmatched-player caps, and the declared relaxed objective `20/51`. Consequently (6) is **not implied by those retained relaxed constraints**, as witnessed by this one exact point. This logical independence is specific and rigorous. It is not a claim of literature novelty. We prove an exact upper bound here, not equality with the true ideal maximum; no independently unaccepted ideal certificate is needed.

## 5. Bounded motif census and stopping diagnosis

`sector_projection_census.py` uses only Python's standard library. It independently rechecks the two saved relaxed points against the stated original full-team core inequalities and old ideal-difference constraints, then evaluates (6) using integer-scaled raw matrices.

For each market, it exhausts all `12*11*10*9*8 = 95,040` ordered distinct-label choices and all six sector permutations, totaling **570,240 labeled motif instantiations**. These are not claimed to be inequivalent supports or a classification of all projected cycles. No LP is solved.

| Diagnostic | Scale | Violated motif instances | Strongest reported instance |
|---|---:|---:|---|
| CW-01 | 51 | 9 | `H_A,2<=1/51`, violated by `3/51=1/17` |
| CW-04 | 2361 | 0 | none |

The retained JSON contains the strongest CW-01 violation for each sector order that has a violation. The exact output is reproduced under `python -O`; checks use exceptions, not assertions. All motif budgets are nonnegative, as required by the separately checked original core.

This family therefore does not explain the CW-04 diagnostic. That absence does not prove that every short cycle family fails, that a fractional certificate is required, or that all larger motifs fail. It identifies only the complete failure of this named five-distinct-label path-plus-loop family on this named raw market. Additional cycles with other topology or combinations might separate it, but no such statement is established here.

**Stop this first-pass route here.** Reopening should require a concrete new coefficient cancellation or structural cycle motif with a stated target, rather than replacing the full-witness LP by an equivalent projection and calling that a proof advance. The all-size projection theorem and the CW-01 restatement alone do not pass the campaign's phase-2 mechanism gate, do not establish a unicyclic theorem, and do not improve the global subsidy bound.

## 6. Source comparison and provenance

The source refresh was checked against freely accessible primary PDFs on 3 October 2026. [Solymosi (2023), Section 4, Lemma 1, printed page 9](https://unipub.lib.uni-corvinus.hu/9034/1/Sensitivity_of_fair_prices_in_assignment_market_ST_23.pdf) identifies two-sided assignment-core extrema through longest reference paths. [Shapley and Shubik (1972), Theorem 2](https://www.math.utoronto.ca/mccann/assignments/477/ShapleyShubik72.pdf) identifies the assignment core with optimal assignment-LP dual solutions. These establish the relevant technique's prior existence. They do not by themselves establish the three-sector frozen-ideal target.

Input SHA-256 values:

- `FORMULATION.md`: `b9c68977417081ca248e53d625fef2aaea085c9c42cc79d3d94b7103e932e383`
- `paired/CW-01_relaxed.json`: `7a1fe769777049a6b2d8ec528b94b9b243fcc95b93bcf97d15d34e36dbecfc53`
- `paired/CW-04_relaxed.json`: `d7a527856afe8ed3dfe2ab5879db11f4ca7fe3e599b85d084ffa8509ea8c7d03`

Artifacts are `/private/tmp/coopgpt-witness-20261003/sector_projection.md`, `sector_projection_census.py`, and `sector_projection_census.json`. Reproduce with:

    python3 -O /private/tmp/coopgpt-witness-20261003/sector_projection_census.py

No campaign files were edited. CW-05/CW-06 were neither read nor optimized in this subtask. The original support-registry construction preceded this distinct held-out restriction; the present mathematical analysis does not use those held-out supports.
