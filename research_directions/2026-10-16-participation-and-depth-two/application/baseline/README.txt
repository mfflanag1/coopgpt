Public participation/fairness extension: bounded theory packet,16 October2026

Read PARTICIPATION_THEOREMS.txt for statements, proofs, and model boundaries;
read SOURCES_AND_CONTRACT.txt for verified free primary sources and the economic
participation contract. No historical novelty or field-level breakthrough claim.

Proved over arbitrary real capacities and every finite m>=1:
* Public local-production floor theta*L has exact worst total factor1+theta;
  the lower is already static and holds with all resources/owners active.
* Public marginal floor theta*(T-v(N\A)),0<=theta<=1, has exact worst static
  funding ratio1+theta/4. An explicit static covering vector proves the upper.
* The same marginal floor forces extra funding relative to POINTWISE STATIC
  minimum B_f: K_f>=max{(8+2theta)/(8+theta),(4+2theta)/5}. These conventional
  proofs need only2 or3 profiles,4 fixed actual owners, and unit coefficients.
  K_f>1 does not prove a higher global worst production-normalized factor.
* Positive constant reservation retainers require additive accounting at zero
  production; the payment-only proof assumes no unmodeled private outside gains.

Finite optima are separately certified on complete stated Cartesian domains.
For theta1/2 and1 on the two-pod ternary grid, static-normalized optima are
18/17 and6/5. The six-fifths result also survives a larger two-pod grid and a
three-pod ternary grid. Production-normalized optima at theta1 are5/4 on both
two- and three-pod ternary grids. These finite upper certificates do not prove
continuous upper bounds. Other small-grid checks for constant/local floors
show no incentive premium on those domains; no global K_f=1 claim is made.

REPLAY (Python standard library only; run from this directory)
  python3 -B -O verify_floor_certificates.py floor-*.json.gz
  python3 -B -O check_domain_guards.py
The verifier reconstructs coalition production by independent exact Fraction
max-profit flow, checks each static LP primal and dual, reconstructs the
mechanism dual, and checks every finite payment, coalition, floor, budget, and
adjacent own-coordinate increase. Complete unique Cartesian domain checks
make adjacent comparisons sufficient for every coordinatewise bundle increase.
DOMAIN_GUARDS.jsonl records8 deliberately malformed inputs being rejected.
EXACT_REPLAY.jsonl records the actual uncompressed-input replay before packaging;
COMPRESSED_REPLAY.jsonl is the portability replay of packaged certificates.

DISCOVERY (optional; SciPy required; not part of exact replay)
  python3 floor_probe.py
This reproduces the four basic two-pod local/marginal cases. The solver's
normalizer argument selects 'static' or 'production'; larger m/levels are
optional bounded diagnostics. Discovery rationalizes solutions and fails
closed if primal or dual verification is unavailable. The independent replay
does not import discovery code or SciPy.

AUDIT STATUS AT FREEZE
Root independently rederived the compact continuous lower proofs. Fable review
of the original packet found no mathematical gap; its two notation requests
(definition of C_f on T>0 and vector-floor B_q) were applied. The later static
1+theta/4 theorem is outside that Fable snapshot and is separately checked by
the pivot lane; coordinator should record its final status. Exact finite
replay independently passed in this lane, and the pivot lane independently
checked both selected243-profile marginal cases with every strict whole-bundle
comparison. The hardening of domain checks was prompted by that review.

This packet adds public floors to the original floor-free model. It does not
close the arbitrary mixed-owner depth-two frontier. Fixed retainers are a
credible contract starting point; marginal-contribution shares are optional
fairness provisions, not private-cost estimates or automatic participation law.

PROVENANCE
flow_oracle.py is copied unchanged from the preceding bounded campaign's
independent exact bipartite-flow oracle. All other theorem/verification artifacts
here were produced in this lane. MANIFEST.json records payload SHA256 and size.
