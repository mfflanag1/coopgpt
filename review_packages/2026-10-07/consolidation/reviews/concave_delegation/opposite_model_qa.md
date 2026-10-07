**Verdict: revise.**

**Findings**

1. **Major: fragment misses the requested concision target.**  
   The task asked for “complete concise proofs, ~250–450 lines.” The candidate fragment is 653 physical lines, and the notes explicitly acknowledge ~650 lines. This is a deliverable mismatch, even though the extra length is mostly proof material rather than irrelevant filler. I would require a shortening pass before insertion.

2. **Minor/process: verifier evidence is inconsistent in the candidate narrative.**  
   `checks.json` reports both supplied verifiers passing, but the result text and notes say the author did not run them. That is not a mathematical defect, but the final notes should clearly distinguish “author did not run” from “controller supplied passing verifier outputs,” so the provenance is not muddy.

3. **No proof-level blocker found in this review.**  
   The fragment appears to cover the requested mathematical content: selected-range `min{K,2^n}`, relative supports extended by `+\infty`, boundary-face proof without continuity, deterministic hybrid coverage and budget, all-large-`n` padding lower, marginal floors, dominant-share fallback with zero cases, nonconcave sharp `d` versus concave gap, and technology-aware refinements. I did not see forbidden novelty, computability, human-review, or sharp-rate claims.

4. **Owned-file scope appears satisfied from the patch.**  
   The patch creates only `concave_extension_fragment.tex` and `concave_integration_notes.txt`.

**Advice**

Revise mainly by compressing the fragment: fold the reusable Chernoff/budget lemmas into shorter “as in preceding section” statements where root context permits, merge the two remarks, and consider moving optional technology-aware cone details to notes if the manuscript section must stay lean. After that, I would be comfortable with **accept** subject to the same verifier outputs.