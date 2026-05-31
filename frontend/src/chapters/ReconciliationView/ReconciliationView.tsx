import { useState, useCallback, useEffect, useRef } from 'react'
import * as Plot from '@observablehq/plot'
import type { Summary, RootCause, TrueFill, Exposure } from '../../types'
import { PlotChart } from '../../components/PlotChart'
import { formatPercent, formatPts, formatDollars } from '../../utils/format'
import {
  deriveDecompositionBars,
  deriveRootCauseBars,
  deriveTrueFillComparison,
  ROOT_CAUSE_COLORS,
} from './domain'
import './ReconciliationView.css'

interface ReconciliationViewProps {
  summary: Summary
  rootCauses: RootCause[]
  trueFill: TrueFill
  exposure: Exposure
}

// ─── Move 1: Dual-dock comparison ────────────────────────────────────────────

function DualDockChart({ summary }: { summary: Summary }) {
  const data = [
    { label: 'Cinderhaven internal fill', value: summary.internal_fill_rate, color: '#158f75' },
    { label: "Walmart's OTIF score",      value: summary.retailer_otif,       color: '#cc100a' },
  ]

  const renderChart = useCallback(
    (container: HTMLDivElement) => {
      const width = Math.max(container.clientWidth || 560, 300)
      return Plot.plot({
        marks: [
          Plot.barX(data, {
            x: 'value',
            y: 'label',
            fill: (d) => d.color,
          }),
          Plot.text(data, {
            x: 'value',
            y: 'label',
            text: (d) => formatPercent(d.value, 0),
            dx: 8,
            textAnchor: 'start',
            fill: '#333333',
            fontWeight: '600',
            fontSize: 13,
          }),
          Plot.ruleX([0]),
        ],
        x: {
          domain: [0, 1.05],
          axis: null,
          label: null,
        },
        y: { label: null },
        marginLeft: 200,
        marginRight: 60,
        width,
        height: 90,
        style: {
          background: 'transparent',
          fontFamily: "'Source Sans 3', sans-serif",
          fontSize: '12px',
          overflow: 'visible',
        },
      })
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [summary.internal_fill_rate, summary.retailer_otif],
  )

  return (
    <PlotChart
      render={renderChart}
      className="recon-chart"
      ariaLabel={`Dual-dock comparison: ${formatPercent(summary.internal_fill_rate)} internal vs ${formatPercent(summary.retailer_otif)} OTIF`}
    />
  )
}

// ─── Move 2: On-time / in-full decomposition ─────────────────────────────────

function DecompositionChart({ summary }: { summary: Summary }) {
  const bars = deriveDecompositionBars(summary)
  const total = summary.gap_pts || 9

  return (
    <div className="decomp-bar-wrap" data-decomp-total={total}>
      {bars.map((bar) => (
        <div key={bar.failure_mode} className={`decomp-segment decomp-segment--${bar.failure_mode}`}>
          <div
            className="decomp-segment__fill"
            style={{ width: `${bar.pct * 100}%` }}
            aria-label={`${bar.label}: ${formatPts(bar.pts)}`}
          />
          <span className="decomp-segment__label">
            <strong>{formatPts(bar.pts)}</strong> {bar.label}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── Move 3: Root cause attribution with click-to-pin ────────────────────────

function RootCauseSection({ rootCauses }: { rootCauses: RootCause[] }) {
  const [pinnedId, setPinnedId] = useState<string | null>(null)
  const sectionRef = useRef<HTMLDivElement>(null)

  const bars = deriveRootCauseBars(rootCauses)
  const maxPts = Math.max(...bars.map((b) => b.gap_pts), 1)
  const barById = Object.fromEntries(bars.map((b) => [b.cause, b]))
  const pinned = pinnedId ? barById[pinnedId] : null

  // Dismiss pin on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (sectionRef.current && !sectionRef.current.contains(e.target as Node)) {
        setPinnedId(null)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const implications: Record<string, string> = {
    warehouse_late:        'ASN was filed late — fix warehouse release process.',
    carrier_late:          'Carrier missed delivery window — audit carrier SLAs.',
    production_short_ship: 'Production couldn\'t fill the order — improve forecast.',
    order_trimming:        'Walmart trimmed the 855 — demand signal was over-ordered.',
  }

  return (
    <div ref={sectionRef} className="root-cause-section">
      {pinned && (
        <div className="pin-card" role="status" aria-live="polite">
          <div className="pin-card__header">
            <span className="pin-card__cause">{pinned.label}</span>
            <button
              className="pin-card__close"
              onClick={() => setPinnedId(null)}
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
          <p className="pin-card__pts">{formatPts(pinned.gap_pts)} of {formatPts(bars.reduce((s, b) => s + b.gap_pts, 0))} gap</p>
          <p className="pin-card__implication">{implications[pinned.cause]}</p>
        </div>
      )}

      <div className="root-cause-bars">
        {bars.map((bar) => {
          const isDimmed = pinnedId !== null && pinnedId !== bar.cause
          return (
            <button
              key={bar.cause}
              className="root-cause-bar-row"
              onClick={() => setPinnedId((prev) => (prev === bar.cause ? null : bar.cause))}
              aria-pressed={pinnedId === bar.cause}
            >
              <span className="root-cause-bar-label">{bar.label}</span>
              <div className="root-cause-bar-track">
                <div
                  className="root-cause-bar-fill"
                  style={{
                    width: `${(bar.gap_pts / maxPts) * 100}%`,
                    background: ROOT_CAUSE_COLORS[bar.cause],
                    opacity: isDimmed ? 0.2 : 1,
                  }}
                />
              </div>
              <span className="root-cause-bar-value">{formatPts(bar.gap_pts)}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// ─── Move 4: True fill reveal ─────────────────────────────────────────────────

function TrueFillSection({ trueFill }: { trueFill: TrueFill }) {
  const comp = deriveTrueFillComparison(trueFill)

  return (
    <div className="kpi-row">
      <div className="kpi-tile">
        <span className="kpi-tile__value">{formatPercent(comp.fill_855_value, 0)}</span>
        <span className="kpi-tile__label">{comp.fill_855_label}</span>
      </div>
      <div className="kpi-tile kpi-tile--accent">
        <span className="kpi-tile__value">{formatPercent(comp.fill_850_value, 0)}</span>
        <span className="kpi-tile__label">{comp.fill_850_label}</span>
      </div>
      <div className="kpi-tile kpi-tile--delta">
        <span className="kpi-tile__value">{formatPts(comp.delta_value)}</span>
        <span className="kpi-tile__label">
          added by <strong>order trimming</strong> before acknowledgment
        </span>
      </div>
    </div>
  )
}

// ─── Move 5: Exposure quantification ─────────────────────────────────────────

function ExposureSection({ exposure }: { exposure: Exposure }) {
  return (
    <div className="kpi-row">
      <div className="kpi-tile">
        <span className="kpi-tile__value">{formatDollars(exposure.annual_fines)}</span>
        <span className="kpi-tile__label">annual OTIF fines (3% of COGS on penalized shipments)</span>
      </div>
      <div className="kpi-tile kpi-tile--velocity">
        <span className="kpi-tile__value kpi-tile__value--large">{formatDollars(exposure.annual_velocity_damage)}</span>
        <span className="kpi-tile__label">estimated velocity damage from empty shelves</span>
      </div>
      <div className="kpi-tile kpi-tile--total">
        <span className="kpi-tile__value">{formatDollars(exposure.total_exposure)}</span>
        <span className="kpi-tile__label">total annual exposure</span>
      </div>
    </div>
  )
}

// ─── Main view ────────────────────────────────────────────────────────────────

export function ReconciliationView({ summary, rootCauses, trueFill, exposure }: ReconciliationViewProps) {
  return (
    <div className="reconciliation-view">

      {/* Move 1 */}
      <section className="recon-section" aria-labelledby="move1-title">
        <h2 className="recon-section__title" id="move1-title">Dual-Dock Reconciliation</h2>
        <p className="recon-section__framing">
          Cinderhaven measures fill rate at the shipping dock. Walmart measures OTIF at their receiving dock.
          The {formatPts(summary.gap_pts)} gap is real — but invisible to systems that only watch one dock.
        </p>
        <DualDockChart summary={summary} />
        <p className="recon-footnote">Source: Cinderhaven fct_retailer_shipments; synthetic Walmart OTIF scorecard. Window: {summary.window_start} – {summary.window_end}.</p>
      </section>

      {/* Move 2 */}
      <section className="recon-section" aria-labelledby="move2-title">
        <h2 className="recon-section__title" id="move2-title">Gap Decomposition</h2>
        <p className="recon-section__framing">
          The {formatPts(summary.gap_pts)} gap splits {formatPts(summary.ontime_gap_pts)} on-time failures and {formatPts(summary.infull_gap_pts)} in-full failures.
          Fixing the wrong one leaves at least {formatPts(Math.min(summary.ontime_gap_pts, summary.infull_gap_pts))} on the table.
        </p>
        <DecompositionChart summary={summary} />
      </section>

      {/* Move 3 */}
      <section className="recon-section" aria-labelledby="move3-title">
        <h2 className="recon-section__title" id="move3-title">Root Cause Attribution</h2>
        <p className="recon-section__framing">
          Four root causes, two failure modes. Click any bar to pin the detail.
        </p>
        <RootCauseSection rootCauses={rootCauses} />
      </section>

      {/* Move 4 */}
      <section className="recon-section" aria-labelledby="move4-title">
        <h2 className="recon-section__title" id="move4-title">True Fill Rate</h2>
        <p className="recon-section__framing">
          Walmart trims POs via EDI 855 acknowledgment before shipment. Cinderhaven fills against the acknowledged quantity —
          which makes fill rate look better than it is against original demand.
        </p>
        <TrueFillSection trueFill={trueFill} />
      </section>

      {/* Move 5 */}
      <section className="recon-section" aria-labelledby="move5-title">
        <h2 className="recon-section__title" id="move5-title">Financial Exposure</h2>
        <p className="recon-section__framing">
          The fine is visible. The velocity damage — revenue lost while shelves were empty — is larger and invisible.
        </p>
        <ExposureSection exposure={exposure} />
      </section>

    </div>
  )
}
