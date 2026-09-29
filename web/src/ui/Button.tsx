import type { ButtonHTMLAttributes, ReactNode } from 'react'
import styles from './Button.module.css'

type Variant = 'primary' | 'secondary' | 'tertiary'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  children: ReactNode
}

/** One button, three weights (manifesto Part 14): primary once per view, secondary, tertiary. */
export function Button({ variant = 'secondary', size = 'md', className, children, ...rest }: ButtonProps) {
  const cls = [styles.button, styles[variant], styles[size], className].filter(Boolean).join(' ')
  return (
    <button type="button" className={cls} {...rest}>
      {children}
    </button>
  )
}

interface LinkButtonProps {
  href: string
  variant?: Variant
  size?: Size
  children: ReactNode
}

/** A link that looks like a button, for navigation actions. */
export function LinkButton({ href, variant = 'primary', size = 'lg', children }: LinkButtonProps) {
  const cls = [styles.button, styles[variant], styles[size]].join(' ')
  return (
    <a className={cls} href={href}>
      {children}
    </a>
  )
}
