# Hostile review packet: unrestricted PXC91c minimum dimension

Checkpoint date: 2026-08-21. The claim under review is PXC100 in
`paper5/divergence.tex`: within the literal PXC97 domain, the global minimum
failure dimension is exactly six. This is a computer-assisted theorem, not a
claimed short human classification.

## Exact statement and dependency map

An instance is `(v,x,z,Cx)` with an exact singleton-normalized game,
`x=Lmin(v)!=Lmax(v)=z`, exactly two Lmax-top players, and any fixed collection
`Cx` of original x-tight proper rows whose retained polytope has Lmin `x`.
The strong formulation is universal over every such fixed `Cx`; the weak
formulation may choose `Cx` after the game is known.

The proof has four independently inspectable layers:

1. The existing through-four coincidence theorem makes `n<=4` vacuous.
2. At `n=5`, the one-coalition ceiling theorem gives `M=nu`, and anchor
   localization forces the two-player top pair `{r,h}` to be tight. Hence
   `{rh}` with weight `1/2`, ambient load zero, and top coefficients
   `(1/2,1/2)` is always a qualifying extreme cover.
3. PXC99 reduces failure of this pair lift to one of four exact staged-polar
   failures on the remaining three coordinates. Each LRA engine combines the
   complete 280-inequality five-player exact cone, exact staged Farkas
   identities for both selectors, an arbitrary Boolean-selected complete
   `Cx`, and the normalized bad direction. Two separate encodings return
   UNSAT on all 3,840 exhaustive stratum cells, with zero SAT/unknown/error.
4. PXC98 is an exact singleton-normalized `n=6` game for which the unique
   complete `Cx` and both qualifying extreme covers change Lmax. Two
   independent rational implementations replay it. Therefore both strong and
   weak formulations first fail at six.

## Five-player finite theorem coverage

The exhaustive cell product is:

```text
weak x orders after sorting x increasingly    16 compositions
two-player z top                              10 choices
orders of the three z outsiders                6 choices
tie patterns of the z outsiders                4 compositions
total                                  16*10*6*4 = 3,840
```

Sorting x is without loss by a global player relabelling.  The driver then
enumerates every location of the z-top pair and every ordered/tied pattern of
the other players; ties cause duplication, never omission.  A second cell
driver uses normalized nonnegative-incidence identities rather than the raw
PXC92b polar equations.  In both encodings, coefficients on already pinned
strata are free and active zero-coordinate normals are present.

The primary query includes:

- `v(empty)=0`, `v(N)=1`, `v({i})=0`, nonnegativity, and all 280 exact-cone
  inequalities;
- x and z in the core, with exact efficiency and complete weak-order/tie
  patterns;
- `x!=z`, exactly two Lmax-top players, and tightness of their pair;
- one Boolean for every nonempty proper coalition row, with selection
  implying x-tightness;
- every stage/player Lmin Farkas identity supported only on selected rows;
- every stage/player Lmax Farkas identity supported only on original z-tight
  rows;
- every applicable normalized PXC92b bad direction, including active
  nonnegativity when a z coordinate is zero.

Thus SAT would exhibit a bad fixed complete `Cx`; UNSAT over every stratum
cell is universal over fixed certificates. Other covers need not be exhausted
on the positive side because the canonical pair itself is faithful.  The
independent encoding is an algebraic replay, not an independent SMT solver.

## Exact reproduction

From the repository root:

```bash
python3 verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.py \
  --workers 4 --cell-timeout-ms 120000 \
  --output /tmp/unrestricted-pxc91c-n5-all-cells.json
cmp verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.json \
  /tmp/unrestricted-pxc91c-n5-all-cells.json

python3 verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells.py \
  --workers 4 \
  --cell-timeout-ms 120000 \
  --cell-driver verifiers/divergence/search_archive/verify_unrestricted_pxc91c_n5_cell_ni.py \
  --encoding-label independent-NI \
  --output /tmp/unrestricted-pxc91c-n5-all-cells-ni.json
cmp verifiers/divergence/search_archive/unrestricted_pxc91c_n5_all_cells_ni.json \
  /tmp/unrestricted-pxc91c-n5-all-cells-ni.json
```

Each artifact pins its census and cell-driver hashes, the exact-cone source,
the 3,840 cell-key digest, solver version, and verdict counts. In a representative
strict cell, deleting the exact cone or singleton normalization changes
UNSAT to SAT and records an exact rational model during the cell replay.

For the six-player negative half, run the three commands in
`paper5/UNRESTRICTED_PXC91C_N6_REVIEW_PACKET.md`.

## Known limitations

- A superseded 736-orbit prototype omitted active nonnegativity normals from
  its selector Farkas layer.  Its UNSAT output is not used here.  The promoted
  3,840-cell drivers include those normals in both selector encodings.
- The five-player closure is computer-assisted. The desirable remaining
  strengthening is a short human proof of the three-coordinate common-polar
  implication.
- The LRA engine conditions on top-pair tightness; the conventional
  five-player one-coalition and anchor theorems supply that condition.
- The independent NI checker changes the selector-certificate algebra but
  uses the same Z3 exact-LRA backend; solver diversity remains desirable.
- The result is scoped to exactly two Lmax-top players and the literal PXC97
  definition. It is not a theorem about arbitrary top-stratum cardinality.
- Solver UNSAT cores are audit conveniences and are not presented as a new
  conceptual proof.

## Questions for the external reviewer

1. Does the five-player one-coalition/anchor reduction really force `{r,h}`
   tight under exactly the stated hypotheses?
2. Do the staged Farkas signs and fixed-`Cx` Boolean quantifiers encode every
   complete certificate rather than a preferred basic certificate?
3. Do the four bad-direction normalizations cover every later residual Lmax
   stratum, including tied and zero-coordinate boundaries?
4. Is the 280-row cone being used in the correct inequality direction and as
   a complete description of normalized five-player exact games?
5. Does the 16-by-10-by-6-by-4 indexing cover every joint x/z weak-order
   pattern after one global relabelling, with ties causing only duplication?
6. Does PXC98 exhaust every qualifying extreme cover and every complete `Cx`,
   so that the weak existential-certificate formulation also fails at six?
7. Is the final claim stated as a computer-assisted minimum-dimension theorem
   without implying a dimension-free faithful-lift theorem?
