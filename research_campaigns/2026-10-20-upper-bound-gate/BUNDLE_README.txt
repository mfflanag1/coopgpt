COOPGPT — 90-MINUTE UPPER-BOUND GATE, 20 OCTOBER 2026

Start with CAMPAIGN_REPORT.txt for the result and stopping decision.
CONTRACT.txt freezes the mathematical domain and acceptance gate.
CAMPAIGN.json records actual timing and disposition.
SOURCE_COMPARISONS.txt distinguishes inspected originals from unresolved priority.

REPLAY
From this directory, run:
  python3 replay_exact.py > replay-local.json
Use Python 3.10 or newer, with assertions enabled (do not use -O).
No network, solver installation, external repository, or third-party package is
needed for the exact replay. The exploratory optimizer scripts are retained for
provenance but are not part of this command and require NumPy/SciPy.

The replay checks 12 groups of rational finite evidence: scalar-price lifts,
min-production repairs, harmonic positive-defect diagnostics, frozen background,
balanced two-terminal contraction, single-terminal limitations, capped fractional
smoothing, selected lower certificates, price reselection, exact optimal-price
normalization, budget-adapted prices, and local null-incidence normalization.

WHAT A PASS MEANS
The recorded exact finite constraints, resource production witnesses, payments,
dual balances, and price identities pass their implemented checks. Symbolic
proofs supply continuous/unbounded quantifiers separately; this replay is not a
proof assistant. No improved unrestricted upper bound or historical novelty is
established. Internal native and opposite-model reviews are not specialist human
review. Review snapshots and their adjudication are retained in reviews/ and
root/VERIFICATION_LOG.txt.

The original coalition manuscript and review packet remain separate deliverables.
Input snapshots in inputs/ preserve provenance; they are not a standalone LaTeX
project. The new Word review draft is linked in CAMPAIGN_REPORT.txt, outside this
math bundle. The M100 application chat has its own reproduction bundle.

INTEGRITY
FINAL_MANIFEST.json hashes each bundled file other than the manifest itself.
The archive has one top-level directory. After extraction, verify hashes before
running any scripts if checking the archived state; replay may create bytecode
cache files. PORTABILITY_CHECK.json records a clean-directory standard-library
replay of the same mathematical inputs and scripts.
