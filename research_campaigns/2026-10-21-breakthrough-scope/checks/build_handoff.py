from pathlib import Path
from html import escape
import json
R=Path(__file__).resolve().parents[1]
report=escape((R/'CAMPAIGN_REPORT.txt').read_text())
proof=escape((R/'proofs/FINAL_ENVELOPE_OBSTRUCTION.txt').read_text())
state=json.loads((R/'CAMPAIGN.json').read_text())
finished=state['status']=='complete'
status='Campaign complete · internally audited · specialist review pending' if finished else 'Final audit and packaging in progress · campaign cutoff07:32:47UTC'
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoopGPT · Three-hour mathematical campaign</title>
<style>
:root{--ink:#172b35;--paper:#f7f5ef;--accent:#155b59;--line:#cbd2ca;--muted:#4e6067}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 Georgia,serif}
header{background:var(--ink);color:#f7f5ef;padding:56px max(24px,calc((100vw - 1080px)/2)) 44px}
.eyebrow,nav,.badge,th,.meta{font-family:system-ui,sans-serif}.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#b7d3ce}
h1{font-size:clamp(32px,4.8vw,60px);line-height:1.08;max-width:900px;margin:18px 0 24px;font-weight:500}
header p{max-width:820px;font-size:20px;color:#dce6e4}.badge{display:inline-block;border:1px solid #789d96;padding:7px 12px;font-size:12px;border-radius:4px}
nav{background:#e8ece5;border-bottom:1px solid var(--line);padding:13px 24px;display:flex;gap:22px;flex-wrap:wrap;justify-content:center;font-size:13px;position:sticky;top:0;z-index:2}
a{color:var(--accent);text-underline-offset:3px}nav a{color:var(--ink)}main{max-width:1080px;margin:auto;padding:30px 24px 80px}section{padding:24px 0 32px;border-bottom:1px solid var(--line);scroll-margin-top:80px}
h2{font-size:30px;font-weight:500;line-height:1.25;margin:0 0 18px}h3{font-size:21px;margin:26px 0 8px}p{max-width:900px}.lead{font-size:22px;line-height:1.5}.equation{padding:25px;background:#e5eee8;border-left:4px solid var(--accent);font:22px/1.7 Georgia,serif;overflow:auto}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.card{background:#fffdf7;padding:22px;border:1px solid var(--line);border-radius:5px}.card p{margin-bottom:0}.meta{font-size:13px;color:var(--muted)}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;padding:14px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:12px;text-transform:uppercase;letter-spacing:.05em;background:#e8ece5}ul,ol{padding-left:23px}li{margin:8px 0}pre{font:13px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#fffdf8;border:1px solid var(--line);padding:22px}details{margin:22px 0}summary{cursor:pointer;font-size:19px;color:var(--accent)}.note{border-left:3px solid #b58041;padding-left:20px;color:#574b3d}.steps{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.steps span{padding:10px 15px;background:#e8ece5;border:1px solid var(--line);font:13px system-ui,sans-serif}
footer{font:12px/1.6 system-ui,sans-serif;color:var(--muted);padding-top:30px}.downloads a{display:block;padding:7px 0}@media(max-width:700px){.grid{grid-template-columns:1fr}header{padding:35px 24px}nav{position:static;justify-content:flex-start}table{font-size:13px}th,td{padding:10px 7px}.equation{font-size:18px}}
@media print{nav{display:none}header{background:white;color:#172b35;padding:10px 0}header p,.eyebrow{color:#172b35}main{padding:0}.card{break-inside:avoid}details:not([open]){display:none}a{color:#172b35}section{break-inside:auto}h2,h3{break-after:avoid}}
</style></head><body>
<header id="top"><div class="eyebrow">CoopGPT / research campaign /21October2026</div>
<h1>A limit of the minimum-norm envelope</h1>
<p>A three-hour campaign found a general obstruction to one proposed payment rule. Making each owner's payment monotone can produce funding far beyond its raw projection benchmark.</p>
<div class="badge">STATUS_TEXT</div></header>
<nav aria-label="Contents"><a href="#result">Result</a><a href="#meaning">Meaning</a><a href="#proof-map">Proof</a><a href="#review">Verification</a><a href="#next">Next direction</a><a href="#files">Files</a><a href="#full-report">Full handoff</a></nav>
<main>
<section id="result"><h2>The result</h2>
<p class="lead">There is no fixed constant <i>C</i> for which this rule always spends at most <i>C</i>√<i>N</i> times output.</p>
<div class="equation">For every <i>C</i> &gt;0 and <i>N</i><sub>0</sub>, there is a finite instance with <i>N</i> ≥ <i>N</i><sub>0</sub> and<br>∑<sub>i</sub> <i>M</i><sub>i</sub>(<i>b</i>) &gt; <i>C</i>√<i>N</i> · <i>T</i>.</div>
<p>Along an explicit sequence, the stronger bound is <strong>∑<sub>i</sub><i>M</i><sub>i</sub> &gt; (1/40)√<i>N</i>(log <i>N</i>/log log <i>N</i>)<sup>1/3</sup><i>T</i></strong>. The squared-payment total and the ratio to raw projection funding are also unbounded.</p>
<p class="note">This is a result about the own-report envelope of the minimum-Euclidean-norm cover. It is not an impossibility theorem for all truthful mechanisms. Novelty and field-level significance remain unconfirmed.</p>
</section>
<section id="meaning"><h2>What it means</h2><div class="grid"><article class="card"><h3>The rule under study</h3><p>First minimize the sum of squared payments while covering every coalition. Then, for each owner, take the largest payment it could obtain by underreporting its resources. This makes the payment nondecreasing in its own report and preserves coalition coverage.</p></article><article class="card"><h3>Why the budget can grow</h3><p>Each owner's maximum can come from a different report profile. Combining those separate coordinates need not preserve one common budget bound. The construction makes this mismatch grow across the whole owner population.</p></article></div>
<p>Owners and production stay fixed in every comparison. The example has two resources per owner, one finite min-linear technology with binary coefficients, and all real unilateral underreports remain allowed. The endpoint reports in the certificate only lower-bound that full supremum.</p>
<p>The existing manuscript already records a different mechanism with an <i>O</i>(√<i>N</i>) guarantee. Today's obstruction does not contradict it; it rules out this proposed substitute. The unrestricted mechanism gap and the coalition paper's arity-three gap are unchanged.</p>
</section>
<section id="proof-map"><h2>How the proof fits together</h2><div class="steps"><span>Q-ary line hypergraph</span><span>Exact local marginals</span><span>All-cut transport</span><span>Projection KKT</span><span>One fixed production game</span><span>Unbounded funding</span></div>
<ol><li>Translate one local construction across all vertices of a q-ary cube.</li><li>Repair every newly completed axis line, then equalize outside marginals.</li><li>Use a finite rational flow argument to preserve the exact set size; check all cuts analytically.</li><li>Certify the changed minimum-norm point while preserving every off-owner constraint.</li><li>Add a common veto and control resources so all selected reports occur inside one institution.</li><li>Let the alphabet grow to obtain the funding lower bound.</li></ol>
<p>The common veto also provides an efficient competing payment rule. That is a deliberate scope check: the construction identifies a weakness of this particular payment architecture.</p>
<table><thead><tr><th>Question entering the campaign</th><th>Final status</th></tr></thead><tbody>
<tr><td>Squared envelope ≤ output²?</td><td>False; the squared ratio is unbounded.</td></tr>
<tr><td>Funding ≤ √<i>N</i> · output?</td><td>False, even with a strictly larger finite certificate.</td></tr>
<tr><td>Funding ≤ <i>C</i>√<i>N</i> · output for some fixed <i>C</i>?</td><td>False for this envelope architecture.</td></tr>
<tr><td>Constant envelope/raw-projection funding ratio?</td><td>False for every constant.</td></tr>
<tr><td>Best possible bound over all eligible mechanisms?</td><td>Still open; this campaign does not change it.</td></tr></tbody></table>
</section>
<section id="refinement"><h2>A sharp result inside the construction class</h2><p>Fix the auxiliary hyperedge size <i>Q</i>. In the specified common-veto production class, the exact asymptotic leading funding coefficient is <strong><i>Q</i>/2</strong>. A matching construction and upper bound include all real own underreports at the designated full bundles.</p><p>Both the hypergraph and the transitive fixed-size row family must be nonempty. This auxiliary <i>Q</i> is not production activity arity. The <a href="proofs/mass_geometry_qary_sharp_audit.txt">precise theorem and stronger finite bounds</a> and <a href="reviews/sharp_extension_verification.txt">separate review record</a> state the limits.</p></section>
<section id="review"><h2>Verification and limits</h2><p>Two independent native mathematical audits rederived the construction. The cross-model q-ary review found no mathematical defect and requested exposition repairs, now incorporated. A separate final integration review also found no mathematical defect in the fixed-owner theorem and quantitative consequence. The ledger records its scope and the accepted clarity additions.</p>
<p>Exact Python checks use only integer and rational arithmetic. One independent audit enumerates2,014 local states, handles composite alphabets, and checks parameter cases through <i>Q</i>=16. These diagnostics supplement the written proof.</p>
<p class="note">The final examples are astronomically large. The full cover and transport network were not enumerated. Their existence follows from the all-cut argument. No proof assistant or human specialist has certified this result.</p>
<p>Projection geometry, KKT, gauge duality, maxflow and minimum-of-additive representations are established ingredients. The source ledger separates those ingredients from the proposed construction and records incomplete original-source comparisons.</p>
</section>
<section id="next"><h2>The recommended next direction</h2><p><strong>Consolidate and obtain specialist correctness and priority review.</strong> The focused packet is drafted; no outreach has been sent.</p><p>Retire the unrestricted constant-times-square-root target for this exact envelope. A useful next mechanism must change the way payments are selected across reports. Require an improvement to a general bound or a structural lemma with a demonstrated consequence; a veto-specific patch or another small instance would not meet that gate.</p><p>The coalition paper remains a separate contract. These results have not been inserted into its manuscript, and neither the canonical repository nor GitHub has been changed.</p></section>
<section id="files"><h2>Read or reproduce</h2><div class="grid"><div class="downloads"><a href="proofs/FINAL_ENVELOPE_OBSTRUCTION.txt">Complete consolidated theorem and proof</a><a href="REVIEW_PACKET.txt">Specialist review packet draft</a><a href="sources/PRIORITY_COMPARISON.txt">Source and novelty comparison ledger</a><a href="reviews/FINAL_REVIEW_LEDGER.txt">Review findings and final adjudication</a></div><div class="downloads"><a href="REPRODUCE.txt">Reproduction instructions</a><a href="replay_essentials.py">Exact replay runner</a><a href="REPLAY_RESULTS.json">Recorded replay results</a><a href="review-bundle.zip">Portable review bundle</a></div></div><pre>python3 replay_essentials.py</pre><p class="meta">Run from the extracted bundle directory. Python3 standard library only. Finite diagnostics do not replace the general proof.</p></section>
<section id="full-report"><h2>Full handoff and proof</h2><details><summary>Read the complete campaign handoff</summary><pre>REPORT_TEXT</pre></details><details><summary>Read the full consolidated proof</summary><pre>PROOF_TEXT</pre></details></section>
<footer>Campaign window:21October2026,04:32:47–07:32:47UTC /00:32:47–03:32:47Eastern. Local research artifact. No outreach, publication, repository push or manuscript change. <a href="#top">Back to top</a></footer>
</main></body></html>'''
html=html.replace('STATUS_TEXT',escape(status)).replace('REPORT_TEXT',report).replace('PROOF_TEXT',proof)
(R/'handoff.html').write_text(html)
print('Wrote handoff.html',len(html),'characters')
