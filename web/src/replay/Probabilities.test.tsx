import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { Probabilities } from './Probabilities'
import { alarmStatus, clock, duration, probabilitySentence } from './status'
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
  fault: 'f',
  nominal_load: 40,
  switch_on_t: switchOn,
  sampling_note: '',
  provenance: '',
  frames: [100, 200, 300, 400, 500].map((t) => frame(t, alarms[t] ?? 'Normal')),
})

describe('formatting', () => {
  it('formats clock and duration', () => {
    expect(clock(125)).toBe('02:05')
    expect(duration(45)).toBe('45 s')
    expect(duration(438)).toBe('7 min 18 s')
  })
})

describe('probabilitySentence', () => {
  it('names the class and percentage', () => {
    expect(probabilitySentence('AC Fouling', { 'AC Fouling': 0.82 })).toBe(
      'The model reads this as air cooler fouling (82%)',
    )
  })
})

describe('alarmStatus', () => {
  const faulty = make(200, { 400: 'AC Fouling' })

  it('says healthy by design before switch-on', () => {
    expect(alarmStatus(faulty, 0)).toBe('Engine healthy by design until 03:20')
  })
  it('says no alarm yet after switch-on', () => {
    expect(alarmStatus(faulty, 2)).toBe('Fault switched on 100 s ago, no alarm yet'.replace('100 s', '1 min 40 s'))
  })
  it('reports the alarm and its delay after it fires', () => {
    expect(alarmStatus(faulty, 3)).toBe('Alarm: air cooler fouling raised 3 min 20 s after switch-on')
    expect(alarmStatus(faulty, 4)).toContain('Alarm: air cooler fouling raised')
  })
  it('says so at the end of a run with no alarm', () => {
    expect(alarmStatus(make(200), 4)).toBe('Fault switched on 5 min 0 s ago, no alarm was raised in this run')
  })
  it('says no fault in a healthy run', () => {
    expect(alarmStatus(make(null), 2)).toBe('No fault in this run')
  })
  it('flags an alarm in a healthy run', () => {
    expect(alarmStatus(make(null, { 300: 'AC Fouling' }), 3)).toContain('no fault was switched on')
  })
})

describe('Probabilities', () => {
  it('shows a text label and percentage for every class, plus provenance', () => {
    render(<Probabilities replay={make(200)} index={1} />)
    expect(screen.getByText('air cooler fouling')).toBeTruthy()
    expect(screen.getByText('82%')).toBeTruthy()
    expect(screen.getByText('normal running')).toBeTruthy()
    expect(screen.getByText('18%')).toBeTruthy()
    expect(screen.getByRole('status').textContent).toContain('Fault switched on')
    expect(screen.getByText(/never saw this engine load/)).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Model card' }).getAttribute('href')).toBe('#/model-card')
  })
})
