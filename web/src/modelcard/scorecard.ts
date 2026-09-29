/**
 * The brief's targets against the locked results (ADR 0009). Numbers are copied from
 * reports/results/*.csv and reports/physics_check.md; scorecard.test.ts checks them there.
 */
export interface Score {
  metric: string
  result: string
  target: string
  met: boolean
  note?: string
}

export const SCORECARD: Score[] = [
  { metric: 'Macro F1 on held-out loads', result: '0.717', target: '0.80', met: false },
  {
    metric: 'Lowest per-class recall',
    result: '0.194',
    target: '0.70',
    met: false,
    note: 'Turbine degradation',
  },
  { metric: 'False alarm rate', result: '12.2%', target: '5%', met: false },
  {
    metric: 'Detection delay',
    result: '9 min 23 s',
    target: '10 min',
    met: false,
    note: 'Median of the 6 of 13 fault runs that raised an alarm; the other 7 never did',
  },
  {
    metric: 'Fault detection AUROC',
    result: '0.528',
    target: '0.95',
    met: false,
    note: 'Anomaly detectors trained on healthy running only',
  },
  { metric: 'Expected calibration error', result: '0.176', target: '0.05', met: false },
  {
    metric: 'Unseen fault severity',
    result: '100%',
    target: '90%',
    met: true,
    note: 'Weak evidence: the model predicted injector clogging for every row of the lockbox',
  },
  { metric: 'Physics check on explanations', result: '2 of 5 faults', target: '4 of 5', met: false },
  {
    metric: 'Demo response time',
    result: '148 ms',
    target: '300 ms',
    met: true,
    note: 'Prediction plus explanation, median; measured after the scores were locked',
  },
]
