import { hrefFor } from '../app/routes'
import styles from './Probabilities.module.css'
import { alarmStatus, className, probabilitySentence } from './status'
import type { Replay } from './types'

interface ProbabilitiesProps {
  replay: Replay
  index: number
}

const COLOURS: Record<string, string> = {
  Normal: 'var(--data-neutral)',
  'AC Fouling': 'var(--data-1)',
  'AF Clogging': 'var(--data-2)',
  'Clogged Injector': 'var(--data-3)',
  'CW Pump': 'var(--data-4)',
  'Turbine Degradation': 'var(--data-5)',
}

export function Probabilities({ replay, index }: ProbabilitiesProps) {
  const frame = replay.frames[Math.min(index, replay.frames.length - 1)]
  if (!frame) return null
  const rows = Object.entries(frame.probabilities).sort((a, b) => b[1] - a[1])

  return (
    <section className={styles.panel} aria-label="Model reading">
      <p className={styles.status} role="status">
        {alarmStatus(replay, index)}
      </p>
      <p className={styles.sentence}>{probabilitySentence(frame.predicted_class, frame.probabilities)}</p>
      <ul className={styles.bars}>
        {rows.map(([name, p]) => (
          <li key={name} className={styles.row}>
            <span className={styles.name}>{className(name)}</span>
            <span className={styles.track} aria-hidden="true">
              <span
                className={styles.fill}
                style={{ width: `${Math.round(p * 100)}%`, background: COLOURS[name] ?? 'var(--data-neutral)' }}
              />
            </span>
            <span className={styles.pct}>{Math.round(p * 100)}%</span>
          </li>
        ))}
      </ul>
      <p className={styles.note}>
        Predictions come from a model that never saw this engine load (held-out load).{' '}
        <a href={hrefFor({ page: 'model-card' })}>Model card</a>
      </p>
    </section>
  )
}
