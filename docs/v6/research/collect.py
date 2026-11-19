# Collect Awwwards Sites of the Day (title, tags, real URL) politely: list pages then each detail page, 1.2 s apart.
import re, html, json, time, urllib.request, sys
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142 Safari/537.36"
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
want = int(sys.argv[1]) if len(sys.argv) > 1 else 170
items, seen = [], set()
for page in range(1, 12):
    h = get(f"https://www.awwwards.com/websites/sites_of_the_day/?page={page}")
    for raw in re.findall(r'data-collectable-model-value="([^"]+)"', h):
        d = json.loads(html.unescape(raw))
        if d["slug"] in seen: continue
        seen.add(d["slug"]); items.append({"slug": d["slug"], "title": d["title"], "tags": d.get("tags", []), "date": d.get("createdAt")})
    print("page", page, len(items), flush=True); time.sleep(1.2)
    if len(items) >= want: break
for it in items[:want]:
    try:
        h = get("https://www.awwwards.com/sites/" + it["slug"])
        m = re.search(r'rel="nofollow noopener"\s+href="(https?://[^"]+)"[^>]*>\s*Visit Site', h, re.S) or re.search(r'href="(https?://[^"]+)"\s+class="button[^"]*"[^>]*data-controller="visit-count"', h, re.S)
        it["url"] = m.group(1) if m else None
    except Exception as e:
        it["url"] = None; it["err"] = str(e)[:80]
    time.sleep(1.2)
json.dump(items[:want], open("sites/awwwards_sotd.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("done", sum(1 for i in items[:want] if i.get("url")), "with url")
