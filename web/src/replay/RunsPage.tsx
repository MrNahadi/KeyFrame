import { AlertTriangle, ListX } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { hrefFor } from '../app/routes'
import { Button, LinkButton } from '../ui/Button'
import { EmptyState } from '../ui/EmptyState'
import { delay, length } from '../ui/format'
import { Keyframe } from '../ui/Keyframe'
import { loadIndex } from './data'
import styles from './RunsPage.module.css'
import type { RunSummary } from './types'

/** Fault groups in display order, keyed by run id prefix; healthy running last. */
const GROUPS: { prefix: string; name: string }[] = [
  { prefix: 'AC_Fouling', name: 'Air cooler fouling' },
  { prefix: 'AF_Clogging', name: 'Air filter clogging' },
  { prefix: 'Clogged_Injector', name: 'Injector nozzle clogging' },
  { prefix: 'CW_Pump', name: 'Cooling water pump cavitation' },
  { prefix: 'Turbine_Degradation', name: 'Turbine degradation' },
  { prefix: 'Reference', name: 'Healthy running' },
]
const OTHER = 'Other runs'

export function groupName(id: string): string {
  return GROUPS.find((g) => id.startsWith(g.prefix))?.name ?? OTHER
}

/** Engine load in words, read from the run id ("AC_Fouling_40_Load", "Reference_60"). */
export function loadLabel(id: string): string {
  const nums = (id.match(/(?:^|_)(\d{2,3})(?=_|$)/g) ?? []).map((n) => n.replace('_', ''))
  if (nums.length === 0) return 'Load program'
  if (nums.length === 1) return `${nums[0]}%`
  return `${nums.slice(0, -1).join(', ')} and ${nums[nums.length - 1]}%`
}

export function groupRuns(runs: RunSummary[]): { name: string; runs: RunSummary[] }[] {
  return [...GROUPS.map((g) => g.name), OTHER]
    .map((name) => ({ name, runs: runs.filter((r) => groupName(r.id) === name) }))
    .filter((g) => g.runs.length > 0)
}

/** Runs in load order; the stepped injector run (several loads) sorts by its first load. */
export function sortByLoad(runs: RunSummary[]): RunSummary[] {
  const first = (id: string) => Number(loadLabel(id).match(/\d+/)?.[0] ?? 0)
  return [...runs].sort((a, b) => first(a.id) - first(b.id))
}

/** The run a first-time visitor should play: the fixed-load fault run caught fastest. */
export function startRun(runs: RunSummary[]): RunSummary | undefined {
  return runs
    .filter((r) => r.switch_on_t !== null && r.switch_on_t > 0 && r.alarm_delay_s !== null)
    .sort((a, b) => (a.alarm_delay_s ?? 0) - (b.alarm_delay_s ?? 0))[0]
}

/** What the last column says for a run. */
export function alarmLabel(run: RunSummary): string {
  if (run.switch_on_t === null) return run.alarm_delay_s === null ? 'No fault' : 'False alarm'
  return run.alarm_delay_s === null ? 'No alarm' : delay(run.alarm_delay_s)
}

/** A miniature keyframe timeline: healthy span, fault span, switch-on and alarm marks. */
function Strip({ run }: { run: RunSummary }) {
  const d = Math.max(run.duration_s, 1)
  const on = run.switch_on_t === null ? null : Math.min(run.switch_on_t / d, 1)
  const alarm =
    run.switch_on_t === null || run.alarm_delay_s === null
      ? null
      : Math.min((run.switch_on_t + run.alarm_delay_s) / d, 1)
  return (
    <span className={styles.strip} aria-hidden="true">
      {on !== null && <span className={styles.span} style={{ left: `${on * 100}%` }} />}
      {on !== null && (
        <span className={styles.mark} style={{ left: `${on * 100}%` }}>
          <Keyframe kind="switch-on" size={12} />
        </span>
      )}
      {alarm !== null && (
        <span className={styles.mark} style={{ left: `${alarm * 100}%` }}>
          <Keyframe kind="alarm" size={12} />
        </span>
      )}
    </span>
  )
}

