---
phase: 04-generation-and-frontend-reliability-stabilization
plan: "02"
subsystem: infra
tags: [vite, packaging, static-site, dist, frontend]
requires:
  - phase: 03-seo-and-content-trust-hardening
    provides: generated catalog and product HTML ready to be packaged as production entries
provides:
  - honest production build for homepage, mobile shell, and generated produtos routes
  - packaged JS and CSS assets for generated routes inside dist/assets
  - quarantined src directory documenting the real production entrypoints
affects: [phase-04, phase-05, launch-verification, build-ops]
tech-stack:
  added: []
  patterns: [html-first Vite entry discovery, explicit quarantined dead-surface directories]
key-files:
  created:
    - src/README.md
  modified:
    - package.json
    - vite.config.js
key-decisions:
  - "Use generated HTML files under produtos/ as first-class Vite inputs instead of post-build copying raw source pages."
  - "Quarantine the emptied src/ directory with a tracked README because the original Vite starter files were untracked in this local repo."
patterns-established:
  - "Production packaging is HTML-first: index.html, mobile/index.html, and produtos/**/*.html define the launch surface."
  - "Dead scaffolds should be removed from active paths and, when git history would otherwise hide that removal, replaced with an explicit quarantine note."
requirements-completed: [FE-02, FE-03, OPS-03]
duration: 12 min
completed: 2026-03-20
---

# Phase 4: Generation And Frontend Reliability Stabilization Summary

**Vite now builds the full launch surface, including generated catalog/product routes, and the old src demo scaffold is explicitly quarantined away from production paths**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-20T16:07:29Z
- **Completed:** 2026-03-20T16:19:29Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added dynamic Vite HTML entry discovery so `/produtos/**` routes are packaged into `dist/` instead of being absent from the production artifact.
- Made `npm run build` point to the now-honest full-site packaging path and verified representative homepage, mobile, catalog, category, and product routes exist in `dist/`.
- Removed the default Vite demo surface and replaced it with an explicit `src/README.md` that points maintainers at the real production entrypoints.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create one production packaging path that includes the generated catalog surface** - `c3de5a0` (feat)
2. **Task 2: Remove or quarantine dead Vite scaffold surface area** - `8965de4` (chore)

## Files Created/Modified
- `package.json` - points `npm run build` at the full-site packaging command
- `vite.config.js` - discovers generated HTML entries and includes them in the Vite build
- `src/README.md` - documents that `src/` is intentionally not part of the live application path

## Decisions Made
- Treated generated `produtos/**/*.html` as first-class Vite inputs so the packaged artifact inherits the same source HTML already verified in earlier phases, with built asset rewriting handled by Vite itself.
- Kept the build path minimal: no custom copy/sync script was needed because Vite can package the full launch surface directly once all HTML entries are declared.
- Left `dist/` as a generated artifact rather than forcing it into git history during this plan; the important change is that the build command now produces a launch-complete output tree on demand.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Quarantined src instead of committing pure deletions**
- **Found during:** Task 2 (Remove or quarantine dead Vite scaffold surface area)
- **Issue:** The original Vite starter files under `src/` were untracked in this local git repo, so deleting them would clean the working tree but leave no durable commit evidence explaining the removal.
- **Fix:** Deleted the demo files from the workspace and added a tracked `src/README.md` that explicitly marks the directory as non-production and points to the real entrypoints.
- **Files modified:** `src/README.md`
- **Verification:** `find src -maxdepth 2 -type f` now returns only `src/README.md`
- **Committed in:** `8965de4` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep. The deviation made the scaffold removal durable and clearer in git history.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `npm run build` now produces `dist/index.html`, `dist/mobile/index.html`, `dist/produtos/index.html`, representative category pages, representative product pages, and the built runtime/style assets they depend on.
- Phase 4 plan `04-03` can now document and verify the real rebuild flow against an honest final artifact instead of a partial shell-only build.

---
*Phase: 04-generation-and-frontend-reliability-stabilization*
*Completed: 2026-03-20*
