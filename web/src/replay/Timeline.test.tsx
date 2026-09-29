import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Timeline } from './Timeline'

afterEach(cleanup)

const times = [0, 600, 1200, 1800, 2400, 3000]

describe('Timeline', () => {
  it('is a labelled slider with the run clock as its text value', () => {
    render(<Timeline times={times} index={2} switchOnT={1200} alarmT={1800} onSeek={() => {}} />)
    const slider = screen.getByRole('slider', { name: 'Position in run' })
    expect(slider.getAttribute('aria-valuetext')).toBe('20:00 into the run')
  })

  it('names the keyframes in words', () => {
    render(<Timeline times={times} index={0} switchOnT={1200} alarmT={1800} onSeek={() => {}} />)
    expect(screen.getByText('Fault switched on at 20:00')).toBeTruthy()
    expect(screen.getByText('Alarm at 30:00')).toBeTruthy()
    cleanup()
    render(<Timeline times={times} index={0} switchOnT={1200} alarmT={null} onSeek={() => {}} />)
    expect(screen.getByText('No alarm')).toBeTruthy()
    cleanup()
    render(<Timeline times={times} index={0} switchOnT={null} alarmT={null} onSeek={() => {}} />)
    expect(screen.getByText('No fault in this run')).toBeTruthy()
  })

  it('seeks to the chosen frame', () => {
    const onSeek = vi.fn()
    render(<Timeline times={times} index={0} switchOnT={null} alarmT={null} onSeek={onSeek} />)
    fireEvent.change(screen.getByRole('slider'), { target: { value: '4' } })
    expect(onSeek).toHaveBeenCalledWith(4)
  })
})
