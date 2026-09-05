# Independent correctness audit: unrestricted asymptotic separation

Date: 2026-09-05. Reviewer lane: `/root/triples_construction`.

This is a fresh mathematical and code audit, not an inference from the old
PASS labels. The source repository was read only. Exact replays ran in this
scratch directory under Python 3.13.5, Z3 5.1.0, with `python -O`.

## Verdict

The central unrestricted theorem is mathematically sound on this audit:

\[
\lim_{n\to\infty} n(2-s_n)=2,
\qquad 2-s_n=2/n+O(\log n/n^2).
\]

Its proof genuinely concerns the **entire core** of singleton-normalized
exact TU games and the **full** opposing lexicographic selectors. The
Fibonacci construction does not substitute the generating segment for its
coalition closure without proof. The segment equality is proved using
complementary coalitions, and both selectors are unique already on their
first optimal faces.

The separate fixed-dimension chamber note is not established by its current
written proof. One older campaign note also contains a false intermediate
support-cardinality inequality. Neither is used in the central theorem.

| Result | Status in this audit | Material boundary |
|---|---|---|
| Generic compact-convex overlap bound `O >= T/(n-1)` | Conventional proof checked; sound | Requires nonnegativity, equal positive total, convexity, maximin/minimax optimality |
| Matrix realization of an entire core segment | Conventional proof checked; sound | Invertible zero-one matrix, positive inverse image of one, and `H >= 1` are essential hypotheses |
| Fibonacci exact TU family and selector formulas | Conventional proof checked; exact replays pass | This is an explicit family, not a classification of extremizers |
| Sharp all-n asymptotic coefficient two | Conventional proof checked; sound | Does not determine exact finite-n `s_n` or uniqueness of asymptotic extremizers |
| Three-generator extension of PXC151 | Conventional proof checked; exact replays pass | `m >= max(2,2k-2)` is material; an out-of-domain formula fails |
| PXC151 relation | Algebraic specialization verified | Historical 66-stage release suite was not rerun |
| PXC152 | Not independently identified in current source | No literal match under `coopgames`; the recovered generic bound cannot certify a lost release |
| Coalition-closure negative-control family | Conventional proof checked; exact replays pass | Its generating convex hull is not its full coalition core |
| Fixed-n rational selector chambers / attainment | Candidate proof incomplete as written | Do not cite current note as an established attainment or rationality theorem |
| Core-equivalent closure and `n+2` exactification | Conventional proof checked; sound | Preserves selectors but need not preserve the entire provisional core in the finite-generator version |
| Sparse-fidelity monotonicity and staged tangent criterion | Conventional arguments checked; sound | Tightness inheritance is one way; first-stage top-cover optimality does not imply full selector fidelity |
| Six-player PXC98 failure | Independent exact active-set replay passes | This verifies a six-player obstruction, not the five-player universal census |
| Five-player PXC100 universal claim | Not certified by this bounded audit | The complete 3840-cell encodings, cone catalog, and proof evidence need their own audit |

## Central proof audit

Primary manuscript:
`coopgames/paper5/asymptotic_constant_two/sharp_asymptotic_separation.tex`.

### 1. Universal overlap bound, lines 66–87

For a nonempty compact convex set in the nonnegative total-`T` simplex,
let `x` maximize the smallest coordinate and `z` minimize the largest.
If they differ, set `a=min x_i`, `M=max z_i`. Equal totals give `a<M`.
Some minimum coordinate `i` of `x` has `z_i<=a`, since otherwise a small
move toward `z` raises all minimum coordinates. Some maximum coordinate
`j` of `z` has `x_j>=M`, by the converse movement argument. The two indices
are different. Therefore

\[
O\ge z_i+M,\qquad
T\le z_i+(n-1)M\le(n-1)(z_i+M)\le(n-1)O.
\]

The middle inequality uses `z_i>=0` and `n>=2`. Zero coordinates cause no
problem. If `x=z`, `O=T`. This proof applies to arbitrary first-stage
optimizers; exactness and later lexicographic stages are not needed.

### 2. Entire-core segment realization, lines 89–125

Take an invertible `p` by `p` zero-one matrix `A` with
`d=A^{-1}1>0`. Let `H=r-sum d>=1` and

\[
U=(H,d;0^r),\quad V=(0^{p+1};1^r),\quad
v(S)=\min\{U(S),V(S)\}.
\]

