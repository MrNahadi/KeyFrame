import { AlertTriangle, ChevronLeft, ChevronRight, Info, Pause, Play, SkipBack, SkipForward } from 'lucide-react'
import { useCallback, useEffect, useReducer, useState } from 'react'
import { hrefFor } from '../app/routes'
import { Button } from '../ui/Button'
import { EmptyState } from '../ui/EmptyState'
import { clock } from '../ui/format'
import { Icon } from '../ui/Icon'
import { Keyframe } from '../ui/Keyframe'
import { Segmented } from '../ui/Segmented'
import { loadIndex, loadRun } from './data'
import {
  createPlayback,
  jumpToSwitchOn,
  pause,
  play,
  setSpeed,
  SPEEDS,
  stepBack,
  stepForward,
  tick,
  toEnd,
  toStart,
  type PlaybackState,
  type Speed,
} from './playback'
import { ExplainPanel } from './ExplainPanel'
import { Probabilities } from './Probabilities'
import styles from './ReplayScreen.module.css'
import { alarmTime, heldOutNote, lowConfidenceNote } from './status'
import { Timeline } from './Timeline'
import { Traces } from './Traces'
import type { Replay, RunSummary } from './types'

type Action =
  | { type: 'reset'; state: PlaybackState }
  | { type: 'toggle' }
  | { type: 'tick'; dt: number }
  | { type: 'back' }
  | { type: 'forward' }
  | { type: 'start' }
  | { type: 'end' }
  | { type: 'switchOn' }
  | { type: 'speed'; speed: Speed }
  | { type: 'seek'; index: number }

function reduce(s: PlaybackState, a: Action): PlaybackState {
  switch (a.type) {
    case 'reset':
      return a.state
    case 'toggle':
      return s.playing ? pause(s) : play(s)
    case 'tick':
      return tick(s, a.dt)
    case 'back':
      return stepBack(s)
    case 'forward':
      return stepForward(s)
    case 'start':
      return pause(toStart(s))
    case 'end':
      return pause(toEnd(s))
    case 'switchOn':
      return jumpToSwitchOn(s)
    case 'speed':
      return setSpeed(s, a.speed)
    case 'seek':
      return pause({ ...s, index: a.index, carry: 0 })
  }
}

const KEYS: Record<string, Action> = {
  ' ': { type: 'toggle' },
  ArrowLeft: { type: 'back' },
  ArrowRight: { type: 'forward' },
  Home: { type: 'start' },
  End: { type: 'end' },
  s: { type: 'switchOn' },
  S: { type: 'switchOn' },
}

interface ReplayScreenProps {
  runId: string
  load?: (id: string) => Promise<Replay>
  loadTitles?: () => Promise<RunSummary[]>
}

type Load =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'ready'; replay: Replay; title: string }

const backHref = hrefFor({ page: 'replay', runId: null })

function BackLink() {
  return (
    <a className={styles.back} href={backHref}>
      <Icon icon={ChevronLeft} size={16} />
      All runs
    </a>
  )
}

export function ReplayScreen({ runId, load = loadRun, loadTitles = loadIndex }: ReplayScreenProps) {
  const [state, setState] = useState<Load>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let live = true
    setState({ kind: 'loading' })
    const title = loadTitles().then(
      (runs) => runs.find((r) => r.id === runId)?.title,
      () => undefined,
    )
    Promise.all([load(runId), title]).then(
      ([replay, name]) => {
        if (live) setState({ kind: 'ready', replay, title: name ?? replay.run })
      },
      (e: unknown) => {
        if (live) setState({ kind: 'error', message: e instanceof Error ? e.message : 'Unknown error' })
      },
    )
    return () => {
      live = false
    }
  }, [runId, load, loadTitles, attempt])

  if (state.kind === 'loading') {
    return (
      <div className={styles.screen} role="status" aria-label="Loading replay">
        <div className={`${styles.skeleton} ${styles.skeletonTitle}`} aria-hidden="true" />
        <div className={`${styles.skeleton} ${styles.skeletonBar}`} aria-hidden="true" />
        <div className={styles.body} aria-hidden="true">
          <div className={`${styles.skeleton} ${styles.skeletonPanel}`} />
          <div className={`${styles.skeleton} ${styles.skeletonPanel}`} />
        </div>
      </div>
    )
  }

  if (state.kind === 'error') {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="This run could not be loaded"
        action={
          <>
            <Button variant="primary" onClick={() => setAttempt((a) => a + 1)}>
              Try again
            </Button>
            <BackLink />
          </>
        }
      >
        {state.message}
      </EmptyState>
    )
  }

  if (state.replay.frames.length === 0) {
    return (
      <EmptyState icon={AlertTriangle} title="This run has no frames" action={<BackLink />}>
        The recording is empty, so there is nothing to play back.
      </EmptyState>
    )
  }

  return <Player replay={state.replay} title={state.title} />
}

