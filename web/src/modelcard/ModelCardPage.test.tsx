import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ModelCardPage } from './ModelCardPage'

const CARD = '# Model card: Test\n\n## Limits\n\n- Bench, not ship. **Not tested on a ship.**'

describe('ModelCardPage', () => {
  afterEach(cleanup)

  it('shows a loading state, then the card, figure and notebook link', async () => {
    render(<ModelCardPage load={() => Promise.resolve(CARD)} />)
    expect(screen.getByRole('status', { name: /loading/i })).toBeTruthy()
    expect(await screen.findByRole('heading', { name: 'Model card: Test' })).toBeTruthy()
    expect(screen.getByText('Not tested on a ship.').tagName).toBe('STRONG')
    const img = screen.getByRole('img', { name: /confusion matrix/i })
    expect(img.getAttribute('src')).toContain('figures/07_confusion.png')
    expect(screen.getByText(/held-out/i)).toBeTruthy()
    const link = screen.getByRole('link', { name: /evaluation notebook/i })
    expect(link.getAttribute('href')).toContain('notebooks/07_evaluation.ipynb')
  })

  it('shows an error with a retry', async () => {
    const load = vi.fn().mockRejectedValueOnce(new Error('Model card not found')).mockResolvedValue(CARD)
    render(<ModelCardPage load={load} />)
    expect(await screen.findByText('Model card not found')).toBeTruthy()
    await userEvent.click(screen.getByRole('button', { name: /try again/i }))
    expect(await screen.findByRole('heading', { name: 'Model card: Test' })).toBeTruthy()
    expect(load).toHaveBeenCalledTimes(2)
  })
})
