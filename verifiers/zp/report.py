"""Emit census7/zp/REPORT.txt and summary.json."""
from __future__ import annotations

import collections
import glob
import json

BASE = "/private/tmp/claude-501/-Users-maxf/f0530d27-effc-4967-b154-48a9b65ca708/scratchpad/census7/zp"

zp = collections.Counter()
pa = collections.Counter()
tot = collections.Counter()
games = collections.Counter()
for f in glob.glob(f"{BASE}/s2_*.json") + glob.glob(f"{BASE}/sc_*.json"):
    d = json.load(open(f))
    tot[d["n"]] += d["h2_slack"]
    games[d["n"]] += d["games"]
    for k, v in d["zp"].items():
        zp[k] += v
    for k, v in d["partition"].items():
        if "split" in k:
            pa[k] += v
hp = collections.Counter()
hg = hb = 0
for f in glob.glob(f"{BASE}/hp*.json"):
    d = json.load(open(f))["stat"]
    hg += d["games"]
    hb += d["h2_slack"]
    for k, v in d["splits"].items():
        hp[k] += v

out = []
W = out.append
W("=" * 78)
W("TASK #21 - THE ZERO-PAYOFF RESIDUE AT n=7")
W("=" * 78)
W("")
W("Two items were open from the n=7 census:")
W("  (1) the j != e branch of the zero-payoff impossibility;")
W("  (2) the two resisting admissible types, poorer-part profiles (4,0) and")
W("      (2,2), to be realized or refuted.")
W("")
W("-" * 78)
W("VERDICTS")
W("-" * 78)
W("")
W("  (1) j != e branch                    : PROVED  (Theorem 8, PROOF.txt)")
W("  (2) profile (4,0)  [type A]          : REFUTED - proved impossible")
W("      profile (2,2)  [type B]          : OPEN - reduced to one conjecture")
W("")
W("The j != e branch is closed not by analysing that case directly but by")
W("showing it cannot recur: each occurrence deletes a null player and drops m")
W("by one, while the phase theorem keeps m >= 3, so the descent is well")
W("founded and must terminate in the j = e case, which is contradictory when")
W("q = 0.  That same descent is what refutes profile (4,0).")
W("")
W("-" * 78)
W("WHAT WAS PROVED (full statements and proofs in PROOF.txt)")
W("-" * 78)
W("")
W("  Lemma 1  a ZP configuration forces phi_e = 0            [k-fold RO]")
W("  Lemma 2  min phi = 0 forces a single player to be zero on the whole core,")
W("           and that player is null                        [convexity]")
W("  Lemma 3  deleting a null player preserves exactness, the core, Lmin,")
W("           tightness and the slack of every boundary avoiding it")
W("  Lemma 4  the converse: suspending a null player over a PART configuration")
W("           creates a ZP configuration of the same profile")
W("  Thm 5    no PART(p,0): it would make a rich singleton tight, forcing")
W("           phi_g = v({g}) = 0 against strictness of the boundary")
W("  Thm 6    every ZP(p,q) descends to PART(p,q) or to ZP(p-1,q) / ZP(p,q-1)")
W("           with one fewer poorer player")
W("  Cor 7    no ZP configuration at all when m = 3          [phase theorem]")
W("  Thm 8    no ZP(p,0) at any m   ===>  the n=7 profile (4,0) is IMPOSSIBLE")
W("  Cor 9    every ZP question is a PARTITION question one level down")
W("")
W("Machine verification: Lemmas 2 and 3 were checked exhaustively on n=5")
W("games - 116/116 games with min phi = 0 had a common zero core player, it")
W("was null in every case, and deletion preserved exactness, Lmin, every")
W("tight set and every slack boundary.  Lemma 1 was checked on all 32")
W("harvested ZP witnesses: phi_e = 0 in 32/32.")
W("")
W("-" * 78)
W("THE RESIDUE: ONE CONJECTURE")
W("-" * 78)
W("")
W("  CONJECTURE.  PART(p,q) is realizable exactly when p,q >= 1 and")
W("               max(p,q) >= 3.")
W("")
W("  The half p,q >= 1 is Theorem 5.  The half max(p,q) >= 3 is open and is")
W("  the entire remaining content of the ZP question, because")
W("")
W("    ZP(2,2) at m=5 -> PART(2,2) at m=4              [max = 2]")
W("                   or ZP(1,2)/ZP(2,1) at m=4")
W("                        -> PART(1,2)/PART(2,1) at m=3   [max = 2]")
W("                        or ZP at m=3                    [Corollary 7]")
W("")
W("  so the conjecture implies type B is impossible and closes the residue.")
W("")
W("EVIDENCE (h=2 slack boundaries in exact games; exact arithmetic):")
W("")
W(f"  random scan       : {sum(games.values())} games, "
  f"{sum(tot.values())} h=2 slack boundaries")
for n in sorted(tot):
    W(f"      n={n} (m={n-2}): {games[n]} games, {tot[n]} boundaries")
