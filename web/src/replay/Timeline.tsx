import { clock } from '../ui/format'
import { Keyframe } from '../ui/Keyframe'
import styles from './Timeline.module.css'

interface TimelineProps {
  times: readonly number[]
  index: number
  switchOnT: number | null
  alarmT: number | null
  onSeek: (index: number) => void
}

/** Room, in percent of the track, a span needs before its name fits inside it. */
const LABEL_ROOM = 14

/**
 * The keyframe timeline: the whole run as one strip, healthy then faulty, with the fault
 * switch-on and the alarm drawn as keyframes. It is also the scrubber (a native range input
 * laid over the strip, so keyboard and assistive technology work as usual).
 */
export function Timeline({ times, index, switchOnT, alarmT, onSeek }: TimelineProps) {
  const t0 = times[0] ?? 0
  const t1 = times[times.length - 1] ?? 0
  const span = t1 - t0 || 1
  const at = (t: number) => Math.min(100, Math.max(0, ((t - t0) / span) * 100))
  const now = times[Math.min(index, times.length - 1)] ?? t0
  const switchPos = switchOnT === null ? 100 : at(switchOnT)
  const last = Math.max(0, times.length - 1)

  return (
    <div className={styles.wrap}>
      <div className={styles.timeline}>
        <div className={styles.track} aria-hidden="true">
          <span className={styles.healthy} style={{ width: `${switchPos}%` }}>
            {switchPos >= LABEL_ROOM && 'Healthy'}
          </span>
          {switchOnT !== null && (
            <span className={styles.fault} style={{ left: `${switchPos}%` }}>
              {100 - switchPos >= LABEL_ROOM && 'Faulty'}
            </span>
          )}
          <span className={styles.played} style={{ width: `${at(now)}%` }} />
          {switchOnT !== null && (
            <span className={styles.key} style={{ left: `${switchPos}%` }}>
              <Keyframe kind="switch-on" size={18} />
            </span>
          )}
          {alarmT !== null && (
            <span className={styles.key} style={{ left: `${at(alarmT)}%` }}>
              <Keyframe kind="alarm" size={18} />
            </span>
          )}
          <span className={styles.playhead} style={{ left: `${at(now)}%` }} />
        </div>
        <input
          className={styles.input}
          type="range"
          aria-label="Position in run"
          min={0}
          max={last}
          step={1}
          value={index}
          aria-valuetext={`${clock(now - t0)} into the run`}
          onChange={(e) => onSeek(Number(e.target.value))}
        />
      </div>
      <div className={styles.scale}>
        <span>{clock(0)}</span>
        <span className={styles.keys}>
          {switchOnT !== null && (
            <span className={styles.legend}>
              <Keyframe kind="switch-on" size={12} />
              Fault switched on at {clock(switchOnT - t0)}
            </span>
          )}
          {alarmT !== null && (
            <span className={styles.legend}>
              <Keyframe kind="alarm" size={12} />
              Alarm at {clock(alarmT - t0)}
            </span>
          )}
          {switchOnT === null && <span className={styles.legend}>No fault in this run</span>}
          {switchOnT !== null && alarmT === null && <span className={styles.legend}>No alarm</span>}
        </span>
        <span>{clock(t1 - t0)}</span>
      </div>
    </div>
  )
}
