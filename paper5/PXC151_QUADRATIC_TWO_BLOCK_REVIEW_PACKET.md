# Hostile review packet — PXC151 quadratic two-block family

Status: internally proved by a conventional incidence argument, checked by
an exact symbolic/transcription verifier, and independently replayed with a
standalone Z3 staged selector. No external cooperative-game specialist has
reviewed correctness or prior art. Do not call this a field-level
breakthrough before that review.

## Claim under review

For integers `m>=2,r>=3`, on roles `U^m,b,c,d,E^r,g`, define the exact game
as the lower envelope of

```text
X = (1^m; m-1,m(2r-1); 1,1^r,1),
B = (0^m; 0,0; 0,(2m+1)^r,m+1),
C = (0^m; m+1,r(2m+1); 0,0^r,0).
```

PXC151 claims

```text
T = 2mr+m+r+1,
Lmin = X,
lambda = (2m+1)/(m(2r+1)),
Lmax = lambda X+(1-lambda)B,
O = 2m+r+2,
rho = 2(2mr-m-1)/(2mr+m+r+1).
```

On `m=r=k`, the exact margin over the balanced `G` benchmark is
`2(k^2-4k-2)/((k+2)(2k^2+2k+1))`, positive exactly for integer `k>=5`.
Along `m/r->a`, `n(2-rho)->(a+1)(2a+1)/a`, whose minimum is
`3+2sqrt(2)<8` at `a=1/sqrt(2)`; the diagonal coefficient is 6.

The campaign defines the `r=2` boundary separately as the existing PXC146
family `H_m`. This is a discrete structural handover, not an algebraic
continuation of the four-generator formula.

## Conventional proof dependency map

1. A finite lower envelope of efficient allocations is exact because every
   coalition minimum is attained; generator zero sets prove singleton
   normalization.
2. The complement of `N\U` caps the Lmin floor at one and pins `U`.
3. The complement of `R3=bcdE` pins `g`.
4. `bdg`, every `beg`, and every `c(E\e)g`, combined with efficiency, give
   `b+d>=m`, `b+e>=m`, and `b+d+e<=m+1`; hence `b=m-1,d=e=1`.
5. The `c(E\e)g` row and efficiency then pin `c=m(2r-1)`.
6. The proposed Lmax is a positive convex combination of `X` and `B`.
7. Weight `1/(2r+1)` on `R3` and `U^m cE`, and distribute the same total
   weight over the `r` rows `c(E\e)g`. The excess loads are supported on
   `c,E` and sum to one; the objective equals the proposed ceiling.
8. Equality first fixes `g`, `sum_U`, and `b+d`. For every `u_j`, the rows
   `u_jbg` and `(U\u_j)cdE` give the opposite inequalities `u_j>=d` and
   `d>=u_j`, so the fixed block sum uniquely pins every remaining coordinate.
9. Direct coordinate comparison gives `O`, `rho`, the diagonal margin, and
   the ray coefficient.

## Authoritative paths

- Theorem and proof: `paper5/divergence.tex`, displays
  `(PXC151a)--(PXC151i)`.
- Primary verifier:
  `verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough.py`.
- Primary artifact:
  `verifiers/divergence/pxc151_quadratic_two_block_breakthrough.json`.
- Independent staged-selector verifier:
  `verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough_independent.py`.
- Independent artifact:
  `verifiers/divergence/pxc151_quadratic_two_block_breakthrough_independent.json`.
- Program status: `paper5/MECHANISM_PRICE_PROGRAM.md`, section 21.
- Protected statement: `paper5/PROTECTED_RESULTS_LEDGER.md`.

## Exact reproduction

Create the pinned review environment exactly as in `paper5/ENVIRONMENT.md`;
in particular it must contain SymPy and `z3-solver==5.0.0.0`. From the
parent directory containing `coopgames/`, with that interpreter stored in
`PAPER5_PYTHON`:

```bash
"${PAPER5_PYTHON}" coopgames/verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough.py \
  --output /tmp/pxc151-primary.json
cmp coopgames/verifiers/divergence/pxc151_quadratic_two_block_breakthrough.json \
  /tmp/pxc151-primary.json

"${PAPER5_PYTHON}" coopgames/verifiers/divergence/verify_pxc151_quadratic_two_block_breakthrough_independent.py \
  --output /tmp/pxc151-independent.json
cmp coopgames/verifiers/divergence/pxc151_quadratic_two_block_breakthrough_independent.json \
  /tmp/pxc151-independent.json

bash coopgames/paper5/verify_release.sh "${PAPER5_PYTHON}"
```

The primary verifier checks all symbolic identities and 110 exact rational
parameter cells. The independent verifier imports no project or primary
selector code; it regenerates every coalition-count orbit and recomputes
both staged selectors with fresh Z3 QF_LRA models.  This role reduction is
exact, rather than an assumed symmetry restriction: the core and objectives
are invariant under permutations within `U` and `E`, and permutation
averaging preserves every previously fixed lexicographic face. Moving one unit in `B`
from `g` to `d` undercuts the load-bearing `H` row and changes the
independently recomputed Lmin.

The `r=2` calibration is not inferred from the new three-generator formulas.
The full release gate separately replays the original PXC144 `H_7` verifier
and both PXC146 all-`m` verifiers; the PXC151 primary audit additionally
rechecks the closed PXC146 total, overlap, and ratio for `m=1,...,8`, including
the required `H_7,H_8,H_9,H_10` cases.

## Questions for hostile review

1. Is the lower-envelope exactness argument stated with the correct
   convention for exact games and singleton normalization?
2. Does the Lmin proof legitimately pass from the floor-one face to the
   three inequalities in `(PXC151c)`, with no hidden assumption that all
   displayed rows are simultaneously tight away from the selector?
3. Is the minimax dual normalized correctly when total weight is distributed
   uniformly over the `r` rows `c(E\e)g`?
4. Does equality in the dual and the four follow-up tight rows prove the
   full egalitarian min-max selector, including all later strata?
5. Are the overlap, diagonal benchmark margin, threshold `k>=5`, and
   asymptotic coefficient correct for both parity conventions?
6. Is defining `Hhat_{m,2}=H_m` and `Hhat_{m,r}=K_{m,r}` for `r>=3`
   appropriately described as a mechanism handover rather than a smooth
   extension?
7. Is an equivalent three-generator exact-game family, selector formula, or
   coefficient below 8 already known in the exact-game, Lorenz-solution,
   Dutta--Ray, egalitarian, or lexicographic-center literature?
8. Assuming correctness and novelty, does an infinite improvement over the
   balanced construction constitute a major construction theorem, or is a
   matching upper bound still needed for field-level significance?

The preliminary author-side source screen is recorded in
`paper5/PXC151_PRIOR_ART_AUDIT_20260830.md`. It is not a specialist novelty
opinion and should not anchor the reviewer's search.

Please report critical, major, minor, and presentational findings separately;
give a theorem-by-theorem verdict; and distinguish correctness, significance,
and novelty.
