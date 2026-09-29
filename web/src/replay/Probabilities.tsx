import { Keyframe } from '../ui/Keyframe'
import styles from './Probabilities.module.css'
import { ProbabilityBars } from './ProbabilityBars'
import { alarmState, probabilitySentence } from './status'
import type { Replay } from './types'

interface ProbabilitiesProps {
  replay: Replay
  index: number
}

/** The model's reading at the current moment: has the alarm fired, and what does the model think. */
export function Probabilities({ replay, index }: ProbabilitiesProps) {
  const frame = replay.frames[Math.min(index, replay.frames.length - 1)]
  if (!frame) return null
  const state = alarmState(replay, index)
  const alarm = state.kind === 'alarm' || state.kind === 'false-alarm'

  return (
    <section className={styles.panel} aria-labelledby="reading-title">
      <div className={alarm ? `${styles.status} ${styles.alarm}` : styles.status}>
        {alarm && (
          <span className={styles.mark}>
            <Keyframe kind="alarm" size={18} />
          </span>
        )}
        <div>
          <p className={styles.headline} role="status">
            {state.headline}
          </p>
          <p className={styles.detail}>{state.detail}</p>
        </div>
      </div>
      <div className={styles.reading}>
        <h2 id="reading-title" className={styles.title}>
          Model&rsquo;s reading
        </h2>
        <p className={styles.sentence}>{probabilitySentence(frame.predicted_class, frame.probabilities)}.</p>
        <ProbabilityBars probabilities={frame.probabilities} predicted={frame.predicted_class} />
      </div>
    </section>
  )
}
