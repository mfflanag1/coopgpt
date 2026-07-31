Online Resource 1
=================
Article:  Core stability does not imply egalitarian stability:
          a sharp six-player counterexample
Author:   Maxwell Flanagan
Contact:  maxwell.flanagan@gmail.com

This archive contains machine-readable exact-rational data for the reported
six-player perturbation, an equivalent alternate normalization retained as a
regression case, and ancillary five-player exact-game data from the discovery
campaign. Each six-player coalition table explicitly contains all 63
nonempty coalitions, including zero values.

The alternate normalization is obtained from the reported witness by taking
old-player coordinates in the order (5,1,2,4,3,6) and then adding the vector
(0,-1,1,1,1,0). verify_paper2.py checks this transformation exactly.

Run from this directory:

    python3 verify_paper2.py
    python3 verify_stability.py
    python3 verify_additive_ray.py

All three programs use only the Python >= 3.8 standard library. The first two read
supplement_data.json from this directory (or its parent). A successful run
ends, respectively, with:

    ALL CHECKS PASSED.
    STABILITY CERTIFICATE PASSED.
    ADDITIVE RAY CERTIFICATE PASSED.

verify_paper2.py reconstructs the coalition functions, recomputes the
procedural egalitarian claims and terminal admissible collections, checks the
main example's two-round trace, checks the two-point generator
representations, and verifies the fully-tight affine-line systems and exact
core parameter intervals. It also checks monotonicity and superadditivity of
both six-player games and verifies the exact transformation to the alternate
normalization.

verify_stability.py is an independent exact cross-check of the paper's hand
proof. For the reported game and the equivalent regression normalization it
constructs the 21 relevant hyperplanes in the five-dimensional efficiency
space, solves all C(21,5)=20,349 candidate bases with fractions, and
constructs an exact segment-core dominator for every outside-core imputation
vertex. It deterministically finds 230 distinct intersections, 104
imputations, two core endpoints, and 102 dominated outside-core vertices in
each normalization. No floating-point classification, external solver, or
checkpoint file is used.

verify_additive_ray.py is a symbolic exact certificate for the continuous
family c(t)=(t,0,0,0,t,0), t>=0. It checks every affine maximization
inequality on the three claim chambers, subdivides at every internal
comparison crossing, and checks all breakpoints directly. It thereby verifies
the paper's piecewise-affine claim formulas and the phase transition from
egalitarian stability at t=0 to failure for every t>0.

Contents:

    README.txt
    supplement_data.json
    verify_paper2.py
    verify_stability.py
    verify_additive_ray.py
