export type Slider = { label: string; min: number; max: number }

export type LoadBaseline = {
  reading: Record<string, number>
  sliders: Record<string, Slider>
}

export type Baselines = {
  load_bins: number[]
  loads: Record<string, LoadBaseline>
}

export type ExplainFeature = {
  feature: string
  value: number
  shap: number
  source_channels: string[]
  group: string
}

export type Explanation = {
  mode: string
  predicted_class: string
  probabilities: Record<string, number>
  base_value: number
  margin: number
  groups: Record<string, number>
  warmup: number
  groups_all_classes: Record<string, Record<string, number>>
  top_features: ExplainFeature[]
  warnings: string[]
}

export type ApiFailure =
  | { ok: false; kind: 'unreachable'; message: string }
  | { ok: false; kind: 'validation'; message: string }
  | { ok: false; kind: 'error'; status: number; message: string }
  | { ok: false; kind: 'unexpected'; message: string }

export type ApiResult<T> = { ok: true; value: T } | ApiFailure

type Obj = Record<string, unknown>

const isObj = (v: unknown): v is Obj => typeof v === 'object' && v !== null && !Array.isArray(v)
const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)
const isNumMap = (v: unknown): v is Record<string, number> =>
  isObj(v) && Object.values(v).every(isNum)
const isStrList = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every((s) => typeof s === 'string')

const isSlider = (v: unknown): v is Slider =>
  isObj(v) && typeof v.label === 'string' && isNum(v.min) && isNum(v.max)

const isLoad = (v: unknown): v is LoadBaseline =>
  isObj(v) && isNumMap(v.reading) && isObj(v.sliders) && Object.values(v.sliders).every(isSlider)

const isBaselines = (v: unknown): v is Baselines =>
  isObj(v) &&
  Array.isArray(v.load_bins) &&
  v.load_bins.every(isNum) &&
  isObj(v.loads) &&
  Object.values(v.loads).every(isLoad)

const isFeature = (v: unknown): v is ExplainFeature =>
  isObj(v) &&
  typeof v.feature === 'string' &&
  isNum(v.value) &&
  isNum(v.shap) &&
  isStrList(v.source_channels) &&
  typeof v.group === 'string'

const isExplanation = (v: unknown): v is Explanation =>
  isObj(v) &&
  typeof v.mode === 'string' &&
  typeof v.predicted_class === 'string' &&
  isNumMap(v.probabilities) &&
  isNum(v.base_value) &&
  isNum(v.margin) &&
  isNumMap(v.groups) &&
  isNum(v.warmup) &&
  isObj(v.groups_all_classes) &&
  Object.values(v.groups_all_classes).every(isNumMap) &&
  Array.isArray(v.top_features) &&
  v.top_features.every(isFeature) &&
  isStrList(v.warnings)

const apiBase = (): string => import.meta.env.VITE_API_BASE ?? '/api'

// FastAPI sends `detail` as a string, or as a list of `{msg}` for schema errors.
const detailOf = (body: unknown, fallback: string): string => {
  if (!isObj(body)) return fallback
  const { detail } = body
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const msgs = detail.flatMap((d) => (isObj(d) && typeof d.msg === 'string' ? [d.msg] : []))
    if (msgs.length > 0) return msgs.join('; ')
  }
  return fallback
}

async function request<T>(
  path: string,
  init: RequestInit | undefined,
  guard: (v: unknown) => v is T,
  what: string,
): Promise<ApiResult<T>> {
  let response: Response
  try {
    response = await fetch(`${apiBase()}${path}`, init)
  } catch {
    return { ok: false, kind: 'unreachable', message: 'The API could not be reached.' }
  }
  let body: unknown
  try {
    body = await response.json()
  } catch {
    body = undefined
  }
  if (response.status === 422) {
    return { ok: false, kind: 'validation', message: detailOf(body, 'The request was rejected.') }
  }
  if (!response.ok) {
    return {
      ok: false,
      kind: 'error',
      status: response.status,
      message: detailOf(body, `The API returned status ${response.status}.`),
    }
  }
  if (!guard(body)) {
    return { ok: false, kind: 'unexpected', message: `Unexpected ${what} from the API.` }
  }
  return { ok: true, value: body }
}

export const fetchBaselines = (): Promise<ApiResult<Baselines>> =>
  request('/whatif/baselines', undefined, isBaselines, 'baselines response')

export const explainWindow = (rows: Record<string, number>[]): Promise<ApiResult<Explanation>> =>
  request(
    '/explain',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rows }),
    },
    isExplanation,
    'explain response',
  )
