import { useRef, useEffect } from 'react'

interface PlotChartProps {
  /**
   * A function that receives the container div and returns an Observable Plot
   * SVGElement or HTMLElement. Called on every render — Plot destroy/rebuild
   * is the documented integration pattern (Plot returns DOM elements, not React elements).
   */
  render: (container: HTMLDivElement) => SVGElement | HTMLElement | null
  className?: string
  /** Accessible label shown to screen readers via aria-label */
  ariaLabel?: string
  /**
   * Optional title text injected as a <title> element inside the SVG.
   * When provided, also sets aria-labelledby on the SVG pointing to that element.
   * More semantic than aria-label alone; preferred for chart SVGs.
   */
  svgTitle?: string
}

/**
 * React wrapper for Observable Plot charts.
 *
 * Mounts the Plot SVG output into a container div via useRef + useEffect.
 * Destroys and rebuilds the chart whenever `render` or its closure dependencies change.
 * Callers control re-render frequency by memoizing the render function or its deps.
 *
 * Usage:
 *   <PlotChart
 *     render={(container) => Plot.plot({ marks: [...] })}
 *     ariaLabel="Contribution per unit by channel"
 *   />
 */
export function PlotChart({ render, className, ariaLabel, svgTitle }: PlotChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Clear any previous Plot output
    container.innerHTML = ''

    const chart = render(container)
    if (chart) {
      // Add accessibility attributes to the SVG
      if (chart instanceof SVGElement) {
        chart.setAttribute('role', 'img')
        if (ariaLabel) {
          chart.setAttribute('aria-label', ariaLabel)
        }
        // Inject <title> element for richer screen-reader support
        if (svgTitle) {
          const titleId = `chart-title-${Math.random().toString(36).slice(2)}`
          const titleEl = document.createElementNS('http://www.w3.org/2000/svg', 'title')
          titleEl.id = titleId
          titleEl.textContent = svgTitle
          chart.insertBefore(titleEl, chart.firstChild)
          chart.setAttribute('aria-labelledby', titleId)
        }
      }
      container.appendChild(chart)
    }

    return () => {
      if (container) {
        container.innerHTML = ''
      }
    }
  }) // No dep array — re-runs on every render; callers control frequency via memo

  return (
    <div
      ref={containerRef}
      className={className}
      data-chart-container="true"
    />
  )
}
