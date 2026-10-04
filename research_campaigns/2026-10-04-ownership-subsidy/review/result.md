**Result: all three claims are true on the four-owner domain, by hand proof.** Nothing was run by machine and no literature search was done, so the algebra below should be checked independently with exact rationals.

## Notation and formula

Capacities are (a,b | c,d) and T = min(a+b, c+d). Write m_ij = min(c_i, c_j) for cross pairs and w_i = v(N\i):

- w_1 = min(b, c+d)
- w_2 = min(a, c+d)
- w_3 = min(a+b, d)
- w_4 = min(a+b, c)

Shapley weights for n=4 are 1/4, 1/12, 1/12, 1/4 for |S| = 0, 1, 2, 3. Singletons and same-side pairs have value 0, so

φ_1 = (1/12)[m13 + m14 + (w_4 − m23) + (w_3 − m24) + w_2] + (1/4)(T − w_1).

The other three follow by the symmetries 1↔2, 3↔4 and side swap. The four values sum to T. At (2,1,1,1) this gives φ = (7/12, 1/4, 7/12, 7/12).

## Theorem 1: φ(S) ≥ (5/6)·v(S) for every S and every profile, and 5/6 is sharp

**Zero-value coalitions.** For singletons, same-side pairs and the empty set, v = 0 and φ_i ≥ 0 because v is monotone.

**Grand coalition.** φ(N) = T.

**Cross pair {2,3}** (the other three pairs follow by symmetry). Summing the formulas:

φ_2 + φ_3 = (1/6)(m23 + w_4 + w_1 − m14) + T/2 − (w_2 + w_3)/6.

So the claim is equivalent to G := 3T + w_1 + w_4 − w_2 − w_3 − m14 ≥ 4·m23.

- The side swap (1↔4, 2↔3) fixes {2,3}, so assume a+b ≤ c+d.
- Then T = a+b, w_2 = a, w_1 = b, and G = 2a + 4b + w_4 − w_3 − m14.
- Since w_3 ≤ a+b and m14 ≤ a, G ≥ 3b + min(a+b, c) ≥ 4·min(b,c). ∎

Equality with m23 > 0 in this case holds exactly when d ≥ a+b, b ≤ c, and (c = b or a = 0); the mirrored conditions apply when a+b ≥ c+d.

**Triple {1,2,3}** (the others follow by symmetry). φ(S) = T − φ_4, and the claim is equivalent to

K := 9T − 7w_4 − w_1 − w_2 − w_3 − m14 − m24 + m13 + m23 ≥ 0.

- **Case a+b ≤ c+d and c ≥ a+b.** K = [(a+b) − min(a+b,d)] + [a − min(a,d)] + [b − min(b,d)] ≥ 0. Equality holds iff d ≥ a+b.
- **Case a+b ≤ c+d and c < a+b.** Bounding the d-terms by a+b, a and b gives K ≥ 6(a+b−c) + [min(a,c) + min(b,c) − c] > 0. The bracket is ≥ 0 because a+b > c.
- **Case a+b > c+d.** Here T = c+d, w_4 = c, w_3 = d. Using min(x, c+d) ≤ min(x,c) + d for x = a, b, and m14, m24 ≤ d, K ≥ 2c + 4d ≥ 0. ∎

**Sharp witnesses (ratio exactly 5/6):**

| Profile | Coalition | v(S) | φ(S) |
|---|---|---|---|
| (2,1,1,1) | {2,3} | 1 | 1/4 + 7/12 = 5/6 |
| (0,1,1,1) | {2,3} | 1 | 2/3 + 1/6 = 5/6 |
| (1,1,2,2) | {1,2,3} | 2 | 2 − 1/3 = 5/3 |

The candidate inequality is therefore a theorem on this domain, not a grid artefact, and no counterexample exists.

## Theorem 2: φ_i ≥ H_i/2, with 1/2 sharp

**Core benchmark.** The original core is nonempty: if a+b ≤ c+d then (a,b,0,0) is in it, and symmetrically otherwise. For any core point x, x_i = T − x(N\i) ≤ T − w_i =: M_i, so H_i ≤ M_i.

This bound can be strict. At (2,1,1,1), H_1 = 0 < M_1 = 1, consistent with the calibration file's core (0,0,1,1). I did not derive a closed form for H_i; the proof needs only the upper bound.

**Proof.** Let f(z) = min(a+b, z) − min(b, z) = clamp(z−b, 0, a). Then M_1 = f(c+d), and the bracket in φ_1 is

B = min(a,c) + min(a,d) + min(a,c+d) + f(c) + f(d).

- f is nondecreasing, 1-Lipschitz and takes values in [0,a], so f(c+d) − f(d) ≤ min(a,c) and f(c+d) − f(c) ≤ min(a,d).
- Also min(a, c+d) ≥ f(c+d).
- Hence B ≥ 3·M_1, and φ_1 = B/12 + M_1/4 ≥ M_1/2 ≥ H_1/2. ∎

**Sharpness.** At (1,1,1,1), φ_1 = 1/2 and H_1 = 1, since (1,1,0,0) is in the core. The same ratio holds at (t,1,1,1) for 0 < t ≤ 1, where φ_1 = t/2 and H_1 = t via the core point (t,1,0,0).

**Zero and tie cases.** If T = 0, every v(S) = 0, φ = 0, the core is {0} and H = 0. No strictness or tie-breaking assumption is used anywhere; every step is a weak inequality between minima.

## Theorem 3: own-capacity monotonicity

For each S not containing i, v(S∪i) is nondecreasing in c_i and v(S) does not depend on c_i. So every marginal contribution, and hence φ_i, is nondecreasing in c_i on all real profiles. It is also continuous in c_i.

## Consequence for the contract (my inference, not independently reviewed)

The rule y = (6/5)·φ satisfies every listed requirement:

- it is deterministic and nonnegative;
- it covers all coalitions at all profiles (Theorem 1);
- it is nondecreasing in own capacity (Theorem 3);
- y_i ≥ (3/5)·H_i ≥ H_i/3 (Theorem 2);
- it is zero at T = 0;
- its total is (6/5)·T.

That gives β = 1/5 < 1/2 on the whole domain. No smaller multiple of φ works, because of the sharp witness. If the proofs survive review, the remaining gap is [1/8, 1/5].

On the five calibration profiles, y = (3/5, 3/5, 3/5, 3/5) at c0 and (7/10, 3/10, 7/10, 7/10) at (2,1,1,1). The subsidy ratio there is 1/5 against the finite optimum of 1/8, and the raised player's payment goes from 3/5 to 7/10.

## Limitations and open points

- Everything is hand-derived. The numeric spot checks above are single profiles, i.e. finite evidence only.
- There is no exact closed form for H_i.
- The fairness floor has slack (3/5 against the required 1/3), which suggests non-Shapley or blended rules might get below 1/5. I did not explore this.
- I make no novelty or priority claim. Shapley monotonicity and the marginal-contribution bound on core payoffs are standard facts.
- The results cover the four-owner {1,2}|{3,4} domain only.
