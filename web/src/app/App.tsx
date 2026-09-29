import { FileText, PlayCircle, SlidersHorizontal } from 'lucide-react'
import { Icon } from '../ui/Icon'
import { EmptyState } from '../ui/EmptyState'
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
      return (
        <EmptyState icon={PlayCircle} title="Replay a real engine run">
          Pick a fault run from the test bench and play it back to see when Keyframe raised
          the alarm. The run list appears here.
        </EmptyState>
      )
    case 'what-if':
      return (
        <EmptyState
          icon={SlidersHorizontal}
          title="Try your own readings"
          action={<a href={hrefFor({ page: 'replay', runId: null })}>Go to Replay</a>}
        >
          Set an engine load, move key readings and watch the diagnosis change. This view
          needs the Keyframe API; until it is built, replay a recorded run instead.
        </EmptyState>
      )
    case 'model-card':
      return (
        <EmptyState
          icon={FileText}
          title="How good is Keyframe, and where does it fail?"
          action={<a href={hrefFor({ page: 'replay', runId: null })}>Go to Replay</a>}
        >
          The model card lists the scores on engine loads the model never trained on, the
          dataset credit and the known limits. It appears here in the next part of the build.
        </EmptyState>
      )
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