Both generators have total `r` and satisfy every lower-envelope coalition
constraint. Every coalition is attained by one of them, so the game is exact.
Their disjoint supports give singleton normalization.

For each row-donor subset `D` and each receiver `e`, both generators give
`D union {e}` value one and its complement value `r-1`. Consequently **every
core point** satisfies `y(D)+y_e=1`. This makes all receiver coordinates
equal to `1-t`, then gives `A y_d=t1`, so `y_d=t d`; efficiency gives
`y_h=tH`. Nonnegativity forces `t` into `[0,1]`. Conversely the segment lies
in the core by convexity. Thus the entire core is exactly `[U,V]`.

Every column of an invertible matrix occurs in a row; positivity and
`Ad=1` then imply `d_i<=1`. With `alpha=min d_i`, the minimum and maximum
coordinates on the segment are respectively

\[
\min(t\alpha,1-t),\qquad \max(tH,1-t).
\]

Their unique optima occur at `1/(1+alpha)` and `1/(1+H)`. Uniqueness of
these first optimal faces establishes the full selectors without an
unproved later-stage continuation. Disjoint support gives the distance
formula in the manuscript.

### 3. Fibonacci specialization, lines 127–160

The `2m` unit-sum rows are the pairs `(A_i,B_i)`, the recurrence rows
`(A_{i+1},A_{i+2},B_i)`, and the two boundary rows
`(A_{m-1},B_m)`, `(A_1,A_2)`. The homogeneous system eliminates `B`, leaves
`A_i=A_{i+1}+A_{i+2}`, `A_{m-1}=A_m`, and `A_1+A_2=0`, and hence has only
the zero solution. The argument includes `m=2`, when recurrence rows are
absent. The inhomogeneous solution has total `m` and minimum `1/F_{m+1}`.
Therefore, for `m>=2,r>=m+1`,

\[
2-\rho=\frac{2}{F_{m+1}+1}+\frac{2}{r-m+1},
\qquad n=r+2m+1.
\]

No transfer from an arbitrary abstract segment is assumed.

### 4. All-n scaling, lines 162–175

For `n>=128`, let `L=ceil(log2 n)`, `m=4L`, and `r=n-8L-1`.
The condition `r>=m+1` is `n>=12L+2`. It holds at 128; for `L>=8`,
`n>=2^(L-1)+1>=12L+2`. The last elementary inequality starts at `L=8`
and is preserved as `L` grows. Also
`F_{2j+1}>=2^j`, so `F_{4L+1}>=n^2`. This gives the claimed squeeze

\[
\frac2{n-1}\le2-s_n\le\frac2{n-12L}+\frac2{n^2+1}.
\]

Subtracting `2/n` yields the stated `O(log n/n^2)` remainder. It is an
all-integer-`n` construction, not merely a subsequence. Integer scaling by
`F_{m+1}` preserves normalized separation. For the alternate least-`m`
choice, `n^2<=F_{m+1}<2n^2` eventually, so the claimed `O(n^3)` scaled total
and `O(log n)` bits per generator coordinate are correct. This is a compact
generator representation; an explicitly listed characteristic function still
has exponentially many coalition entries.

### 5. Three-generator proof and PXC151 relation

`THREE_GENERATOR_PROOF.md` was read literally and its coalition values,
coefficient identities, equality cases, and parameter signs were rederived.
Writing `A=km-k+1`, `B=q-1=A+m`, its core inequalities imply

\[
\delta=p-(m-1)t\ge0,\quad
H=At+(k-1)\delta,\quad L=Bt+k\delta,
\]
\[
y_e+L\le q,\quad y_c+\sum_Ey_e=rq-H,\quad
(A/B)L-H=((m-k+1)/B)\delta\ge0.
\]

These are valid on the stated domain. They force the asserted unique
floor-one point and the asserted unique minimum-ceiling point; the overlap
reduces to `q+r+1`. The parameter restriction also ensures that the
third-generator comparison for the `c,g,E\e` coalitions has the required
sign. Setting `k=1` reproduces the PXC151 vectors and formulas in
`divergence.tex`, including `q=2m+1`, `T=2mr+m+r+1`, and
`O=2m+r+2`. PXC151 remains correct as a construction; the inference that
its coefficient might be globally optimal has been superseded.

## Exact replay and code soundness

