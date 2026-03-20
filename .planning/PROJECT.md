# VARIANT

## What This Is

`VARIANT` is a customer-facing CASE Construction / IBL Máquinas website focused on machine discovery, product evaluation, and lead generation. It combines a marketing homepage, generated category and product pages, and webhook-based lead capture that creates opportunities inside `ibl-ai-os`.

The initial production-hardening milestone is now complete. The project has a verified v1.0 baseline, and future milestones should build on that hardened foundation instead of reopening launch-readiness work by default.

## Core Value

Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

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

- [ ] Define the next milestone's highest-value feature additions from the now-stable baseline
- [ ] Decide which business improvements should become real product features instead of further hardening work
- [ ] Validate the external `ibl-ai-os` acceptance path in the target production environment

### Out of Scope

- Reopening completed v1.0 production-hardening work without a new defect or business reason
- Major platform rewrites or a full-stack rebuild unless a future milestone explicitly justifies that cost
- Nice-to-have experiments that do not materially improve customer trust, conversion, or operational leverage

## Current State

- `v1.0` shipped on 2026-03-20
- 6 phases, 18 plans, and 21 / 21 milestone requirements satisfied
- The formal launch gate verifies rebuild, packaged smoke, and homepage/mobile/product lead flows with enforced WhatsApp handoff
- Build and generation workflows are documented in `docs/OPERATIONS.md`, `docs/LAUNCH-GATE.md`, and `docs/LAUNCH-READINESS.md`
- Remaining non-blocking items are bounded and mostly external: optional image refresh, upstream CASE source refresh, and final `ibl-ai-os` acceptance in the target environment

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

- Choose the highest-value product or business improvements now that the launch baseline is stable
- Preserve the v1.0 quality bar while adding new capability
- Keep launch verification and operational evidence current as the product evolves

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat the first initiative as a production-hardening milestone, not a feature-first milestone | The original site needed stability and credibility before more feature work could compound existing issues | ✓ Validated in `v1.0` |
| Keep the site focused on both customer research and lead generation | The website must serve prospects while feeding commercial opportunity creation into `ibl-ai-os` | ✓ Validated in `v1.0` |
| Allow only small must-have additions in the first roadmap | Some launch-critical gaps required additions, but broad expansion would have undermined stabilization | ✓ Validated in `v1.0` |
| Use a full-sweep discovery approach instead of a fixed bug list | The user was non-technical and wanted the project to learn what was wrong through structured analysis | ✓ Validated in `v1.0` |

---
*Last updated: 2026-03-20 after v1.0 milestone*
