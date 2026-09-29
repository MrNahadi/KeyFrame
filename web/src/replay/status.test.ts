import { describe, expect, it } from 'vitest'
import { lowConfidenceNote } from './status'
import type { ReplayFrame } from './types'

const frame = (probabilities: Record<string, number>): ReplayFrame => ({
  t: 0,
  sensors: {},
  probabilities,
  alarm: 'Normal',
  predicted_class: 'Normal',
  shap_groups: {},
  top_features: [],
})

describe('lowConfidenceNote', () => {
  it('returns a sentence with the highest probability when no frame reaches 40%', () => {
    const note = lowConfidenceNote([frame({ Normal: 0.3, AC: 0.25 }), frame({ Normal: 0.35, AC: 0.2 })])
    expect(note).toContain('barely confident')
    expect(note).toContain('at most 35%')
  })

  it('returns null when any frame reaches 40%', () => {
    expect(lowConfidenceNote([frame({ Normal: 0.3 }), frame({ Normal: 0.4 })])).toBeNull()
  })

  it('returns null for an empty run', () => {
    expect(lowConfidenceNote([])).toBeNull()
  })
})
