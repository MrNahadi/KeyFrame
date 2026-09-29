import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { App } from './App'
import { hrefFor, parseRoute } from './routes'

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

describe('routes', () => {
  it('parses and builds every route', () => {
    expect(parseRoute('')).toEqual({ page: 'replay', runId: null })
    expect(parseRoute('#/replay/AC_Fouling_40_Load')).toEqual({
      page: 'replay',
      runId: 'AC_Fouling_40_Load',
    })
    expect(parseRoute('#/what-if')).toEqual({ page: 'what-if' })
    expect(parseRoute('#/model-card')).toEqual({ page: 'model-card' })
    expect(hrefFor({ page: 'replay', runId: 'a b' })).toBe('#/replay/a%20b')
  })
})

describe('App shell', () => {
  it('shows the primary navigation with Replay active by default', () => {
    render(<App />)
    const nav = screen.getByRole('navigation', { name: 'Primary' })
    expect(nav.textContent).toContain('Replay')
    expect(nav.textContent).toContain('What-if')
    expect(nav.textContent).toContain('Model card')
    expect(screen.getByRole('link', { name: 'Replay' }).getAttribute('aria-current')).toBe('page')
  })

  it('opens the what-if placeholder from its route', () => {
    window.location.hash = '#/what-if'
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Try your own readings' })).toBeTruthy()
  })
})
