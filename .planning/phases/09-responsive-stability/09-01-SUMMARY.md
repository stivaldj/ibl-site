---
phase: 09-responsive-stability
plan: 01
subsystem: ui
tags: [hero, responsive-stability, shell-containment, mobile-guardrails]

# Dependency graph
requires:
  - phase: 8
    provides: tuned hero stage, shell-scoped overlay variables, and overlay hierarchy guardrails
provides:
  - hero shell containment across desktop, laptop, tablet, and mobile widths
  - mobile-first guardrails that preserve the tuned first fold without desktop bleed-through
affects: [09-02, later rapid-switch stability]

# Tech tracking
tech-stack:
  added: []
  patterns: [viewport-safe hero shell sizing, clamp-based stage heights, mobile overflow guardrails]

key-files:
  created: [".planning/phases/09-responsive-stability/09-01-SUMMARY.md"]
  modified: ["index.html", "mobile/index.html", "style.css", "mobile/style.css"]

key-decisions:
  - "Keep the hero stage contract intact and only harden the shell-level overflow, width, and height behavior."
  - "Use clamp-based stage heights to preserve the tuned composition at desktop, laptop, tablet, and mobile widths."
  - "Add mobile guardrails in the mobile stylesheet rather than changing selector semantics or stage logic."

patterns-established:
  - "Pattern 1: hero shell containment lives on the outer section and direct container, not inside the stage layering contract."
  - "Pattern 2: mobile guardrails can narrow overflow and padding without reintroducing desktop offsets or selector changes."

requirements-completed: [RSP-01, RSP-02]

# Metrics
duration: 0min
completed: 2026-03-28
---

# Phase 9-01 Summary

**Breakpoint containment and mobile guardrails for the hero shell**

## Performance

- **Duration:** 0 min
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Tightened the hero shell wrapper in `index.html` and `mobile/index.html` to use viewport-safe widths with overflow visible at the markup level.
- Replaced the fixed hero stage height with clamp-based sizing so the tuned composition stays within the available fold at desktop, laptop, tablet, and mobile widths.
- Added shell-level containment rules in `style.css` and `mobile/style.css` so the hero container stays bounded while preserving the Phase 8 stage contract.
- Added mobile-first guardrails in `mobile/style.css` to keep the first fold touch-safe and prevent desktop overflow behavior from bleeding into the mobile layout.

## Verification
- `npm run build`
- `rg -n "entry-hero-shell|showcase-stage|showcase-machine-stage|showcase-overlay|overflow|clamp|max-width|min-height" index.html mobile/index.html style.css mobile/style.css`
- `rg -n "@media|max-width|showcase-stage|showcase-overlay|showcase-machine-stage|hero-tech-card|hero-model-meta|touch|min-height|overflow-x" mobile/style.css mobile/index.html style.css`

## Notes
- Selector behavior and stage-variable logic were left unchanged.
- Phase 9-02 remains responsible for initial-load and rapid-switch stability.
