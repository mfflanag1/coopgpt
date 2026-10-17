from pathlib import Path
import hashlib,json
b=Path('/private/tmp/coopgpt-overnight-20261017')
def replace(p,a,c):
 f=b/p;s=f.read_text();assert a in s,(p,a);f.write_text(s.replace(a,c))
replace('handoff/READ_FIRST.txt','curated25 check entry points','curated26 check entry points')
replace('handoff/VERIFICATION_GUIDE.txt','curated25 entry points','curated26 entry points')
f=b/'handoff/READ_FIRST.txt';s=f.read_text();mark='HOW TO READ FUNDING CLAIMS\n';assert mark in s
s=s.replace(mark,'''A broad payment architecture now has a sharp-order limitation. For fixed
nonnegative whole-owner marginal weights, protecting groups up to size s on
arity-r production requires order s^(r-1) in the worst case. This includes
asymmetric and population-dependent fixed weights. At r=3 it blocks improving
the quadratic upper by merely changing those weights. A finite16-owner,
size4 certificate requires factor5 on min3; general mechanisms have factor2
on that same technology. Read root64 and65. This is an architecture separation,
not an unrestricted lower. The general arity-three frontier remains
Omega(s^(1/4)) versus O(s^2).

'''+mark);f.write_text(s)
replace('handoff/CAMPAIGN_OUTCOMES.txt','The final positive-marginal gate investigates a broad\nsampling architecture; its acceptance and exact scope are recorded separately.','''The final gate proves that EVERY fixed nonnegative whole-owner marginal-weight
rule has worst funding order Theta_r(s^(r-1)), even permitting asymmetric and
population-dependent weights. The lower already holds on one fixed min-r
technology. At r=3 this architecture cannot improve the quadratic exponent.
An exact16-owner certificate requires factor5 for protected groups up to4;
general mechanisms on the same min3 technology have factor2. These accepted
root64/65 obstructions identify a class to leave behind; they do not improve
the unrestricted lower or establish that the general exponent is quadratic.''')
replace('handoff/CAMPAIGN_OUTCOMES.txt','The signed-L1 transfer gives sharp3/2 and1+c for L1-embeddable norm reserve pooling, including\nEuclidean reserves.','The signed-L1 transfer gives sharp3/2 and1+c, uniformly over finite owner\npopulations, for L1-embeddable norm reserve pooling, including Euclidean reserves.')
f=b/'handoff/RECONCILIATION_NOTES.txt';f.write_text(f.read_text()+'''
11. The final positive-marginal barrier applies to arbitrary nonnegative fixed
whole-owner marginal weights, including asymmetric population-dependent ones
(root64). It is not limited to a common Bernoulli mixture. Only the weak-limit
measure has support in[0,1/s]; no finite-n support claim follows. The exact
16-owner certificate(root65) needs no weak limit and gives factor5 versus the
general min3 mechanism's2. Neither result is an unrestricted funding lower.
Normalized semivalues are classical; arbitrary scaled positive rules here need
not have unit mass. Report-adaptive, signed, resource-level and nonlinear rules
remain outside the obstruction.
''')
f=b/'handoff/VERIFICATION_GUIDE.txt';f.write_text(f.read_text()+'''
Entry26 reconstructs the finite16-owner positive marginal-rule certificate.
Its focused report is checks/FINITE_POSITIVE_MARGINAL_REPLAY_20261017.json.
The separate composition-lane replay uses subset-incidence aggregation and is
included as independent evidence. The analytic symmetrization and inequality
logic are audited separately; the numerical LP scout is not a proof dependency.
''')
replace('handoff/REVIEW_READING_ORDER.txt','generic SFM implementation is claimed. A weighted-coverage max-flow backend is\nunder separate implementation and is excluded until accepted. This is a separate\npacket, not mandatory reading for A or B.','''generic SFM implementation is claimed. An exact rational weighted-coverage
max-flow backend is now accepted in root63, with independent exact checks and
cross-model review. Its optional polymatroid-with-flow archive includes the
full implementation dependencies. The fixed-public-fleet-mix coverage subclass
already embeds into earlier bipartite resource graphs; no new technology class,
full OUT extension, energy saving, or service-latency claim follows. This is a
separate packet, not mandatory reading for A or B.''')
f=b/'handoff/REVIEW_READING_ORDER.txt';s=f.read_text();mark='VERIFICATION AND PACKAGING\n';assert mark in s
s=s.replace(mark,'''OPTIONAL POSITIVE MARGINAL-RULE BOUNDARY

The positive-marginal archive is an architecture theorem with an exact finite
separation. Read unrestricted/SEMIVALUE_MIXTURE_OBSTRUCTION_GATE.txt first,
then SEMIVALUE_MIXTURE_GENERAL_FIXED_MARGINALS.txt. Fixed nonnegative
whole-owner marginal weights have worst funding order Theta_r(s^(r-1)).
The same fixed min-r technology admits a general TCWM mechanism of factor
(r+1)/2, so the obstruction diagnoses the formula, not the underlying problem.
The supplied GENERAL_FACE_AVERAGE_TCWM.txt proves that comparator.

For a finite entry point, POSITIVE_MARGINAL_FINITE_CERT_THEOREM.txt gives
16 actual owners, protected groups at most4, and a factor5 lower on min3.
Its JSON and standard-library checker reconstruct actual report transitions
and exact rational dual coefficients; an independent replay is included.
No finite-n support restriction or LP numerical optimum is asserted.
The scaled-binomial sparse-production theorem supplies the matching-order
upper; its Bernoulli and bounded-arity ingredients are established. Read
energy/SEMIVALUE_MIXTURE_PRIORITY_GATE.txt for the direct source comparisons.
Historical novelty remains unconfirmed. Report-dependent, signed and general
resource-level mechanisms are outside this lower-bound class.

'''+mark);f.write_text(s)
p=b/'handoff/MINIMAL_REVIEW_PACKETS.json';d=json.loads(p.read_text())
for row in d['optional_modules']:
 if row['id']=='structural-polymatroid':
  a=row['algorithm_extension'];a.pop('claim_if_accepted',None)
  a['remaining_gates']=['Practical general SFM implementation remains outside this packet.','No bit-cost theorem for unspecified or approximate real oracles.','Original1980 and Groenevelt1991 texts were not retrieved; the inspected2013 original supplies the needed recursion.']
  a['excluded_pending_work']='Weighted-coverage max-flow is accepted in root63 and included in the separate coverage-flow module and polymatroid-with-flow archive.'
