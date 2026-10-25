COALITION WITHHOLDING — DATED SPECIALIST REVIEW PACKET
Prepared 25 October 2026; scientific manuscript version 24 October 2026.

Read specialist_brief.pdf, then manuscript.pdf and review/PRIORITY_MATRIX.txt.
The corresponding standalone .tex sources are included.
The manuscript source is byte-identical to the current canonical manuscript.
The brief has editorial changes to packet date, version-aware reading
instructions, ambiguous internal-baseline wording, and replay commands.
The priority matrix now requests P1-P5, has distinct section labels, and
repairs run-together tokens. No mathematical statement or proof was changed.

IMPORTANT FILE VERSION BOUNDARY
The canonical manuscript.pdf and specialist_brief.pdf are OLD 18 October
exports, omitting the 24 October graph section. They are NOT included here.
Fresh PDF export was explicitly authorized on 25 October. The current PDFs
are generated from the .tex sources in this packet. The current compilation,
export and visual checks are recorded in verification_20261025/.

The two .tex files are standalone. source/ and assemble.py retain editorial
provenance. Rebuilding manuscript.tex from these fragments reproduces its bytes.
The ordinary LaTeX package dependencies are declared in each source preamble.

EVIDENCE
Run python3 reproduce.py for six inherited exact suites; they use the Python
standard library and require assertions enabled. Run the two graph checkers
in evidence/graph separately, preferably from a copied scratch directory:
  python3 protected_leaf_exact_replay.py
  python3 leaf_recursion_exact_check.py
The graph checkers write adjacent JSON output. They are finite diagnostics,
not all-profile proofs. review/REPRODUCTION_NOTES.txt documents exact scopes.
The new dated replay outputs are included in verification_20261025/.

HISTORICAL REVIEW RECORDS
review/ and evidence/graph/ contain dated internal audits. Older page counts
and export assertions refer to the older versions they name. Do not treat
18 October PDF verification as verification of the 24 October graph section.
The new readiness disposition is included in review/READINESS_20261025.txt.

CURRENT STATUS
All five contribution groups are proposed for correctness and priority review.
The arity-three sqrt(s/6)-to-3s^2 gap is open. No arbitrary-graph bound or P4
optimality is claimed. Novelty remains unconfirmed. Human review has not been
obtained. No application efficacy or field-level breakthrough is asserted.
The 25 October method obstructions are separate research notes, not added claims.
No third-party article PDFs are redistributed. No human outreach was sent.
