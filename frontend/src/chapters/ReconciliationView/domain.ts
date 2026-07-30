import type { Summary, RootCause, TrueFill, RootCauseKey } from '../../types'

// Lailara Design System v2 hex values — CSS vars don't work in SVG fill attributes
export const ROOT_CAUSE_COLORS: Record<RootCauseKey, string> = {
  warehouse_late:        '#158f75',  // --color-hk-35
  carrier_late:          '#6dcdb5',  // --color-hk-70
  short_ship:            '#ee8a2a',  // --color-sg-55
  receiving_discrepancy: '#f6b97c',  // --color-sg-70
}

export interface DecompositionBar {
  label: string
  pts: number
  pct: number
  failure_mode: 'on_time' | 'in_full'
}

export interface RootCauseBar {
  cause: RootCauseKey
  label: string
  failure_mode: 'on_time' | 'in_full'
  gap_pts: number
  shipment_count: number
  pct_of_gap: number
}

export interface TrueFillComparison {
  fill_855_label: string
  fill_855_value: number
  fill_850_label: string
  fill_850_value: number
  delta_label: string
  delta_value: number
}

export function deriveDecompositionBars(summary: Summary): DecompositionBar[] {
  const total = summary.gap_pts
  const share = (pts: number) => (total > 0 ? pts / total : 0)
  return [
    {
      label: 'On-time failures',
      pts: summary.ontime_gap_pts,
      pct: share(summary.ontime_gap_pts),
      failure_mode: 'on_time',
    },
    {
      label: 'In-full failures',
      pts: summary.infull_gap_pts,
      pct: share(summary.infull_gap_pts),
      failure_mode: 'in_full',
    },
  ]
}

export function deriveRootCauseBars(rootCauses: RootCause[]): RootCauseBar[] {
  return [...rootCauses].sort((a, b) => b.gap_pts - a.gap_pts)
}

export function deriveTrueFillComparison(trueFill: TrueFill): TrueFillComparison {
  // fill_vs_855 = units shipped ÷ ordered (shipping-dock fill);
  // fill_vs_850 = units received ÷ ordered (receiving-dock fill);
  // the delta is what went missing between the two docks. The 855/850 field
  // names are legacy — the data carries shipped/received/ordered, not an EDI
  // acknowledgment layer.
  return {
    fill_855_label: 'Fill at the shipping dock — shipped ÷ ordered',
    fill_855_value: trueFill.fill_vs_855,
    fill_850_label: 'Fill at the receiving dock — received ÷ ordered',
    fill_850_value: trueFill.fill_vs_850,
    delta_label: 'lost between the two docks',
    delta_value: trueFill.trimming_gap_pts,
  }
}