All three portable verifier scripts were copied without modification to
this scratch directory and executed with optimization enabled. They do not
rely on Python `assert` statements for their checks. All returned exit zero.
The regenerated three JSON files are byte-identical to the source artifacts;
`replay_manifest.json` records source/replay SHA-256 hashes and versions.

| Suite | Replayed scope | Result |
|---|---|---|
| `verify_fibonacci_segment.py` | `(m,r)=(2,3),(2,4),(3,4),(3,5),(4,5)`, `n=8..14`; every proper coalition; first-stage optima and uniqueness | All pass |
| Fibonacci arithmetic | `m=2..64`, six displayed all-n parameter choices | All pass; finite corroboration only |
| Fibonacci negative control | Perturb one unit-sum coordinate at `(2,3)` | A raw-core point outside the proposed segment is found |
| `verify_integer_family.py` | `(m,k,r)=(2,1,3),(2,2,3),(3,2,4),(4,3,3)`; four exclusion queries each | All 16 UNSAT |
| Three-generator negative control | `(3,3,3)` violates the theorem domain | Exact feasible point improves the proposed leximin allocation |
| `verify_closure.py` | 24 cases, `n=4..9`, including zero and chamber-boundary parameters | Both directions of core equivalence and every lexicographic stage pass |
| Closure negative control | `n=5,a=1/5`, outside the claimed chamber | The extrapolated selector formula fails as intended |

The coalition lists are reconstructed from the raw efficient generators,
not from the predicted segment equations. The Fibonacci segment check uses
UNSAT of raw-core membership plus failure of the segment equations.
Reverse containment follows separately from generator feasibility and
convexity. Candidate feasibility in the integer-family checks likewise
follows from explicitly checked generators and a convex combination, so the
UNSAT exclusions cannot pass vacuously on an empty claimed core.

The staged selector implementation checks which coordinates are fixed on
each optimal face by optimizing each candidate coordinate over that face.
It does not pin an arbitrary LP solution. Timeouts and UNKNOWN are rejected.
These are exact rational solver checks, not a proof-kernel verification of
the all-parameter theorem or independently checked proof objects.

## Defects and overclaim risks

### A. False support-cardinality step in the older campaign note

`SHARP_ASYMPTOTIC_GAP_PROGRAM.md`, lines 59–65, says
`O >= mu |supp(z)| >= mu T/M`, justified by
`min(x_i,z_i)>=mu` on the positive support of `z`. That pointwise claim is
false when `0<z_i<mu`.

It fails even for a verified family here: Fibonacci `m=2,r=4` has

\[
x=(4/3,(1/3)^8),\quad
z=(2/3,(1/6)^4,(2/3)^4),
\]

so `mu=1/3`, `supp(z)=N`, `n=9`, but `O=8/3<3=mu|supp(z)|`.

The weaker conclusion `O>=mu T/M` is valid and can replace the erroneous
step with this two-line proof:

\[
\min(x_i,z_i)\ge(\mu/M)z_i
\quad(0<\mu\le M,\ z_i\le M),
\qquad O\ge\mu T/M.
\]

The scalar-ratio obstruction in that note remains valid; the false
cardinality step does not invalidate the main asymptotic release, which
does not use it. The same note's stated live target
`c_*=3+2 sqrt(2)` is historical and now false as a global-optimality target.

### B. Candidate selector-chamber proof is incomplete

`SHARP_GAP_CHAMBER_REDUCTION.md` explicitly labels itself a candidate and
lists the right review obligations. At lines 52–60, however, it asserts
that primal/dual feasibility and equality of objectives are jointly linear
in the game and certificate variables. A dual objective contains products
of parameter-dependent right-hand sides with dual multipliers unless the
chosen dual-basis solution has first been eliminated and shown constant.
That missing step is repairable in some standard parametric-LP settings,
but has not been supplied here.

More substantially, "exactly these coordinates are forced" includes
non-forcing conditions. Showing a coordinate is not fixed requires a
strict improvement witness on the current optimal face. The prose does not
show how its finite disjunction yields closed weak-inequality polyhedra,
nor prove continuity/boundary compatibility of the fully staged selector.
Consequently the final invocation of compact rational cells and attained
LP maxima does not follow from the preceding written argument.

This audit supplies no counterexample to the chamber theorem. It records a
proof gap and treats rationality/attainment as unproved by this note. No
repair is needed for the asymptotic theorem because its definition uses a
supremum and its proof constructs a lower bound directly.

