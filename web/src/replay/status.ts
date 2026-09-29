import { alarmTime } from './Traces'
import type { Replay } from './types'

const CLASS_NAMES: Record<string, string> = {
  Normal: 'normal running',
  'AC Fouling': 'air cooler fouling',
  'AF Clogging': 'air filter clogging',
  'Clogged Injector': 'injector nozzle clogging',
  'CW Pump': 'cooling water pump cavitation',
  'Turbine Degradation': 'turbine degradation',
}

/** Plain-language class name; unknown classes fall back to the raw label. */
export function className(raw: string): string {
  return CLASS_NAMES[raw] ?? raw.toLowerCase()
}

const pad = (n: number) => String(n).padStart(2, '0')

/** Clock style mm:ss for a time in seconds. */
export function clock(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  return `${pad(Math.floor(s / 60))}:${pad(s % 60)}`
}

/** Short duration such as "7 min 18 s" or "45 s". */
export function duration(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  const m = Math.floor(s / 60)
  return m === 0 ? `${s} s` : `${m} min ${s % 60} s`
}

/** The most likely class as a sentence, with its percentage. */
export function probabilitySentence(predicted: string, probabilities: Record<string, number>): string {
  const p = probabilities[predicted]
  const pct = p === undefined ? '' : ` (${Math.round(p * 100)}%)`
  return `The model reads this as ${className(predicted)}${pct}`
}

/** One line that always answers "has the alarm fired?" for the frame at `index`. */
export function alarmStatus(replay: Replay, index: number): string {
  const frames = replay.frames
  if (frames.length === 0) return 'No frames in this run'
  const i = Math.min(Math.max(0, index), frames.length - 1)
  const now = frames[i].t
  const switchOn = replay.switch_on_t
  const alarmT = alarmTime(replay)
  const alarmClass = alarmT === null ? '' : (frames.find((f) => f.t === alarmT)?.alarm ?? '')

  if (switchOn === null) {
    if (alarmT !== null && now >= alarmT) {
      return `Alarm: ${className(alarmClass)} raised, though no fault was switched on`
    }
    return 'No fault in this run'
  }
  if (alarmT !== null && now >= alarmT) {
    return `Alarm: ${className(alarmClass)} raised ${duration(alarmT - switchOn)} after switch-on`
  }
  if (now < switchOn) return `Engine healthy by design until ${clock(switchOn)}`
  if (i === frames.length - 1) {
    return alarmT === null
      ? `Fault switched on ${duration(now - switchOn)} ago, no alarm was raised in this run`
      : `Fault switched on ${duration(now - switchOn)} ago, no alarm yet`
  }
  return `Fault switched on ${duration(now - switchOn)} ago, no alarm yet`
}
