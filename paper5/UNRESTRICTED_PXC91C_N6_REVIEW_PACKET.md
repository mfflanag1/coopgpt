# Hostile review packet: unrestricted PXC91c failure at six

Checkpoint date: 2026-08-21. This packet concerns the negative PXC97--PXC98
half in `paper5/divergence.tex`. PXC100 subsequently proves the five-player
positive half and makes six globally minimal; its separate reviewer packet
is `paper5/UNRESTRICTED_PXC91C_MINIMUM_REVIEW_PACKET.md`.

## Claim under review

Let `N={0,1,2,3,4,5}`, total `17`, and let `v` be the lower envelope of the
nonnegative efficiency polytope cut out by

```text
y(012) >= 11
y(013) >= 11
y(04)  >= 6
y(0145)>= 11.
```

The claimed exact selectors are

```text
Lmin(v) = (9/2,9/2,2,2,2,2)
Lmax(v) = (4,4,3,3,2,1).
```

The only complete fixed Lmin certificate is `{012,013}`. The complete proper
Lmax-tight menu is `{01,012,013,04,0145}`. Its normalized positive-cover
polytope has exactly two extreme supports of size at most four:

```text
{01}:             lambda=1/2, eta=0,   alpha=(1/2,1/2)
{012,013,0145}:   lambda=(1/4,1/4,1/4), eta=1/4,
                  alpha=(1/2,1/2).
```

For either cover, the minimal lift with `{012,013}` preserves Lmin and
singleton normalization but changes Lmax to
`(4,4,3,3,3/2,3/2)`. The omitted row `04` is the indispensable later-stage
blocker. Therefore both the universal fixed-Cx and weaker existential-Cx
versions of unrestricted PXC91c fail at `n=6`.

## Exact reproduction

From the repository root:

```bash
python3 verifiers/divergence/search_archive/unrestricted_pxc91c_exact_search.py \
  --output /tmp/unrestricted-pxc91c-exact-search.json
cmp verifiers/divergence/search_archive/unrestricted_pxc91c_exact_search.json \
  /tmp/unrestricted-pxc91c-exact-search.json

python3 verifiers/divergence/verify_unrestricted_pxc91c_pxc98_independent.py \
  --output /tmp/unrestricted-pxc91c-pxc98-independent.json
cmp verifiers/divergence/unrestricted_pxc91c_pxc98_independent.json \
  /tmp/unrestricted-pxc91c-pxc98-independent.json

```

The second verifier imports no project LP, selector, cover, or game code and
implements its own rational active-set enumeration. The first verifier also
replays PXC88, PXC90, and the restricted PXC94--PXC96 result as controls.  A
separate six-generator counterexample is retained as a robustness control in
`search_archive/unrestricted_pxc91c_n6_generator_control.py`; it is not used
to verify PXC98.

## Human proof checkpoints

1. Exactness: the defining polytope is nonempty and compact; every coalition
   minimum is attained at a point in the polytope, which lies in `Core(v)`.
2. Singleton normalization: `(0,11,0,0,6,0)` zeros player 0, while
   `(17,0,0,0,0,0)` zeros any selected player 1--5.
3. Lmin: complements of `012` and `013` have sums at most 6. A common floor
   is therefore at most 2; equality pins players 2--5 at 2, after which
   players 0 and 1 equalize at 9/2.
4. Lmax: `v(01)=8` forces ceiling at least 4. Equality pins players 0,1 at
   4; rows `012,013` pin players 2,3 at 3; efficiency leaves `y4+y5=3`, and
   `04>=6` pins `(y4,y5)=(2,1)` through the later stages.
5. Cover exhaustion: with weights `(A,B,C,D,E)` on
   `(01,012,013,04,0145)`, outsider balance and normalization give
   `B=C=E=eta`, `D=0`, `2A+4eta=1`. The two displayed endpoints are the only
   extreme covers.
6. Certificate exhaustion: the x-tight proper menu is exactly `{012,013}`;
   direct recomputation of all four subsets makes only the full pair complete.

## Questions for the reviewer

- Is the lower-envelope exactness argument stated with the correct inclusion
  direction and attainment quantifier?
- Does the staged Lmax argument pin every payoff stratum, not merely the
  first ceiling?
- Does the one-dimensional cover polytope calculation exclude every extreme
  support allowed by PXC97a, including mixed eta-zero/positive-ambient
  representations?
- Is the certificate quantifier truly exhausted, including the weaker
  existential-Cx formulation?
- Are singleton rows or active nonnegativity normals missing from either
  tight-menu census? (All coordinates of x and z are positive.)
- Is the PXC98 conclusion kept logically separate from the later PXC100
  five-player exact-cone theorem that supplies global minimality?
