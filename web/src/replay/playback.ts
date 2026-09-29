export type Speed = 1 | 10 | 60

export const SPEEDS: readonly Speed[] = [1, 10, 60]

/** Seconds between frames in the replay files. */
export const FRAME_SECONDS = 10

export interface PlaybackState {
  readonly times: readonly number[]
  readonly switchOnT: number | null
  readonly index: number
  readonly playing: boolean
  readonly speed: Speed
  /** Fraction of a frame already elapsed towards the next one. */
  readonly carry: number
}

export function createPlayback(
  times: readonly number[],
  switchOnT: number | null,
): PlaybackState {
  return { times, switchOnT, index: 0, playing: false, speed: 1, carry: 0 }
}

const last = (s: PlaybackState) => Math.max(0, s.times.length - 1)

const at = (s: PlaybackState, index: number): PlaybackState => ({
  ...s,
  index: Math.min(last(s), Math.max(0, index)),
  carry: 0,
})

export function play(s: PlaybackState): PlaybackState {
  if (s.times.length === 0) return s
  const from = s.index >= last(s) ? at(s, 0) : s
  return { ...from, playing: true }
}

export function pause(s: PlaybackState): PlaybackState {
  return { ...s, playing: false }
}

export function setSpeed(s: PlaybackState, speed: Speed): PlaybackState {
  return { ...s, speed }
}

/** Advance by `dtMs` of wall time (from requestAnimationFrame timestamps). */
export function tick(s: PlaybackState, dtMs: number): PlaybackState {
  if (!s.playing || s.times.length === 0) return s
  const frames = s.carry + (dtMs / 1000) * (s.speed / FRAME_SECONDS)
  const whole = Math.floor(frames)
  const index = s.index + whole
  if (index >= last(s)) return { ...s, index: last(s), carry: 0, playing: false }
  return { ...s, index, carry: frames - whole }
}

export const stepForward = (s: PlaybackState) => pause(at(s, s.index + 1))
export const stepBack = (s: PlaybackState) => pause(at(s, s.index - 1))
export const toStart = (s: PlaybackState) => at(s, 0)
export const toEnd = (s: PlaybackState) => at(s, last(s))

/** Jump to the frame nearest `t` seconds, clamped to the run. */
export function seekToTime(s: PlaybackState, t: number): PlaybackState {
  let best = 0
  for (let i = 1; i < s.times.length; i++) {
    if (Math.abs(s.times[i] - t) < Math.abs(s.times[best] - t)) best = i
  }
  return at(s, best)
}

export function jumpToSwitchOn(s: PlaybackState): PlaybackState {
  return s.switchOnT === null ? s : seekToTime(s, s.switchOnT)
}
