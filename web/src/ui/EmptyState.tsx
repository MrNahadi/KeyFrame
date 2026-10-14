import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import styles from './EmptyState.module.css'
import { Icon } from './Icon'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  children: ReactNode
  action?: ReactNode
}

/** A short heading, one sentence, and the one action that fills the space (MY-DESIGN §10.16). */
export function EmptyState({ icon, title, children, action }: EmptyStateProps) {
  return (
    <section className={styles.empty}>
      <span className={styles.circle}>
        <Icon icon={icon} size={24} />
      </span>
      <h2 className={styles.title}>{title}</h2>
      <div className={styles.body}>{children}</div>
      {action ? <div className={styles.action}>{action}</div> : null}
    </section>
  )
}
