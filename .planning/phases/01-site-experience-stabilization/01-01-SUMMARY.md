---
phase: 01-site-experience-stabilization
plan: "01"
subsystem: ui
tags: [homepage, mobile, cta, navigation, smoke-test]
requires: []
provides:
  - "Desktop homepage entry shell with launch-approved CTA destinations"
  - "Mobile entry shell parity for browse and contact actions"
  - "Local coverage summary panel that removes external map noise from entry-shell smokes"
affects: [01-site-experience-stabilization, 02-lead-flow-hardening]
tech-stack:
  added: []
  patterns:
    - "Shell-specific CTA wiring lives in entry HTML/runtime instead of generated surfaces"
    - "Entry-shell location coverage uses local summary UI instead of external tile dependencies"
key-files:
  created:
    - ".planning/phases/01-site-experience-stabilization/01-01-SUMMARY.md"
  modified:
    - "index.html"
    - "mobile/index.html"
    - "webapp/main.js"
    - "mobile/main.js"
    - "webapp/style.css"
    - "mobile/style.css"
    - ".planning/STATE.md"
    - ".planning/ROADMAP.md"
key-decisions:
  - "Aligned desktop and mobile launch CTAs to only two real first-step destinations: /produtos/ and #captacao-lead."
  - "Demoted non-ready footer/social actions to explicit disabled controls instead of leaving them apparently clickable."
  - "Replaced Leaflet/OpenStreetMap entry-shell map usage with a local coverage summary so smoke checks stay free of external asset noise."
patterns-established:
  - "Entry-shell-only fixes stay in index/mobile shells and their dedicated stylesheets."
  - "Coverage selector cards expose active state through aria-pressed and update a shared summary panel."
requirements-completed: [EXP-01, EXP-02, EXP-03, EXP-04, FE-01]
duration: 16min
completed: 2026-03-20
---

# Phase 01: Site Experience Stabilization Summary

**Desktop and mobile entry shells now share real browse/contact paths, clean CTA states, and noise-free shell-only smoke behavior**

## Performance

- **Duration:** 16 min
- **Started:** 2026-03-20T12:39:09Z
- **Completed:** 2026-03-20T12:54:41Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Rewired desktop homepage CTAs and footer states so launch-facing actions resolve to `/produtos/`, `#captacao-lead`, or explicit disabled states.
- Brought `/mobile/` into parity with the desktop entry shell, including canonical metadata, CTA behavior, and small-screen layout handling.
- Replaced external entry-shell map behavior with a local coverage summary and completed clean desktop/mobile smoke validation with no console or request noise.

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove homepage dead ends and misleading entry CTAs** - `2e0118a` (fix)
2. **Task 2: Mirror the approved browse path on the mobile entry shell** - `4b02781` (fix)
3. **Task 3: Close shell-only regressions with route-specific smoke validation** - `8b4a8b0` (fix)

**Plan metadata:** `docs(01-01)` completion commit

## Files Created/Modified

- `index.html` - Desktop shell CTA destinations and disabled launch-state markup
- `mobile/index.html` - Mobile shell parity updates plus canonical/OG route correction
- `webapp/main.js` - Desktop coverage summary runtime and smoke-driven unit selector cleanup
- `mobile/main.js` - Mobile coverage summary runtime and smoke-driven unit selector cleanup
- `webapp/style.css` - Desktop shell spacing, CTA, coverage panel, and narrow viewport fixes
- `mobile/style.css` - Mobile shell spacing, CTA, coverage panel, and narrow viewport fixes
- `.planning/STATE.md` - Execution status and next planning position
- `.planning/ROADMAP.md` - Phase 1 progress note for completed Plan 01

## Decisions Made

- Kept Phase 2 lead-flow implementation out of scope and routed launch-facing contact actions only to the existing lead section anchor.
- Used shell-specific CSS for overlap and CTA layout fixes instead of runtime-only positioning hacks.
- Removed per-card unit map links once smoke validation showed nested interactive controls inside the selectable unit cards.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced desktop external map dependency with a local coverage panel**
- **Found during:** Task 1 (Remove homepage dead ends and misleading entry CTAs)
- **Issue:** The desktop entry shell depended on Leaflet/OpenStreetMap assets, which introduced avoidable route noise and conflicted with the plan's clean asset smoke requirement.
- **Fix:** Removed the external map scripts/styles and rendered a local coverage summary panel driven from the existing unit cards.
- **Files modified:** `index.html`, `webapp/main.js`, `webapp/style.css`
- **Verification:** `npm run build`; desktop `/` smoke check; console clean; non-static network requests clean
- **Committed in:** `2e0118a`

**2. [Rule 3 - Blocking] Mirrored the local coverage panel on the mobile entry shell**
- **Found during:** Task 2 (Mirror the approved browse path on the mobile entry shell)
- **Issue:** The mobile shell had the same external map dependency and would have failed the route-cleanliness verification for `/mobile/`.
- **Fix:** Removed the external map scripts/styles from the mobile shell and reused the local coverage summary behavior with mobile-specific layout support.
- **Files modified:** `mobile/index.html`, `mobile/main.js`, `mobile/style.css`
- **Verification:** `npm run build`; mobile `/mobile/` smoke check at 390px; console clean; non-static network requests clean
- **Committed in:** `4b02781`

**3. [Rule 1 - Bug] Removed nested interactions from the unit coverage selector during smoke validation**
- **Found during:** Task 3 (Close shell-only regressions with route-specific smoke validation)
- **Issue:** Each selectable unit card still injected its own Google Maps link, creating nested interactive controls inside the keyboard-activatable selector cards.
- **Fix:** Removed the per-card map links and surfaced the active selector state through `aria-pressed` on desktop and mobile.
- **Files modified:** `webapp/main.js`, `mobile/main.js`
- **Verification:** `npm run build`; desktop `/` and mobile `/mobile/` smoke checks; CTA click checks for `#captacao-lead` and `/produtos/`
- **Committed in:** `8b4a8b0`

---

**Total deviations:** 3 auto-fixed (1 bug, 2 blocking)
**Impact on plan:** All deviations were shell-only and necessary to meet the plan's route-cleanliness and interaction requirements. No architectural scope change was introduced.

## Issues Encountered

- The chat launcher initially crowded the narrow-width hero action area during responsive smoke checks; this was absorbed into the shell CSS refinements within Tasks 1 and 2.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Desktop `/` and mobile `/mobile/` are stable enough to move Phase 1 focus onto generated catalog, category, and PDP browsing surfaces.
- No blocker remains on the entry shells for Phase 2 lead-flow hardening.

## Self-Check

- Summary exists at `.planning/phases/01-site-experience-stabilization/01-01-SUMMARY.md`: PASSED
- Task commits for `01-01` exist in git log (`2e0118a`, `4b02781`, `8b4a8b0`): PASSED
- Verification completed: `npm run build`, desktop `/` smoke, mobile `/mobile/` smoke, console clean, non-static network requests clean: PASSED

**PASSED**

---
*Phase: 01-site-experience-stabilization*
*Completed: 2026-03-20*
