# Requirements: VARIANT

**Defined:** 2026-03-27
**Core Value:** Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

## v1 Requirements

Requirements for `v1.1 Hero First Fold Stability`. Each maps to exactly one roadmap phase.

### Hero Stage System

- [x] **HERO-01**: Each `showcaseMachines` entry defines explicit hero-stage layout metadata for its model, including machine, ring, badge, title, and supporting overlay positioning values.
- [x] **HERO-02**: `switchShowcase()` applies the active model's hero-stage metadata through one consolidated visual update path with safe neutral fallbacks for missing values.
- [x] **HERO-03**: The hero markup separates the right-side visual stage into independent ring, machine, and overlay layers with clear anchor wrappers for controlled positioning.

### Visual Balance

- [x] **VIS-01**: The rotating ring aligns to the active machine's visual center using per-model offsets instead of a single fixed shell center.
- [x] **VIS-02**: The active machine image uses CSS custom properties for translation and scale so all eight current models reach a consistent perceived visual mass on desktop hero layouts.
- [x] **VIS-03**: Hover amplification on the machine preserves the centered relationship between the machine and rotating ring without shifting the composed stage.

### Overlay Hierarchy

- [x] **OVR-01**: The large machine title is positioned per model so it does not obscure the machine's critical silhouette.
- [x] **OVR-02**: The technical card uses controlled variable-driven positioning rather than the current fixed offset and does not visually collide with the model-meta block.
- [x] **OVR-03**: The model-meta block is positioned so it stays readable and does not compete with the technical card or ring badge across the eight hero models.

### Responsive Stability

- [x] **RSP-01**: The updated hero stage remains intact without clipping or overlay collisions at desktop `1440px`, laptop `1280px`, and tablet `1024px`.
- [x] **RSP-02**: The hero-stage changes do not reintroduce mobile overflow, broken touch targets, or incorrect variable leakage into the mobile-specific first-dobra layout.
- [x] **RSP-03**: Rapid category switching and initial load complete without abnormal flicker, jump, or broken active-state rendering.

## v2 Requirements

### Asset Quality

- **AST-01**: Replace or reprocess individual machine assets whose source crop quality remains visibly poor even after per-model stage tuning.
- **AST-02**: Introduce an asset-preparation workflow that standardizes hero-ready cutouts before they enter the showcase dataset.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Hero redesign or change of overall art direction | This milestone is a layout-system correction, not a redesign |
| Removal of the rotating ring, technical card, or editorial title | The milestone explicitly preserves these existing hero signatures |
| Changes to category selector behavior or information architecture | The current selector interaction should remain intact |
| Reprocessing all source assets immediately | The current goal is per-model normalization in code first |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| HERO-01 | Phase 7 | Complete |
| HERO-02 | Phase 7 | Complete |
| HERO-03 | Phase 7 | Complete |
| VIS-01 | Phase 8 | Complete |
| VIS-02 | Phase 8 | Complete |
| VIS-03 | Phase 8 | Complete |
| OVR-01 | Phase 8 | Complete |
| OVR-02 | Phase 8 | Complete |
| OVR-03 | Phase 8 | Complete |
| RSP-01 | Phase 9 | Complete |
| RSP-02 | Phase 9 | Complete |
| RSP-03 | Phase 9 | Complete |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-27*
*Last updated: 2026-03-28 after Phase 9 verification*
