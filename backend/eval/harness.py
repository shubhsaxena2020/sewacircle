"""Roster evaluation harness. Run from backend/:  python -m eval.harness --out eval_report.json

Methods: cp_sat (SewaCircle), nearest_skill, manual_greedy (with one backup per role), random_feasible (mean over 20 seeds).
Metrics come from ONE shared function (solver.metrics.compute_metrics) for every method.
Uncertainty: paired bootstrap over TASKS (the same resampled task ids for every method), 1000 resamples, seed 7.
With n = 10 synthetic tasks the intervals are descriptive, not a significance test. Misses are listed honestly.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from importlib.metadata import version

from app.schemas import EvalReport, EvalRow, RosterOptions, TaskSpec, Volunteer
from app.solver import api

METRICS = ("role_coverage", "robustness", "repeat_pick_share", "exposure_gini")
LOWER_IS_BETTER = {"repeat_pick_share", "exposure_gini"}
RF_SEEDS = list(range(1, 21))
BOOT_N, BOOT_SEED = 1000, 7


def _rows_for_task(task: TaskSpec, vols: list[Volunteer]) -> list[EvalRow]:
    out: list[EvalRow] = []
    for method, roster in (("cp_sat", api.build_roster(task, vols, RosterOptions(seed=7))),
                           ("nearest_skill", api.baseline_nearest_skill(task, vols)),
                           ("manual_greedy", api.baseline_manual_greedy(task, vols))):
        m = roster.metrics
        out.append(EvalRow(task_id=task.id, method=method, role_coverage=m.role_coverage, robustness=m.robustness,  # type: ignore[arg-type]
                           repeat_pick_share=m.repeat_pick_share, exposure_gini=m.exposure_gini, solve_ms=m.solve_ms))
    rf = [api.baseline_random_feasible(task, vols, s).metrics for s in RF_SEEDS]
    out.append(EvalRow(task_id=task.id, method="random_feasible",
                       **{k: statistics.fmean(getattr(m, k) for m in rf) for k in METRICS},
                       solve_ms=int(statistics.fmean(m.solve_ms for m in rf))))
    return out


def _ci(values_by_task: dict[str, float], task_ids: list[str], rng: random.Random) -> list[float]:
    means = []
    for _ in range(BOOT_N):
        sample = [rng.choice(task_ids) for _ in task_ids]
        means.append(statistics.fmean(values_by_task[t] for t in sample))
    means.sort()
    return [round(means[int(0.025 * BOOT_N)], 4), round(means[int(0.975 * BOOT_N) - 1], 4)]


def run_eval(volunteers: list[Volunteer], tasks: list[TaskSpec]) -> EvalReport:
    rows = [r for t in tasks for r in _rows_for_task(t, volunteers)]
    ids = [t.id for t in tasks]
    methods = ["cp_sat", "nearest_skill", "manual_greedy", "random_feasible"]
    table = {(r.method, r.task_id): r for r in rows}
    summary = {m: {k: round(statistics.fmean(getattr(table[(m, t)], k) for t in ids), 4) for k in METRICS} for m in methods}
    ci95: dict[str, dict[str, list[float]]] = {}
    for m in methods:
        ci95[m] = {}
        for k in METRICS:
            ci95[m][k] = _ci({t: getattr(table[(m, t)], k) for t in ids}, ids, random.Random(BOOT_SEED))
    # paired deltas: cp_sat minus each baseline, same resampled tasks (seeded identically per metric)
    for b in methods[1:]:
        key = f"delta_vs_{b}"
        summary[key] = {}
        ci95[key] = {}
        for k in METRICS:
            d = {t: getattr(table[("cp_sat", t)], k) - getattr(table[(b, t)], k) for t in ids}
            summary[key][k] = round(statistics.fmean(d.values()), 4)
            ci95[key][k] = _ci(d, ids, random.Random(BOOT_SEED))
    misses: list[str] = []
    for t in ids:
        cp = table[("cp_sat", t)]
        for b in methods[1:]:
            base = table[(b, t)]
            for k in METRICS:
                worse = getattr(cp, k) > getattr(base, k) + 1e-9 if k in LOWER_IS_BETTER else getattr(cp, k) < getattr(base, k) - 1e-9
                if worse:
                    misses.append(f"{t}: cp_sat {k} {getattr(cp, k):.2f} worse than {b} {getattr(base, k):.2f}")
        if cp.role_coverage < 1.0:
            misses.append(f"{t}: cp_sat could not fill every must slot (coverage {cp.role_coverage:.2f}); no eligible people")
        if cp.robustness < 1.0 and cp.role_coverage == 1.0:
            misses.append(f"{t}: cp_sat dropout robustness only {cp.robustness:.2f} (too few eligible standby people)")
    gen = (f"synthetic data seed 7 ({len(volunteers)} volunteers, {len(tasks)} tasks); ortools {version('ortools')}; "
           f"CP-SAT 1 worker, seed 7, sequential tiers; random_feasible mean of {len(RF_SEEDS)} seeds; "
           f"paired task bootstrap n={BOOT_N} seed {BOOT_SEED}")
    return EvalReport(n_tasks=len(tasks), n_volunteers=len(volunteers), rows=rows, summary=summary, ci95=ci95,
                      misses=misses, generated_by=gen, synthetic=True)


def _print(rep: EvalReport) -> None:
    print(f"SewaCircle roster evaluation (SYNTHETIC) - {rep.generated_by}")
    print(f"{'method':<26}" + "".join(f"{k:>30}" for k in METRICS))
    for m, vals in rep.summary.items():
        cells = "".join(f"{vals[k]:>8.3f} [{rep.ci95[m][k][0]:>7.3f},{rep.ci95[m][k][1]:>7.3f}]   " for k in METRICS)
        print(f"{m:<26}{cells}")
    print("\nper task (cov / robustness / repeat / gini):")
    for t in sorted({r.task_id for r in rep.rows}):
        cells = "  ".join(f"{r.method[:6]} {r.role_coverage:.2f}/{r.robustness:.2f}/{r.repeat_pick_share:.2f}/{r.exposure_gini:.2f}"
                          for r in rep.rows if r.task_id == t)
        print(f"  {t}  {cells}")
    print(f"\nMISSES ({len(rep.misses)}):")
    for m in rep.misses:
        print("  - " + m)


def main(argv: list[str] | None = None) -> int:
    from app.data.synth import make_tasks, make_volunteers
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    rep = run_eval(make_volunteers(), make_tasks())
    _print(rep)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rep.model_dump(mode="json"), f, ensure_ascii=False, indent=1)
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
