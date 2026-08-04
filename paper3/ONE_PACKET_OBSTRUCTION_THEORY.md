# The one-packet obstruction theorem

## 1. Scope and prior-art boundary

Let `v` be a singleton-normalized exact game, let `phi=Lmin(v)`, and let a
strict payoff boundary split the players as

```text
N = L dot-union H,
phi_i < phi_j  for every i in L and j in H.
```

Write `s(A)=phi(A)-v(A)`.  The question is what incidence geometry is forced
when the richer suffix fails exact partition, `s(H)>0`.

The following ingredients are prior art and are not claimed here:

- property I and the transfer-blocking characterization of egalitarian core
  allocations;
- balanced and minimal balanced collections;
- exact-balanced and semi-balanced inequalities for exact games;
- the correspondence between indecomposable minimal semi-balanced systems
  and facets of the exact-game cone.
- the Studeny--Kratochvil correspondence that obtains purely minimal
  semi-balanced systems from minimal balanced systems on the full player set
  by complementing the exceptional coalition.

The candidate contribution is not that full-set correspondence, but the
selection theorem below.  Leximin
optimality first supplies a *simultaneous strict normal certificate*.  After
projection to the richer side, convexity then selects a *single* minimal
balanced packet with positive rooted defect.  Thus an arbitrary
exact-partition failure is not an unstructured mixture of tight coalitions.
It has one exterior-sacrifice packet or one internal balanced-transport
packet.  The proof is dimension-free.

## 2. A rigorous simultaneous-cover lemma

### Lemma 1 (nested normal certificate)

Let `K` be a polytope in an efficient hyperplane and let `phi` be its leximin
point.  At a strict payoff boundary `N=L dot-union H`, the normal cone of `K`
at `phi` contains a vector `w` satisfying

```text
w_i>0  (i in L),             w_j=0  (j in H).       (N)
```

#### Proof

Let `T_K(phi)` be the tangent cone.  There is no `d in T_K(phi)` such that

```text
d_i>=0 for every i in L,     and d_i>0 for some i in L.          (A)
```

Indeed a sufficiently short segment `phi+t d` remains in `K`, preserves the
strict gap between `L` and `H`, and lexicographically improves the increasing
rearrangement at the first poorer payoff stratum on which `d` is nonzero.

The projection of the polyhedral cone `T_K(phi)` onto the `L` coordinates is
closed.  Its intersection with the nonnegative orthant is therefore `{0}`.
The strict polyhedral alternative (equivalently, strong separation from the
unit simplex in that orthant) supplies `w_L>0` with

```text
w_L dot d_L <= 0  for every d in T_K(phi).
```

Extending `w_L` by zero on `H` gives `(N)`, and the displayed inequality says
exactly that `w` belongs to the normal cone.  QED.

### Corollary 2 (simultaneous strict tight cover)

For a core polytope, there are nonnegative weights on proper coalitions tight
at `phi` whose incidence load is a common positive number on `H` and is
strictly smaller at every player in `L`.

#### Proof

The tangent cone of the core at `phi` is described by efficiency and the
inequalities

```text
d(T)>=0
```

for the proper `phi`-tight coalitions `T`.  The polar representation of its
normal cone writes the vector from Lemma 1 as

```text
w = mu 1_N - sum_T lambda_T 1_T,        lambda_T>=0.              (C)
```

Consequently the weighted tight-coalition load equals `mu` on `H` and
`mu-w_i<mu` at every `i in L`.  Since the load vector is nonnegative and
`w_L>0`, one has `mu>0`.  Coalitions disjoint from `H` may be deleted: this
leaves the richer load unchanged and only lowers poorer loads.  QED.

This proof closes a gap left by citing property I alone.  Pairwise transfer
blockers do not visibly imply one common weighting; the normal-cone argument
does.

## 3. Lifted minimal balanced packets

Normalize the common richer load in Corollary 2 to one and delete coalitions
disjoint from `H`.  For each supported tight coalition `T`, put

```text
R_T = T intersect H,          Q_T = T intersect L.
```

Projecting the normalized weights to the nonempty traces `R_T` gives an exact
cover of `H`.  Decompose it into vertices of the exact-cover polytope.  These
vertices are precisely the uniquely weighted minimal balanced collections on
`H`.

For every trace, distribute its vertex weight among the original coalitions
having that trace in the same conditional proportions as in the normalized
cover.  Expanding the resulting finite product of conditional distributions
expresses the original cover as a convex mixture of *pure lifted packets*.
Every packet `q` has richer load one.  Let

```text
r^q_i = its incidence load at poorer player i,
c_i   = average_q r^q_i < 1.
```

For a nonnegative poor-load vector `r`, define

```text
b(r)     = max_i r_i,
delta(r) = 1+(|L|-1)b(r)-sum_i r_i.                 (D)
```

The function `delta` is convex.  Moreover

```text
delta(c) >= 1-max_i c_i > 0.
```

Jensen's inequality therefore forces `delta(r^q)>0` for at least one lifted
minimal packet.

## 4. Main theorem

### Theorem 3 (one-packet rooted obstruction)

If `s(H)>0`, there exist

1. a minimal balanced collection `B` of nonempty subsets of `H`, with its
   unique normalized weights;
2. for each occurrence of a trace `R in B`, a `phi`-tight coalition `T` with
   `T intersect H=R`;
3. the resulting poorer load vector `r`, its maximum `b=max_i r_i`, and
   nonnegative completion weights

   ```text
   u_i=b-r_i;
   ```

such that

```text
delta=1+sum_i u_i-b>0                                             (E)
```

and the rooted incidence identity

