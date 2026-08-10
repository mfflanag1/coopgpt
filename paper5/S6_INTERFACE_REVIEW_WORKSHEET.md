# External-review worksheet: counterexample to frozen relaxation

Date: 2026-08-10

Target implication:

```text
genuine singleton-normalized exact-game counterexample
    ==> satisfying assignment of one frozen strict QF_LRA formula.
```

This worksheet is a verdict form, not an internal certificate.  The existing
JSON audits establish transcription and local formula equivalence.  A reviewer
must independently assess the mathematical implications below.  Mark each row
`proved`, `false`, or `not checked`; for `false`, give a concrete counterexample
or the first invalid inference.

## A. Load-bearing human lemmas

| ID | Claim to verify | Source | What would falsify it | Verdict / notes |
|---|---|---|---|---|
| H1 | Scaling by `v(N)` preserves exactness, the core, and both selectors up to the same scalar. | Interface Sections 1--2 | A selector or exactness condition not homogeneous under positive scaling. | |
| H2 | Singleton normalization makes every core point nonnegative; exactness supplies six core points `q^i` with `q^i_i=0`. | Section 1, `(W)` | Exactness at a singleton failing to give a common-total core witness. | |
| H3 | Relabeling into consecutive `P,M,E` blocks preserves both anonymous sorted-lex selectors. | Section 2 | A retained assertion depending on more than the common relabeling. | |
| H4 | Equal totals imply `||x-z||_1=2 sum_{i in P}(x_i-z_i)`. | Section 2, `(D)` | A missing sign class or normalization factor. | |
| H5 | Lmax cannot have a unique top player. | Section 3, `a21` | A failure of the segment `z+epsilon(q^i-z)` at a tied/boundary case. | |
| H6 | Some `z`-top player has `x_i>=z_i`. | Section 3, `a22` | The whole old top stratum can decrease without improving decreasing lex order. | |
| H7 | Some `x`-bottom player has `z_i<=x_i`. | Section 3, `a23` | The dual bottom-stratum segment argument fails. | |
| H8 | `Delta(y,h)` preserves every strict order between distinct old strata. | Section 5 | A pair crosses before its displayed positive crossing time. | |
| H9 | The lowest-affected-level sign test strictly improves increasing lex order, including tied strata and nonunit coefficients. | Section 5 | A touched lower stratum changes first, or the sorted block fails to improve. | |
| H10 | The highest-affected-level dual strictly improves decreasing lex order. | Section 5 | A sign/orientation reversal in the Lmax criterion. | |
| H11 | The radius `epsilon_*` in `(E1)` is positive and simultaneously preserves lex order and every core inequality. | Section 6 | A missing coalition family, zero slack ratio, or unprotected equality. | |
| H12 | Optimality therefore forces a nonempty proper tight coalition with `h(S)<0`. | Section 6, `(B)` | Efficiency or singleton constraints are not covered by the short-step argument. | |
| H13 | Tightness plus core membership gives the seven comparisons `(Bx)` or `(Bz)` with the displayed orientation. | Section 6 | Any comparison points toward the selected allocation in the wrong direction. | |
| H14 | Enumerating every nonempty proper `S` with `h(S)<0` makes the consequent a relaxation: tightness and a common blocker across rows may safely be forgotten. | Section 6 | A genuine blocker absent from the disjunction or an extra machine premise. | |

The anchor steps H5--H7 now use the same explicit radius as H8: for the
appropriate segment direction choose
`0<epsilon<min(1,Delta(y,h))`.  H11 uses
`epsilon_* = min(1,Delta,positive slack ratios)`.  The literal `1` removes
all empty-minimum conventions.

## B. Formula correspondence

| ID | Frozen assertion family | Human source | Independent evidence | Verdict / notes |
|---|---|---|---|---|
| F1 | `a0-a1`: efficiency | H1--H2 | semantic interface audit | |
| F2 | `a2-a13`: selection nonnegativity | H2 | semantic interface audit | |
| F3 | `a14-a19`: strict/equal `P,M,E` signs | H3 | semantic interface audit | |
| F4 | `a20`: normalized distance `>2/3` | H4 | semantic interface audit | |
| F5 | `a21-a23`: three anchors | H5--H7 | independent anchor formulation | |
| F6 | `a24-a71`: six witness simplices and zero coordinates | H2 | semantic interface audit | |
| F7 | Every suffix antecedent is exactly H9 or H10 for its recorded direction and side. | H8--H10 | 15,079,260 weak-order/direction comparisons; independent semantic encoder | |
| F8 | Every suffix consequent contains exactly all negative proper cuts and seven comparisons per cut. | H12--H14 | 4,722 cuts and 33,054 comparisons reconstructed | |
| F9 | There are no undeclared symbols, hidden assertions, or unaccounted suffix rows. | Sections 8--9 | 48 declarations, 72 base assertions per case, 252 suffix rows | |

The two scripts below are audit conveniences.  Their passing status is not a
substitute for verdicts H1--H14.

```bash
python3 coopgames/verifiers/s6/audit_strict_exchange_formula_interface.py \
  --output /tmp/strict_exchange_formula_interface.json
cmp /tmp/strict_exchange_formula_interface.json \
  coopgames/verifiers/s6/strict_exchange_formula_interface.json
python3 coopgames/verifiers/s6/audit_strict_exchange_semantic_interface.py \
  --output /tmp/strict_exchange_semantic_interface.json
cmp /tmp/strict_exchange_semantic_interface.json \
  coopgames/verifiers/s6/strict_exchange_semantic_interface.json
```

## C. Mandatory coefficient-two traces

Review both rows completely, without sampling:

1. `(2,3,1)`, assertion `a72`, direction `(-2,-1,1,1,1,0)`:
   verify the activation condition, all 24 negative cuts, and all seven
   comparisons on every cut.
2. `(3,3,0)`, assertion `a74`, direction `(-2,0,-2,1,1,2)`:
   verify the activation condition, all 26 negative cuts, and all seven
   comparisons on every cut.

Record separately whether the independently formulated encoder in
`independent_bound_two_reconstruction.py` is genuinely independent in its
Lmin-optimality component.  Do not infer the human implication from agreement
between encoders.

## D. Required reviewer conclusion

Answer each question separately.

1. Are H1--H14 all proved?
2. Does F1--F9 cover every frozen assertion with the correct orientation?
3. Do both coefficient-two traces match their complete formula rows?
4. Does every genuine counterexample therefore map into a frozen relaxation?
5. If not, is the defect fatal, repairable, or expository?

Only an affirmative external answer to question 4 closes this review gate.
