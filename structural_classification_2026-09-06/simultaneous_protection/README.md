# Simultaneous core protection: resolved mathematical target

The proposed universal 1/K guarantee is false already for three sectors. The existing triangle family has **rho(M_q)=1/(2q+3)**, where rho optimizes the minimum fraction of individual whole-core maxima over every core allocation. Thus no positive bound depending only on K survives for arbitrary pair-additive markets with K≥3.

More precisely, for every fixed connected allowed sector graph G, the best size-independent simultaneous guarantee is **R(G)=1/K for trees and R(G)=0 for cyclic graphs**, conditional on a nonempty entire core. Equal sector sizes, nonnegative pair matrices (zeros permitted), and productive full teams only are essential scope assumptions.

- [Conventional proof](SIMULTANEOUS_PROTECTION.md): full-core simplex representation, all coordinate ideals, exact triangle optimum, matching dual certificate, and graph extension.
- [Exact certificate data](CERTIFICATES.json) and [verification report](VERIFICATION.json).
- [Free-only source audit](SOURCE_STATUS.md): credits the bilateral half-optimal core; priority remains unconfirmed.
- [Unsent specialist review brief](REVIEW_PACKET.md).
- [Proof and verification audit](AUDIT.md).

Run `bash build.sh` with standard Python 3 for rational cover, vertex, embedding and negative-control checks. Run `COOPGT_PYTHON=/absolute/path/to/python bash build.sh --smt` with the pinned optional requirement for raw-core/simplex equivalence, ideal upper bounds, and optimal-protection upper bounds. Both modes fail with a nonzero exit and a FAILED report on errors. The standard run intentionally contains no SMT queries.

The verified combined run checks 2,553,912 full-team covers, both directions of raw-core/simplex equivalence for q=1..4, the corresponding ideal and protection bounds (16 UNSAT queries total), and three rejected corrupt inputs. Triangle vertices and optimal witnesses are checked for q=1..8. Six longer-cycle/embedding cases check actual lifted ideal witnesses and the unit matching budget. These finite checks support, and do not replace, the all-parameter proof.

The Python file family.py and the files in dependencies/ are retained prior-project ingredients. certificates.py constructs the triangle matrices independently; verify.py checks the rational witnesses against every raw full-team inequality in the stated finite cases. All original-sector ideal lower witnesses used for embeddings are checked after lifting. The earlier mathematical result had a scoped model review; this new proof has not received an independent external reviewer. No separately paid review was invoked under the free-only constraint.
