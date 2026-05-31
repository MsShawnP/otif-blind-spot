import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ReconciliationView } from './ReconciliationView'
import type { Summary, RootCause, TrueFill, Exposure } from '../../types'

const summary: Summary = {
  internal_fill_rate: 0.95, retailer_otif: 0.86, gap_pts: 9.0,
  ontime_gap_pts: 5.0, infull_gap_pts: 4.0,
  total_shipments: 100, walmart_shipments: 100,
  window_start: '2024-01-01', window_end: '2026-03-31',
}

const rootCauses: RootCause[] = [
  { cause: 'warehouse_late',        label: 'Warehouse late',        failure_mode: 'on_time', gap_pts: 3.0, shipment_count: 20, pct_of_gap: 0.333 },
  { cause: 'carrier_late',          label: 'Carrier late',          failure_mode: 'on_time', gap_pts: 2.0, shipment_count: 15, pct_of_gap: 0.222 },
  { cause: 'production_short_ship', label: 'Production short-ship', failure_mode: 'in_full', gap_pts: 2.5, shipment_count: 18, pct_of_gap: 0.278 },
  { cause: 'order_trimming',        label: 'Order trimming',        failure_mode: 'in_full', gap_pts: 1.5, shipment_count: 10, pct_of_gap: 0.167 },
]

const trueFill: TrueFill = {
  fill_vs_855: 0.95, fill_vs_850: 0.91,
  trimming_gap_pts: 4.0, orders_with_trimming: 35, pct_orders_trimmed: 0.35,
}

const exposure: Exposure = {
  annual_fines: 140000, annual_velocity_damage: 320000, total_exposure: 460000,
  fines_by_quarter: [], velocity_by_sku: [],
}

function renderView() {
  return render(
    <ReconciliationView
      summary={summary}
      rootCauses={rootCauses}
      trueFill={trueFill}
      exposure={exposure}
    />
  )
}

// AE2 — decomposition
describe('Move 2: gap decomposition', () => {
  it('renders two labeled segments within the decomp bar', () => {
    const { container } = renderView()
    const decomp = container.querySelector('.decomp-bar-wrap')
    expect(decomp).toBeTruthy()
    // Two segments exist
    const segments = decomp!.querySelectorAll('.decomp-segment')
    expect(segments.length).toBe(2)
  })
})

// AE2 — click-to-pin
describe('Move 3: root cause click-to-pin', () => {
  it('shows all 4 root cause bars', () => {
    renderView()
    expect(screen.getByText('Warehouse late')).toBeInTheDocument()
    expect(screen.getByText('Carrier late')).toBeInTheDocument()
    expect(screen.getByText('Production short-ship')).toBeInTheDocument()
    expect(screen.getByText('Order trimming')).toBeInTheDocument()
  })

  it('shows pin card when a bar is clicked', async () => {
    const user = userEvent.setup()
    renderView()
    await user.click(screen.getByRole('button', { name: /warehouse late/i }))
    const card = screen.getByRole('status')
    expect(card).toBeInTheDocument()
    // Pin card shows the pts for the pinned bar
    expect(within(card).getByText(/3\.0 pts/)).toBeInTheDocument()
  })

  it('non-pinned bars have opacity 0.2 when a bar is pinned', async () => {
    const user = userEvent.setup()
    const { container } = renderView()
    await user.click(screen.getByRole('button', { name: /warehouse late/i }))

    const fills = container.querySelectorAll('.root-cause-bar-fill')
    const dimmed = Array.from(fills).filter(
      (el) => (el as HTMLElement).style.opacity === '0.2'
    )
    // 3 bars should be dimmed (all except the pinned one)
    expect(dimmed.length).toBe(3)
  })

  it('clicking the same bar again clears the pin', async () => {
    const user = userEvent.setup()
    renderView()
    await user.click(screen.getByRole('button', { name: /warehouse late/i }))
    await user.click(screen.getByRole('button', { name: /warehouse late/i }))
    expect(screen.queryByRole('status')).toBeNull()
  })
})

// AE3 — true fill
describe('Move 4: true fill reveal', () => {
  it('shows both fill rate values', () => {
    renderView()
    // fill_vs_855 = 95%, fill_vs_850 = 91%
    expect(screen.getAllByText('95%').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('91%')).toBeInTheDocument()
  })

  it('delta is labeled with order trimming', () => {
    renderView()
    expect(screen.getByText(/order trimming/)).toBeInTheDocument()
  })
})

// AE4 — exposure
describe('Move 5: exposure quantification', () => {
  it('shows $140K fines', () => {
    renderView()
    expect(screen.getByText('$140K')).toBeInTheDocument()
  })

  it('shows $320K velocity damage', () => {
    renderView()
    expect(screen.getByText('$320K')).toBeInTheDocument()
  })

  it('velocity damage tile has prominent styling', () => {
    const { container } = renderView()
    const velocityTile = container.querySelector('.kpi-tile--velocity')
    expect(velocityTile).toBeTruthy()
  })
})
