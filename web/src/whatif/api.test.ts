import { afterEach, describe, expect, it, vi } from 'vitest'
import { explainWindow, fetchBaselines } from './api'

const baselines = {
  load_bins: [40, 60],
  loads: {
    '40': {
      reading: { 'Engine Speed': 310.5, t: 0 },
      sliders: { 'Engine Speed': { label: 'Engine speed', min: 1, max: 2 } },
    },
    '60': { reading: { 'Engine Speed': 320 }, sliders: {} },
  },
}

const explanation = {
  mode: 'window',
  predicted_class: 'normal',
  probabilities: { normal: 0.9, fault: 0.1 },
  base_value: -1,
  margin: 2,
  groups: { cooling: 0.5 },
  warmup: 0,
  groups_all_classes: { normal: { cooling: 0.5 }, fault: { cooling: -0.5 } },
  top_features: [
    {
      feature: 'a',
      value: 1,
      shap: 0.4,
      source_channels: ['Engine Speed'],
      group: 'cooling',
    },
  ],
  warnings: ['careful'],
}

const reply = (status: number, body: unknown) =>
  vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  })

afterEach(() => vi.unstubAllGlobals())

describe('fetchBaselines', () => {
  it('returns parsed baselines from /api by default', async () => {
    const fetchMock = reply(200, baselines)
    vi.stubGlobal('fetch', fetchMock)
    const result = await fetchBaselines()
    expect(fetchMock.mock.calls[0][0]).toBe('/api/whatif/baselines')
    expect(result).toEqual({ ok: true, value: baselines })
  })

  it('reports an unreachable API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('failed')))
    expect(await fetchBaselines()).toMatchObject({ ok: false, kind: 'unreachable' })
  })

  it('surfaces the API message for a 503', async () => {
    vi.stubGlobal('fetch', reply(503, { detail: 'What-if baselines missing.' }))
    expect(await fetchBaselines()).toEqual({
      ok: false,
      kind: 'error',
      status: 503,
      message: 'What-if baselines missing.',
    })
  })

  it('reports an unexpected shape', async () => {
    vi.stubGlobal('fetch', reply(200, { load_bins: 'x' }))
    expect(await fetchBaselines()).toMatchObject({ ok: false, kind: 'unexpected' })
  })
})

describe('explainWindow', () => {
  const rows = [{ t: 0, 'Engine Speed': 310 }]

  it('posts rows and returns the explanation', async () => {
    const fetchMock = reply(200, explanation)
    vi.stubGlobal('fetch', fetchMock)
    const result = await explainWindow(rows)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/explain')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body)).toEqual({ rows })
    expect(result).toEqual({ ok: true, value: explanation })
  })

  it('reports an unreachable API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('failed')))
    expect(await explainWindow(rows)).toMatchObject({ ok: false, kind: 'unreachable' })
  })

  it('returns the 422 message as a validation error', async () => {
    vi.stubGlobal('fetch', reply(422, { detail: 'Missing required channels: Engine Speed' }))
    expect(await explainWindow(rows)).toEqual({
      ok: false,
      kind: 'validation',
      message: 'Missing required channels: Engine Speed',
    })
  })

  it('joins pydantic 422 detail lists', async () => {
    vi.stubGlobal('fetch', reply(422, { detail: [{ msg: 'bad one' }, { msg: 'bad two' }] }))
    expect(await explainWindow(rows)).toEqual({
      ok: false,
      kind: 'validation',
      message: 'bad one; bad two',
    })
  })

  it('reports an unexpected shape', async () => {
    vi.stubGlobal('fetch', reply(200, { predicted_class: 'normal' }))
    expect(await explainWindow(rows)).toMatchObject({ ok: false, kind: 'unexpected' })
  })
})