type State =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; runs: RunSummary[] }

export function RunsPage({ load = loadIndex }: { load?: () => Promise<RunSummary[]> }) {
  const [state, setState] = useState<State>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let live = true
    setState({ kind: 'loading' })
    load().then(
      (runs) => live && setState({ kind: 'ready', runs }),
      (e: unknown) =>
        live && setState({ kind: 'error', message: e instanceof Error ? e.message : 'Unknown error' }),
    )
    return () => {
      live = false
    }
  }, [load, attempt])
  const retry = useCallback(() => setAttempt((a) => a + 1), [])

  const start = state.kind === 'ready' ? startRun(state.runs) : undefined

  return (
    <div className={styles.page}>
      <section className={styles.intro}>
        <h1 className={styles.title}>
          Watch a marine diesel go from healthy to faulty, and see when the model raised the alarm.
        </h1>
        <p className={styles.lead}>
          These are real runs from a test-bench engine. Each is replayed with predictions from a
          model that never saw that engine load, so you see how it copes with a load it has not met.
        </p>
        <div className={styles.legend}>
          <span>
            <Keyframe kind="switch-on" /> Fault switched on
          </span>
          <span>
            <Keyframe kind="alarm" /> Alarm raised
          </span>
        </div>
        {start && (
          <LinkButton href={hrefFor({ page: 'replay', runId: start.id })}>Play {start.title.toLowerCase()}</LinkButton>
        )}
      </section>

      <section aria-labelledby="runs-title" className={styles.runs}>
        <h2 id="runs-title">Fault runs</h2>
        {state.kind === 'loading' && (
          <div role="status" aria-label="Loading runs" className={styles.skeletonTable}>
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <div key={i} className={styles.skeletonRow} aria-hidden="true" />
            ))}
          </div>
        )}
        {state.kind === 'error' && (
          <EmptyState
            icon={AlertTriangle}
            title="The run list could not be loaded"
            action={
              <Button onClick={retry} variant="secondary">
                Try again
              </Button>
            }
          >
            {state.message}
          </EmptyState>
        )}
        {state.kind === 'ready' && state.runs.length === 0 && (
          <EmptyState icon={ListX} title="No recorded runs yet">
            Copy the replay files into the app with <code>npm --prefix web run sync-replays</code>,
            then reload this page.
          </EmptyState>
        )}
        {state.kind === 'ready' && state.runs.length > 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">Load</th>
                <th scope="col" className={styles.num}>
                  Length
                </th>
                <th scope="col" className={styles.timelineHead}>
                  Timeline
                </th>
                <th scope="col" className={styles.num}>
                  Alarm after switch-on
                </th>
              </tr>
            </thead>
            {groupRuns(state.runs).map((g) => (
              <tbody key={g.name} className={styles.group}>
                <tr className={styles.groupRow}>
                  <th scope="rowgroup" colSpan={4}>
                    {g.name}
                  </th>
                </tr>
                {sortByLoad(g.runs).map((run) => (
                  <tr key={run.id} className={styles.row}>
                    <th scope="row" className={styles.load}>
                      <a href={hrefFor({ page: 'replay', runId: run.id })} className={styles.rowLink}>
                        <span className="visually-hidden">{g.name}, </span>
                        {loadLabel(run.id)}
                        <span className="visually-hidden"> load</span>
                      </a>
                    </th>
                    <td className={`${styles.num} ${styles.length}`}>{length(run.duration_s)}</td>
                    <td className={styles.timelineCell}>
                      <Strip run={run} />
                    </td>
                    <td
                      className={`${styles.num} ${styles.alarm} ${run.alarm_delay_s !== null && run.switch_on_t !== null ? styles.alarmed : styles.quiet}`}
                    >
                      {alarmLabel(run)}
                    </td>
                  </tr>
                ))}
              </tbody>
            ))}
          </table>
        )}
      </section>
    </div>
  )
}
