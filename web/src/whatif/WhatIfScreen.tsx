import { useCallback, useEffect, useRef, useState } from 'react'
import { buildWaterfall } from '../replay/waterfall'
import { className, probabilitySentence } from '../replay/status'
import probStyles from '../replay/Probabilities.module.css'
import { explainWindow, fetchBaselines, type ApiFailure, type Baselines, type Explanation } from './api'
import styles from './WhatIfScreen.module.css'

const DEBOUNCE_MS = 250
const WINDOW_S = 900
const STEP_S = 10
const START_COMMAND = 'uv run uvicorn api.main:app --port 8000'

const COLOURS: Record<string, string> = {
  Normal: 'var(--data-neutral)',
  'AC Fouling': 'var(--data-1)',
  'AF Clogging': 'var(--data-2)',
  'Clogged Injector': 'var(--data-3)',
  'CW Pump': 'var(--data-4)',
  'Turbine Degradation': 'var(--data-5)',
}

const signed = (v: number) => `${v < 0 ? '−' : '+'}${Math.abs(v).toFixed(2)}`

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

  return (
    <div className={styles.screen}>
      <h1 className={styles.title}>Try your own readings</h1>
      <p className={styles.notice}>Assumes the engine has held these readings steady for 15 minutes.</p>

      {unreachable && (
        <div className={styles.problem} role="alert">
          <p>{failure.message}</p>
          <p>
            Start the API with <code>{START_COMMAND}</code>, then try again.
          </p>
          <button type="button" className={styles.button} onClick={() => void loadBaselines()}>
            Retry
          </button>
        </div>
      )}

      {!baselines && !failure && (
        <div className={styles.skeleton} role="status" aria-label="Loading">
          Loading readings…
        </div>
      )}

      {baselines && (
        <>
          <div role="radiogroup" aria-label="Engine load" className={styles.segmented}>
            {baselines.load_bins.map((bin) => (
              <button
                key={bin}
                type="button"
                role="radio"
                aria-checked={String(bin) === load}
                className={String(bin) === load ? `${styles.seg} ${styles.segOn}` : styles.seg}
                onClick={() => setLoad(String(bin))}
              >
                {bin}%
              </button>
            ))}
          </div>

          {entry && (
            <div className={styles.sliders}>
              {Object.entries(entry.sliders).map(([channel, s]) => (
                <label key={channel} className={styles.slider}>
                  <span>
                    {s.label}: {values[channel] ?? entry.reading[channel]}
                  </span>
                  <input
                    type="range"
                    min={s.min}
                    max={s.max}
                    step="any"
                    value={values[channel] ?? entry.reading[channel]}
                    onChange={(e) => setValues((v) => ({ ...v, [channel]: Number(e.target.value) }))}
                  />
                  <span className={styles.range}>
                    {s.min} to {s.max}
                  </span>
                </label>
              ))}
              <button type="button" className={styles.button} onClick={() => load && resetTo(load)}>
                Reset to healthy baseline
              </button>
            </div>
          )}

          {failure?.kind === 'validation' && (
            <p className={styles.problem} role="alert">
              {failure.message}
            </p>
          )}

          {!result && !failure && (
            <div className={styles.skeleton} role="status" aria-label="Loading">
              Reading the model…
            </div>
          )}

          {result && (
            <section
              className={updating ? `${styles.result} ${styles.updating}` : styles.result}
              aria-label="Diagnosis"
              aria-busy={updating}
            >
              {updating && <p className={styles.updatingNote}>Updating…</p>}
              <p className={probStyles.sentence}>
                {probabilitySentence(result.predicted_class, result.probabilities)}
              </p>
              <ul className={probStyles.bars}>
                {Object.entries(result.probabilities)
                  .sort((a, b) => b[1] - a[1])
                  .map(([name, p]) => (
                    <li key={name} className={probStyles.row}>
                      <span className={probStyles.name}>{className(name)}</span>
                      <span className={probStyles.track} aria-hidden="true">
                        <span
                          className={probStyles.fill}
                          style={{
                            width: `${Math.round(p * 100)}%`,
                            background: COLOURS[name] ?? 'var(--data-neutral)',
                          }}
                        />
                      </span>
                      <span className={probStyles.pct}>{Math.round(p * 100)}%</span>
                    </li>
                  ))}
              </ul>
              <h2 className={styles.sub}>Why the model reads this as {className(result.predicted_class)}</h2>
              <ul className={styles.steps}>
                {buildWaterfall(result.groups, result.base_value).steps.map((s) => (
                  <li key={s.name}>
                    {s.name}: {signed(s.value)} ({s.sign === 'positive' ? 'towards' : 'away from'}{' '}
                    {className(result.predicted_class)})
                  </li>
                ))}
              </ul>
              {result.warnings.length > 0 && (
                <ul className={styles.warnings}>
                  {result.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              )}
            </section>
          )}
        </>
      )}
    </div>
  )
}
