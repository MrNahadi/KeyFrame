import { FileText, PlayCircle, SlidersHorizontal } from 'lucide-react'
import { Icon } from '../ui/Icon'
import { WhatIfScreen } from '../whatif/WhatIfScreen'
import { RunPicker } from '../replay/RunPicker'
import { ReplayScreen } from '../replay/ReplayScreen'
import { ModelCardPage } from '../modelcard/ModelCardPage'
import styles from './App.module.css'
import { hrefFor, type Route, useRoute } from './routes'

const NAV: { page: Route['page']; label: string; icon: typeof PlayCircle }[] = [
  { page: 'replay', label: 'Replay', icon: PlayCircle },
  { page: 'what-if', label: 'What-if', icon: SlidersHorizontal },
  { page: 'model-card', label: 'Model card', icon: FileText },
]

function Page({ route }: { route: Route }) {
  switch (route.page) {
    case 'replay':
      return route.runId ? (
        <div>
          <p className={styles.pageLead}>
            <a href={hrefFor({ page: 'replay', runId: null })}>Back to all runs</a>
          </p>
          <ReplayScreen key={route.runId} runId={route.runId} />
        </div>
      ) : (
        <div>
          <h1 className={styles.pageTitle}>Replay a real engine run</h1>
          <p className={styles.pageLead}>
            Pick a fault run from the test bench and play it back to see when Keyframe raised
            the alarm.
          </p>
          <RunPicker />
        </div>
      )
    case 'what-if':
      return <WhatIfScreen />
    case 'model-card':
      return <ModelCardPage />
  }
}

export function App() {
  const route = useRoute()
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <a className={styles.brand} href={hrefFor({ page: 'replay', runId: null })}>
          Keyframe
        </a>
        <nav aria-label="Primary">
          <ul className={styles.nav}>
            {NAV.map((item) => {
              const active = route.page === item.page
              const href =
                item.page === 'replay'
                  ? hrefFor({ page: 'replay', runId: null })
                  : hrefFor({ page: item.page } as Route)
              return (
                <li key={item.page}>
                  <a
                    className={active ? `${styles.navLink} ${styles.active}` : styles.navLink}
                    href={href}
                    aria-current={active ? 'page' : undefined}
                  >
                    <Icon icon={item.icon} size={16} />
                    <span>{item.label}</span>
                  </a>
                </li>
              )
            })}
          </ul>
        </nav>
      </header>
      <main className={styles.main}>
        <Page route={route} />
      </main>
    </div>
  )
}
