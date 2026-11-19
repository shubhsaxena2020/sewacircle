import { chromium } from '@playwright/test'
import { mkdir } from 'node:fs/promises'

const out = new URL('../../docs/screens/v4/models/', import.meta.url)
await mkdir(out, { recursive: true })
const browser = await chromium.launch({ channel: 'chrome', headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1040, height: 1300 }, deviceScaleFactor: 1 })
  page.on('pageerror', error => console.error(error))
  await page.goto('http://127.0.0.1:4190/models/preview.html')
  await page.locator('body[data-done="true"]').waitFor({ timeout: 30000 })
  for (const name of ['volunteer_token', 'role_slot', 'standby_node', 'gap_marker', 'ready_seal', 'crew_ring']) {
    await page.locator(`#${name} canvas`).screenshot({ path: new URL(`${name}.png`, out).pathname.slice(1) })
    console.log(`Captured ${name}`)
  }
  await page.screenshot({ path: new URL('kit-gallery.png', out).pathname.slice(1), fullPage: true })
} finally {
  await browser.close()
}
