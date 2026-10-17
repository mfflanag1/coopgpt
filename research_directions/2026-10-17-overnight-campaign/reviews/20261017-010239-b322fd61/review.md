**Provisional verdict: no findings in reviewed scope (chain independently traced; no hidden assumption located).** Most important observation: the lower uses only instances of (1)–(3) plus nonnegativity and symmetry, and every later inequality is a scaled instance of these, so no architecture assumption is smuggled in.

## Findings

**No correctness defects found.** Verified steps (by hand, not executed):

1. **§1 symmetrization** (lines 27–42): role-internal permutations and joint role/label exchange are domain automorphisms of the 2N pure model; coverage, budget, OUT are linear in payments, so averaging preserves them. (1)–(3) are necessary: inactive payments appear only with nonnegative coefficient on the dropped side. Coverage (2) is never used downstream (it follows from (3) with u=r, v=s), which is fine.

2. **§2–3 dilation/averaging** (lines 72–91): T_k maps C→C — checked (1): divide by k; (3): coalition (kr,ks), withheld (ku,kv), reduced profile (k(m−u),k(n−v)), min(ku,kv)=k·min(u,v). Telescoping bound kappa/L is correct (L^{L−1} boundary terms over L^L). Fixed point for all T_{p_j} ⇒ all T_k by commutativity. This is an elementary amenable-semigroup (Markov–Kakutani-type) argument; valid.

3. **§4 well-definedness** (lines 96–99): x_{mn}=x_{mm',nm'}=x_{m'm,n'm}=x_{m'n'} when nm'=n'm. Correct. Orientation reversal via x_{mn}=y_{nm} handles reduced profiles that flip the short side.

4. **§5 Lipschitz** (lines 116–141): (5),(6) are (3) with v=0 / u=0; (7) is (3) with coalition (all A, s B), u=0; (8) is (3) with coalition (m_c A, all B), v=0. Bounds p: kappa-Lipschitz, q: kappa/ε-Lipschitz on [ε,1] all check.

5. **§6 analytic lower**: I rederived (9) from (3) with u=v: dividing the OUT inequality by Δ, t_Δ=(B−Δ)/(A−Δ), gives p+q+(1−t)(αp'+βtq')≥1 at a.e. t; α→0, β=1 gives the third inequality. Integrating factor t/(1−t) yields exactly (10); max of tQ_C(t) at 1−e^{−1/C} equals 1−C+Ce^{−1/C}; monotonicity of C(2−e^{−1/C}) gives C≥c.

6. **Upper** (OUTSIDE §2–4): identities q'=c[log(1−t)+t]/t², q+tq'=1+c·log(1−t), p+q+t(1−t)q'=1, branch junction t0·q(t0)=c with matching q'=−c/t0², corner bounds g_A≥0, g_B≥0, g_A+g_B≥1 all verified.

7. **§7 block extension** (lines 180–191): diagonal profiles are invariant under block permutation; per-block outside worth sums to K·min(u,v); division by K recovers (1)–(3). Correct but adds nothing beyond K=1.

**Minor (low severity, presentational):** line 122–123 remark about inactive owners "whose payments are zero in the derived price formula" is unnecessary and could mislead; (5) follows directly from (3) with the coalition = the m active A owners at the higher profile.

## Scope limitations
- The "complete-access public source-price extension" claim (lines 20–22) rests on the fixed-threshold identity and OUTSIDE §5, whose definitions/proof are not in the packet; not verified.
- The characterization of "finite fixed actual-owner model" (admissible domains, whether budget applies at F=0) is only implicit; the lower is robust to this since zero-production coordinates are never on the binding side.
- Novelty/priority not assessed per instructions.
- No numerical checks run.

## Verdict
No findings in reviewed scope. The reduction from arbitrary finite pure-role mechanisms to a dilation-invariant array and then to Lipschitz rational prices is sound as written; the nonconstructive, rate-free nature (line 193–198) is correctly disclosed. An explicit finite certificate would still be valuable as an independent cross-check.
