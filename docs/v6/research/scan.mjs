// Scan one batch of sites: hero + 4 scroll frames at 1440x900, plus a technical/design signature per site.
import { chromium } from 'playwright'
import fs from 'node:fs'
const [, , listFile, from = '0', to = '999'] = process.argv
const list = JSON.parse(fs.readFileSync(listFile, 'utf8')).slice(+from, +to)
fs.mkdirSync('shots', { recursive: true })
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] })
const results = []
for (const site of list) {
  if (!site.url) continue
  const id = (site.slug || site.title).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40)
  const out = { id, title: site.title, url: site.url, tags: site.tags || [] }
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0 Safari/537.36' })
  const page = await ctx.newPage()
  try {
    await page.goto(site.url, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(7000)
    await page.mouse.move(720, 450); await page.mouse.click(5, 5).catch(() => {})
    await page.screenshot({ path: `shots/${id}-0.jpg`, type: 'jpeg', quality: 70 })
    const H = await page.evaluate(() => document.documentElement.scrollHeight)
    for (let i = 1; i <= 4; i++) {
      for (let k = 0; k < 6; k++) { await page.mouse.wheel(0, 300); await page.waitForTimeout(120) }
      await page.waitForTimeout(900)
      await page.screenshot({ path: `shots/${id}-${i}.jpg`, type: 'jpeg', quality: 70 })
    }
    Object.assign(out, await page.evaluate(() => {
      const els = [...document.querySelectorAll('h1,h2,h3,p,a,button,span')].slice(0, 600)
      const sizes = els.map(e => parseFloat(getComputedStyle(e).fontSize)).filter(Boolean)
      const fams = new Set(els.slice(0, 200).map(e => getComputedStyle(e).fontFamily.split(',')[0].replace(/["']/g, '').trim()))
      return {
        pageHeight: document.documentElement.scrollHeight,
        canvases: document.querySelectorAll('canvas').length,
        webgl: [...document.querySelectorAll('canvas')].some(c => { try { return !!(c.getContext('webgl2') || c.getContext('webgl')) } catch { return true } }),
        videos: document.querySelectorAll('video').length,
        three: !!(window.THREE || window.__THREE__), gsap: !!window.gsap, lenis: !!(window.lenis || document.documentElement.classList.contains('lenis')),
        maxFont: Math.max(0, ...sizes), fonts: [...fams].slice(0, 6),
        bodyBg: getComputedStyle(document.body).backgroundColor, sections: document.querySelectorAll('section').length,
        h1: document.querySelector('h1')?.innerText.slice(0, 120) || '', navLinks: document.querySelectorAll('nav a').length,
      }
    }))
    out.ok = true
  } catch (e) { out.ok = false; out.err = String(e).slice(0, 160) }
  results.push(out); console.log(out.ok ? 'ok  ' : 'FAIL', id)
  await ctx.close()
}
await browser.close()
fs.writeFileSync(`scan-${listFile.replace(/\W+/g, '_')}-${from}.json`, JSON.stringify(results, null, 1))
