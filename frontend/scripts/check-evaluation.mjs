import { chromium } from '@playwright/test'

const browser = await chromium.launch({ channel: 'chrome', headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('http://127.0.0.1:4173/console?step=evaluation')
  await page.locator('.eval-chart svg').first().waitFor({ timeout: 20000 })
  await page.waitForTimeout(800)
  console.log(JSON.stringify({ charts: await page.locator('.eval-chart svg').count(), bars: await page.locator('.recharts-rectangle').count(), whiskers: await page.locator('.recharts-errorBar').count(), errors }))
  await page.screenshot({ path: '../docs/screens/v4/console-evaluation-chart-1440x900.png', fullPage: true })
} finally {
  await browser.close()
}
