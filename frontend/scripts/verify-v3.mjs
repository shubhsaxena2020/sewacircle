import AxeBuilder from '@axe-core/playwright'
import { chromium } from '@playwright/test'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173'
const out = path.resolve(process.env.SCREENSHOT_DIR ?? path.join('..', 'docs', 'screens', 'v5', 'round2', 'after'))
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
let filmRanges = []
page.on('pageerror', error => pageErrors.push(error.message))
page.on('response', response => { if (response.status() === 403) api403.push(response.url()) })
page.on('request', request => { if (request.url().includes('/api/roster')) apiRequests.push(`${request.method()} ${new URL(request.url()).pathname}`) })
const routePages = [
  ['story', '/'], ['console', '/console'], ['volunteer', '/volunteer'],
  ['districts', '/districts'], ['method', '/method'],
]
const chapters = ['intro', 'interest', 'brief', 'crew', 'bench', 'verdict', 'dropout', 'evidence', 'districts', 'numbers', 'try']
const capture = async name => page.screenshot({ path: path.join(out, `${name}.png`), animations: 'disabled' })

try {
  const resetResponse = await page.request.post(`${base}/api/demo/reset`, { headers: { 'X-Demo-Role': 'organiser' } })
  if (!resetResponse.ok()) throw new Error(`Could not reset the local synthetic demo state: HTTP ${resetResponse.status()}`)
  e2e.push({ demoReset: `HTTP ${resetResponse.status()} before the verification workflow` })
  // Full story and updated 1440x900 chapter screenshots.
  await page.goto(base, { waitUntil: 'domcontentloaded' })
  await page.getByRole('heading', { level: 1 }).waitFor()
  filmRanges = await page.locator('.chapter-film').evaluateAll(nodes => nodes.map(node => node.getAttribute('aria-label')))
  if (filmRanges.length !== 6 || filmRanges.some(range => !range?.includes('Illustrative film'))) throw new Error(`Expected all six illustrative film cuts, got ${filmRanges.length}`)
  await page.waitForTimeout(800)
  await capture('page-story')
  for (let index = 0; index < 6; index++) {
    const film = page.locator('.chapter-film').nth(index)
    await film.scrollIntoViewIfNeeded()
    const bounds = await film.evaluate(node => [Number(node.getAttribute('data-start')), Number(node.getAttribute('data-end'))])
    await page.waitForFunction(({ i, start, end }) => {
      const video = document.querySelectorAll('.chapter-film')[i]?.querySelector('video')
      return video && video.currentTime > start + .3 && video.currentTime <= end + 1.25
    }, { i: index, start: bounds[0], end: bounds[1] }, { timeout: 15000 })
    await page.screenshot({ path: path.join(out, `film-cut-${String(index + 1).padStart(2, '0')}.png`), animations: 'disabled' })
  }
  for (let index = 0; index < chapters.length; index++) {
    const id = chapters[index]
    await page.locator(`#${id}`).scrollIntoViewIfNeeded()
    if (id === 'numbers') {
      await page.waitForFunction(() => document.querySelectorAll('.story-metric[data-counter-ready="true"]').length === 5, null, { timeout: 5000 })
      const values = await page.locator('#numbers .story-metric strong').allTextContents()
      const expected = ['70%', '10%', '23%', '40%']
      if (expected.some((value, i) => values[i] !== value)) throw new Error(`Evaluation counters did not settle at ${expected.join(', ')}: ${values.join(', ')}`)
      e2e.push({ evaluationCounters: values.slice(0, 4) })
    }
    await page.waitForTimeout(350)
    await capture(`chapter-${String(index).padStart(2, '0')}-${id}`)
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }))
  await page.getByRole('button', { name: 'हिन्दी' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'hi')
  const hindiHeadline = await page.getByRole('heading', { level: 1 }).innerText()
  if (!/[\u0900-\u097F]/.test(hindiHeadline)) throw new Error(`Hindi headline missing Devanagari: ${hindiHeadline}`)
  await page.waitForTimeout(250)
  await capture('page-story-hi')
  await page.getByRole('button', { name: 'English' }).click()
  await page.waitForFunction(() => document.documentElement.lang === 'en')
  await page.locator('#crew').scrollIntoViewIfNeeded()
  await page.getByRole('button', { name: 'Plan the crew' }).click()
  await page.locator('.crew-pill-list').waitFor({ timeout: 30000 })
  await page.locator('#dropout').scrollIntoViewIfNeeded()
  const firstDrop = page.locator('#dropout').getByRole('button', { name: /^Drop / })
  await firstDrop.click()
  const dropoutStatus = page.locator('#dropout [role="status"]')
  await dropoutStatus.waitFor({ timeout: 30000 })
  const firstDropResult = await dropoutStatus.innerText()
  if (!firstDropResult.includes('NOT READY')) throw new Error(`Live dropout did not expose NOT READY: ${firstDropResult}`)
  await capture('story-dropout-not-ready')
  const secondDrop = page.locator('#dropout').getByRole('button', { name: /^Drop Heena P\./ })
  if (await secondDrop.count()) { await secondDrop.click(); await page.waitForTimeout(400); }
  e2e.push({ storyDropout: firstDropResult, apiCalls: apiRequests.slice() })
  e2e.push({ story: 'all 11 anchors captured; Hindi title rendered in Devanagari' })

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

  // Reduced-motion experience uses the static still and avoids the 3D canvas/video.
  const reducedContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' })
  const reducedPage = await reducedContext.newPage()
  await reducedPage.goto(base)
  await reducedPage.waitForSelector('.scene-still')
  const reducedMotionResult = { canvas: await reducedPage.locator('.world-canvas canvas').count(), video: await reducedPage.locator('.intro-film').count(), still: await reducedPage.locator('.scene-still').count() }
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
  await noWebglPage.waitForSelector('.scene-still')
  const noWebglResult = { canvas: await noWebglPage.locator('.world-canvas canvas').count(), still: await noWebglPage.locator('.scene-still').count() }
  await noWebglContext.close()

  // Record a separate slow, smooth chapter-by-chapter story pass.
  const videoContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, recordVideo: { dir: path.join(out, '.video-tmp'), size: { width: 1440, height: 900 } } })
  const videoPage = await videoContext.newPage()
  await videoPage.goto(base)
  await videoPage.waitForTimeout(1000)
  const maxScroll = await videoPage.evaluate(() => document.documentElement.scrollHeight - window.innerHeight)
  const step = Math.ceil(maxScroll / 42)
  for (let y = step; y < maxScroll; y += step) {
    await videoPage.evaluate(top => window.scrollTo({ top, behavior: 'smooth' }), y)
    await videoPage.waitForTimeout(480)
  }
  await videoPage.evaluate(top => window.scrollTo({ top, behavior: 'smooth' }), maxScroll)
  await videoPage.waitForTimeout(1200)
  await videoPage.waitForTimeout(1000)
  const video = videoPage.video()
  await videoPage.close()
  await video.saveAs(path.join(out, 'story-scroll.webm'))
  await videoContext.close()

  e2e.push({ filmCuts: filmRanges })
  const summary = { viewport: '1440x900', e2e, axe: axeResults, api403, apiRequests, reducedMotion: reducedMotionResult, noWebgl: noWebglResult, pageErrors, screenshots: ['page-story.png', 'page-story-hi.png', 'story-dropout-not-ready.png', ...chapters.map((id, i) => `chapter-${String(i).padStart(2, '0')}-${id}.png`), 'page-console.png', 'page-volunteer.png', 'page-districts.png', 'page-method.png', 'page-share.png'], video: 'story-scroll.webm' }
  await writeFile(path.join(out, 'verification-summary.json'), JSON.stringify(summary, null, 2))
  console.log(JSON.stringify(summary, null, 2))
  const blocking = axeResults.filter(item => item.blocking.length)
  if (blocking.length) throw new Error(`Axe found serious/critical violations: ${JSON.stringify(blocking)}`)
  if (pageErrors.length) throw new Error(`Browser page errors: ${pageErrors.join(' | ')}`)
} finally {
  await context.close().catch(() => {})
  await browser.close().catch(() => {})
}
