# VARIANT

## What This Is

`VARIANT` is a customer-facing CASE Construction / IBL Máquinas website focused on machine discovery, product evaluation, and lead generation. It combines a marketing homepage, category and product detail pages, and webhook-based lead capture that creates opportunities inside `ibl-ai-os`. This initiative is about turning the current vibecoded site into a production-grade system with a stable foundation for future milestones.

## Core Value

Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

## Requirements

### Validated

- ✓ Visitors can browse a CASE/IBL homepage experience with brand-specific messaging and CTAs — existing
- ✓ Visitors can navigate a generated product catalog by category and machine model — existing
- ✓ Visitors can open machine detail pages with specs, imagery, and product-specific lead CTAs — existing
- ✓ Visitors can submit or initiate lead flows that can trigger webhook delivery to `ibl-ai-os` when configured — existing
- ✓ The site can be built and served as a static frontend using Vite and generated catalog pages — existing

### Active

- [ ] Eliminate the most visible UI and UX defects across homepage, catalog, product pages, and mobile variants
- [ ] Make lead capture and webhook-triggered opportunity creation reliable, observable, and production-safe
- [ ] Correct SEO, metadata, content consistency, and trust issues that would weaken launch quality
- [ ] Reduce structural fragility in generation, assets, and frontend code so future milestones build on a stable base
- [ ] Add only the small set of must-have launch additions required for production readiness

### Out of Scope

- Large net-new feature expansion unrelated to launch readiness — the current priority is production hardening before the next milestone
- Major platform rewrites or a full-stack rebuild — the project should improve the current brownfield system, not restart it from zero
- Nice-to-have experiments that do not materially improve launch readiness, trust, or lead generation — they would dilute focus from production quality

## Context

The current site was developed quickly and without a structured engineering process. The result is a working but uneven brownfield codebase with visible UI and UX problems, content and SEO fragility, and maintainability concerns that need a full sweep before further planned feature phases continue.

The codebase map in `.planning/codebase/` shows a static-site-first architecture with multiple entry points, generated product pages, optional analytics, and webhook-based lead capture. It also highlights concrete risks around runtime SEO, inconsistent generated content, stale assets, and weak testing discipline.

The primary audience is prospective customers researching CASE machines, while the business outcome is lead generation for the IBL commercial flow. Production success depends both on customer trust and on reliable data handoff into `ibl-ai-os`.

The user is non-technical and cannot enumerate all defects in advance. That means this project must include systematic discovery, prioritization, and correction of issues rather than assuming a pre-defined bug list.

## Constraints

- **Tech stack**: Brownfield static frontend with generated catalog pages — improvements must work within the existing architecture unless a narrow structural change is clearly justified
- **Business flow**: Lead generation must continue to support webhook creation of opportunities in `ibl-ai-os` — this is core to the site's business value
- **Scope control**: Must prioritize hardening over expansion — only launch-critical additions belong in this initial roadmap
- **Quality bar**: The site must be trustworthy enough for production use — UI polish alone is insufficient without operational and content reliability
- **Discovery**: Defects are not fully enumerated upfront — the roadmap must include a real sweep for problems across UX, code, content, and operations

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat this as a production-hardening milestone, not a feature-first milestone | The current site needs stability and credibility before more feature work compounds existing issues | — Pending |
| Keep the site focused on both customer research and lead generation | The website must serve prospects while feeding commercial opportunity creation into `ibl-ai-os` | — Pending |
| Allow only small must-have additions in the first roadmap | Some launch-critical gaps may require additions, but broad expansion would undermine the stabilization effort | — Pending |
| Use a full-sweep discovery approach instead of a fixed bug list | The user is non-technical and wants the project to learn what is wrong through structured analysis | — Pending |

---
*Last updated: 2026-03-20 after initialization*
