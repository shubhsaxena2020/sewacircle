# SewaCircle - how does the CP-SAT roster planner scale? (Kaggle CPU notebook)
# Declared grid: pool sizes 20/80/200/500 volunteers (realistic synthetic generator, seeds 7 and 8) x the 10 labelled
# synthetic tasks, using the SAME eligibility/metric code as the app. Compares cp_sat with nearest-skill and
# manual-greedy on coverage, dropout robustness and solve time. Synthetic data only; this is scale sensitivity, not field data.
import json, statistics, subprocess, sys, time

subprocess.run(["git", "clone", "--depth", "1", "https://github.com/shubhsaxena2020/sewacircle", "/kaggle/working/sewacircle"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pydantic>=2.6", "ortools==9.15.6755", "httpx"], check=True)
sys.path.insert(0, "/kaggle/working/sewacircle/backend")

from app.schemas import RosterOptions
from app.solver import api
from app.data.synth import make_tasks, make_volunteers

rows = []
for n in (20, 80, 200, 500):
    for seed in (7, 8):
        vols = make_volunteers(n, seed)
        for task in make_tasks(seed):
            t0 = time.perf_counter()
            cp = api.build_roster(task, vols, RosterOptions(seed=seed, time_limit_s=30))
            wall = time.perf_counter() - t0
            ns = api.baseline_nearest_skill(task, vols)
            mg = api.baseline_manual_greedy(task, vols)
            rows.append({"n": n, "seed": seed, "task": task.id, "status": cp.metrics.solver_status, "wall_s": round(wall, 3),
                         "cp_cov": cp.metrics.role_coverage, "cp_rob": cp.metrics.robustness,
                         "ns_cov": ns.metrics.role_coverage, "ns_rob": ns.metrics.robustness,
                         "mg_cov": mg.metrics.role_coverage, "mg_rob": mg.metrics.robustness})
            print(rows[-1], flush=True)

summary = {}
for n in (20, 80, 200, 500):
    r = [x for x in rows if x["n"] == n]
    summary[n] = {k: round(statistics.fmean(x[k] for x in r), 3) for k in ("wall_s", "cp_cov", "cp_rob", "ns_cov", "ns_rob", "mg_cov", "mg_rob")}
    summary[n]["max_wall_s"] = max(x["wall_s"] for x in r)
    summary[n]["optimal"] = sum(x["status"] == "OPTIMAL" for x in r)
    print("SUMMARY", n, summary[n], flush=True)
json.dump({"rows": rows, "summary": summary}, open("/kaggle/working/results.json", "w"), indent=1)
print("DONE")
