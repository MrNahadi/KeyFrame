import { faultName, faultPhrase } from '../app/vocabulary'
import { clock, delay, percent } from '../ui/format'
import type { Replay, ReplayFrame } from './types'

/** Plain-language class name for use in a sentence; unknown classes fall back to lower case. */
export function className(raw: string): string {
  const phrase = faultPhrase(raw)
  return phrase === raw ? raw.toLowerCase() : phrase
}

/** Time of the first frame where the alarm is raised, or null. */
export function alarmTime(replay: Replay): number | null {
  return replay.frames.find((f) => f.alarm !== 'Normal')?.t ?? null
}

/** The most likely class as a sentence, with its percentage. */
export function probabilitySentence(predicted: string, probabilities: Record<string, number>): string {
  const p = probabilities[predicted]
  const pct = p === undefined ? '' : ` (${percent(p)})`
  return `The model reads this as ${className(predicted)}${pct}`
}

export type AlarmKind = 'no-fault' | 'false-alarm' | 'healthy' | 'fault-on' | 'missed' | 'alarm'

export interface AlarmState {
  kind: AlarmKind
  /** Short, changes rarely: safe to announce. */
  headline: string
  /** Changes every frame (elapsed times). */
  detail: string
}

/** Answers "has the alarm fired?" for the frame at `index`, as a headline and a detail line. */
export function alarmState(replay: Replay, index: number): AlarmState {
  const frames = replay.frames
  if (frames.length === 0) return { kind: 'no-fault', headline: 'No frames in this run', detail: '' }
  const i = Math.min(Math.max(0, index), frames.length - 1)
  const now = frames[i].t
  const switchOn = replay.switch_on_t
  const alarmT = alarmTime(replay)
  const alarmClass = alarmT === null ? '' : (frames.find((f) => f.t === alarmT)?.alarm ?? '')
  const raised = alarmT !== null && now >= alarmT

  if (switchOn === null) {
    if (raised) {
      return {
        kind: 'false-alarm',
        headline: `Alarm: ${className(alarmClass)}`,
        detail: 'Raised though no fault was switched on in this run.',
      }
    }
    return { kind: 'no-fault', headline: 'No fault in this run', detail: 'The engine runs healthy throughout.' }
  }
  if (raised) {
    const wrong = replay.fault && faultName(replay.fault) !== faultName(alarmClass)
    return {
      kind: 'alarm',
      headline: `Alarm: ${className(alarmClass)}`,
      detail:
        `Raised ${delay(alarmT - switchOn)} after switch-on.` +
        (wrong ? ` The fault switched on was ${className(replay.fault)}.` : ''),
    }
  }
  if (now < switchOn) {
    return {
      kind: 'healthy',
      headline: 'Healthy by design',
      detail: `The fault is switched on at ${clock(switchOn)}.`,
    }
  }
  if (i === frames.length - 1 && alarmT === null) {
    return {
      kind: 'missed',
      headline: 'No alarm raised',
      detail: `The fault ran for ${delay(now - switchOn)} and the model never raised the alarm.`,
    }
  }
  return {
    kind: 'fault-on',
    headline: 'Fault on, no alarm yet',
    detail: `Switched on ${delay(now - switchOn)} ago.`,
  }
}

const CONFIDENT = 0.4

/** A plain sentence when the model never reaches 40% on any class in the whole run, else null. */
export function lowConfidenceNote(frames: ReplayFrame[]): string | null {
  if (frames.length === 0) return null
  const max = frames.reduce((m, f) => Math.max(m, ...Object.values(f.probabilities)), 0)
  if (max >= CONFIDENT) return null
  return `The held-out model for this load is barely confident on any reading (at most ${percent(max)}). This is a known tuning defect, described on the model card; the scores shown are the locked ones.`
}

/** Which held-out model made the predictions, in one sentence (from the replay's provenance). */
export function heldOutNote(replay: Replay): string {
  const folds = replay.provenance.match(/fold ([\d, ]+)/)?.[1]?.split(',').map((f) => f.trim()).filter(Boolean)
  if (folds && folds.length > 1) {
    return 'The load changes during this run; each moment is predicted by a model that never saw that load.'
  }
  const load = folds?.[0] ?? replay.nominal_load
  if (load === null || load === undefined) return 'Predictions come from a model that never saw this engine load.'
  return `Predictions come from a model that never saw ${load}% load.`
}
