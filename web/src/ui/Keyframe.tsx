/**
 * The keyframe diamond, the product's one signature mark: hollow for the moment the fault
 * was switched on, filled red for the moment the model raised the alarm.
 */
export function Keyframe({ kind, size = 12 }: { kind: 'switch-on' | 'alarm'; size?: number }) {
  const half = size / 2
  const points = `${half},1 ${size - 1},${half} ${half},${size - 1} 1,${half}`
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true" focusable="false">
      <polygon
        points={points}
        fill={kind === 'alarm' ? 'var(--alarm)' : 'var(--surface)'}
        stroke={kind === 'alarm' ? 'var(--alarm)' : 'var(--switch-on)'}
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
    </svg>
  )
}

/** The brand mark: the keyframe diamond on a near-black tile, in the ink colour of the text. */
export function Logo({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <rect width="24" height="24" rx="6" fill="var(--primary-fill)" />
      <polygon points="12,5 19,12 12,19 5,12" fill="var(--on-primary)" />
    </svg>
  )
}
