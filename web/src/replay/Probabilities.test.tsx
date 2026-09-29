import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { Probabilities } from './Probabilities'
import { alarmState, className, heldOutNote, probabilitySentence } from './status'
import type { Replay, ReplayFrame } from './types'

afterEach(cleanup)

const frame = (t: number, alarm: string): ReplayFrame => ({
  t,
  sensors: {},
  probabilities: { Normal: 0.18, 'AC Fouling': 0.82 },
  alarm,
  predicted_class: 'AC Fouling',
  shap_groups: {},
  top_features: [],
})

const make = (switchOn: number | null, alarms: Record<number, string> = {}): Replay => ({
  run: 'r',
  fault: 'AC',
  nominal_load: 40,
  switch_on_t: switchOn,
  sampling_note: '',
  provenance: '',
  frames: [100, 200, 300, 400, 500].map((t) => frame(t, alarms[t] ?? 'Normal')),
})

describe('probabilitySentence', () => {
  it('names the class and percentage', () => {
    expect(probabilitySentence('AC Fouling', { 'AC Fouling': 0.82 })).toBe(
      'The model reads this as air cooler fouling (82%)',
    )
  })

  it('understands the class codes in the real replay files', () => {
    expect(probabilitySentence('AC', { AC: 0.9 })).toBe('The model reads this as air cooler fouling (90%)')
    expect(className('INJ')).toBe('injector nozzle clogging')
    expect(className('Normal')).toBe('normal running')
  })
})

describe('alarmState', () => {
  const faulty = make(200, { 400: 'AC' })

  it('says healthy by design before switch-on', () => {
    expect(alarmState(faulty, 0)).toMatchObject({ kind: 'healthy', detail: 'The fault is switched on at 3:20.' })
  })
  it('says no alarm yet after switch-on', () => {
    expect(alarmState(faulty, 2)).toMatchObject({
      kind: 'fault-on',
      headline: 'Fault on, no alarm yet',
      detail: 'Switched on 1 min 40 s ago.',
    })
  })
  it('reports the alarm and its delay after it fires', () => {
    expect(alarmState(faulty, 3)).toEqual({
      kind: 'alarm',
      headline: 'Alarm: air cooler fouling',
      detail: 'Raised 3 min 20 s after switch-on.',
    })
    expect(alarmState(faulty, 4).kind).toBe('alarm')
  })
  it('says plainly when the alarm names the wrong fault', () => {
    expect(alarmState(make(200, { 400: 'TD' }), 3).detail).toBe(
      'Raised 3 min 20 s after switch-on. The fault switched on was air cooler fouling.',
    )
  })
  it('says so at the end of a run with no alarm', () => {
    expect(alarmState(make(200), 4)).toMatchObject({
      kind: 'missed',
      detail: 'The fault ran for 5 min 0 s and the model never raised the alarm.',
    })
  })
  it('says no fault in a healthy run', () => {
    expect(alarmState(make(null), 2).headline).toBe('No fault in this run')
  })
  it('flags an alarm in a healthy run', () => {
    expect(alarmState(make(null, { 300: 'AC' }), 3)).toMatchObject({
      kind: 'false-alarm',
      detail: 'Raised though no fault was switched on in this run.',
    })
  })
})

describe('heldOutNote', () => {
  it('names the held-out load, or says the load changes', () => {
    const r = make(null)
    expect(heldOutNote({ ...r, provenance: 'predictions from ... (leave-one-load-out fold 75); git commit x' })).toBe(
      'Predictions come from a model that never saw 75% load.',
    )
    expect(heldOutNote({ ...r, provenance: '(leave-one-load-out fold 40, 60, 75, 85); git' })).toContain(
      'The load changes during this run',
    )
    expect(heldOutNote(r)).toBe('Predictions come from a model that never saw 40% load.')
  })
})

describe('Probabilities', () => {
  it('shows the status and a text label and percentage for every class, leading class first', () => {
    render(<Probabilities replay={make(200)} index={1} />)
    expect(screen.getByRole('status').textContent).toBe('Fault on, no alarm yet')
    const rows = screen.getAllByRole('listitem').map((li) => li.textContent)
    expect(rows).toEqual(['Air cooler fouling82%', 'Normal running18%'])
  })

  it('marks the alarm', () => {
    render(<Probabilities replay={make(200, { 300: 'AC' })} index={2} />)
    expect(screen.getByRole('status').textContent).toBe('Alarm: air cooler fouling')
  })
})
