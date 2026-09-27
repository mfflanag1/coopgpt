# Matched-team cloning: exact full-core encoding and a local distance reduction

5 September 2026. One bounded structural route. All statements below are independently derived conventional mathematics, supplemented by finite exact checks. No novelty or external-source theorem claim is made. Only this scratch directory was written.

**Result.** Cloning the players of each optimal matched team by an arbitrary positive integer multiplicity preserves the entire original core as a labeled coordinate-replication image. It also preserves both full sorted selectors and every individual ideal fraction. This operation therefore cannot amplify the failure of individual protection. It can, however, concentrate the normalized selector distance on one matched team. Consequently the class-wide distance supremum equals the supremum of the distance ratio on a single positive-value team belonging to an optimal matching. This is an explicit class-preserving construction with all auxiliary payoff coordinates and total surplus controlled.

## 1. Exact construction

Start with a complete three-sided strict assignment market with equal sector size m, nonnegative pair matrices A,B,C, and nonempty full core P. Only full triples generate surplus. Let M consist of triples `(i_t,j_t,k_t)`, t=1,...,m, and be an optimal perfect matching. Write `s_t=w(i_t,j_t,k_t)>=0`; then `T=sum_t s_t>0`.

Choose positive integers r_t. Replace each of the three agents in team t by r_t distinct copies. Every sector now has size `m'=sum_t r_t`. Pair entries between copies are inherited from their original agent types:

`A'_(i,a),(j,b)=A_ij`, and analogously for B' and C'.

Thus all triple types, including every mixed triple between different copy blocks, are present with the original type's weight. Pair entries remain nonnegative and keep their original upper bound and integrality. This is not null-dummy padding: the new agents have the full economic interactions of their types.

Let D_r duplicate payoff coordinate i exactly r_t times when i belongs to original team t. Define `T_r=sum_t r_t*s_t`.

**Full-core theorem:** the enlarged market has integral worth T_r and entire labeled core exactly `P_r=D_r(P)`.

Proof of worth and one inclusion. The r_t copies of team t can be matched coordinatewise, producing a perfect matching of value T_r. Every p in P has `p(i_t)+p(j_t)+p(k_t)=s_t`: matching covers have nonnegative slack and their sum equals efficiency. Its lift D_r(p) is nonnegative, covers every enlarged triple by type, and totals T_r. It therefore upper-bounds every enlarged matching, including partial matchings. Hence T_r is the integral optimum, and every lifted point belongs to the full core. Triple covers plus nonnegativity imply all coalition inequalities by summing over disjoint teams.

Proof of the reverse inclusion. At any enlarged core point every coordinatewise cloned matching triple is tight. Consider two copies a,b of an original first-sector agent in team t. Replace that first-sector agent in the matched team using copy b by copy a. Its weight remains s_t. The resulting cover, compared with the tight matched team using b, implies `p(i_t,a)>=p(i_t,b)`. Reversing a and b gives equality. The same argument applies separately in each sector. All copies of each original coordinate are therefore forced equal throughout the entire enlarged core.

Call the common original-coordinate vector p. Each original triple cover holds because all types have at least one copy. Each original matched team is tight, so `sum_i p_i=sum_t s_t=T`. Nonnegativity holds as well. Therefore p belongs to P. This proves exact full-core equality and injectivity, with no projection that hides free auxiliary payoffs.

Positive multiplicities are essential: setting r_t=0 deletes types and need not preserve the core. Zero-value teams are allowed; all their payoffs, original and copied, are forced to zero by nonnegativity and matching tightness.

## 2. Full selectors do not change under coordinate replication

For any nonempty compact convex set K and any positive integer multiplicity for each coordinate, duplication carries the full ascending leximin of K to that of the duplicated set. The same is true for the full descending lexicographic minimum.

Here is a proof covering labeled uniqueness and all levels. At an ascending stage, with some coordinates already frozen, maximize the minimum of the remaining coordinates. On the maximizing face freeze every remaining coordinate identically equal to the attained floor. There is at least one: otherwise, for each coordinate choose a point of the face where that coordinate is strictly larger, and average these finitely many points. Convexity then produces a point with every remaining coordinate strictly above the supposedly optimal floor. Iterate. Compactness gives each floor, and at least one coordinate freezes per stage, so eventually a unique labeled vector is determined. The procedure is full ascending leximin.

Repeated copies impose exactly the same floor inequalities as the original coordinates, and a coordinate is forced at the floor precisely when all its copies are. Each stage therefore corresponds to the same original face, regardless of positive copy counts. For the descending selector, minimize the maximum and freeze coordinates identically equal to the ceiling; the same averaging and duplication argument applies with reversed inequalities.

