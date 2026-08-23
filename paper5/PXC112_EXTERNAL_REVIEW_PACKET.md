# Hostile external review packet — PXC112–PXC114

Status: candidate revision on branch `codex/pxc112-selector-obstruction-fan`,
based on frozen commit `929ffa0844b3e58a737fbe59bff9e98ea8c194f9`.
Do not treat verifier output as proof and do not infer novelty from the dated
negative literature search.

## Claims requiring review

### PXC112 — certificate dependence and canonical fiber

The total-17 lower-envelope game on players `(r,h,a,b,j,k)` is defined by

    rha>=11, rhb>=11, rj>=6, rhaj>=13, rhjk>=11.

It is claimed to be exact and singleton-normalized, with

    x=Lmin=(9/2,9/2,2,2,2,2)
    z=Lmax=(4,4,3,3,2,1).

The full proper x-tight menu is `{rha,rhb,rhaj}`.  Exactly three subsets are
complete Lmin certificates:

    C1={rha,rhb}
    C2={rhb,rhaj}
    C3={rha,rhb,rhaj}.

The full proper z-tight menu is `{rh,rha,rhb,rj,rhaj,rhjk}` and has exactly
two extreme normalized top covers:

    R0={rh}, lambda=1/2, eta=0
    R1={rha,rhb,rhjk}, lambda=(1/4,1/4,1/4), eta=1/4.

The six reduced Lmax selectors are claimed to be

| complete Cx | R0 | R1 |
|---|---|---|
| C1 | `(4,4,3,3,3/2,3/2)` | `(4,4,3,3,3/2,3/2)` |
| C2 | `(4,4,5/2,3,5/2,1)` | `z` |
| C3 | `z` | `z` |

Every lift retains Lmin and singleton normalization.  Thus no graph depending
only on `(v,x,z)` can encode sparse fidelity independently of complete-Cx
choice.

The proposed invariant replacement groups complete certificates whenever
their active tangent cones at both x and z agree.  The canonical object
is the finite family of PXC108 graphs over these tangent-cone classes.  It
claims equal candidate-selector fidelity verdicts, not equality of the
eventual altered Lmax allocation after fidelity fails.  This is a canonical
sufficient quotient for all staged tests; it is not
claimed to be the coarsest graph-preserving quotient.  In
extended `(v,x,z)` space, central hyperplanes for payoff order, zero
coordinates, active rows, and common tightness produce a finite rational fan;
after discarding faces with the wrong selectors, the certificate fiber and
all graph data are constant on each remaining face.  The claimed object is a
fan-supported stratification, not necessarily a selector-valid subfan.

Please check especially:

1. all eight Cx subsets and both covers, including redundant-row conventions;
2. whether the tangent-cone quotient is sufficient as claimed, and whether
   any strictly coarser canonical quotient is available;
3. whether “fan” is technically correct after restricting to selector-valid
   faces and whether projection should be called a stratification instead;
4. whether the counterexample refutes both natural certificate-independence
   quantifiers.

### PXC113 — strict-stratum rank potential

For strictly ordered residual payoffs and no active common-Cx normals, let
`K=ker(A^T)` for a positive balanced outsider incidence matrix.  If `p` is
the first coordinate not fixed by `K^perp`, the claimed polar identity is

    D(K)^* = K^perp + R_{<=0} e_p,

where `D(K)` is the lex-negative half of K and the polar uses nonnegative
pairing.  It implies that every asymmetric cover edge strictly raises
outsider incidence rank.  For partition covers, `P->Q` iff Q splits a block
of P; one-way edges are strict refinements and reciprocal edges are
incomparable partition pairs.

Please audit the polar sign, the designated first free coordinate, the use of
strict positivity in the balance representation, and the direction of the
partition-refinement order.

### PXC114 — dimension-free descent-set potential

For arbitrary payoff ties, active common-Cx inequalities, active
zero-coordinate normals, and eta-zero or positive-ambient covers, let `D_R`
be the full union of later-stage PXC92b descent directions for cover R in one
fixed tangent-cone certificate class.  The main new claim is

    R' not-> R  implies  D_R' subseteq D_R,

and therefore

    R->R' and R' not->R  implies  D_R' proper-subset D_R.

The proof is one line but load-bearing.  A missing reverse edge gives
`d(S)>=0` on every R row for every `d in D_R'`.  Dotting with the positive
normalized R-cover identity gives zero because efficiency and all earlier
top coordinates are fixed.  Every derivative therefore vanishes, so d also
satisfies the R tangent constraints; all other common, zero-normal, and stage
conditions are unchanged.

Consequences claimed:

1. asymmetric edges cannot form a directed cycle in any dimension;
2. every directed cycle contains a reciprocal pair, hence any cyclic graph
   has a two-cycle;
3. under universal extreme-cover failure, PXC107 improves to a
   dimension-free mechanism decomposition: either a common staged descent
   with an outside-union blocker, or—when the common intersection is
   empty—a reciprocal two-cover cycle;
