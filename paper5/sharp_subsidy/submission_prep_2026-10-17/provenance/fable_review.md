**Provisional verdict: findings, all low severity — I found no mathematical error, missing hypothesis or counterexample.** The most important concrete item is an unstated step in the tree argument at `manuscript.tex:423–428`.

## Findings

1. **Low (proof-exposition gap) — `manuscript.tex:423–428`.** "Connected … so it is a tree" needs every label vertex to lie in some special team, which is never stated. It follows from the label sets at 411–413 (union {0,…,2ℓ}) or the count 3ℓ−(ℓ−1)=2ℓ+1. *Verification:* add that sentence; hand-check ℓ=1,2.

2. **Low (ambiguous notation).** `B` is both the N₁×N₃ matrix (114–118, 203–204, 408) and the scalar residual budget (260, 275, 308, 320, 388, 489). `ℓ` is the family parameter (400) and the slack ℓ_{e;a,b,c} (495–498). `(a,b,c)` denotes players (116, 407) and sector permutations (236). The range of Σ_h at 334 is unstated. *Verification:* rename, then reread 308 and 388.

3. **Low (attribution scope).** No confirmed-novelty claim appears, line 108 hedges adequately, and Quint's model (95–97) is attributed secondhand rather than to the unread original.
   - Lines 108–110 name only Quint/Lucas/Stuart, whereas `SOURCE_COMPARISON.md:29–31` lists further unresolved leads (Marchi–Oviedo abstract-only, Vazirani, hypergraph routes, non-exhaustive search).
   - Bachrach et al. (87–88, 598–603) has no reading-scope note, although ledger line 30 says that original was not fully compared. The claim is generic, so risk is small.
   - *Verification:* widen the disclosure; annotate the entry.

4. **Low (wording; unverifiable) — 566–573.** "27 three-label coincidence patterns": three labels have five coincidence patterns, so 27 is presumably label triples over three symbols. The figure 3,603,804 does equal Σ_{ℓ=1..12}(3n+1)n³ by my hand arithmetic (3n witnesses plus one subsidy allocation), but no code or output is in the packet.

## Re-derived by hand, no error found

- LP dual and domain (164–183).
- Range and comparison lemmas; the witness correctly maximizes the subtracted H_{c,j_b} (219–254).
- Six-permutation sum 3Σ_a H_{a,j_a} − Σ_a H^Σ_{j_a}, valid with repeated labels; deficit coefficient Σ_{b≠a} q_{b,j} ≥ 0 for fractional loads (279–310).
- Witness budget for q_i=0 and real k (323–347); strictness via attainment (350–364).
- Integral weights give (8k−5)T/(2k−1) (384–396).
- Remark 6.2 (481–490): W=7, S=9, k=1, objective 1>0; it saturates the fractional bound (B=6, C₂=3, V=30).
- Family: coloring, exhaustive team classification, T=3n, H_i=3, s=2ℓ, equality at k=ℓ+1 (416–479).
- Slack identities (504–515); identity at 537–542 as a feasible-set deduction, conditional on the cited definition.

## Scope limitations

Nothing was executed. The Python package, audit record and cited sources are outside the packet, so I cannot confirm the checks ran or that source descriptions (Núñez–Rafels Def. 6, Meir et al. §2.2, Atay–Núñez p. 273) match the originals. This was a hand re-derivation, not a formalization; novelty was not assessed.

## Verdict

**Findings (low severity only).** The proofs of Theorems 2.2 and 5.1 and Proposition 6.1 check step by step in the reviewed scope.
