# Sharp asymptotic gap campaign

Status date: 2026-08-30.  Campaign branch: `codex/sharp-asymptotic-gap`.
The PXC151 mathematical checkpoint is frozen at
`8d5947ff7ed80535bbcc0b7fa13d2e44bfcbe564`; this program does not alter it.

## 1. Immutable target and evidence boundary

For a singleton-normalized exact game on `n` players, write `T=v(N)`,
`x=Lmin(v)`, `z=Lmax(v)`,

```
O(x,z) = sum_i min(x_i,z_i),
rho(v) = 2 - 2 O(x,z)/T,
s_n = sup_v rho(v),
c_* = liminf_n n(2-s_n).
```

PXC151 conventionally proves an all-parameter family with
`c_* <= 3+2 sqrt(2)`.  Its exact selectors have also been reconstructed by a
standalone Z3 verifier.  External cooperative-game correctness and prior-art
review are still pending.  No matching upper bound and no global optimality
claim is currently proved.

Primary target: prove `c_* = 3+2 sqrt(2)`.  Adversarial target: construct a
genuine all-parameter family with a smaller coefficient, or a faster approach
to two.  A universal `O >= c T/(2n)` for any explicit absolute `c>0` is a
meaningful intermediate theorem.

## 2. Calibrations and hard no-go ledger

Every upper-bound mechanism must reproduce PXC151's exact identity

```
T = 2mr+m+r+1,  O = 2m+r+2,
n(2-rho) -> 2a+3+1/a  when m/r -> a,
```

and must tolerate the archived PXC115/PXC116 zero-Lmax witness.  Every new
construction must beat PXC151 at an exact finite calibration before symbolic
scaling work continues.

Do not reopen PXC138/PXC140 or the PXC147--PXC150 nested tight skeletons.
Null padding, direct sums, and bounded grids are not proof mechanisms.  A
route stops after one phase if its missing step is merely the unrestricted
overlap claim in new notation.

## 3. Three independent lanes

### Lane A: global dual coupling

Couple staged selector normal cones and singleton exactness witnesses.  The
artifact must be an explicit inequality whose hypotheses are separately
checkable and whose conclusion is `O >= cT/(2n)`.

First reduction (proved): if `mu=min_i x_i>0` and `M=max_i z_i`, then

```
O >= mu T/M.
```

Since `0<mu<=M`, `x_i>=mu`, and `0<=z_i<=M`, one has
`min(x_i,z_i)>=(mu/M) z_i` coordinatewise. Summing proves the bound.
The stronger support-cardinality step formerly printed here is false:
the Fibonacci segment with `m=2,r=4` has `mu=1/3`, full support of `z`,
and `O=8/3<3=mu |supp(z)|`. Therefore `M<=Cn mu` would imply the universal
gap `2-rho>=2/(Cn)`. Corrected in the portfolio audit of 2026-09-05.

This scalar route is globally false.  Take the direct sum of two normalized
two-player unanimity games of totals `epsilon` and `1`.  Its core is the
product of two line segments and both selectors are
`(epsilon/2,epsilon/2,1/2,1/2)`, so `mu=epsilon/2` and `M=1/2`; hence
`M/(n mu)=1/(4 epsilon)` is unbounded.  This example is a falsifier only,
not a construction route.  It shows that any viable coupling must be
stratified or component-local and cannot use only the first floor and first
ceiling.

An exact archive audit independently exposes the finite warning: PXC116 has
`n=6`, `mu=1/2`, `M=6`, hence `M/(n mu)=2`.  The discovery script
`verifiers/divergence/search_sharp_scale_bound.py` reproduces exact staged
selectors for additional lower-envelope controls; a null search is not
treated as proof.

Next live lemma A1: formulate a level-set or component-local replacement
whose charge is additive across exact direct sums and whose integral is
exactly `O`.  It must yield a nonzero charge on the large component in the
two-unanimity falsifier and recover `O=2m+r+2` on PXC151.

### Lane B: exact-cone reduction

Determine whether extremizing selector separation can be reduced to a
controlled class of exact-cone faces or sparse lower envelopes.  Do not infer
this from fixed-`n` polyhedrality: selector chambers can create vertices that
are not extreme rays of the exact cone.

Next live lemma B1: on the normalized exact-game polytope, fix the complete
ordered partitions and tight bases of both staged selectors plus the signs
of `x_i-z_i`.  Derive the resulting rational polyhedral chamber and prove
that `rho` is linear there.  Then characterize which chamber vertices can be
non-extreme in the exact-game polytope.  A single explicit non-extreme strict
maximizer falsifies naive facet reduction and is a valid scoped no-go.

### Lane C: construction escape

Search only outside the PXC147--PXC151 nested block templates: cyclic menus,
growing role types, and nonlaminar fractional covers are admissible.

For any two-scale family with

```
T = A mr + o(mr),  O = Bm+Dr+o(m+r),  n=m+r+O(1),
```

direct minimization gives

```
C(a) = (2/A)(a+1)(Ba+D)/a,
min_a C(a) = (2/A)(sqrt(B)+sqrt(D))^2,
a_opt = sqrt(D/B).
```

Thus the construction quality index is
`kappa=A/(sqrt(B)+sqrt(D))^2`; beating PXC151 is exactly
`kappa > 2/(3+2sqrt(2))`.  This coefficient test is necessary, not
sufficient: exactness and both full staged selectors still require
conventional all-parameter proofs.

Next live experiment C1: design a cyclic/nonlaminar lower-envelope ansatz
whose symbolic row balances expose `(A,B,D)` before any large search.  Stop
unless one exact finite instance beats the best PXC151 value at the same `n`
under independent selector reconstruction.

Phase C0 (closed negative, 2026-08-30): one bounded unrestricted sparse
lower-envelope hill-climb at `n=10` (seed `rand10`, worker 41, 5,000 mutation
steps, common integer total 1,000, at most 12 generators) improved monotonically
to `rho=0.978` but did not approach the finite gate.  At `n=10`, PXC151 gives
`26/23`, the balanced construction gives `6/5`, and PXC146's `H_10` gives
`133/100`.  The run was discovery-only and its floating selector output is
not a theorem.  Because it missed even PXC151 by more than `0.15`, generic
payoff mutation is retired; C1 must begin from symbolic incidence balances
that improve `kappa`, not from another unrestricted hill-climb.

## 4. Pivot gates

1. Lane A gets one phase to produce a stratified inequality surviving the
   two-unanimity and PXC116 controls.  A restatement of `O>=cT/n` is failure.
2. Lane B gets one chamber derivation and one adversarial vertex test.  Mere
   fixed-dimensional enumeration is failure.
3. Lane C gets one symbolic coefficient system and exact finite calibration.
   Parameter tuning inside an old nested skeleton is failure.
4. Synthesize only after each lane exposes its load-bearing lemma or a precise
   falsifier.  Preserve every negative result with its exact scope.

## 5. Evidence ladder

- exploratory exact examples: discovery only;
- exhaustive bounded chamber/family audit: finite theorem with derived scope;
- conventional all-parameter argument plus independent reconstruction:
  internal theorem;
- external correctness and prior-art assessment: required before any
  field-level claim.
