---
phase: 09-responsive-stability
plan: 02
subsystem: ui
tags: [hero, responsive-stability, initial-render, rapid-switching]

# Dependency graph
requires:
  - phase: 8
    provides: tuned hero stage, shell-scoped overlay variables, and overlay hierarchy guardrails
  - phase: 9-01
    provides: shell containment and mobile guardrails
provides:
  - deterministic initial hero render with a bounded readiness gate
  - rapid-switch cleanup that prevents stale image timers and opacity drift
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [hero-ready gate, revision-guarded image swap, bounded opacity transition]

key-files:
  created: [".planning/phases/09-responsive-stability/09-02-SUMMARY.md"]
  modified: ["main.js", "mobile/main.js", "style.css", "mobile/style.css"]

key-decisions:
  - "Keep the existing selector and copy/link behavior intact."
  - "Use a single hero-ready class to suppress the first-frame transition contract until the initial state has settled."
  - "Guard image swaps with a revision counter so rapid switches cannot reapply stale opacity or source changes."

patterns-established:
  - "Pattern 1: first paint should be stable before motion is re-enabled."
  - "Pattern 2: repeated hero state changes need stale-timer cleanup, not more layout work."

requirements-completed: [RSP-03]

# Metrics
duration: 0min
completed: 2026-03-28
---

# Phase 9-02 Summary

**Deterministic initial render and rapid-switch stability for the hero**

## Performance

- **Duration:** 0 min
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added a `hero-ready` gate that is applied after the first settled render, so the tuned hero enters view without a first-frame transition flash.
- Mirrored the readiness gate in `mobile/main.js` so the mobile bundle follows the same deterministic startup path.
- Added a revision-guarded image swap with timer cleanup in `main.js` and `mobile/main.js` so rapid category switching cannot leave stale opacity or delayed image updates behind.
- Suppressed machine/ring transitions until the ready state is active in `style.css` and `mobile/style.css`, keeping the motion bounded instead of stacking on load.

## Verification
- `npm run build`
- `rg -n "switchShowcase|showcase-ready|hero-ready|requestAnimationFrame|transition|opacity" main.js mobile/main.js style.css mobile/style.css`
- `rg -n "switchShowcase|hero-ready|transition|will-change|opacity|transform" main.js mobile/main.js style.css mobile/style.css`

## Notes
- Selector semantics, copy, and link behavior were left unchanged.
- Phase 9-01 still owns shell containment and mobile guardrails; this plan only hardened the runtime transition path.
