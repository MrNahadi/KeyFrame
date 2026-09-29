import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ReplayScreen } from './ReplayScreen'
import type { Replay, ReplayFrame } from './types'

vi.mock('./Traces', async (importOriginal) => ({
  ...(await importOriginal<typeof import('./Traces')>()),
  Traces: () => <div data-testid="traces" />,
}))

afterEach(cleanup)

const frame = (t: number): ReplayFrame => ({
  t,
  sensors: {},
  probabilities: { Normal: 0.9, 'AC Fouling': 0.1 },
  alarm: 'Normal',
  predicted_class: 'Normal',
  shap_groups: {},
  top_features: [],
})

const replay: Replay = {
  run: 'r',
  fault: 'AC Fouling',
  nominal_load: 40,
  switch_on_t: 400,
  sampling_note: '',
  provenance: 'prov',
  frames: [0, 100, 200, 300, 400, 500].map(frame),
}

const setup = async () => {
  const user = userEvent.setup()
  render(<ReplayScreen runId="r" load={() => Promise.resolve(replay)} />)
  const scrubber = (await screen.findByRole('slider', { name: 'Position in run' })) as HTMLInputElement
  return { user, scrubber }
}

describe('ReplayScreen', () => {
  it('shows a skeleton then the controls', async () => {
    render(<ReplayScreen runId="r" load={() => Promise.resolve(replay)} />)
    expect(screen.getByRole('status', { name: 'Loading replay' })).toBeTruthy()
    expect(await screen.findByRole('button', { name: 'Play' })).toBeTruthy()
  })

  it('shows an error with retry', async () => {
    const load = vi.fn<(id: string) => Promise<Replay>>().mockRejectedValueOnce(new Error('boom'))
    load.mockResolvedValue(replay)
    const user = userEvent.setup()
    render(<ReplayScreen runId="r" load={load} />)
    expect(await screen.findByText('boom')).toBeTruthy()
    await user.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('button', { name: 'Play' })).toBeTruthy()
  })

  it('titles the page with the plain run title from the index', async () => {
    const titles = () =>
      Promise.resolve([
        { id: 'r', title: 'Air cooler fouling at 40% load', duration_s: 500, switch_on_t: 400, alarm_delay_s: null },
      ])
    render(<ReplayScreen runId="r" load={() => Promise.resolve(replay)} loadTitles={titles} />)
    expect((await screen.findByRole('heading', { level: 1 })).textContent).toBe('Air cooler fouling at 40% load')
  })

  it('says which held-out model made the predictions and links the model card', async () => {
    render(<ReplayScreen runId="r" load={() => Promise.resolve(replay)} loadTitles={() => Promise.resolve([])} />)
    expect(await screen.findByText(/never saw 40% load/)).toBeTruthy()
    expect(screen.getByRole('link', { name: 'Model card' }).getAttribute('href')).toBe('#/model-card')
    expect(screen.getByRole('link', { name: 'All runs' }).getAttribute('href')).toBe('#/replay')
  })

  it('shows the low-confidence note only when the model is never confident', async () => {
    const weak: Replay = {
      ...replay,
      frames: replay.frames.map((f) => ({ ...f, probabilities: { Normal: 0.3, 'AC Fouling': 0.2 } })),
    }
    render(<ReplayScreen runId="r" load={() => Promise.resolve(weak)} loadTitles={() => Promise.resolve([])} />)
    expect(await screen.findByText(/barely confident on any reading \(at most 30%\)/)).toBeTruthy()
    cleanup()
    render(<ReplayScreen runId="r" load={() => Promise.resolve(replay)} loadTitles={() => Promise.resolve([])} />)
    await screen.findByRole('button', { name: 'Play' })
    expect(screen.queryByText(/barely confident/)).toBeNull()
  })

  it('gives the scrubber a text value', async () => {
    const { scrubber } = await setup()
    expect(scrubber.getAttribute('aria-valuetext')).toBe('0:00 into the run')
  })

  it('Space toggles play and pause', async () => {
    const { user } = await setup()
    await user.keyboard(' ')
    expect(screen.getByRole('button', { name: 'Pause' })).toBeTruthy()
    await user.keyboard(' ')
    expect(screen.getByRole('button', { name: 'Play' })).toBeTruthy()
  })

  it('arrows step, Home and End jump', async () => {
    const { user, scrubber } = await setup()
    await user.keyboard('{ArrowRight}{ArrowRight}')
    expect(scrubber.value).toBe('2')
    await user.keyboard('{ArrowLeft}')
    expect(scrubber.value).toBe('1')
    await user.keyboard('{End}')
    expect(scrubber.value).toBe('5')
    await user.keyboard('{Home}')
    expect(scrubber.value).toBe('0')
  })

  it('S jumps to fault switch-on', async () => {
    const { user, scrubber } = await setup()
    await user.keyboard('s')
    expect(scrubber.value).toBe('4')
  })

  it('playback advances with animation frames', async () => {
    const raf = vi.spyOn(window, 'requestAnimationFrame')
    const { user, scrubber } = await setup()
    await user.click(screen.getByRole('radio', { name: '60×' }))
    await user.click(screen.getByRole('button', { name: 'Play' }))
    await waitFor(() => expect(raf).toHaveBeenCalled())
    expect(scrubber).toBeTruthy()
    raf.mockRestore()
  })
})
