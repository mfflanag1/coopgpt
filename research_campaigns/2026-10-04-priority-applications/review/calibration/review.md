**Provisional verdict: no invalid proof step found in the calibration lemma; minor findings only, on unverified citations and one significance phrase.** All checks below are by-hand logic; nothing was executed and no literature was consulted.

## Lemma checks (CALIBRATION_LEMMA.txt)

- **L17–19:** T(c0)=2, so some y_i(c0)≥1/2; T(c1)=min(3,2)=2. Relabelling is legitimate because the game is symmetric under side reversal and within-side swaps, and the domain contains all four raised profiles.
- **L20–25:** worths {2,3}=1, {2,4}=1, {1,3,4}=min(2,2)=2 are correct. The sum x₁+2x₂+2x₃+2x₄≥4 gives Σx−2≥x₁/2≥1/4. Nonnegativity is never used.
- **DSIC:** own-report monotonicity is equivalent to underreport-only DSIC if utility equals payment, payments depend only on reports, and over-reporting is infeasible. The lemma applies it only for c0→c_i.
- **L15:** correct; adding a fairness floor only shrinks the class.

## Findings

1. **Low — the lemma understates what is checkable (L31).** On the five-profile domain 1/8 appears exactly tight.
   - Witness: y(c0)=(½,½,½,½), y(c1)=(½,¼,¾,¾), symmetric at the other profiles.
   - By hand, all coalitions are covered and Δ(c1)=¼. The H/3 floor also holds, since H(c0)=(1,1,1,1) and H_i(c1)≤1.
   - Consequence: any improvement over 1/8 needs more profiles or graphs; these five cannot yield it.
   - Verification: enumerate the 15 coalitions at c1 independently.

2. **Medium — unverified citation dependence (LEMMA L28–30, L32–33; APPLICATIONS L19–22, L82).** The packet does not show that Huang et al. Example 1 is this graph, that their model is underreport-only and no-cost, or that Núñez "Model 2" is exactly min(supply, demand) with multi-unit pairs. "Exactly the mathematical Model 2" is a strong identity claim.
   - Verification: quote the source definitions side by side.

3. **Medium — unsupported significance wording (APPLICATIONS L84–86, L10–11).** "Historically open sector-optimal question" and "strongest exact interpretation" assert open status with no supporting source in the packet. Rephrase as a hypothesis until the literature is checked.

4. **Low — no upper bound exists in the packet (APPLICATIONS L32–35).** The file correctly avoids claiming one, and the lemma gives only β≥1/8. The obvious monotone rule y_i=c_i is feasible, but Σc/T is unbounded, so it yields no universal β. "Smallest universal β" may be +∞.

5. **Low — scope gaps (APPLICATIONS L25–26, L42).** The lemma's graph uses parallel arcs; the target ("depth≤3 DAGs") should say multigraphs are allowed, or β≥1/8 does not transfer. The implied assumptions (reports are binding, payments are independent of delivered capacity, no group deviations) should also be stated in the target.

6. **Trivial — typo (LEMMA L32).** "Delta0" should read "Delta=0". At c1, Δ=0 forces x₁≤0, which contradicts x₁≥½ and is consistent with the stated impossibility.

## Application scope of the 12-player example

- The scaling transfer to p·min(Σg,Σb) (APPLICATIONS L57–58) is logically valid as an existence statement.
- The example is static and has s_(1/3)=0, so it gives no incentive or subsidy bound. The files say this at LEMMA L33–34.
- APPLICATIONS L43–44 ("checks that no proof assumes simultaneous sector maxima") is a process note, not a result.

## Scope limitations

- No sources were read and no novelty or priority assessment was made.
- The 12-player proof was not re-audited.
- The tightness witness in finding 1 is hand-checked only.

## Verdict

**Findings (minor).** The lemma is logically sound in the reviewed scope. The citation-identity and "historically open" claims lack evidence in the packet.
