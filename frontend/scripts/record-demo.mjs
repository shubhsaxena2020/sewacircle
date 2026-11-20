import { chromium } from 'playwright'
const out = process.env.DEMO_OUT ?? '../docs/demo'
const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173'
const gpu = process.env.DEMO_GPU === '1'
const b = await chromium.launch(gpu ? { headless: process.env.DEMO_HEADED !== '1', args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-gpu-rasterization'] } : {})
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, recordVideo: { dir: out, size: { width: 1440, height: 900 } } })
const page = await ctx.newPage()
const wait = ms => page.waitForTimeout(ms)
const caption = async text => page.evaluate(t => {
  let el = document.getElementById('demo-cap')
  if (!el) { el = document.createElement('div'); el.id = 'demo-cap'; el.style.cssText = 'position:fixed;right:48px;bottom:40px;z-index:99999;max-width:560px;padding:12px 22px;background:rgba(36,30,24,.88);color:#fff6e2;font:600 22px/1.35 system-ui,sans-serif;border-radius:6px;text-align:right;pointer-events:none;transition:opacity .3s'; document.body.appendChild(el) }
  el.textContent = t; el.style.opacity = t ? '1' : '0'
}, text)
const shot = async name => { await page.evaluate(() => { const c = document.getElementById('demo-cap'); if (c) c.style.visibility = 'hidden' }); await page.screenshot({ path: `${out}/${name}.png` }); await page.evaluate(() => { const c = document.getElementById('demo-cap'); if (c) c.style.visibility = 'visible' }) }
const glide = async (id, ms = 2600) => {
  const target = await page.locator('#' + id).evaluate(n => n.getBoundingClientRect().top + scrollY)
  const start = await page.evaluate(() => scrollY); const steps = Math.max(1, Math.round(ms / 40))
  for (let i = 1; i <= steps; i++) { const t = i / steps; const e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; await page.evaluate(y => scrollTo(0, y), start + (target - start) * e); await wait(40) }
}
await page.request.post(`${base}/api/demo/reset`, { headers: { 'X-Demo-Role': 'organiser' } })
await page.goto(base, { waitUntil: 'load' }); await page.getByRole('heading', { level: 1 }).waitFor(); await wait(1200)
await page.mouse.move(700, 450); await wait(1800)
await caption('SevaSetu - willing volunteers are here. Can this drive run?'); await wait(4200)
await glide('interest'); await caption('Each light is a synthetic volunteer who opted in to this drive.'); await wait(4000)
await glide('brief'); await caption('AI reads a Hindi brief and proposes roles, each tied to the phrase it came from.'); await wait(1200)
const ph = page.locator('.phrase').first(); if (await ph.count()) await ph.click(); await wait(3200)
await glide('crew'); await caption('Plan the crew: a solver picks from people who opted in - live API, synthetic data.'); await wait(1500)
await page.getByRole('button', { name: 'Plan the crew' }).click(); await page.locator('#crew .meta').waitFor({ timeout: 30000 }); await wait(4200); await shot('screen2_story_crew')
await glide('bench'); await caption('Every essential seat has a standby with the right skills.'); await wait(3800)
await glide('verdict'); await caption('READY means every role has cover, including host-checked safety roles.'); await wait(4000); await shot('screen3_story_ready')
await glide('gap'); await page.locator('#gap .recruit li').first().waitFor({ timeout: 30000 }); await caption('A drive that cannot run says NOT READY - and writes the recruit request.'); await wait(4200); await shot('screen3c_story_gap')
await glide('dropout'); await caption('Someone drops out. The plan re-runs live - and honestly says what is still missing.'); await wait(1500)
await page.locator('#dropout .btn').click(); await page.locator('#dropout .drop-result').waitFor({ timeout: 30000 }); await wait(4500); await shot('screen4_story_dropout_not_ready')
await glide('evidence'); await caption('After the drive: draft contribution cards, checked against attendance; a host decides.'); await wait(3500)
await glide('numbers'); await caption('Measured on 10 synthetic drives: READY on 7 of 10 vs 1 of 10 for nearest-skill matching.'); await wait(4500); await shot('screen6_story_numbers')
await glide('districts'); await caption('Every drive keeps its own live status.'); await wait(3000)
await glide('try', 1800); await caption(''); await wait(1200)
// Youth side: profile -> top projects with an explained % match
await page.goto(`${base}/youth`, { waitUntil: 'load' }); await wait(1500)
await caption('The youth side: a young person tells SevaSetu what they can do and when they are free.'); await wait(2500)
await page.getByRole('button', { name: 'Fill a sample profile' }).click(); await wait(2500)
await page.getByRole('button', { name: 'Show my top projects' }).click(); await page.locator('.match-card').first().waitFor({ timeout: 20000 }); await wait(800)
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })); await wait(800)
await caption('Eligibility first, then a % match with reasons: skills, time, distance and interests.'); await wait(4500); await shot('screen0_youth_matches')
await page.evaluate(() => window.scrollBy({ top: 520, behavior: 'smooth' })); await wait(1500)
await caption('Projects that are too far or 18+ only are listed with the reason, never silently hidden.'); await wait(3500)
await page.locator('.match-card .btn').first().click().catch(() => {}); await wait(1200)
await page.goto(`${base}/console`, { waitUntil: 'domcontentloaded' }); await wait(1200)
await caption('The organiser console: the same steps, for real work.'); await wait(1500)
await page.getByRole('button', { name: 'Hindi sample' }).click(); await wait(1200)
await page.getByRole('button', { name: 'Extract roles' }).click()
let hindiOk = true
try { await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 30000 }) } catch { hindiOk = false }
if (!hindiOk) { await page.getByRole('button', { name: 'English sample' }).click(); await page.getByRole('button', { name: 'Extract roles' }).click(); await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 30000 }) }
await caption('AI drafts the roles; a person confirms or edits them.'); await wait(3500); await shot('screen1_console_roles')
await page.getByRole('button', { name: 'Build crew', exact: true }).click(); await page.locator('.crew-board').waitFor({ timeout: 30000 })
await caption('The solver decides: crew, standby, reasons for every pick.'); await wait(4000); await shot('screen2b_console_crew')
await page.goto(`${base}/console`, { waitUntil: 'domcontentloaded' }); await page.getByRole('combobox', { name: 'Choose a drive' }).selectOption('task-05'); await page.getByRole('button', { name: 'English sample' }).click(); await page.getByRole('button', { name: 'Extract roles' }).click(); await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 30000 })
await page.getByRole('button', { name: 'Build crew', exact: true }).click(); await page.locator('.crew-board').waitFor({ timeout: 30000 })
await caption('A drive that cannot run gets NOT READY plus exactly who to recruit.'); await wait(4000); await shot('screen3b_console_not_ready')
const nav = page.getByRole('navigation', { name: 'Organiser console' })
await nav.getByRole('button', { name: /Evidence/ }).click(); await wait(800)
await page.getByLabel('Host notes').fill('The team completed its water and hygiene setup. One paper attendance entry needs review: 8 hours claimed, 5 recorded.')
for (const f of await page.locator('.attendance-row input[type="number"]').all()) await f.fill('5')
await page.getByRole('button', { name: 'Draft contribution cards' }).click(); await page.locator('.contribution-card').first().waitFor({ timeout: 30000 })
await caption('Contribution cards are drafts until a host confirms them. Nothing is auto-verified.'); await wait(4000); await shot('screen5_console_evidence')
await nav.getByRole('button', { name: /Evaluation/ }).click(); await wait(1500)
await caption('Every number comes from a reproducible evaluation on synthetic data.'); await wait(4000); await shot('screen6b_console_evaluation')
await page.getByRole('button', { name: 'हिन्दी' }).click(); await wait(1200)
await caption('Full Hindi interface.'); await wait(3000); await shot('screen7_console_hindi')
await caption('SevaSetu - synthetic data, not affiliated with MY Bharat or any government body.'); await wait(3500)
console.log(JSON.stringify({ hindiExtraction: hindiOk }))
await ctx.close(); await b.close()
