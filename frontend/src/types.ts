// Types matching the 5 JSON shapes produced by scripts/02_export_json.py

export interface Summary {
  internal_fill_rate: number
  retailer_otif: number
  gap_pts: number
  ontime_gap_pts: number
  infull_gap_pts: number
  total_shipments: number
  walmart_shipments: number
  window_start: string
  window_end: string
}

export interface RootCause {
  cause: string
  label: string
  failure_mode: 'on_time' | 'in_full'
  gap_pts: number
  shipment_count: number
  pct_of_gap: number
}

export interface TrueFill {
  fill_vs_855: number
  fill_vs_850: number
  trimming_gap_pts: number
  orders_with_trimming: number
  pct_orders_trimmed: number
}

export interface FinesByQuarter {
  quarter: string
  fines: number
}

export interface VelocityBySku {
  order_id: string
  velocity_damage: number
}

export interface Exposure {
  annual_fines: number
  annual_velocity_damage: number
  total_exposure: number
  fines_by_quarter: FinesByQuarter[]
  velocity_by_sku: VelocityBySku[]
}

export interface AuditRow {
  shipment_id: string
  po_number: string
  ship_date: string | null
  mabd: string | null
  delivery_date: string | null
  on_time_result: boolean
  on_time_root_cause: string | null
  po_units: number
  acknowledged_units: number
  shipped_units: number
  in_full_result: boolean
  in_full_root_cause: string | null
  otif_fine: number
  retailer_penalty_flag: boolean
}
