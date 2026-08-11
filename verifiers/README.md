# Verifiers — proof dependencies and bug audits for paper4 and paper5

Archived from the 2026-08-06/07 campaign.  Scripts import the shared toolkit
in `lib/` (exact rational arithmetic; z3 for LRA); run them from their own
directory with `lib` on `sys.path`, without Python `-O`.  The catalogue CSVs
in `lib/cat/` are the published Studený–Kratochvíl data.

Two tiers, matching the papers' status tables.

## Proof dependencies (the papers' "finite exact check" results)

| Result | Driver |
|---|---|
| paper5 Thm (one-coalition certificates, n=5): μ=λ and M=ν | `a3check/` — `cone.py` (facet description, validated both directions), `coververt.py` (2287 cover vertices), `a3lp.py` + `allverts.py` (1142 classes per side, all infeasible), `controls.py` (drop-the-cone and known-failure controls) |
| paper5 Thm + Cor (CFG starvation bound f({j}) ≥ T/8) | `o2/` — `pinvert.py` (354 pinning-dual vertices), `o2main.py` (31 × 354 programs, all infeasible), `pincontrol.py`, `ablate.py`/`minimal.py` (minimal hypothesis set), `extract.py` (the T/16 essentiality models), `core.py` (unsat cores) |
| paper4 Thm (h=2 split threshold, m≤4) and Thm (h=3 collections) | `selection/` — `m5.py` (42/216/950 abstract packets, the two m=5 split facets), `facet_test.py` (h=3 breakdown 2/31/10/12), `enum_packets.py`, `starproof.py` (34 star types re-classified) |
| paper4 §7 large-core statements for the four example games | `large_core_qe.py` (quantifier-elimination, no enumeration) |
| paper5 Thm (unconditional configuration bound): rich-branch μ ≥ T/6 | `s5full/jrich.py` (31 × 354 programs), `s5full/checks2.py` (controls), `s5full/arith*.py` (the game-free 3/2 ceiling), `s5full/REPORT.txt` (incl. the ceiling second-stage derivation sketch) |
| paper5 Thms (five-player supremum s(5)=1/2; the (4,1) regime ≤ 1/3) | `s5close/` — `PROOF.txt` (L1–L4, Proposition S, T0/T0-BIS/T1/T2), `REPORT.txt`, pipeline 1 (`arith22.py`, `closecfg.py`/`closecfg2.py` + `batch*.py`, `stages.py`, `pinvert.py`), pipeline 2 (`closecfg3.py`, `farkas.py` with the re-derived leximax mirror), `coverage.py` (2961-configuration audit), `compare3.py` (pipeline agreement), the full control suite (`poscontrol.py`, `completeness*.py`, `crosscheck.py`, `audit22.py`), `lead_verify_s5.py` (the lead's independent falsification sweep) |
| PART(p,q) characterization (realizable ⟺ p,q≥1, p+q≥4; Conjecture 10 refuted; n=7 ZP(2,2) realized) | `part/` — `PROOF.txt` (Theorems A/B/D/E/F, block rigidity, padding), `decisive.py` (48 UNSAT at m=3 + audited witnesses), `families.py` (independent CEGAR cross-check), `controls.py` (L±, X±, P+), `audit_witness.py`, `lead_verify_part22.py` (the lead's independent witness check) |
| paper5 Thm thm:cfg (f({j}) ≥ T/8 in CFG) — NOW A HAND THEOREM; drivers here are guards, not premises | `cfg_hand/` — `PROOF_A3.txt` (the one-page proof: key lemma + dualized pinning + exact-tightness pivot + load count; no A3 hard direction, no catalogue), `verify_hand_cfg.py` (case-exhaustiveness, sharpness at μ=T/8, load-system UNSAT), `reality2.py` (the extremal game realizes the predicted failing shape) |
| paper4 Thm (five-player containment W ⊆ Ĥ ⊆ S) and the C-C-left refutation | `cc/` — `PROOF.txt` (Lemma L, D+/C+, window, master inequalities, closed forms), `d2_lab.py` (the 32-shape decision procedure, targets left/right/leftmin/rightmin/control), `d3_lemmaL.py`/`d16_crosscheck.py` (certificate controls + cross-validation vs `part/` Theorem B), `d11_audit.py` (counterexample audit), `d5_ablate.py`, `d6_closed.py` (93 closed-form regions), `lead_verify_cc.py` (the lead's independent counterexample check) |

## Bug audits and computational evidence (not proof dependencies)

| Content | Driver |
|---|---|
| paper4 §7 examples, C-C evidence, exact-partition search | `monotonicity/` — `refute.py`/`refute2.py` (the two retiring examples), `survive.py` (the 1041-record tally), `inexact_cc.py` (localization non-correlation), `hunt7.py`/`family_ep.py` (exact-partition search), `ce5.py`/`ce7.py` (inexactness examples), `family.py` (the 197-member family) |
| paper5 enumeration table, extremal class, searches | `divergence/` — `exhaust2n.py`/`exhaust3.py` (complete 2- and 3-generator enumerations), `twogen.py` (duality/floor checks), `cspace.py` (seeded core-space climbing), `seesaw.py`/`structure.py` (extremal-class profiling), `scan2block.py`, `simplex.py`/`lexsimplex.py` (independent exact solvers) |
| paper5 clipped effective-bipartition and dispersion-price program | `divergence/audit_effective_bipartition.py` (the finite controls which the later counterexample escaped), `divergence/audit_overcover_dispersion_dual.py` (independent rational primal/dual replay), `divergence/verify_n7_effective_bipartition_counterexample.py` (solver-free staged identities plus independent exact checks refuting CEB without challenging the main target), `divergence/audit_spectral_label_currency.py` (exact top-selection/threshold-label currency decomposition and canonical saturation audit), `divergence/verify_staged_interval_deficit_controls.py` (exact staged availability of clipped rectangles), `divergence/verify_n7_neutral_rectangle_control.py` (neutral-endpoint hostile control), `divergence/verify_rooted_hinge_projection.py` (independently formulated exact witness elimination/cutting plane, pair-floor budget, singleton and rooted-pair min-semi-balanced lifts, and exhaustive exact-LP facet filter), `divergence/verify_rooted_hinge_decompositions_z3.py` (independent Z3 replay of every decomposition and pair-lift facet count), `divergence/audit_overcover_pair_lift_coupling.py` (root-specific deleted-load versus common strict-leader over-cover optima, pair-lift incidence/slack checks, rooted-pair gauge quotient, and coefficient-two two-facet decomposition), `divergence/verify_overcover_pair_lift_coupling_z3.py` (independent exact-LRA replay of those optima/infeasibilities and the two new indecomposability tests), `divergence/audit_surplus_absorption.py` (common-support deficiency primal/dual, noncommon pair-lift slack defect, null-padded negative control, and best-single-anchor optimization), and `divergence/verify_surplus_absorption_z3.py` (independent exact-LRA replay of fixed-control deficiency and best-anchor optima); saved outputs are adjacent JSON files |
| paper5 mixed-support gluing | `divergence/verify_mixed_packet_gluing.py` — exact mixed-colour rooted incidence packet and fixed-branch Farkas coefficient identities; output is `divergence/mixed_packet_gluing.json` |
| n=5/n=6/n=7 packet censuses and the campaign theorem files | `records/` — census reports, `THEOREMS.txt`, `FINAL.txt`, `S5PROOF.txt` |
| ZP descent: profile (4,0) impossibility at n=7 (proved); Conjecture 10 (since refuted — see `part/`) | `zp/` — `PROOF.txt` (the null-player descent chain L1–T8, with the 2026-08-08 resolution note), `REPORT.txt`, harvest and validation scripts |

Earlier verifiers for the phase-diagram core remain in `../src` with saved
outputs in `../results`, as described in the papers' reproducibility notes.
