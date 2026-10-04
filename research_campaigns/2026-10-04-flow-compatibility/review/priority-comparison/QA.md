## Verdict: revise

The report is careful and mostly accurate, but a few claims need tightening before acceptance.

### Concrete findings

1. **The target-model identification is verified.**  
   The game
   \[
   v(S,R)=\min\{\sum_{i\in S}p_i,\sum_{j\in R}q_j\}
   \]
   is exactly a two-commodity **singular, non-uniform glove-market game**: each player owns only one commodity, but may own more than one unit. Apartsin–Holzman define glove-market worth as the minimum of aggregate commodity holdings and distinguish singularity from uniformity on printed pp. 190–196. Their Theorem 3.2 applies only to unitary games; Examples 4.1 and 4.3 do not show failure of a side-optimal entire-core point. [Free original PDF](https://holzman.technion.ac.il/files/2012/09/ijgtglove.pdf)

2. **The transportation embedding is correct, but should be stated as a direct derivation.**  
   Núñez’s transportation model has \(x_{ij}\ge0\), row bounds \(p_i\), column bounds \(q_j\), and objective \(\sum a_{ij}x_{ij}\), on slide/printed p. 36. With \(a_{ij}=1\) on the complete bipartite market, the coalition optimum is exactly the smaller aggregate capacity. This equality is elementary from the displayed LP, but the source does not state the specialization explicitly. [Núñez slides, pp. 36–39](https://archive.illc.uva.nl/COST-IC1205/documents/Budapest-2013-Slides/Nunez.pdf)

3. **The 2013 historical open-problem claim is accurately attributed.**  
   Printed p. 39 explicitly says that existence of a core element optimal for each side is open. The preceding pages make clear this is the divisible/multi-unit transportation model, not merely the distinct-partners model. The report correctly limits this to historical status.

4. **The multiple-partners distinction is correct and important.**  
   In the multiple-partners model, each pair can contract at most once; quotas bound the number of distinct partners. Consequently, setting all pair weights to one generally gives a capacitated simple bipartite \(b\)-matching value, not \(\min(p(S),q(R))\). Splitting capacity owners into clones changes the player set and entire core, so it is not a model-preserving reduction. The report handles this properly.

5. **The 2024/2026 many-to-one paper does not update the general many-to-many question.**  
   Its introduction distinguishes multiple-partners from transportation games and states side-optimal existence only when one side has unit capacity. It contains no general many-to-many nonexistence theorem and no explicit current-open-status statement. [Free 2024 version, pp. 1–3](https://arxiv.org/pdf/2404.04847)

6. **The 2024 transportation-core abstract is too weak to establish current openness of this exact question.**  
   “Complete characterization of the core remains open” is broader and logically compatible with side-optimal existence having been settled separately. The report correctly labels this abstract-level evidence, but should avoid treating that paper as one of the “most likely” unread settlements without inspecting its theorem statements.

### Required revisions

- Replace the heading **“explicit priority gap, no precise match”** with something less easily mistaken for a literature-priority conclusion, such as:

  > **Bounded audit found no precise match; priority remains undetermined.**

- Remove or qualify:

  > “the most likely locations of prior art were not freely retrievable.”

  The audit does not establish which inaccessible works are most likely to contain the result. Say instead that the listed inaccessible originals remain unresolved comparison points.

- Change “same phenomenon as ledger K2 Example 1” to the narrower statement that both examples show the **entire core can strictly exceed the competitive/min-cut set**. They are not the same game or the same dimensional core structure.

- Clarify that the transportation specialization uses a **complete bipartite set of admissible pairs with unit weights**. Without completeness, the value need not equal the minimum of aggregate capacities.

- Explicitly label the 2013 slides and 2014 one-seller paper as historical status evidence, not current status. A free 2014 source also states the transportation-model question was open then: [One-seller assignment markets working paper, introduction](https://diposit.ub.edu/server/api/core/bitstreams/a83aed45-9902-4795-b6be-caf584281cf9/content).

### Bottom line

No inspected free source supplies a matching counterexample or theorem for the exact unweighted unrestricted game. The attached construction would fall within the transportation model’s \(a_{ij}\equiv1\) complete-bipartite subclass if its mathematics is valid. But the audit does not establish novelty or present-day open status, because important originals and later transportation literature remain unread.