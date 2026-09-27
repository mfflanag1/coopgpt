# Exact addition of sectors with zero pair values

Conventional proof, reviewed by Claude with no substantive defect; minor positivity and wording clarifications applied. The standing model allows zero matrices on edges of a fixed connected sector graph. This is not a theorem under a requirement that every allowed edge have a positive entry. Precisely, c(G) is the infimum of full-leximin payoff divided by the same player's whole-core ideal over nonnegative permitted matrices (including zero matrices), nonempty full cores, positive total worth, and players with positive ideal. Zero-ideal players remain in the selector.

## Source and extension

Start with k>=2 sectors of equal size m>=1, nonnegative full-team values, integral coalition matching, positive grand worth T, and nonempty entire core C. Only complete k-tuples are productive. Add ell>=1 sectors of the same size and define each full (k+ell)-team's value to be the value of its projection onto the original k sectors. All new incident pair matrices are zero in a pair-additive source model. Write K=k+ell.

Grand worth remains T: every extended matching projects to an old matching, and an old optimal perfect matching can be completed using the new sectors. Nonnegative old values and equal sizes ensure an optimal perfect matching exists.

## Exact description of the entire extended core

Let p denote the payoffs to old players and q^a_j the payoffs in new sector a. Each new sector's payoffs must be constant across labels j. To prove this, fix an old optimal perfect matching and match its teams to new-sector labels by any permutation in each new sector. Every such extended perfect matching has worth T, so every one of its team covers is tight at every extended core point. Exchange two labels j,h in one new sector while leaving all other choices fixed. The tight equation for either affected old team gives q^a_j=q^a_h. This also holds trivially when m=1. Write q_a for the common value, and R=sum_a q_a.

The entire extended core is therefore exactly

    q_a>=0, z in C, z_i>=R/k for every old player,
    p_i=z_i-R/k,
    each of the m players in new sector a receives q_a.

For necessity, set z_i=p_i+R/k. Nonnegativity holds and sum_old z=sum_old p+mR=T. Each extended team inequality says p(team)+R>=w(team), exactly the old team inequality for z. For sufficiency, the displayed construction is nonnegative and efficient and covers every extended team; it is the entire coalitional core because only full teams are productive and unmatched players have nonnegative payoffs. This is an affine description of the FULL core, not an identification with a proper subset.

## Ideals are exactly preserved for old players

For an old player i, every extended payoff satisfies p_i=z_i-R/k<=z_i<=H_i. Conversely, take an old ideal-attaining z and set all q_a=0, so p=z. Thus H_i^extended=H_i^old, without any positive-floor assumption.

## First optimal face

Let tau=max_(z in C) min_i z_i>=0. Compactness of the nonempty nonnegative efficient core ensures all maxima used here are attained. An extended core point with every payoff at least t has q_a>=t and p_i>=t, hence R>=ell*t and z_i>=t+R/k>=K*t/k. Therefore t<=k*tau/K.

Set t*=k*tau/K, choose any old floor-attaining z with z>=tau, and put q_a=t* for every new sector. Then R/k=ell*tau/K and p_i=z_i-ell*tau/K>=t*. This attains the upper bound; it is a strictly positive full-core point when tau>0. If tau=0, every extended core point has R=0, since 0<=R/k<=min_i z_i<=tau, and all new payoffs are zero. Thus zero-floor sources are not silently claimed to lift to positive-floor markets.

On the entire first optimal face, q_a>=t* and R>=ell*t*, while the old floor bound applied to z_i>=t*+R/k gives R<=k*(tau-t*)=ell*t*. Thus every q_a=t*, R=ell*t*, and z belongs to the old first optimal face F={z in C:z>=tau}. Conversely every z in F gives such an extended first-face point.

Consequently, if an old target is fixed to tau throughout F, its extended payoff is fixed to tau-ell*tau/K=k*tau/K=t* on the whole new first optimal face. Its full leximin payoff is t*, regardless of later stages, and its ideal is unchanged. The extended target ratio is exactly k/K times the old target ratio.

## Triangle-containing graphs

For the previously proved three-sector family indexed by q>=1, the sector size is m=3q+1, T=6q+1, tau=1/[3(q+1)], and a target is fixed to tau on the first face with ideal1. Pair entries belong to {0,1,2}.

Let G be any fixed graph on K>=3 vertices containing a triangle. Put the three source pair matrices on that triangle, set every other allowed edge matrix to zero, and add the remaining K-3 sectors as above (K=3 is the original theorem). The full K-sector market has

    K(3q+1) players; all pair entries in {0,1,2};
    integral T=6q+1; a strictly positive full-core allocation;
    target ideal1 and full leximin payoff1/[K(q+1)].

Its target ratio tends to zero, proving c(G)=0. If G is connected, this is within the active goal's stated allowed-graph model even though some allowed matrices are zero. Hence every connected four-vertex graph containing a triangle (paw, diamond, K4) has zero protection constant. P4 and K1,3 have constant1/4 by the all-tree theorem; C4 is the remaining connected four-vertex case.

## Limits and credits

The proof does not transfer along edge subdivision or contraction, and does not settle triangle-free cyclic graphs. It uses the existing three-sector vanishing family, ordinary matching/cover tightness, and a direct core calculation. Novelty of the extension is not asserted. This is not dummy-player invariance: adding a sector changes the productive full teams, and its new players have positive first-floor payoffs in the construction.
