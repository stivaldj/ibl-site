---
phase: 01-site-experience-stabilization
plan: "03"
subsystem: ui
tags: [runtime, browse-journey, analytics, breadcrumb, mobile]
requires:
  - phase: 01-site-experience-stabilization
    provides: Entry-shell CTA parity and generated-route baseline from plans 01-01 and 01-02
provides:
  - Shared runtime parity for CTA tracking, breadcrumb schema extraction, and unit-summary behavior
  - Final desktop and mobile browse-journey verification for the Phase 1 representative route
  - Phase 1 completion evidence for homepage, catalog, category, and PDP runtime behavior
affects: [phase-1, phase-2, generated-runtime]
tech-stack:
  added: []
  patterns:
    - Shared browse-runtime fixes must land identically in main.js, webapp/main.js, and mobile/main.js
    - Generated-route runtime verification should use Vite dev serving when the page imports source entry modules directly
key-files:
  created:
    - .planning/phases/01-site-experience-stabilization/01-03-SUMMARY.md
  modified:
    - main.js
    - webapp/main.js
    - mobile/main.js
    - .planning/STATE.md
    - .planning/ROADMAP.md
key-decisions:
  - "Switched CTA tracking to delegated click handling so dynamically injected PDP controls are counted without per-element rebinding."
  - "Scoped breadcrumb schema extraction to dedicated breadcrumb markup via data-breadcrumb-nav or the breadcrumb aria label, never broad header navigation."
  - "Used the Vite dev server for final runtime smoke coverage because generated pages import source entry modules that do not execute under a raw static server."
patterns-established:
  - "Shared runtime sections should be diff-checked across all three entry scripts before closing browse-runtime work."
  - "Representative route smokes should confirm runtime-injected PDP content and schema, not just static HTML presence."
requirements-completed: [EXP-01, EXP-02, EXP-03, EXP-04, FE-01]
duration: 15min
completed: 2026-03-20
---

# Phase 1: Site Experience Stabilization Summary

**Shared runtime tracking, breadcrumb targeting, and unit-summary behavior are now aligned across all entry scripts, and the representative Phase 1 browse path passes on desktop and mobile**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-20T12:56:45Z
- **Completed:** 2026-03-20T13:11:50Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Aligned the duplicated runtime so dynamically injected PDP CTA controls now emit `cta_click` events in all three entry scripts.
- Scoped breadcrumb schema generation to page-level breadcrumb markup and synchronized the legacy unit-summary behavior in `main.js` with the corrected shell runtime.
- Re-ran the representative browse journey from `/` and `/mobile/` through `/produtos/`, `/produtos/retroescavadeiras/`, and `/produtos/retroescavadeiras/580n/` with clean console/network results.

## Task Commits

Each task was committed atomically:

1. **Task 1: Eliminate shared-runtime browse drift across all three entry scripts** - `cc437de` (fix)
2. **Task 2: Re-run the desktop and mobile browse journey end to end** - `PENDING_HASH` (docs)

**Plan metadata:** `PENDING_HASH` (docs)

## Files Created/Modified

- `main.js` - Brought CTA delegation, breadcrumb schema targeting, and unit-summary behavior into line with the approved shared runtime.
- `webapp/main.js` - Switched shared CTA tracking to delegated handling and scoped breadcrumb schema extraction to page breadcrumb markup.
- `mobile/main.js` - Mirrored the same shared CTA tracking and breadcrumb schema corrections used by the desktop runtime.
- `.planning/phases/01-site-experience-stabilization/01-03-SUMMARY.md` - Recorded execution details, deviations, and verification evidence for plan 01-03.
- `.planning/STATE.md` - Marked Phase 1 complete and updated the next execution target to Phase 2.
- `.planning/ROADMAP.md` - Added the final Phase 1 execution-progress note for completed plan 01-03.

## Decisions Made

- Kept the runtime fix scoped to browse-critical parity work and did not drift into lead webhook or SEO migration changes.
- Verified breadcrumb correctness from the generated PDP schema itself so the selector fix is proven against the page-level breadcrumb target.
- Preserved the webapp-only layout editor block and only aligned the browse-critical sections shared by all three entry scripts.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Switched runtime smoke verification from raw static serving to a local Vite dev server**
- **Found during:** Task 2 (Re-run the desktop and mobile browse journey end to end)
- **Issue:** The generated routes import `/main.js`, `/webapp/main.js`, and `/mobile/main.js` source entry modules directly, so a plain static server exposes the HTML but does not execute the CSS-importing runtime correctly.
- **Fix:** Kept `npm run build` as the compile gate, used a raw Python server only to confirm generated-route HTML resolution, and ran the final route journey against `vite` on `http://127.0.0.1:4318/` so the source runtime executed as shipped during local development.
- **Files modified:** `.planning/phases/01-site-experience-stabilization/01-03-SUMMARY.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`
- **Verification:** `npm run build`; desktop and mobile route smoke on Vite dev server with clean console/network capture
- **Committed in:** `PENDING_HASH`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The deviation was verification-only and necessary to exercise the real shared runtime on generated routes. No product-scope expansion was introduced.

## Issues Encountered

- The built-in browser tool failed to launch due to a local Chrome persistent-profile collision, so the route smoke used an isolated Playwright install under `/tmp/variant-playwright` instead.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 1 browse stabilization is complete across homepage, generated routes, and the mobile entry path.
- Phase 2 can now focus on lead-flow hardening without carrying shared browse-runtime blockers from Phase 1.

## Self-Check

- Summary exists at `.planning/phases/01-site-experience-stabilization/01-03-SUMMARY.md`: PENDING
- Task commits for `01-03` exist in git log: PENDING
- Verification completed: `npm run build`; desktop `/ -> /produtos/ -> /produtos/retroescavadeiras/ -> /produtos/retroescavadeiras/580n/`; mobile `/mobile/ -> /produtos/ -> /produtos/retroescavadeiras/ -> /produtos/retroescavadeiras/580n/`; console clean; network clean: PENDING

**PENDING**

---
*Phase: 01-site-experience-stabilization*
*Completed: 2026-03-20*
