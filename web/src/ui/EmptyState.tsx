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

/** What goes here, plus the one action that fills it (manifesto Part 14, "States"). */
export function EmptyState({ icon, title, children, action }: EmptyStateProps) {
  return (
    <section className={styles.empty}>
      <Icon icon={icon} size={24} />
      <h2 className={styles.title}>{title}</h2>
      <div className={styles.body}>{children}</div>
      {action ? <div className={styles.action}>{action}</div> : null}
    </section>
  )
}
