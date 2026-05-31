import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('OTIF Blind Spot')).toBeInTheDocument()
  })

  it('shows headline numbers above the chapter nav', () => {
    render(<App />)
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('86%')).toBeInTheDocument()
  })

  it('renders two navigation tabs', () => {
    render(<App />)
    expect(screen.getByText('Reconciliation Matrix')).toBeInTheDocument()
    expect(screen.getByText('EDI Audit Sheet')).toBeInTheDocument()
  })

  it('shows ReconciliationView on initial load', () => {
    const { container } = render(<App />)
    expect(container.querySelector('[data-view="reconciliation"]')).toBeTruthy()
    expect(container.querySelector('[data-view="audit-sheet"]')).toBeNull()
  })

  it('switches to AuditSheetView when tab 2 is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(<App />)

    await user.click(screen.getByText('EDI Audit Sheet'))

    expect(container.querySelector('[data-view="audit-sheet"]')).toBeTruthy()
    expect(container.querySelector('[data-view="reconciliation"]')).toBeNull()
  })

  it('returns to ReconciliationView when tab 1 is clicked', async () => {
    const user = userEvent.setup()
    const { container } = render(<App />)

    await user.click(screen.getByText('EDI Audit Sheet'))
    await user.click(screen.getByText('Reconciliation Matrix'))

    expect(container.querySelector('[data-view="reconciliation"]')).toBeTruthy()
  })
})
