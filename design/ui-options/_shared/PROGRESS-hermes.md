# PROGRESS — UI options 01/02/03 (Hermes lead)

Card: build three complete UI directions (11 pages each + screenshots + README) for SewaCircle.
Scope: only 01-precision-dark, 02-premium-gradient, 03-field-notebook; never commit; never touch other folders.

## Setup (done)
- Read _shared/BRIEF.md, _shared/DIRECTIONS.md, sample-data.json, up_districts.json.
- Verified playwright + chromium work with the Hermes venv python; Google Fonts reachable.
- Wrote _shared/PAGE-SPEC.md — one shared content spec so all three directions tell the same story with the same
  verbatim numbers (10 tasks, 80 volunteers, task-01 READY, task-02 NOT READY, eval values, ledger, cards).
- Wrote _shared/districts-20.json — the 20 UP districts from docs/research/up_districts.json with real approximate
  coordinates; only 4 have drives in the sample.
- Wrote _shared/qa_check.py — automated QA at 1440 px: horizontal overflow, clipped text, tiny text, WCAG AA contrast,
  missing badges, broken internal links, JS errors, sparse blocks, overlapping absolute layers. Exit 1 on errors.

## Build (in progress)
| option | 11 pages | screenshots | QA clean | my visual review | README |
|---|---|---|---|---|---|
| 01-precision-dark | | | | | |
| 02-premium-gradient | | | | | |
| 03-field-notebook | | | | | |

## Notes
- Districts page: data has 20 district names (real geography) but drives in only 4. Options must show 20 nodes with
  4 populated and 16 honestly marked "no drives in this sample" — no invented counts.
- Visual review is done by opening every PNG with vision_analyze; anything below the bar goes back to the builder.
