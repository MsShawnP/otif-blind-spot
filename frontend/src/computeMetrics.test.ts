import { describe, it, expect } from 'vitest'
import {
  summary as fullSummary,
  rootCauses as fullRootCauses,
  trueFill as fullTrueFill,
  exposure as fullExposure,
  auditRows,
  portfolioShipments,
  chargebackRows,
} from './data'
import {
  presetToRange,
  filterByShipDate,
  computeSummary,
  computeRootCauses,
  computeTrueFill,
  computeExposure,
  type WindowRange,
} from './computeMetrics'
import type { AuditRow, PortfolioShipment, ChargebackRow } from './types'

// The full-corpus range mirrors what App.tsx uses when the 'all' preset is active.
const FULL_RANGE: WindowRange = {
  start: fullSummary.window_start,
  end: fullSummary.window_end,
}

// ─── Parity: the client-side recompute must reproduce the Python pipeline ─────
// This is the guard against computeMetrics.ts silently drifting from
// scripts/02_export_json.py. Run the same full corpus through the TS functions
// and assert the output matches the baked JSON the Python pipeline produced.
// Money/rate fields allow a 1-cent / rounding tolerance because Python's round()
// is banker's rounding while Math.round is half-up.
describe('parity: full-corpus recompute matches the baked pipeline output', () => {
  it('computeSummary matches summary.json', () => {
    const s = computeSummary(auditRows, portfolioShipments, FULL_RANGE)
    expect(s.internal_fill_rate).toBeCloseTo(fullSummary.internal_fill_rate, 4)
    expect(s.retailer_otif).toBeCloseTo(fullSummary.retailer_otif, 4)
    expect(s.gap_pts).toBeCloseTo(fullSummary.gap_pts, 2)
    expect(s.ontime_gap_pts).toBeCloseTo(fullSummary.ontime_gap_pts, 2)
    expect(s.infull_gap_pts).toBeCloseTo(fullSummary.infull_gap_pts, 2)
    expect(s.walmart_shipments).toBe(fullSummary.walmart_shipments)
  })

  it('computeRootCauses matches root_causes.json', () => {
    const rc = computeRootCauses(auditRows, fullSummary)
    expect(rc).toHaveLength(fullRootCauses.length)
    for (const expected of fullRootCauses) {
      const actual = rc.find((r) => r.cause === expected.cause)
      expect(actual, `cause ${expected.cause} present`).toBeDefined()
      expect(actual!.gap_pts).toBeCloseTo(expected.gap_pts, 2)
      expect(actual!.shipment_count).toBe(expected.shipment_count)
      expect(actual!.pct_of_gap).toBeCloseTo(expected.pct_of_gap, 4)
    }
  })

  it('computeTrueFill matches true_fill.json', () => {
    const tf = computeTrueFill(auditRows)
    expect(tf.fill_vs_855).toBeCloseTo(fullTrueFill.fill_vs_855, 4)
    expect(tf.fill_vs_850).toBeCloseTo(fullTrueFill.fill_vs_850, 4)
    expect(tf.trimming_gap_pts).toBeCloseTo(fullTrueFill.trimming_gap_pts, 2)
  })

  it('computeExposure matches exposure.json', () => {
    const ex = computeExposure(auditRows, chargebackRows, FULL_RANGE)
    expect(ex.annual_fines).toBeCloseTo(fullExposure.annual_fines, 0)
    expect(ex.annual_velocity_damage).toBeCloseTo(fullExposure.annual_velocity_damage, 0)
    expect(ex.total_exposure).toBeCloseTo(fullExposure.total_exposure, 0)
  })
})

