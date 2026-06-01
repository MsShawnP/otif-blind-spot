import { useState, useMemo } from 'react'
import type { AuditRow } from '../../types'
import { formatDollars } from '../../utils/format'
import './AuditSheetView.css'

type FilterMode = 'all' | 'on_time_fail' | 'in_full_fail' | 'both_fail' | 'clean'
type SortDir = 'asc' | 'desc'

interface AuditSheetViewProps {
  rows: AuditRow[]
}

const PAGE_SIZE = 50
const PAGINATION_THRESHOLD = 200

const FILTER_LABELS: Record<FilterMode, string> = {
  all:          'All',
  on_time_fail: 'On-time failures',
  in_full_fail: 'In-full failures',
  both_fail:    'Both failures',
  clean:        'Clean',
}

interface Column {
  key: keyof AuditRow
  label: string
  width: string
  sortable: boolean
  render: (row: AuditRow) => string | React.ReactNode
}

const COLUMNS: Column[] = [
  { key: 'po_number',           label: 'PO #',          width: '7%',  sortable: true,  render: (r) => r.po_number },
  { key: 'ship_date',           label: 'Ship date',      width: '8%',  sortable: true,  render: (r) => r.ship_date ?? '—' },
  { key: 'mabd',                label: 'MABD',           width: '7%',  sortable: true,  render: (r) => r.mabd ?? '—' },
  { key: 'delivery_date',       label: 'Delivery date',  width: '9%',  sortable: true,  render: (r) => r.delivery_date ?? '—' },
  { key: 'on_time_result',      label: 'On-time?',       width: '7%',  sortable: true,  render: (r) => <ResultChip pass={r.on_time_result} /> },
  { key: 'on_time_root_cause',  label: 'Root cause',     width: '13%', sortable: false, render: (r) => r.on_time_root_cause ?? '—' },
  { key: 'po_units',            label: 'PO units',       width: '7%',  sortable: true,  render: (r) => r.po_units.toLocaleString() },
  { key: 'acknowledged_units',  label: 'Acknowledged',   width: '8%',  sortable: true,  render: (r) => r.acknowledged_units.toLocaleString() },
  { key: 'shipped_units',       label: 'Shipped',        width: '7%',  sortable: true,  render: (r) => r.shipped_units.toLocaleString() },
  { key: 'in_full_result',      label: 'In-full?',       width: '7%',  sortable: true,  render: (r) => <ResultChip pass={r.in_full_result} /> },
  { key: 'in_full_root_cause',  label: 'Root cause',     width: '13%', sortable: false, render: (r) => r.in_full_root_cause ?? '—' },
  { key: 'otif_fine',           label: 'OTIF fine',      width: '7%',  sortable: true,  render: (r) => r.otif_fine > 0 ? formatDollars(r.otif_fine) : '—' },
]

function ResultChip({ pass }: { pass: boolean }) {
  return (
    <span className={`result-chip result-chip--${pass ? 'pass' : 'fail'}`}>
      {pass ? 'Yes' : 'No'}
    </span>
  )
}

function compareValues(a: AuditRow, b: AuditRow, key: keyof AuditRow, dir: SortDir): number {
  const av = a[key]
  const bv = b[key]
  const mul = dir === 'asc' ? 1 : -1

  if (av == null && bv == null) return 0
  if (av == null) return 1
  if (bv == null) return -1

  if (typeof av === 'boolean' && typeof bv === 'boolean') {
    return (av === bv ? 0 : av ? -1 : 1) * mul
  }
  if (typeof av === 'number' && typeof bv === 'number') {
    return (av - bv) * mul
  }
  return String(av).localeCompare(String(bv)) * mul
}

