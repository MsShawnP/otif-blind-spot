import type { AuditRow } from '../../types'

interface AuditSheetViewProps {
  rows: AuditRow[]
}

export function AuditSheetView(_props: AuditSheetViewProps) {
  return <div data-view="audit-sheet" />
}