### C. PXC152 provenance and external claims

A literal search for `PXC152` under `coopgames` found no source occurrence
(excluding PDF and JSON in the text search). The manuscript's generic lemma
is independently sound, but this cannot reconstruct or validate a lost
release claim. No specialist prior-art or external correctness assessment
was performed in this audit. The manuscript already limits these claims
appropriately at lines 208–216.

## Bounded follow-up: exactification and sparse fidelity

### Core closure and finite exactification

The proofs in `CORE_CLOSURE_REDUCTION.md` are sound. For a compact nonempty
core `C=Core(u)`, define `cl_C(S)=min_{y in C} y(S)`. Since
`cl_C(S)>=u(S)` and every point of `C` satisfies all the closed inequalities,
`Core(cl_C)=C`; compactness supplies exactness. Singleton witnesses at zero
preserve singleton normalization.

For the finite-generator form, include full selectors `x,z` and one zero
singleton witness per player, and define their lower envelope `v_G`.
Then

\[
x,z\in Core(v_G)\subseteq C.
\]

An optimizer remains optimal in any subset that contains it, including for
the sorted lexicographic orders. Thus both selectors survive immediately.
The staged-certificate argument in the note is also valid, but is stronger
machinery than the conclusion needs. This preserves selector pairs using
at most `n+2` generators; it does **not** assert equality of the two cores,
fixed-n attainment, or an `n`-independent generator bound.

I inspected the Farkas-sign construction in
`verifiers/s6/core_closure_pipeline.py`. Its use of marker-implies-tightness
is logically appropriate: the markers select eligible certificate supports
and need not enumerate every tight row. This is not a certification of the
complete six-player census or every caller's configuration coverage.

### One-way abstraction and staged fidelity

PXC91b, `divergence.tex` near lines 6797–6806, is correct: for a completion
`z in P subseteq P_R`, coalition minima can increase, and a minimum already
equal to `z(Q)` remains equal because `z` stays feasible. This transfers
tightness and positive-singleton impossibility in the stated direction. It
does not transfer a recomputed selector or an inequality evaluated at that
changed selector. The surrounding prose correctly acknowledges this.

PXC92b near lines 6859–6889 is the proper exact criterion. At a proposed
selector, active coalition and zero-coordinate normals describe feasible
small directions. A direction that fixes earlier strata, weakly improves
the current stratum, and strictly improves one of its coordinates gives a
small lexicographic improvement. Conversely any better point yields such
a direction at the first stratum at which it improves. Thus all later
strata matter; a sparse top cover alone only supplies the first-stage
certificate. The auxiliary-row bound PXC92c follows from conic
Caratheodory in a space of dimension at most `n`, applied separately to
the `n-2` non-top coordinates. Its coarse `n(n-2)` count is safe.

### PXC98 six-player replay

Executed the standalone verifier
`verify_unrestricted_pxc91c_pxc98_independent.py` with `python -O`; it
imports no project game, LP, selector, or cover implementation. Its exact
Fraction active-set enumeration returned exit zero and produced
`pxc98_independent_replay.json` here. Its LP vertex enumeration and staged
pinning logic were read before running.

The full core has total 17 and defining rows
`v(012)=11,v(013)=11,v(04)=6,v(0145)=11`. Its selectors are

\[
x=(9/2,9/2,2,2,2,2),\qquad z=(4,4,3,3,2,1).
\]

All singleton minima are zero. The only complete retained Lmin row pool
is `{012,013}`; the positive extreme top covers have supports `{01}` and
`{012,013,0145}`. Each resulting lift retains `x` and changes the upper
selector to `(4,4,3,3,3/2,3/2)`. Therefore the six-player failure is real,
including the existential choice of complete Lmin certificate for this
game. This does not independently prove that dimension six is minimal:
the universal five-player claim uses a separate 3840-cell computation that
was outside this lane's scope.

## Files produced

- `UNRESTRICTED_ASYMPTOTIC_AUDIT.md`: this report.
- `replay_manifest.json`: exact versions and byte/hash comparisons.
- `closure_calibration.json`, `fibonacci_segment_calibration.json`,
  `integer_family_calibration.json`: freshly regenerated source suites.
- `pxc98_independent_replay.json`: freshly generated rational active-set audit.
- Three unchanged copied verifier scripts for reproducibility.

All files are under
`/private/tmp/coopgt-portfolio-review-20260905/asymptotic/`.
