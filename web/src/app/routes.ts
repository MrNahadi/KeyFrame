import { useEffect, useState } from 'react'

/** Hash routes, so the app works on any static host. */
export type Route =
  | { page: 'replay'; runId: string | null }
  | { page: 'what-if' }
  | { page: 'model-card' }

export function parseRoute(hash: string): Route {
  const path = hash.replace(/^#\/?/, '')
  const [page, ...rest] = path.split('/')
  if (page === 'what-if') return { page: 'what-if' }
  if (page === 'model-card') return { page: 'model-card' }
  const runId = page === 'replay' && rest[0] ? decodeURIComponent(rest[0]) : null
  return { page: 'replay', runId }
}

export function hrefFor(route: Route): string {
  switch (route.page) {
    case 'replay':
      return route.runId ? `#/replay/${encodeURIComponent(route.runId)}` : '#/replay'
    case 'what-if':
      return '#/what-if'
    case 'model-card':
      return '#/model-card'
  }
}

export function useRoute(): Route {
  const [route, setRoute] = useState(() => parseRoute(window.location.hash))
  useEffect(() => {
    const onChange = () => setRoute(parseRoute(window.location.hash))
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return route
}
