/** Readings as an engineer would write them: a sensible precision and a proper unit. */

const UNITS: Record<string, string> = {
  'kgf/cm2': 'kgf/cm²',
  m3h: 'm³/h',
  'm3/h': 'm³/h',
  degC: '°C',
}

export function unit(raw: string): string {
  return UNITS[raw] ?? raw
}

const sigDecimals = (abs: number) => (abs >= 100 ? 0 : abs >= 10 ? 1 : abs >= 1 ? 2 : 3)

/** Three significant figures, never more than three decimals, no trailing float noise. */
export function number(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return '–'
  const decimals = sigDecimals(Math.abs(value))
  return value.toLocaleString('en-GB', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

export function reading(value: number | null | undefined, rawUnit: string): string {
  const u = unit(rawUnit)
  return u ? `${number(value)} ${u}` : number(value)
}

export function percent(p: number): string {
  return `${Math.round(p * 100)}%`
}

/** A signed contribution such as "+1.24" or "−0.38" (true minus sign); "0.00" when it rounds to zero. */
export function signed(v: number): string {
  const text = Math.abs(v).toFixed(2)
  if (Number(text) === 0) return '0.00'
  return `${v < 0 ? '−' : '+'}${text}`
}

/** "2 h 54 min", "35 min", "45 s". */
export function length(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  if (s < 60) return `${s} s`
  const minutes = Math.round(s / 60)
  if (minutes < 60) return `${minutes} min`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m === 0 ? `${h} h` : `${h} h ${m} min`
}

/** "9 min 5 s", "45 s". */
export function delay(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  const m = Math.floor(s / 60)
  return m === 0 ? `${s} s` : `${m} min ${s % 60} s`
}

const pad = (n: number) => String(n).padStart(2, '0')

/** Run clock, "1:04:30" or "53:21". */
export function clock(seconds: number): string {
  const s = Math.max(0, Math.round(seconds))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  return h > 0 ? `${h}:${pad(m)}:${pad(s % 60)}` : `${m}:${pad(s % 60)}`
}

/** Decimals an axis needs so that ticks across `range` stay distinct (0 to 4). */
export function axisDecimals(range: number): number {
  if (!Number.isFinite(range) || range <= 0) return 2
  return Math.min(4, Math.max(0, Math.ceil(-Math.log10(range)) + 1))
}

export function fixed(value: number, decimals: number): string {
  return value.toLocaleString('en-GB', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

/** A value on a control whose whole range is `range` wide: enough decimals to tell its steps apart. */
export function precise(value: number, range: number, rawUnit = ''): string {
  const text = fixed(value, Math.max(sigDecimals(Math.abs(value)), axisDecimals(range)))
  const u = unit(rawUnit)
  return u ? `${text} ${u}` : text
}
