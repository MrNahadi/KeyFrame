import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { afterEach, describe, expect, it } from 'vitest'
import { Segmented } from './Segmented'

afterEach(cleanup)

function Harness() {
  const [v, setV] = useState(10)
  const options = [1, 10, 60].map((n) => ({ value: n, label: `${n}×` }))
  return <Segmented label="Speed" options={options} value={v} onChange={setV} />
}

describe('Segmented', () => {
  it('is one tab stop, and arrow keys move and select', async () => {
    const user = userEvent.setup()
    render(<Harness />)
    const radios = screen.getAllByRole('radio')
    expect(radios.map((r) => r.tabIndex)).toEqual([-1, 0, -1])
    await user.tab()
    expect(document.activeElement).toBe(radios[1])
    await user.keyboard('{ArrowRight}')
    expect(radios[2].getAttribute('aria-checked')).toBe('true')
    expect(document.activeElement).toBe(radios[2])
    await user.keyboard('{ArrowRight}')
    expect(radios[0].getAttribute('aria-checked')).toBe('true')
    await user.keyboard('{ArrowLeft}')
    expect(radios[2].getAttribute('aria-checked')).toBe('true')
  })
})
