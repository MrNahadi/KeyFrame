import { describe, expect, it } from 'vitest'
import { axisDecimals, clock, delay, fixed, length, number, reading, signed } from './format'

describe('format', () => {
  it('writes readings at a sensible precision with proper units', () => {
    expect(reading(0.211272661, 'kgf/cm2')).toBe('0.211 kgf/cm²')
    expect(reading(422.56827000000004, '°C')).toBe('423 °C')
    expect(reading(36.48824225, '°C')).toBe('36.5 °C')
    expect(reading(1.107401649, 'V')).toBe('1.11 V')
    expect(reading(12.7498, 'm3/h')).toBe('12.7 m³/h')
    expect(number(null)).toBe('–')
  })

  it('writes durations and clocks', () => {
    expect(length(8040)).toBe('2 h 14 min')
    expect(length(1800)).toBe('30 min')
    expect(delay(545)).toBe('9 min 5 s')
    expect(clock(3870)).toBe('1:04:30')
    expect(clock(3201)).toBe('53:21')
    expect(signed(-0.384)).toBe('−0.38')
  })

  it('gives axes enough decimals to keep ticks distinct', () => {
    expect(axisDecimals(0.04)).toBe(3)
    expect(axisDecimals(0.4)).toBe(2)
    expect(axisDecimals(4)).toBe(1)
    expect(axisDecimals(400)).toBe(0)
    expect(fixed(12.6612, 2)).toBe('12.66')
  })
})
