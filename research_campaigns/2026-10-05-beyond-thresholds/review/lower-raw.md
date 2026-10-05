# Unrestricted divergence via linked owner-report changes: unresolved, with a proved barrier for single-sink compositions

**No divergent family was found; the question stays unresolved.** I proved that a whole class of linked-report compositions (single-sink stars) can never certify β > 1, and I isolated the two places where budget weights cancel the gain. Everything below is hand-derived from the two supplied files; nothing was machine-checked and no files were written.

## 1. Transport form of a certificate

For a profile c and owner weights w ≥ 0, define F_c(w) = min{ w·x : x ≥ 0, x(S) ≥ v_c(S) for all S }.

A finite certificate consists of:
- budget weights μ_c > 0 on finitely many profiles;
- flows ρ ≥ 0, each from (c, i) to (c', i), where c' differs from c only by a higher report of owner i;
- induced weights w_c(i) = μ_c + outflow − inflow, required to be ≥ 0.

Weak duality gives (1+β) Σ μ_c T_c ≥ Σ_c F_c(w_c): multiply coverage rows by the LP-dual multipliers of each F_c, and monotonicity rows by ρ. I use only this direction and make no claim of complete duality over the infinite profile space.

The supplied proof fits this form after de-symmetrization. Y is a source with μ = 2, each of its 4 unit owners exports t−1, and F_Y = 2(2t−1). X is a sink with μ = t that absorbs t−1 on each of its k−1 t-owners at zero loss, F_X = t².

## 2. Cover lemma (any profile, exact)

Let E be a set of owners inside one pool A, with τ = c(E), and let B ≠ A be any other pool. Define x_l = c_l on A∖E, x_l = min(c_l, τ) on B, and x = 0 elsewhere.

This x is a cover, because v(S) ≤ min(c(S_A∖E) + τ, c(S_B)) ≤ c(S_A∖E) + Σ_{S_B} min(c_l, τ). It pays E nothing and costs c(A∖E) + Σ_B min(c_l, τ).

Two consequences:
- **Cap on a source.** However heavily E is overweighted, F_c ≤ μ·[c(A∖E) + min_{B≠A} Σ_B min(c_l, τ)], plus terms for other overweighted owners that x pays.
- **No gain outside a unique minimum pool.** If some minimum pool M contains no exporter, the price cover on M gives F_c ≤ μT.

## 3. Theorem A: star compositions cannot exceed β = 1

**Scope.** One sink profile c' with weight μ' and no exports. Arbitrarily many source profiles c^s, each equal to c' with one owner i_s lowered from a_s to σ_s. Each source has exactly one flow ρ_s into c' and no imports. Owners may repeat and may share pools. Disjoint unions of such stars are included. Then Σ F ≤ 2 Σ μT.

**Proof.**
1. Call a source active if i_s lies in the unique minimum pool of c^s. Inactive sources have F_s ≤ μ_s T_s by §2.
2. For an active source, T_s = D_s + σ_s, where D_s is the sink total of i_s's pool minus a_s. Let i* minimise D over active sources, in pool A*.
3. For an active source with i_s outside A*, apply §2 with E = {i_s} and B = A*. Pool A* contains i* at its sink value, so Σ_B min(c_l, σ_s) ≤ D* + σ_s. The cost is at most D_s + D* + σ_s ≤ 2T_s, so F_s ≤ 2 μ_s T_s.
4. For an active source with i_s in A*, the price cover on its minimum pool gives F_s ≤ μ_s T_s + ρ_s σ_s. The gains ρ_s σ_s are handled in two cases:
   - If A* is a minimum pool at the sink, the price cover on A* there gives F_sink ≤ μ'T' − Σ ρ_s a_s, and a_s ≥ σ_s cancels the gains.
   - Otherwise the sink total C' of A* exceeds T'. Then σ_s ≤ T' − D_i and the flows per owner sum to at most μ'. Over the n owners with positive terms, Σ (T' − C' + a_i) ≤ T' + (n−1)(T' − C') ≤ T'. So the gains total at most μ'T'.
5. With F_sink ≤ μ'T', the grand total is at most 2 Σ μT. ∎

## 4. Explicit failed amplification

**Profiles.** The source has a unique minimum pool A = R ∪ {e} with c_e = σ and T = c(R) + σ, and k−1 other pools each consisting of m owners of capacity σ, with mσ ≥ T.

**Source value.** F_source(μ(1 + ε·1_e)) = μ·min(T + εσ, c(R) + mσ). The upper bound comes from the price cover and the §2 cover. The lower bound comes from weight μ on the grand coalition (R ∪ {e} with all other owners) plus weight μ on each of m−1 disjoint coalitions formed by e with one owner from every other pool. At ε = m−1 the source ratio is 1 + (m−1)σ/T, which is unbounded in m.

**Where the gain disappears.** The flow is ρ = (m−1)μ, the sink needs μ' ≥ ρ, and T' ≥ T. The overall ratio is therefore at most

1 + (m−1)σ / (T + (m−1)T') ≤ 1 + σ/T ≤ 2.

If e overshoots so that T' = mσ, the ratio is below 1 + 1/m, so it decays as the source ratio grows.

**The two cancellation mechanisms.**
- **Single-import sinks.** Sink budget ρT' is at least the gain ρσ.
- **Multi-import sinks.** Spreading sink budget over n importers in distinct pools puts sibling pools into every source. By §2 this caps F_s ≤ μ_s(T_s + min_j D_j), which is at most 2μ_s T_s for every source except the one with the smallest D. This is why the supplied X/Y family tops out at (2t−1)/t.
- **Same-pool importers.** For gap Γ > 2 between the minimum and the other pools, these are impossible, since each would need capacity above half the pool.

**Veto ladder.** A = {e} alone, climbing σ_0 < … < σ_N below all other capacities, gives F_σ(w) = σ·min(w_e, mμ). Telescoping gives Σ F ≤ Σ μT + Σ out_s(σ_s − σ_{s+1}) ≤ Σ μT, so it yields nothing.

## 5. Independent recalibration witness (not divergence)

The profiles are X (one L pool, k−1 H pools) and X2 (all H pools, T = 2t−1), using the symmetrized roles of the supplied file.

- At X, C1 + q·C2 + C4 gives Budget_X + (t−1)a ≥ 2t−1, so (t−1)a ≥ t−1−tβ.
- At X2, the coalition of all non-t owners gives k(u' + qv') ≥ t−1, so k·w' ≤ t + (2t−1)β.
- Raising one L-unit of X from 1 to t gives X2, so w' ≥ a.

Combining: β ≥ (t−1)(k−t) / (kt + (t−1)(2t−1)), which tends to 1 − 1/t as k grows. This has the same limit as the supplied bound and is slightly weaker at finite k (for t = 4, k = 100: 0.684 against 0.694). It confirms the transport picture: X alone is a source with gain equal to export, and an all-equal sink loses only ρt on a budget of order k.

## Limitations and unresolved points

- Theorem A does not cover sources with two or more exporters, which both known β→1 families use. It also does not cover one owner exporting to several sinks, or cascades where a profile both imports and exports.
- For multi-exporter sources I have only the §2 cap F ≤ μ(T + min over co-importer pools of D_j) plus payments to other exporters in B. I could not close the charging argument to a clean bound of 2.
- Cascades: an importing owner in pool B only lowers the §2 cover cost, so an intermediate profile is no better a source than a pure one. I did not prove that it cannot recover its own sink budget often enough to compound.
- Any route to β > 1 must leave the star class and avoid the sibling cap. The live region is asymmetric multi-exporter or cascade families where every co-importer pool has D_j far above T_s.
- No divergence is proved and no constant upper bound follows; the O(log k / log log k) mechanism remains the ceiling.
