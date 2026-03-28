# Roadmap: VARIANT v1.1 Hero First Fold Stability

**Last updated:** 2026-03-27
**Primary project reference:** `.planning/PROJECT.md`

## Overview

This milestone focuses on the homepage hero stage only. The goal is to keep the current art direction and interaction model while replacing the improvised positioning logic with a per-model stage system that keeps the machine, ring, badge, title, and technical overlays visually stable.

## Phases

- [x] **Phase 7: Hero Stage Foundation** - Replace improvised hero positioning with explicit per-model stage metadata and layered markup
- [ ] **Phase 8: Visual Balance** - Normalize perceived machine size, ring centering, and overlay hierarchy across all showcase models
- [ ] **Phase 9: Responsive Stability** - Prove the updated hero stays stable across desktop, tablet, and rapid-switch interaction states

## Phase Details

### Phase 7: Hero Stage Foundation
**Goal:** Establish a model-aware hero stage with explicit layout metadata, a consolidated update path, and separated right-side layers.
**Depends on:** Phase 6
**Requirements:** HERO-01, HERO-02, HERO-03
**Success Criteria** (what must be TRUE):
1. Each of the eight showcase models has explicit stage metadata for machine and overlay placement.
2. `switchShowcase()` updates the active hero from one visual state path with neutral fallbacks for missing values.
3. The hero markup separates ring, machine, and overlay layers into independent wrappers.
4. The category selector continues to behave as it does today while the stage system changes underneath it.
**Plans:** 2 plans

Plans:
- [x] 07-01: Model-aware hero runtime contract
- [x] 07-02: Hero stage wrappers and neutral CSS baseline

### Phase 8: Visual Balance
**Goal:** Normalize the active machine's perceived scale and eliminate overlay competition while keeping the ring centered on the active asset.
**Depends on:** Phase 7
**Requirements:** VIS-01, VIS-02, VIS-03, OVR-01, OVR-02, OVR-03
**Success Criteria** (what must be TRUE):
1. The rotating ring visually tracks the active machine center instead of the shell center.
2. The machine image uses CSS custom properties for scale and translation so all eight models feel comparable in mass.
3. Hover amplification keeps the ring-machine relationship stable.
4. The large title no longer obscures the machine silhouette.
5. The technical card and model-meta block remain readable without colliding.
**Plans:** 2 plans

Plans:
- [ ] 08-01: Per-model balance and ring tracking
- [ ] 08-02: Overlay hierarchy and responsive guardrails

### Phase 9: Responsive Stability
**Goal:** Verify the updated hero remains intact across target breakpoints and interaction sequences.
**Depends on:** Phase 8
**Requirements:** RSP-01, RSP-02, RSP-03
**Success Criteria** (what must be TRUE):
1. The hero stays unclipped and collision-free at desktop `1440px`, laptop `1280px`, and tablet `1024px`.
2. The mobile layout does not inherit desktop hero overflow or broken touch targets.
3. Rapid category switching and initial load complete without flicker, jump, or broken active-state rendering.
**Plans:** TBD

Plans:
- [ ] TBD (run `$gsd-plan-phase 9` to break down)

## Coverage

- Total v1 requirements: 12
- Mapped to phases: 12
- Unmapped: 0
