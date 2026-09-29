export interface RunSummary {
  id: string
  title: string
  duration_s: number
  switch_on_t: number | null
  alarm_delay_s: number | null
}

export interface SensorReading {
  label: string
  value: number
  unit: string
}

export interface TopFeature {
  feature: string
  /** null when the value is undefined, e.g. a rolling spread over a run's first reading. */
  value: number | null
  shap: number
}

export interface ReplayFrame {
  t: number
  sensors: Record<string, SensorReading>
  probabilities: Record<string, number>
  alarm: string
  predicted_class: string
  shap_groups: Record<string, number>
  top_features: TopFeature[]
}

export interface Replay {
  run: string
  fault: string
  nominal_load: number | null
  switch_on_t: number | null
  sampling_note: string
  provenance: string
  frames: ReplayFrame[]
}
