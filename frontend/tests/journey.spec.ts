import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const shot = '../docs/screens/v4/'
async function consoleShot(page: import('@playwright/test').Page, name: string) {
  await expect(page.locator('.console-content > div').first()).toHaveCSS('opacity','1')
  await page.screenshot({path:shot+name,fullPage:true})
}
async function axe(page: import('@playwright/test').Page, name: string) {
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()
  const severe=results.violations.filter(v=>v.impact==='serious'||v.impact==='critical')
  if(severe.length) console.log(JSON.stringify(severe.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))))
  expect(severe.map(v=>`${name}: ${v.id} ${v.nodes.map(n=>n.target.join(' ')).join(', ')}`)).toEqual([])
}
test('live organiser journey and desktop pages',async({page})=>{
  const reset=await page.request.post('/api/demo/reset')
  expect(reset.ok()).toBe(true)
  await page.setViewportSize({width:1440,height:900})
  await page.goto('/')
  await expect(page.getByRole('heading',{level:1})).toContainText('Willing volunteers')
  await expect(page.locator('.result-cards')).toBeVisible()
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(1440)
  await page.screenshot({path:shot+'landing-1440x900.png',fullPage:true})
  await axe(page,'landing')
  await page.getByRole('link',{name:'Build a crew'}).first().click()
  await expect(page.getByRole('heading',{name:'Turn interest into a crew decision.'})).toBeVisible()
  await expect(page.locator('select').first()).toHaveValue('task-01')
  await consoleShot(page,'console-task-1440x900.png')
  await axe(page,'console task')
  await page.getByRole('button',{name:'Extract roles'}).click()
  await expect(page.getByRole('heading',{name:'Review the AI draft'})).toBeVisible()
  await consoleShot(page,'console-roles-1440x900.png')
  await axe(page,'console roles')
  await page.getByRole('button',{name:'Build crew'}).click()
  await expect(page.getByRole('status').filter({hasText:'READY'}).first()).toBeVisible()
  await consoleShot(page,'console-crew-1440x900.png')
  await axe(page,'console crew')
  await page.locator('.crew-person button').first().click()
  await expect(page.locator('.dropout-result')).toBeVisible()
  await page.locator('select[aria-label="Choose a volunteer"]').selectOption({index:1})
  await page.getByRole('button',{name:'Compare with this volunteer'}).click()
  await expect(page.locator('.counter-result')).toBeVisible()
  await page.getByRole('button',{name:'Evidence',exact:true}).last().click()
  await expect(page.getByRole('heading',{name:'Host notes'})).toBeVisible()
  const names=await page.locator('.attendance-row span:first-child').allTextContents()
  await page.getByRole('textbox',{name:/Host notes/}).fill(names.map((name,i)=>`${name} worked ${i===names.length-1?8:5} hours.`).join('\n'))
  for(const input of await page.locator('.attendance-row input').all()) await input.fill('5')
  await page.getByRole('button',{name:'Draft contribution cards'}).click()
  await expect(page.locator('.contribution-card').first()).toBeVisible()
  await expect(page.getByRole('button',{name:'Draft contribution cards'})).toBeEnabled()
  await consoleShot(page,'console-evidence-1440x900.png')
  await axe(page,'console evidence')
  await page.locator('.contribution-card').filter({has:page.getByRole('button',{name:'Confirm',exact:true})}).first().getByRole('button',{name:'Confirm',exact:true}).click()
  await page.locator('.console-nav-item').filter({hasText:'Ledger'}).click()
  await page.getByRole('button',{name:'Verify hash chain'}).click()
  await expect(page.getByRole('status')).toContainText('Chain verified')
  await consoleShot(page,'console-ledger-1440x900.png')
  await axe(page,'console ledger')
  await page.locator('.console-nav-item').filter({hasText:'Evaluation'}).click()
  await expect(page.locator('.eval-metric').first()).toBeVisible()
  await expect(page.locator('.recharts-errorBar')).toHaveCount(20)
  await consoleShot(page,'console-evaluation-1440x900.png')
  await axe(page,'console evaluation')
  await page.getByRole('button',{name:'हिन्दी'}).click()
  await expect(page.getByRole('heading',{name:'पूरा नतीजा देखें'})).toBeVisible()
  await page.getByRole('link',{name:'स्वयंसेवक दृश्य'}).first().click()
  await expect(page.getByRole('heading',{level:1})).toContainText('स्वयंसेवक')
  await page.screenshot({path:shot+'volunteer-1440x900.png',fullPage:true})
  await axe(page,'volunteer')
  await page.getByRole('link',{name:'ज़िले'}).click()
  await expect(page.getByRole('heading',{level:1})).toContainText('ज़िलों')
  await expect(page.locator('.district-drive b').first()).not.toHaveText(/अभी जाँच नहीं हुई|Not yet computed/)
  await page.screenshot({path:shot+'districts-1440x900.png',fullPage:true})
  await axe(page,'districts')
  await page.getByRole('link',{name:'तरीका'}).first().click()
  await page.screenshot({path:shot+'method-1440x900.png',fullPage:true})
  await axe(page,'method')
})
test('mock mode works without API',async({page})=>{
  await page.goto('/?mock=1')
  await expect(page.getByText('Mock data · illustrative only')).toBeVisible()
  await page.getByRole('link',{name:'Build a crew'}).first().click()
  await expect(page.getByText('Mock data · illustrative only')).toBeVisible()
  await page.getByRole('button',{name:'Extract roles'}).click()
  await expect(page.getByRole('heading',{name:'Review the AI draft'})).toBeVisible()
  await page.getByRole('button',{name:'Build crew'}).click()
  await expect(page.getByRole('status').filter({hasText:'READY'}).first()).toBeVisible()
  await axe(page,'mock console')
})