const sentence = (s: string) => s.charAt(0).toUpperCase() + s.slice(1)

const SPEED_OPTIONS = SPEEDS.map((sp) => ({ value: sp, label: `${sp}×` }))

function Player({ replay, title }: { replay: Replay; title: string }) {
  const times = replay.frames.map((f) => f.t)
  const [pb, dispatch] = useReducer(reduce, undefined, () => createPlayback(times, replay.switch_on_t))

  const playing = pb.playing
  useEffect(() => {
    if (!playing) return
    let raf = 0
    let prev: number | null = null
    const frame = (now: number) => {
      if (prev !== null) dispatch({ type: 'tick', dt: now - prev })
      prev = now
      raf = requestAnimationFrame(frame)
    }
    raf = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(raf)
  }, [playing])

  const onKey = useCallback((e: KeyboardEvent) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return
    const target = e.target as HTMLElement | null
    const tag = target?.tagName
    // The range input handles its own arrows/Home/End; buttons handle Space.
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return
    if (tag === 'BUTTON' && e.key === ' ') return
    const action = KEYS[e.key]
    if (!action) return
    e.preventDefault()
    dispatch(action)
  }, [])
  useEffect(() => {
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onKey])

  const lowNote = lowConfidenceNote(replay.frames)
  const elapsed = times[pb.index] - times[0]

  return (
    <div className={styles.screen}>
      <header className={styles.header}>
        <BackLink />
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.heldOut}>
          {heldOutNote(replay)} <a href={hrefFor({ page: 'model-card' })}>Model card</a>
        </p>
      </header>

      {lowNote && (
        <p className={styles.notice}>
          <Icon icon={Info} size={16} />
          <span>{lowNote}</span>
        </p>
      )}

      <Timeline
        times={times}
        index={pb.index}
        switchOnT={replay.switch_on_t}
        alarmT={alarmTime(replay)}
        onSeek={(index) => dispatch({ type: 'seek', index })}
      />

      <div className={styles.transport}>
        <p className={styles.now}>
          <span className={styles.clock}>{clock(elapsed)}</span>
          <span className={styles.clockLabel}>into the run</span>
        </p>
        <div className={styles.buttons} role="group" aria-label="Playback controls">
          <Button variant="tertiary" onClick={() => dispatch({ type: 'start' })} aria-label="Go to start">
            <Icon icon={SkipBack} size={20} />
          </Button>
          <Button variant="tertiary" onClick={() => dispatch({ type: 'back' })} aria-label="Step back">
            <Icon icon={ChevronLeft} size={20} />
          </Button>
          <Button
            variant="primary"
            className={styles.play}
            onClick={() => dispatch({ type: 'toggle' })}
            aria-label={pb.playing ? 'Pause' : 'Play'}
          >
            <Icon icon={pb.playing ? Pause : Play} size={20} />
            <span aria-hidden="true">{pb.playing ? 'Pause' : 'Play'}</span>
          </Button>
          <Button variant="tertiary" onClick={() => dispatch({ type: 'forward' })} aria-label="Step forward">
            <Icon icon={ChevronRight} size={20} />
          </Button>
          <Button variant="tertiary" onClick={() => dispatch({ type: 'end' })} aria-label="Go to end">
            <Icon icon={SkipForward} size={20} />
          </Button>
        </div>
        <Button onClick={() => dispatch({ type: 'switchOn' })} disabled={replay.switch_on_t === null}>
          <Keyframe kind="switch-on" size={14} />
          Jump to switch-on
        </Button>
        <div className={styles.speed}>
          <span className={styles.speedLabel} aria-hidden="true">
            Speed
          </span>
          <Segmented
            label="Playback speed"
            options={SPEED_OPTIONS}
            value={pb.speed}
            onChange={(speed: Speed) => dispatch({ type: 'speed', speed })}
          />
        </div>
      </div>
      <p className={styles.keys}>
        Keys: Space plays or pauses, arrows step, Home and End jump, S jumps to switch-on.
      </p>

      <div className={styles.body}>
        <aside className={styles.aside} aria-label="Model">
          <Probabilities replay={replay} index={pb.index} />
          <ExplainPanel replay={replay} index={pb.index} playing={pb.playing} />
        </aside>
        <Traces replay={replay} index={pb.index} />
      </div>

      <details className={styles.about}>
        <summary>About this replay</summary>
        <dl>
          <dt>Recording</dt>
          <dd>Real test-bench run, {replay.sampling_note}.</dd>
          <dt>Predictions</dt>
          <dd>
            {sentence(replay.provenance)}. Each moment is read using only what had happened up to then.
          </dd>
        </dl>
      </details>
    </div>
  )
}
