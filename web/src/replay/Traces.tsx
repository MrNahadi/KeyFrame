import { Line, LineChart, ReferenceLine, ResponsiveContainer, XAxis, YAxis } from 'recharts'
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

/** Time of the first frame where the alarm is raised, or null. */
export function alarmTime(replay: Replay): number | null {
  return replay.frames.find((f) => f.alarm !== 'Normal')?.t ?? null
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

export function Traces({ replay, index, width, height }: TracesProps) {
  const first = replay.frames[0]
  if (!first) return null
  const alarmT = alarmTime(replay)
  const nowT = replay.frames[Math.min(index, replay.frames.length - 1)].t

  return (
    <div className={styles.grid} role="group" aria-label="Sensor traces">
      {Object.entries(first.sensors)
        .slice(0, 8)
        .map(([key, s]) => {
          const chart = (
            <LineChart
              data={buildSeries(replay, key, index)}
              width={width}
              height={height}
              margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
            >
              <XAxis dataKey="t" type="number" domain={['dataMin', 'dataMax']} hide />
              <YAxis width={40} domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
              <Line
                dataKey="future"
                stroke="var(--data-future)"
                dot={false}
                isAnimationActive={false}
              />
              <Line
                dataKey="past"
                stroke="var(--data-trace)"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              {replay.switch_on_t !== null && (
                <ReferenceLine
                  x={replay.switch_on_t}
                  stroke="var(--data-marker-switch-on)"
                  strokeDasharray="4 3"
                />
              )}
              {alarmT !== null && (
                <ReferenceLine x={alarmT} stroke="var(--data-marker-alarm)" strokeWidth={2} />
              )}
              <ReferenceLine x={nowT} stroke="var(--text)" />
            </LineChart>
          )
          return (
            <figure key={key} className={styles.chart}>
              <figcaption className={styles.title}>{`${s.label} (${s.unit})`}</figcaption>
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
  )
}
