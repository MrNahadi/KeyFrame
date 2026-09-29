import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as api from './api'
import { WhatIfScreen } from './WhatIfScreen'

vi.mock('./api')

afterEach(cleanup)

const baselines: api.Baselines = {
  load_bins: [40, 60],
  loads: {
    '40': {
      reading: { 'Engine Speed': 310, t: 0 },
      sliders: { 'Engine Speed': { label: 'Engine speed', min: 300, max: 320 } },
    },
    '60': {
      reading: { 'Engine Speed': 330 },
      sliders: { 'Engine Speed': { label: 'Engine speed', min: 320, max: 340 } },
    },
  },
}

const explanation = (predicted: string): api.Explanation => ({
  mode: 'window',
  predicted_class: predicted,
  probabilities: { Normal: 0.7, 'AC Fouling': 0.3 },
  base_value: 0,
  margin: 1,
  groups: { cooling: 0.5 },
  warmup: 0,
  groups_all_classes: {},
  top_features: [],
  warnings: ['Check the sensor range.'],
})

/** The verdict line, whose name and percentage sit in separate elements. */
const verdict = (text: string) => (_: string, el: Element | null) => el?.tagName === 'P' && el.textContent === text

const slider = () => screen.getByRole('slider') as HTMLInputElement

beforeEach(() => {
  vi.mocked(api.fetchBaselines).mockResolvedValue({ ok: true, value: baselines })
  vi.mocked(api.explainWindow).mockReset()
  vi.mocked(api.explainWindow).mockResolvedValue({ ok: true, value: explanation('Normal') })
})

describe('WhatIfScreen', () => {
  it('shows the steady-state notice and loads the baseline for the chosen load', async () => {
    render(<WhatIfScreen />)
    expect(screen.getByText(/held these readings steady for 15 minutes/)).toBeTruthy()
    await waitFor(() => expect(slider().value).toBe('310'))
    fireEvent.click(screen.getByRole('radio', { name: '60%' }))
    await waitFor(() => expect(slider().value).toBe('330'))
    expect(screen.getByText(/held these readings steady/)).toBeTruthy()
  })

  it('sends one debounced request per burst of slider changes', async () => {
    render(<WhatIfScreen />)
    await waitFor(() => expect(api.explainWindow).toHaveBeenCalledTimes(1))
    fireEvent.change(slider(), { target: { value: '312' } })
    fireEvent.change(slider(), { target: { value: '315' } })
    expect(api.explainWindow).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(api.explainWindow).toHaveBeenCalledTimes(2))
    const rows = vi.mocked(api.explainWindow).mock.calls[1][0]
    expect(rows[0]['Engine Speed']).toBe(315)
    expect(rows.length).toBeGreaterThan(1)
  })

  it('lets the latest response win', async () => {
    let releaseFirst: (r: api.ApiResult<api.Explanation>) => void = () => {}
    vi.mocked(api.explainWindow)
      .mockReturnValueOnce(new Promise((res) => (releaseFirst = res)))
      .mockResolvedValueOnce({ ok: true, value: explanation('AC Fouling') })
    render(<WhatIfScreen />)
    await waitFor(() => expect(api.explainWindow).toHaveBeenCalledTimes(1))
    fireEvent.change(slider(), { target: { value: '312' } })
    await screen.findByText(verdict('Air cooler fouling 30%'))
    releaseFirst({ ok: true, value: explanation('Normal') })
    await new Promise((r) => setTimeout(r, 20))
    expect(screen.getByText(verdict('Air cooler fouling 30%'))).toBeTruthy()
  })

  it('shows each reading with its unit and how far it has moved from healthy', async () => {
    const withUnits: api.Baselines = {
      load_bins: [40],
      loads: {
        '40': {
          reading: { 'Fuel Flow': 28 },
          sliders: { 'Fuel Flow': { label: 'Fuel flow', min: 20, max: 60 } },
        },
      },
    }
    vi.mocked(api.fetchBaselines).mockResolvedValue({ ok: true, value: withUnits })
    render(<WhatIfScreen />)
    await waitFor(() => expect(slider().value).toBe('28'))
    await screen.findByText(verdict('Normal running 70%'))
    expect(screen.getByRole('group', { name: 'Fuel system' })).toBeTruthy()
    expect(slider().getAttribute('aria-valuetext')).toBe('28.0 m³/h')
    expect(screen.getByText('Healthy 28.0')).toBeTruthy()
    const reset = screen.getByRole('button', { name: 'Reset to healthy baseline' }) as HTMLButtonElement
    expect(reset.disabled).toBe(true)
    fireEvent.change(slider(), { target: { value: '31' } })
    expect(await screen.findByText('+3.00 m³/h from healthy')).toBeTruthy()
    fireEvent.click(reset)
    await waitFor(() => expect(slider().value).toBe('28'))
  })

  it('shows the API warnings', async () => {
    render(<WhatIfScreen />)
    expect(await screen.findByText('Check the sensor range.')).toBeTruthy()
  })

  it('explains how to start the API and retries', async () => {
    vi.mocked(api.fetchBaselines).mockResolvedValueOnce({
      ok: false,
      kind: 'unreachable',
      message: 'The API could not be reached.',
    })
    render(<WhatIfScreen />)
    expect(await screen.findByText(/uv run uvicorn api.main:app --port 8000/)).toBeTruthy()
    expect(screen.getByText(/held these readings steady/)).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))
    await waitFor(() => expect(slider().value).toBe('310'))
  })

  it('shows the API message on a validation error', async () => {
    vi.mocked(api.explainWindow).mockResolvedValue({
      ok: false,
      kind: 'validation',
      message: 'Engine Speed is out of range.',
    })
    render(<WhatIfScreen />)
    expect(await screen.findByText('Engine Speed is out of range.')).toBeTruthy()
  })
})
