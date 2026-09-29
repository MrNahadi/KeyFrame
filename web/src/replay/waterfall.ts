export interface WaterfallStep {
  name: string
  value: number
  start: number
  end: number
  sign: 'positive' | 'negative'
}

export interface Waterfall {
  base: number
  output: number
  steps: WaterfallStep[]
}

const GROUP_NAMES: Record<string, string> = {
  'air path': 'Air path',
  'combustion and power': 'Combustion and power',
  'fuel system': 'Fuel system',
  cooling: 'Cooling',
  'lube oil': 'Lube oil',
}

function plainName(key: string): string {
  return GROUP_NAMES[key] ?? key.charAt(0).toUpperCase() + key.slice(1)
}

/** Grouped SHAP values (predicted class) to steps from the base value to the model output. */
export function buildWaterfall(shapGroups: Record<string, number>, base: number): Waterfall {
  const ordered = Object.entries(shapGroups).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
  let running = base
  const steps = ordered.map(([key, value]) => {
    const start = running
    running += value
    return {
      name: plainName(key),
      value,
      start,
      end: running,
      sign: value < 0 ? ('negative' as const) : ('positive' as const),
    }
  })
  return { base, output: running, steps }
}