```text
sum_T lambda_T 1_T
+ sum_i u_i 1_(H union {i})
- delta 1_H
= b 1_N.                                                         (R)
```

The root slack obeys the exact obstruction budget

```text
delta s(H) <= sum_i u_i s(H union {i}).                           (B)
```

At least one `u_i` is positive.  The trace packet has exactly one of two
forms:

- **exterior-sacrifice type:** `B={H}`;
- **internal-transport type:** every member of `B` is a proper subset of
  `H`.

The rooted identity uses at most `|H|` packet coalitions and `|L|` spokes,
and therefore at most `|N|` positive coalitions.

#### Proof

Choose a lifted packet with positive `delta` by Section 3.  Its richer load
is one and its poorer load is `r`.  A poorer coordinate in `(R)` receives
`r_i+u_i=b`.  A richer coordinate receives

```text
1+sum_i u_i-delta=b,
```

which proves the identity.

At a vertex of the exact-cover polytope, the positive trace-incidence columns
are linearly independent; otherwise a small signed kernel perturbation would
preserve feasibility in both directions.  Therefore the packet has at most
`|H|` traces.  A pure lift uses one tight coalition per trace, and at most
`|L|` completion weights are positive.  This proves the linear sparsity
bound.

Exactify `H`: choose `z in Core(v)` with `z(H)=v(H)`.  Evaluate `(R)` first
at `phi` and then at `z`.  Every packet coalition is tight at `phi` and
feasible at `z`, while every spoke is feasible at both points.  Subtracting
the two evaluations gives `(B)` directly.  This is the semi-balanced
inequality with exceptional coalition `H`, but no external inequality theorem
is needed.

If every `u_i` vanished, `(B)` would give `delta s(H)<=0`, contradicting
`delta>0` and `s(H)>0`.  Finally, a minimal balanced collection containing
`H` must equal `{H}`, because that singleton collection is already balanced.
Otherwise all of its traces are proper.  QED.

### Corollary 4 (support-minimal rooted atom)

The support of `(R)` contains a relation that is support-minimal within the
fixed sign cone having `H` as its negative root.  If this rooted circuit
retains a packet coalition with a non-full richer trace, its richer traces
contain the whole minimal balanced trace packet; otherwise it is a rooted
star assembled only from full-trace coalitions and spokes.

#### Proof

Choose an inclusion-minimal conformal subrelation of `(R)` that retains the
negative root.  Restriction of its incidence identity to `H` shows that its
retained non-full traces form a balanced subcollection of `B`.  Minimality of
`B` forces that subcollection to be all of `B`.  If no non-full trace remains,
every positive coalition has full richer trace, giving the stated rooted-star
branch.  QED.

This is a fixed-sign circuit statement.  It should not be conflated with the
stronger established notion of an indecomposable min-semi-balanced system,
whose minimality also compares relations with different exceptional sets.

The statement deliberately does not claim that one fixed finite minor occurs
in every failure.  Minimal balanced packets have many irreducible classes;
the four-co-singleton packet and the blown-up three-cycle packet already show
that a universal-minor formulation is false.

## 5. Consequences

### 5.1 A general structural theory, not a finite search

Every failed exact-partition boundary passes through the following canonical
chain:

```text
leximin normal cone
  -> simultaneous strict tight cover
  -> one lifted minimal balanced packet with delta>0
  -> rooted semi-balanced obstruction budget
  -> exterior-sacrifice or internal-transport atom.
```

The number of players never enters the reduction.  Player-count thresholds
arise only when exact singleton faces and strict payoff inequalities rule out
the smallest packets.

### 5.2 Recovery of the complete phase staircase

- If `|H|=1`, the only trace packet is `{H}`.  The sacrifice-budget argument
  shows that four poorer players are necessary and sufficient.
- If `|L|=2`, the internal branch must contain a proper hyperedge of size at
  least three.  Hence `|H|>=4`, sharply.
- With at least three poorer players and at least two richer players, the
  three-poorer lower-envelope family realizes every remaining pair.

Thus the one-packet theorem supplies the general mechanism beneath

```text
m_min(1)=4,
m_min(2)=m_min(3)=3,
m_min(h)=2 for h>=4.
```

### 5.3 Universal local slack ascent remains a separate scalar corollary

Applying the same rooted completion to the original strict cover rather than
to a selected packet gives

```text
delta(c)s(H) <= sum_i (b(c)-c_i)s(H union {i}).
```

Here `b(c)<1`, so `delta(c)>sum_i(b(c)-c_i)`.  Therefore some proper adjacent
coalition has strictly greater slack than `H`.  The selected packet supplies
the obstruction type; the un-decomposed cover supplies the universal strict
amplification factor.  Neither role should be attributed to the other.

## 6. Novelty and remaining gate

The incidence relation `(R)` is a semi-balanced system in the established
terminology of Studeny and Kratochvil, and its validity for exact games is
prior art.  Their complement-of-the-exceptional-set construction also gives a
general correspondence from purely minimal semi-balanced systems to minimal
balanced systems on `N`; that is prior art too.  Minimal balanced trace
packets are classical.  The proposed new result is their *forced selection on
the richer subset `H` by a leximin normal certificate* and the convex `delta`
argument eliminating mixtures.

This would materially broaden the phase theorem: it is a dimension-free
obstruction theory for every failed Lmin suffix.  It is still not safe to call
it a major field breakthrough until two external questions are answered:

1. does the egalitarian/property-I literature already contain the nested
   normal certificate in an equivalent simultaneous-cover form?
2. does the semi-balanced literature already project exceptional systems to
   minimal balanced trace packets in a way equivalent to Theorem 3?

The proof itself should be hostilely reviewed before incorporation into a
short submission.
