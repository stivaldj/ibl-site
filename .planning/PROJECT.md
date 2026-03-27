# VARIANT

## What This Is

`VARIANT` is a customer-facing CASE Construction / IBL Máquinas website focused on machine discovery, product evaluation, and lead generation. It combines a marketing homepage, generated category and product pages, and webhook-based lead capture that creates opportunities inside `ibl-ai-os`.

The initial production-hardening milestone is now complete. The project has a verified v1.0 baseline, and future milestones should build on that hardened foundation instead of reopening launch-readiness work by default.

## Core Value

Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

## Current Milestone: v1.1 Hero First Fold Stability

**Goal:** Stabilize the homepage hero so every machine presents with consistent visual weight, correctly centered stage effects, and non-competing overlays without redesigning the existing experience.

**Target features:**
- Model-specific hero stage metadata for machine, ring, badge, title, and support overlays
- Anchored hero-stage layering that keeps the rotating ring visually centered on the active machine
- Responsive-safe overlay and sizing normalization across the eight showcase models

## Requirements

### Validated

- ✓ Visitors can browse a CASE/IBL homepage experience with brand-specific messaging and CTAs — existing
- ✓ Visitors can navigate a generated product catalog by category and machine model — existing
- ✓ Visitors can open machine detail pages with specs, imagery, and product-specific lead CTAs — existing
- ✓ Visitors can submit or initiate lead flows that can trigger webhook delivery to `ibl-ai-os` when configured — existing
- ✓ The site can be built and served as a static frontend using Vite and generated catalog pages — existing
- ✓ Visible UI and UX defects across homepage, catalog, product pages, and mobile variants were removed to a production-hardening bar — shipped in `v1.0`
- ✓ Lead capture and webhook-triggered opportunity creation are reliable, observable, and production-safe inside repo scope — shipped in `v1.0`
- ✓ SEO, metadata, content consistency, and trust issues blocking launch were corrected — shipped in `v1.0`
- ✓ Structural fragility in generation, assets, packaging, and frontend runtime was reduced enough for safe continuation — shipped in `v1.0`
- ✓ Launch-critical additions required for production readiness were completed without broad feature creep — shipped in `v1.0`

### Active

- [ ] Fix the first-dobra hero by replacing improvised positioning with a model-specific visual stage system
- [ ] Preserve the current hero design while eliminating ring-centering drift and overlay competition
- [ ] Keep hero interactions and category switching stable across desktop, tablet, and mobile layouts

### Out of Scope

- Reopening completed v1.0 production-hardening work without a new defect or business reason
- Major platform rewrites or a full-stack rebuild unless a future milestone explicitly justifies that cost
- Nice-to-have experiments that do not materially improve customer trust, conversion, or operational leverage

## Current State

- `v1.0` shipped on 2026-03-20
- 6 phases, 18 plans, and 21 / 21 milestone requirements satisfied
- The formal launch gate verifies rebuild, packaged smoke, and homepage/mobile/product lead flows with enforced WhatsApp handoff
- Build and generation workflows are documented in `docs/OPERATIONS.md`, `docs/LAUNCH-GATE.md`, and `docs/LAUNCH-READINESS.md`
- `v1.1` now focuses on improving the homepage hero stage system from the shipped baseline without reopening platform-hardening scope

## Context

The site began as a fast vibecoded brownfield build. The first milestone converted that into a production-grade baseline through systematic discovery, verification, and gap closure rather than relying on a fixed bug list.

The codebase map in `.planning/codebase/` still describes the architecture and ongoing constraints: a static-site-first frontend, generated catalog pages, webhook-driven lead capture, and a workflow that depends on disciplined rebuild and verification rather than framework complexity.

The primary audience remains prospective customers researching CASE machines, while the business outcome remains qualified lead generation for the IBL commercial flow.

## Constraints

- **Tech stack**: Brownfield static frontend with generated catalog pages — future milestones should preserve the working foundation unless a narrow change is clearly justified
- **Business flow**: Lead generation must continue to support webhook creation of opportunities in `ibl-ai-os`
- **Operational discipline**: Future work should preserve the documented rebuild and launch-gate workflows instead of introducing ad hoc release paths
- **Scope control**: Future milestones should be explicit about whether work is feature expansion, conversion optimization, or platform evolution

## Next Milestone Goals

- Replace the hero's hard-coded layout behavior with explicit per-model stage controls
- Preserve the v1.0 quality bar while fixing the most visible first-fold presentation issues
- Keep launch verification and operational evidence current as the hero implementation evolves

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat the first initiative as a production-hardening milestone, not a feature-first milestone | The original site needed stability and credibility before more feature work could compound existing issues | ✓ Validated in `v1.0` |
| Keep the site focused on both customer research and lead generation | The website must serve prospects while feeding commercial opportunity creation into `ibl-ai-os` | ✓ Validated in `v1.0` |
| Allow only small must-have additions in the first roadmap | Some launch-critical gaps required additions, but broad expansion would have undermined stabilization | ✓ Validated in `v1.0` |
| Use a full-sweep discovery approach instead of a fixed bug list | The user was non-technical and wanted the project to learn what was wrong through structured analysis | ✓ Validated in `v1.0` |
| Preserve the current hero art direction while fixing first-fold composition issues | The business problem is visual instability in the shipped hero, not lack of a design direction | — Pending |
| Solve hero consistency with per-model layout metadata instead of global offsets | Machine assets have different crops and proportions, so the stage must normalize perceived composition per asset | — Pending |

---
*Last updated: 2026-03-27 after starting v1.1 milestone*
