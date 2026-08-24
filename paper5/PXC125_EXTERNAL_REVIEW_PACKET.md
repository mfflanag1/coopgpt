# Hostile external review packet — PXC125 common-demand localization

Date: 2026-08-23

Status: internal theorem candidate with primary and independently formulated
exact audits. No novelty claim. No cooperative-game specialist has reviewed
this result.

## Result to review

For `t>=1`, put `n=t+5` and consider the full natural affine
common-obstruction chamber

```text
0<A<B,
B+A/(t+1)<K0<B+2A/t,
M>max(K0,2A),
C=A+(t+1)B-tK0.
```

The exact lower-envelope construction uses the four rows

```text
rh>=2M,
rhj>=2M+2A,
rhaK>=2M+tK0,
rhbK>=2M+A+(t+1)B.
```

Its selectors are

```text
x=(M+A/2,M+A/2,A,B,A,B^t),
z=(M,M,0,C,2A,K0^t).
```

The fixed complete proper-row Lmin certificate is `{rhj,rhbK}`. The
coalition `rhaK` is tight at `z` but has coefficient zero in every normalized
extreme top cover. Every such cover lift has the same wrong Lmax selector,
so this is a PXC114 common-direction obstruction throughout the chamber.

Let `B_H` be the actual-top spectral bound and

```text
D_H=(n*T/floor(n^2/4)-B_H)_+.
```

PXC125 claims:

1. If `t>=2`, then `D_H=0`.
2. If `t=1` and `A>=B/3`, then `D_H=0`.
3. Hence positive demand forces `t=1` and `B>3A`.
4. In that remaining chamber the two predeclared disjoint rank rectangles
   `(B-A)` and `(min(B,C)-2A)` are positive and their sum is at least `D_H`.

Thus the narrow `B>3A` assumption in PXC122–PXC123 is not a restriction on
the positive-demand problem: it is forced whenever spectral closure fails.
The theorem resolves this entire affine obstruction chamber, not the full
PXC114 common branch.

## Human proof checkpoints

After removing the two top players, the residual spectra are

```text
x_R={A,A,B^(t+1)},
z_R={0,2A,C,K0^t}.
```

Threshold counting gives the opposite-pair residual exactly. For `t=1`,

```text
R_H=2A+min(A,C)+(min(B,2A,C)-A)_+.
```

For `t>=2`,

```text
R_H=(t+1)A+min(A,C)+(t-2)(B-A)
    +(min(B,2A)-A)_+ +(min(B,C)-A)_+.
```

The declared price is

```text
t=1:   P=(B-A)+(min(B,C)-2A)_+,
t>=2:  P=(B-A)+(B-2A)_+.
```

These are literal disjoint high–low rectangles: for `t=1`, pair the `K`
coordinate with `a` and, when nonempty, `b` with `j`; for `t>=2`, pair two
different `K` coordinates with `a,j`. Therefore `P<=O-B_H` without using the
complete rectangle identity.

The dimension cases are then elementary:

- `t>=3`: a coarse layer bound gives `2B_H-T>0`.
- `t=2`: split at `A<=B/2`; the blocker/core comparison
  `K0<B+A` is load-bearing and yields `12B_H-7T>0`.
- `t=1`: if `A>=B/3`, a short `C<=B`/`C>=B` split gives
  `3B_H-2T>0`. Otherwise `C>B-A>2A`, and the PXC123 two-rectangle inequality
  gives `P-D_H>0`.

## Exact artifacts

Primary audit:

```text
verifiers/divergence/verify_pxc125_common_demand_localization.py
verifiers/divergence/pxc125_common_demand_localization.json
```

It checks 240 exact-rational algebra points and recomputes four
lower-envelope games, including points outside the old `B>3A` chamber. For
each exact game it recomputes all coalition minima, both selectors, the tight
menus, the five extreme covers, singleton normalization, and every reduced
cover lift.

Independent audit:

```text
verifiers/divergence/verify_pxc125_common_demand_localization_independent.py
verifiers/divergence/pxc125_common_demand_localization_independent.json
```

It imports no project selector, cover, primary price, or PXC125 code. It
integrates the threshold counts directly on 1,536 rational points through
`t=64`. Its fail-open control drops the blocker comparison upper endpoint and
produces positive seven-player post-top demand, showing that hypothesis is
not cosmetic.

## Hostile questions

1. Does the four-row lower envelope have the displayed selectors throughout
   the whole chamber, including every possible relative order of `2A,C,K0`?
2. Are `{rhj,rhbK}` the only proper x-tight rows and uniquely complete there?
3. Is the eight-row z-tight menu parameter-independent, and do its cover
   equations really leave exactly the five stated extreme supports?
4. Does every cover lift share the displayed reduced Lmax even when `2A`
   changes position among later z strata?
5. Are the two residual layer formulas correct at all equality boundaries?
6. Are the declared rectangles genuinely disjoint and therefore a
   predeclared subpacking of label currency?
7. Is the `t=2` proof valid under only the displayed blocker/core comparison,
   rather than silently using `B>3A`?
8. Does `D_H>0 => t=1 and B>3A` follow with strict quantifiers exactly as
   stated?
9. Does the theorem materially advance the common-branch program, or is it
   best described only as maximal closure of one incidence chamber?
10. Is an equivalent demand-localization theorem known in exact-game,
    Lorenz-core, rearrangement, or semi-balanced-system terminology?

## Required verdict

Please report critical, major, minor, and presentational findings separately;
give an explicit theorem verdict; and distinguish correctness, significance,
and novelty. Treat the JSON outputs as regression evidence, not proof.
