**Provisional verdict: no invalidating findings in the reviewed scope.** The new lemma (1), its all-switch proof, the log-sum/monotone optimization (4)–(6), and the scalar expansion (7)–(9) recompute correctly. Only minor presentational gaps.

## Findings

**1. (Low) `SHARP_LOCAL_ONLY_ENTROPY.txt` L35–36 — missing positive part in (2).**
For a mixed opponent k, the full-to-final change is `(1−q−q_new)l_k + [q_new·min(s_k,t) − (1−q)s_k]`, with the bracket ≤0, so `I ≤ v·(1−q−q_new)_+`, not `v·(1−q−q_new)`. Harmless, because the target `qv(e^d−1)` is nonnegative and (3) shows `1−q−exp(1−1/v)/2 ≤ q(e^d−1)` directly. Suggest inserting `(·)_+`.

**2. (Low) L32 — implicit use of `q_new ≤ 1/2`.**
The claim `q_new·min(s_k,t) ≤ s_k/2` needs `rho_new ≥ 1`. This holds since `Σ_k min(s_k,t) ≥ min(Σ s_k, t) = t`, but is not stated. Suggest one line.

**3. (Info) Verified computations.**
- Second bound of (1): `2V = d·exp(1−rho)` gives `log(1/(2V)) = rho−1−log d`, so `rho−d = log(1/(2V)) + log d + 1 − d ≤ log(1/(2V))`; nonnegativity of `log(1/(2V))` follows from `V ≤ q ≤ 1/2`. ✓
- (3): derivative ratio `exp(v−1/v−2log v)`, exponent derivative `(1−v)²/v² ≥ 0`, zero at v=1 → sum nonincreasing to 2. ✓ Transformation of (2) uses `q e^d = exp(1−v)/2` exactly. ✓ Hand check d=0.5, rho=1, many tiny short owners: actual increase 0.158 = bound (2), ≤ first bound 0.162. ✓
- Sharpness (L55–61): d=1, deletion gives `q' = eq`, gain `Kq(rho−1)T = KV·log(T/(2V))`, pool stays long since `rho−1 ≥ 1`. Exact equality. ✓
- (4): log-sum with `b_j = T_j`, `Σ b_j ≤ X`, and the `−v_i log 2` term carried correctly. `z_i − v_i` bounds short local roles outside J_h plus hardware roles. ✓
- (5): `f'(v) = −1 + K[log(X/(2v))−1] ≥ −1 + K·(1/K) = 0` when `X ≥ A0ε`; `d/dz[Kz log(X/(2z))] = K[log(X/(2z))−1] ≥ 1`. ✓ (6): `v* = X/(2exp(1+1/K))`, max value `Kv*`, giving `< (1+K)ε = eε`; note the boundary value at `X = A0ε` is `K(1+1/K) = e`, so the max with e is continuous. ✓
- (7): `x+log x = L+1`, value `(x−1)²/x = x−2+1/x`, `x = L−log L+1+o(1)` → `F = K(L−log L−1)+o(1)`. Concavity `−1/Y−1/Y²`. ✓
- (8)–(9): `t = Kε + εF + o(ε) = Kε(L−log L)+o(ε)`; `cA·exp(t/A) = c + cKε + cKε(L−log L)+o(ε)`. The +1 in (9) is the `A` factor, not a residual from (iii). ✓ Hence limsup ≤ cK.

**4. (Info) Dependency consistency.** New bound `KV log(T/(2V)) ≤ KV[1+log(T/(2V))]` (GLOBAL (iii)), so substituting into Section 4/5 of GLOBAL is monotone; G_- ≤ 1−X/2 and the positive-gap comparison are untouched. The cutoff change (ε → A0ε) only enlarges the region using the constant e, still eventually dominated.

## Scope limitations
- No numerical execution; checks are by hand at a few points.
- The accepted dependencies (restoration lemma, positive-gap comparison, SHARP_OUTGOING_LOSS, lower witness) were not re-audited; the lemma's proof is self-contained and only uses primitive formulas.
- The envelope-level use (S' ≤ S + I_i) is inherited from GLOBAL Section 5, not re-derived here.

## Verdict
**No findings in reviewed scope** beyond two low-severity presentational omissions (positive part in (2); explicit `rho_new ≥ 1`). The sharp long-coordinate bound (1), its switch-inclusive proof, exact sharpness family, joint-role optimization, and the improved order-ε upper coefficient cK are correct as written.
