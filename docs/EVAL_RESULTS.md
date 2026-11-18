# Roster evaluation results (real output)

All data is SYNTHETIC. Reproduce from `backend/`:

```
python -m eval.harness --out ../docs/eval_report.json
```

Raw machine-readable output: `docs/eval_report.json`. Pasted stdout of that exact command, unedited:

```
SewaCircle roster evaluation (SYNTHETIC) - synthetic data seed 7 (80 volunteers, 10 tasks); ortools 9.15.6755; CP-SAT 1 worker, seed 7, sequential tiers; random_feasible mean of 20 seeds; paired task bootstrap n=1000 seed 7
method                                     role_coverage                    robustness             repeat_pick_share                 exposure_gini
cp_sat                       0.917 [  0.767,  1.000]      0.760 [  0.500,  0.960]      0.230 [  0.083,  0.410]      0.470 [  0.381,  0.548]   
nearest_skill                0.917 [  0.767,  1.000]      0.153 [  0.017,  0.370]      0.403 [  0.215,  0.593]      0.504 [  0.403,  0.587]   
manual_greedy                0.917 [  0.767,  1.000]      0.760 [  0.500,  0.960]      0.427 [  0.248,  0.610]      0.508 [  0.406,  0.591]   
random_feasible              0.904 [  0.748,  0.996]      0.219 [  0.026,  0.439]      0.301 [  0.145,  0.474]      0.487 [  0.390,  0.565]   
delta_vs_nearest_skill       0.000 [  0.000,  0.000]      0.607 [  0.323,  0.867]     -0.173 [ -0.273, -0.070]     -0.034 [ -0.059, -0.015]   
delta_vs_manual_greedy       0.000 [  0.000,  0.000]      0.000 [  0.000,  0.000]     -0.197 [ -0.310, -0.093]     -0.038 [ -0.069, -0.015]   
delta_vs_random_feasible     0.013 [  0.000,  0.031]      0.541 [  0.282,  0.809]     -0.071 [ -0.113, -0.030]     -0.016 [ -0.035, -0.004]   

per task (cov / robustness / repeat / gini):
  task-01  cp_sat 1.00/1.00/0.00/0.61  neares 1.00/0.17/0.17/0.67  manual 1.00/1.00/0.33/0.67  random 1.00/0.78/0.08/0.62
  task-02  cp_sat 1.00/1.00/0.17/0.42  neares 1.00/0.17/0.17/0.52  manual 1.00/1.00/0.17/0.56  random 1.00/0.25/0.14/0.50
  task-03  cp_sat 1.00/1.00/0.75/0.17  neares 1.00/1.00/0.75/0.17  manual 1.00/1.00/0.75/0.17  random 1.00/0.90/0.74/0.17
  task-04  cp_sat 0.33/0.00/0.00/0.50  neares 0.33/0.00/0.00/0.50  manual 0.33/0.00/0.00/0.50  random 0.33/0.00/0.00/0.50
  task-05  cp_sat 0.83/0.00/0.60/0.37  neares 0.83/0.00/0.80/0.38  manual 0.83/0.00/0.80/0.38  random 0.74/0.00/0.65/0.37
  task-06  cp_sat 1.00/1.00/0.25/0.55  neares 1.00/0.00/0.75/0.61  manual 1.00/1.00/0.75/0.61  random 1.00/0.00/0.44/0.58
  task-07  cp_sat 1.00/0.60/0.20/0.51  neares 1.00/0.20/0.40/0.52  manual 1.00/0.60/0.40/0.52  random 0.96/0.26/0.32/0.52
  task-08  cp_sat 1.00/1.00/0.00/0.51  neares 1.00/0.00/0.00/0.58  manual 1.00/1.00/0.40/0.59  random 1.00/0.00/0.11/0.55
  task-09  cp_sat 1.00/1.00/0.33/0.42  neares 1.00/0.00/0.67/0.44  manual 1.00/1.00/0.67/0.44  random 1.00/0.00/0.48/0.41
  task-10  cp_sat 1.00/1.00/0.00/0.64  neares 1.00/0.00/0.33/0.64  manual 1.00/1.00/0.00/0.64  random 1.00/0.00/0.05/0.64

MISSES (6):
  - task-02: cp_sat repeat_pick_share 0.17 worse than random_feasible 0.14
  - task-03: cp_sat repeat_pick_share 0.75 worse than random_feasible 0.74
  - task-04: cp_sat could not fill every must slot (coverage 0.33); no eligible people
  - task-05: cp_sat could not fill every must slot (coverage 0.83); no eligible people
  - task-07: cp_sat dropout robustness only 0.60 (too few eligible standby people)
  - task-09: cp_sat exposure_gini 0.42 worse than random_feasible 0.41

wrote ../docs/eval_report.json
```

## How to read this honestly
- n = 10 synthetic tasks, 80 synthetic volunteers. Intervals are paired task-bootstrap ranges, descriptive only.
- **Role coverage is tied** with the nearest-skill and manual-greedy baselines. On this data every method fills
  what can be filled; two tasks (task-04, task-05) are deliberately short of eligible people and every method fails them.
- **Dropout robustness** is the main gain over nearest-skill (+0.61) and random (+0.54). It **ties manual-greedy**,
  because our manual-greedy baseline is generous: it simulates a careful organiser who keeps one backup per role.
- **Fairness**: versus the careful organiser (manual-greedy), SewaCircle reaches the same coverage and robustness while
  picking far fewer heavily-used volunteers (repeat-pick share -0.20, interval [-0.31, -0.09]) and lowering exposure
  inequality slightly (Gini -0.04).
- **Misses** are listed by the harness itself (6), including two tasks where a random roster was marginally fairer.
- These are proxy measures on synthetic data, not field impact.
