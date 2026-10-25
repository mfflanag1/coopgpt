COOPGPT — CERTIFICATE SELECTION FOLLOW-UP
Open index.html, then CAMPAIGN_REPORT.txt.
Complete proof: math/LAMINAR_SELECTION_OBSTRUCTION.txt.
Exact replay (standard library; Python 3.10+, assertions enabled):
  python3 math/check_laminar_obstruction.py
Expected retained output: math/EXACT_CHECK.json.
The script certifies the declared finite profile system and the exact positive-report variant. The general epsilon argument is the written proof. Neither is an all-profile upper bound.
Numerical discovery: math/search_laminar.py and the discovery JSONs require NumPy/SciPy and are exploratory only; the exact theorem does not depend on solver tolerances. Earlier diagnostic grids did not establish a theorem. The random discovery seed was 251025; the seventh four-owner binary min3 instance yielded the reduced three-profile witness.
Independent review and root adjudication: reviews/PROOF_DISPOSITION.txt.
Failed independent exploration: reviews/DELEGATE_DISPOSITION.txt.
Scope/priority check: SOURCE_COMPARISON.txt.
Input hashes: INPUT_MANIFEST.json. Final output hashes: ARTIFACT_HASHES.json.
The preceding reset package is preserved unchanged.
