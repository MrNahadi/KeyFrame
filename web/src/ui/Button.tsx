import type { ComponentPropsWithRef, ReactNode } from 'react'
import styles from './Button.module.css'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'md' | 'lg' | 'xl'

interface ButtonProps extends ComponentPropsWithRef<'button'> {
  variant?: Variant
  size?: Size
  /** A circle holding one icon; needs an aria-label. */
  iconOnly?: boolean
  children: ReactNode
}

function classes(variant: Variant, size: Size, iconOnly: boolean, extra?: string) {
  return [styles.button, styles[variant], styles[size], iconOnly && styles.icon, extra].filter(Boolean).join(' ')
}

/**
 * One pill shape, three weights (MY-DESIGN §10.1): primary once per view, secondary beside
 * it, ghost for quiet actions. Sizes: md is the app default (32px, 44px on touch), lg 40px,
 * xl 44px.
 */
export function Button({
  variant = 'secondary',
  size = 'md',
  iconOnly = false,
  className,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button type="button" className={classes(variant, size, iconOnly, className)} {...rest}>
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
export function LinkButton({ href, variant = 'primary', size = 'md', children }: LinkButtonProps) {
  return (
    <a className={classes(variant, size, false)} href={href}>
      {children}
    </a>
  )
}
