# Sharp asymptotic separation of opposing egalitarian core selections

This focused review package proves the exact first-order deficit constant
for the distance between two full core selections in singleton-normalized
exact TU games:

\[
\lim_{n\to\infty}n(2-s_n)=2,
\qquad 2-s_n=2/n+O(\log n/n^2).
\]

`Lmin` maximizes increasingly sorted individual payoffs. `Lmax` here
**minimizes** decreasingly sorted individual payoffs. The distance is
`||Lmin-Lmax||_1/v(N)`, and `s_n` is its supremum over the stated games.

The argument combines a compact-convex overlap lemma with an explicit
Fibonacci construction whose **entire core** is a segment. Both selectors
are unique at their first optimization stages. It works for every
sufficiently large player count. The manuscript contains every mathematical
step needed for the theorem; it does not rely on the historical finite-player
censuses or a claim that the supremum is attained.

## Read the package

- [manuscript.tex](manuscript.tex): self-contained paper source; author Maxwell Flanagan.
- [CLAIMS_AND_SOURCES.md](CLAIMS_AND_SOURCES.md): claim-level evidence, primary literature, and bounded search record.
- [REVIEW_REQUEST.md](REVIEW_REQUEST.md): precise questions for a specialist reviewer.
- [PROVENANCE.json](PROVENANCE.json): source revision, file hashes, changes, and verification provenance.
- [verification/run_checks.py](verification/run_checks.py): portable exact verifier.

This package is an internally audited conventional theorem candidate for
specialist review. It is not a claim of human review, established novelty,
journal acceptance, or formal proof-assistant verification. No external assessment has been received.

## One verification command

With Python and the dependency in `requirements.txt` installed, run from the
package root:

```sh
python verification/run_checks.py
```

The command exits nonzero on any failed check, solver timeout, UNKNOWN,
infeasibility, or unexpected non-rational optimum. It writes
`verification/results/verification.json`, first replacing any previous
success with `RUNNING` and recording `FAIL` if an exception occurs. It has no imports from the source
repository and no absolute repository paths. An alternative output path can
be supplied with `--output`.

For a clean environment, setup is:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verification/run_checks.py
```

The pinned and freshly tested runtime is Python 3.13.5 with
`z3-solver==5.1.0.0`. The mathematical checks use rational arithmetic and
explicit exceptions rather than removable assertions. A fresh `python -O`
run is recorded alongside the ordinary run.

The fast harness control `python verification/check_failure_record.py`
injects an error after the initial status transition and verifies that an
old successful record cannot survive as the result, normally or under `-O`.

## What verification establishes

The five complete raw-coalition cases are `(m,r)=(2,3),(2,4),(3,4),(3,5),
(4,5)`, with 8, 9, 11, 12, and 14 players. The verifier excludes off-segment
core points, computes both first-stage optima, proves the predicted optimal
faces are singletons, and checks feasibility and the exact distance formula.
The reverse segment containment follows from checked generator feasibility
and convexity. A perturbed unit-sum construction must produce an explicitly
verified off-segment core point. Arithmetic checks cover `m=2..64` and nine
large-player parameter choices, including jumps of `ceil(log2 n)`.

These are finite corroborations of the manuscript proof. They do not turn
the theorem into an exhaustive computational proof over all exact games.
The code does not claim to compute exact finite-player `s_n`, verify
unrelated historical results, or establish novelty.

## Scope of this consolidation

The package retains the generic overlap lemma, segment-realization lemma,
Fibonacci family, all-player-count squeeze, integer representation bound,
and their focused finite checks. The separate three-generator construction,
old conjectural constants, finite five/six-player results, and the large PXC
research history are not needed and are omitted. Their omission is a scope
choice, not a retraction of a construction that was separately audited.

Build the paper with `bash build.sh`; the PDF is
`output/pdf/manuscript.pdf`. The enclosing release records PDF inspection
and clean-archive replay in `BUILD_AND_REPLAY.json`. `SHA256SUMS` identifies
the files supplied in this package.
