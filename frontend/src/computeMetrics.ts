import type { Summary, RootCause, TrueFill, Exposure, AuditRow, PortfolioShipment, ChargebackRow } from './types'

const VELOCITY_DAMAGE_PER_UNIT = 3.50

export interface WindowPreset {
  key: string
  label: string
  weeks: number | null
}

export interface WindowRange {
  start: string
  end: string
}

export const WINDOW_PRESETS: WindowPreset[] = [
  { key: '13w', label: 'Last 13 weeks', weeks: 13 },
  { key: '26w', label: 'Last 26 weeks', weeks: 26 },
  { key: '52w', label: 'Last 52 weeks', weeks: 52 },
  { key: 'all', label: 'Full corpus', weeks: null },
]

export const DEFAULT_PRESET_KEY = '52w'

export function presetToRange(
  preset: WindowPreset,
  corpusStart: string,
  corpusEnd: string,
): WindowRange {
  if (preset.weeks === null) {
    return { start: corpusStart, end: corpusEnd }
  }
  const [ey, em, ed] = corpusEnd.split('-').map(Number)
  const startDate = new Date(ey, em - 1, ed - preset.weeks * 7 + 1)
  const sy = startDate.getFullYear()
  const sm = String(startDate.getMonth() + 1).padStart(2, '0')
  const sd = String(startDate.getDate()).padStart(2, '0')
  return { start: `${sy}-${sm}-${sd}`, end: corpusEnd }
}

export function filterByShipDate<T extends { ship_date?: string | null }>(
  rows: T[],
  range: WindowRange,
): T[] {
  return rows.filter(r => {
    if (!r.ship_date) return false
    return r.ship_date >= range.start && r.ship_date <= range.end
  })
}

export function filterChargebacks(
  chargebacks: ChargebackRow[],
  range: WindowRange,
): ChargebackRow[] {
  const startMonth = range.start.slice(0, 7)
  const endMonth = range.end.slice(0, 7)
  return chargebacks.filter(cb => cb.month >= startMonth && cb.month <= endMonth)
}

function round4(n: number): number {
  return Math.round(n * 10000) / 10000
}

function round2(n: number): number {
  return Math.round(n * 100) / 100
}

export function computeSummary(
  wmRows: AuditRow[],
  portfolioRows: PortfolioShipment[],
  range: WindowRange,
): Summary {
  const totalOrdered = portfolioRows.reduce((s, r) => s + r.units_ordered, 0)
  const totalShipped = portfolioRows.reduce((s, r) => s + r.units_shipped, 0)
  const internalFill = totalOrdered > 0 ? round4(totalShipped / totalOrdered) : 0

  const wmTotal = wmRows.length
  const wmOtifPass = wmRows.filter(r => r.on_time_result && r.in_full_result).length
  const retailerOtif = wmTotal > 0 ? round4(wmOtifPass / wmTotal) : 0

  const gapPts = round2((internalFill - retailerOtif) * 100)

  let ontimeGapPts = 0
  let infullGapPts = 0

  if (wmTotal > 0 && gapPts > 0) {
    const ontimeFail = wmRows.filter(r => !r.on_time_result).length
    const infullFail = wmRows.filter(r => !r.in_full_result).length
    const totalFails = ontimeFail + infullFail
    if (totalFails > 0) {
      ontimeGapPts = round2(ontimeFail / totalFails * gapPts)
      infullGapPts = round2(gapPts - ontimeGapPts)
    }
  }

  return {
    internal_fill_rate: internalFill,
    retailer_otif: retailerOtif,
    gap_pts: gapPts,
    ontime_gap_pts: ontimeGapPts,
    infull_gap_pts: infullGapPts,
    total_shipments: portfolioRows.length,
    walmart_shipments: wmTotal,
    window_start: range.start,
    window_end: range.end,
  }
}

