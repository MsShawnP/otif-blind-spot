import { useState, useMemo } from 'react'
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
  WINDOW_PRESETS,
  DEFAULT_PRESET_KEY,
  presetToRange,
  filterByShipDate,
  filterChargebacks,
  computeSummary,
  computeRootCauses,
  computeTrueFill,
  computeExposure,
} from './computeMetrics'
import type { Summary } from './types'
import { ChapterNav } from './components/ChapterNav'
import { ReconciliationView } from './chapters/ReconciliationView/ReconciliationView'
import { AuditSheetView } from './chapters/AuditSheetView/AuditSheetView'
import { formatPercent, formatPts } from './utils/format'
import './App.css'

const CORPUS_START = fullSummary.window_start
const CORPUS_END = fullSummary.window_end

function HeadlineHook({ summary }: { summary: Summary }) {
  return (
    <section className="headline-hook" aria-labelledby="headline-title">
      <div className="headline-hook__inner">
        <div className="headline-hook__numbers">
          <div className="headline-hook__number-block">
            <span className="headline-hook__pct">{formatPercent(summary.internal_fill_rate)}</span>
            <span className="headline-hook__label">
              Cinderhaven internal fill rate<br />
              <span className="headline-hook__sublabel">all retailers, measured at the shipping dock</span>
            </span>
          </div>

          <div className="headline-hook__divider" aria-hidden="true">≠</div>

          <div className="headline-hook__number-block">
            <span className="headline-hook__pct headline-hook__pct--low">{formatPercent(summary.retailer_otif)}</span>
            <span className="headline-hook__label">
              Walmart's OTIF score<br />
              <span className="headline-hook__sublabel">measured at their receiving dock</span>
            </span>
          </div>
        </div>

        <p className="headline-hook__gap" id="headline-title">
          {formatPts(summary.gap_pts)} gap. Same shipments. Different docks. Different baselines.
        </p>
      </div>
    </section>
  )
}

function WindowPresetBar({ activeKey, onChange }: { activeKey: string; onChange: (key: string) => void }) {
  return (
    <div className="window-preset-bar" role="group" aria-label="Date range">
      {WINDOW_PRESETS.map((p) => (
        <button
          key={p.key}
          className={`window-preset-btn${activeKey === p.key ? ' window-preset-btn--active' : ''}`}
          onClick={() => onChange(p.key)}
          aria-pressed={activeKey === p.key}
        >
          {p.label}
        </button>
      ))}
    </div>
  )
}

function App() {
  const [chapter, setChapter] = useState<1 | 2>(1)
  const [presetKey, setPresetKey] = useState(DEFAULT_PRESET_KEY)

  const computed = useMemo(() => {
    const preset = WINDOW_PRESETS.find((p) => p.key === presetKey)!
    const range = presetToRange(preset, CORPUS_START, CORPUS_END)

    if (preset.key === 'all') {
      return {
        summary: fullSummary,
        rootCauses: fullRootCauses,
        trueFill: fullTrueFill,
        exposure: fullExposure,
        filteredAudit: auditRows,
      }
    }

    const filteredPortfolio = filterByShipDate(portfolioShipments, range)
    const filteredAudit = filterByShipDate(auditRows, range)
    const filteredChargebacks = filterChargebacks(chargebackRows, range)

    const summary = computeSummary(filteredAudit, filteredPortfolio, range)
    const rootCauses = computeRootCauses(filteredAudit, summary)
    const trueFill = computeTrueFill(filteredAudit)
    const exposure = computeExposure(filteredAudit, filteredChargebacks, range)

    return { summary, rootCauses, trueFill, exposure, filteredAudit }
  }, [presetKey])

  return (
    <div className="app-shell lailara-page">
      <header className="lailara-header">
        <nav className="lailara-nav-inner">
          <a href="https://lailarallc.com" className="lailara-wordmark" target="_blank" rel="noopener">
            Lailara LLC
          </a>
          <span className="lailara-tool-name">OTIF Blind Spot</span>
        </nav>
      </header>

      <header className="app-header">
        <span className="brand-name">OTIF Blind Spot</span>
        <span className="brand-subtitle">Cinderhaven</span>
      </header>

      <HeadlineHook summary={computed.summary} />

      <WindowPresetBar activeKey={presetKey} onChange={setPresetKey} />

      <ChapterNav activeChapter={chapter} onChapterChange={setChapter} />

      <main className="app-main lailara-main">
        {chapter === 1 && (
          <ReconciliationView
            summary={computed.summary}
            rootCauses={computed.rootCauses}
            trueFill={computed.trueFill}
            exposure={computed.exposure}
            exposureScope={presetKey === 'all'
              ? 'Annualized from full observation period (Jan 2023 – Dec 2025).'
              : `Annualized from last ${WINDOW_PRESETS.find(p => p.key === presetKey)!.weeks} weeks.`}
          />
        )}
        {chapter === 2 && (
          <AuditSheetView rows={computed.filteredAudit} />
        )}
      </main>

      <footer className="lailara-footer">
        <div className="lailara-footer-inner">
          <p>Built by <a href="https://lailarallc.com" target="_blank" rel="noopener">Lailara LLC</a></p>
          <p className="lailara-footer-note">Data: Cinderhaven Provisions synthetic dataset.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
