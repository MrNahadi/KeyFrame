import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import index from './__fixtures__/index.json'
import { durationLabel, loadLabel, RunPicker } from './RunPicker'
import type { RunSummary } from './types'

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

const runs = index as RunSummary[]

describe('RunPicker', () => {
  it('groups runs by fault in plain words with load and duration', async () => {
    render(<RunPicker load={() => Promise.resolve(runs)} />)
    expect(await screen.findByRole('heading', { name: 'Air cooler fouling' })).toBeTruthy()
    expect(screen.getByRole('heading', { name: 'Healthy running' })).toBeTruthy()
    const link = screen.getByRole('link', { name: /Air cooler fouling at 40% load/ })
    expect(link.textContent).toContain('40% load · 2 h 13 min')
  })

  it('opens a run by updating the hash route', async () => {
    render(<RunPicker load={() => Promise.resolve(runs)} />)
    const link = await screen.findByRole('link', { name: /Healthy reference at 60% load/ })
    expect(link.getAttribute('href')).toBe('#/replay/Reference_60')
    fireEvent.click(link)
    await waitFor(() => expect(window.location.hash).toBe('#/replay/Reference_60'))
  })

  it('shows a skeleton while loading', () => {
    render(<RunPicker load={() => new Promise<RunSummary[]>(() => {})} />)
    expect(screen.getByRole('status', { name: 'Loading runs' })).toBeTruthy()
  })

  it('shows an error and retries', async () => {
    const load = vi
      .fn<() => Promise<RunSummary[]>>()
      .mockRejectedValueOnce(new Error('Network down'))
      .mockResolvedValue(runs)
    render(<RunPicker load={load} />)
    expect(await screen.findByText('Network down')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('heading', { name: 'Air cooler fouling' })).toBeTruthy()
    expect(load).toHaveBeenCalledTimes(2)
  })

  it('shows an empty state when there are no runs', async () => {
    render(<RunPicker load={() => Promise.resolve([])} />)
    expect(await screen.findByRole('heading', { name: 'No recorded runs yet' })).toBeTruthy()
  })
})

describe('labels', () => {
  it('reads load from the run id', () => {
    expect(loadLabel('AC_Fouling_85_Load')).toBe('85% load')
    expect(loadLabel('Reference_40')).toBe('40% load')
    expect(loadLabel('Clogged_Injector_Nozzle1_40_60_85_Load')).toBe('40, 60 and 85% load')
    expect(durationLabel(1800)).toBe('30 min')
  })
})
