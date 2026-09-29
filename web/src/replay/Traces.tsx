import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import { groupOrder, sensorGroup, sensorLabel } from '../app/vocabulary'
import { axisDecimals, fixed, reading } from '../ui/format'
import { alarmTime } from './status'
import styles from './Traces.module.css'
import type { Replay } from './types'

interface TracesProps {
  replay: Replay
  index: number
  /** Fixed size for tests; jsdom measures zero, so ResponsiveContainer is skipped. */
  width?: number
  height?: number
}

export interface TraceRow {
  t: number
  past: number | null
  future: number | null
}

/** Played values (up to the current frame) and future values; both share the current frame so the line is continuous. */
export function buildSeries(replay: Replay, key: string, index: number): TraceRow[] {
  return replay.frames.map((f, i) => {
    const value = f.sensors[key]?.value ?? null
    return {
      t: f.t,
      past: i <= index ? value : null,
      future: i >= index ? value : null,
    }
  })
}

const TICK = { fontSize: 11, fill: 'var(--chart-axis)' }

/** Trend charts like an engine-room trend page: one per sensor, grouped by pipe colour, with live readings. */
export function Traces({ replay, index, width, height }: TracesProps) {
  const first = replay.frames[0]
  if (!first) return null
  const alarmT = alarmTime(replay)
  const frame = replay.frames[Math.min(index, replay.frames.length - 1)]
  const sensors = Object.entries(first.sensors)
    .slice(0, 8)
    .sort((a, b) => groupOrder(sensorGroup(a[0]).key) - groupOrder(sensorGroup(b[0]).key))

  return (
    <section className={styles.section} aria-labelledby="traces-title">
      <h2 id="traces-title" className={styles.heading}>
        Sensor readings
      </h2>
      <div className={styles.grid}>
        {sensors.map(([key, s]) => {
          const g = sensorGroup(key)
          const values = replay.frames.map((f) => f.sensors[key]?.value).filter(Number.isFinite) as number[]
          const decimals = axisDecimals(Math.max(...values) - Math.min(...values))
          const chart = (
            <LineChart
              data={buildSeries(replay, key, index)}
              width={width}
              height={height}
              margin={{ top: 6, right: 4, bottom: 4, left: 0 }}
            >
              <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
              <XAxis dataKey="t" type="number" domain={['dataMin', 'dataMax']} hide />
              <YAxis
                width={44}
                domain={['auto', 'auto']}
                tick={TICK}
                tickCount={3}
                tickFormatter={(v: number) => fixed(v, decimals)}
                axisLine={false}
                tickLine={false}
              />
              <Line
                dataKey="future"
                stroke="var(--trace-future)"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line dataKey="past" stroke={g.colour} strokeWidth={2} dot={false} isAnimationActive={false} />
              {replay.switch_on_t !== null && (
                <ReferenceLine x={replay.switch_on_t} stroke="var(--switch-on)" strokeDasharray="4 3" />
              )}
              {alarmT !== null && <ReferenceLine x={alarmT} stroke="var(--alarm)" strokeWidth={1.5} />}
              <ReferenceLine x={frame.t} stroke="var(--playhead)" strokeOpacity={0.5} />
            </LineChart>
          )
          const now = frame.sensors[key]
          return (
            <figure key={key} className={styles.chart} style={{ ['--group' as string]: g.colour }}>
              <figcaption className={styles.caption}>
                <span className={styles.label}>{sensorLabel(key, s.label)}</span>
                <span className={styles.value}>{reading(now?.value, s.unit)}</span>
                <span className={styles.group}>{g.label}</span>
              </figcaption>
              <div className={styles.plot}>
                {width && height ? (
                  chart
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    {chart}
                  </ResponsiveContainer>
                )}
              </div>
            </figure>
          )
        })}
      </div>
      <p className={styles.key}>
        Coloured line: readings so far. Grey line: the rest of the run. Dashed rule: fault switched on. Red rule:
        alarm.
      </p>
    </section>
  )
}
