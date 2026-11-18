import { describe, expect, it } from 'vitest'
import { copy, formatNumber, formatPercent, formatSlot, tr } from './i18n'

describe('translation coverage',()=>{
  it('provides nonempty English and Hindi for every key',()=>{
    for(const [key,value] of Object.entries(copy)){
      expect(value.length,key).toBe(2)
      expect(value[0].trim(),key).not.toBe('')
      expect(value[1].trim(),key).not.toBe('')
      expect(tr('en',key as keyof typeof copy)).toBe(value[0])
      expect(tr('hi',key as keyof typeof copy)).toBe(value[1])
    }
  })
})
describe('number formatting',()=>{
  it('formats Indian grouping and Hindi numerals',()=>{
    expect(formatNumber(123456,'en')).toBe('1,23,456')
    expect(formatNumber(123456,'hi')).toBe('१,२३,४५६')
    expect(formatPercent(.7,'en')).toBe('70%')
    expect(formatPercent(.7,'hi')).toBe('७०%')
  })
  it('labels task slots naturally in both languages',()=>{
    expect(formatSlot('sat_morning','en')).toBe('Saturday morning')
    expect(formatSlot('sat_morning','hi')).toBe('शनिवार सुबह')
  })
})
