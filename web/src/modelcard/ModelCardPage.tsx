import { AlertTriangle, Check, ExternalLink, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { EmptyState } from '../ui/EmptyState'
import { Icon } from '../ui/Icon'
import { renderMarkdown } from './markdown'
import styles from './ModelCardPage.module.css'
import { SCORECARD } from './scorecard'

const NOTEBOOK_URL = 'https://github.com/MrNahadi/KeyFrame/blob/main/notebooks/07_evaluation.ipynb'
const publicUrl = (path: string) => `${import.meta.env.BASE_URL}${path}`

export async function loadModelCard(): Promise<string> {
  let res: Response
  try {
    res = await fetch(publicUrl('model_card.md'))
  } catch {
    throw new Error('Could not reach the model card file. Check your connection.')
  }
  if (!res.ok) throw new Error(`The model card was not found (HTTP ${res.status}).`)
  return res.text()
}

type Load = { kind: 'loading' } | { kind: 'error'; message: string } | { kind: 'ready'; card: string }

export function ModelCardPage({ load = loadModelCard }: { load?: () => Promise<string> }) {
  const [state, setState] = useState<Load>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let live = true
    setState({ kind: 'loading' })
    load().then(
      (card) => {
        if (live) setState({ kind: 'ready', card })
      },
      (e: unknown) => {
        if (live) setState({ kind: 'error', message: e instanceof Error ? e.message : 'Unknown error' })
      },
    )
    return () => {
      live = false
    }
  }, [load, attempt])

  if (state.kind === 'loading') {
    return (
      <div className={styles.page} role="status" aria-label="Loading model card">
        {[0, 1, 2].map((i) => (
          <div key={i} className={styles.skeleton} aria-hidden="true" />
        ))}
      </div>
    )
  }

  if (state.kind === 'error') {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="The model card could not be loaded"
        action={
          <Button variant="primary" onClick={() => setAttempt((a) => a + 1)}>
            Try again
          </Button>
        }
      >
        {state.message}
      </EmptyState>
    )
  }

  const met = SCORECARD.filter((s) => s.met).length
  const { title, body } = splitTitle(state.card)

  return (
    <article className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.lead}>
          How good the model is and where it fails, scored on engine loads it never saw. {met} of{' '}
          {SCORECARD.length} targets met.
        </p>
      </header>

      <section aria-labelledby="targets-title" className={styles.section}>
        <h2 id="targets-title" className={styles.sectionTitle}>
          Targets
        </h2>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">Measure</th>
                <th scope="col" className={styles.num}>
                  Result
                </th>
                <th scope="col" className={styles.num}>
                  Target
                </th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {SCORECARD.map((s) => (
                <tr key={s.metric}>
                  <th scope="row">
                    {s.metric}
                    {s.note && <span className={styles.note}>{s.note}</span>}
                  </th>
                  <td className={`${styles.num} ${styles.result}`}>{s.result}</td>
                  <td className={`${styles.num} ${styles.target}`}>
                    <span className={styles.phoneLabel}>Target </span>
                    {s.target}
                  </td>
                  <td className={styles.statusCell}>
                    <span className={s.met ? `${styles.status} ${styles.met}` : styles.status}>
                      <Icon icon={s.met ? Check : X} size={16} />
                      {s.met ? 'Met' : 'Not met'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className={styles.card}>{renderMarkdown(body)}</div>

      <figure className={styles.figure}>
        <img
          className={styles.image}
          src={publicUrl('figures/07_confusion.png')}
          alt="Confusion matrix: true fault state against predicted state on held-out engine loads"
        />
        <figcaption className={styles.caption}>
          Confusion matrix on held-out engine loads: rows are the true state, columns the prediction.
        </figcaption>
      </figure>
      <p>
        <a className={styles.external} href={NOTEBOOK_URL} rel="noreferrer">
          Full evaluation notebook on GitHub
          <Icon icon={ExternalLink} size={16} />
        </a>
      </p>
    </article>
  )
}

/** The card's own first heading becomes the page title, so the page has one h1. */
function splitTitle(card: string): { title: string; body: string } {
  const match = /^\s*#\s+(.+)\n?/.exec(card)
  if (!match) return { title: 'Model card', body: card }
  return { title: match[1].trim(), body: card.slice(match[0].length) }
}
