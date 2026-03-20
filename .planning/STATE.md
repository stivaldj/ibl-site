# Planning State: VARIANT

**Initialized:** 2026-03-20
**Primary project reference:** `.planning/PROJECT.md`

## Current Focus

The current focus is the v1 production-hardening initiative for the existing VARIANT site. This is a brownfield stabilization effort, so work should prioritize fixing and verifying the current customer-facing experience, lead flow, SEO/content trust, and generation reliability before any non-essential additions.

Plan `01-02` is now complete and establishes the generated catalog/category/product baseline for the rest of Phase 1.

## Current Phase

- **Current phase:** Phase 1 - Site Experience Stabilization
- **Phase status:** In progress - Plans 01 and 02 completed
- **Roadmap status:** Active execution

## Phase Queue Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 - Site Experience Stabilization | In progress | Plans 01 and 02 completed: entry shells and generated browse surfaces now share launch-safe CTA behavior and route-verification baselines |
| Phase 2 - Lead Flow Hardening | Queued | Starts after browsing experience is stable enough to validate conversions cleanly |
| Phase 3 - SEO And Content Trust Hardening | Queued | Depends on stabilized page behavior and launch-page audit baseline |
| Phase 4 - Generation And Frontend Reliability Stabilization | Queued | Hardens generator/runtime foundations after visible and trust-critical fixes are defined |
| Phase 5 - Launch Verification And Operations Gate | Queued | Final release gate after Phases 1 through 4 |

## Initialized Project Context

- **Core value:** Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.
- **Planning configuration:** `mode=yolo`, `depth=standard`, `parallelization=true`, `model_profile=quality`
- **Roadmap inputs used:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/config.json`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`
- **Primary launch risks:** visible UX defects, unreliable or opaque lead handling, runtime-dependent SEO, generated-content drift, stale assets or generation leftovers, and lack of a repeatable launch check
- **Scope rule:** only launch-critical additions are allowed, and only when required for production readiness

## Next Planning Action

Execute the next incomplete Phase 1 plan while preserving the generated-route baseline established by `01-02`.

## Execution Notes

- Plan `01-01` completed on 2026-03-20.
- Desktop `/` and mobile `/mobile/` now share the same launch-approved first-step CTA paths: `/produtos/` and `#captacao-lead`.
- Entry-shell unit coverage no longer depends on Leaflet/OpenStreetMap; a local summary panel keeps console and asset-request smoke checks clean.
- Plan `01-02` completed on 2026-03-20.
- Generated header/footer/chat affordances under `produtos/` now use real destinations or explicit non-interactive copy, and generated breadcrumbs are isolated under dedicated breadcrumb nav markup.
- Shared generated-page CSS now guards long titles, mobile CTA rows, wrapped footer actions, and floating chat sizing.
- Generated route verification should continue to use the local generated-page server; `vite preview` currently falls back to the app shell for `/produtos/**` even though `npm run build` passes.

---
*Last updated: 2026-03-20 after completing plan 01-02*
