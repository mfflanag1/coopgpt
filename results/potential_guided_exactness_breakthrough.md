# Potential-guided exactness repair

The recoloring-capacity dual assigns a player-potential vector to each game.
The initial experiment restricted the full endpoint-exactness LP to tight
coalitions drawn from:

1. weak and strict level sets of the three potential vectors and all pairwise
   potential differences;
2. coalitions on the circuit support and their complements;
3. the two arms and their complements.

The restricted LP is stronger than the full endpoint test: it demands exact
witnesses only at this selected family, so a zero optimum gives a certificate
using no other tight coalition.

All 15 subunit-capacity circuits in the representative six-player frontier
pass. Candidate families contain 14--30 of the 62 proper coalitions; the
verified rational duals use only 3--11 tight coalitions. Every used tight
coalition is either a potential threshold set or a supported coalition (or
its complement); no unexplained set is needed.

## Source ablation

An exact ablation on those 15 circuits, the five-player Type-I exception, and
15 deficient circuits from representative probes of all six seven-player
geometries
now gives a substantially cleaner result:

| allowed tight-witness source | verified cases |
|---|---:|
| all potential threshold sets | 31/31 |
| bumped-game potentials \(u_1,u_2\) only | 31/31 |
| pairwise potential differences only | 31/31 |
| \(u_1\) only | 27/31 |
| \(u_2\) only | 19/31 |
| circuit support only | 9/31 |
| circuit support and complements | 16/31 |

Here a threshold family contains every nontrivial weak or strict superlevel
set. The two arm potentials generate only 1--6 candidates in these examples.
Exact inclusion minimization gives a much stronger regularity: in every one of
the 31 cases, a single threshold coalition \(U\) suffices. Twenty-eight
repairs use two blocks and three use three, with every block tight at that same
\(U\). Thus supported sets
and complements are not needed at all; their appearance in the first duals
was LP degeneracy. The repeated success of three different threshold
generators is evidence for an order-theoretic mechanism rather than a finite
support coincidence.

The search can be reduced once more. Let
\(P_g=\operatorname{argmax}_{i\in N}u_{g,i}\) for the two bumped-game
potentials. In all 31 cases, at least one of the two candidates \(P_1,P_2\)
is already a successful single witness. \(P_1\) works in 24 cases and \(P_2\)
in 16, with overlap. Thus the current conjecture is a two-cut alternative,
not a search over an entire threshold chain. Across all arm-potential
thresholds, 95 of 114 individual candidates work.

The top-set audit gives a further exact simplification. In all 31 cases a
successful top-set certificate can be chosen with no base-game block and with
zero total coverage defect:
\[
 \mu_0=0,\qquad \delta_1+\delta_2=0.
\]
Consequently it is enough to choose one subcollection \(0\leq w\leq q\) whose
degree vector is \(\alpha\mathbf1+\delta\mathbf1_U\); the other bumped-game
collection is \(q-w\). This turns the conjecture into a box-constrained degree
zonotope problem rather than a general three-color decomposition problem.

The ordinary capacity problem itself has the same reduction: any base-color
mass can be split between the two bumped colors without decreasing either
retention constraint. Its dual therefore has one intrinsic zero-sum potential
\(z\). Let
\[
 P^+=\operatorname{argmax}_i z_i,
 \qquad P^-=\operatorname{argmin}_i z_i.
\]
The exact canonical audit finds that \(P^+\) repairs 29/31 cases and \(P^-\)
repairs 29/31; their union repairs all 31, with
\(\max\{\tau_{P^+},\tau_{P^-}\}=1\) exactly. This is stronger and more
intrinsic than the earlier \(u_1,u_2\) top-set pattern.
Every individual extreme capacity is either \(\rho\) or \(1\). The four
failed extremes stay exactly at \(\rho\), suggesting that the proof should
analyze whether the new orthogonality hyperplane intersects the original
dual optimal face; if it does not, circuit minimality may force the next face
to occur at level one.

This is now explained by a support-nullspace calculation. A coalition \(U\)
is flexible exactly when some zero-sum player vector vanishes on every
coalition in \(\operatorname{supp}(q)\) but not on \(U\). Shifting the dual
potential along that vector enforces the fixed-witness equation for free, so
\(\tau_U=\rho\). The audit finds exactly four such extremes, matching the four
failures coefficientwise; no circuit has both extremes flexible. Every rigid
extreme jumps to one.

Projecting the optimal potential orthogonally onto the support nullspace
removes exactly this gauge freedom while preserving every supported coalition
sum and the dual objective. The exact rational quotient audit then makes all
four failures disappear: both extreme sets repair in every one of the 31
cases, so all 62 quotient-canonical capacities equal one. The strongest
current conjecture is therefore that both extremes of a support-orthogonal
optimal potential always repair.
The corresponding primal defects have a uniform orientation: \(\delta<0\)
at every maximum-set repair and \(\delta>0\) at every minimum-set repair.

The quotient step is supported well beyond the deficient corpus. Exact rank
calculations over the 609 exhaustive five-player circuits and 86
representative six-/seven-player circuits find 14 nontrivial support
nullspaces, all one-dimensional and generated by swapping support-indistinguishable
players; there are no non-twin directions in 695 cases. Under this
twin-generation property, every level set of a support-orthogonal potential
is automatically rigid.

The strongest compression occurs already at the five-player Type-I orbit.
The old generic endpoint dual used eight blocks. Potential guidance finds two
that are both tight at the singleton \(\{1\}\):

\[
\begin{aligned}
t_A(123)+t_A(145)
  &\leq t_A(N)+t_A(1),\\
t_B(13)+t_B(23)+t_B(124)+t_B(35)+t_B(45)+t_B(245)
  &\leq 3t_B(N)-t_B(1).
\end{aligned}
\]

The first collection has coverage
\(\mathbf1+\mathbf1_{1}\); the second has coverage
\(3\mathbf1-\mathbf1_{1}\). Expanding the bumps and adding cancels
\(b(1)\) and yields the Type-I circuit bound exactly. This replaces the
exceptional machine certificate in the manuscript with a short hand proof.

This does not yet prove that potential guidance always works. It isolates a
clean dimension-free target: prove that the top set of at least one bumped-game
potential satisfies the single-witness recoloring system. The precise
conjecture and proposed separation argument are in
`results/potential_guided_uncrossing_program.md`.

Implementation and evidence:

- `src/analyze_potential_guided_exactness.py`;
- `src/audit_potential_guided_sources.py`;
- `src/minimize_potential_guided_tights.py`;
- `results/potential_guided_source_ablation.json`;
- `results/potential_guided_minimal_tights.json`;
- `results/disjoint_n6_*_potential_guided_exactness.json`.