// ─── Edge cases: guard branches must produce zeros, not NaN ────────────────────
describe('edge cases: empty and zero-denominator windows', () => {
  const emptyRange: WindowRange = { start: '2099-01-01', end: '2099-12-31' }

  it('computeSummary on empty inputs yields zeros, not NaN', () => {
    const s = computeSummary([], [], emptyRange)
    expect(s.internal_fill_rate).toBe(0)
    expect(s.retailer_otif).toBe(0)
    expect(s.gap_pts).toBe(0)
    expect(s.ontime_gap_pts).toBe(0)
    expect(s.infull_gap_pts).toBe(0)
    expect(Number.isNaN(s.gap_pts)).toBe(false)
  })

  it('computeTrueFill on empty input yields zeros, not NaN', () => {
    const tf = computeTrueFill([])
    expect(tf.fill_vs_855).toBe(0)
    expect(tf.fill_vs_850).toBe(0)
    expect(tf.trimming_gap_pts).toBe(0)
  })

  it('computeExposure on empty input yields zeros, not NaN', () => {
    const ex = computeExposure([], [], emptyRange)
    expect(ex.annual_fines).toBe(0)
    expect(ex.annual_velocity_damage).toBe(0)
    expect(ex.total_exposure).toBe(0)
    expect(ex.velocity_by_sku).toEqual([])
  })

  it('computeRootCauses with a zero gap yields zero pct_of_gap', () => {
    const zeroSummary = { ...fullSummary, gap_pts: 0, ontime_gap_pts: 0, infull_gap_pts: 0 }
    const rc = computeRootCauses(auditRows, zeroSummary)
    for (const r of rc) {
      expect(r.gap_pts).toBe(0)
      expect(r.pct_of_gap).toBe(0)
    }
  })
})

// ─── computeExposure: value assertions on the annualization + velocity formula ─
describe('computeExposure: annualization and velocity math', () => {
  function auditRow(overrides: Partial<AuditRow> = {}): AuditRow {
    return {
      shipment_id: 'RS-x',
      po_number: 'PO-WMT-1',
      ship_date: '2025-01-15',
      mabd: '2025-01-18',
      delivery_date: '2025-01-16',
      on_time_result: true,
      on_time_root_cause: null,
      po_units: 100,
      acknowledged_units: 100,
      shipped_units: 80, // 20-unit shortfall → 20 × $3.50 = $70 velocity
      in_full_result: false,
      in_full_root_cause: 'short_ship',
      ...overrides,
    }
  }

  it('scales a 6-month window up to a 12-month annual figure', () => {
    const rows = [auditRow()]
    const cb: ChargebackRow[] = [
      { retailer: 'Walmart', reason: 'short_ship', amount: 100, month: '2025-03' },
    ]
    // Jan–Jun 2025 = 6 months → scale 12/6 = 2×
    const ex = computeExposure(rows, cb, { start: '2025-01-01', end: '2025-06-30' })
    expect(ex.annual_fines).toBeCloseTo(200, 2) // 100 × 2
    expect(ex.annual_velocity_damage).toBeCloseTo(140, 2) // 70 × 2
    expect(ex.total_exposure).toBeCloseTo(340, 2)
  })

  it('only counts Walmart chargebacks toward fines', () => {
    const cb: ChargebackRow[] = [
      { retailer: 'Walmart', reason: 'short_ship', amount: 100, month: '2025-03' },
      { retailer: 'Kroger', reason: 'short_ship', amount: 999, month: '2025-03' },
    ]
    // 12-month window → scale 1×
    const ex = computeExposure([auditRow()], cb, { start: '2025-01-01', end: '2025-12-31' })
    expect(ex.annual_fines).toBeCloseTo(100, 2)
  })
})

// ─── presetToRange: date math at boundaries ────────────────────────────────────
describe('presetToRange', () => {
  it('returns the full corpus for a null-weeks preset', () => {
    const r = presetToRange({ key: 'all', label: 'Full corpus', weeks: null }, '2023-01-01', '2025-12-31')
    expect(r).toEqual({ start: '2023-01-01', end: '2025-12-31' })
  })

  it('computes a 13-week window back from the corpus end', () => {
    const r = presetToRange({ key: '13w', label: 'Last 13 weeks', weeks: 13 }, '2023-01-01', '2025-12-31')
    expect(r.end).toBe('2025-12-31')
    // 13 weeks = 91 days back, inclusive → 2025-10-02
    expect(r.start).toBe('2025-10-02')
  })

  it('filterByShipDate drops rows outside the range and null ship dates', () => {
    const rows: PortfolioShipment[] = [
      { ship_date: '2025-01-01', units_ordered: 1, units_shipped: 1 },
      { ship_date: '2025-06-01', units_ordered: 1, units_shipped: 1 },
      { ship_date: null, units_ordered: 1, units_shipped: 1 },
    ]
    const kept = filterByShipDate(rows, { start: '2025-01-01', end: '2025-03-31' })
    expect(kept).toHaveLength(1)
    expect(kept[0].ship_date).toBe('2025-01-01')
  })
})
