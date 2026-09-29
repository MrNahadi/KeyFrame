import { AlertTriangle, ChevronLeft, ChevronRight, Pause, Play, SkipBack, SkipForward, Zap } from 'lucide-react'
import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { hrefFor } from '../app/routes'
import { EmptyState } from '../ui/EmptyState'
import { Icon } from '../ui/Icon'
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
import { duration, lowConfidenceNote } from './status'
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

  const back = <a href={hrefFor({ page: 'replay', runId: null })}>Back to all runs</a>

  if (state.kind === 'loading') {
    return (
      <div className={styles.screen} role="status" aria-label="Loading replay">
        <div className={`${styles.skeleton} ${styles.skeletonBar}`} aria-hidden="true" />
        <div className={styles.body} aria-hidden="true">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className={`${styles.skeleton} ${styles.skeletonChart}`} />
          ))}
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
            <button type="button" className={styles.button} onClick={() => setAttempt((a) => a + 1)}>
              Try again
            </button>{' '}
            {back}
          </>
        }
      >
        {state.message}
      </EmptyState>
    )
  }

  if (state.replay.frames.length === 0) {
    return (
      <EmptyState icon={AlertTriangle} title="This run has no frames" action={back}>
        The recording is empty, so there is nothing to play back.
      </EmptyState>
    )
  }

  return <Player replay={state.replay} title={state.title} />
}

function Player({ replay, title }: { replay: Replay; title: string }) {
  const times = replay.frames.map((f) => f.t)
  const [pb, dispatch] = useReducer(
    reduce,
    undefined,
    () => createPlayback(times, replay.switch_on_t),
  )

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

  const rootRef = useRef<HTMLDivElement>(null)
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

  const last = times.length - 1
  const lowNote = lowConfidenceNote(replay.frames)
  const elapsed = duration(times[pb.index] - times[0])

  return (
    <div className={styles.screen} ref={rootRef}>
      <h1 className={styles.title}>{title}</h1>
      <div className={styles.controls} role="group" aria-label="Playback controls">
        <button type="button" className={styles.button} onClick={() => dispatch({ type: 'start' })} aria-label="Go to start">
          <Icon icon={SkipBack} size={20} />
        </button>
        <button type="button" className={styles.button} onClick={() => dispatch({ type: 'back' })} aria-label="Step back">
          <Icon icon={ChevronLeft} size={20} />
        </button>
        <button
          type="button"
          className={`${styles.button} ${styles.primary}`}
          onClick={() => dispatch({ type: 'toggle' })}
          aria-label={pb.playing ? 'Pause' : 'Play'}
        >
          <Icon icon={pb.playing ? Pause : Play} size={20} />
        </button>
        <button type="button" className={styles.button} onClick={() => dispatch({ type: 'forward' })} aria-label="Step forward">
          <Icon icon={ChevronRight} size={20} />
        </button>
        <button type="button" className={styles.button} onClick={() => dispatch({ type: 'end' })} aria-label="Go to end">
          <Icon icon={SkipForward} size={20} />
        </button>
        <button
          type="button"
          className={styles.button}
          onClick={() => dispatch({ type: 'switchOn' })}
          disabled={replay.switch_on_t === null}
        >
          <Icon icon={Zap} size={20} /> Jump to fault switch-on
        </button>
        <div className={styles.speeds} role="group" aria-label="Playback speed">
          {SPEEDS.map((sp) => (
            <button
              key={sp}
              type="button"
              className={styles.button}
              aria-pressed={pb.speed === sp}
              onClick={() => dispatch({ type: 'speed', speed: sp })}
            >
              {sp}×
            </button>
          ))}
        </div>
      </div>
      <input
        className={styles.scrubber}
        type="range"
        aria-label="Position in run"
        min={0}
        max={last}
        step={1}
        value={pb.index}
        aria-valuetext={elapsed}
        onChange={(e) => dispatch({ type: 'seek', index: Number(e.target.value) })}
      />
      <p className={styles.elapsed}>
        {elapsed} into the run. Keys: Space plays or pauses, arrows step, Home and End jump, S jumps to switch-on.
      </p>
      <div className={styles.body}>
        <Traces replay={replay} index={pb.index} />
        <Probabilities replay={replay} index={pb.index} />
      </div>
      <ExplainPanel replay={replay} index={pb.index} playing={pb.playing} />
      {lowNote && (
        <p className={styles.lowNote}>
          {lowNote} <a href={hrefFor({ page: 'model-card' })}>Model card</a>
        </p>
      )}
    </div>
  )
}
