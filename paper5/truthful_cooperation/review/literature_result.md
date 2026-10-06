## Bounded literature audit

I found three original sources with direct partial overlap, but none establishes the manuscript’s combined package of coalition coverage, own-report incentives, the continuous-Banzhaf rule, and the stated sharp asymptotics. This is overlap/gap evidence only—not a novelty determination.

### Closest primary sources

1. **Moretti–Norde, “A note on weighted multi-glove games” (2021).**  
   Free [authoritative full text](https://d-nb.info/1240670206/34), DOI `10.1007/s00355-021-01337-8`.

   - Section 3, Definition 3.1 (printed pp. 3–4) defines
     \[
     v_{P,w}(S)=\min_j\sum_{i\in S\cap P_j}w_i,
     \]
     exactly the underlying weighted multi-glove characteristic function.
   - Theorem 3.2 proves total balancedness by paying a bottleneck pool, hence establishes nonempty cores for all subgames.
   - Theorems 3.3–3.5 concern supermodularity and population-monotonic allocation schemes; Theorem 3.7 concerns Shapley values for a dominated-pool subclass.
   - The concluding remark on printed p. 11 explicitly extends the results from positive integer weights to positive real weights and discusses zero weights.

   **Overlap:** exact cooperative-game model, real weights, core existence, Shapley/proportionality phenomena.  
   **Gap:** reports are not private types; there is no underreport mechanism, coalition-covering subsidy rule, continuous Banzhaf construction, budget-factor analysis, proportional-rule lower bound, or nonlinear restricted-family escape.

2. **Kurz, “Measuring Voting Power in Convex Policy Spaces” (2013).**  
   Free [arXiv original](https://arxiv.org/abs/1312.5936); stable [v1 PDF](https://arxiv.org/pdf/1312.5936v1).

   - Section 4 defines continuous decision rules \(v:[0,1]^n\to[0,1]\).
   - Section 6.2, Definition 6.11 (v1 printed p. 17) defines the absolute continuous Banzhaf index by integrating the endpoint difference
     \(v(1,x_{-i})-v(0,x_{-i})\) over the other coordinates.
   - Definitions 6.13–6.14 and Lemma 6.15 discuss total power and basic properties; Section 7 explains the independent, equiprobable-coordinate interpretation.

   **Overlap:** the precise continuous-Banzhaf functional used in `BANZHAF_IDENTIFICATION.txt`. The identity \(d_i p_j=T\,\mathrm{BZI}_i(f_d)\) is therefore an application/derivation, not a new index.  
   **Gap:** Kurz studies influence in a fixed continuous voting rule. He does not treat capacity reports, report-dependent games \(f_d\), coalition-covering transfers, truthfulness, subsidies, or \(k\)-asymptotics.

3. **Huang–Mei–Yang–Cao, “Mechanism Design in Max-Flows” (2025).**  
   Free [arXiv paper](https://arxiv.org/html/2502.08248).

   - Section 2.1 defines the edge-player max-flow game and assumes binding underreports, \(\hat c_i\le c_i\), with no usage cost.
   - Section 2.1 defines DSIC/NEIC; the mechanism is constrained to be efficient, so its payments total the reported max-flow value.
   - Example 1 in Section 2.2 proves that no core-selection mechanism is NEIC in their general network class.
   - Proposition 1 in Section 3 proves that the Shapley-value mechanism is DSIC and strongly individually rational.
   - Section 4.1, Definition 2 gives a minimal-cut mechanism that distributes value within cuts proportionally to capacity; Theorem 1 proves DSIC, SIR, split-proofness, merge-proofness, and cross-monotonicity.
   - Section 4.2 explicitly notes that this mechanism need not be in the core and players may have incentives to collude.

   **Overlap:** almost exactly the manuscript’s binding-underreport/no-cost incentive convention, monotonicity of payoff in own reported capacity, max-flow revenue allocation, and a capacity-proportional construction. A series of parallel-edge layers realizes the multi-glove game as a special max-flow topology.  
   **Gap:** their “truthfulness” is efficiency-constrained and does not require every coalition’s assigned payments to cover its worth. Their own text says the MC allocation may fail core stability. They provide neither subsidies nor Banzhaf payments, the \(O(\log k/\log\log k)\) bound, the proportional-class minimax lower bound, nor the restricted-family nonlinear escape. This is the most important paper to distinguish explicitly.

4. **Bachrach et al., “The Cost of Stability in Coalitional Games” (2009).**  
   Free [arXiv original](https://arxiv.org/abs/0907.4385).

   - The introductory model defines external subsidy to make a grand-coalition allocation satisfy core constraints.
   - Later sections give general and class-specific cost-of-stability bounds, including weighted voting games.

   **Overlap:** “subsidy” plus simultaneous coalitional stability constraints.  
   **Gap:** values are fixed rather than owner-reported capacities; no own-report incentive constraint, multi-glove specialization, continuous Banzhaf rule, or proportional-rule asymptotic. It is framing prior art, not apparent theorem preemption.

### Claim-by-claim assessment

- **All-profile continuous-Banzhaf \(O(\log k/\log\log k)\) upper:** Kurz preempts the functional, and Moretti–Norde preempt the game. I found no source in this bounded audit combining them with coalition coverage, report monotonicity, and this budget bound.
- **Unrestricted necessary total factor 2:** unresolved. None of the four supplied files contains a clearly labeled unrestricted factor-2 theorem or its witness. It therefore cannot presently be audited from the supplied evidence.
- **Sharp floor-free capped-proportional asymptotic:** the linked-profile lower bound and matching continuous-Banzhaf upper appear distinct from the located sources. Huang et al.’s proportional cut mechanism is close in form but lacks coalition coverage, so it does not defeat the lower bound’s stated scope.
- **Nonlinear escape on restricted families:** no located source gives this construction. It must be described narrowly: it is an existence result on the two-/fixed-\(m\)-altered-pool family, not an unrestricted constant-factor result.

## Concrete source-note defects to resolve

- [`SCALING_THEOREM.txt:126`](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-235329-231595e3/workspace/research_campaigns/2026-10-04-stage-scaling/SCALING_THEOREM.txt:126) should cite the exact Moretti–Norde items—Definition 3.1, Theorem 3.2, and the real/zero-weight remark—not merely `SOURCES.txt`. Verify explicitly that extending from positive real to zero weights preserves every manuscript use.
- [`BANZHAF_IDENTIFICATION.txt:3`](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-235329-231595e3/workspace/research_campaigns/2026-10-04-stage-scaling/BANZHAF_IDENTIFICATION.txt:3) correctly points to Kurz v1, but the manuscript should say “Definition 6.11 in arXiv v1, printed p. 17”; numbering can differ across renderings.
- [`SCALING_THEOREM.txt:12`](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-235329-231595e3/workspace/research_campaigns/2026-10-04-stage-scaling/SCALING_THEOREM.txt:12) and lines 29–40 use payoff monotonicity as the incentive condition. Add a formal utility/report model explaining why binding underreports plus zero usage cost makes weakly increasing own payment equivalent to DSIC. Huang et al. Section 2.1 is the closest precedent.
- The asserted **unrestricted necessary total factor 2** is absent from the supplied notes. Supply the exact theorem/witness before including it among the manuscript’s strongest claims.
- [`PROPORTIONAL_THEOREM.txt:66`](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261005-235329-231595e3/workspace/research_campaigns/2026-10-05-beyond-thresholds/PROPORTIONAL_THEOREM.txt:66) defines \(A_k\) over “families … for every finite fixed ownership.” Clarify whether a single uniform rule family must work across ownership structures or whether the infimum is taken separately and then supremized; the lower and upper quantifier order should be written formally.

## Ranked informal specialists

1. **Stefano Moretti** — strongest exact-model fit. He coauthored the defining weighted multi-glove paper and works in cooperative game theory. [Dauphine institutional profile](https://dauphine.psl.eu/en/research/resume-database/profile/moretti-stefano). Email is institutionally/publication verified as `stefano.moretti@dauphine.fr` in the paper; the profile supplies an email link, and his institutional CV prints it.

   **Ask:** “Does any weighted multi-glove, glove-market, PMAS, or allocation-scheme literature already combine report-dependent weights with coalition-covering payments and own-report monotonicity; and is our real/nonnegative-weight formulation genuinely the same game as Definition 3.1?”

2. **Sascha Kurz** — strongest continuous-Banzhaf and asymptotic-index fit. [University of Bayreuth profile](https://www.wm.uni-bayreuth.de/de/team/kurz_sascha/index.php), with verified institutional email `sascha.kurz@uni-bayreuth.de`.

   **Ask:** “Is \(T\,\mathrm{BZI}_i(f_d)\) for this report-dependent capped minimum game already studied as a payment or allocation rule, and are there known total-power bounds or extremal examples that could subsume the \(O(\log k/\log\log k)\) and matching-rule asymptotic?”

3. **Zhigang Cao** — best own-report mechanism comparator among the max-flow coauthors. He is corresponding author of the closest mechanism-design source. [Beijing Jiaotong institutional profile](https://faculty.bjtu.edu.cn/9191/); that page verifies `zhigangcao@amss.ac.cn`, while the paper itself lists `zgcao@bjtu.edu.cn`. Both are public and verified; neither is guessed.

   **Ask:** “On a series-of-parallel-edges network, is there prior work strengthening your DSIC/efficient max-flow mechanisms to cover every coalition after allowing subsidy, and do your core impossibility or minimal-cut arguments imply either our factor-2 lower bound or any lower bound for capped proportional coalition-covering rules?”

**Not selected:** Henk Norde is also an excellent exact-model reviewer and his [Tilburg profile](https://research.tilburguniversity.edu/en/persons/henk-norde/) verifies `H.Norde@tilburguniversity.edu`. Moretti ranks marginally higher because his current profile shows a broader algorithmic/cooperative-game fit; Norde is the natural substitute if independence from Moretti is preferred.

### Limitations

This was a bounded audit of freely accessible original literature and institutional profiles. Formula extraction from some HTML/PDF renderings was imperfect, and I did not establish novelty from absent search results. The factor-2 claim remains unauditable until its source note or proof is supplied.