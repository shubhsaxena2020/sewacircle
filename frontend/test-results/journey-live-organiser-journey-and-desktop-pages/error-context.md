# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: journey.spec.ts >> live organiser journey and desktop pages
- Location: tests\journey.spec.ts:10:1

# Error details

```
Test timeout of 120000ms exceeded.
```

```
Error: locator.click: Test timeout of 120000ms exceeded.
Call log:
  - waiting for locator('.contribution-card').first().getByRole('button', { name: 'Confirm', exact: true })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - link "Skip to content" [ref=e3] [cursor=pointer]:
    - /url: "#main"
  - generic [ref=e4]:
    - text: Synthetic data
    - generic [ref=e6]: Not affiliated with MY Bharat or any government body.
  - banner [ref=e7]:
    - link "SewaCircle" [ref=e8] [cursor=pointer]:
      - /url: /
    - navigation "Main navigation" [ref=e14]:
      - link "The idea" [ref=e15] [cursor=pointer]:
        - /url: /
      - link "Organiser console" [ref=e16] [cursor=pointer]:
        - /url: /console
      - link "Volunteer view" [ref=e17] [cursor=pointer]:
        - /url: /volunteer
      - link "Districts" [ref=e18] [cursor=pointer]:
        - /url: /districts
      - link "Method" [ref=e19] [cursor=pointer]:
        - /url: /method
    - generic [ref=e20]:
      - button "हिन्दी" [ref=e21] [cursor=pointer]
      - button "Projector mode" [ref=e27] [cursor=pointer]
  - main [ref=e32]:
    - generic [ref=e33]:
      - generic [ref=e34]:
        - text: READY CREW · ORGANISER TOOL
        - heading "Turn interest into a crew decision." [level=1] [ref=e35]
        - paragraph [ref=e36]: Start with a synthetic drive. Every AI role is a draft until you review it.
      - generic [ref=e37]:
        - complementary [ref=e38]:
          - navigation "Organiser console" [ref=e39]:
            - button "01 Task" [ref=e40] [cursor=pointer]:
              - generic [ref=e41]: "01"
              - text: Task
            - button "02 Roles" [ref=e44] [cursor=pointer]:
              - generic [ref=e45]: "02"
              - text: Roles
            - button "03 Crew" [ref=e48] [cursor=pointer]:
              - generic [ref=e49]: "03"
              - text: Crew
            - button "04 Evidence" [ref=e52] [cursor=pointer]:
              - generic [ref=e53]: "04"
              - text: Evidence
            - button "05 Ledger" [ref=e56] [cursor=pointer]:
              - generic [ref=e57]: "05"
              - text: Ledger
            - button "06 Evaluation" [ref=e60] [cursor=pointer]:
              - generic [ref=e61]: "06"
              - text: Evaluation
          - paragraph [ref=e68]: Safety roles use only host-checked skills.
        - generic [ref=e71]:
          - generic [ref=e72]:
            - text: Evidence
            - heading "Host notes" [level=2] [ref=e73]
            - paragraph [ref=e74]: A host decides each contribution card. The ledger records edits, not truth.
          - generic [ref=e75]:
            - generic [ref=e76]: Host notes
            - textbox "Host notes Describe what the team actually did after the drive." [ref=e77]: Imran B. (Poster team) worked about 5 hours. Mohit Z. (First-aid support) worked about 5 hours. Divya H. (Supplies and site setup) worked about 5 hours. Kabir Z. (Local-language liaison) worked about 8 hours.
            - generic [ref=e78]: Describe what the team actually did after the drive.
          - generic [ref=e79]:
            - heading "Attendance sheet" [level=3] [ref=e80]
            - generic [ref=e81]: Synthetic data
          - generic [ref=e82]:
            - generic [ref=e83]:
              - generic [ref=e84]: Imran B.
              - generic [ref=e85]: Hours on site
              - spinbutton "Imran B. Hours on site" [ref=e86]: "5"
            - generic [ref=e87]:
              - generic [ref=e88]: Mohit Z.
              - generic [ref=e89]: Hours on site
              - spinbutton "Mohit Z. Hours on site" [ref=e90]: "5"
            - generic [ref=e91]:
              - generic [ref=e92]: Divya H.
              - generic [ref=e93]: Hours on site
              - spinbutton "Divya H. Hours on site" [ref=e94]: "5"
            - generic [ref=e95]:
              - generic [ref=e96]: Kabir Z.
              - generic [ref=e97]: Hours on site
              - spinbutton "Kabir Z. Hours on site" [ref=e98]: "5"
          - button "Draft contribution cards" [ref=e99] [cursor=pointer]
          - generic [ref=e103]:
            - article [ref=e104]:
              - generic [ref=e105]:
                - generic [ref=e106]: Contribution card
                - generic [ref=e107]: Confirmed
              - heading "Imran B." [level=3] [ref=e108]
              - paragraph [ref=e109]: Poster team
              - paragraph [ref=e110]: The notes say this person worked about 5 hours on the poster team.
              - generic [ref=e111]:
                - generic [ref=e112]:
                  - text: Claimed hours
                  - generic [ref=e113]: "5.0"
                - generic [ref=e114]:
                  - text: Recorded hours
                  - generic [ref=e115]: "5.0"
              - button "Export unsigned credential" [ref=e116] [cursor=pointer]
            - article [ref=e117]:
              - generic [ref=e118]:
                - generic [ref=e119]: Contribution card
                - generic [ref=e120]: Draft
              - heading "Mohit Z." [level=3] [ref=e121]
              - paragraph [ref=e122]: First-aid support
              - paragraph [ref=e123]: The notes say this volunteer worked about 5 hours providing first-aid support.
              - generic [ref=e124]:
                - generic [ref=e125]:
                  - text: Claimed hours
                  - generic [ref=e126]: "5.0"
                - generic [ref=e127]:
                  - text: Recorded hours
                  - generic [ref=e128]: "5.0"
              - generic [ref=e129]:
                - strong [ref=e130]: Rule flags
                - paragraph [ref=e131]: 5 hours is a round number shared by at least 3 cards in this batch; worth a quick spot-check, but round shifts are normal and this is not a rejection.
              - generic [ref=e132]:
                - button "Confirm" [ref=e133] [cursor=pointer]
                - generic [ref=e134]:
                  - generic [ref=e135]: Correct hours
                  - spinbutton "Correct hours card-task-01-v-070-first-aid-support" [ref=e136]: "5"
                - button "Correct hours" [ref=e137] [cursor=pointer]
                - button "Reject" [ref=e138] [cursor=pointer]
            - article [ref=e139]:
              - generic [ref=e140]:
                - generic [ref=e141]: Contribution card
                - generic [ref=e142]: Draft
              - heading "Divya H." [level=3] [ref=e143]
              - paragraph [ref=e144]: Supplies and site setup
              - paragraph [ref=e145]: The notes say this volunteer worked about 5 hours on supplies and site setup.
              - generic [ref=e146]:
                - generic [ref=e147]:
                  - text: Claimed hours
                  - generic [ref=e148]: "5.0"
                - generic [ref=e149]:
                  - text: Recorded hours
                  - generic [ref=e150]: "5.0"
              - generic [ref=e151]:
                - strong [ref=e152]: Rule flags
                - paragraph [ref=e153]: 5 hours is a round number shared by at least 3 cards in this batch; worth a quick spot-check, but round shifts are normal and this is not a rejection.
              - generic [ref=e154]:
                - button "Confirm" [ref=e155] [cursor=pointer]
                - generic [ref=e156]:
                  - generic [ref=e157]: Correct hours
                  - spinbutton "Correct hours card-task-01-v-067-supplies-and-site-setup" [ref=e158]: "5"
                - button "Correct hours" [ref=e159] [cursor=pointer]
                - button "Reject" [ref=e160] [cursor=pointer]
            - article [ref=e161]:
              - generic [ref=e162]:
                - generic [ref=e163]: Contribution card
                - generic [ref=e164]: Flagged
              - heading "Kabir Z." [level=3] [ref=e165]
              - paragraph [ref=e166]: Local-language liaison
              - paragraph [ref=e167]: The notes say this volunteer worked about 8 hours as local-language liaison.
              - generic [ref=e168]:
                - generic [ref=e169]:
                  - text: Claimed hours
                  - generic [ref=e170]: "8.0"
                - generic [ref=e171]:
                  - text: Recorded hours
                  - generic [ref=e172]: "5.0"
              - generic [ref=e173]:
                - strong [ref=e174]: Rule flags
                - paragraph [ref=e175]: Claims 8 hours but attendance records at most 5; ask the host to check the difference.
              - generic [ref=e176]:
                - button "Confirm" [ref=e177] [cursor=pointer]
                - generic [ref=e178]:
                  - generic [ref=e179]: Correct hours
                  - spinbutton "Correct hours card-task-01-v-011-local-language-liaison" [ref=e180]: "5"
                - button "Correct hours" [ref=e181] [cursor=pointer]
                - button "Reject" [ref=e182] [cursor=pointer]
          - button "Ledger" [ref=e183] [cursor=pointer]
  - contentinfo [ref=e186]:
    - generic [ref=e187]:
      - link "Sewa Circle" [ref=e188] [cursor=pointer]:
        - /url: /
        - text: Sewa
        - generic [ref=e189]: Circle
      - paragraph [ref=e190]: Not affiliated with MY Bharat or any government body. Synthetic data.
    - generic [ref=e191]:
      - link "Method" [ref=e192] [cursor=pointer]:
        - /url: /method
      - link "Organiser console" [ref=e196] [cursor=pointer]:
        - /url: /console
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test'
  2  | import AxeBuilder from '@axe-core/playwright'
  3  | 
  4  | const shot = '../docs/screens/v4/'
  5  | async function axe(page: import('@playwright/test').Page, name: string) {
  6  |   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()
  7  |   const severe=results.violations.filter(v=>v.impact==='serious'||v.impact==='critical')
  8  |   expect(severe.map(v=>`${name}: ${v.id} ${v.nodes.map(n=>n.target.join(' ')).join(', ')}`)).toEqual([])
  9  | }
  10 | test('live organiser journey and desktop pages',async({page})=>{
  11 |   await page.setViewportSize({width:1440,height:900})
  12 |   await page.goto('/')
  13 |   await expect(page.getByRole('heading',{level:1})).toContainText('Willing volunteers')
  14 |   await page.screenshot({path:shot+'landing-1440x900.png',fullPage:true})
  15 |   await axe(page,'landing')
  16 |   await page.getByRole('link',{name:'Build a crew'}).first().click()
  17 |   await expect(page.getByRole('heading',{name:'Turn interest into a crew decision.'})).toBeVisible()
  18 |   await expect(page.locator('select').first()).toHaveValue('task-01')
  19 |   await page.screenshot({path:shot+'console-task-1440x900.png',fullPage:true})
  20 |   await axe(page,'console task')
  21 |   await page.getByRole('button',{name:'Extract roles'}).click()
  22 |   await expect(page.getByRole('heading',{name:'Review the AI draft'})).toBeVisible()
  23 |   await page.screenshot({path:shot+'console-roles-1440x900.png',fullPage:true})
  24 |   await axe(page,'console roles')
  25 |   await page.getByRole('button',{name:'Build crew'}).click()
  26 |   await expect(page.getByRole('status').filter({hasText:'READY'}).first()).toBeVisible()
  27 |   await page.screenshot({path:shot+'console-crew-1440x900.png',fullPage:true})
  28 |   await axe(page,'console crew')
  29 |   await page.locator('.crew-person button').first().click()
  30 |   await expect(page.locator('.dropout-result')).toBeVisible()
  31 |   await page.locator('select[aria-label="Choose a volunteer"]').selectOption({index:1})
  32 |   await page.getByRole('button',{name:'Compare with this volunteer'}).click()
  33 |   await expect(page.locator('.counter-result')).toBeVisible()
  34 |   await page.getByRole('button',{name:'Evidence',exact:true}).last().click()
  35 |   await expect(page.getByRole('heading',{name:'Host notes'})).toBeVisible()
  36 |   await page.getByRole('button',{name:'Draft contribution cards'}).click()
  37 |   await expect(page.locator('.contribution-card').first()).toBeVisible()
  38 |   await page.screenshot({path:shot+'console-evidence-1440x900.png',fullPage:true})
  39 |   await axe(page,'console evidence')
> 40 |   await page.locator('.contribution-card').first().getByRole('button',{name:'Confirm',exact:true}).click()
     |                                                                                                    ^ Error: locator.click: Test timeout of 120000ms exceeded.
  41 |   await page.locator('.console-nav-item').filter({hasText:'Ledger'}).click()
  42 |   await page.getByRole('button',{name:'Verify hash chain'}).click()
  43 |   await expect(page.getByRole('status')).toContainText('Chain verified')
  44 |   await page.screenshot({path:shot+'console-ledger-1440x900.png',fullPage:true})
  45 |   await axe(page,'console ledger')
  46 |   await page.locator('.console-nav-item').filter({hasText:'Evaluation'}).click()
  47 |   await expect(page.locator('.eval-metric').first()).toBeVisible()
  48 |   await page.screenshot({path:shot+'console-evaluation-1440x900.png',fullPage:true})
  49 |   await axe(page,'console evaluation')
  50 |   await page.getByRole('button',{name:'हिन्दी'}).click()
  51 |   await expect(page.getByRole('heading',{name:'पूरा नतीजा देखें'})).toBeVisible()
  52 |   await page.getByRole('link',{name:'स्वयंसेवक दृश्य'}).first().click()
  53 |   await expect(page.getByRole('heading',{level:1})).toContainText('स्वयंसेवक')
  54 |   await page.screenshot({path:shot+'volunteer-1440x900.png',fullPage:true})
  55 |   await axe(page,'volunteer')
  56 |   await page.getByRole('link',{name:'ज़िले'}).click()
  57 |   await expect(page.getByRole('heading',{level:1})).toContainText('ज़िलों')
  58 |   await page.screenshot({path:shot+'districts-1440x900.png',fullPage:true})
  59 |   await axe(page,'districts')
  60 |   await page.getByRole('link',{name:'तरीका'}).first().click()
  61 |   await page.screenshot({path:shot+'method-1440x900.png',fullPage:true})
  62 |   await axe(page,'method')
  63 | })
  64 | test('mock mode works without API',async({page})=>{
  65 |   await page.goto('/?mock=1')
  66 |   await expect(page.getByText('Mock data · illustrative only')).toBeVisible()
  67 |   await page.getByRole('link',{name:'Build a crew'}).first().click()
  68 |   await expect(page.getByText('Mock data · illustrative only')).toBeVisible()
  69 |   await page.getByRole('button',{name:'Extract roles'}).click()
  70 |   await expect(page.getByRole('heading',{name:'Review the AI draft'})).toBeVisible()
  71 |   await page.getByRole('button',{name:'Build crew'}).click()
  72 |   await expect(page.getByRole('status').filter({hasText:'READY'}).first()).toBeVisible()
  73 |   await axe(page,'mock console')
  74 | })
  75 | test('phone pages fit and pass axe',async({page})=>{
  76 |   await page.setViewportSize({width:390,height:844})
  77 |   for(const [path,name] of [['/','landing'],['/console','console-task'],['/volunteer','volunteer'],['/districts','districts'],['/method','method']]){
  78 |     await page.goto(path)
  79 |     await expect(page.locator('main')).toBeVisible()
  80 |     await page.screenshot({path:shot+`${name}-390x844.png`,fullPage:true})
  81 |     const width=await page.evaluate(()=>document.documentElement.scrollWidth)
  82 |     expect(width,`${name} horizontal overflow`).toBeLessThanOrEqual(391)
  83 |     await axe(page,`${name} phone`)
  84 |   }
  85 | })
  86 | 
```