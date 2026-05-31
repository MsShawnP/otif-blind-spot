// Static JSON imports — baked in at Vite build time, no fetch/loading states needed.
// Requires verbatimModuleSyntax; use `as unknown as T` for strict-mode JSON casts.
import type { Summary, RootCause, TrueFill, Exposure, AuditRow } from './types'

import rawSummary from './data/summary.json'
import rawRootCauses from './data/root_causes.json'
import rawTrueFill from './data/true_fill.json'
import rawExposure from './data/exposure.json'
import rawAuditRows from './data/audit_rows.json'

export const summary = rawSummary as unknown as Summary
export const rootCauses = rawRootCauses as unknown as RootCause[]
export const trueFill = rawTrueFill as unknown as TrueFill
export const exposure = rawExposure as unknown as Exposure
export const auditRows = rawAuditRows as unknown as AuditRow[]
