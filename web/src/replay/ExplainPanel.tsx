import { Pause } from 'lucide-react'
import { featureName } from '../app/vocabulary'
import { Icon } from '../ui/Icon'
import { number, signed } from '../ui/format'
import styles from './ExplainPanel.module.css'
import { className, lowConfidenceNote } from './status'
import type { Replay } from './types'
import { buildWaterfall } from './waterfall'
import { Waterfall } from './Waterfall'

interface ExplainPanelProps {
  replay: Replay
  index: number
  playing: boolean
}

/** The replay JSON carries no base value, so the waterfall starts from zero. */
const BASE = 0

export function ExplainPanel({ replay, index, playing }: ExplainPanelProps) {
  const frame = replay.frames[Math.min(index, replay.frames.length - 1)]
  if (!frame) return null

  if (playing) {
    return (
      <section className={`${styles.panel} ${styles.waiting}`} aria-label="Why the model reads this">
        <Icon icon={Pause} size={16} />
        <p>Pause to see why the model reads it this way.</p>
      </section>
    )
  }

  const cls = className(frame.predicted_class)
  const lead = buildWaterfall(frame.shap_groups, BASE).steps.find((s) => s.sign === 'positive')
  const lowNote = lowConfidenceNote(replay.frames)

  return (
    <section className={styles.panel} aria-labelledby="explain-title">
      <h2 id="explain-title" className={styles.title}>
        Why the model reads this as {cls}
      </h2>
      <p className={styles.summary}>
        {lead
          ? `${lead.name} readings pushed the most towards ${cls}.`
          : `No group of readings pushed towards ${cls}.`}
      </p>
      {lowNote && (
        <p className={styles.lowNote}>This explanation describes a model that is barely confident on this run.</p>
      )}
      <Waterfall groups={frame.shap_groups} base={BASE} target={cls} />
      <h3 className={styles.sub}>Strongest single readings</h3>
      <ol className={styles.features}>
        {frame.top_features.slice(0, 3).map((f) => (
          <li key={f.feature} className={styles.feature}>
            <span className={styles.featureName}>{featureName(f.feature)}</span>
            <span className={styles.featureNumbers}>
              value {number(f.value)}, push {signed(f.shap)}
            </span>
          </li>
        ))}
      </ol>
      <p className={styles.caveat}>Sensors move together, so credit between groups is approximate.</p>
    </section>
  )
}
