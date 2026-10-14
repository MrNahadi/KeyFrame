import { ExternalLink, FileText, Menu, PlayCircle, SlidersHorizontal, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { ModelCardPage } from '../modelcard/ModelCardPage'
import { ReplayScreen } from '../replay/ReplayScreen'
import { RunsPage } from '../replay/RunsPage'
import { Button } from '../ui/Button'
import { Icon } from '../ui/Icon'
import { Logo } from '../ui/Keyframe'
import { WhatIfScreen } from '../whatif/WhatIfScreen'
import styles from './App.module.css'
import { hrefFor, type Route, useRoute } from './routes'

const NAV: { page: Route['page']; label: string; icon: typeof PlayCircle }[] = [
  { page: 'replay', label: 'Replay', icon: PlayCircle },
  { page: 'what-if', label: 'What-if', icon: SlidersHorizontal },
  { page: 'model-card', label: 'Model card', icon: FileText },
]

/** The marketing site, when the demo is deployed under it (set at build time). */
const SITE_URL: string | undefined = import.meta.env.VITE_SITE_URL || undefined

function Page({ route }: { route: Route }) {
  switch (route.page) {
    case 'replay':
      return route.runId ? <ReplayScreen key={route.runId} runId={route.runId} /> : <RunsPage />
    case 'what-if':
      return <WhatIfScreen />
    case 'model-card':
      return <ModelCardPage />
  }
}

const navHref = (page: Route['page']) =>
  page === 'replay' ? hrefFor({ page: 'replay', runId: null }) : hrefFor({ page } as Route)

/** The top bar's border appears only once content scrolls under it (MY-DESIGN §8). */
function useScrolled() {
  const sentinel = useRef<HTMLDivElement>(null)
  const [scrolled, setScrolled] = useState(false)
  useEffect(() => {
    const el = sentinel.current
    if (!el || typeof IntersectionObserver === 'undefined') return
    const io = new IntersectionObserver(([entry]) => setScrolled(!entry.isIntersecting))
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return { sentinel, scrolled }
}

export function App() {
  const route = useRoute()
  const [open, setOpen] = useState(false)
  const menuButton = useRef<HTMLButtonElement>(null)
  const firstLink = useRef<HTMLAnchorElement>(null)
  const { sentinel, scrolled } = useScrolled()
  const current = NAV.find((n) => n.page === route.page) ?? NAV[0]

  const close = useCallback(() => {
    setOpen(false)
    menuButton.current?.focus()
  }, [])

  // A new page starts at the top, and the drawer closes when a link changes the page (and on Esc).
  const mounted = useRef(false)
  useEffect(() => {
    setOpen(false)
    if (mounted.current) window.scrollTo(0, 0)
    mounted.current = true
  }, [route])
  useEffect(() => {
    if (!open) return
    firstLink.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, close])

  return (
    <div className={styles.shell} data-open={open || undefined}>
      <aside id="sidebar" className={styles.sidebar} aria-label="Sidebar">
        <div className={styles.sidebarHead}>
          <a className={styles.brand} href={navHref('replay')}>
            <Logo size={24} />
            <span>Keyframe</span>
          </a>
          <Button variant="ghost" iconOnly className={styles.closeMenu} onClick={close} aria-label="Close menu">
            <Icon icon={X} size={20} />
          </Button>
        </div>
        <nav aria-label="Primary">
          <ul className={styles.nav}>
            {NAV.map((item, i) => {
              const active = route.page === item.page
              return (
                <li key={item.page}>
                  <a
                    ref={i === 0 ? firstLink : undefined}
                    className={active ? `${styles.navLink} ${styles.active}` : styles.navLink}
                    href={navHref(item.page)}
                    aria-current={active ? 'page' : undefined}
                  >
                    <Icon icon={item.icon} size={20} />
                    <span>{item.label}</span>
                  </a>
                </li>
              )
            })}
          </ul>
        </nav>
        <div className={styles.sidebarFoot}>
          <p className={styles.note}>
            Bench results only. Not tested on a ship. Data: Marine Engine Fault Dataset v1.0 (BahooToroody et al.,
            2026), CC BY 4.0.
          </p>
          {SITE_URL && (
            <a className={styles.footLink} href={SITE_URL}>
              About Keyframe
              <Icon icon={ExternalLink} size={16} />
            </a>
          )}
        </div>
      </aside>
      <div className={styles.backdrop} onClick={close} aria-hidden="true" />

      <div className={styles.column} inert={open || undefined}>
        <header className={styles.topbar} data-scrolled={scrolled || undefined}>
          <Button
            ref={menuButton}
            variant="ghost"
            iconOnly
            className={styles.openMenu}
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            aria-expanded={open}
            aria-controls="sidebar"
          >
            <Icon icon={Menu} size={20} />
          </Button>
          <p className={styles.place}>{current.label}</p>
        </header>
        <div ref={sentinel} className={styles.sentinel} aria-hidden="true" />
        <main className={styles.main}>
          <Page route={route} />
        </main>
      </div>
    </div>
  )
}
