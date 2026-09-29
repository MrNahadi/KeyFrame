import styles from './Segmented.module.css'

interface SegmentedProps<T extends string | number> {
  label: string
  options: { value: T; label: string }[]
  value: T
  onChange: (value: T) => void
}

/** A small set of mutually exclusive choices shown side by side (radio group semantics). */
export function Segmented<T extends string | number>({ label, options, value, onChange }: SegmentedProps<T>) {
  return (
    <div className={styles.group} role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button
          key={String(o.value)}
          type="button"
          role="radio"
          aria-checked={o.value === value}
          className={o.value === value ? `${styles.option} ${styles.on}` : styles.option}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}
