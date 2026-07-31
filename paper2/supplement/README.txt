Online Resource 1
=================
Article:  Core stability does not imply egalitarian stability:
          a sharp six-player counterexample
Author:   Maxwell Flanagan [Affiliation - to be completed]
Contact:  maxwell.flanagan@gmail.com

This archive contains machine-readable exact-rational data for the reported
six-player perturbation, an equivalent alternate normalization retained as a
regression case, and ancillary five-player exact-game data from the discovery
campaign. Each six-player coalition table explicitly contains all 63
nonempty coalitions, including zero values.

Run from this directory:

    python3 verify_paper2.py
    python3 verify_stability.py

Both programs use only the Python >= 3.8 standard library and read
supplement_data.json from this directory (or its parent). A successful run
ends, respectively, with:

    ALL CHECKS PASSED.
    STABILITY CERTIFICATE PASSED.

verify_paper2.py reconstructs the coalition functions, recomputes the
procedural egalitarian claims and terminal admissible collections, checks the
main example's two-round trace, checks the two-point generator
representations, and verifies the fully-tight affine-line systems and exact
core parameter intervals.

verify_stability.py is an independent exact cross-check of the paper's hand
proof. For the reported game and the equivalent regression normalization it
constructs the 21 relevant hyperplanes in the five-dimensional efficiency
space, solves all C(21,5)=20,349 candidate bases with fractions, and
constructs an exact segment-core dominator for every outside-core imputation
vertex. It deterministically finds 230 distinct intersections, 104
imputations, two core endpoints, and 102 dominated outside-core vertices in
each normalization. No floating-point classification, external solver, or
checkpoint file is used.

Contents:

    README.txt
    supplement_data.json
    verify_paper2.py
    verify_stability.py
