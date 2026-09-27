# Pair-additive strict-triple assignment campaign

Authorized by the user on September 5, 2026: “Start next goal.”

Status: active research pilot. External specialist review of the three September 5 paper packages remains pending. The app goal tracker rejected a replacement because the prior external-review goal is unfinished; this file records the newly authorized research objective without falsely marking that review complete.

## Frozen target

Let I,J,K have the same finite cardinality m>=1. All triples are feasible, and only full triples generate surplus. For nonnegative real matrices A,B,C, let w_ijk=A_ij+B_ik+C_jk. A coalition earns its maximum weight of disjoint triples. Let T>0 be the integral matching value; nonnegativity and completeness allow an optimal perfect matching. Assume the entire labeled payoff core

    P={p>=0: sum p=T, p_i+p_j+p_k>=w_ijk for every triple}

is nonempty. All 3m players count, including any fixed-zero coordinates. Define x as the full lexicographic maximum of ascending sorted payoffs, z as the full lexicographic minimum of descending sorted payoffs, and H_i=max_{p in P}p_i. The target constants, over all such markets and all m, are

    c_pair = inf min_{i:H_i>0} x_i/H_i,
    d_pair = sup ||x-z||_1/T.

Determine whether c_pair>0, and separately whether d_pair<2; seek sharp values if a structural route supports them. Vanishing individual protection does not imply maximal selector disagreement. If c_pair>=c>0, the common-mass argument gives d_pair<=2(1-c).

## Permitted outcomes and calibration

Outcomes: a conventional proof; an exact infinite counterexample family; a corrected conjecture or structural lemma; an exhaustively certified bounded statement; or an explicit remaining obstruction with bounded negative evidence. None alone establishes global priority or field-level significance.

Calibration: reproduce the player-additive core simplex, x_i>=H_i/3, and w_ijk=1+1_{i=1}+1_{j=1}, whose selector distance is 4m/[3(m+2)]. Thus c_pair<=1/3 and d_pair>=4/3. Represent this benchmark with A_ij=1+1_{i=1}+1_{j=1}, B=C=0. Reject the existing sparse triple recurrence from this class by its nonzero third mixed difference. Full selectors must be computed through all lexicographic levels.

## Independent routes and first gates

1. Source gate: compare original Quint strict-team pair-additive results and later representation/decomposition results at theorem level. Preserve access gaps and exact hypotheses. Models allowing smaller profitable coalitions are different. No broad search before assessing relevant source implications.
2. Theory: derive restrictions imposed by pair-additivity on full cores, optimal matching equalities, and feasible payoff transfers. A representation must preserve all labeled payoff coordinates.
3. Bounded experiment: start with m=2 and m=3 nonnegative integer matrices and calibrated full selectors. Floating arithmetic is discovery evidence; promote witnesses only with independent exact certificates. A null sample is not an exhaustive theorem.

Initial outputs: SOURCE_GATE.md plus source/query ledgers; THEORY.md; reproducible experiment driver, inputs, calibration and witness certificates, EXPERIMENT.md; synthesized STATUS.md and proof-state ledger.

## No-go ledger and continuation rule

- Player-additive arrays are a settled calibration subclass, not the live target.
- The existing irreducible-triple recurrence is outside the target class.
- Pair-additive matrices need not be silently replaced by arbitrary triple values or by a model with productive pairs.
- Nonempty core must be verified using the integral matching value, not inferred from pair-additivity or a fractional relaxation.
- Independent normalizations or auxiliary players cannot be discarded when computing anonymous full selectors.
- Do not treat repeated clean samples, reparameterized recurrences, or an equivalent missing lemma as progress.

After one bounded discovery cycle and an independent adversarial check, continue only for a demonstrably new structural lemma, an exactly verified construction mechanism, or a substantive reduction. If an implication is equivalent in strength to the target without a new mechanism, mark that route blocked. Source novelty, proof correctness, and external priority review remain separate gates.
