---
phase: 08-visual-balance
plan: 01
subsystem: ui
tags: [hero, visual-balance, runtime, css-vars]

# Dependency graph
requires:
  - phase: 7
    provides: hero-stage contract, layered markup, and shell-scoped stage variables
provides:
  - tuned per-model stage metadata for the eight showcase machines
  - variable-driven machine and ring composition with stable hover amplification
affects: [08-02, later responsive hero refinement]

# Tech tracking
tech-stack:
  added: []
  patterns: [model-specific hero stage tuning, shell-scoped transform variables, ring tracking through badge offsets]

key-files:
  created: [".planning/phases/08-visual-balance/08-01-SUMMARY.md"]
  modified: ["main.js", "mobile/main.js", "style.css", "mobile/style.css", ".planning/STATE.md"]

key-decisions:
  - "Keep explicit stage metadata on every model and tune the values directly instead of adding fallback heuristics."
  - "Drive the machine and ring from shell-scoped CSS variables so the active asset and badge move together."
  - "Preserve hover amplification by scaling the machine locally without changing the stage anchor."

patterns-established:
  - "Pattern 1: model balance is adjusted in the dataset, not through per-model inline style overrides."
  - "Pattern 2: the hero stage consumes one shared CSS variable contract for machine, badge, and object-position alignment."

requirements-completed: [VIS-01, VIS-02, VIS-03]

# Metrics
duration: 35min
completed: 2026-03-27
---

# Phase 8-01 Summary

**Per-model visual balance tuning for the hero stage**

## Performance

- **Duration:** 35 min
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Tuned the eight `showcaseMachines` stage definitions in `main.js` and `mobile/main.js` so each model now carries an explicit perceived-size balance.
- Removed the inline image `objectPosition` override so the CSS variable contract drives the active hero placement consistently.
- Updated `style.css` and `mobile/style.css` to consume `--hero-machine-scale`, `--hero-machine-x`, `--hero-machine-y`, `--hero-machine-object-position`, `--hero-badge-scale`, `--hero-badge-x`, and `--hero-badge-y` from the shared stage wrapper.
- Kept the selector behavior, copy, and links unchanged.

## Verification
- `npm run build`
- `rg -n "stage: \\{|scale:|translateX:|translateY:|objectPosition:|badgeScale:|badgeTranslateX:|badgeTranslateY:" main.js mobile/main.js`
- `rg -n "showcase-machine-img|showcase-ring|hero-machine-scale|hero-machine-x|hero-machine-y|hero-machine-object-position|hero-badge-scale|hero-badge-x|hero-badge-y" style.css mobile/style.css`
- `rg -n "translateX\\(-150px\\)|center 52%|right: -112px|right: 10px|--img-translate" main.js mobile/main.js style.css mobile/style.css || true`

## Notes
- No functional selector changes were introduced.
- Wave 2 remains pending for overlay hierarchy refinements.
