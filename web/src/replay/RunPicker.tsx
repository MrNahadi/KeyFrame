import { AlertTriangle, ListX } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { hrefFor } from '../app/routes'
import { EmptyState } from '../ui/EmptyState'
import { loadIndex } from './data'
import styles from './RunPicker.module.css'
import type { RunSummary } from './types'

/** Plain names for the fault groups, in display order (keyed by the run id prefix). */
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

/** Engine load in percent, read from the run id ("AC_Fouling_40_Load", "Reference_60"). */
export function loadLabel(id: string): string {
  const nums = (id.match(/(?:^|_)(\d{2,3})(?=_|$)/g) ?? []).map((n) => n.replace('_', ''))
  if (nums.length === 0) return 'Load not stated'
  if (nums.length === 1) return `${nums[0]}% load`
  return `${nums.slice(0, -1).join(', ')} and ${nums[nums.length - 1]}% load`
}

export function durationLabel(seconds: number): string {
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m === 0 ? `${h} h` : `${h} h ${m} min`
}

export function groupRuns(runs: RunSummary[]): { name: string; runs: RunSummary[] }[] {
  const names = [...GROUPS.map((g) => g.name), OTHER]
  return names
    .map((name) => ({ name, runs: runs.filter((r) => groupName(r.id) === name) }))
    .filter((g) => g.runs.length > 0)
}

type State =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; runs: RunSummary[] }

interface RunPickerProps {
  load?: () => Promise<RunSummary[]>
}

export function RunPicker({ load = loadIndex }: RunPickerProps) {
  const [state, setState] = useState<State>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let live = true
    setState({ kind: 'loading' })
    load().then(
      (runs) => {
        if (live) setState({ kind: 'ready', runs })
      },
      (e: unknown) => {
        if (live) setState({ kind: 'error', message: e instanceof Error ? e.message : 'Unknown error' })
      },
    )
    return () => {
      live = false
    }
  }, [load, attempt])

  const retry = useCallback(() => setAttempt((a) => a + 1), [])

  if (state.kind === 'loading') {
    return (
      <div className={styles.picker} role="status" aria-label="Loading runs">
        {[0, 1, 2].map((i) => (
          <div key={i} className={styles.skeletonGroup} aria-hidden="true">
            <div className={`${styles.skeleton} ${styles.skeletonHead}`} />
            <div className={`${styles.skeleton} ${styles.skeletonRow}`} />
            <div className={`${styles.skeleton} ${styles.skeletonRow}`} />
          </div>
        ))}
      </div>
    )
  }

  if (state.kind === 'error') {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="The run list could not be loaded"
        action={
          <button type="button" className={styles.button} onClick={retry}>
            Try again
          </button>
        }
      >
        {state.message}
      </EmptyState>
    )
  }

  if (state.runs.length === 0) {
    return (
      <EmptyState icon={ListX} title="No recorded runs yet">
        Replays are copied into the app from the model results. Run the sync-replays step, then
        reload this page.
      </EmptyState>
    )
  }

  return (
    <div className={styles.picker}>
      {groupRuns(state.runs).map((group) => (
        <section key={group.name} aria-labelledby={`group-${group.name}`}>
          <h2 id={`group-${group.name}`} className={styles.groupTitle}>
            {group.name}
          </h2>
          <ul className={styles.list}>
            {group.runs.map((run) => (
              <li key={run.id}>
                <a className={styles.row} href={hrefFor({ page: 'replay', runId: run.id })}>
                  <span className={styles.rowTitle}>{run.title}</span>
                  <span className={styles.meta}>
                    {loadLabel(run.id)} · {durationLabel(run.duration_s)}
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}
