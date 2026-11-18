Work in C:\Users\shubh\Projects\sewacircle-backend (branch backend-ideas). Edit only backend\app\main.py and
backend\tests\test_geo_tree.py. Do not push. Another agent (Hermes) is editing main.py in this worktree at the same time: make
small, surgical edits only inside your geo-tree block and re-read the file right before editing.

REVIEW FINDINGS on your commit 652ad56 (geo tree endpoint). Fix all four:
1. geo_tree(request: Request = None) has a "request is None" branch returning a different shape. FastAPI always passes Request;
   remove the default and that branch. Remove the unused alias build_geo_tree.
2. If-None-Match: compare per RFC 9110. Split the header on commas, trim each, accept "*" or an exact match of the quoted ETag or
   W/ plus the quoted ETag. Do NOT strip quotes. Add tests for a list value ("a", <etag>) and for "*".
3. Only 4 of the 20 districts have synthetic blocks (BLOCKS in synth.py). Add "blocks_available": true/false per district and a
   top-level "blocks_note": "Blocks are listed only for the 4 districts used by the synthetic demo data." so an empty list is not
   misread as a district with no blocks. Test that exactly the BLOCKS keys have blocks_available true.
4. Carry through coordinate_caveat and retrieved_date from up_districts.json at the top level (tests check presence).
Run from backend\: ..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q   all must pass. Commit "geo tree: review fixes".
Print the final pytest line.
