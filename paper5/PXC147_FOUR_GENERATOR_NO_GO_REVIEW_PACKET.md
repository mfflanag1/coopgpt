# Hostile review packet — PXC147 four-generator two-block no-go

Review target: branch `codex/hmr-four-generator-no-go`, based on PXC146
checkpoint `d57b6a22bae7d3f6ca747a1b38cdc9e9a743cec9`.

## Claim and scope

PXC147 classifies one explicitly defined family, not all exact games.  It is
the ordered-transfer four-generator extension obtained by replacing the two
`e` roles of `H_m` by an `r`-player symmetric loser block while retaining the
PXC146 Lmin-pinning incidence rows.  For integers `m>=1`, `r>=3`, put

```text
h=2m/(r-1), p=rh+1, q=h+1, s=m+1,
T=m+2rh+r+2, p/2<=t<=p.
```

The four displayed generators and both selector formulas are in
`paper5/divergence.tex` at PXC147.  The theorem proves:

- exactness and singleton normalization;
- the displayed `X` is Lmin for every parameter;
- a closed Lmax formula in each chamber `h<=1` and `h>=1`;
- the overlap formulas in PXC147e;
- `rho<8/5` throughout the `r>=3` class;
- along `m/r->a`, `rho->8a/(5a+1)`;
- the closest one-row replacement `c(E\i)g` still forces `X_c<=3m`.
- PXC148 exhausts all 15 one-own-loser symmetric row types in the retained
  dual form; only `be_i`, `be_i g`, and `bcde_i g` survive, and the
  two new types force `(r-1)X_b\le m` and a linear upper bound on `X_c`.

Consequently this incidence-faithful class cannot beat the balanced
two-generator benchmark infinitely often.  No upper bound for arbitrary
exact games and no novelty claim is made.

## Load-bearing symbolic steps to audit

1. Do the four retained Lmin row values and efficiency really force
   `(r-1)h=2m` and `X_c=m+rh`, or is a parameter orbit omitted?
2. In the Lmin proof, check both incidence identities coordinate by
   coordinate, especially the distinction between the number of E players
   in a coalition and the coefficient on each individual E coordinate.
3. In the `h<=1` chamber, check nonnegativity of all three convex weights,
   the `cdg` first-ceiling argument, and the second-stage deduction from the
   complementary pair plus `bcdE`.
4. In the `h>=1` chamber, check `p/2>=q,s`, all claimed lower-envelope row
   values, and the efficiency step that forces zero on `U union {b}`.
5. Check the chamber boundary `h=1`, every weak inequality, and the full
   transfer interval including `t=p/2` and `t=p`.
6. Recompute the overlap in both chambers and the extended-ray limits
   `m/r->0`, finite positive `a`, and `m/r->infinity`.
7. Hostilely assess the claim that the class is the *entire* retained-row
   ordered-transfer class; identify any different four-generator incidence
   decoration that still deserves the phrase “incidence-faithful.”
8. Check PXC147h and the precise statement about why merely adding a fifth
   lower-envelope point cannot undo an existing B-generated undercut.
9. Independently solve the seven PXC148 load equations, audit the
   nonnegativity quantifier, and check whether its retained-row dual form
   omits a comparably natural one-row mechanism.

## Reproduction

From the repository root, with the pinned review Python:

```bash
python3 coopgames/verifiers/divergence/verify_pxc147_hmr_four_generator_no_go.py \
  --output /tmp/pxc147-primary.json
cmp coopgames/verifiers/divergence/pxc147_hmr_four_generator_no_go.json \
  /tmp/pxc147-primary.json

python3 coopgames/verifiers/divergence/verify_pxc147_hmr_four_generator_no_go_independent.py \
  --output /tmp/pxc147-independent.json
cmp coopgames/verifiers/divergence/pxc147_hmr_four_generator_no_go_independent.json \
  /tmp/pxc147-independent.json

python3 coopgames/verifiers/divergence/verify_pxc148_one_row_escape_no_go.py \
  --output /tmp/pxc148.json
cmp coopgames/verifiers/divergence/pxc148_one_row_escape_no_go.json \
  /tmp/pxc148.json
```

The primary artifact is a stdlib exact transcription audit of the
conventional proof.  The independent artifact uses its own Z3 role-orbit
core and staged-selector implementation on 25 calibrations spanning PXC146,
both new chambers, three transfer values, and a fail-open control below
`p/2`.  The finite replay is not the universal proof.

## Significance and novelty questions

Please separate correctness, significance, and novelty.

- Is the forced-scale phenomenon already standard under a name from exact
  games, Lorenz selections, balanced collections, or incidence geometry?
- Is classifying a natural extremal family and proving its asymptotic
  failure independently publishable, or only useful internal guidance?
- Does the two-chamber Lmax formula or transfer plateau have prior-art
  analogues?
- Is the proposed split-loser/cross-block successor genuinely the smallest
  live mechanism, or is there a simpler four-generator decoration not
  covered by PXC147?

## Present frontier

The positive breakthrough target remains open.  The next construction
experiment should split the B-type load across two complementary growing
loser subblocks and add a cross-block d-pinning row.  It must reproduce the
PXC146 `r=2` boundary and either yield `2-rho~C/n` with `C<8`, or produce a
second structural no-go.  PXC147--PXC148 should not be called a field-level
breakthrough before specialist correctness and prior-art review.
