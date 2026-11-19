"""Mechanical layout/accessibility QA for one UI option folder.

Usage:  python C:/Users/shubh/Projects/sewacircle/design/ui-options/_shared/qa_check.py <option-folder>

Checks every src/*.html at 1440 px wide and prints a compact report:
  * horizontal overflow at document level or from a leaking element
  * clipped / cut-off text (scrollHeight > clientHeight on overflow:hidden)
  * text smaller than 12 px, contrast below WCAG AA (4.5 / 3.0 for large)
  * missing required badges, broken internal links, duplicate H1s
  * JS errors, failed font loads, broken images, empty SVGs
Exit code 1 if any ERROR-level problem is found.
"""
import pathlib
import sys
import json

from playwright.sync_api import sync_playwright

folder = pathlib.Path(sys.argv[1]).resolve()
src = folder / "src"
pages = sorted(src.glob("*.html"))
if not pages:
    sys.exit(f"no html pages in {src}")

JS = r"""
() => {
  const out = {overflow: [], clipped: [], tiny: [], contrast: [], notes: []};
  const W = 1440;
  const docW = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);

  const visible = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const clippedBy = (el) => {
    let p = el.parentElement;
    while (p && p !== document.documentElement) {
      const cs = getComputedStyle(p);
      if (cs.overflow !== 'visible' || cs.overflowX !== 'visible') return true;
      p = p.parentElement;
    }
    return false;
  };
  const label = (el) => {
    const t = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
    const cls = (el.className && typeof el.className === 'string') ? '.' + el.className.trim().split(/\s+/).slice(0,2).join('.') : '';
    return el.tagName.toLowerCase() + cls + (t ? ' "' + t + '"' : '');
  };

  // 1. horizontal overflow
  if (docW > W + 1) {
    out.overflow.push('document scrollWidth=' + docW + ' (viewport ' + W + ')');
  }
  // 2. elements leaking past the right edge without a clipping ancestor
  const all = document.querySelectorAll('body *');
  const seen = new Set();
  for (const el of all) {
    if (!visible(el)) continue;
    if (['SCRIPT','STYLE','LINK','META','BR'].includes(el.tagName)) continue;
    const r = el.getBoundingClientRect();
    if ((r.right > W + 2 || r.left < -2) && !clippedBy(el)) {
      const k = label(el);
      if (!seen.has(k)) { seen.add(k); out.overflow.push('leaks: ' + k + ' rect=' + Math.round(r.left) + '..' + Math.round(r.right)); }
    }
  }
  // 3. clipped text
  for (const el of all) {
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    const txt = (el.textContent || '').trim();
    if (!txt || el.children.length > 0) continue;
    const hideY = cs.overflowY !== 'visible' || cs.overflow !== 'visible';
    const hideX = cs.overflowX !== 'visible' || cs.overflow !== 'visible';
    if (hideY && el.scrollHeight > el.clientHeight + 3 && cs.height !== 'auto') {
      out.clipped.push(label(el) + ' h=' + el.clientHeight + ' need=' + el.scrollHeight);
    } else if (hideX && el.scrollWidth > el.clientWidth + 3 && cs.whiteSpace === 'nowrap') {
      out.clipped.push(label(el) + ' w=' + el.clientWidth + ' need=' + el.scrollWidth);
    }
  }
  // 4. tiny text
  const tinySeen = new Set();
  for (const el of all) {
    const txt = (el.textContent || '').trim();
    if (!txt || el.children.length > 0) continue;
    if (!visible(el)) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 11.5) {
      const k = fs.toFixed(1) + 'px ' + label(el);
      if (!tinySeen.has(k)) { tinySeen.add(k); out.tiny.push(k); }
    }
  }
  // 5. contrast (best effort: nearest opaque ancestor background)
  const parse = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    if (p.length < 3) return null;
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  };
  const lum = ({r, g, b}) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const blend = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1
  });
  const bgOf = (el) => {
    let p = el;
    let acc = null;
    while (p) {
      const cs = getComputedStyle(p);
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0.01) {
        acc = acc ? blend(acc, c) : c;
        if (c.a >= 0.99) return acc;
      }
      p = p.parentElement;
    }
    return acc || {r: 255, g: 255, b: 255, a: 1};
  };
  const seenC = new Set();
  for (const el of all) {
    const txt = (el.textContent || '').trim();
    if (!txt || el.children.length > 0) continue;
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    const fgRaw = parse(cs.color);
    if (!fgRaw) continue;
    const bg = bgOf(el);
    const fg = fgRaw.a < 0.99 ? blend(fgRaw, bg) : fgRaw;
    const L1 = lum(fg), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const fs = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 600;
    const large = fs >= 24 || (fs >= 18.66 && bold);
    const need = large ? 3.0 : 4.5;
    if (ratio < need - 0.05) {
      const k = ratio.toFixed(2) + ' need ' + need + ' ' + label(el);
      if (!seenC.has(k)) { seenC.add(k); out.contrast.push(k); }
    }
  }
  // 6. structural checks
  const bodyText = document.body.innerText;
  out.notes.push('title=' + (document.title || '(none)'));
  out.notes.push('lang=' + (document.documentElement.lang || '(none)'));
  const h1s = document.querySelectorAll('h1').length;
  out.notes.push('h1=' + h1s);
  out.notes.push('height=' + document.documentElement.scrollHeight);
  out.notes.push('synthetic_badge=' + /synthetic data/i.test(bodyText));
  out.notes.push('affiliation_line=' + /not affiliated with my bharat/i.test(bodyText));
  out.notes.push('devanagari=' + /[\u0900-\u097F]/.test(bodyText));
  const imgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0);
  if (imgs.length) out.notes.push('broken_images=' + imgs.map(i => i.getAttribute('src')).join(','));
  const emptySvg = [...document.querySelectorAll('svg')].filter(s => s.children.length === 0);
  if (emptySvg.length) out.notes.push('empty_svg=' + emptySvg.length);
  // 7. sparse blocks (big box, almost no text) hint at an empty / unfinished area
  out.sparse = [];
  const blocks = [...document.querySelectorAll('main > *, main section, section')];
  for (const b of blocks) {
    if (!visible(b)) continue;
    const r = b.getBoundingClientRect();
    const t = (b.innerText || '').trim().length;
    if (r.height > 420 && t < 160) out.sparse.push(label(b) + ' h=' + Math.round(r.height) + ' text=' + t);
  }
  // 8. overlapping text (absolute/fixed layers colliding with other text)
  out.overlap = [];
  const abs = [...document.querySelectorAll('body *')].filter(el => {
    const p = getComputedStyle(el).position;
    return (p === 'absolute' || p === 'fixed') && visible(el) && (el.innerText || '').trim().length > 0;
  });
  const texts = [...document.querySelectorAll('body *')].filter(el => {
    return el.children.length === 0 && visible(el) && (el.textContent || '').trim().length > 1;
  });
  for (const a of abs) {
    const ra = a.getBoundingClientRect();
    for (const t of texts) {
      if (a.contains(t) || t.contains(a)) continue;
      const rt = t.getBoundingClientRect();
      const ix = Math.min(ra.right, rt.right) - Math.max(ra.left, rt.left);
      const iy = Math.min(ra.bottom, rt.bottom) - Math.max(ra.top, rt.top);
      if (ix > 12 && iy > 10) {
        out.overlap.push(label(a).slice(0, 40) + ' over ' + label(t).slice(0, 40));
        break;
      }
    }
  }
  out.overlap = [...new Set(out.overlap)].slice(0, 8);
  const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
  out.notes.push('links=' + JSON.stringify(links));
  const fonts = [...document.fonts].filter(f => f.status === 'error').map(f => f.family);
  if (fonts.length) out.notes.push('font_errors=' + fonts.join(','));
  return out;
}
"""

