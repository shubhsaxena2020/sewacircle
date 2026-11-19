// Renders the intro frame of the 3D ring (reduced motion = time 0, no pointer) to a still used before the live scene starts.
import { chromium } from 'playwright'
const base = process.env.BASE_URL ?? 'http://127.0.0.1:5173'
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] })
for (const [name, vp] of [['ring-hero', { width: 1440, height: 900 }], ['ring-hero-m', { width: 390, height: 844 }]]) {
  const ctx = await b.newContext({ viewport: vp, reducedMotion: 'reduce', deviceScaleFactor: vp.width < 500 ? 2 : 1 })
  const p = await ctx.newPage()
  await p.goto(base, { waitUntil: 'load' })
  await p.addStyleTag({ content: '.ch,.site-header,.notice,.chapter-dots,.seat-labels,.site-footer{visibility:hidden!important}' })
  await p.waitForSelector('.stage canvas', { timeout: 20000 }); await p.waitForTimeout(3500)
  await p.locator('.stage').screenshot({ path: `public/media/${name}.png` })
  await ctx.close()
}
await b.close()
