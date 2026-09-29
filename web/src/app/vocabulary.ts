/** The product's words for faults and sensor groups, and each group's colour role. */

export const FAULT_NAMES: Record<string, string> = {
  Normal: 'Normal running',
  AC: 'Air cooler fouling',
  AF: 'Air filter clogging',
  INJ: 'Injector nozzle clogging',
  CW: 'Cooling water pump cavitation',
  TD: 'Turbine degradation',
}

/** Long class labels used by the dataset and older fixtures, mapped to the codes. */
const FAULT_ALIASES: Record<string, string> = {
  'AC Fouling': 'AC',
  'AF Clogging': 'AF',
  'Clogged Injector': 'INJ',
  'CW Pump': 'CW',
  'Turbine Degradation': 'TD',
}

/** Sentence-case fault name for a class code; unknown codes pass through. */
export function faultName(code: string): string {
  return FAULT_NAMES[FAULT_ALIASES[code] ?? code] ?? code
}

/** Lower-case form for use inside a sentence. */
export function faultPhrase(code: string): string {
  const name = FAULT_NAMES[FAULT_ALIASES[code] ?? code]
  return name ? name.charAt(0).toLowerCase() + name.slice(1) : code
}

export interface SensorGroup {
  key: string
  label: string
  colour: string
}

/**
 * Sensor groups in their fixed display order (the order the colour palette was validated
 * in). Colours echo ship pipework colour coding, see docs/design/keyframe-design-plan.md.
 */
export const GROUPS: SensorGroup[] = [
  { key: 'air path', label: 'Air path', colour: 'var(--group-air)' },
  { key: 'fuel system', label: 'Fuel system', colour: 'var(--group-fuel)' },
  { key: 'cooling', label: 'Cooling', colour: 'var(--group-cooling)' },
  { key: 'lube oil', label: 'Lube oil', colour: 'var(--group-lube)' },
  { key: 'combustion and power', label: 'Combustion and power', colour: 'var(--group-combustion)' },
]

export function group(key: string): SensorGroup {
  return (
    GROUPS.find((g) => g.key === key.toLowerCase()) ?? {
      key,
      label: key,
      colour: 'var(--text-secondary)',
    }
  )
}

/** Which group each replay sensor and what-if channel belongs to. */
const SENSOR_GROUP: Record<string, string> = {
  charge_air_pressure: 'air path',
  charge_air_temp_after_cooler: 'air path',
  turbine_in_temp: 'air path',
  turbine_out_temp: 'air path',
  exhaust_temp_spread: 'combustion and power',
  cooling_water_flow: 'cooling',
  fresh_cooling_water_pressure: 'cooling',
  fuel_flow: 'fuel system',
  'Charge Air Press.': 'air path',
  'Charge Air IC Air Temp. Out': 'air path',
  'Exh.Gas Temp. Turbine In': 'air path',
  'Exh.Gas Temp. Turbine Out': 'air path',
  'No.1 Exh.Gas Temp.': 'combustion and power',
  'No.2 Exh.Gas Temp.': 'combustion and power',
  'No.3 Exh.Gas Temp.': 'combustion and power',
  'Fresh Cooling Water Press.': 'cooling',
  'Engine Cooling water flow': 'cooling',
  'Fuel Flow': 'fuel system',
}

/** Shorter labels where the replay file's own label is too long for a chart title. */
const SENSOR_LABELS: Record<string, string> = {
  exhaust_temp_spread: 'Exhaust temperature spread, cylinders 1 to 3',
  fresh_cooling_water_pressure: 'Fresh cooling water pressure (sensor voltage)',
}

export function sensorLabel(key: string, fallback: string): string {
  return SENSOR_LABELS[key] ?? fallback
}

/** Index of a group in the fixed display order; unknown groups sort last. */
export function groupOrder(key: string): number {
  const i = GROUPS.findIndex((g) => g.key === key.toLowerCase())
  return i === -1 ? GROUPS.length : i
}

export function sensorGroup(sensor: string): SensorGroup {
  return group(SENSOR_GROUP[sensor] ?? 'other')
}

/** Engine-room feature names in plain words, e.g. "Charge Air IC Air Temp. Out_roll_300s_mean". */
export function featureName(feature: string): string {
  const [base, roll] = feature.split('_roll_')
  const plain = base
    .replace(/^resid_/, '')
    .replace(/^phys_/, '')
    .replace(/Exh\.Gas/g, 'exhaust gas')
    .replace(/Temp\./g, 'temperature')
    .replace(/Press\./g, 'pressure')
    .replace(/\bIC\b/g, 'cooler')
    .replace(/\bLO\b/g, 'lube oil')
    .replace(/\bTCH\b/g, 'turbocharger')
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  const sentence = plain.charAt(0).toUpperCase() + plain.slice(1).toLowerCase()
  if (!roll) return sentence
  const match = roll.match(/^(\d+)s_(mean|std|slope)$/)
  if (!match) return sentence
  const minutes = Math.round(Number(match[1]) / 60)
  const stat = { mean: 'average', std: 'spread', slope: 'trend' }[match[2] as 'mean' | 'std' | 'slope']
  return `${sentence}, ${minutes}-minute ${stat}`
}
