# Exact core compression by sector minima and local completions

Date: 2026-09-07. Conventional all-size equivalence for the sparse two-matching reduction, with symbolic and exact rational verification. This is an intermediate tool for the active sharp-bound problem, not a proof of the one-third inequality. Global bounds remain 1/3 <= S_3 <= 2/5; novelty and external review remain unconfirmed.

## Setting and theorem

Fix m labels in each of sectors A,B,C. Pair entries are nonnegative and supported on the union of the diagonal matching mu and an ordinary partial matching P of r teams. P may contain teams with repeated diagonal labels and may share pairs with mu. Define a supported pair as one appearing in mu or P, even if its numerical value is zero. Let T be the sum of the diagonal team worths, and retain the existing requirement that mu be optimal and the original entire core be nonempty when applying the sharp-subsidy reduction.

Introduce three auxiliary variables ell_A,ell_B,ell_C. For a payoff vector x, use the following constraints:

1. x_i >= 0, ell_s >= 0, and ell_s <= x_i for every sector-s player i.
2. For each supported pair {i,j} from sectors s,t, with missing sector u and pair value a_ij,

       x_i+x_j+ell_u >= a_ij.

3. The original full-team inequality for every diagonal team and every team in P.
4. For each off-diagonal supported pair joining labels a != b, the original full-team inequalities obtained by completing that pair with the missing-sector player at label a and at label b.
5. sum_i x_i=T.

**Theorem.** A payoff vector x belongs to the entire original core if and only if there exist ell_A,ell_B,ell_C satisfying this system. There are 3m+3 variables, at most 7m+10r listed inequalities excluding variable nonnegativity bounds, and one total equality. Duplicate team constraints can be removed. No genuine minimum equality is required in the LP.

## Proof: the original core implies the compressed constraints

Given an original core point x, set ell_s=min_{i in sector s} x_i. Nonnegativity and the lower-envelope constraints hold. Complete any supported pair with a player attaining the missing-sector minimum. Its original full-team value is at least that pair's value because the other pair values are nonnegative. Its core inequality therefore implies constraint 2. Constraints 3 and 4 are original full-team inequalities. Efficiency gives constraint 5.

This direction uses pair nonnegativity. It does not assert that an arbitrary pair is itself a productive coalition in the strict full-team model.

## Proof: the compressed constraints cover every original coalition

Consider any full team t. If it is a listed local team from constraints 3 or 4, its inequality is explicit. Otherwise classify its supported off-diagonal pairs.

Two off-diagonal pairs of t share an actual player. Each such pair belongs to a P-team. Since P is an actual partial matching, the shared player belongs to only one P-team; hence both pairs belong to that same team, and their union identifies t as a team of P. This case was already covered by constraint 3. The reasoning remains valid when a P-team has repeated diagonal labels.

If t has exactly one off-diagonal supported pair, its missing-sector player either has one of that pair's endpoint labels or has neither. In the former case t is a listed completion from constraint 4. In the latter, t has no supported diagonal pair, and its other two off-diagonal pairs are unsupported. Its worth is exactly the single pair value. Add that pair's constraint 2 to ell_u <= x_k for the missing-sector player k to obtain the full-team inequality.

If t has no off-diagonal supported pairs, it is either fully diagonal, covered already, or has at most one supported diagonal pair. If it has one, the same pair-plus-minimum implication covers it. If it has none, its worth is zero and nonnegative payoffs suffice.

Thus every full-team inequality holds. Every original coalition produces by disjoint full teams with possibly unmatched players. Summing their inequalities and using nonnegativity covers the coalition. Together with efficiency, this proves core membership.

The row count follows from 3m lower-envelope constraints, at most 3m+3r supported-pair constraints, m+r diagonal/P constraints, and at most 6r off-diagonal completion constraints. Their sum is at most 7m+10r. If a P-pair is diagonal or a team is duplicated, the count only decreases.

## Local completions give within-sector difference inequalities

At any original core point every diagonal team is tight. This permits a useful exact rewriting of constraint 4. For an AB pair between A_a and B_b, a != b, the completions (a,b,a) and (a,b,b) imply respectively

    x_B(b)-x_B(a) >= AB[a,b]+BC[b,a]-AB[a,a]-BC[a,a],
    x_A(a)-x_A(b) >= AB[a,b]+AC[a,b]-AB[b,b]-AC[b,b].

These are identities obtained by substituting the diagonal equalities, not additional assumptions. The extra cross-pair terms must be retained for repeated-label P-teams. For a distinct-label P-team (a,b,c), c differs from a and b; the partial-matching property then makes BC[b,a]=AC[a,b]=0. Sector permutations give the other completion identities.

For any directed cycle of these same-sector difference inequalities, the sum of their right sides is at most zero whenever the original core is nonempty. If the sum equals zero, every inequality on that cycle is tight at every original core point. This follows because their nonnegative slacks sum to zero. More generally, paths give valid difference bounds by addition.

The same difference inequalities hold for the original ideal vector H. If x_i >= x_j+c for every original core point, choose a core point attaining H_j to get H_i >= H_j+c. If a cycle forces fixed differences for all core points, those differences also hold for the ideals. This is a constraint on coordinate maxima that survives their being attained at different allocations.

These identities explain the uniform-ring collapse: its cyclic AB completion comparisons have zero total slack. The broken-ring edit makes the total slack negative, so the equality conclusion no longer follows. They do not by themselves bound the full protected subsidy; the P-team and pair-minimum constraints still couple sectors and must not be discarded.

## Independent checks and discovery scope

`sector_min_core.py` constructs the sparse rows. Run `python3 -O verify_sector_min_core.py` to check their implications symbolically. For every full team, the checker either identifies its exact listed row, adds one supported-pair row and one minimum lower-envelope row with an exact coefficient identity, or verifies that the team has zero worth and follows from nonnegativity.

The checker enumerates all 187 partial matchings at sector sizes 1,2,3, including repeated-label teams and shared diagonal pairs, then checks the 34 retained cyclic-frontier records. These entail 112,057 symbolic full-team checks. It also extends every retained fixed-pattern core witness by its actual sector minima and checks 116,673 compressed inequalities with rational arithmetic. A missing local completion constraint is rejected. The all-size equivalence comes from the case proof above; the finite symbolic checks corroborate it.

A floating all-weight fixed-obstruction search with these rows reproduced the known cases at r=2,4,6. For two new supports each at r=12 and r=16, it returned (r-1)/(3r) to numerical precision. Those new numerical optima are discovery evidence only, not accepted exact all-weight bounds. Both r=24 attempts hit their 35-second limits. Their partial solver status establishes neither infeasibility nor an upper bound, and they are not counted as solved. No counterexample to the proposed unicyclic formula was found in the completed runs; the search is not exhaustive.

The source driver and numerical records are retained in discovery/sector_minimum_archive.zip with a hash manifest. The core equivalence and its exact checker do not depend on any numerical solver, solver status, or discovery objective.

## Next mathematical action

Use the three shared sector-minimum variables and within-sector difference constraints to eliminate local factors around an incidence cycle. The required result is a boundary inequality controlling original ideal expansion, while preserving the P-team constraints; a fresh LP statement or more matching numerical examples is not success. The exact no-go in CYCLIC_OPTIMA_REQUIRED.md prevents assuming a forest-supported optimum, and BROKEN_RING_THEOREM.md prevents bounding cycle-opening cost solely by the removed pair value.

The universal unicyclic inequality and the remaining multiple-hub tree and multiple-cycle cases are still unproved. Completion criteria of the active sharp-constant goal are unchanged.
