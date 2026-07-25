Online Resource 1
=================

Article:  Coalitional monotonicity and the core: minimal impossibility, an
          exact-games escape, and the boundary of surplus-distributor
          solutions
Journal:  International Journal of Game Theory (submitted)
Author:   Maxwell Flanagan [Affiliation, City, Country - to be completed]
Contact:  maxwell.flanagan@gmail.com

Caption:  Machine-readable exact-rational certificates for all computational
          theorems of the article (game tables, per-coalition exactness
          witnesses, satisfaction/excess tables, balancing weights for every
          cumulative level set, Farkas multipliers, and segment samples),
          together with a self-contained verifier and an environment
          manifest.

Contents:
  certificates.json   All certificate data (exact rationals as strings).
  verify_paper.py     Standalone verifier; requires only Python >= 3.8
                      standard library. Run:  python3 verify_paper.py
  environment.txt     Environment used for the original computations.

The verifier recomputes every satisfaction and excess table from scratch,
checks stored level sets against recomputed ones, validates all balancing
weights and Farkas multipliers by pure rational arithmetic, and confirms
the witness comparisons stated in the article. Expected output ends with
"ALL CHECKS PASSED".
