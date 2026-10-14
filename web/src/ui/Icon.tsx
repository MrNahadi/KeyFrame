import type { LucideIcon } from 'lucide-react'

/** The only way to render an icon: one family (Lucide), three sizes, 1.5px stroke (MY-DESIGN §12). */
export type IconSize = 16 | 20 | 24

interface IconProps {
  icon: LucideIcon
  size?: IconSize
  /** Accessible name. Omit for icons next to a visible label (they are then hidden). */
  label?: string
  className?: string
}

export function Icon({ icon: Glyph, size = 20, label, className }: IconProps) {
  return (
    <Glyph
      size={size}
      strokeWidth={1.5}
      absoluteStrokeWidth
      className={className}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? 'img' : undefined}
      focusable="false"
    />
  )
}
