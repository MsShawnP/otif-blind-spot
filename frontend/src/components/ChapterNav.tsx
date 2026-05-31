import './ChapterNav.css'

interface Tab {
  id: 1 | 2
  label: string
}

const TABS: Tab[] = [
  { id: 1, label: 'Reconciliation Matrix' },
  { id: 2, label: 'EDI Audit Sheet' },
]

interface ChapterNavProps {
  activeChapter: 1 | 2
  onChapterChange: (chapter: 1 | 2) => void
}

export function ChapterNav({ activeChapter, onChapterChange }: ChapterNavProps) {
  return (
    <nav className="chapter-nav" aria-label="View navigation">
      <ol className="chapter-nav__list">
        {TABS.map((tab) => (
          <li key={tab.id} className="chapter-nav__item">
            <button
              className={`chapter-nav__btn${activeChapter === tab.id ? ' chapter-nav__btn--active' : ''}`}
              onClick={() => onChapterChange(tab.id)}
              aria-current={activeChapter === tab.id ? 'true' : undefined}
            >
              {tab.label}
            </button>
          </li>
        ))}
      </ol>
    </nav>
  )
}