Convexity is important. One should not claim arbitrary replication preserves the lexicographic order of every pair of sorted vectors: for example (0,1) and (1,0) originally tie, but duplicating the first coordinate twice breaks their sorted-vector tie. The convex feasible-face argument, not that false pointwise claim, establishes selector invariance.

Applying the lemma gives `x_r=D_r(x)` and `z_r=D_r(z)`. The exact full-core theorem also gives `H_(i,a)=H_i`. Thus every original and copied ideal fraction is unchanged, including fixed zeros handled under the original `H_i>0` convention. Uniform replication preserves normalized distance as well.

## 3. Concentrating distance on one optimal team

Put `D_t=sum_(i in team t) |x_i-z_i|`. Since both vectors sum to s_t on team t, `0<=D_t<=2*s_t`. In particular s_t=0 forces D_t=0, so no zero denominator is needed.

The enlarged normalized distance is exactly

`rho_r = (sum_t r_t*D_t)/(sum_t r_t*s_t)`.

It is a weighted average of `R_t=D_t/s_t` over positive-value teams, using weights r_t*s_t. Fix one positive-value team t, let r_t=L, and keep every other multiplicity one. As L tends to infinity, `rho_r -> R_t`, while all ideal fractions remain unchanged. This supplies an explicit finite construction for approaching the chosen local ratio.

For the class C of all balanced nonnegative pair-additive strict markets, define

`S_local = sup_(G in C, M optimal perfect, t in M with s_t>0) D_t/s_t`.

Then **`d_pair=S_local`**. One inequality follows because any original global distance is a weighted average of its team ratios. The reverse inequality follows by the above cloning construction, since each enlarged market still belongs to C. This also gives a useful finite success gate: any one exactly certified team with `D_t/s_t>4/3` yields finite enlarged markets with global distance greater than4/3, even when the original global distance is small. If a fixed base market has all local ratios below two, cloning that market alone cannot approach two.

The reduction is constructive rather than a claim that local and global difficulty automatically differ. The remaining substantive target is a local team with a larger certified ratio, or a new universal bound on all such local ratios.

## 4. Existing witnesses and bounded checks

For the exact nine-player counterexample, the matched teams and local ratios are:

| Team | Value s_t | Distance D_t | Local ratio |
|---|---:|---:|---:|
| (a,f,i) | 1 | 4/3 | 4/3 |
| (b,d,h) | 3 | 2/3 | 2/9 |
| (c,e,g) | 4 | 5/3 | 5/12 |

Taking multiplicities `(L,1,1)` gives sector size L+2, total surplus L+7, and

`rho_L=(4L+7)/(3L+21) -> 4/3`.

Every copy of player d still has ideal fraction5/18. Thus this known gadget supplies no improvement over the established4/3 distance benchmark through cloning. The exact dense discovery example has local ratios4/33,17/84,1/12 on its saved optimal matching, also offering no improvement.

`check_cloning.py` uses a fresh raw Z3 encoding, imports no campaign scientific module, and performs no optimization. Seven multiplicity vectors cover sector sizes3–6. For each it checks both directions of full-core correspondence and every forced face of both full selectors. All126 queries returned UNSAT; any other result, including UNKNOWN, raises an error. Direct Fraction calculations additionally verify cover feasibility, total surplus, and the distance formula. These are finite solver corroborations of the all-parameter conventional proof, not a formal all-parameter proof.

The same script reanalyzes all optimal perfect matchings in the272 saved cycle1 screen records. Of these,269 have saved selectors. No local ratio exceeded4/3 beyond roundoff; the largest reported value was1.3333333333333375. This is floating discovery evidence on existing records, not an exhaustive theorem. No new random instances were generated and no uncertified excess was nominated. `check_results.json` records inputs, their hash, scope, and results.

## 5. Outcome and remaining interface

This route provides a full-payoff auxiliary-player encoding, a proved no-go for amplifying individual protection by matched-team cloning, and an exact reduction of the global distance supremum to local optimal-team distances. It does not encode arbitrary irreducible triple interactions into pair-additive ones: inherited pair matrices preserve their structural restrictions. It also does not prove that more general auxiliary-player constructions cannot realize gain amplification.

The next useful distance gate is local: retain all full-core coordinates and seek a certified positive-value optimal team with ratio above4/3. The next individual-protection gate requires a construction that changes the underlying core geometry, since repetition alone leaves every ideal fraction fixed. Source priority is unassessed; no old representation or general fairness principle is being claimed new.
