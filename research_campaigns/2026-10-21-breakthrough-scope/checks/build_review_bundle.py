from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
paths={
 'README.txt','CAMPAIGN.json','CAMPAIGN_REPORT.txt','REVIEW_PACKET.txt',
 'REPRODUCE.txt','replay_essentials.py','REPLAY_RESULTS.json','handoff.html',
 'CONTRACT.txt','TARGET.txt','INPUT_MANIFEST.json','SOURCE_PRESERVATION.json','scouting/SELECTION.txt',
 'sources/PRIORITY_COMPARISON.txt',
 'proofs/FINAL_ENVELOPE_OBSTRUCTION.txt','proofs/activation_qary_cube_proof.txt',
 'proofs/activation_qary_direct_corollary.txt','proofs/activation_qary_portable_manifest.txt',
 'proofs/activation_qary_provenance_restore.txt','proofs/mass_geometry_qary_audit.txt',
 'proofs/mass_search_qary_cube_audit.txt','proofs/mass_geometry_final_integration_audit.txt',
 'proofs/CONSOLIDATED_THEOREM.txt','proofs/mass_search_true_envelope_upper_audit.txt',
 'proofs/mass_geometry_final_upper_attempt.txt','proofs/FUNDING_VERSUS_DIAGONAL_REDUCTION.txt',
 'proofs/activation_qary_cube_check.py','proofs/activation_qary_direct_check.py',
 'checks/mass_search_qary_cube_audit.py','checks/mass_geometry_qary_verify.py',
 'checks/mass_search_true_envelope_upper.py',
}
for pattern in ('reviews/*.txt','reviews/snapshots/*','replay-logs/*.txt','proofs/*qary*sharp*','checks/*qary*sharp*'):
 paths.update(str(p.relative_to(R)) for p in R.glob(pattern) if p.is_file())
missing=[p for p in paths if not (R/p).is_file()]
assert not missing,missing
manifest={'description':'Selected portable review files. Manifest excludes itself and the zip archive.',
 'files':{p:{'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest(),'bytes':(R/p).stat().st_size} for p in sorted(paths)}}
(R/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
paths.add('PACKAGE_MANIFEST.json')
with zipfile.ZipFile(R/'review-bundle.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(paths):z.write(R/p,p)
with zipfile.ZipFile(R/'review-bundle.zip') as z:
 assert z.testzip() is None
 for p,meta in manifest['files'].items():assert hashlib.sha256(z.read(p)).hexdigest()==meta['sha256'],p
print(json.dumps({'files':len(paths),'zip_bytes':(R/'review-bundle.zip').stat().st_size,'hashes_verified':True}))
