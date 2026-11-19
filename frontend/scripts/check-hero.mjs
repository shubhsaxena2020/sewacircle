import { chromium } from '@playwright/test'

const browser = await chromium.launch({ channel: 'chrome', headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`) })
  await page.goto('http://127.0.0.1:4173/')
  await page.locator('.scene-wrap canvas').waitFor({ timeout: 30000 })
  await page.waitForTimeout(3500)
  await page.screenshot({ path: '../docs/screens/v4/landing-3d-1440x900.png' })
  await page.waitForTimeout(4400)
  await page.locator('.scene-wrap canvas').screenshot({ path: '../docs/screens/v4/models/hero-ready.png' })
  console.log(JSON.stringify({ errors, canvas: await page.locator('.scene-wrap canvas').count() }, null, 2))
} finally {
  await browser.close()
}
