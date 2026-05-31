import type { Summary, RootCause, TrueFill, Exposure } from '../../types'

interface ReconciliationViewProps {
  summary: Summary
  rootCauses: RootCause[]
  trueFill: TrueFill
  exposure: Exposure
}

export function ReconciliationView(_props: ReconciliationViewProps) {
  return <div data-view="reconciliation" />
}
