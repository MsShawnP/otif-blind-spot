/** Format a dollar amount: $1.2M / $300K / $1,234 */
export function formatDollars(n: number): string {
  if (Math.abs(n) >= 1_000_000) {
    return `$${(n / 1_000_000).toFixed(1)}M`
  }
  if (Math.abs(n) >= 1_000) {
    return `$${Math.round(n / 1_000)}K`
  }
  return `$${Math.round(n).toLocaleString()}`
}

/** Format a ratio as a percentage: 0.95 → "95%" or "95.0%" with digits=1 */
export function formatPercent(n: number, digits = 0): string {
  return `${(n * 100).toFixed(digits)}%`
}

/** Format a gap in percentage points: 5 → "5.0 pts" */
export function formatPts(n: number): string {
  return `${n.toFixed(1)} pts`
}
