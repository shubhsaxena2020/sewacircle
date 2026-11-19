// Capture every story chapter (and the main pages) at 1440x900 for review.
import { chromium } from 'playwright'
import fs from 'node:fs'
const base = process.env.BASE_URL ?? 'http://127.0.0.1:5181'
const out = process.env.OUT ?? '../docs/screens/v6'
fs.mkdirSync(out, { recursive: true })
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] })
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()
const errors = []
page.on('pageerror', e => errors.push(String(e)))
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })
await page.request.post('http://127.0.0.1:8000/api/demo/reset', { headers: { 'X-Demo-Role': 'organiser' } })
await page.goto(base, { waitUntil: 'load' }); await page.waitForTimeout(3500)
const chapters = ['intro', 'interest', 'brief', 'crew', 'bench', 'verdict', 'gap', 'dropout', 'evidence', 'numbers', 'districts', 'try']
for (const [i, c] of chapters.entries()) {
  await page.evaluate(id => document.getElementById(id).scrollIntoView({ block: 'center' }), c)
  if (c === 'crew') { await page.waitForTimeout(800); await page.getByRole('button', { name: 'Plan the crew' }).click(); await page.waitForTimeout(2600) }
  else if (c === 'brief') { await page.waitForTimeout(1200); const p = page.locator('.phrase').first(); if (await p.count()) await p.click() }
  else if (c === 'dropout') { await page.waitForTimeout(1200); await page.locator('#dropout .btn').click(); await page.waitForTimeout(3000) }
  else if (c === 'evidence') { await page.waitForTimeout(800); await page.getByRole('button', { name: 'Verify the log' }).click() }
  await page.waitForTimeout(2600)
  await page.screenshot({ path: `${out}/story-${String(i).padStart(2, '0')}-${c}.png` })
}
for (const p of ['console', 'districts', 'volunteer', 'method']) { await page.goto(`${base}/${p}`, { waitUntil: 'load' }); await page.waitForTimeout(1500); await page.screenshot({ path: `${out}/page-${p}.png` }) }
fs.writeFileSync(`${out}/errors.json`, JSON.stringify(errors, null, 1))
console.log('errors', errors.length, errors.slice(0, 5))
await b.close()
