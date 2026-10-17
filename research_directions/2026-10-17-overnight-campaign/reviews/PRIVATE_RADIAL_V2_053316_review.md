**Provisional verdict: no findings in reviewed scope (minor documentation nits only).** I independently re-derived both dual tables, the prices 2/3, 14/15, 58/99, 4/11, 232/495, the loss 1/495, and the Section 2–3 limit argument; all steps check.

## Findings

**1. (Low) Stale certificate string — `TWO_COMMON_FRESH_CHECK_RADIAL_OBSTRUCTION.py:114`.**
`'analytic_extensions': 'Continuous-at-zero kernel proof is in companion note...'` describes v1's hypothesis. v2 (txt lines 33–35) explicitly drops continuity and replaces it with the Cesaro argument. Suggest updating the string to "Section 2–3 Cesaro argument; no continuity assumed" so the JSON certificate does not misdescribe the proof it certifies.

**2. (Low) Phrasing in Section 2, txt line 113–116.**
"For each fixed 0≤a<b<∞ and lambda large enough, ∫_a^b h(s/λ)ds → L(b−a)" — the "large enough" is only needed for b/λ ≤ 1 (so A is defined); the convergence is as λ→∞. Harmless, but the sentence reads as a two-quantifier condition. Also Section 3 silently needs λ ≥ 4/5 so the upper limit ∫_0^λ covers the support of the gradients; worth one clause.

**3. (Informational) Base table omits a tangent form.** The dual form 1+5s/4 (vertex (p,q)=(1,0), gradient (1/2,0,3/4)) equals the envelope exactly at s=4/9 but nowhere in the open intervals, so the displayed base supergradients are correct on the open intervals; the checker's midpoint test handles this correctly. No change required, but readers comparing the base and restored tables may wonder why that form "appears" only at c′.

## Verified steps (independently)

- Dual vertices in the nonnegative quadrant: (0,0),(1,0),(0,1),(3/2,0),(0,3/2),(4,0),(0,4),(5/6,2/3),(2/3,5/6),(4/5,4/5). Envelope for c=(1,1,1): 7s/2 → 3/2+s/8 (two active forms, g1+g2 ≡ 1/8) → 8/5 with breaks 4/9, 4/5. For c′=(1,3/2,1): 4s → 1+5s/4 → 3/2+s/8 → 8/5, breaks 4/11, 4/9, 4/5, unique gradients in each open interval (checked 1+13s/8, 3/2+3s/16, 3/2+5s/8 are strictly above).
- Prices: p0=2/3, p1+p2=8/9+2/45=14/15; p0′=6/11+4/99=58/99, p1′=4/11, p2′=232/495. 17/15−112/99 = (561−560)/495 = 1/495.
- Section 2: at (tr,0,0) the dual is unique (p=q=0 for tr<1, p+q=3/2 for tr>1), so g0 is tie-free; singleton TCWM gives A nonincreasing, nonnegativity + funding gives A ≤ κ, hence L exists with H(1) ≤ L ≤ κ, and the λ-substitution identity is correct.
- Section 3: substitution s=tλ, tie-independence of g0 and g1+g2, convergence of both restored coalition payments to 112L/99, liminf of selected-coalition loss ≥ L/495.
- Section 4: pairwise coverage summed over n² pairs gives Σu+Σv ≥ (3/2)n = nF; requires only coverage, not TCWM.
- Checker logic (endpoint inequalities for affine forms, midpoint activity, nonnegative slopes for the terminal interval, reflection) is sound.

## Scope limitations

I did not run the checker; correctness of the exact arithmetic is by hand re-derivation only. I did not assess historical novelty, the separate three-pool obstruction, or whether the TCWM definition matches the broader program's usage. Singular (non-density) kernels, report-dependent compensation, and unrestricted mechanisms are explicitly outside the claim and were not evaluated.

## Verdict

No findings in reviewed scope. The two exact tables, tie independence, the five-owner Cesaro argument, the capacity-dilation transfer of the 1/495 loss, and the zero-kernel n·F lower bound are all valid as stated. Only the stale certificate string (Finding 1) warrants an edit.