files=[
('unrestricted/SEMIVALUE_MIXTURE_OBSTRUCTION_GATE.txt','threshold-support proof'),
('unrestricted/SEMIVALUE_MIXTURE_GENERAL_FIXED_MARGINALS.txt','general asymmetric fixed-weight lower proof'),
('unrestricted/POSITIVE_MARGINAL_FINITE_CERT_THEOREM.txt','exact finite architecture separation proof'),
('unrestricted/POSITIVE_MARGINAL_FINITE_CERT_N16_S4_FACTOR5.json','rational dual certificate input'),
('unrestricted/POSITIVE_MARGINAL_FINITE_CERT_CHECK.py','raw-subset exact checker'),
('unrestricted/POSITIVE_MARGINAL_FINITE_CERT_CHECKS.json','exact finite record'),
('unrestricted/SEMIVALUE_MIXTURE_CHECK.py','exact threshold checks'),
('unrestricted/SEMIVALUE_MIXTURE_CHECKS.json','threshold check record'),
('unrestricted/SEMIVALUE_MIXTURE_EXCHANGEABILITY_CHECK.py','hypergeometric comparison checks'),
('unrestricted/SEMIVALUE_MIXTURE_EXCHANGEABILITY_CHECKS.json','exchangeability check record'),
('composition/SEMIVALUE_MIXTURE_FINAL_GATE.txt','independent analytic audit'),
('composition/POSITIVE_MARGINAL_FINITE_CERT_AUDIT.txt','independent finite analytic and computational audit'),
('composition/POSITIVE_MARGINAL_FINITE_CERT_REPLAY/independent_replay.py','second exact implementation'),
('composition/POSITIVE_MARGINAL_FINITE_CERT_REPLAY/independent_replay.json','second implementation evidence'),
('energy/BOUNDED_COALITION_SPARSE_PRODUCTION.txt','matching-order upper proof with classical ingredients credited'),
('root/GENERAL_FACE_AVERAGE_TCWM.txt','general-mechanism comparator proof'),
('energy/SEMIVALUE_MIXTURE_PRIORITY_GATE.txt','original-source comparisons and unresolved priority'),
('root/ROOT_ADJUDICATION_64_POSITIVE_MARGINAL_BARRIER.txt','asymptotic acceptance and scope'),
('root/ROOT_ADJUDICATION_65_FINITE_POSITIVE_MARGINAL_SEPARATION.txt','finite acceptance and scope'),
('reviews/POSITIVE_MARGINAL_FABLE.md','cross-model general proof review'),
('reviews/FINITE_POSITIVE_MARGINAL_FABLE.md','cross-model finite review; wording findings corrected'),
('checks/POSITIVE_MARGINAL_REPLAY_20261017.json','isolated threshold/exchangeability replay'),
('checks/FINITE_POSITIVE_MARGINAL_REPLAY_20261017.json','isolated current finite checker replay')]
records=[{'path':p,'role':role,'sections':'all','sha256':hashlib.sha256((b/p).read_bytes()).hexdigest()} for p,role in files]
d['optional_modules'].append({'id':'positive-marginal','title':'Limits of fixed positive whole-owner marginal rules','status':'Accepted root64 and65 after independent and cross-model audits','claim':'Worst architecture order Theta_r(s^(r-1)); exact16-owner min3 factor5 versus general factor2.','files':records,'limits':['Architecture-only, not an unrestricted-mechanism lower.','No sharp leading constant or finite-n support claim.','Historical novelty and external specialist review unconfirmed.']})
d['archive_sets'].append({'id':'positive-marginal','archive_name':'coopgpt-review-positive-marginal.zip','claim_scope':'Fixed positive whole-owner marginal rules have worst coalition-size order Theta_r(s^(r-1)); exact16-owner factor5 architecture separation on min3, whose general TCWM factor is2.','proof_and_evidence_paths':[p for p,_ in files]})
p.write_text(json.dumps(d,indent=2)+'\n')
print('Updated final-gate handoff and explicit review packet manifest')
