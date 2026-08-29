# Dated novelty audit — PXC144--PXC146 (fixed-n divergence constants)

Date: 2026-08-26; updated 2026-08-28.  Scope: the explicit game `H_7`
(PXC144), the eight/nine-player games of PXC145, the all-parameter theorem
PXC146, and the negative statement that the fixed-n formula
`s(n)=2-8n/(n^2-(n mod 2))` is not the value of `s(n)` for `7<=n<=14`.

## What is claimed

1. Exact singleton-normalized lower-envelope games whose `Lmin`/`Lmax`
   distance exceeds the two-generator family value: `56/65>5/6` at `n=7`,
   `63/55>1` at `n=8`, and the nine-player value recorded in PXC145 (`>11/10`).
2. The consequence that the balanced `G(p,k)` family is not extremal for
   `7<=n<=14`, although it is extremal at `n=5` (as a value) and `n=6`
   (Theorem `s6`).  No claim is made for `n>=15`.
3. A search method (true-distance hill-climb plus a cell-frozen tangent
   linear program in the generator entries) that converts a first-crossing
   witness into a vertex of its combinatorial cell.
4. A conventional all-parameter proof for the four-generator family `H_m`,
   giving exact selectors and `rho(H_m)=14(5m-1)/(5(9m+4))` for every
   integer `m>=1`.  This family is not claimed asymptotically extremal.

No sharp value `s(n)` for `n>=7` is claimed.  No upper bound is claimed.

## Prior-art posture

- The selectors `Lmin`/`Lmax` and their axiomatics: Arin–Iñarra (2001),
  Arin–Kuipers–Vermeulen (2003, 2008), Dietzenbacher (2021) — see
  `S6_LITERATURE_NOVELTY_AUDIT.md`, whose primary-source list is reused
  unchanged.  None of these sources studies the normalized `L1` distance
  between the two selectors, a fixed-`n` supremum, or lower-envelope
  witnesses of that supremum.
- Algorithmic leximin/leximax core imputations (Vazirani and coauthors,
  flow/assignment/b-matching games, 2024–2025; see the citations already in
  the manuscript) concern computation on structured game classes, not the
  divergence quantity.
- Web search on 2026-08-25/26 (queries: leximin/leximax core selections
  exact games distance bound; exact games lower envelope egalitarian
  selections divergence counterexample) returned only the above lines of
  work and unrelated leximin-fairness papers; no published bound on
  `||Lmin-Lmax||_1/v(N)` was located.  This is a targeted search, not a
  definitive novelty opinion.
- Inside this manuscript: PXC141 (five-player literal-target failure) and
  PXC143 (first seven-player crossing, `5/6+1/9948`) are the direct
  predecessors; PXC144 improves PXC143 by `18173/646620` with a game of
  total `13` instead of `119376`, and PXC145 extends the failure to `n=8,9`,
  where the formula had never been tested against anything but the
  two-generator family.  PXC146 replaces the observed finite pattern by a
  symbolic all-parameter selector theorem; no specialist novelty opinion
  has yet been obtained for that family.

## Correctness posture

The explicit fixed-dimensional games are verified twice: an LP-free stdlib
replay of staged Farkas identities and a standalone Z3 selector/tangent
audit.  PXC146 is instead proved for all `m` by the displayed incidence
argument; a stdlib affine audit checks that algebra, while an independent
Z3 implementation calibrates `m=1..4`.  The finite calibration does not
carry the universal quantifier.

## Recommended external review questions

1. Re-derive the eight coalition values used by the `H_7` hand proof from
   the four generators and check each summation.
2. Confirm that the stage logic (bound + forcing from one identity per
   player, attainment by the displayed vector) is a complete proof of the
   lexicographic optimum in both directions.
3. Assess whether any equivalent explicit game or bound is known in the
   egalitarian-core / Lorenz-selection literature under other names.
4. For PXC146, check all eight parametric coalition values, the incidence
   sums at both selectors, and the positive convex-combination expression
   for Lmax feasibility before accepting the all-`m` quantifier.