test('reduced motion shows the rendered hero still',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'})
  await page.goto('/')
  await expect(page.locator('.hero-art img.hero-fallback')).toBeVisible()
  await expect(page.locator('.hero-art canvas')).toHaveCount(0)
  await expect(page.locator('.hero-art video')).toHaveCount(0)
})
test('phone pages fit and pass axe',async({page})=>{
  await page.setViewportSize({width:390,height:844})
  for(const [path,name] of [['/','landing'],['/console','console-task'],['/volunteer','volunteer'],['/districts','districts'],['/method','method']]){
    await page.goto(path)
    await expect(page.getByRole('heading',{level:1})).toBeVisible()
    if(path==='/console') await expect(page.locator('select').first()).toHaveValue('task-01')
    if(path==='/volunteer') await expect(page.locator('.profile-meta')).toBeVisible()
    if(path==='/districts') { await expect(page.locator('.map-marker')).toHaveCount(20); await expect(page.locator('.district-picker')).toBeVisible(); await expect(page.locator('.district-drive b').first()).not.toHaveText(/Not yet computed|अभी जाँच नहीं हुई/) }
    if(path==='/') await expect(page.locator('.result-cards')).toBeVisible()
    await page.screenshot({path:shot+`${name}-390x844.png`,fullPage:true})
    const width=await page.evaluate(()=>document.documentElement.scrollWidth)
    expect(width,`${name} horizontal overflow`).toBeLessThanOrEqual(391)
    await axe(page,`${name} phone`)
    if(path==='/console'){
      await page.getByRole('button',{name:'Extract roles'}).click()
      await expect(page.getByRole('heading',{name:'Review the AI draft'})).toBeVisible()
      await consoleShot(page,'console-roles-390x844.png')
      await page.getByRole('button',{name:'Build crew'}).click()
      await expect(page.getByRole('status').filter({hasText:'READY'}).first()).toBeVisible()
      await consoleShot(page,'console-crew-390x844.png')
      await page.getByRole('button',{name:'Evidence',exact:true}).last().click()
      await expect(page.getByRole('heading',{name:'Host notes'})).toBeVisible()
      await consoleShot(page,'console-evidence-390x844.png')
      await page.locator('.console-nav-item').filter({hasText:'Ledger'}).click()
      await expect(page.getByRole('heading',{name:'A record of decisions'})).toBeVisible()
      await consoleShot(page,'console-ledger-390x844.png')
      await page.locator('.console-nav-item').filter({hasText:'Evaluation'}).click()
      await expect(page.locator('.eval-metric').first()).toBeVisible()
      await consoleShot(page,'console-evaluation-390x844.png')
    }
  }
})

test('3D stays on landing and static fallbacks work',async({page,browser})=>{
  const requests:string[]=[]
  page.on('request',request=>requests.push(request.url()))
  for(const path of ['/console','/volunteer','/districts','/method']){
    await page.goto(path)
    await expect(page.getByRole('heading',{level:1})).toBeVisible()
  }
  expect(requests.filter(url=>/CrewScene-[^/]+\.js/.test(url))).toEqual([])

  const webgl=await page.evaluate(()=>!!(document.createElement('canvas').getContext('webgl2')||document.createElement('canvas').getContext('webgl')))
  await page.goto('/')
  if(webgl){
    await expect(page.locator('.hero-art canvas')).toBeVisible()
    expect(requests.some(url=>/CrewScene-[^/]+\.js/.test(url))).toBe(true)
  }

  await page.emulateMedia({reducedMotion:'reduce'})
  await page.goto('/')
  await expect(page.locator('.hero-art img.hero-fallback')).toBeVisible()
  await expect(page.locator('.hero-art canvas')).toHaveCount(0)

  const noWebgl=await browser.newPage()
  try{
    await noWebgl.addInitScript(()=>{
      const original=HTMLCanvasElement.prototype.getContext
      HTMLCanvasElement.prototype.getContext=function(type,...args){
        if(type==='webgl'||type==='webgl2'||type==='experimental-webgl') return null
        return original.call(this,type,...args)
      } as typeof original
    })
    await noWebgl.goto('/')
    await expect(noWebgl.locator('.hero-art video.hero-fallback')).toBeVisible()
    await expect(noWebgl.locator('.hero-art canvas')).toHaveCount(0)
  }finally{await noWebgl.close()}
})

test('keyboard controls and preferences persist',async({page})=>{
  await page.goto('/method')
  await page.keyboard.press('Tab')
  await expect(page.locator('.skip')).toBeFocused()
  await page.locator('.language-button').focus()
  await page.keyboard.press('Space')
  await expect(page.locator('html')).toHaveAttribute('lang','hi')
  await page.locator('.projector-button').focus()
  await page.keyboard.press('Space')
  await expect(page.locator('html')).toHaveClass(/projector/)
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('lang','hi')
  await expect(page.locator('html')).toHaveClass(/projector/)
})
