# Four-cycle counterexample to one-quarter protection

This is a finite exact certificate, not a vanishing family or a computation of c(C4). Use four sectors of three players each, in order 0,1,2,3, and edges 01,12,23,03. The four 3x3 matrices, with parent/first-sector row index and second-sector column index, are recorded in FOUR_CYCLE_CERTIFICATE.json. All pair entries are in {0,1,2}. Only full four-player teams are productive.

The certificate provides an integral perfect matching of worth T=18 and a nonnegative full-team cover x of total 18. Hence integral matching worth is exactly 18 and x is a core point. Its minimum coordinate is tau=9/8. Player 3 in zero-based flattened indexing (sector 1, local label 0) is the target.

Let lambda_t>=0 be the six positive fractional team weights in residual_dual. Their player loads are at most one. Put d_i=1-sum_(t contains i)lambda_t. The recorded rational weights satisfy d_target>0 and

    T-sum_t lambda_t*w_t = tau*sum_i d_i.

For every full-core payoff p, efficiency gives the exact identity

    sum_i d_i*p_i + sum_t lambda_t*(sum_(i in t)p_i-w_t)
      = T-sum_t lambda_t*w_t.

All cover slacks and all deficits are nonnegative. As sum d>0, no core point can have every payoff strictly above tau. Since x attains floor tau, this is the optimal first floor. On the whole face p>=tau, the identity forces p_i=tau whenever d_i>0. In particular, the target's full leximin payoff is 9/8, irrespective of later stages.

The target's team in the recorded optimal perfect matching has value 5. Every core point makes each team in this matching tight; nonnegative teammate payoffs therefore imply H_target<=5. The recorded ideal_witness is a full-team cover of total 18 with target payoff 5. Thus H_target=5 and the full-leximin ratio is 9/40<1/4.

The standard-library check_cycle.py verifies all these rational identities, matching perfectness, the graph and matrix alphabet, and 162 full-team covers. No optimizer is needed to replay the target result. The saved complete x and H arrays also come from full raw-core exact optimization, but the proof above needs only x as a floor witness and the one target ideal; it does not infer the entire leximin vector from the floor witness. The H, levels and raw_exclusions fields are optimizer results, not certified by the standard-library checker. They are corroborated in the optional solver run, and are unnecessary for the claimed target ratio.
