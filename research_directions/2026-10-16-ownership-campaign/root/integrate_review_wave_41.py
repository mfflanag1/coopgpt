from pathlib import Path
import shutil,json
r=Path('/private/tmp/coopgpt-ownership-20261016');a=r/'audits';s=Path('/Users/maxf/.local/state/claude-reviews/coopgpt-ownership-20261016-0ad718e4be4a/20261016-204802-a33529c6')
for f in ['review.md','request.json','status.json','execution.json']:shutil.copy2(s/f,a/('HIGH_S_AND_STOPPING_OBSTRUCTION_FABLE_'+f))
artifact=json.loads((r/'root/entropy_general_certificate/eight_fifths/high_S_certificate.json').read_text())
if (artifact['NS'],artifact['ND'])!=(64,32):raise RuntimeError('Reported root partition changed')
(a/'ROOT_REVIEW_ADJUDICATION_41.txt').write_text('''ROOT ADJUDICATION 41 -- EIGHT-FIFTHS SUBREGIME AND EXACT STOPPING WITNESS
17 October 2026. Accepted internally. GENERAL bound remains323/200.

Accept EIGHT_FIFTHS_SUBREGIME_AND_STOPPING_OBSTRUCTION.txt with its stated scope:
for physical hardware bottlenecks H>0 with S=sum min(p_i+z_i,H)/H>=2, the
original actual whole-owner envelope satisfies sum E_i<(8/5)H. This is NOT a
global8/5 theorem. The proof separately covers high effective grid and the
closed low-grid high-S domain with no one-cap rows.

Root inspected the standalone verifier, all row/objective directions and binary
partition logic and executed an independent -I -O exact Fraction replay.
Independent Codex inspected the same mathematics and replayed normal and
optimized modes. All outputs agree:2,020 certified leaves,200 geometric empty
leaves,1,900 uniform/120 curved objectives,maximum1.5999986058139273<8/5.
Exact rational comparisons, not decimals, establish each inequality. Root also
confirmed the frozen artifact has exactly64 by32 roots. The verifier permits
other complete root partitions, which is sound; it does not need to pin these
particular counts to prove complete coverage. Frozen hashes identify this one.

Accept the finite255-row rational relaxation obstruction: at S=47/25,
delta=1/125,v=1/30 the stored rational vector satisfies every frozen row and
coordinate cap strictly and its stated objective exceeds8/5. Root and Codex
replays agree. It blocks that finite rational relaxation only. It is not an
actual game, not an envelope/eligible-mechanism lower bound, and not a barrier
to every support parameter or a different inequality. Uniform saving is weaker
than the curved objective at this witness, so switching those two objectives
does not resolve its failure. All further8/5 discovery was stopped.

Fable204802 found no concrete algebra/code/scope error. Its dependency-status
concern is resolved by adjudication34, which had already accepted the full
PARAMETRIC_ENTROPY_DEFICIT_SPILL theorem for every real eta>=2 after root
rederivation and Fable202317. The source's old candidate header is historical.
Root reread the omitted SUBSET_ENTROPY_DEFICIT_COUPLING reduction: hardware-
short uses the convex tangent; power-short uses exact clipping h-rho*T,
D>A and h/T>=rho; substitution gives precisely EP3. Thus H1 is supported by
an accepted analytic theorem, not by the header or sampled scalar checks.
The inverse-deficit PF rows follow from accepted IG8 and adjudication38's
sharp individual ceiling, with eta_Q>=0 including the M=0 convention.

Fable could not inspect the377KB certificate in its bounded text packet and
executed no checks. That is an actual limitation of its review; it is resolved
for campaign acceptance by root/Codex exact execution and code inspection,
not by claiming Fable checked the tree. All primary frozen certificate/verifier
hashes were rechecked before integration. The prior false general S>=2 C^2
pointer remains withdrawn and is not a dependency of either accepted theorem.

The campaign therefore ends with a proved general improvement and a precise
stopping result for the stronger attempted bound. External specialist review,
historical priority and unrestricted mechanism optimality remain open.
''')
print('Adjudication41 saved; dependency and packet limitations explicitly resolved.')
