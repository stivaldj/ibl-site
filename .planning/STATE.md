# Planning State: VARIANT

**Initialized:** 2026-03-20
**Primary project reference:** `.planning/PROJECT.md`

## Current Focus

The current focus is the v1 production-hardening initiative for the existing VARIANT site. This is a brownfield stabilization effort, so work should prioritize fixing and verifying the current customer-facing experience, lead flow, SEO/content trust, and generation reliability before any non-essential additions.

Phase 1 is now complete. Plans `01-01` through `01-04` established entry-shell parity, generated-route browse safety, shared-runtime consistency, and generator-level contact-anchor alignment across the representative desktop and mobile browse journey.

## Current Phase

- **Current phase:** Phase 2 - Lead Flow Hardening
- **Phase status:** In progress after plan 02-01 established the local webhook verification harness
- **Roadmap status:** Active execution

## Phase Queue Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 - Site Experience Stabilization | Completed | Plans 01 through 04 completed: homepage, generated browse surfaces, mobile entry, and generated CTA anchor behavior now share the approved `#captacao-lead` contract |
| Phase 2 - Lead Flow Hardening | In progress | Plan 02-01 completed a repo-local webhook harness and env wiring, so payload and failure-path checks no longer depend on an external endpoint |
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

Execute the next incomplete Phase 2 plan using the repo-local webhook harness (`npm run lead:webhook:mock`) and the documented local `VITE_LEAD_WEBHOOK_URL` target for payload and failure-path verification.

## Execution Notes

- Plan `01-01` completed on 2026-03-20.
- Desktop `/` and mobile `/mobile/` now share the same launch-approved first-step CTA paths: `/produtos/` and `#captacao-lead`.
- Entry-shell unit coverage no longer depends on Leaflet/OpenStreetMap; a local summary panel keeps console and asset-request smoke checks clean.
- Plan `01-02` completed on 2026-03-20.
- Generated header/footer/chat affordances under `produtos/` now use real destinations or explicit non-interactive copy, and generated breadcrumbs are isolated under dedicated breadcrumb nav markup.
- Shared generated-page CSS now guards long titles, mobile CTA rows, wrapped footer actions, and floating chat sizing.
- Plan `01-03` completed on 2026-03-20.
- Shared browse-runtime behavior across `main.js`, `webapp/main.js`, and `mobile/main.js` now aligns for delegated CTA tracking, breadcrumb schema targeting, and the unit-summary behavior that remained stale in `main.js`.
- Plan `01-04` completed on 2026-03-20.
- Generated catalog/category/product contact CTAs now resolve to `/#captacao-lead` from one generator source, and sampled clicks from `/produtos/`, `/produtos/retroescavadeiras/`, and `/produtos/retroescavadeiras/580n/` land on the homepage lead section correctly.
- Final representative route verification passed on desktop and mobile for `/`, `/mobile/`, `/produtos/`, `/produtos/retroescavadeiras/`, and `/produtos/retroescavadeiras/580n/` with clean console and network results.
- Generated-route runtime verification should use the local Vite dev server for source-module execution; `vite preview` still falls back to the app shell for `/produtos/**`, and a raw static server exposes the HTML but not the CSS-importing runtime modules.
- Plan `02-01` completed on 2026-03-20.
- Phase 2 now has a repo-local mock webhook harness at `scripts/mock-lead-webhook.mjs` with success mode on `127.0.0.1:8787/lead`, failure mode available via `--mode failure --port 8788`, and optional payload persistence through `--capture-file`.
- Local lead verification should default `VITE_LEAD_WEBHOOK_URL` to `http://127.0.0.1:8787/lead` and start the harness with `npm run lead:webhook:mock` before browser checks so payload inspection and failure reproduction do not depend on `ibl-ai-os`.

---
*Last updated: 2026-03-20 after completing plan 02-01*
