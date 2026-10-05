Verdict: **revise**

The two principal mathematical results appear sound:

- The pivotal-height rule is explicitly defined, own-monotone, has the stated nonconstant budget bounds, and is decisively falsified by the \(k=2\) coalition.
- The report-independent random-order obstruction appears to prove an \(\Omega(\log k/\log\log k)\) scale requirement for that class, which genuinely lies outside the earlier independent-threshold class.

However, several claims exceed the supplied proof.

## Required corrections

1. **The claim that a constant rule must sometimes pay owners with \(M_i=0\) is not established.**

   In the proposed profile, after lowering one large owner, \(T=3/4\). Each pool-1 half-owner has
   \[
   M_i=\min(1/2,\,3/4-1/2)=1/4.
   \]
   Paying both half-owners \(1/4\) costs only \(1/2\), independent of \(k\), and covers every displayed coalition without paying any non-pivotal small owner. Thus the argument gives only the stated disjunction; it does not force its second branch.

   Remove the “constant rule must” assertion or label it explicitly as an unsupported conjectural design heuristic.

2. **The claimed lower-bound construction showing the logarithmic budget is “real” is insufficiently specified.**

   “Pool counts growing geometrically” does not define a finite profile or calculate its payment. Either give the exact number of pools at each scale and prove the resulting \(\Omega(T\log m)\) payment, or drop this tightness claim.

3. **The three asserted exact-cost covering families are not verified in the submission.**

   They are reported as hand-derived facts without complete profile definitions or coalition checks. They should be omitted, supplied with proofs, or clearly labeled as unchecked observations rather than established results.

4. **Clarify the random-order notation and quantifiers.**

   Define \(\phi_i\) explicitly as the unscaled expected marginal payment. State that the random slot placements are an averaging argument yielding a deterministic capacity assignment for the fixed, possibly nonexchangeable order distribution \(\mu\). This is implicit but important.

## Findings that withstand review

For the height rule:

- \(a_i=C_j-c_i\) is fixed along owner \(i\)’s report coordinate.
- Although \(q_j\) can change with \(c_i\), the own pool contributes exactly one to \(Q(h)\) throughout the integration interval because \(q_j\le a_i\le h\). Hence the integrand’s remaining terms are report-independent.
- The \(k=2\) counterexample is exact: the three pivotal owners receive \(1/4\), the two small pool-2 owners receive zero, and the identified coalition has value \(1/2\) but payment \(1/4\).
- The \(H_kT\) budget argument works if tied \(q_j\)’s are assigned ranks consistently so that \(Q(h)\) dominates each assigned rank.

For the random-order obstruction:

- Expected marginal contributions are own-monotone for every fixed order.
- Payments telescope to exactly \(\lambda T\).
- Randomly selecting one owner from each \(L\)-owner pool gives expected selected payment at most \(P_s+1/L\).
- The tail-slot event, independence across pools, and averaging over the \(b_j\)-ranks yield the stated contradiction.
- Inverting \(k\lesssim \Lambda\log\Lambda\,(16\Lambda)^{2\Lambda}\) gives \(\lambda=\Omega(\log k/\log\log k)\).

After removing or proving the three overclaims, this would be an acceptable partial result: an exact failed nonlinear construction plus a credible obstruction for a genuinely different mechanism class, while correctly leaving the unrestricted constant-budget question open.