import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderMarkdown } from './markdown'

const html = (md: string) => render(<div>{renderMarkdown(md)}</div>).container.firstElementChild!

describe('renderMarkdown', () => {
  it('renders headings by level', () => {
    const el = html('# One\n\n## Two\n\n### Three')
    expect(el.querySelector('h1')?.textContent).toBe('One')
    expect(el.querySelector('h2')?.textContent).toBe('Two')
    expect(el.querySelector('h3')?.textContent).toBe('Three')
  })

  it('joins wrapped lines into one paragraph and splits on blank lines', () => {
    const el = html('first line\nsecond line\n\nnext')
    const ps = el.querySelectorAll('p')
    expect(ps).toHaveLength(2)
    expect(ps[0].textContent).toBe('first line second line')
  })

  it('renders bullet lists', () => {
    const el = html('- a\n- b\n* c')
    expect(Array.from(el.querySelectorAll('li')).map((li) => li.textContent)).toEqual(['a', 'b', 'c'])
    expect(el.querySelectorAll('ul')).toHaveLength(1)
  })

  it('renders bold, inline code and links', () => {
    const el = html('A **strong** and `code()` and [site](https://example.com/x).')
    expect(el.querySelector('strong')?.textContent).toBe('strong')
    expect(el.querySelector('code')?.textContent).toBe('code()')
    const a = el.querySelector('a')!
    expect(a.textContent).toBe('site')
    expect(a.getAttribute('href')).toBe('https://example.com/x')
  })

  it('does not link unsafe schemes', () => {
    const el = html('[bad](javascript:alert(1))')
    expect(el.querySelector('a')).toBeNull()
    expect(el.textContent).toContain('bad')
  })

  it('renders <script> as text, never as an element', () => {
    const el = html('Hello <script>alert(1)</script>\n\n- <img src=x onerror=alert(1)>')
    expect(el.querySelector('script')).toBeNull()
    expect(el.querySelector('img')).toBeNull()
    expect(el.textContent).toContain('<script>alert(1)</script>')
  })
})
