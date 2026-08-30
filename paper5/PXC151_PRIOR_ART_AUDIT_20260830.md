# PXC151 prior-art audit — 2026-08-30

Status: preliminary author-side primary-source screen, not an external
specialist correctness or novelty opinion.

## Candidate contribution being screened

PXC151 constructs a singleton-normalized exact game `K_{m,r}` for every
`m>=2,r>=3`, gives closed opposing core selectors, and proves an infinite
strict improvement over the paper's balanced two-generator benchmark.  Its
asymptotic separation coefficient is

```text
C(a)=(a+1)(2a+1)/a,
min C(a)=3+2sqrt(2)<8.
```

The novelty question is this selector-specific construction and quantitative
separation.  Lower-envelope exactness, semi-balanced incidence certificates,
and the definitions of Lmin/Lmax are classical and are not novelty claims.

## Primary sources checked

- Dutta and Ray (1989), *A Concept of Egalitarianism Under Participation
  Constraints*, Econometrica 57(3), 615--635,
  <https://doi.org/10.2307/1911055>.
- Arin, Kuipers, and Vermeulen (2003), *Some characterizations of egalitarian
  solutions on classes of TU-games*, Mathematical Social Sciences 46,
  <https://doi.org/10.1016/S0165-4896(03)00051-9>.
- Llerena and Mauri (2017), *On the existence of the Dutta--Ray's egalitarian
  solution*, Mathematical Social Sciences 89,
  <https://doi.org/10.1016/j.mathsocsci.2017.07.002>.
- Biswas, Parthasarathy, Potters, and Voorneveld (1999), *Large Cores and
  Exactness*, Games and Economic Behavior 28,
  <https://doi.org/10.1006/game.1998.0686>.
- Csóka, Herings, and Kóczy (2011), *Balancedness conditions for exact games*,
  Mathematical Methods of Operations Research 74,
  <https://doi.org/10.1007/s00186-011-0348-3>.
- Studený and Kratochvíl (2022), *Facets of the cone of exact games*,
  <https://arxiv.org/abs/2103.02414>.
- Vazirani (2024), *Equitable Core Imputations via a New Adaptation of the
  Primal-Dual Framework*, <https://arxiv.org/abs/2402.11437>.
- Gangam, Garg, Shahkar, and Vazirani (2024), *Equitable Core Imputations for
  Max-Flow, MST and b-Matching Games*,
  <https://arxiv.org/abs/2403.06037>.

The cumulative adjacent-source table and subscription-database obligations
are in `paper5/S6_SPECIALIST_NOVELTY_SIGNOFF.md`.

## Findings

1. The checked egalitarian and large-core sources define or characterize the
   relevant selections on convex, exact-partition, large-core, or neighboring
   domains. They do not state a normalized L1 separation theorem for the two
   opposing selectors over arbitrary singleton-normalized exact games.
2. Exact-balancedness and exact-cone sources supply the correct classical
   language for the sparse incidence certificate. The PXC151 Lmax dual should
   be presented as a concrete semi-balanced/LP certificate, not as a new
   general duality.
3. The recent equitable-core papers explicitly compare leximin and leximax
   and provide algorithms on combinatorial-game domains. The inspected
   statements do not give this lower-envelope family, its ratio, or a
   coefficient below eight.
4. No checked source yielded the three-generator block family, the
   `3+2sqrt(2)` coefficient, or an implication that subsumes it. This is only
   a non-location result, not evidence that no equivalent result exists.

## Required external determination

A cooperative-game specialist should independently search MathSciNet or
zbMATH, citation networks around the exact-partition/large-core papers, and
terminology including egalitarian set, Lmin/Lmax, Lorenz set, exactification,
semi-balanced systems, and coherent lower probabilities.  The reviewer must
separate:

- correctness of the all-parameter selector proof;
- significance of beating one benchmark without a matching upper bound; and
- novelty relative to constructions or quantitative separation results under
  different terminology.

Until that review is received, the permissible description is “internally
proved infinite benchmark improvement; external correctness and prior-art
assessment pending.”
