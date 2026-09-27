# A twelve-player C4 market with ratio 5/44

Finite exact result; no optimal-size or vanishing claim. Four sectors, three players each, edges 01,12,23,03. The integer pair matrices in C4_INTEGER_CERTIFICATE.json have entries between0 and25. Only complete four-player teams are productive. Full core and integral matching conventions are unchanged.

The diagonal perfect matching has team values32,10,9, so T>=51. The recorded positive cover x sums to51 and covers all81 teams, so T=51 and x lies in the entire core. Its minimum coordinate is tau=5/4; the target is sector0, label0.

Ten nonnegative fractional team weights lambda in the certificate have player loads at most1. Their deficits d=1-load obey d_target=1/20>0 and the exact identity

    T-sum_t lambda_t*w_t = tau*sum_i d_i.

Every positive lambda team is tight at x and every positive-deficit player has x_i=tau. For any core point p, efficiency gives

    sum_i d_i*p_i + sum_t lambda_t*(p(t)-w_t)
        = T-sum_t lambda_t*w_t.

Consequently no core point has all coordinates strictly above tau, and every core point with p>=tau has p_target=tau. Thus the target's FULL leximin payoff is5/4, independent of later stages. A floor witness is not being identified with the entire selector without proof; the target pinning is sufficient.

The ideal upper certificate is particularly simple. The disjoint teams (1,2,2,2) and (2,1,1,0) have total value40, and neither contains the target. Their combined core inequality and efficiency bound the total payoff of their four unmatched players by11. In particular H_target<=11. The recorded cover

    y=(11,1,7; 0,2,2; 0,7,0; 21,0,0)

has total51, covers every team, and gives the target11. Hence H_target=11 and the ratio is5/44.

The standard-library checker independently verifies all162 covers, the diagonal integral matching, the fractional loads and floor identity, and the ideal dual. The complete optimizer x/H/levels fields are auxiliary; only the target result is certified by this argument. The value5/44 improves the previously certified C4 upper bound9/40. It does not determine c(C4) or settle acyclicity as a necessary condition.

Discovery: an exact disjunctive-linear complementarity synthesis first found a rational ratio below1/8. An affine simplification and rescaling produced the integer matrices here. The final witness is checked from scratch, not trusted because of its discovery process. A separate search for a first-face ratio below1/16 at m=3 timed out; that observation is unknown, not a no-go theorem.
