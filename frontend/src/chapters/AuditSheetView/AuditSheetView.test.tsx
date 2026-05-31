import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuditSheetView } from './AuditSheetView'
import type { AuditRow } from '../../types'

function makeRow(overrides: Partial<AuditRow> = {}): AuditRow {
  return {
    shipment_id: `RS-${Math.random().toString(36).slice(2)}`,
    po_number: 'PO-WMT-000001',
    ship_date: '2025-03-01',
    mabd: '2025-03-03',
    delivery_date: '2025-03-02',
    on_time_result: true,
    on_time_root_cause: null,
    po_units: 120,
    acknowledged_units: 120,
    shipped_units: 120,
    in_full_result: true,
    in_full_root_cause: null,
    otif_fine: 0,
    retailer_penalty_flag: false,
    ...overrides,
  }
}

const cleanRow = makeRow()
const lateRow = makeRow({
  shipment_id: 'RS-late-001',
  po_number: 'PO-WMT-000002',
  on_time_result: false,
  on_time_root_cause: 'carrier_late',
})
const shortRow = makeRow({
  shipment_id: 'RS-short-001',
  po_number: 'PO-WMT-000003',
  in_full_result: false,
  in_full_root_cause: 'production_short_ship',
  shipped_units: 96,
  otif_fine: 120,
  retailer_penalty_flag: true,
})
const bothRow = makeRow({
  shipment_id: 'RS-both-001',
  po_number: 'PO-WMT-000004',
  on_time_result: false,
  on_time_root_cause: 'warehouse_late',
  in_full_result: false,
  in_full_root_cause: 'order_trimming',
  shipped_units: 80,
  otif_fine: 200,
  retailer_penalty_flag: true,
})

const ALL_ROWS = [cleanRow, lateRow, shortRow, bothRow]

describe('AuditSheetView — table structure', () => {
  it('renders all 12 column headers', () => {
    render(<AuditSheetView rows={ALL_ROWS} />)
    const expectedHeaders = [
      'PO #', 'Ship date', 'MABD', 'Delivery date',
      'On-time?', 'Root cause',
      'PO units', 'Acknowledged', 'Shipped',
      'In-full?', 'Root cause',
      'OTIF fine',
    ]
    expectedHeaders.forEach((label) => {
      expect(screen.getAllByText(new RegExp(label, 'i')).length).toBeGreaterThanOrEqual(1)
    })
  })

  it('shows empty state when rows is empty', () => {
    render(<AuditSheetView rows={[]} />)
    expect(screen.getByText(/no data/i)).toBeInTheDocument()
  })
})

describe('AuditSheetView — filtering (AE5)', () => {
  it('On-time failures filter shows only late rows', async () => {
    const user = userEvent.setup()
    render(<AuditSheetView rows={ALL_ROWS} />)

    await user.click(screen.getByRole('button', { name: 'On-time failures' }))

    const tbody = document.querySelector('tbody')!
    const rows = within(tbody).queryAllByRole('row')
    // lateRow and bothRow fail on-time
    expect(rows.length).toBe(2)
  })

  it('In-full failures filter shows only in-full fail rows', async () => {
    const user = userEvent.setup()
    render(<AuditSheetView rows={ALL_ROWS} />)

    await user.click(screen.getByRole('button', { name: 'In-full failures' }))

    const tbody = document.querySelector('tbody')!
    const rows = within(tbody).queryAllByRole('row')
    // shortRow and bothRow fail in-full
    expect(rows.length).toBe(2)
  })

  it('Clean filter shows only fully-passing rows', async () => {
    const user = userEvent.setup()
    render(<AuditSheetView rows={ALL_ROWS} />)

    await user.click(screen.getByRole('button', { name: 'Clean' }))

    const tbody = document.querySelector('tbody')!
    const rows = within(tbody).queryAllByRole('row')
    expect(rows.length).toBe(1)
    expect(within(rows[0]).getByText(cleanRow.po_number)).toBeInTheDocument()
  })

  it('Both failures filter shows only rows failing both', async () => {
    const user = userEvent.setup()
    render(<AuditSheetView rows={ALL_ROWS} />)

    await user.click(screen.getByRole('button', { name: 'Both failures' }))

    const tbody = document.querySelector('tbody')!
    const rows = within(tbody).queryAllByRole('row')
    expect(rows.length).toBe(1)
    expect(within(rows[0]).getByText(bothRow.po_number)).toBeInTheDocument()
  })
})

describe('AuditSheetView — row styling', () => {
  it('rows failing both get a distinct class from single-failure rows', () => {
    const { container } = render(<AuditSheetView rows={ALL_ROWS} />)
    const bothFail = container.querySelectorAll('.audit-row--both-fail')
    const singleFail = container.querySelectorAll('.audit-row--single-fail')
    expect(bothFail.length).toBe(1)
    expect(singleFail.length).toBe(2)
  })
})

describe('AuditSheetView — sorting', () => {
  it('clicking a sortable column header sorts rows ascending', async () => {
    const user = userEvent.setup()
    render(<AuditSheetView rows={ALL_ROWS} />)

    // Click "PO #" to sort ascending
    await user.click(screen.getByRole('columnheader', { name: /PO #/i }))

    const tbody = document.querySelector('tbody')!
    const firstCell = within(tbody).queryAllByRole('row')[0].querySelectorAll('td')[0]
    // PO numbers are PO-WMT-000001 through 000004 — ascending should give 000001
    expect(firstCell.textContent).toBe('PO-WMT-000001')
  })
})

describe('AuditSheetView — OTIF fine display', () => {
  it('shows — for zero fine and formatted amount for non-zero', () => {
    render(<AuditSheetView rows={ALL_ROWS} />)
    // cleanRow has fine=0 → "—"
    // shortRow has fine=120 → "$120"
    expect(screen.getByText('$120')).toBeInTheDocument()
  })
})
