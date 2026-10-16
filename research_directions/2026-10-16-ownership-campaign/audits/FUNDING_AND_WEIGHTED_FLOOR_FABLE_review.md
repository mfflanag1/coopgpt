**Provisional verdict: no findings in reviewed scope (minor dependency/wording notes only).** Most important item: LC1's cap-safe step rests on the "complement-surplus lemma" Z−z_i−M_{−i}≤M/2, which is not in the packet and not named in the context's audited list.

## Findings

**1. Low — unverified external dependency (LOW_CAPPED_TOTAL_MANY_POSITIVE.txt:17–18; also GRID_WEIGHTED_OVERLAP_ADDENDUM.txt:21).**
The floor min{1,(S−d_i−1/2)_+} follows from the grand-opponents floor only via Z−z_i−M_{−i}≤M/2. I checked this per branch for the single-opponent-type reduction (surplus ≤ T·max_s(1−½e^{−s})(1−s)=T/2, attained at s=0) and it holds, but the general multi-owner statement is not supplied. Verification: attach the lemma or confirm it is within the audited "fixed-owner coalition floors".

**2. Low — ambiguous definition that the proof depends on (POSITIVE_GAP_DUAL_AGGREGATION.txt:69–71, 76).**
"t the resulting total capped opposing account mass" must include i's own restored account d_i'; only then are r≤min(t,1), "exactly a_i+k(t)r" (t≥1), and B=S−t=x+(others' capped loss) correct. SMALL_POSITIVE_GAP_FUNDING.txt uses the same convention consistently. Suggest stating "including d_i'" explicitly.

**3. Low — statement scope (SMALL_POSITIVE_GAP_FUNDING.txt:20–21).**
The "in particular" sentence omits S≤2H, which SP1 needs (q0≥c for η≤q0/2 and the final c-substitution). It inherits the theorem hypothesis, but should repeat it.

**4. Low — code evidence incomplete (verify_nonlinear_funding_exact.py:73).**
Hashes `CAPPED_TOTAL_OVERFLOW_OBSTRUCTION.txt`, absent from the snapshot; the script would raise if the file is missing. Not a mathematical issue.

## Independently rederived (all confirmed)
- **PD3**: lambda≥1/(2S)≥q0 via monotonicity of e^{1−y}(1+y−1/S); quotient decreasing on [1,S); F'(t) sign = S[(1−λ)−q_h(t)(1+1/t−1/S)], strictly increasing bracket, zero at u, F(u)=q/S=η.
- **PD4/PD1**: D≤x+w_i and D≥x in both overflow cases; square completion exact; t<1 pool-switch case uses ρ≤1/t correctly.
- **SP1**: |k'|≤(e/2)y²e^{−y}≤2/e=4c; Lipschitz chain, q0≥c (S≤2), η≤q0/2, 8K²c²z_ig_i²/q0≤8K²cz_ig_i².
- **SP3–SP5**: L'=−L/[2(1+√(1−v))], L≥1−v/3 for v≤3/4; cubic expansion coefficients 3207/12800, 19/3200, −35/32, −7/8; s≥−1/4 domination; max 8979961/35840000<13/50.
- **SP2 arithmetic**: 698699/500000<699/500<5041/3600; raw total 1+q0(S−1)≤C.
- **LC2–LC4**: max(d_i,T) floor valid because T≤1 (no truncation); s↦k(s+R)(s−a_i) increasing in both k-regimes; [Tk(T)]'≥0 via (1+y)e^{1−y}≤2; LC1 reduces to e^{1/2+c}<2 (margin ≈0.0009, exact tail bound correct).
- **AD**: profile values S=19/10,G=7/5,Z_±=1/2 correct; A''=1/q, tangent 2/3−(1+log 3/2)q; AM-GM 6647/32000>81/400; 1024/729<57/40.
- **CT**: q'=ce^t, S'=2−cte^t, log-ratio ≥(t/2)[c−t/(1−t)]>0 for t≤1/10; valid refutation of the uncapped charge.
- **SH1/SH3**: ratio decreasing in d, (3−x)e^x≤3(x+1) via F'(1)=3−e>0.
- **Weighted floor (1),(2)**: concavity of min(z',1−p_k), layer-cake, (1−w_k)U_k=(U_k+u_k−1)_+.

## Scope limitations
Cannot verify the sharp outgoing bound, negative-gap theorem, own-monotonicity, or coalition floors beyond the context summary; did not run the checker; FIXED_OPPONENT_COALITION_FLOOR.txt and the complement-surplus lemma are not in the packet. No global C² inference is made.

## Verdict
No mathematical findings in reviewed scope; one load-bearing lemma (item 1) should be attached or explicitly cross-referenced to an audited note.
