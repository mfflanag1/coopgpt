# Exact zero-face reduction and a same-class obstruction

5 September 2026. Conventional proofs; no priority assertion or general ratio bound.

Let P be a nonempty core of a complete strict three-sector assignment game, with equal sector sizes and nonnegative triple values. Suppose its first global leximin floor is zero. Sector translation gives a zero minimum in every sector at every core point. Each sector then has a coordinate permanently zero on P: if every coordinate in that sector were positive somewhere, averaging those finitely many points would make every coordinate of that sector positive, a contradiction. Write Z_r for all such coordinates in sector r and N_+ for the remaining coordinates. Convex averaging makes all coordinates of N_+ strictly positive at some core point, so the first positive leximin level exists and is positive when T>0.

## Exact reduction to a generalized assignment game

For an active singleton i, give it weight d_i equal to the maximum original triple value over its two partners in the other sectors' Z sets. For an active cross-sector pair i,j, give it weight a_ij equal to the maximum original triple value over its remaining partner in that sector's Z set. Retain the original value for each all-active triple. Teams have at most one player per sector; allow singleton, pair, and triple teams. The projected core is exactly

    p>=0, sum(p)=T,
    p_i>=d_i,
    p_i+p_j>=a_ij,
    p_i+p_j+p_k>=w_ijk.

Indeed these are precisely the original covers after setting Z to zero and grouping duplicate left sides. All-zero triples have weight zero, because the original core is nonempty. Project an optimal perfect original matching onto the active players. The resulting disjoint generalized teams have total assigned weight at least T by the definitions of the maxima. Any projected core point covers all these teams and has sum T, bounding their total weight by T. Hence the generalized matching worth is exactly T, and the displayed inequalities are its full core. There is no unresolved integral-versus-fractional worth step.

The projection preserves every surviving player's entire payoff range and ideal. Both full selectors are preserved, since appending the same fixed zero coordinates to each nonnegative vector does not change either lexicographic comparison. The first positive stage becomes the first stage of this generalized game. The remaining sector sizes need not be equal. Even when they are equal, compulsory singleton and pair covers generally cannot be dropped or absorbed into a strict triple tensor.

In the pair-additive case the all-active triple tensor remains pair-additive. The additional singleton and pair constraints are the obstruction; deletion alone is not an exact reduction to the original class.

## An obstruction even to replacing the reduced strict tensor

Take four players in each sector, indexed 0,1,2,3. Player 0 in each sector is a center, and the other three are leaves. Set

    A_ij = 1 exactly when i=0 and j>0;
    B_ik = 1 exactly when i>0 and k=0;
    C_jk = 1 exactly when j=0 and k>0;

with all other entries zero. All three pair matrices are nonnegative. Every induced triple has weight at most one; a triple with exactly one center has weight one, and an all-leaf triple has weight zero. The allocation paying each center one and every leaf zero covers every triple and has total three.

Choose any one leaf from each sector and put them in a zero-weight team. The remaining players admit three disjoint teams, each with one center and two leaves, of total value three: allocate the two remaining leaves in each sector to the two teams whose centers lie in the other sectors. This is an optimal perfect matching. Its zero team must have total payoff zero in every core point, so the three arbitrarily chosen leaves are permanently zero. Hence all nine leaves are permanently zero. Triple covers then force each center to receive at least one, and efficiency forces each to receive exactly one. The full core is the singleton paying the centers (1,1,1).

After deletion, there is one surviving player per sector. The inherited strict tensor has value zero, while the inherited total surplus is three. More strongly, **no replacement strict three-player tensor can have the required labeled core or preserve these ideals and selectors**: for its single triple of value W>=0, the core is the simplex of nonnegative vectors summing to W. Preserving the selector (1,1,1) requires W=3, but then each ideal is 3, whereas each original surviving ideal is 1. Thus the proposed universal same-class deletion reduction is false even with equal nonempty remaining sectors.

The generalized reduction instead assigns each surviving singleton value one, recovering the singleton core exactly. This example does not violate the proposed one-sixth bound; it rules out one route for extending a positive-floor argument to the first positive stage.

Further extensions were paused when the separate positive-floor candidate became available.
