import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { alarmTime } from './status'
import { buildSeries, Traces } from './Traces'
import type { Replay, ReplayFrame } from './types'

afterEach(cleanup)

const keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

const frame = (i: number, alarm: string): ReplayFrame => ({
  t: 100 + i * 10,
  sensors: Object.fromEntries(
    keys.map((k) => [k, { label: `Sensor ${k}`, value: i + keys.indexOf(k), unit: 'bar' }]),
  ),
  probabilities: {},
  alarm,
  predicted_class: alarm,
  shap_groups: {},
  top_features: [],
})

const replay: Replay = {
  run: 'r',
  fault: 'f',
  nominal_load: 40,
  switch_on_t: 120,
  sampling_note: '',
  provenance: '',
  frames: [0, 1, 2, 3, 4].map((i) => frame(i, i >= 3 ? 'AC Fouling' : 'Normal')),
}

describe('Traces', () => {
  it('renders eight charts, each with its label and the current reading with its unit', () => {
    render(<Traces replay={replay} index={2} width={300} height={120} />)
    expect(screen.getAllByRole('figure')).toHaveLength(8)
    expect(screen.getByText('Sensor a')).toBeTruthy()
    expect(screen.getByText('2.00 bar')).toBeTruthy()
  })

  it('orders charts by sensor group and names each group', () => {
    const sensors = {
      fuel_flow: { label: 'Fuel flow', value: 50, unit: 'm3/h' },
      charge_air_pressure: { label: 'Charge air pressure', value: 0.5, unit: 'kgf/cm2' },
    }
    const two: Replay = { ...replay, frames: replay.frames.map((f) => ({ ...f, sensors })) }
    render(<Traces replay={two} index={0} width={300} height={120} />)
    const captions = screen.getAllByRole('figure').map((f) => f.querySelector('figcaption')?.textContent)
    expect(captions).toEqual(['Charge air pressure0.500 kgf/cm²Air path', 'Fuel flow50.0 m³/hFuel system'])
  })

  it('finds the first alarm time', () => {
    expect(alarmTime(replay)).toBe(130)
    expect(alarmTime({ ...replay, frames: replay.frames.slice(0, 3) })).toBeNull()
  })

  it('splits values into played and future around the current frame', () => {
    const rows = buildSeries(replay, 'a', 2)
    expect(rows.map((r) => r.past)).toEqual([0, 1, 2, null, null])
    expect(rows.map((r) => r.future)).toEqual([null, null, 2, 3, 4])
  })
})
