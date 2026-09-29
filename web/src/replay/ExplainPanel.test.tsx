import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { ExplainPanel } from './ExplainPanel'
import type { Replay } from './types'

afterEach(cleanup)

const make = (max: number): Replay => ({
  run: 'r',
  fault: 'f',
  nominal_load: 40,
  switch_on_t: null,
  sampling_note: '',
  provenance: '',
  frames: [
    {
      t: 0,
      sensors: {},
      probabilities: { Normal: Math.min(0.2, max), 'AC Fouling': max },
      alarm: 'Normal',
      predicted_class: 'AC Fouling',
      shap_groups: { 'air path': 0.6, cooling: -0.2, 'lube oil': 0.1 },
      top_features: [
        { feature: 'Charge air pressure', value: 1.5, shap: 0.4 },
        { feature: 'Coolant flow', value: 2, shap: -0.2 },
        { feature: 'Oil temp', value: 3, shap: 0.1 },
        { feature: 'Extra', value: 4, shap: 0.05 },
      ],
    },
  ],
})

describe('ExplainPanel', () => {
  it('shows the explanation when paused', () => {
    render(<ExplainPanel replay={make(0.9)} index={0} playing={false} width={300} height={200} />)
    expect(screen.getByRole('heading', { name: /Why the model reads this as/ })).toBeTruthy()
    expect(screen.getByText(/Air path readings pushed the most towards/)).toBeTruthy()
    expect(screen.getByText(/Charge air pressure/)).toBeTruthy()
    expect(screen.getByText(/Oil temp/)).toBeTruthy()
    expect(screen.queryByText(/Extra/)).toBeNull()
    expect(screen.getByText('Sensors move together, so credit between groups is approximate.')).toBeTruthy()
    expect(screen.queryByText('Pause to see why')).toBeNull()
    expect(screen.queryByText(/barely confident/)).toBeNull()
  })

  it('shows a hint while playing', () => {
    render(<ExplainPanel replay={make(0.9)} index={0} playing={true} />)
    expect(screen.getByText('Pause to see why')).toBeTruthy()
    expect(screen.queryByRole('heading')).toBeNull()
  })

  it('says the model is barely confident when applicable', () => {
    render(<ExplainPanel replay={make(0.3)} index={0} playing={false} width={300} height={200} />)
    expect(screen.getByText(/describes a model that is barely confident/)).toBeTruthy()
  })
})
