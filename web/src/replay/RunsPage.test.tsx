import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import index from './__fixtures__/index.json'
import { alarmLabel, groupRuns, loadLabel, RunsPage } from './RunsPage'
import type { RunSummary } from './types'

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

const runs = index as RunSummary[]

describe('RunsPage', () => {
  it('lists runs in a table grouped by fault, with load and the alarm result', async () => {
    render(<RunsPage load={() => Promise.resolve(runs)} />)
    const table = await screen.findByRole('table')
    expect(table.textContent).toContain('Air cooler fouling')
    expect(table.textContent).toContain('Healthy running')
    expect(screen.getByRole('columnheader', { name: 'Alarm after switch-on' })).toBeTruthy()
  })

  it('opens a run from its row link', async () => {
    render(<RunsPage load={() => Promise.resolve(runs)} />)
    const links = await screen.findAllByRole('link')
    const link = links.find((l) => l.getAttribute('href') === '#/replay/Reference_60')
    if (!link) throw new Error('no link to Reference_60')
    expect(link.textContent).toBe('Healthy running, 60% load')
    fireEvent.click(link)
    await waitFor(() => expect(window.location.hash).toBe('#/replay/Reference_60'))
  })

  it('offers one primary action to start', async () => {
    render(<RunsPage load={() => Promise.resolve(runs)} />)
    const start = await screen.findByRole('link', { name: /^Play / })
    expect(start.getAttribute('href')).toMatch(/^#\/replay\//)
  })

  it('shows a skeleton while loading', () => {
    render(<RunsPage load={() => new Promise<RunSummary[]>(() => {})} />)
    expect(screen.getByRole('status', { name: 'Loading runs' })).toBeTruthy()
  })

  it('shows an error and retries', async () => {
    const load = vi
      .fn<() => Promise<RunSummary[]>>()
      .mockRejectedValueOnce(new Error('Network down'))
      .mockResolvedValue(runs)
    render(<RunsPage load={load} />)
    expect(await screen.findByText('Network down')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('table')).toBeTruthy()
    expect(load).toHaveBeenCalledTimes(2)
  })

  it('shows an empty state when there are no runs', async () => {
    render(<RunsPage load={() => Promise.resolve([])} />)
    expect(await screen.findByRole('heading', { name: 'No recorded runs yet' })).toBeTruthy()
  })
})

describe('labels', () => {
  it('reads load from the run id', () => {
    expect(loadLabel('AC_Fouling_85_Load')).toBe('85%')
    expect(loadLabel('Reference_40')).toBe('40%')
    expect(loadLabel('Clogged_Injector_Nozzle1_40_60_85_Load')).toBe('40, 60 and 85%')
  })

  it('says what happened to the alarm', () => {
    const base = { id: 'x', title: 'x', duration_s: 100 }
    expect(alarmLabel({ ...base, switch_on_t: 10, alarm_delay_s: 545 })).toBe('9 min 5 s')
    expect(alarmLabel({ ...base, switch_on_t: 10, alarm_delay_s: null })).toBe('No alarm')
    expect(alarmLabel({ ...base, switch_on_t: null, alarm_delay_s: null })).toBe('No fault')
  })

  it('puts healthy running last', () => {
    const names = groupRuns(runs).map((g) => g.name)
    expect(names[names.length - 1]).toBe('Healthy running')
  })
})