export function AuditSheetView({ rows }: AuditSheetViewProps) {
  const [filterMode, setFilterMode] = useState<FilterMode>('all')
  const [sortKey, setSortKey] = useState<keyof AuditRow | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [page, setPage] = useState(0)

  const filtered = useMemo(() => {
    switch (filterMode) {
      case 'on_time_fail': return rows.filter((r) => !r.on_time_result)
      case 'in_full_fail': return rows.filter((r) => !r.in_full_result)
      case 'both_fail':    return rows.filter((r) => !r.on_time_result && !r.in_full_result)
      case 'clean':        return rows.filter((r) => r.on_time_result && r.in_full_result)
      default:             return rows
    }
  }, [rows, filterMode])

  const sorted = useMemo(() => {
    if (!sortKey) return filtered
    return [...filtered].sort((a, b) => compareValues(a, b, sortKey, sortDir))
  }, [filtered, sortKey, sortDir])

  const paginated = rows.length > PAGINATION_THRESHOLD
    ? sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
    : sorted

  const totalPages = rows.length > PAGINATION_THRESHOLD
    ? Math.ceil(sorted.length / PAGE_SIZE)
    : 1

  function handleSort(key: keyof AuditRow) {
    if (sortKey === key) {
      if (sortDir === 'asc') {
        setSortDir('desc')
      } else {
        setSortKey(null)
        setSortDir('asc')
      }
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  function handleFilterChange(mode: FilterMode) {
    setFilterMode(mode)
    setSortKey(null)
    setSortDir('asc')
    setPage(0)
  }

  function rowClass(row: AuditRow): string {
    if (!row.on_time_result && !row.in_full_result) return 'audit-row audit-row--both-fail'
    if (!row.on_time_result || !row.in_full_result) return 'audit-row audit-row--single-fail'
    return 'audit-row'
  }

  return (
    <div className="audit-sheet-view" data-view="audit-sheet">
      <div className="audit-sheet-header">
        <h2 className="audit-sheet-title">EDI Audit Sheet</h2>
        <p className="audit-sheet-subtitle">
          {rows.length === 0
            ? 'Run the pipeline to populate audit rows.'
            : `${filtered.length.toLocaleString()} of ${rows.length.toLocaleString()} shipments`}
        </p>
      </div>

      <div className="audit-filter-bar" role="group" aria-label="Filter shipments">
        {(Object.keys(FILTER_LABELS) as FilterMode[]).map((mode) => (
          <button
            key={mode}
            className={`audit-filter-btn${filterMode === mode ? ' audit-filter-btn--active' : ''}`}
            onClick={() => handleFilterChange(mode)}
            aria-pressed={filterMode === mode}
          >
            {FILTER_LABELS[mode]}
          </button>
        ))}
      </div>

      <div className="audit-table-wrap">
        <table className="audit-table">
          <colgroup>
            {COLUMNS.map((col) => (
              <col key={col.key} style={{ width: col.width }} />
            ))}
          </colgroup>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className={`audit-th${col.sortable ? ' audit-th--sortable' : ''}${sortKey === col.key ? ' audit-th--sorted' : ''}`}
                  onClick={col.sortable ? () => handleSort(col.key) : undefined}
                  aria-sort={
                    sortKey === col.key
                      ? (sortDir === 'asc' ? 'ascending' : 'descending')
                      : undefined
                  }
                >
                  {col.label}
                  {col.sortable && (
                    <span className="sort-chevron" aria-hidden="true">
                      {sortKey === col.key ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ' ⬦'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginated.length === 0 ? (
              <tr>
                <td colSpan={COLUMNS.length} className="audit-empty">
                  {rows.length === 0 ? 'No data — run the pipeline first.' : 'No shipments match this filter.'}
                </td>
              </tr>
            ) : (
              paginated.map((row) => (
                <tr key={row.shipment_id} className={rowClass(row)}>
                  {COLUMNS.map((col) => (
                    <td key={col.key} className="audit-td">
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="audit-pagination">
          <button
            className="audit-page-btn"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            ← Prev
          </button>
          <span className="audit-page-info">
            Page {page + 1} of {totalPages}
          </span>
          <button
            className="audit-page-btn"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
