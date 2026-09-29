import { AlertTriangle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { EmptyState } from '../ui/EmptyState'
import { renderMarkdown } from './markdown'
import styles from './ModelCardPage.module.css'

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
          <button type="button" className={styles.button} onClick={() => setAttempt((a) => a + 1)}>
            Try again
          </button>
        }
      >
        {state.message}
      </EmptyState>
    )
  }

  return (
    <article className={styles.page}>
      <div className={styles.card}>{renderMarkdown(state.card)}</div>
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
        <a href={NOTEBOOK_URL} rel="noreferrer">
          Full evaluation notebook on GitHub
        </a>
      </p>
    </article>
  )
}
