# Roster evaluation results (real output)

All data is SYNTHETIC. Reproduce from `backend/`:

```
python -m eval.harness --out ../docs/eval_report.json
```

Raw machine-readable output: `docs/eval_report.json`. Pasted stdout of that exact command, unedited:

```
SewaCircle roster evaluation (SYNTHETIC) - synthetic data seed 7 (80 volunteers, 10 tasks); ortools 9.15.6755; CP-SAT 1 worker, seed 7, sequential tiers; random_feasible mean of 20 seeds; paired task bootstrap n=1000 seed 7
method                                     role_coverage                    robustness             repeat_pick_share                 exposure_gini                         ready
cp_sat                       0.917 [  0.767,  1.000]      0.760 [  0.500,  0.960]      0.230 [  0.083,  0.410]      0.468 [  0.376,  0.546]      0.700 [  0.400,  0.900]   
nearest_skill                0.917 [  0.767,  1.000]      0.153 [  0.017,  0.370]      0.403 [  0.215,  0.593]      0.504 [  0.403,  0.588]      0.100 [  0.000,  0.300]   
manual_greedy                0.917 [  0.767,  1.000]      0.760 [  0.500,  0.960]      0.427 [  0.248,  0.610]      0.508 [  0.406,  0.591]      0.700 [  0.400,  0.900]   
random_feasible              0.914 [  0.767,  0.998]      0.218 [  0.025,  0.438]      0.307 [  0.150,  0.482]      0.486 [  0.389,  0.566]      0.150 [  0.010,  0.360]   
delta_vs_nearest_skill       0.000 [  0.000,  0.000]      0.607 [  0.323,  0.867]     -0.173 [ -0.273, -0.070]     -0.037 [ -0.061, -0.017]      0.600 [  0.300,  0.900]   
delta_vs_manual_greedy       0.000 [  0.000,  0.000]      0.000 [  0.000,  0.000]     -0.197 [ -0.310, -0.093]     -0.040 [ -0.071, -0.017]      0.000 [  0.000,  0.000]   
delta_vs_random_feasible     0.003 [  0.000,  0.007]      0.542 [  0.282,  0.810]     -0.077 [ -0.115, -0.036]     -0.018 [ -0.036, -0.005]      0.550 [  0.280,  0.840]   

per task (cov / robustness / repeat / gini / ready):
  task-01  cp_sat 1.00/1.00/0.00/0.61/1  neares 1.00/0.17/0.17/0.67/0  manual 1.00/1.00/0.33/0.67/1  random 1.00/0.78/0.11/0.63/0
  task-02  cp_sat 1.00/1.00/0.17/0.42/1  neares 1.00/0.17/0.17/0.52/0  manual 1.00/1.00/0.17/0.56/1  random 1.00/0.25/0.14/0.50/0
  task-03  cp_sat 1.00/1.00/0.75/0.17/1  neares 1.00/1.00/0.75/0.17/1  manual 1.00/1.00/0.75/0.17/1  random 1.00/0.90/0.74/0.17/1
  task-04  cp_sat 0.33/0.00/0.00/0.50/0  neares 0.33/0.00/0.00/0.50/0  manual 0.33/0.00/0.00/0.50/0  random 0.33/0.00/0.00/0.50/0
  task-05  cp_sat 0.83/0.00/0.60/0.37/0  neares 0.83/0.00/0.80/0.38/0  manual 0.83/0.00/0.80/0.38/0  random 0.83/0.00/0.68/0.37/0
  task-06  cp_sat 1.00/1.00/0.25/0.55/1  neares 1.00/0.00/0.75/0.61/0  manual 1.00/1.00/0.75/0.61/1  random 1.00/0.00/0.44/0.58/0
  task-07  cp_sat 1.00/0.60/0.20/0.48/0  neares 1.00/0.20/0.40/0.53/0  manual 1.00/0.60/0.40/0.53/0  random 0.97/0.25/0.32/0.51/0
  task-08  cp_sat 1.00/1.00/0.00/0.51/1  neares 1.00/0.00/0.00/0.58/0  manual 1.00/1.00/0.40/0.59/1  random 1.00/0.00/0.11/0.55/0
  task-09  cp_sat 1.00/1.00/0.33/0.42/1  neares 1.00/0.00/0.67/0.44/0  manual 1.00/1.00/0.67/0.44/1  random 1.00/0.00/0.48/0.41/0
  task-10  cp_sat 1.00/1.00/0.00/0.64/1  neares 1.00/0.00/0.33/0.64/0  manual 1.00/1.00/0.00/0.64/1  random 1.00/0.00/0.05/0.64/0

MISSES (7):
  - task-02: cp_sat repeat_pick_share 0.17 worse than random_feasible 0.14
  - task-03: cp_sat repeat_pick_share 0.75 worse than random_feasible 0.74
  - task-04: cp_sat could not fill every must slot (coverage 0.33); no eligible people
  - task-05: cp_sat exposure_gini 0.37 worse than random_feasible 0.37
  - task-05: cp_sat could not fill every must slot (coverage 0.83); no eligible people
  - task-07: cp_sat dropout robustness only 0.60 (too few eligible standby people)
  - task-09: cp_sat exposure_gini 0.42 worse than random_feasible 0.41

wrote ../docs/eval_report.json
```

## How to read this honestly
- n = 10 synthetic tasks, 80 synthetic volunteers. Intervals are paired task-bootstrap ranges, descriptive only.
- **Ready** is the Ready Crew verdict: every must slot filled AND every critical slot has an eligible standby
  (no single point of failure) AND no unresolved role. It is 1 or 0 per task; the column is the share of tasks.
- **Ready drives: 7/10 for SewaCircle vs 1/10 nearest-skill and 1.5/10 random.** It **ties the careful-organiser
  baseline (manual-greedy, 7/10)**, which by design keeps one backup per role. The three not-ready tasks fail for
  every method: task-04 and task-05 have too few eligible people, task-07 has too few eligible standbys. On those the
  product's job is the recruit request it emits (who is missing, which skill, which slot), not a better roster.
- **Role coverage is tied** with every baseline: on this data every method fills what can be filled.
- **Dropout robustness** is the main gain over nearest-skill (+0.61) and random (+0.54); it ties manual-greedy.
- **Fairness**: versus the careful organiser, SewaCircle reaches the same coverage, robustness and ready rate while
  picking far fewer heavily-used volunteers (repeat-pick share -0.20, interval [-0.31, -0.09]) and slightly lower
  exposure inequality (Gini -0.04). So the honest claim is: "as ready as a careful organiser, automatically, and fairer".
- **Misses** are listed by the harness itself (7), including tasks where a random roster was marginally fairer.
- These are proxy measures on synthetic data, not field impact.
