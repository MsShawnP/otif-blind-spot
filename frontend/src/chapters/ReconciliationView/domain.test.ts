import { describe, it, expect } from 'vitest'
import {
  deriveDecompositionBars,
  deriveRootCauseBars,
  deriveTrueFillComparison,
  ROOT_CAUSE_COLORS,
} from './domain'
import type { Summary, RootCause, TrueFill } from '../../types'

const mockSummary: Summary = {
  internal_fill_rate: 0.95,
  retailer_otif: 0.86,
  gap_pts: 9.0,
  ontime_gap_pts: 5.0,
  infull_gap_pts: 4.0,
  total_shipments: 100,
  walmart_shipments: 100,
  window_start: '2024-01-01',
  window_end: '2026-03-31',
}

const mockRootCauses: RootCause[] = [
  { cause: 'order_trimming',       label: 'Order trimming',        failure_mode: 'in_full',  gap_pts: 1.5, shipment_count: 10, pct_of_gap: 0.167 },
  { cause: 'warehouse_late',       label: 'Warehouse late',        failure_mode: 'on_time',  gap_pts: 3.0, shipment_count: 20, pct_of_gap: 0.333 },
  { cause: 'carrier_late',         label: 'Carrier late',          failure_mode: 'on_time',  gap_pts: 2.0, shipment_count: 15, pct_of_gap: 0.222 },
  { cause: 'production_short_ship',label: 'Production short-ship', failure_mode: 'in_full',  gap_pts: 2.5, shipment_count: 18, pct_of_gap: 0.278 },
]

const mockTrueFill: TrueFill = {
  fill_vs_855: 0.95,
  fill_vs_850: 0.91,
  trimming_gap_pts: 4.0,
  orders_with_trimming: 35,
  pct_orders_trimmed: 0.35,
}

describe('deriveDecompositionBars', () => {
  it('returns two bars summing to the total gap', () => {
    const bars = deriveDecompositionBars(mockSummary)
    expect(bars).toHaveLength(2)
    const totalPts = bars.reduce((sum, b) => sum + b.pts, 0)
    expect(totalPts).toBeCloseTo(9.0, 1)
  })

  it('first bar is on_time, second is in_full', () => {
    const bars = deriveDecompositionBars(mockSummary)
    expect(bars[0].failure_mode).toBe('on_time')
    expect(bars[1].failure_mode).toBe('in_full')
  })

  it('pct values sum to 1.0', () => {
    const bars = deriveDecompositionBars(mockSummary)
    const totalPct = bars.reduce((sum, b) => sum + b.pct, 0)
    expect(totalPct).toBeCloseTo(1.0, 4)
  })
})

describe('deriveRootCauseBars', () => {
  it('sorts bars descending by gap_pts', () => {
    const bars = deriveRootCauseBars(mockRootCauses)
    for (let i = 0; i < bars.length - 1; i++) {
      expect(bars[i].gap_pts).toBeGreaterThanOrEqual(bars[i + 1].gap_pts)
    }
  })

  it('returns all 4 causes', () => {
    const bars = deriveRootCauseBars(mockRootCauses)
    expect(bars).toHaveLength(4)
  })

  it('does not mutate the original array', () => {
    const original = [...mockRootCauses]
    deriveRootCauseBars(mockRootCauses)
    expect(mockRootCauses[0].cause).toBe(original[0].cause)
  })
})

describe('deriveTrueFillComparison', () => {
  it('fill_vs_855 is higher than fill_vs_850', () => {
    const comp = deriveTrueFillComparison(mockTrueFill)
    expect(comp.fill_855_value).toBeGreaterThan(comp.fill_850_value)
  })

  it('returns delta_value matching trimming_gap_pts', () => {
    const comp = deriveTrueFillComparison(mockTrueFill)
    expect(comp.delta_value).toBe(4.0)
  })

  it('delta_label mentions order trimming', () => {
    const comp = deriveTrueFillComparison(mockTrueFill)
    expect(comp.delta_label.toLowerCase()).toContain('order trimming')
  })
})

describe('ROOT_CAUSE_COLORS', () => {
  it('has entries for all 4 root causes', () => {
    const causes = ['warehouse_late', 'carrier_late', 'production_short_ship', 'order_trimming']
    for (const cause of causes) {
      expect(ROOT_CAUSE_COLORS[cause]).toBeDefined()
      expect(ROOT_CAUSE_COLORS[cause]).toMatch(/^#[0-9a-f]{6}$/i)
    }
  })
})
