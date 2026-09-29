import { useRef, type KeyboardEvent } from 'react'
import styles from './Segmented.module.css'

interface SegmentedProps<T extends string | number> {
  label: string
  options: { value: T; label: string }[]
  value: T
  onChange: (value: T) => void
}

const NEXT: Record<string, number> = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }

/**
 * A small set of mutually exclusive choices shown side by side. Radio group semantics: one
 * tab stop (the checked option), arrow keys move and select.
 */
export function Segmented<T extends string | number>({ label, options, value, onChange }: SegmentedProps<T>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([])
  const current = Math.max(0, options.findIndex((o) => o.value === value))

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const step = NEXT[e.key]
    if (step === undefined || options.length === 0) return
    e.preventDefault()
    e.stopPropagation()
    const i = (current + step + options.length) % options.length
    onChange(options[i].value)
    refs.current[i]?.focus()
  }

  return (
    <div className={styles.group} role="radiogroup" aria-label={label} onKeyDown={onKeyDown}>
      {options.map((o, i) => (
        <button
          key={String(o.value)}
          ref={(el) => {
            refs.current[i] = el
          }}
          type="button"
          role="radio"
          aria-checked={o.value === value}
          tabIndex={i === current ? 0 : -1}
          className={o.value === value ? `${styles.option} ${styles.on}` : styles.option}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}
