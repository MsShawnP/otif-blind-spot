import type { Summary, RootCause, TrueFill } from '../../types'

// Lailara Design System v2 hex values — CSS vars don't work in SVG fill attributes
export const ROOT_CAUSE_COLORS: Record<string, string> = {
  warehouse_late:        '#158f75',  // --color-hk-35
  carrier_late:          '#6dcdb5',  // --color-hk-70
  production_short_ship: '#ee8a2a',  // --color-sg-55
  order_trimming:        '#f6b97c',  // --color-sg-70
}

export const DEMO_DATE = '2026-05-31'

export interface DecompositionBar {
  label: string
  pts: number
  pct: number
  failure_mode: 'on_time' | 'in_full'
}

export interface RootCauseBar {
  cause: string
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
  const total = summary.gap_pts || 9
  return [
    {
      label: 'On-time failures',
      pts: summary.ontime_gap_pts,
      pct: summary.ontime_gap_pts / total,
      failure_mode: 'on_time',
    },
    {
      label: 'In-full failures',
      pts: summary.infull_gap_pts,
      pct: summary.infull_gap_pts / total,
      failure_mode: 'in_full',
    },
  ]
}

export function deriveRootCauseBars(rootCauses: RootCause[]): RootCauseBar[] {
  return [...rootCauses].sort((a, b) => b.gap_pts - a.gap_pts)
}

export function deriveTrueFillComparison(trueFill: TrueFill): TrueFillComparison {
  return {
    fill_855_label: 'Fill rate vs. acknowledged orders (855)',
    fill_855_value: trueFill.fill_vs_855,
    fill_850_label: 'True fill rate vs. original POs (850)',
    fill_850_value: trueFill.fill_vs_850,
    delta_label: 'Added by order trimming before acknowledgment',
    delta_value: trueFill.trimming_gap_pts,
  }
}
