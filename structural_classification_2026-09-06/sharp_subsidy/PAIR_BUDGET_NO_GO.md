# Rejected pair-budget shortcuts

Status: exact counterexample, independently verified with standard-library rational arithmetic. This does not improve the global lower bound 1/3 or upper bound (7-4 sqrt(2))/3.

In the strict original model take three players in each sector and pair matrices

```
AB = [0 1 0; 0 0 0; 0 0 0]
AC = [1 0 1; 0 1 0; 0 0 1]
BC = [1 0 0; 0 1 1; 0 0 1].
```

The diagonal matching has worth 6. The nine explicit core witnesses in `verify_pair_budget.py` each sum to 6 and cover all 27 triples, proving T=6 and nonempty original core. Each diagonal team has worth 2 and is tight throughout the core; therefore every coordinate is at most 2. The witnesses attain 2 in every coordinate, so all original ideals are H_i=2.

The triple (A_0,B_1,C_2) has worth 3. Its stability constraint, together with the six other players' floors 2/3, forces total payment at least 7. Giving A_0 the payoff 5/3 and all other players 2/3 covers every triple and attains 7. Hence s_3=1 exactly.

Two tempting bounds fail:

1. **Diagonal pair budget:** s_3 cannot be bounded by the minimum, over the three pair matrices, of the entries used by the optimal diagonal matching. The AB diagonal budget is zero here.
2. **Cycle grand-worth increment:** s_3 cannot be bounded by T minus the largest grand worth of the three markets obtained by deleting one pair matrix. Deleting AB leaves the diagonal worth 6 and cannot increase any coalition worth, so that difference is zero here.

The second counterexample compares the original frozen ideals with a proposed numerical bound; it does not recompute ideals after subsidy. Removing AB changes the original core geometry even though grand worth stays fixed.

The separate pairwise matching optima are 1,3,3 and sum to 7>T. Thus this example does not refute any conjecture restricted to simultaneous compatibility of optimal bilateral matchings. No such conjecture is established here.

Both shortcuts belong to the cycle-removal budget mechanism. Retire that mechanism in this form. The live direction remains improving the universal aggregate pair-coverage bound, or finding a market above 1/3. In particular, distinguish the count configuration where the current constructor loses coverage from an actual extremal market; its extremality has not been proved.

Verification: `python3 -O verify_pair_budget.py`. The verifier checks all 36 perfect matchings in both markets, all nine core witnesses against all 27 triples, the exact subsidy primal and lower certificate, bilateral optima, and a failing zero-subsidy negative control.
