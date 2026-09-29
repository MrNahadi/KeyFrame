import { Bar, BarChart, Cell, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import styles from './ExplainPanel.module.css'
import { className, lowConfidenceNote } from './status'
import type { Replay } from './types'
import { buildWaterfall } from './waterfall'

interface ExplainPanelProps {
  replay: Replay
  index: number
  playing: boolean
  /** Fixed size for tests; jsdom measures zero, so ResponsiveContainer is skipped. */
  width?: number
  height?: number
}

/** The replay JSON carries no base value, so the waterfall starts from zero. */
const BASE = 0

const signed = (v: number) => `${v < 0 ? '−' : '+'}${Math.abs(v).toFixed(2)}`

export function ExplainPanel({ replay, index, playing, width, height }: ExplainPanelProps) {
  const frame = replay.frames[Math.min(index, replay.frames.length - 1)]
  if (!frame) return null

  if (playing) {
    return (
      <section className={styles.panel} aria-label="Why the model reads this">
        <p className={styles.hint}>Pause to see why</p>
      </section>
    )
  }

  const cls = className(frame.predicted_class)
  const wf = buildWaterfall(frame.shap_groups, BASE)
  const lead = wf.steps.find((s) => s.sign === 'positive')
  const lowNote = lowConfidenceNote(replay.frames)
  const data = wf.steps.map((s) => ({
    name: s.name,
    range: [Math.min(s.start, s.end), Math.max(s.start, s.end)] as [number, number],
    sign: s.sign,
  }))

  const chart = (
    <BarChart
      data={data}
      layout="vertical"
      width={width}
      height={height}
      margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
    >
      <XAxis type="number" domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
      <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
      <Bar dataKey="range" isAnimationActive={false}>
        {data.map((d) => (
          <Cell key={d.name} fill={d.sign === 'positive' ? 'var(--data-1)' : 'var(--data-neutral)'} />
        ))}
      </Bar>
    </BarChart>
  )

  return (
    <section className={styles.panel} aria-label="Why the model reads this">
      <h2 className={styles.title}>Why the model reads this as {cls}</h2>
      <p className={styles.summary}>
        {lead
          ? `${lead.name} readings pushed the most towards ${cls}.`
          : `No group of readings pushed towards ${cls}.`}
      </p>
      {lowNote && (
        <p className={styles.lowNote}>
          This explanation describes a model that is barely confident on this run.
        </p>
      )}
      <div className={styles.plot}>
        {width && height ? (
          chart
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {chart}
          </ResponsiveContainer>
        )}
      </div>
      <ul className={styles.steps}>
        {wf.steps.map((s) => (
          <li key={s.name}>
            {s.name}: {signed(s.value)} ({s.sign === 'positive' ? 'towards' : 'away from'} {cls})
          </li>
        ))}
      </ul>
      <h3 className={styles.sub}>Top features</h3>
      <ul className={styles.features}>
        {frame.top_features.slice(0, 3).map((f) => (
          <li key={f.feature}>
            {f.feature}: value {f.value}, push {signed(f.shap)}
          </li>
        ))}
      </ul>
      <p className={styles.caveat}>Sensors move together, so credit between groups is approximate.</p>
    </section>
  )
}
