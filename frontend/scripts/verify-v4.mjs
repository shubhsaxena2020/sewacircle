import AxeBuilder from '@axe-core/playwright'
import { chromium } from '@playwright/test'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173'
const out = path.resolve(process.env.SCREENSHOT_DIR ?? path.join('..', 'docs', 'screens', 'v5', '..', 'v6'))
await mkdir(out, { recursive: true })
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: base })
const page = await context.newPage()
await page.addInitScript(() => { if (!localStorage.getItem('sewa-role')) localStorage.setItem('sewa-role', 'organiser') })
const pageErrors = []
const api403 = []
const apiRequests = []
const axeResults = []
const e2e = []
page.on('pageerror', error => pageErrors.push(error.message))
page.on('response', response => { if (response.status() === 403) api403.push(response.url()) })
page.on('request', request => { if (request.url().includes('/api/roster')) apiRequests.push(`${request.method()} ${new URL(request.url()).pathname}`) })
const routePages = [
  ['story', '/'], ['console', '/console'], ['volunteer', '/volunteer'],
  ['districts', '/districts'], ['method', '/method'],
]
const capture = async name => page.screenshot({ path: path.join(out, `${name}.png`), animations: 'disabled' })

try {
  const resetResponse = await page.request.post(`${base}/api/demo/reset`, { headers: { 'X-Demo-Role': 'organiser' } })
  if (!resetResponse.ok()) throw new Error(`Could not reset the local synthetic demo state: HTTP ${resetResponse.status()}`)
  e2e.push({ demoReset: `HTTP ${resetResponse.status()} before the verification workflow` })
  // v4 story: one ring, live API at the crew, verdict, gap and dropout moments.
  await page.goto(base, { waitUntil: 'load' })
  await page.getByRole('heading', { level: 1 }).waitFor()
  await page.waitForTimeout(2500)
  await capture('page-story')
  const at = async id => { await page.evaluate(c => document.getElementById(c).scrollIntoView({ block: 'center' }), id); await page.waitForTimeout(1800) }
  await at('crew')
  await page.getByRole('button', { name: 'Plan the crew' }).click()
  await page.locator('#crew .meta').waitFor({ timeout: 30000 })
  const planned = await page.locator('#crew .meta').innerText()
  const seatLabels = await page.locator('.seat-label.s-filled').count()
  if (!seatLabels) throw new Error('No filled seats rendered on the ring after planning')
  await page.waitForTimeout(1500); await capture('chapter-03-crew')
  await at('verdict'); await page.waitForTimeout(800)
  const verdict = await page.locator('#verdict .verdict').innerText()
  await capture('chapter-05-verdict')
  await at('gap'); await page.locator('#gap .recruit li').first().waitFor({ timeout: 30000 })
  const gapVerdict = await page.locator('#gap .verdict').innerText()
  if (!gapVerdict.includes('NOT READY')) throw new Error(`Gap drive should be NOT READY, got ${gapVerdict}`)
  await page.waitForTimeout(800); await capture('chapter-06-gap')
  await at('dropout')
  await page.locator('#dropout .btn').click()
  await page.locator('#dropout .drop-result').waitFor({ timeout: 30000 })
  const dropText = await page.locator('#dropout .drop-result').innerText()
  await page.waitForTimeout(1500); await capture('chapter-07-dropout')
  await at('numbers')
  await page.waitForFunction(() => document.querySelectorAll('#numbers [data-final="true"]').length >= 2, null, { timeout: 8000 })
  const counters = await page.locator('#numbers .num > span').allTextContents()
  if (counters[0] !== '70%' || counters[1] !== '23%') throw new Error(`Counters did not settle on 70% / 23%: ${counters.join(', ')}`)
  await capture('chapter-09-numbers')
  e2e.push({ story: { planned, seatLabels, verdict, gapVerdict, dropout: dropText.replace(/\s+/g, ' '), counters } })
  await page.getByRole('button', { name: 'हिन्दी' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'hi')
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(1200)
  await capture('page-story-hi')
  await page.getByRole('button', { name: 'English' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'en')
  // Live organiser journey, including a card revision cycle and a public share link.
  await page.goto(`${base}/console`, { waitUntil: 'domcontentloaded' })
  await page.getByRole('button', { name: 'Hindi sample' }).click()
  const hindiSample = await page.locator('textarea').first().inputValue()
  if (!/[\u0900-\u097F]/.test(hindiSample)) throw new Error('Hindi console sample was not Hindi text')
  await page.getByRole('button', { name: 'Hinglish sample' }).click()
  const hinglishSample = await page.locator('textarea').first().inputValue()
  if (!hinglishSample.includes('Saturday subah')) throw new Error('Hinglish sample was not loaded')
  const hiTasks = page.waitForResponse(response => response.url().includes('/api/tasks?lang=hi'))
  await page.getByRole('button', { name: 'हिन्दी' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'hi')
  await hiTasks
  const hindiConsoleHeading = await page.getByRole('heading', { level: 1 }).innerText()
  await page.getByRole('button', { name: 'English' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'en')
  await page.getByRole('button', { name: 'English sample' }).click()
  await page.getByRole('button', { name: 'Extract roles' }).click()
  await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 30000 })
  const extractedRoleCount = await page.locator('.role-editor').count()
  await page.getByRole('button', { name: 'Build crew', exact: true }).click()
  await page.locator('.crew-board').waitFor({ timeout: 30000 })
  const readyText = (await page.locator('.crew-view').innerText()).includes('READY')
  await page.getByRole('button', { name: 'Create and copy public share link' }).click()
  const shareLink = page.locator('.share-panel a[href*="/drive/"]')
  await shareLink.waitFor({ timeout: 15000 })
  const sharePath = new URL(await shareLink.getAttribute('href')).pathname
  await page.goto(`${base}${sharePath}`)
  await page.getByRole('heading', { level: 1 }).waitFor()
  await page.waitForTimeout(300)
  await capture('page-share')
  const shareText = await page.locator('.share-page').innerText()
  if (!shareText.includes('Roles in this drive')) throw new Error('Public share summary did not render roles')
  e2e.push({ samples: 'Hindi and Hinglish text loaded; English selected for extraction', hindiConsoleHeading, console: 'English sample -> live role extraction -> crew planner -> READY/NOT READY view -> real public share', extractedRoleCount, readyText, sharePath })

  // Evidence draft, flag visibility, reasoned revision, API redraft, confirmation and correction.
  await page.goto(`${base}/console`)
  await page.getByRole('combobox', { name: 'Choose a drive' }).selectOption('task-05')
  await page.getByRole('button', { name: 'English sample' }).click()
  await page.getByRole('button', { name: 'Extract roles' }).click()
  await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 30000 })
  await page.getByRole('button', { name: 'Build crew', exact: true }).click()
  await page.locator('.crew-board').waitFor({ timeout: 30000 })
  const consoleNav = page.getByRole('navigation', { name: 'Organiser console' })
  await consoleNav.getByRole('button', { name: /Evidence/ }).click()
  await page.getByLabel('Host notes').fill('The team completed its water and hygiene setup. One paper attendance entry needs review: 8 hours claimed, 5 recorded.')
  for (const field of await page.locator('.attendance-row input[type="number"]').all()) await field.fill('5')
  await page.getByRole('button', { name: 'Draft contribution cards' }).click()
  await page.locator('.contribution-card').first().waitFor({ timeout: 30000 })
  await page.getByRole('button', { name: 'Draft contribution cards' }).waitFor({ timeout: 30000 })
  const draftedCardCount = await page.locator('.contribution-card').count()
  const initialFlagCount = await page.locator('.flag-list').count()
  const revisionInput = page.locator('input[aria-label^="Reason for revision"]').first()
  const revisionCardIndex = await revisionInput.evaluate(input => Array.from(document.querySelectorAll('.contribution-card')).indexOf(input.closest('.contribution-card')))
  const revisionCard = page.locator('.contribution-card').nth(revisionCardIndex)
  await revisionInput.fill('Please reconcile the recorded attendance with the host note.')
  const requestButton = revisionCard.getByRole('button', { name: 'Request revision' })
  await page.waitForFunction(() => Array.from(document.querySelectorAll('.contribution-card button')).some(button => button.textContent.includes('Request revision') && !button.disabled), null, { timeout: 30000 })
  await requestButton.click()
  await revisionCard.getByText('Revision requested', { exact: true }).waitFor({ timeout: 30000 })
  await revisionCard.getByRole('button', { name: 'Redraft cards' }).click()
  await page.getByRole('button', { name: 'Draft contribution cards' }).waitFor({ timeout: 30000 })
  await revisionCard.getByRole('button', { name: 'Confirm', exact: true }).waitFor({ timeout: 30000 })
  await revisionCard.getByRole('button', { name: 'Confirm', exact: true }).click()
  await page.getByRole('button', { name: 'Draft contribution cards' }).waitFor({ timeout: 30000 })
  let corrected = false
  for (const card of await page.locator('.contribution-card').all()) {
    const button = card.getByRole('button', { name: 'Correct hours', exact: true })
    if (await button.count()) { await button.click(); corrected = true; break }
  }
  if (!corrected) throw new Error('No editable card remained for the correction action')
  await consoleNav.getByRole('button', { name: /Ledger/ }).click()
  await page.getByRole('button', { name: 'Verify hash chain' }).click()
  await page.getByText(/Chain verified/).waitFor({ timeout: 30000 })
  await consoleNav.getByRole('button', { name: /Evaluation/ }).click()
  await page.getByText(/Misses|misses/i).waitFor({ timeout: 30000 })
  e2e.push({ evidence: 'drafted cards, requested revision with reason, redrafted card, confirmed and corrected records, verified ledger, opened evaluation', draftedCardCount, initialFlagCount })

  // Actual API role denial as configured by the running service (public_demo=false).
  const roleActions = {}
  for (const role of ['host', 'volunteer', 'viewer']) {
    const capabilityResponse = page.waitForResponse(response => response.url().includes(`/api/capabilities?role=${role}`), { timeout: 15000 })
    await page.getByLabel('Demo role (simulation, not authentication)').selectOption(role)
    await capabilityResponse
    await page.waitForTimeout(100)
    roleActions[role] = await page.locator('.role-switch small').innerText()
  }
  const forbiddenWait = page.waitForResponse(response => response.status() === 403 && response.url().endsWith('/api/volunteers'), { timeout: 15000 }).catch(() => null)
  await page.waitForFunction(() => localStorage.getItem('sewa-role') === 'viewer')
  await page.goto(`${base}/console`)
  const forbidden = await forbiddenWait
  if (forbidden) await page.getByRole('alert').waitFor({ timeout: 15000 })
  const viewerActions = await page.locator('.role-switch small').innerText()
  if (!forbidden) throw new Error('The expected viewer-role 403 on /api/volunteers was not observed')
  await page.getByLabel('Demo role (simulation, not authentication)').selectOption('organiser')
  await page.waitForFunction(() => localStorage.getItem('sewa-role') === 'organiser')
  e2e.push({ roleSwitch: 'capabilities loaded for host, volunteer and viewer; viewer volunteer request returned HTTP 403; UI surfaced the error; organiser restored', roleActions, viewerActions, forbiddenUrl: forbidden.url() })

  await page.goto(`${base}/districts`)
  await page.locator('.map-marker').first().waitFor({ timeout: 15000 })
  const districtCount = await page.locator('.map-marker').count()
  if (districtCount > 1) await page.locator('.map-marker').nth(1).click()
  const selectedDistrict = await page.locator('.district-detail h2').innerText()
  await page.goto(`${base}/volunteer`)
  const volunteerHeading = await page.getByRole('heading', { level: 1 }).innerText()
  e2e.push({ districts: `loaded ${districtCount} read-only map markers; selected ${selectedDistrict}`, volunteer: volunteerHeading })

  // Route screenshots and axe WCAG 2.1 A/AA on every page in both languages.
  for (const lang of ['en', 'hi']) {
    await page.goto(base)
    if ((await page.locator('html').getAttribute('lang')) !== lang) await page.getByRole('button', { name: lang === 'hi' ? 'हिन्दी' : 'English' }).click()
    await page.waitForFunction(expected => document.documentElement.lang === expected, lang)
    for (const [name, route] of [...routePages, ['share', sharePath]]) {
      await page.goto(`${base}${route}`)
      await page.waitForTimeout(400)
      if (lang === 'en') await capture(`page-${name}`)
      const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze()
      const blocking = result.violations.filter(item => ['serious', 'critical'].includes(item.impact ?? ''))
      axeResults.push({ lang, page: name, violations: result.violations.map(item => ({ id: item.id, impact: item.impact, nodes: item.nodes.length })), blocking: blocking.map(item => item.id) })
    }
  }

  // Mock/offline route uses in-browser fixtures and does not call /api on the network.
  const mockRequests = []
  page.on('request', request => { if (new URL(request.url()).pathname.startsWith('/api/')) mockRequests.push(request.url()) })
  await page.goto(`${base}/console?mock=1`)
  if ((await page.locator('html').getAttribute('lang')) !== 'en') await page.getByRole('button', { name: 'English' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'en')
  await page.getByRole('button', { name: 'English sample' }).click()
  await page.getByRole('button', { name: 'Extract roles' }).click()
  await page.getByRole('heading', { name: 'Review the AI draft' }).waitFor({ timeout: 15000 })
  await page.getByRole('button', { name: 'Build crew', exact: true }).click()
  await page.locator('.crew-board').waitFor({ timeout: 15000 })
  const mockBanner = await page.locator('.mock-notice').innerText()
  if (mockRequests.length) throw new Error(`Mock route made live API requests: ${mockRequests.join(', ')}`)
  e2e.push({ mock: `fixture task/extraction/planner completed (${mockBanner}); zero API network calls` })

  // Reduced motion: no animation loop, no smooth scroll; the ring still renders as a still frame.
  const reducedContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' })
  const reducedPage = await reducedContext.newPage()
  await reducedPage.goto(base); await reducedPage.waitForTimeout(2500)
  const reducedMotionResult = { canvas: await reducedPage.locator('.stage canvas').count(), lenis: await reducedPage.evaluate(() => document.documentElement.classList.contains('lenis')) }
  await reducedContext.close()
  const noWebglContext = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const noWebglPage = await noWebglContext.newPage()
  await noWebglPage.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') return null
      return original.call(this, type, ...args)
    }
  })
  await noWebglPage.goto(base)
  await noWebglPage.waitForSelector('.stage-fallback')
  const noWebglResult = { canvas: await noWebglPage.locator('.stage canvas').count(), fallback: await noWebglPage.locator('.stage-fallback').count() }
  await noWebglContext.close()
  // Phone width: no horizontal scroll on the story and console.
  const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  const phonePage = await phone.newPage()
  const phoneResult = {}
  for (const [name, route] of [['story', '/'], ['console', '/console']]) {
    await phonePage.goto(`${base}${route}`); await phonePage.waitForTimeout(2000)
    phoneResult[name] = await phonePage.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)
    await phonePage.screenshot({ path: path.join(out, `phone-${name}.png`) })
  }
  await phone.close()

  const summary = { viewport: '1440x900', e2e, axe: axeResults, api403, apiRequests, reducedMotion: reducedMotionResult, noWebgl: noWebglResult, phoneNoOverflow: phoneResult, pageErrors }
  await writeFile(path.join(out, 'verification-summary.json'), JSON.stringify(summary, null, 2))
  console.log(JSON.stringify(summary, null, 2))
  const blocking = axeResults.filter(item => item.blocking.length)
  if (blocking.length) throw new Error(`Axe found serious/critical violations: ${JSON.stringify(blocking)}`)
  if (pageErrors.length) throw new Error(`Browser page errors: ${pageErrors.join(' | ')}`)
  if (Object.values(phoneResult).some(v => !v)) throw new Error(`Horizontal overflow at phone width: ${JSON.stringify(phoneResult)}`)
} finally {
  await context.close().catch(() => {})
  await browser.close().catch(() => {})
}
