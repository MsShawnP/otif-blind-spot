import { useState } from 'react'
import { summary, rootCauses, trueFill, exposure, auditRows } from './data'
import { ChapterNav } from './components/ChapterNav'
import { ReconciliationView } from './chapters/ReconciliationView/ReconciliationView'
import { AuditSheetView } from './chapters/AuditSheetView/AuditSheetView'
import { formatPercent, formatPts } from './utils/format'
import './App.css'

function HeadlineHook() {
  const gapPts = summary.gap_pts ?? 9
  const internalFill = summary.internal_fill_rate ?? 0.95
  const retailerOtif = summary.retailer_otif ?? 0.86

  return (
    <section className="headline-hook" aria-labelledby="headline-title">
      <div className="headline-hook__inner">
        <div className="headline-hook__numbers">
          <div className="headline-hook__number-block">
            <span className="headline-hook__pct">{formatPercent(internalFill)}</span>
            <span className="headline-hook__label">
              Cinderhaven internal fill rate<br />
              <span className="headline-hook__sublabel">measured at the shipping dock</span>
            </span>
          </div>

          <div className="headline-hook__divider" aria-hidden="true">≠</div>

          <div className="headline-hook__number-block">
            <span className="headline-hook__pct headline-hook__pct--low">{formatPercent(retailerOtif)}</span>
            <span className="headline-hook__label">
              Walmart's OTIF score<br />
              <span className="headline-hook__sublabel">measured at their receiving dock</span>
            </span>
          </div>
        </div>

        <p className="headline-hook__gap" id="headline-title">
          {formatPts(gapPts)} gap. Same shipments. Different docks. Different baselines.
        </p>
      </div>
    </section>
  )
}

function App() {
  const [chapter, setChapter] = useState<1 | 2>(1)

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand-name">OTIF Blind Spot</span>
        <span className="brand-subtitle">Cinderhaven</span>
      </header>

      <HeadlineHook />

      <ChapterNav activeChapter={chapter} onChapterChange={setChapter} />

      <main className="app-main">
        {chapter === 1 && (
          <ReconciliationView
            summary={summary}
            rootCauses={rootCauses}
            trueFill={trueFill}
            exposure={exposure}
          />
        )}
        {chapter === 2 && (
          <AuditSheetView rows={auditRows} />
        )}
      </main>
    </div>
  )
}

export default App
