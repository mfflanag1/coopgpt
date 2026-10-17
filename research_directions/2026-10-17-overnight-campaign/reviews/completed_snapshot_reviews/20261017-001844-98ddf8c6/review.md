**Provisional verdict: no findings in reviewed scope.** I checked each step of the symmetrization, the baseline/deviation accounting, the block lift, and the Huber coalition corollary and found no error or missing hypothesis. The most delicate step—that each relabeling maps a TCWM instance (S, b'_S ≤ b_S, fixed b_{-S}) to another TCWM instance (gS, (gb')_{gS} ≤ (gb)_{gS}, fixed (gb)_{-gS})—holds because the A/B swap and owner permutations are coordinatewise order-preserving on reports.

## Findings

**1. Symmetrization (COALITION_THREE_HALVES_CANDIDATE.txt L27–37) — verified, no finding.**
Defining y^g_i(b)=y_{g(i)}(gb): nonnegativity is trivial; coverage uses F(b_S)=F((gb)_{gS}) (F symmetric under A/B swap, aggregate of gS under gb equals swapped aggregate of S); TCWM transfers as above; budget uses F(gb)=F(b). All are linear in y, so the uniform average over the finite group preserves them and is G-invariant. Not a strategic identity change—correct characterization.

**2. Baseline and deviation (L39–52) — verified.**
- b0 is fixed by (1 2)∘swap and by permutations of nulls, so payments a,a,z,…,z. Note coverage of {1,2} already gives a ≥ 1/2, which yields the needed a+(m−1)z ≥ 1/2 more directly than the grand-coverage route; the written route is also correct since z ≥ 0.
- b0 → b1 is a coordinatewise increase confined to S (owner 1 unchanged, nulls (0,0)→(1,0)), owner 2 fixed, so TCWM gives mx ≥ a+(m−1)z ≥ 1/2. Pair coverage {2,i}: x+y ≥ 1. F(b1)=min(m,1)=1. κ ≥ mx+y ≥ 1+(m−1)x ≥ 3/2−1/(2m). Values m=2,3 give 5/4, 4/3, matching the stated LP record (which I cannot verify).

**3. Disconnected-block lift (L54–73) — verified.**
Block permutations respect the block-local eligibility structure, so the averaged rule is invariant. b1 is invariant under block permutations and within-block A-owner permutations, giving uniform x,y. TCWM for S (all but one B owner per block), per-block pair coverage, and F(b1)=k reproduce the same ratio; coupling across blocks is absorbed by the averaging. k=m gives d=2m, n=m(m+1), all final reports positive.

**4. Huber coalition-total corollary (HUBER_v2 L156–169) — verified at the level of the supplied Lemma 4.**
Derivatives (5),(6) are correctly computed from t=B/(2A), and only a ≤ A, b ≤ B are used; these hold for coalition sums. A coordinatewise aggregate decrease by S is a finite sequence of single-coordinate decreases by members, each covered. Boundary regularization keeps a ≤ A, b ≤ B. Hence TCWM. Coverage is dual feasibility; funding is Lemma 3. The "exact optimum under TCWM" statement is therefore sound given the upper holds for arbitrary eligibility and the lower uses a sub-family.

**5. Scope statements (L85–91) — accurate.** TCWM for singletons is individual monotonicity, so TCWM is strictly stronger; the document correctly does not claim 3/2 under individual truthfulness.

## Scope limitations
- I did not re-audit Lemma 4's pattern-change argument or Lemma 1/2 beyond what the corollary needs; two prior reviews exist.
- The n=3,4 LP values and dual certificates are not in the packet.
- No historical novelty assessment.

## Verdict
No findings in reviewed scope. The lower bound 3/2−1/(2m) under nonnegative, coalition-covering, TCWM rules on symmetric two-input eligibility, its disconnected lift, and the Huber matching upper are correct as written.
