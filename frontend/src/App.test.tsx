import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('OTIF Blind Spot')).toBeInTheDocument()
  })

  it('renders the Cinderhaven subtitle', () => {
    render(<App />)
    expect(screen.getByText('Cinderhaven')).toBeInTheDocument()
  })
})
