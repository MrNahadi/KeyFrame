import { describe, expect, it } from 'vitest'
import {
  createPlayback,
  jumpToSwitchOn,
  pause,
  play,
  seekToTime,
  setSpeed,
  stepBack,
  stepForward,
  tick,
  toEnd,
  toStart,
} from './playback'

const times = Array.from({ length: 100 }, (_, i) => i * 10)
const fresh = () => createPlayback(times, 500)

describe('playback engine', () => {
  it('starts paused at frame 0 at 1x', () => {
    const s = fresh()
    expect(s).toMatchObject({ index: 0, playing: false, speed: 1 })
  })

  it('does not advance while paused', () => {
    expect(tick(fresh(), 5000).index).toBe(0)
  })

  it('advances one frame per 10 s of wall time at 1x', () => {
    const s = tick(play(fresh()), 10_000)
    expect(s.index).toBe(1)
  })

  it('advances 10 frames per 10 s at 10x and 6 per second at 60x', () => {
    expect(tick(play(setSpeed(fresh(), 10)), 10_000).index).toBe(10)
    expect(tick(play(setSpeed(fresh(), 60)), 1000).index).toBe(6)
  })

  it('carries fractional frames across ticks', () => {
    let s = play(setSpeed(fresh(), 60))
    for (let i = 0; i < 10; i++) s = tick(s, 100)
    expect(s.index).toBe(6)
  })

  it('stops at the last frame', () => {
    const s = tick(play(setSpeed(fresh(), 60)), 1_000_000)
    expect(s.index).toBe(99)
    expect(s.playing).toBe(false)
  })

  it('steps forward and back within bounds', () => {
    expect(stepForward(fresh()).index).toBe(1)
    expect(stepBack(fresh()).index).toBe(0)
    expect(stepBack(stepForward(fresh())).index).toBe(0)
    expect(stepForward(toEnd(fresh())).index).toBe(99)
  })

  it('stepping pauses playback and clears the fractional carry', () => {
    const s = stepForward(tick(play(fresh()), 4000))
    expect(s.playing).toBe(false)
    expect(tick(play(s), 6000).index).toBe(1)
  })

  it('goes to start and end', () => {
    expect(toEnd(fresh()).index).toBe(99)
    expect(toStart(toEnd(fresh())).index).toBe(0)
  })

  it('seeks to the nearest frame by time, clamped', () => {
    expect(seekToTime(fresh(), 124).index).toBe(12)
    expect(seekToTime(fresh(), 126).index).toBe(13)
    expect(seekToTime(fresh(), -50).index).toBe(0)
    expect(seekToTime(fresh(), 99_999).index).toBe(99)
  })

  it('jumps to the switch-on frame', () => {
    expect(jumpToSwitchOn(fresh()).index).toBe(50)
  })

  it('ignores the switch-on jump when there is none', () => {
    const s = stepForward(createPlayback(times, null))
    expect(jumpToSwitchOn(s).index).toBe(1)
  })

  it('play at the end restarts from the beginning', () => {
    const s = play(toEnd(fresh()))
    expect(s).toMatchObject({ index: 0, playing: true })
  })

  it('pause stops advancing', () => {
    const s = pause(play(fresh()))
    expect(tick(s, 10_000).index).toBe(0)
  })

  it('handles an empty run', () => {
    const s = tick(play(createPlayback([], null)), 1000)
    expect(s.index).toBe(0)
    expect(s.playing).toBe(false)
  })
})
