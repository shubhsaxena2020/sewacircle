Work in C:\Users\shubh\Projects\sewacircle-backend (git worktree, branch backend-ideas). Edit only backend\ files. Do not push.
Do not touch any other folder. Write every line yourself; do not copy code from elsewhere.

TASK (one feature, keep it small): add GET /api/geo/tree to the FastAPI app in backend\app\main.py.
- Read docs\research\up_districts.json (20 Uttar Pradesh districts with coordinates and source URL fields) and the BLOCKS dict in
  backend\app\data\synth.py. Return ONE nested JSON tree: {"state": "Uttar Pradesh", "source_url": ..., "districts": [{"name",
  "lat", "lon", "source_record_id", "blocks": [names]}]}. Carry the source URL fields through unchanged.
- Build it once and cache it (functools.lru_cache). Send an ETag header (sha256 of the JSON body, quoted). If the request has
  If-None-Match equal to that ETag, return 304 with no body.
- Add backend\tests\test_geo_tree.py: shape (20 districts, each with lat/lon/blocks), cache returns the same object, ETag present,
  304 on matching If-None-Match.
- Run from backend\: ..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q   All tests must pass (692 existed before).
- Commit with message "geo tree endpoint with ETag" and print the final pytest line.
