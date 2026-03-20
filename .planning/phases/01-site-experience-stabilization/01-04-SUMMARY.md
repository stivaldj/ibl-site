---
phase: 01-site-experience-stabilization
plan: "04"
subsystem: ui
tags: [generator, cta, anchor, browse-verification, produtos]
requires:
  - phase: 01-site-experience-stabilization
    provides: Generated browse surfaces and runtime parity from plans 01-01 through 01-03
provides:
  - Single generator source for the launch-approved homepage lead anchor
  - Regenerated catalog, category, and product pages without stale /#contato CTA targets
  - Browser verification that sampled generated CTAs land on /#captacao-lead while homepage and mobile keep the approved contact target
affects: [phase-1, phase-2, generated-pages]
tech-stack:
  added: []
  patterns:
    - Repeated generated CTA destinations should resolve from one generator constant instead of mixed hardcoded hashes
    - Generated-route CTA fixes must be proven in source, regenerated HTML, and browser navigation on representative routes
key-files:
  created:
    - .planning/phases/01-site-experience-stabilization/01-04-SUMMARY.md
  modified:
    - generate_pages.py
    - produtos/index.html
    - produtos/retroescavadeiras/index.html
    - produtos/retroescavadeiras/580n/index.html
    - .planning/STATE.md
    - .planning/ROADMAP.md
key-decisions:
  - "Kept the fix scoped to the generator-owned contact destination instead of adding alternate homepage anchors or runtime redirects."
  - "Updated the generated header CTA to read the shared HOME_CONTACT_URL constant so catalog, category, and product output do not drift from one another."
  - "Used the local Vite dev server for browser proof because the sampled generated routes import source entry modules during local verification."
patterns-established:
  - "If generated HTML repeats the same CTA contract, fix the generator source first and regenerate the tree rather than patching individual pages."
  - "Hash-target browse regressions should be verified by actual clicks from representative generated routes into the homepage anchor."
requirements-completed: [EXP-04, EXP-01, FE-01]
duration: 4min
completed: 2026-03-20
---

# Phase 1: Site Experience Stabilization Summary

**Generated catalog, category, and product CTAs now resolve to the real homepage lead anchor, and sampled generated-route clicks land on `/#captacao-lead` without breaking homepage or mobile contact behavior**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-20T13:26:56Z
- **Completed:** 2026-03-20T13:30:19Z
- **Tasks:** 3
- **Files modified:** 45

## Accomplishments

- Repointed the generator-owned contact destination from `/#contato` to the approved homepage lead anchor `/#captacao-lead`.
- Regenerated the full `produtos/` catalog/category/product tree so no stale generated CTA links still ship the dead-end hash.
- Re-verified `/`, `/mobile/`, `/produtos/`, `/produtos/retroescavadeiras/`, and `/produtos/retroescavadeiras/580n/` in a browser, including real CTA clicks from the sampled generated routes back to the homepage lead section.

## Task Commits

Each task was committed atomically:

1. **Task 1: Align repeated generated contact CTAs to the real homepage lead anchor** - `04fa678` (fix)
2. **Task 2: Regenerate the affected browse surfaces and remove stale dead-end targets** - `e5607f6` (fix)
3. **Task 3: Re-verify generated CTA navigation against homepage and mobile anchor behavior** - `TBD_ON_COMMIT` (docs)

**Plan metadata:** `TBD_ON_COMMIT` (docs)

## Files Created/Modified

- `generate_pages.py` - Centralized generated contact CTA output on `HOME_CONTACT_URL="/#captacao-lead"` and routed the generated header CTA through that shared source.
- `produtos/index.html` - Regenerated the catalog page so launch-facing contact CTAs now point to `/#captacao-lead`.
- `produtos/retroescavadeiras/index.html` - Regenerated the representative category page so repeated support/footer contact actions no longer use `/#contato`.
- `produtos/retroescavadeiras/580n/index.html` - Regenerated the representative product page so header, hero, CTA section, and footer contact links all resolve to the approved homepage anchor.
- `.planning/phases/01-site-experience-stabilization/01-04-SUMMARY.md` - Recorded execution details, verification evidence, and plan-closeout state for plan 01-04.
- `.planning/STATE.md` - Corrected Phase 1 state to reflect the gap closure and restored Phase 2 as the next ready execution target.
- `.planning/ROADMAP.md` - Added the Phase 1 execution-progress note showing 01-04 closed the remaining generated CTA mismatch.

## Decisions Made

- Kept the change set limited to the generator-owned contact destination mismatch and did not add alternate homepage anchors or broader CTA-flow work.
- Treated the generated header CTA as part of the same repeated contract and removed its hardcoded hash so future generator edits stay consistent.
- Verified the fix with actual browser clicks from generated routes rather than relying on static HTML inspection alone.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 1 is now fully closed, including the generated CTA anchor gap called out by verification.
- Phase 2 can proceed without carrying a generated-route contact-anchor mismatch into lead-flow hardening.

---
*Phase: 01-site-experience-stabilization*
*Completed: 2026-03-20*
