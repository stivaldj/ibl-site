# ibl-site

## What This Is

`ibl-site` is a customer-facing CASE Construction / IBL Máquinas website focused on machine discovery, product evaluation, and lead generation. It combines a marketing homepage, generated category and product pages, and webhook-based lead capture that creates opportunities inside `ibl-ai-os`.

The initial production-hardening milestone is complete, and the homepage hero first-fold stabilization milestone is now complete as well. The project has a verified `v1.1` baseline, and future milestones should build from the shipped launch-ready foundation plus the stabilized hero system rather than reopening either by default.

## Core Value

Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

## Current State

- `v1.0` shipped on 2026-03-20 and remains the verified production-hardening baseline
- `v1.1` shipped on 2026-03-28 with 3 phases, 6 plans, and 12 / 12 milestone requirements satisfied
- The homepage hero now uses explicit per-model stage metadata, layered stage anchors, tuned visual balance, and responsive/runtime stability guardrails
- Lead generation, rebuild, packaging, and launch-gate workflows from `v1.0` remain intact and are still the operational baseline
- The latest milestone audit closed with accepted non-blocking tech debt around future hero metadata upkeep and duplicated desktop/mobile hero logic

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
- ✓ The homepage hero uses per-model stage metadata instead of improvised shared offsets — shipped in `v1.1`
- ✓ The rotating ring, machine mass, and hero overlays stay visually balanced across the eight showcase models — shipped in `v1.1`
- ✓ Hero first-render, rapid switching, and responsive containment are stable across supported breakpoints — shipped in `v1.1`

### Active

- [ ] Define the next milestone based on the highest-value user or business outcome after the shipped `v1.1` baseline
- [ ] Decide whether hero-related follow-up should target asset quality, implementation deduplication, or a different commercial priority

### Out of Scope

- Reopening completed v1.0 production-hardening work without a new defect or business reason
- Major platform rewrites or a full-stack rebuild unless a future milestone explicitly justifies that cost
- Nice-to-have experiments that do not materially improve customer trust, conversion, or operational leverage

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

- Choose the next highest-leverage milestone instead of assuming more hero work by default
- Preserve the shipped v1.0 and v1.1 quality bar while scoping any follow-up narrowly
- If hero follow-up is chosen, treat asset quality and desktop/mobile deduplication as explicit planned work rather than incidental cleanup

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat the first initiative as a production-hardening milestone, not a feature-first milestone | The original site needed stability and credibility before more feature work could compound existing issues | ✓ Validated in `v1.0` |
| Keep the site focused on both customer research and lead generation | The website must serve prospects while feeding commercial opportunity creation into `ibl-ai-os` | ✓ Validated in `v1.0` |
| Allow only small must-have additions in the first roadmap | Some launch-critical gaps required additions, but broad expansion would have undermined stabilization | ✓ Validated in `v1.0` |
| Use a full-sweep discovery approach instead of a fixed bug list | The user was non-technical and wanted the project to learn what was wrong through structured analysis | ✓ Validated in `v1.0` |
| Preserve the current hero art direction while fixing first-fold composition issues | The business problem was visual instability in the shipped hero, not lack of a design direction | ✓ Validated in `v1.1` |
| Solve hero consistency with per-model layout metadata instead of global offsets | Machine assets have different crops and proportions, so the stage must normalize perceived composition per asset | ✓ Validated in `v1.1` |

---
*Last updated: 2026-03-28 after closing v1.1 milestone*
