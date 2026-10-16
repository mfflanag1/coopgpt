from pathlib import Path
r=Path('/private/tmp/coopgpt-ownership-20261016')
p=r/'CURRENT_RESULTS.txt';s=p.read_text()
s=s.replace('Updated17October2026,00:30UTC. Campaign ACTIVE; main synthesis after00:53:56UTC.','Updated17October2026 after adjudication40. Campaign ACTIVE; main synthesis after00:53:56UTC.')
s=s.replace('liminf >=c[Fresp-2e-Klog2] approximately-0.785643710331513,','liminf >=c[J-2e-Klog2] approximately-0.777825046106238,')
s=s.replace('Fresp=2exp(1/4)-exp(-11/4)-1+(3/5)[2exp(1/5)-exp(-19/5)-1].\n   Lower: SHARED_RESPONSE_BRANCH_DIFFUSE_LOWER.txt, adjudication36.','J=(11/5)exp(2/5)-8/5+(3/5)Lambda, Lambda=(1-v_*)^2/v_*,\n   v_*exp(v_*)=1/2. Lower: JOINT_RESPONSE_DIFFUSE_LOWER.txt, adjudication40.')
s=s.replace('- Signed OTHER local loss<=3z_i/2 for arbitrary local-only bundle withholding;\n  hardware stays fixed and gains offset losses. It does NOT control capped\n  outer losses or the sum of positive losses. Adjudication36. Sharpening pending.','- SHARP signed OTHER local loss<=Lambda*z_i, Lambda=1.194793583015429...,\n  for arbitrary local-only bundle withholding with hardware fixed. More precisely\n  charge U_local-short+Lambda*V_local-long. Gains offset losses; capped outer\n  losses and positive-loss sums are separate. Actual attainment. Adjudication38.\n- SHARP inverse-entropy individual gap ceiling and one-capped-owner positive\n  dual coupling are accepted under adjudication38. The latter requires S<2;\n  the draft general S>=2 C^2 shortcut was explicitly withdrawn.')
s=s.replace('- Cap hiding invalidates replacing capped opposing-account loss by signed local\n  loss. The shared-response family demonstrates the distinction exactly.','- Cap hiding invalidates replacing capped opposing-account loss by signed local\n  loss. Exact joint-response counterexample ratio(11exp(2/5)-8)/7>6/5>Lambda\n  disproves the proposed two-deviation Lambda charge. Its unbounded lift\n  improves the actual diffuse lower, adjudication40.')
a=s.index('LIVE, NOT YET ACCEPTED\n');b=s.index('\nATTRIBUTION / LIMITS',a)
s=s[:a]+'''LIVE, NOT YET ACCEPTED
- The 8/5 global certificate attempt has separately covered S>=2 at builder
  level, but low-S pointwise relaxation failures remain. No universal8/5
  theorem has passed its gate. Exact verification and last support tests pending.
- Floating LP probes are relaxation diagnostics, NOT universal bounds, actual
  profiles, or exact obstructions. The accepted general bound remains323/200.
- The inverse-deficit PF support is a useful proved-ingredient corollary;
  its eventual effect on a global certificate needs separate validation.
'''+s[b:]
p.write_text(s)
p=r/'PROOF_MAP.txt';s=p.read_text()
s=s.replace('17 October2026,00:39UTC. ACTIVE research supplement;', '17 October2026 after adjudication40. ACTIVE research supplement;')
s=s.replace('SHARED_RESPONSE_BRANCH_DIFFUSE_LOWER.txt:\n accepted residual liminf >=approximately-0.785643710331513, adjudication36.\n A sharper mixed-response lower is in independent review; do not promote it\n before adjudication. The existence/exact value of a residual limit is open.','JOINT_RESPONSE_DIFFUSE_LOWER.txt:\n accepted residual liminf >=approximately-0.777825046106238, adjudication40.\n Its exact cap-hiding joint-response obstruction invalidates the proposed\n two-deviation Lambda charge. The residual limit/exact coefficient stays open.')
s=s.replace('Adjudication37: signed OTHER local-only loss<=4z_i/e, hardware retained. A sharp\nconstantLambda theorem is now in independent review. Neither statement controls\nthe sum of positive losses or capped outer losses without extra accounting.','Adjudication37 accepted signed4/e; now superseded by\n extension/SHARP_SIGNED_OTHER_LOCAL_LOSS.txt\nAdjudication38: SHARP Lambda=(1-v_*)^2/v_*, v_*exp(v_*)=1/2, with hardware\nretained. Role-sensitive charge U_short+Lambda V_long is also valid. This does\nnot control positive-loss sums or capped outer losses without extra accounting.')
s=s.replace('coupling: root/Codex/Fable algebra reviews PASS; final adjudication pending.','coupling: accepted under adjudication38 after root/Codex/Fable reviews.\nOne-cap applies only at S<2; the unsupported general S>=2 shortcut was withdrawn.\n root/RATIONAL_CAP_AND_CHORD_ROW_AUDIT.txt: accepted interval directions,\nadjudication39, but no global theorem without complete exact certification.\n extension/JOINT_SIGNED_RESPONSE_OBSTRUCTION.txt and\n extension/JOINT_RESPONSE_DIFFUSE_LOWER.txt: exact method obstruction and its\nunbounded consequence, adjudication40; supersede earlier pair lower.')
p.write_text(s)
with (r/'PROGRESS.txt').open('a') as f:f.write('''\n17October2026, final review consolidation: adjudications38--40 accept the sharp\nsignedLambda response theorem, sharp inverse-entropy gap ceiling, S<2 one-cap\ndual coupling, safe rational row directions, improved diffuse residual lower\n-0.777825046106238 and exact cap-hiding joint-response obstruction. The\nunsupported general S>=2 C^2 draft citation was withdrawn. Stronger8/5\ncertification remains unresolved and is in one final bounded support test.\n''')
print('Current ledger, proof map and progress synchronized through adjudication40.')
