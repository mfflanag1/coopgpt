# Native Astra xhigh independent QA

Reviewer: /root/support_inventory, native subagent explicitly requested gpt-6-astra xhigh. Verdict: approve for integration subject to parent verification; no mathematical soundness defect found. This is not completed CLI-runner QA.

Confirmed all raw triples checked, dummy witness on perfect P, shared pair union, residual signs and box correction, exact primal lower meaning and matching primal/dual optimum semantics, fail-closed malformed data under optimized Python. Two documentation corrections: m2 AB-only calibration C-target ideals are zero (J=-1/3), and parser deliberately accepts only signed integers/fractions/plain decimals.

Reviewer reports 38/38 tests; 380 manually constructed residual-dual certificates over19supports; all380 perturbed claimed upper bounds rejected; a corruption preserving diagonal budgets but violating a non-diagonal team rejected. Parent reran38tests and independently checked all34 retained frontier certificates (2678055 full-team checks) and five generator outputs. The additional380-case script was retained as src/checker_adversarial_qa.py and the parent reran it under python -O:380cases accepted,380corruptions rejected, and the non-diagonal violation rejected.

Unchanged candidate hashes:
- check_certificate.py 2f6ab9a7703e7835686b499ec0060ebd65dfbab9d3773ea50b80fdb78c4fa9fc
- test_check_certificate.py 183aac3acdb48029ed84a186273754d62fc6f5c66d01204ef61d2226db85c516

CLI-runner QA requested Astra but failed HTTP400 because installed CLI needs an upgrade. No code was reviewed by that failed call. The native subagent supplied opposite-model review instead. The routing runner requires its own successful QA record to adjudicate, so no accepted routing score was fabricated.
