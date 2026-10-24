COALITION WITHHOLDING — UPDATED CORRECTNESS AND PRIORITY REVIEW PACKAGE
Source update24 October2026. Existing dimension and arity results retained.

READ FIRST
manuscript.tex — standalone main manuscript, now including Section6 graph rule.
specialist_brief.tex — updated scoped correctness and priority questions.
review/PRIORITY_MATRIX.txt — original-source comparisons and unresolved gaps.
review/GRAPH_ADDITION_ADJUDICATION.txt — checks for the24October addition.

ADDITION
Explicit funding1+1/sqrt(2) for full coalition outside-production protection on
unit-profit P4 graphs, complete path blow-ups and disjoint unions. Fixed actual
mixed owners, all real report boxes, every coalition including passive members.
Total funding is distinguished from additional subsidy1/sqrt(2) times output.
Neither arbitrary graphs nor optimality on P4 are claimed. Complete proof is
integrated in the same paper; no separate corollary paper or novelty clearance.

RETAINED FRONTIERS
Dimension factors(d+1)/2 and1+c(d-1), c(2-exp(-1/c))=1.
Arity3: sqrt(s/6)<=K3(s)<=K3^OUT(s)<=3s^2, with sharper finite certificate
B_s~sqrt(2*pi*s)/(3*sqrt(e)); B6=493/243. Higher-arity and separate pure-owner
realizations remain. No old proof was replaced by the graph construction.

REPLAY
The six inherited checks remain python3 reproduce.py from this directory.
The added graph diagnostic is separate:
  python3 evidence/graph/protected_leaf_exact_replay.py
It uses exact Q(sqrt2) arithmetic at625 profiles and holding-cube corners.
All-real correctness is proved analytically, not by that finite replay.
The new recursive-architecture counterexample has its own exact checker:
  python3 evidence/graph/leaf_recursion_exact_check.py
Its FINAL proof note narrows an ambiguous historical peeling-order label to
layerwise processing; arbitrary sequential orders are not ruled out.

LATEX AND REVIEW
Both main .tex sources are standalone. source/ fragments are maintained editorial
inputs to assemble.py; the assembled manuscript has no external dependencies.
Human specialist correctness and historical-priority review have not yet been
obtained. OPEN_REVIEW_REQUEST.txt is an updated UNSENT local draft. No external
message, purchase, submission, Git commit or push is part of this source update.

PDF VERSION BOUNDARY
The existing manuscript.pdf and specialist_brief.pdf are the18October exports;
they do not include the24October graph addition. They are retained as archive
artifacts. Use the current .tex sources and live editor preview for this update.
Both current sources passed the desktop compiler. No separate PDF was compiled
or new editor tab opened, respecting the current document workflow.
