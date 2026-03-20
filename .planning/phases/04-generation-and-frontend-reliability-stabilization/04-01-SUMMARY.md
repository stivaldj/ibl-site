---
phase: 04-generation-and-frontend-reliability-stabilization
plan: "01"
subsystem: infra
tags: [python, generation, assets, static-site, pipeline]
requires:
  - phase: 03-seo-and-content-trust-hardening
    provides: generated pages with source-owned metadata ready for deterministic reruns
provides:
  - deterministic generated asset selection for catalog and product pages
  - explicit refresh controls for image-processing helpers
  - strict scrape failure signaling for content refresh runs
affects: [phase-04, phase-05, build-ops, content-regeneration]
tech-stack:
  added: []
  patterns: [deterministic asset sync, dry-run-first pipeline refresh, strict scraper exits]
key-files:
  created: []
  modified:
    - generate_pages.py
    - process_fotos.py
    - remove_bg_batch.py
    - scrape_specs.py
key-decisions:
  - "Preserve intentional *-nobg derivatives during public asset sync while deleting other unmanaged leftovers."
  - "Use force/sync/dry-run flags instead of hidden manual-deletion requirements for image refreshes."
  - "Expose scraper partial-refresh failures through --strict instead of silently returning success."
patterns-established:
  - "Generated asset choice must be sorted and timestamp-aware before HTML is regenerated."
  - "Pipeline helpers should support dry-run inspection even when heavyweight processing dependencies are unavailable."
requirements-completed: [GEN-01, GEN-03, FE-03]
duration: 15 min
completed: 2026-03-20
---

# Phase 4: Generation And Frontend Reliability Stabilization Summary

**The Python generation pipeline now picks assets deterministically, removes unmanaged leftovers, and exposes refresh behavior explicitly instead of depending on manual cleanup**

## Performance

- **Duration:** 15 min
- **Started:** 2026-03-20T16:04:00Z
- **Completed:** 2026-03-20T16:19:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Sorted source-asset selection in `generate_pages.py`, refreshed copied assets when upstream files changed, and deleted unmanaged leftovers while preserving deliberate `*-nobg.png` derivatives.
- Added `--force`, `--sync`, and `--dry-run` controls to both image-processing helpers so reruns no longer depend on deleting output files by hand.
- Added `--strict` to `scrape_specs.py` so partial refresh failures can fail the run instead of leaving stale content under a success exit code.

## Task Commits

Each task was committed atomically:

1. **Task 1: Make generator asset selection and public sync deterministic** - `15da589` (fix)
2. **Task 2: Remove silent stale-output behavior from image/spec processing scripts** - `a775975` (fix)

## Files Created/Modified
- `generate_pages.py` - sorts and synchronizes model assets before regenerating product/catalog HTML
- `process_fotos.py` - adds timestamp-aware refresh logic plus `--force`, `--sync`, and `--dry-run`
- `remove_bg_batch.py` - adds explicit derivative refresh/sync controls and lazy `rembg` loading
- `scrape_specs.py` - adds explicit strict failure mode and configurable pacing for refresh runs

## Decisions Made
- Preserved `*-nobg.png` outputs as intentional launch assets instead of deleting them during source asset sync, but removed any other unmanaged files from model asset directories.
- Made dry-run inspection independent from `rembg` import success so operators can verify what a rerun would do before installing heavyweight image dependencies.
- Kept the scraper write path intact while surfacing partial refresh failure through exit status, which is the smallest safe change for production hardening.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Moved rembg imports behind execution paths**
- **Found during:** Task 2 (Remove silent stale-output behavior from image/spec processing scripts)
- **Issue:** The new dry-run verification path still crashed immediately in environments without `rembg`, making the explicit refresh controls unusable for inspection.
- **Fix:** Deferred `rembg` imports until the actual background-removal step executes.
- **Files modified:** `process_fotos.py`, `remove_bg_batch.py`
- **Verification:** `python3 process_fotos.py --dry-run --sync` and `python3 remove_bg_batch.py --dry-run --sync` both complete successfully without `rembg` installed
- **Committed in:** `a775975` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep. The deviation was necessary to make the new refresh controls verifiable in the current environment.

## Issues Encountered
- The local Python environment does not currently have `rembg` installed, so full image regeneration was not re-run end-to-end during this plan. The new refresh semantics were still validated through dry-run mode and timestamp/sync logic, and Phase 4 docs should call out that dependency explicitly.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Repeated `python3 generate_pages.py` runs now keep the generated HTML digest stable.
- The generator now removes unmanaged leftovers from audited model asset folders, confirmed by creating and re-running away a temporary stale file under `public/case-assets/retroescavadeiras/580n/`.
- Phase `04-03` can document the rebuild flow around explicit `--sync` and `--strict` commands instead of relying on tribal knowledge.

---
*Phase: 04-generation-and-frontend-reliability-stabilization*
*Completed: 2026-03-20*
