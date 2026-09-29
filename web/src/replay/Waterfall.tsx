import { group } from '../app/vocabulary'
import { signed } from '../ui/format'
import styles from './Waterfall.module.css'
import { buildWaterfall } from './waterfall'

interface WaterfallProps {
  groups: Record<string, number>
  base: number
  /** The class being explained, in words, e.g. "air cooler fouling". */
  target: string
}

const pct = (v: number, lo: number, span: number) => ((v - lo) / span) * 100

/**
 * Grouped contributions as a waterfall: each sensor group moves the model's score from the
 * base to the output. Direction, sign text and a label carry the meaning; colour only names
 * the group (pipe colours), and pushes away from the class are drawn hollow.
 */
export function Waterfall({ groups, base, target }: WaterfallProps) {
  const wf = buildWaterfall(groups, base)
  const points = [base, wf.output, 0, ...wf.steps.flatMap((s) => [s.start, s.end])]
  const lo = Math.min(...points)
  const hi = Math.max(...points)
  const span = hi - lo || 1
  const zero = pct(0, lo, span)

  return (
    <figure className={styles.figure}>
      <figcaption className={styles.caption}>
        Push on the model&rsquo;s score for {target}, by sensor group (log-odds, starting from{' '}
        {signed(base)})
      </figcaption>
      <ol className={styles.steps}>
        {wf.steps.map((s) => {
          const g = group(s.name)
          const left = pct(Math.min(s.start, s.end), lo, span)
          const width = Math.max(0.6, pct(Math.max(s.start, s.end), lo, span) - left)
          const towards = s.sign === 'positive'
          return (
            <li key={s.name} className={styles.step} style={{ ['--group' as string]: g.colour }}>
              <span className={styles.name}>
                <span className={styles.swatch} aria-hidden="true" />
                {g.label}
              </span>
              <span className={styles.track} aria-hidden="true">
                <span className={styles.zero} style={{ left: `${zero}%` }} />
                <span
                  className={towards ? `${styles.bar} ${styles.towards}` : `${styles.bar} ${styles.away}`}
                  style={{ left: `${left}%`, width: `${width}%` }}
                />
              </span>
              <span className={styles.value}>
                {signed(s.value)}
                {signed(s.value) !== '0.00' && (
                  <span className={styles.direction}>{towards ? ' towards' : ' away'}</span>
                )}
              </span>
            </li>
          )
        })}
        <li className={`${styles.step} ${styles.total}`}>
          <span className={styles.name}>Model&rsquo;s score</span>
          <span className={styles.track} aria-hidden="true">
            <span className={styles.zero} style={{ left: `${zero}%` }} />
            <span className={styles.mark} style={{ left: `${pct(wf.output, lo, span)}%` }} />
          </span>
          <span className={styles.value}>{signed(wf.output)}</span>
        </li>
      </ol>
    </figure>
  )
}