W(f"  targeted scan     : {hg} games in the frozen-total slice, {hb} boundaries")
W("")
W("  ZP configurations observed:")
if zp:
    for k, v in sorted(zp.items()):
        W(f"      {k:28s} {v}")
else:
    W("      none")
W("  PARTITION configurations observed:")
for k, v in sorted(pa.items()):
    W(f"      {k:28s} {v}")
W("  targeted-slice partition configurations:")
for k, v in sorted(hp.items()):
    W(f"      {k:28s} {v}")
W("")
W("  Read off: no configuration of either kind at m=3; at m=4 the splits")
W("  (1,3) and (3,1) occur and (2,2) never does; at m=5 every split with both")
W("  parts nonempty occurs.  And the ZP profiles realized at m=5 are exactly")
W("  (1,3) and (3,1) - precisely the PART splits at m=4, as Corollary 9")
W("  predicts.  That agreement is the strongest single check on the whole")
W("  descent picture.")
W("")
W("-" * 78)
W("THE FINITE-FEASIBILITY ROUTE: WHERE IT STOPS")
W("-" * 78)
W("")
W("On n <= 6 the cone of exact games is cut out by the catalogue:")
W("      v exact  <=>  sum_{S proper} lambda_S v(S) <= r v(N)")
W("for every permuted min-semi-balanced system - 280 inequalities at n=5 and")
W("7,006 at n=6.  Validated in exactcone.py: 200 exact games violate none and")
W("20 non-exact games each violate one at n=5; 60 exact games violate none at")
W("n=6 (the converse direction is not run at n=6 because deciding exactness by")
W("definition needs exponential vertex enumeration).")
W("")
W("So everything in the PART(p,q) question is exactly encodable EXCEPT")
W("phi = Lmin.  Three relaxations were tried: the plain cone LP; plus leximin")
W("stage 1 as a quantified linear condition; plus the one-packet theorem as a")
W("disjunction over all delta>0 packet certificates.  All three are")
W("SATISFIABLE for PART(1,2) at n=5, and every model fails the reality check -")
W("rebuilding the game from the model's v and recomputing Lmin gives a")
W("different leximin point at which H is not even a strict boundary.  The")
W("obstruction is the multi-stage leximin condition, not exactness and not the")
W("packet structure.  A decisive LP needs the full leximin encoding: fix the")
W("stratification of the poorer side and add one quantified pinning condition")
W("per stage.  That is the recommended continuation.")
W("")
W("-" * 78)
W("WHY THE THRESHOLD IS PLAUSIBLY 3")
W("-" * 78)
W("")
W("If a PART game were the direct sum of its two sides, each side would be an")
W("exact game in which its rich player is uniquely richest and {f} is slack,")
W("so the phase theorem at h=1 would force at least m_min(1) = 4 poorer")
W("players per side.  PART games are not direct sums - their core is strictly")
W("inside the product of the two side cores - which is why the observed")
W("threshold is 3 rather than 4.  Quantifying that gap is the natural route to")
W("a proof of the conjecture.")
W("")

open(f"{BASE}/REPORT.txt", "w").write("\n".join(out) + "\n")

summary = {
    "task": 21,
    "item1_j_neq_e_branch": {
        "verdict": "PROVED",
        "how": "well-founded descent: each occurrence deletes a null player, "
               "m drops by one, phase theorem keeps m >= 3, so the branch "
               "cannot recur; terminal case j = e is contradictory when q = 0",
        "theorem": "PROOF.txt Theorem 8"},
    "item2_profile_4_0": {
        "verdict": "REFUTED (proved impossible)",
        "theorem": "PROOF.txt Theorem 8"},
    "item2_profile_2_2": {
        "verdict": "OPEN",
        "reduced_to": "Conjecture 10: PART(p,q) realizable iff p,q>=1 and "
                      "max(p,q)>=3; the half p,q>=1 is proved (Theorem 5)",
        "implies": "the conjecture implies profile (2,2) is impossible"},
    "new_lemmas": ["zero payoff (phi_e = 0)", "common zero / null player",
                   "null-player deletion", "null-player suspension",
                   "rich-singleton exclusion", "ZP-to-PART descent",
                   "no ZP at m=3"],
    "machine_verification": {
        "lemma2_lemma3_n5_games": 116, "lemma2_lemma3_failures": 0,
        "lemma1_zp_witnesses": 32, "lemma1_failures": 0,
        "exact_cone_n5_inequalities": 280, "exact_cone_n6_inequalities": 7006},
    "evidence": {
        "random_games": sum(games.values()),
        "random_h2_slack_boundaries": sum(tot.values()),
        "targeted_games": hg, "targeted_h2_slack_boundaries": hb,
        "zp_observed": dict(zp), "partition_observed": dict(pa),
        "partition_observed_targeted": dict(hp)},
    "artifacts": ["PROOF.txt", "REPORT.txt", "summary.json", "scan.py",
                  "scan2.py", "hunt_partition.py", "verify_lemma.py",
                  "exactcone.py", "decide.py"],
}
json.dump(summary, open(f"{BASE}/summary.json", "w"), indent=1)
print("\n".join(out))