export function computeRootCauses(
  wmRows: AuditRow[],
  summary: Summary,
): RootCause[] {
  const { gap_pts: gapPts, ontime_gap_pts: ontimeGap, infull_gap_pts: infullGap } = summary

  const counts: Record<string, number> = {}
  for (const r of wmRows) {
    if (r.on_time_root_cause) counts[r.on_time_root_cause] = (counts[r.on_time_root_cause] || 0) + 1
    if (r.in_full_root_cause) counts[r.in_full_root_cause] = (counts[r.in_full_root_cause] || 0) + 1
  }

  const totalOntimeFails = (counts['warehouse_late'] || 0) + (counts['carrier_late'] || 0)
  const totalInfullFails = (counts['short_ship'] || 0) + (counts['receiving_discrepancy'] || 0)

  function causeGap(cause: string, mode: 'on_time' | 'in_full'): number {
    const totalModeFails = mode === 'on_time' ? totalOntimeFails : totalInfullFails
    const modeGap = mode === 'on_time' ? ontimeGap : infullGap
    if (totalModeFails === 0) return 0
    return round2((counts[cause] || 0) / totalModeFails * modeGap)
  }

  const definitions: Array<{ cause: string; mode: 'on_time' | 'in_full'; label: string }> = [
    { cause: 'warehouse_late', mode: 'on_time', label: 'Warehouse late' },
    { cause: 'carrier_late', mode: 'on_time', label: 'Carrier late' },
    { cause: 'short_ship', mode: 'in_full', label: 'Short-ship' },
    { cause: 'receiving_discrepancy', mode: 'in_full', label: 'Receiving discrepancy' },
  ]

  return definitions
    .map(d => {
      const gp = causeGap(d.cause, d.mode)
      return {
        cause: d.cause,
        label: d.label,
        failure_mode: d.mode,
        gap_pts: gp,
        shipment_count: counts[d.cause] || 0,
        pct_of_gap: gapPts > 0 ? round4(gp / gapPts) : 0,
      }
    })
    .sort((a, b) => b.gap_pts - a.gap_pts)
}

export function computeTrueFill(wmRows: AuditRow[]): TrueFill {
  const totalOrdered = wmRows.reduce((s, r) => s + r.po_units, 0)
  const totalShipped = wmRows.reduce((s, r) => s + r.acknowledged_units, 0)
  const totalReceived = wmRows.reduce((s, r) => s + r.shipped_units, 0)

  const brandFill = totalOrdered > 0 ? round4(totalShipped / totalOrdered) : 0
  const retailerFill = totalOrdered > 0 ? round4(totalReceived / totalOrdered) : 0
  const receivingGapPts = round2((brandFill - retailerFill) * 100)

  const withDiscrepancy = wmRows.filter(r => r.shipped_units < r.acknowledged_units).length

  return {
    fill_vs_855: brandFill,
    fill_vs_850: retailerFill,
    trimming_gap_pts: receivingGapPts,
    orders_with_trimming: withDiscrepancy,
    pct_orders_trimmed: wmRows.length > 0 ? round4(withDiscrepancy / wmRows.length) : 0,
  }
}

export function computeExposure(
  wmRows: AuditRow[],
  chargebacks: ChargebackRow[],
  range: WindowRange,
): Exposure {
  const wmCbs = chargebacks.filter(cb => cb.retailer === 'Walmart')
  const totalFines = wmCbs.reduce((s, cb) => s + cb.amount, 0)

  const totalVelocity = wmRows.reduce((s, r) => {
    return s + Math.max(0, r.po_units - r.shipped_units) * VELOCITY_DAMAGE_PER_UNIT
  }, 0)

  const [sy, sm] = range.start.split('-').map(Number)
  const [ey, em] = range.end.split('-').map(Number)
  const windowMonths = (ey - sy) * 12 + em - sm + 1
  const scale = windowMonths > 0 ? 12 / windowMonths : 1

  const annualFines = round2(totalFines * scale)
  const annualVelocity = round2(totalVelocity * scale)

  const byQuarter: Record<string, number> = {}
  for (const cb of wmCbs) {
    if (cb.month && cb.month.length >= 7) {
      const year = parseInt(cb.month.slice(0, 4))
      const month = parseInt(cb.month.slice(5, 7))
      const q = Math.ceil(month / 3)
      byQuarter[`${year}-Q${q}`] = (byQuarter[`${year}-Q${q}`] || 0) + cb.amount
    }
  }

  const finesByQuarter = Object.entries(byQuarter)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([quarter, fines]) => ({ quarter, fines: round2(fines) }))

  const velocityBySku = wmRows
    .map(r => ({
      order_id: r.po_number,
      velocity_damage: round2(Math.max(0, r.po_units - r.shipped_units) * VELOCITY_DAMAGE_PER_UNIT),
    }))
    .filter(v => v.velocity_damage > 0)
    .sort((a, b) => b.velocity_damage - a.velocity_damage)
    .slice(0, 10)

  return {
    annual_fines: annualFines,
    fines_source: 'platform',
    annual_velocity_damage: annualVelocity,
    velocity_source: 'modeled',
    total_exposure: round2(annualFines + annualVelocity),
    fines_by_quarter: finesByQuarter,
    velocity_by_sku: velocityBySku,
  }
}
