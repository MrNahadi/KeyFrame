import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { SCORECARD } from './scorecard'

const REPORTS = join(__dirname, '..', '..', '..', 'reports')

/** Rows of a results CSV as objects (the files quote only the metric names). */
function csv(name: string): Record<string, string>[] {
  const [head, ...rows] = readFileSync(join(REPORTS, 'results', name), 'utf8').trim().split('\n')
  const split = (line: string) => [...line.matchAll(/("[^"]*"|[^,]*)(,|$)/g)].map((m) => m[1].replace(/^"|"$/g, ''))
  const keys = split(head)
  return rows.map((r) => Object.fromEntries(split(r).map((v, i) => [keys[i], v])))
}

const row = (metric: string) => SCORECARD.find((s) => s.metric === metric)!

describe('scorecard', () => {
  it('matches the locked classifier results', () => {
    const t = Object.fromEntries(csv('04_targets.csv').map((r) => [r.metric, r]))
    expect(row('Macro F1 on held-out loads').result).toBe(Number(t['Macro F1, held-out loads'].value).toFixed(3))
    expect(row('Lowest per-class recall').result).toBe(Number(t['Lowest per-class recall'].value).toFixed(3))
    expect(row('False alarm rate').result).toBe(`${(Number(t['False alarm rate'].value) * 100).toFixed(1)}%`)
    const delay = Number(t['Detection delay (median of detected runs)'].value)
    expect(row('Detection delay').result).toBe(`${Math.floor(delay / 60)} min ${delay % 60} s`)
    for (const r of Object.values(t)) expect(r.met).toBe('False')
  })

  it('matches the anomaly, calibration, lockbox and latency results', () => {
    const auroc = csv('05_targets.csv').find((r) => r.metric.startsWith('Fault detection AUROC'))!
    expect(row('Fault detection AUROC').result).toBe(Number(auroc.value).toFixed(3))
    expect(row('Expected calibration error').result).toBe(
      Number(csv('07_calibration.csv')[0].pooled_ece_before).toFixed(3),
    )
    const lockbox = csv('07_lockbox.csv').find((r) => r.scope === 'all')!
    expect(row('Unseen fault severity').result).toBe(`${Math.round(Number(lockbox.share) * 100)}%`)
    const explain = csv('11_latency.csv').find((r) => r.endpoint === '/explain')!
    expect(row('Demo response time').result).toBe(`${Math.round(Number(explain.median_ms))} ms`)
  })

  it('matches the physics check', () => {
    const report = readFileSync(join(REPORTS, 'physics_check.md'), 'utf8')
    const passed = /Result: (\d) of 5 faults pass/.exec(report)![1]
    expect(row('Physics check on explanations').result).toBe(`${passed} of 5 faults`)
  })

  it('meets exactly the two targets the model card says', () => {
    expect(SCORECARD.filter((s) => s.met).map((s) => s.metric)).toEqual([
      'Unseen fault severity',
      'Demo response time',
    ])
  })
})
