"""RESTART SWEEP: spend one 600s budget per configuration as THREE 200s
attempts under different z3 random seeds, instead of one 600s attempt.

WHY.  The paired experiment (stageC_fresh_paired.json) showed that three
configurations the gate DECIDED in 8.7-20.4s came back UNKNOWN at 600s under an
identical encoding, and that a configuration capped at 600s twice resolved in
56.5s on a third attempt.  A 1.5x contention factor cannot turn 8.7s into 600s.
That signature -- the same instance landing anywhere from seconds to beyond the
cap -- is a HEAVY-TAILED runtime distribution, and the standard exploit for it
is restarts: k short attempts beat one long attempt when the distribution has
enough mass near zero.

This measures whether that exploit works here, AT EQUAL TOTAL BUDGET, so it is
a fair comparison against the 600s single attempt already on record for each of
these configurations.

Stops a configuration as soon as any attempt returns a verdict.
HALT-ON-SAT is absolute.

usage: python3 seedsweep.py <jobs.json> <tag> <workers> <cap_ms_each> <seeds...>
writes seedsweep_<tag>.json
"""
import json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
jobs = json.load(open(sys.argv[1]))
tag = sys.argv[2]
W = int(sys.argv[3])
cap = int(sys.argv[4])
seeds = [int(x) for x in sys.argv[5:]] or [1, 2, 3]
OUT = os.path.join(HERE, f"seedsweep_{tag}.json")

lock = threading.Lock()
done = []
halted = threading.Event()
t_start = time.time()


def run(job):
    attempts = []
    verdict, total = "unknown", 0.0
    for sd in seeds:
        if halted.is_set():
            break
        t0 = time.time()
        try:
            p = subprocess.run(
                ["python3", os.path.join(HERE, "solveseed.py"),
                 json.dumps({k: job[k] for k in ("lmin", "lmax", "tbl")}),
                 str(cap), str(sd)],
                capture_output=True, text=True, cwd=HERE,
                timeout=cap / 1000.0 + 180)
            rec = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception as e:
            rec = {"res": "ERROR", "s": round(time.time() - t0, 1),
                   "seed": sd, "error": f"{type(e).__name__}: {e}"[:300]}
        attempts.append({"seed": sd, "res": rec["res"], "s": rec["s"]})
        total += rec["s"]
        if rec["res"] in ("sat", "unsat"):
            verdict = rec["res"]
            if rec["res"] == "sat":
                halted.set()
                with open(os.path.join(HERE, "HALT_SAT.txt"), "w") as f:
                    f.write(json.dumps(rec, indent=1))
                print(f"*** HALT *** SAT at 2/3: {job}", flush=True)
            break
    out = {"lmin": job["lmin"], "lmax": job["lmax"], "tbl": job["tbl"],
           "k": len(job["lmin"]), "verdict": verdict,
           "seconds_spent": round(total, 1), "attempts": attempts,
           "prior_single_attempt": job.get("prior", None)}
    with lock:
        done.append(out)
        json.dump(done, open(OUT, "w"), indent=1)
        n = len(done)
    print(f"  [{tag}] {n}/{len(jobs)} {verdict} after {len(attempts)} attempt(s), "
          f"{total:.1f}s total  k={out['k']} lmin={job['lmin']} lmax={job['lmax']}",
          flush=True)


with ThreadPoolExecutor(max_workers=W) as ex:
    list(ex.map(run, jobs))

res = [d["verdict"] for d in done]
print(f"SEEDSWEEP {tag} DONE: decided {sum(1 for r in res if r != 'unknown')}"
      f" of {len(res)}  in {time.time()-t_start:.1f}s", flush=True)
