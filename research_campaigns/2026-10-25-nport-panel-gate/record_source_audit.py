"""Preserve browser-observed NAV fields and exact field-match outcomes; no network."""
from pathlib import Path
from fractions import Fraction as F
import json,datetime
p=Path(__file__).parent
# Values transcribed from browser audit output; not inferred from the bulk table.
observed='''S000000046 692256901.80 2387844.65 689869057.15 1
S000000047 2999389302.45 168742824.83 2830646477.62 1
S000000091 303588023.50 926523.53 302661499.97 1
S000000094 133184890.63 3375070.85 129809819.78 1
S000000179 403903898.66 82146024.62 321757874.04 0
S000000181 162307572.90 11085462.06 151222110.84 0
S000000205 188578690.62 46444507.59 142134183.03 0
S000000285 7725557769.00 68847852.00 7656709917.00 2
S000000286 4129061768.00 228050577.00 3901011191.00 2
S000000288 4776979375.00 56903491.00 4720075884.00 2
S000000289 19672270981.00 5245975572.00 14426295409.00 2
S000000317 648421383.67 69614388.39 578806995.28 1
S000000540 2304351416.91 38041395.98 2266310020.93 1
S000000699 800719709.140000000000 21057639.820000000000 779662069.320000000000 0
S000000713 2938901106.92 371343146.89 2567557960.03 1
S000000714 6278131909.57 825870399.46 5452261510.11 1
S000000715 51962784.64 547917.03 51414867.61 1
S000000753 52808709058.160000000000 26262720.020000000000 52782446338.140000000000 0
S000000754 38479756113.090000000000 42637080.960000000000 38437119032.130000000000 0
S000000755 10934588476.170000000000 11322731.220000000000 10923265744.950000000000 0
S000000882 149012335.83 1449044.45 147563291.38 1
S000002766 458112946.59 7014293.25 451098653.34 1
S000002874 156158067.56 6302157.46 149855910.10 2
S000009699 664202551.540000 256666623.260000 407535928.280000 7
S000011985 3617284.91 135860.91 3481424.00 2
S000013233 1158904356.960000 714360465.560000 444543891.400000 7
S000018357 794498784.79 14395895.17 780102889.62 2
S000026750 1595833136.920000 188259.960000 1595644876.960000 7
S000037359 718647307.88 1286773.88 717360534.00 0
S000037364 858966430.72 486919.78 858479510.94 0
S000037365 1939916471.22 2195685.89 1937720785.33 0
S000055861 43813924.650000000000 673233.830000000000 43140690.820000000000 1
S000062360 28423360095.89 1656913696.94 26766446398.95 2
S000062374 21380607.13 892001.67 20488605.46 2
S000062376 1054306985.75 32647156.26 1021659829.49 2
S000072568 46744711.74 1981345.90 44763365.84 1
S000072935 138846383.22 65882162.79 72964220.43 1
S000075349 1250764338.64 6539629.52 1244224709.12 0
S000075444 5402751795.13 3506285120.45 1896466674.68 0
S000090015 6272279.85 100679.08 6171600.77 0'''
audit=json.loads((p/'bulk_analysis/audit_selection.json').read_text())
rows={r['series_id']:r for r in json.loads((p/'reviewed_bulk_analysis/rows.json').read_text())}
obs={x.split()[0]:x.split()[1:] for x in observed.splitlines()}
if set(obs)!={r['series_id'] for r in audit}:raise ValueError('Audit membership mismatch')
pre=json.loads((p/'complete_preflight.json').read_text())
versions={r['series_id']:r['all_batch_accessions'] for r in pre['amendment_audit']}
for entry in audit:
 sid=entry['series_id'];assets,liabilities,nav,notes=obs[sid];r=rows[sid]
 if F(assets)-F(liabilities)!=F(nav) or F(nav)!=F(r['nav']):raise ValueError('Original NAV mismatch: '+sid)
 if int(notes)!=len(r['notes']):raise ValueError('Note count mismatch')
 entry.update(original_rendered_url=entry['filing_index'].rsplit('/',1)[0]+'/xslFormNPORT-P_X01/primary_doc.xml',status='SOURCE_FIELDS_MATCHED; CONVENTIONS_UNRESOLVED',original_assets=assets,original_liabilities=liabilities,original_nav=nav,nav_identity_exact=True,original_note_count=int(notes),all_10_metric_values_numerically_matched=True,series_cik_reference_date_usd_nav_matched=True,filing_index_accession_and_reference_date_matched=True,all_part_e_note_texts_and_count_matched=True,bulk_metric_strings_compared=r['raw_metrics'],bulk_notes_compared=r['notes'],batch_versions=versions[sid],direction_convention='not established',internal_precision='unknown',economic_valuation_validated=False)
result={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'SEC filing index and its observed primary_doc.html link opened in normal browser; rendered Part A/B/E read from document.body.innerText. Decimal strings normalized only for sign/leading/trailing zeros and compared as strings, never floating point. Original NAV fields below copied from tool output and rechecked with Fraction. Notes matched by whitespace-normalized text and count. 40 final records had all field checks true. Some incomplete renders were retried after navigation/load; they were not treated as source mismatches.','preservation_limit':'Browser comparison log and original NAV values are preserved; complete original XML/HTML files were not downloaded. Bulk raw values remain in the SHA256-identified archive. Re-reading originals requires public access.','sampling':'First20 lexicographic and top20 plus ties on the provisional exact-NAV subset, no overlap. If quarantines later change eligibility, regenerate both sets; this is not a final audit selection for a changed sample.','source_fields_matched':40,'metric_values_matched':400,'nav_identities_checked':40,'convention_validated_funds':0,'full_materiality_gate':'NOT_ESTABLISHED','rows':audit}
(p/'source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
