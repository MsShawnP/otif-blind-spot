---
title: Flex Min-Width Default Causes Table to Overflow Page Instead of Wrapper
date: 2026-05-31
category: docs/solutions/ui-bugs
module: otif-blind-spot
problem_type: ui_bug
component: frontend_stimulus
symptoms:
  - Page scrolls horizontally when viewing the EDI Audit Sheet
  - "overflow-x: auto on .audit-table-wrap does not create a scoped scrollbar"
  - 12-column table forces the entire page layout past the 900px max-width constraint
  - Table content bleeds past the viewport; wrapper appears to match table width exactly
root_cause: logic_error
resolution_type: code_fix
severity: medium
tags:
  - css-flexbox
  - scroll-behavior
  - layout-bug
  - table-layout
  - min-width
  - overflow-scoping
  - flex-item
  - responsive-design
---

# Flex Min-Width Default Causes Table to Overflow Page Instead of Wrapper

## Problem

A 12-column data table inside a flex container was forcing the entire page to scroll horizontally
instead of scrolling within its designated wrapper. The `overflow-x: auto` property on the table
wrapper had no visible effect — no scoped scrollbar appeared. Users had to scroll the whole page
to see all columns.

## Symptoms

- Horizontal scrollbar appears on the page when viewing the EDI Audit Sheet
- Table wrapper (`audit-table-wrap`) shows no internal scrollbar
- Content extends beyond the `900px` max-width boundary set on `.app-main`
- The symptom only surfaces in a live browser with real content; automated tests pass

## What Didn't Work

- **No fix was attempted during initial development.** The table was built in one pass, all tests
  passed, and the build succeeded — but the layout defect wasn't caught because vitest + Testing
  Library runs in jsdom, which does not compute CSS layout properties, scroll dimensions, or
  overflow behavior. The bug only surfaced after deployment in a real browser.

- **Considered but not used:** Reducing column count, `table-layout: fixed` with narrower cells,
  text truncation with ellipsis, compact font sizes, and hiding columns on smaller viewports.
  None were needed — the root cause was structural, not content-based. Fixing CSS precedence
  solved the issue without changing column layout or readability.

## Solution

Two CSS property changes in `frontend/src/chapters/AuditSheetView/AuditSheetView.css`:

**Before:**
```css
.audit-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-gridline);
  border-radius: var(--border-radius);
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
}
```

**After:**
```css
.audit-table-wrap {
  overflow-x: auto;
  min-width: 0; /* flex item: allow shrinking below content width so overflow-x: auto fires */
  border: 1px solid var(--color-gridline);
  border-radius: var(--border-radius);
}

.audit-table {
  min-width: 100%;
  border-collapse: collapse;
}
```

Two changes, both necessary:

1. `min-width: 0` on `.audit-table-wrap` — overrides the flex `min-width: auto` default so the
   wrapper can shrink to its constrained parent width.
2. `min-width: 100%` on `.audit-table` (replacing `width: 100%`) — allows the table to grow wider
   than the wrapper when its natural content width exceeds the container, which triggers the
   scoped scrollbar.

## Why This Works

Flex items have a default `min-width: auto`, which resolves to the element's minimum content size.
For a table with `white-space: nowrap` on all cells, the minimum content size is the full width
needed to render all columns without wrapping — approximately 1100px for a 12-column table.

The wrapper therefore expanded to 1100px, exceeding its parent's constrained width (900px
max-width minus 48px padding on each side = 804px content area). Because the wrapper was as wide
as the table, `overflow-x: auto` never detected content wider than its container — and no scoped
scrollbar fired. The overflow escaped upward to the page level instead.

Adding `min-width: 0` tells the flex algorithm: "this item is allowed to be narrower than its
minimum content size." The wrapper now shrinks to 804px. The table's natural width (~1100px) now
exceeds the wrapper, triggering `overflow-x: auto` correctly. The page stays at 804px; only the
table wrapper scrolls.

`min-width: 100%` on the table (instead of `width: 100%`) is the paired fix. `width: 100%` on a
table means "try to be exactly 100% of the container," which some browsers enforce too strictly
when combined with `white-space: nowrap`, causing cells to overflow the table rather than the
table growing. `min-width: 100%` means "be at least 100% wide" — the table fills the wrapper
when content is narrow, and grows when content demands more space.

## Prevention

**The canonical pattern for scrollable content inside a flex column:**

```css
/* The flex child that wraps the scrollable content */
.scrollable-wrapper {
  overflow-x: auto;
  min-width: 0; /* required — overrides flex min-width:auto default */
}

/* The content that should scroll */
.wide-content {
  min-width: 100%; /* fills wrapper if narrow; expands beyond if content is wider */
}
```

Apply this pattern whenever you have a flex item that contains horizontally scrollable content
(tables, code blocks, horizontal lists, etc.).

**How to detect the bug early:**
- Build browsers don't catch this; jsdom-based tests (Vitest, Jest + JSDOM) won't either.
- Test in a real browser at a viewport narrower than the content's natural width.
- If the page scrolls instead of the wrapper, check `min-width: 0` on the flex item.

**Warning sign:** If you have `overflow-x: auto` on a flex item and no scoped scrollbar appears
even when the content should be wider than the container, the flex item's `min-width: auto`
default is almost certainly the cause.

## Related Issues

- Session `bb48a5b6` (2026-05-31): bug shipped without being caught; deferred to next session
- Committed in `0e9c587`: `fix: prevent EDI Audit Sheet from scrolling the full page horizontally`