bad = 0
report = {}
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
    for html in pages:
        errs.clear()
        page.goto(html.as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(600)
        r = page.evaluate(JS)
        r["errors"] = list(errs)
        report[html.name] = r
    browser.close()

for name, r in report.items():
    problems = []
    problems += [("ERROR", x) for x in r["overflow"]]
    problems += [("ERROR", "clipped text: " + x) for x in r["clipped"]]
    problems += [("WARN", "tiny text: " + x) for x in r["tiny"]]
    problems += [("WARN", "contrast: " + x) for x in r["contrast"]]
    problems += [("WARN", "sparse block: " + x) for x in r.get("sparse", [])]
    problems += [("WARN", "overlap: " + x) for x in r.get("overlap", [])]
    problems += [("ERROR", "js: " + x) for x in r["errors"]]
    notes = dict(n.split("=", 1) for n in r["notes"] if "=" in n)
    if notes.get("synthetic_badge") != "true":
        problems.append(("ERROR", "missing 'Synthetic data' badge"))
    if notes.get("affiliation_line") != "true":
        problems.append(("ERROR", "missing 'Not affiliated with MY Bharat' line"))
    if notes.get("h1") not in ("1",):
        problems.append(("WARN", "h1 count = " + notes.get("h1", "?")))
    # broken internal links
    links = json.loads(notes.get("links", "[]"))
    for l in links:
        if l.startswith(("http", "#", "mailto:", "tel:")):
            continue
        target = (src / l.split("#")[0]).resolve()
        if not target.exists():
            problems.append(("ERROR", f"broken link {l}"))
    for k in ("font_errors", "broken_images", "empty_svg"):
        if k in notes:
            problems.append(("ERROR", f"{k}: {notes[k]}"))
    nerr = sum(1 for lvl, _ in problems if lvl == "ERROR")
    bad += nerr
    print(f"\n=== {name}  (height {notes.get('height','?')}px, {nerr} errors, "
          f"{len(problems)-nerr} warnings)")
    for lvl, msg in problems[:40]:
        print(f"  [{lvl}] {msg}")
    if len(problems) > 40:
        print(f"  ... {len(problems)-40} more")

print("\nTOTAL ERRORS:", bad)
sys.exit(1 if bad else 0)
