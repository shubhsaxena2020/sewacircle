"""Capture every page of one UI option as full-page desktop PNGs.

Usage (from anywhere):  python capture.py <option-folder>
Reads <option-folder>/src/*.html, writes <option-folder>/screens/<same-name>.png at 1440 px wide, full page.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

folder = pathlib.Path(sys.argv[1]).resolve()
src, out = folder / "src", folder / "screens"
out.mkdir(exist_ok=True)
pages = sorted(src.glob("*.html"))
if not pages:
    sys.exit(f"no html pages in {src}")
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    for html in pages:
        page.goto(html.as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(out / (html.stem + ".png")), full_page=True)
        print("captured", html.stem)
    browser.close()
print("page errors:", errors or "none")
