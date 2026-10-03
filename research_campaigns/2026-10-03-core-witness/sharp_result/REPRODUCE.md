# Reproduce the sharp theorem checks

Run from the CoopGPT repository root. Python 3.14.3 was used; these exact checkers use only the standard library and run with assertions disabled. Outputs below go to a temporary directory so committed evidence is preserved.

```sh
python3 -B -O research_campaigns/2026-10-03-core-witness/src/verify_sharp_aggregation.py research_campaigns/2026-10-03-core-witness /tmp/coopgt-sharp-checks.json
python3 -B -O research_campaigns/2026-10-03-core-witness/src/check_residual_dual.py research_campaigns/2026-10-03-core-witness/sharp_result/CW-01_residual_dual.json --qa-output /tmp/coopgt-rp-dual-checks.json
python3 -B -O structural_classification_2026-09-06/sharp_subsidy/tree_certificate.py
```

The symbolic checker verifies coefficient identities for the universal proof and semantic applications to retained matrices. The lower-family verifier independently constructs each coordinate-attaining original-core witness and subsidy allocation. The dual checker reconstructs scalar rows and coefficient rows independently of the numerical generator. See committed `SHARP_AGGREGATION_CHECKS.json`, `RP_DUAL_QA.json` and `../calibration/LOWER_FAMILY_SUMMARY.json` for exact scope.

The theorem is the written all-size derivation in `SHARP_ONE_THIRD.md`. Passing examples is not a proof of a universal statement. The enriched relaxation's h vector is not certified as actual H. Its sharp 211/714 value is distinct from CW-01's full-witness support optimum 5/18 and from its earlier diagnostic market's actual fixed-P objective 11/153.

Earlier full-witness checks and registry reproduction remain in `../README.md`. All six selected supports were fixed before optimization, and no additional computational supports were introduced. The numerical RP recovery script is preserved as `../src/recover_residual_dual.py`; rerunning discovery is unnecessary to verify the exact result and is outside the completed campaign's solve allowance.
