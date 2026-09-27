# A serial family with protection ratio tending to zero

The construction below is a parameterized family of complete strict three-sector pair-additive games with a nonempty core, positive first leximin level, and a target whose full leximin-to-ideal ratio equals `1/(3q+3)`. This tends to zero as q grows. The argument checks every mixed triple symbolically; the finite depth checks are corroboration, not the proof of the infinite claim. Priority is not assessed here.

## Definition for every integer q>=1

Each sector has `m=3q+1` players. Use matched-team labels L0 and, for each s=1,...,q, O_s,L_s,R_s. A player is specified by its sector and its team label. Concrete indices are `L0=0`, `O_s=3s-2`, `L_s=3s-1`, `R_s=3s`.

Every triple has value `A_ij+B_ik+C_jk`. All unspecified pair entries are zero. Set:

```text
A[O_s,O_s] = 2       B[O_s,O_s] = 2
C[L_s,L_s] = 1      (s=0,...,q)
C[R_s,R_s] = 1
A[O_s,R_s] = 2       B[O_s,L_s] = 2
C[R_s,L_s] = 1       C[L_(s-1),O_s] = 1
```

There are `8q+1` nonzero pair entries, all1 or2. The matching of each team's three players has output-team weight4 and leaf-team weight1. Its total is `T=6q+1`.

## Two whole-core witnesses

Let `tau=1/(3q+3)`. In sector order(A,B,C), define

```text
u(L_s) = (tau, 1-(3s+2)tau, (3s+1)tau),    0<=s<=q
u(R_s) = (tau, 1-2tau, tau),                 1<=s<=q
u(O_s) = (4-(3s-1)tau, tau, (3s-2)tau),     1<=s<=q.

y(L_s) = (0,0,1),      0<=s<=q
y(R_s) = (0,1,0),      1<=s<=q
y(O_s) = (3,0,1),      1<=s<=q.
```

Every u-coordinate is at least tau>0. Each vector has exactly the matching total on every matched team, hence total T. The point u is a first-floor witness; it is not asserted to be the complete leximin selector.

### Exhaustive symbolic check of all triples

An A-sector leaf has no incident A- or B-matrix entry. Its triple's value is therefore a C-matrix entry, which is0 or1. For the four positive C-entry types, the u sum of the B and C endpoints is respectively:

| C-entry type | Endpoint sum at u | Endpoint sum at y |
|---|---:|---:|
| L_s diagonal | 1-tau | 1 |
| R_s diagonal | 1-tau | 1 |
| R_s to L_s | 1+(3s-1)tau | 2 |
| L_(s-1) to O_s | 1-tau | 1 |

Thus a leaf's A payoff tau at u, or0 at y, covers every such triple. Zero C entries are automatic by nonnegativity.

For an A-sector output O_s, each incident A- or B-matrix entry is0 or2. If at most one of those two entries is positive, the entire triple value is at most3. This is covered because `u_A(O_s)>=3+4tau>3` and `y_A(O_s)=3`.

If both entries are positive, there are exactly four possibilities; no other mixed triple belongs to this case:

| B endpoint | C endpoint | Triple value | Payoff sum at u | Payoff sum at y |
|---|---|---:|---:|---:|
| O_s | O_s | 4 | 4 | 4 |
| O_s | L_s | 4 | 4+3tau | 4 |
| R_s | O_s | 4 | 5-3tau | 5 |
| R_s | L_s | 5 | 5 | 5 |

Here `tau<=1/6`, so `5-3tau>=4`. This exhausts every triple for every q. Both vectors are nonnegative whole covers of total T. The matching proves integral worth>=T; either cover bounds every integral matching by T. Thus the true integral worth is T, and both vectors belong to the entire core. Summing covers along coalition matchings also establishes every coalition inequality.

## A partial-matching certificate and the full leximin target

For each s, use the two triples

```text
(A_Os, B_Rs, C_Ls)       of weight5,
(A_L(s-1), B_L(s-1), C_Os) of weight1.
```

These `2q` triples are pairwise player-disjoint: they are an actual partial matching N of value `6q`. Its unmatched players are exactly

```text
C_L0,
A_Lq, B_Lq,
and A_Rs, B_Os, C_Rs for each1<=s<=q.
```

There are `3q+3` of them. Summing the N triple inequalities and subtracting from efficiency gives, for every core allocation p,

```text
p(C_L0) + p(A_Lq) + p(B_Lq)
 + sum_s[p(A_Rs)+p(B_Os)+p(C_Rs)] <= 1.       (*).
```

Thus a common payoff floor t is at most `1/(3q+3)=tau`. The vector u attains that floor and assigns tau to every player in(*). Therefore the first positive leximin level is exactly tau. On its entire first optimal face every term in(*) must equal tau. In particular the **complete ascending leximin selector** has `x(C_L0)=tau`, regardless of later stages.

The original matching team L0 has weight1, so nonnegativity gives `H(C_L0)<=1`. The whole-core witness y attains `y(C_L0)=1`. Hence the actual ideal is1 and

```text
x(C_L0)/H(C_L0) = 1/(3q+3) -> 0.
```

The construction has `n=9q+3` players. It establishes a vanishing family by growing player count. It does not rely on changing weights within a fixed player set.

## How the recurrence was obtained and what was rejected

The21-player1/9 example suggested viewing critical triples as a graph on matched teams. Its triangle output can transfer a budget to a new leaf. The corrected gate above realizes the exact one-step inequality

```text
A_L(s-1)+B_L(s-1)
 >= A_Ls+B_Ls+A_Rs+B_Os+C_Rs.
```

It follows from the weight5 triangle, the weight1 incoming triple, and the three matching equalities. Telescoping gives(*). Equivalently, the partial-matching argument proves it immediately and avoids introducing auxiliary equal-minimum variables.

An earlier algebraic draft, examined before any finite recurrence tests, used output diagonal AB1+AC2, cross AB2+AC2, and no BC crossedge. It was rejected because the mixed triple using output A, right-leaf B, and output C forced

```text
A_Rs + B_Os + C_Rs <= 0.
```

Thus its nonempty core could not have a positive global floor. The corrected weight4 output and BC crossedge avoid that saturation. This is a specific obstruction to the rejected gate, not a universal composition impossibility.

## Verification and coverage

`manifest.json` declares exactly one corrected recurrence and the first four positive integer depths q=1,2,3,4. The driver first replays the canonical21-player1/9 standalone verifier, then creates and checks only those four cases using Fraction arithmetic. Every pair-induced triple is checked at both saved witnesses, together with the integral matching, critical partial matching, and first-face/ideal certificate.

Run from this directory:

```sh
python3 -O family.py
```

The concrete results have12,21,30,39 players and ratios1/6,1/9,1/12,1/15. The general result follows from the symbolic proof above, not extrapolation from those instances. No random support search, LP scan, extra depth settings, or isolated-constant chase was run.
