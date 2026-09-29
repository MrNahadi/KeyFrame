import type { Replay, ReplayFrame, RunSummary, SensorReading, TopFeature } from './types'

export class ReplayDataError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ReplayDataError'
  }
}

type Obj = Record<string, unknown>

const fail = (what: string): never => {
  throw new ReplayDataError(`Unexpected replay data: ${what}`)
}

const isObj = (v: unknown): v is Obj => typeof v === 'object' && v !== null && !Array.isArray(v)

const obj = (v: unknown, what: string): Obj => (isObj(v) ? v : fail(`${what} is not an object`))
const str = (v: unknown, what: string): string =>
  typeof v === 'string' ? v : fail(`${what} is not a string`)
const num = (v: unknown, what: string): number =>
  typeof v === 'number' && Number.isFinite(v) ? v : fail(`${what} is not a number`)
const orNull = <T>(v: unknown, what: string, read: (v: unknown, what: string) => T): T | null =>
  v === null ? null : read(v, what)

const numberMap = (v: unknown, what: string): Record<string, number> =>
  Object.fromEntries(Object.entries(obj(v, what)).map(([k, x]) => [k, num(x, `${what}.${k}`)]))

function summary(v: unknown, i: number): RunSummary {
  const w = `index[${i}]`
  const o = obj(v, w)
  return {
    id: str(o.id, `${w}.id`),
    title: str(o.title, `${w}.title`),
    duration_s: num(o.duration_s, `${w}.duration_s`),
    switch_on_t: orNull(o.switch_on_t, `${w}.switch_on_t`, num),
    alarm_delay_s: orNull(o.alarm_delay_s, `${w}.alarm_delay_s`, num),
  }
}

function reading(v: unknown, w: string): SensorReading {
  const o = obj(v, w)
  return {
    label: str(o.label, `${w}.label`),
    value: num(o.value, `${w}.value`),
    unit: str(o.unit, `${w}.unit`),
  }
}

function topFeature(v: unknown, w: string): TopFeature {
  const o = obj(v, w)
  return {
    feature: str(o.feature, `${w}.feature`),
    value: num(o.value, `${w}.value`),
    shap: num(o.shap, `${w}.shap`),
  }
}

function frame(v: unknown, i: number): ReplayFrame {
  const w = `frames[${i}]`
  const o = obj(v, w)
  if (!Array.isArray(o.top_features)) fail(`${w}.top_features is not a list`)
  return {
    t: num(o.t, `${w}.t`),
    sensors: Object.fromEntries(
      Object.entries(obj(o.sensors, `${w}.sensors`)).map(([k, x]) => [
        k,
        reading(x, `${w}.sensors.${k}`),
      ]),
    ),
    probabilities: numberMap(o.probabilities, `${w}.probabilities`),
    alarm: str(o.alarm, `${w}.alarm`),
    predicted_class: str(o.predicted_class, `${w}.predicted_class`),
    shap_groups: numberMap(o.shap_groups, `${w}.shap_groups`),
    top_features: (o.top_features as unknown[]).map((x, j) =>
      topFeature(x, `${w}.top_features[${j}]`),
    ),
  }
}

export function parseIndex(data: unknown): RunSummary[] {
  if (!Array.isArray(data)) return fail('index is not a list')
  return data.map(summary)
}

export function parseRun(data: unknown): Replay {
  const o = obj(data, 'run')
  if (!Array.isArray(o.frames)) fail('frames is not a list')
  return {
    run: str(o.run, 'run'),
    fault: str(o.fault, 'fault'),
    nominal_load: orNull(o.nominal_load, 'nominal_load', num),
    switch_on_t: orNull(o.switch_on_t, 'switch_on_t', num),
    sampling_note: str(o.sampling_note, 'sampling_note'),
    provenance: str(o.provenance, 'provenance'),
    frames: (o.frames as unknown[]).map(frame),
  }
}

async function fetchJson(url: string): Promise<unknown> {
  let res: Response
  try {
    res = await fetch(url)
  } catch {
    throw new ReplayDataError(`Could not reach ${url}`)
  }
  if (!res.ok) throw new ReplayDataError(`Could not load ${url} (status ${res.status})`)
  try {
    return await res.json()
  } catch {
    throw new ReplayDataError(`${url} is not valid JSON`)
  }
}

const base = `${import.meta.env.BASE_URL}replays/`

export async function loadIndex(): Promise<RunSummary[]> {
  return parseIndex(await fetchJson(`${base}index.json`))
}

export async function loadRun(id: string): Promise<Replay> {
  return parseRun(await fetchJson(`${base}${encodeURIComponent(id)}.json`))
}
