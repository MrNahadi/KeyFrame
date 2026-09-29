import { describe, expect, it } from 'vitest'
import { faultName, faultPhrase, featureName, GROUPS, sensorGroup } from './vocabulary'

describe('vocabulary', () => {
  it('names faults in words', () => {
    expect(faultName('AC')).toBe('Air cooler fouling')
    expect(faultPhrase('TD')).toBe('turbine degradation')
    expect(faultName('XYZ')).toBe('XYZ')
    expect(faultName('AC Fouling')).toBe('Air cooler fouling')
    expect(faultPhrase('Normal')).toBe('normal running')
  })

  it('keeps the validated fixed group order', () => {
    expect(GROUPS.map((g) => g.label)).toEqual([
      'Air path',
      'Fuel system',
      'Cooling',
      'Lube oil',
      'Combustion and power',
    ])
    expect(sensorGroup('fuel_flow').label).toBe('Fuel system')
    expect(sensorGroup('No.2 Exh.Gas Temp.').label).toBe('Combustion and power')
  })

  it('turns engine feature names into plain words', () => {
    expect(featureName('Charge Air IC Air Temp. Out_roll_300s_mean')).toBe(
      'Charge air cooler air temperature out, 5-minute average',
    )
    expect(featureName('LO Cooling Water Temp. In_roll_900s_std')).toBe(
      'Lube oil cooling water temperature in, 15-minute spread',
    )
    expect(featureName('Engine Speed')).toBe('Engine speed')
  })
})
