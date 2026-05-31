import { describe, it, expect } from 'vitest'
import { formatDollars, formatPercent, formatPts } from './format'

describe('formatDollars', () => {
  it('formats thousands as K', () => {
    expect(formatDollars(140_000)).toBe('$140K')
    expect(formatDollars(300_000)).toBe('$300K')
    expect(formatDollars(460_000)).toBe('$460K')
  })

  it('formats millions as M', () => {
    expect(formatDollars(1_200_000)).toBe('$1.2M')
    expect(formatDollars(2_500_000)).toBe('$2.5M')
  })

  it('formats small values as dollars', () => {
    expect(formatDollars(999)).toBe('$999')
    expect(formatDollars(0)).toBe('$0')
  })
})

describe('formatPercent', () => {
  it('formats ratio as percent with 0 decimal places by default', () => {
    expect(formatPercent(0.95)).toBe('95%')
    expect(formatPercent(0.86)).toBe('86%')
  })

  it('formats ratio with specified decimal places', () => {
    expect(formatPercent(0.864, 1)).toBe('86.4%')
    expect(formatPercent(0.95, 1)).toBe('95.0%')
  })
})

describe('formatPts', () => {
  it('formats integer gap as one decimal', () => {
    expect(formatPts(5)).toBe('5.0 pts')
    expect(formatPts(4)).toBe('4.0 pts')
    expect(formatPts(9)).toBe('9.0 pts')
  })

  it('formats decimal gap', () => {
    expect(formatPts(3.5)).toBe('3.5 pts')
    expect(formatPts(1.5)).toBe('1.5 pts')
  })
})
