import type { LucideIcon } from 'lucide-react'

/** The only way to render an icon: one family (Lucide), three sizes (manifesto Part 14). */
export type IconSize = 16 | 20 | 24

interface IconProps {
  icon: LucideIcon
  size?: IconSize
  /** Accessible name. Omit for icons next to a visible label (they are then hidden). */
  label?: string
}

export function Icon({ icon: Glyph, size = 20, label }: IconProps) {
  return (
    <Glyph
      size={size}
      strokeWidth={2}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? 'img' : undefined}
      focusable="false"
    />
  )
}
