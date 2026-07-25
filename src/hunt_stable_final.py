"""Consolidated stable-core non-ES hunt over assignment games.

Tests ONLY dominant-diagonal (= stable core, Solymosi-Raghavan) matrices that
are NOT doubly-dominant (= NOT large, NOT exact) -- the sole regime that could
yield a non-ES game, since large core => ES. Pure matrix filters, no LP in the
hot loop. Any non-ES => stable-core non-ES witness, resolving the second half
of Dietzenbacher's open question negatively.
"""
import random, sys, json
from fractions import Fraction as F
from assignment import assignment_game
from eshunt import is_ES
from hunt_stablecore import (gen_dominant, dominant_diagonal, doubly_dominant,
                             certify_witness)
from sweep_stablecore import gen_hub_dominant

LOG = "/Users/maxf/projects/counterexample-hunt/coopgames/results/agent_stable.txt"


def run():
    log = open(LOG, "w")
    def emit(s):
        print(s, flush=True); log.write(s + "\n"); log.flush()
    emit("STABLE-CORE non-ES hunt (dominant-diagonal, NOT doubly-dominant = strictly stable, non-large)")
    configs = [
        ("3x3", gen_dominant, 3, 10, 4000),
        ("3x3wide", gen_dominant, 3, 25, 4000),
        ("3x3hub", gen_hub_dominant, 3, 15, 4000),
        ("4x4", gen_dominant, 4, 8, 1500),
        ("4x4hub", gen_hub_dominant, 4, 10, 1500),
    ]
    grand_tested = 0
    for name, gen, m, dmax, trials in configs:
        tested = skipped_large = 0
        for seed in range(5):
            rng = random.Random(seed)
            for t in range(trials):
                A = gen(rng, m, dmax)
                if not dominant_diagonal(A):
                    continue
                if doubly_dominant(A):
                    skipped_large += 1
                    continue
                g = assignment_game(A)
                es, gamma = is_ES(g)
                tested += 1
                if not es:
                    emit(f"[NON-ES WITNESS] {name} seed={seed} t={t} A={A} "
                         f"claims={[str(x) for x in gamma]} vN={g.v[g.N]}")
                    cert = certify_witness(A)
                    emit("CERTIFICATION: " + json.dumps(cert))
                    with open("/Users/maxf/projects/counterexample-hunt/coopgames/results/WITNESS_stablecore_not_ES.json", "w") as wf:
                        json.dump(cert, wf, indent=1)
                    log.close(); return A
        grand_tested += tested
        emit(f"{name}: strictly-stable-non-large tested={tested} "
             f"(skipped large={skipped_large}) -> ALL ES")
    emit(f"DONE. Total strictly-stable-non-large games tested: {grand_tested}. "
         f"NO stable-core non-ES assignment game found.")
    log.close()
    return None


if __name__ == "__main__":
    run()
