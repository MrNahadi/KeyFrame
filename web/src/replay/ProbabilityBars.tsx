import { faultName } from '../app/vocabulary'
import { percent } from '../ui/format'
import styles from './ProbabilityBars.module.css'

interface ProbabilityBarsProps {
  probabilities: Record<string, number>
  predicted: string
}

/** Every class with a text label and percentage; the model's leading class in ink, the rest grey. */
export function ProbabilityBars({ probabilities, predicted }: ProbabilityBarsProps) {
  const rows = Object.entries(probabilities).sort((a, b) => b[1] - a[1])
  return (
    <ul className={styles.bars}>
      {rows.map(([name, p]) => {
        const lead = name === predicted
        return (
          <li key={name} className={lead ? `${styles.row} ${styles.lead}` : styles.row}>
            <span className={styles.name}>{faultName(name)}</span>
            <span className={styles.track} aria-hidden="true">
              <span className={styles.fill} style={{ width: `${Math.max(0, Math.min(1, p)) * 100}%` }} />
            </span>
            <span className={styles.pct}>{percent(p)}</span>
          </li>
        )
      })}
    </ul>
  )
}
