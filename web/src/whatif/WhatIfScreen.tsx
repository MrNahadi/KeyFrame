import { AlertTriangle, Info, Loader2, RotateCcw } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { channelUnit, faultName, featureName, GROUPS, groupOrder, sensorGroup, sensorLabel } from '../app/vocabulary'
import { ProbabilityBars } from '../replay/ProbabilityBars'
import { className } from '../replay/status'
import { Waterfall } from '../replay/Waterfall'
import { Button } from '../ui/Button'
import { number, percent, precise, signed } from '../ui/format'
import { Icon } from '../ui/Icon'
import { Segmented } from '../ui/Segmented'
import { explainWindow, fetchBaselines, type ApiFailure, type Baselines, type Explanation, type Slider } from './api'
import styles from './WhatIfScreen.module.css'

const DEBOUNCE_MS = 250
const WINDOW_S = 900
const STEP_S = 10
const START_COMMAND = 'uv run uvicorn api.main:app --port 8000'

/** The API's explain endpoint takes a window, so hold one reading for 15 minutes. */
const steadyRows = (reading: Record<string, number>) =>
  Array.from({ length: WINDOW_S / STEP_S + 1 }, (_, i) => ({ ...reading, t: i * STEP_S }))

export function WhatIfScreen() {
  const [baselines, setBaselines] = useState<Baselines | null>(null)
  const [failure, setFailure] = useState<ApiFailure | null>(null)
  const [load, setLoad] = useState<string | null>(null)
  const [values, setValues] = useState<Record<string, number>>({})
  const [result, setResult] = useState<Explanation | null>(null)
  const [updating, setUpdating] = useState(false)
  const latest = useRef(0)

  const loadBaselines = useCallback(async () => {
    setFailure(null)
    const res = await fetchBaselines()
    if (!res.ok) {
      setFailure(res)
      return
    }
    setBaselines(res.value)
    const first = res.value.load_bins[0]
    setLoad((cur) => cur ?? (first === undefined ? null : String(first)))
  }, [])

  useEffect(() => {
    void loadBaselines()
  }, [loadBaselines])

  const resetTo = useCallback(
    (key: string) => {
      const entry = baselines?.loads[key]
      if (entry) setValues({ ...entry.reading })
    },
    [baselines],
  )

  useEffect(() => {
    if (load) resetTo(load)
  }, [load, resetTo])

  useEffect(() => {
    if (Object.keys(values).length === 0) return
    const id = ++latest.current
    setUpdating(true)
    const timer = setTimeout(async () => {
      const res = await explainWindow(steadyRows(values))
      if (id !== latest.current) return
      setUpdating(false)
      if (res.ok) {
        setResult(res.value)
        setFailure(null)
      } else {
        setFailure(res)
      }
    }, DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [values])

  const entry = load ? baselines?.loads[load] : undefined
  const unreachable = failure !== null && failure.kind !== 'validation'
  const changed = entry
    ? Object.keys(entry.sliders).filter((c) => values[c] !== undefined && values[c] !== entry.reading[c]).length
    : 0

  return (
    <div className={styles.screen}>
      <header className={styles.header}>
        <h1 className={styles.title}>Try your own readings</h1>
        <p className={styles.lead}>
          Start from a healthy engine, move a reading and see what the model makes of it.
        </p>
        <p className={styles.notice}>
          <Icon icon={Info} size={16} />
          <span>Assumes the engine has held these readings steady for 15 minutes.</span>
        </p>
      </header>

      {unreachable && (
        <section className={styles.problem} role="alert">
          <Icon icon={AlertTriangle} size={20} />
          <div className={styles.problemBody}>
            <h2 className={styles.problemTitle}>The model&rsquo;s API is not answering</h2>
            <p>{failure.message}</p>
            <p>
              Start it from the repository root with <code className={styles.code}>{START_COMMAND}</code>, then
              retry.
            </p>
            <div>
              <Button variant="primary" onClick={() => void loadBaselines()}>
                Retry
              </Button>
            </div>
          </div>
        </section>
      )}

      {!baselines && !failure && (
        <div className={styles.skeleton} role="status" aria-label="Loading">
          Loading the healthy baselines…
        </div>
      )}

      {baselines && (
        <div className={styles.body}>
          <section className={styles.controls} aria-label="Readings">
            <div className={styles.toolbar}>
              <div className={styles.load}>
                <span className={styles.toolbarLabel} aria-hidden="true">
                  Engine load
                </span>
                <Segmented
                  label="Engine load"
                  options={baselines.load_bins.map((bin) => ({ value: String(bin), label: `${bin}%` }))}
                  value={load ?? ''}
                  onChange={setLoad}
                />
              </div>
              <Button variant="tertiary" onClick={() => load && resetTo(load)} disabled={changed === 0}>
                <Icon icon={RotateCcw} size={16} />
                Reset to healthy baseline
              </Button>
            </div>

            {entry && <SliderGroups entry={entry} values={values} setValues={setValues} />}
            {result && (
              // Phones only: the full diagnosis sits below the sliders, so keep its verdict in view.
              <p className={styles.dock} aria-hidden="true">
                <span className={styles.dockLabel}>{updating ? 'Updating…' : 'The model reads this as'}</span>
                <span className={styles.dockValue}>
                  {faultName(result.predicted_class)}{' '}
                  {percent(result.probabilities[result.predicted_class] ?? 0)}
                </span>
              </p>
            )}
          </section>

          <section
            className={updating && result ? `${styles.result} ${styles.updating}` : styles.result}
            aria-label="Diagnosis"
            aria-busy={updating}
          >
            {failure?.kind === 'validation' && (
              <p className={styles.validation} role="alert">
                {failure.message}
              </p>
            )}
            {!result && !failure && (
              <div className={styles.waiting} role="status" aria-label="Loading">
                Reading the model…
              </div>
            )}
            {result && <Diagnosis result={result} updating={updating} />}
          </section>
        </div>
      )}
    </div>
  )
}

interface SliderGroupsProps {
  entry: { reading: Record<string, number>; sliders: Record<string, Slider> }
  values: Record<string, number>
  setValues: (update: (v: Record<string, number>) => Record<string, number>) => void
}

function SliderGroups({ entry, values, setValues }: SliderGroupsProps) {
  const channels = Object.keys(entry.sliders).sort(
    (a, b) => groupOrder(sensorGroup(a).key) - groupOrder(sensorGroup(b).key),
  )
  const groups = [...GROUPS, sensorGroup('other')]
    .map((g) => ({ g, channels: channels.filter((c) => sensorGroup(c).key === g.key) }))
    .filter((x) => x.channels.length > 0)

  return (
    <div className={styles.groups}>
      {groups.map(({ g, channels: list }) => (
        <fieldset key={g.key} className={styles.group} style={{ ['--group' as string]: g.colour }}>
          <legend className={styles.legend}>{g.label}</legend>
          {list.map((channel) => {
            const s = entry.sliders[channel]
            const base = entry.reading[channel]
            const value = values[channel] ?? base
            const u = channelUnit(channel)
            const range = s.max - s.min
            const delta = value - base
            const show = (v: number, withUnit = true) => precise(v, range, withUnit ? u : '')
            const moved = Math.abs(delta) > range / 1000
            const id = `slider-${channel.replace(/\W+/g, '-')}`
            return (
              <div key={channel} className={styles.slider}>
                <label htmlFor={id} className={styles.sliderLabel}>
                  {sensorLabel(channel, s.label)}
                </label>
                <output htmlFor={id} className={styles.sliderValue}>
                  {show(value)}
                </output>
                <input
                  id={id}
                  className={styles.range}
                  type="range"
                  min={s.min}
                  max={s.max}
                  step={range / 200}
                  value={value}
                  aria-valuetext={show(value)}
                  onChange={(e) => setValues((v) => ({ ...v, [channel]: Number(e.target.value) }))}
                />
                <span className={styles.scale}>
                  <span>{show(s.min, false)}</span>
                  <span className={moved ? styles.moved : undefined}>
                    {moved
                      ? `${delta < 0 ? '−' : '+'}${show(Math.abs(delta))} from healthy`
                      : `Healthy ${show(base, false)}`}
                  </span>
                  <span>{show(s.max, false)}</span>
                </span>
              </div>
            )
          })}
        </fieldset>
      ))}
    </div>
  )
}

function Diagnosis({ result, updating }: { result: Explanation; updating: boolean }) {
  const cls = className(result.predicted_class)
  const p = result.probabilities[result.predicted_class]
  return (
    <>
      <div className={styles.verdict}>
        <p className={styles.verdictLabel}>
          The model reads this as
          {updating && (
            <span className={styles.updatingNote}>
              <Icon icon={Loader2} size={16} />
              Updating…
            </span>
          )}
        </p>
        <p className={styles.verdictValue}>
          {cls.charAt(0).toUpperCase() + cls.slice(1)}
          {p !== undefined && <span className={styles.verdictPct}> {percent(p)}</span>}
        </p>
      </div>
      <ProbabilityBars probabilities={result.probabilities} predicted={result.predicted_class} />
      <div className={styles.why}>
        <h2 className={styles.whyTitle}>Why the model reads this as {cls}</h2>
        <Waterfall groups={result.groups} base={result.base_value} target={cls} />
        {result.top_features.length > 0 && (
          <>
            <h3 className={styles.sub}>Strongest single readings</h3>
            <ol className={styles.features}>
              {result.top_features.slice(0, 3).map((f) => (
                <li key={f.feature}>
                  <span>{featureName(f.feature)}</span>
                  <span className={styles.featureNumbers}>
                    value {number(f.value)}, push {signed(f.shap)}
                  </span>
                </li>
              ))}
            </ol>
          </>
        )}
      </div>
      {result.warnings.length > 0 && (
        <ul className={styles.warnings}>
          {result.warnings.map((w) => (
            <li key={w}>
              <Icon icon={Info} size={16} />
              <span>{w}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
