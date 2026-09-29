import { describe, expect, it } from 'vitest'
import { buildWaterfall } from './waterfall'

const groups = {
  'air path': 1.0,
  'combustion and power': -0.25,
  cooling: 0.5,
  'fuel system': 0.05,
  'lube oil': -2,
}

describe('buildWaterfall', () => {
  it('runs from the base value to the output, summing every step', () => {
    const { steps, base, output } = buildWaterfall(groups, -1)
    expect(base).toBe(-1)
    expect(steps[0].start).toBeCloseTo(-1)
    for (let i = 1; i < steps.length; i++) expect(steps[i].start).toBeCloseTo(steps[i - 1].end)
    expect(steps[steps.length - 1].end).toBeCloseTo(output)
    expect(output).toBeCloseTo(-1 + 1.0 - 0.25 + 0.5 + 0.05 - 2)
  })

  it('orders steps by absolute size, largest first', () => {
    const { steps } = buildWaterfall(groups, 0)
    expect(steps.map((s) => s.name)).toEqual([
      'Lube oil',
      'Air path',
      'Cooling',
      'Combustion and power',
      'Fuel system',
    ])
  })

  it('gives each step a sign and a plain group name', () => {
    const { steps } = buildWaterfall(groups, 0)
    const byName = Object.fromEntries(steps.map((s) => [s.name, s]))
    expect(byName['Lube oil'].sign).toBe('negative')
    expect(byName['Air path'].sign).toBe('positive')
    expect(byName['Lube oil'].end).toBeLessThan(byName['Lube oil'].start)
    expect(byName['Air path'].end).toBeGreaterThan(byName['Air path'].start)
  })

  it('treats a zero contribution as positive and keeps unknown groups readable', () => {
    const { steps } = buildWaterfall({ 'odd group': 0 }, 2)
    expect(steps[0]).toMatchObject({ name: 'Odd group', sign: 'positive', start: 2, end: 2 })
  })
})
