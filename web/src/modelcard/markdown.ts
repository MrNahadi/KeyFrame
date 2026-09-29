import { createElement, type ReactNode } from 'react'

// A small renderer for the subset the model card uses. Text becomes React children,
// so it is escaped by React and never injected as HTML.

const INLINE = /(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)\s]+\))/g
const SAFE_HREF = /^(https?:\/\/|\/|#)/

function inline(text: string, keyBase: string): ReactNode[] {
  return text.split(INLINE).map((part, i) => {
    const key = `${keyBase}-${i}`
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return createElement('strong', { key }, part.slice(2, -2))
    }
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return createElement('code', { key }, part.slice(1, -1))
    }
    const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(part)
    if (link) {
      return SAFE_HREF.test(link[2])
        ? createElement('a', { key, href: link[2], rel: 'noreferrer' }, link[1])
        : link[1]
    }
    return part
  })
}

export function renderMarkdown(source: string): ReactNode[] {
  const out: ReactNode[] = []
  const lines = source.replace(/\r\n?/g, '\n').split('\n')
  let para: string[] = []
  let items: string[] = []

  const flushPara = () => {
    if (para.length) {
      const k = `p${out.length}`
      out.push(createElement('p', { key: k }, ...inline(para.join(' '), k)))
      para = []
    }
  }
  const flushList = () => {
    if (items.length) {
      const k = `ul${out.length}`
      out.push(
        createElement(
          'ul',
          { key: k },
          ...items.map((t, i) => createElement('li', { key: `${k}-${i}` }, ...inline(t, `${k}-${i}`))),
        ),
      )
      items = []
    }
  }

  for (const raw of lines) {
    const line = raw.trim()
    const heading = /^(#{1,6})\s+(.*)$/.exec(line)
    const bullet = /^[-*]\s+(.*)$/.exec(line)
    if (heading) {
      flushPara()
      flushList()
      const k = `h${out.length}`
      out.push(createElement(`h${heading[1].length}`, { key: k }, ...inline(heading[2], k)))
    } else if (bullet) {
      flushPara()
      items.push(bullet[1])
    } else if (line === '') {
      flushPara()
      flushList()
    } else if (items.length) {
      items[items.length - 1] += ` ${line}`
    } else {
      para.push(line)
    }
  }
  flushPara()
  flushList()
  return out
}
