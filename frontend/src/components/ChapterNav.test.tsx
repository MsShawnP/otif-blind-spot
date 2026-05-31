import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChapterNav } from './ChapterNav'

describe('ChapterNav', () => {
  it('renders two tabs', () => {
    render(<ChapterNav activeChapter={1} onChapterChange={vi.fn()} />)
    expect(screen.getByText('Reconciliation Matrix')).toBeInTheDocument()
    expect(screen.getByText('EDI Audit Sheet')).toBeInTheDocument()
  })

  it('marks the active chapter with aria-current', () => {
    render(<ChapterNav activeChapter={2} onChapterChange={vi.fn()} />)
    const auditBtn = screen.getByText('EDI Audit Sheet').closest('button')
    expect(auditBtn?.getAttribute('aria-current')).toBe('true')
  })

  it('calls onChapterChange with the correct id when a tab is clicked', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<ChapterNav activeChapter={1} onChapterChange={onChange} />)

    await user.click(screen.getByText('EDI Audit Sheet'))
    expect(onChange).toHaveBeenCalledWith(2)
  })

  it('applies --active class to the selected tab', () => {
    render(<ChapterNav activeChapter={1} onChapterChange={vi.fn()} />)
    const reconcBtn = screen.getByText('Reconciliation Matrix').closest('button')
    expect(reconcBtn?.className).toContain('chapter-nav__btn--active')
  })
})