4. PXC101 and PXC104–PXC106 are canonical prototypes of the two mechanisms,
   but no literal oriented-matroid-minor generation claim is made.

The original “every minimal failure is a primitive cycle” formulation is
therefore explicitly rejected: the common-direction PXC101/PXC98 branch has
no cover cycle.  PXC114c is the proposed exact replacement, and its cyclic
branch is always generated by a reciprocal pair.

Please attack whether `D_R` really uses identical non-cover constraints for
all R, whether earlier top coordinates always vanish in every included stage,
whether eta-zero covers are covered, and whether “deletion-minimal” is being
used more broadly than the displayed certificate permits.

## Exact artifacts and reproduction

Run the following commands from the repository's `coopgames/` directory.

Primary PXC112:

    python3 verifiers/divergence/verify_pxc112_certificate_dependence.py \
      --output /tmp/pxc112.json
    cmp /tmp/pxc112.json \
      verifiers/divergence/pxc112_certificate_dependence.json

Independent PXC112 active-set replay:

    python3 verifiers/divergence/verify_pxc112_certificate_dependence_independent.py \
      --output /tmp/pxc112-independent.json
    cmp /tmp/pxc112-independent.json \
      verifiers/divergence/pxc112_certificate_dependence_independent.json

Rank theorem audits:

    python3 verifiers/divergence/verify_pxc113_rank_potential_cycles.py \
      --output /tmp/pxc113.json
    cmp /tmp/pxc113.json \
      verifiers/divergence/pxc113_rank_potential_cycles.json

    python3 verifiers/divergence/verify_pxc113_rank_potential_cycles_independent.py \
      --output /tmp/pxc113-independent.json
    cmp /tmp/pxc113-independent.json \
      verifiers/divergence/pxc113_rank_potential_cycles_independent.json

Descent-set theorem audits:

    python3 verifiers/divergence/verify_pxc114_descent_set_potential.py \
      --output /tmp/pxc114.json
    cmp /tmp/pxc114.json \
      verifiers/divergence/pxc114_descent_set_potential.json

    python3 verifiers/divergence/verify_pxc114_descent_set_potential_independent.py \
      --output /tmp/pxc114-independent.json
    cmp /tmp/pxc114-independent.json \
      verifiers/divergence/pxc114_descent_set_potential_independent.json

The independent PXC112 verifier uses standalone Fraction active-set vertex
enumeration and imports no project LP, selector, cover, or game
implementation.  The independent PXC113/PXC114 audits use standalone Z3 and
separate rational/combinatorial checks.  These are audit aids, not substitutes
for the symbolic arguments.

Discovery-only artifacts, not proof evidence:

- `verifiers/divergence/search_archive/search_pxc112_cx_dependence.py`
- `verifiers/divergence/search_archive/search_pxc113_u5_asymmetric_cycles.py`
- `verifiers/divergence/search_archive/search_pxc114_active_cx_long_cycles.py`

## Prior-art boundary

The standard ingredients are not claimed as new:

- multiparametric LP critical-region degeneracy and lexicographic
  perturbation;
- oriented-matroid circuits, covectors, and program pivot graphs;
- exact covers, minimal exact balancedness, semi-balanced systems, and
  exact-cone facets;
- partition-star semi-balanced facets.

The searched literature did not reveal the specific graph whose vertices are
distinct positive top-cover circuits and whose edges are generated by staged
selector descents cutting another cover, nor the descent-set inclusion
potential above.  That is a dated negative search, not a novelty conclusion.
Please determine whether the PXC114 implication is a known theorem under
terms such as antitone feasible-direction systems, complementary-cone orders,
or circuit-covector elimination.

Closest sources currently cited:

- Jones, Kerrigan and Maciejowski (2007), lexicographic perturbation for
  multiparametric LP, DOI `10.1016/j.automatica.2007.03.008`;
- Björner, Las Vergnas, Sturmfels, White and Ziegler, *Oriented Matroids*,
  Chapter 10;
- Fukuda and Terlaky (1992), oriented-matroid complementarity and criss-cross
  pivots, DOI `10.15807/jorsj.35.45`;
- Studený and Kratochvíl (2022), exact-game cone facets, DOI
  `10.1007/s00186-022-00770-4`;
- Lohmann, Borm and Herings (2012), minimal exact balancedness, DOI
  `10.1016/j.mathsocsci.2012.01.002`;
- Reijnierse and Derks (1998), exact covers, DOI
  `10.1007/s001820050084`.

## Requested verdict

For each PXC112, PXC113, and PXC114, report critical, major, minor, and
presentational findings, then give separate verdicts on:

1. correctness;
2. exact quantifier coverage;
3. mathematical significance;
4. prior-art novelty;
5. whether the combined result meets the stated breakthrough criterion of a
   certificate-independent-after-quotient, dimension-free canonical minimal
   obstruction theorem.
