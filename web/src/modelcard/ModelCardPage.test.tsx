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
    expect((await screen.findByRole('heading', { level: 1 })).textContent).toBe('Model card: Test')
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(screen.getByText('Not tested on a ship.').tagName).toBe('STRONG')
    // The targets table comes first, with a worded status on every row.
    const rows = screen.getAllByRole('row').slice(1)
    expect(rows).toHaveLength(9)
    expect(rows[0].textContent).toContain('Macro F1 on held-out loads0.717Target 0.80Not met')
    expect(screen.getByText(/2 of 9 targets met/)).toBeTruthy()
    const img = screen.getByRole('img', { name: /confusion matrix/i })
    expect(img.getAttribute('src')).toContain('figures/07_confusion.png')
    expect(screen.getByText(/Confusion matrix on held-out/)).toBeTruthy()
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
