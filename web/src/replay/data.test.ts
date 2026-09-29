import { afterEach, describe, expect, it, vi } from 'vitest'
import { loadIndex, loadRun, ReplayDataError } from './data'
import indexFixture from './__fixtures__/index.json'
import runFixture from './__fixtures__/run.json'

function stubFetch(body: unknown, ok = true) {
  const fn = vi.fn(async (_url: string) => ({ ok, status: ok ? 200 : 404, json: async () => body }))
  vi.stubGlobal('fetch', fn)
  return fn
}

afterEach(() => vi.unstubAllGlobals())

describe('loadIndex', () => {
  it('returns typed summaries', async () => {
    const fn = stubFetch(indexFixture)
    const index = await loadIndex()
    expect(index).toHaveLength(2)
    expect(index[0].switch_on_t).toBeNull()
    expect(index[1].alarm_delay_s).toBe(438)
    expect(fn.mock.calls[0][0]).toMatch(/replays\/index\.json$/)
  })

  it('rejects a malformed index', async () => {
    stubFetch([{ id: 'x', title: 'y' }])
    await expect(loadIndex()).rejects.toBeInstanceOf(ReplayDataError)
  })
})

describe('loadRun', () => {
  it('returns a typed replay and encodes the id', async () => {
    const fn = stubFetch(runFixture)
    const run = await loadRun('AC Fouling')
    expect(run.frames[0].probabilities['AC Fouling']).toBe(0.1)
    expect(run.frames[0].top_features[0].feature).toBe('f1')
    expect(fn.mock.calls[0][0]).toMatch(/AC%20Fouling\.json$/)
  })

  it('rejects a malformed frame with a typed error naming the field', async () => {
    const bad = { ...runFixture, frames: [{ ...runFixture.frames[0], alarm: 3 }] }
    stubFetch(bad)
    await expect(loadRun('x')).rejects.toThrow(/frames\[0\]\.alarm/)
  })

  it('rejects a non-object and a failed request', async () => {
    stubFetch('nope')
    await expect(loadRun('x')).rejects.toBeInstanceOf(ReplayDataError)
    stubFetch({}, false)
    await expect(loadRun('x')).rejects.toThrow(/status 404/)
  })
})
