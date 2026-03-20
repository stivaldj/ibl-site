# Planning State: VARIANT

**Initialized:** 2026-03-20
**Primary project reference:** `.planning/PROJECT.md`

## Current Focus

The current focus is the v1 production-hardening initiative for the existing VARIANT site. This is a brownfield stabilization effort, so work should prioritize fixing and verifying the current customer-facing experience, lead flow, SEO/content trust, and generation reliability before any non-essential additions.

Phase 1 is now complete. Plans `01-01` through `01-04` established entry-shell parity, generated-route browse safety, shared-runtime consistency, and generator-level contact-anchor alignment across the representative desktop and mobile browse journey.

## Current Phase

- **Current phase:** Phase 4 - Generation And Frontend Reliability Stabilization
- **Phase status:** Phase 3 is verified and complete. Phase 4 is the next queued execution target.
- **Roadmap status:** Phases 1 through 3 complete, Phase 4 queued

## Phase Queue Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 - Site Experience Stabilization | Completed | Plans 01 through 04 completed: homepage, generated browse surfaces, mobile entry, and generated CTA anchor behavior now share the approved `#captacao-lead` contract |
| Phase 2 - Lead Flow Hardening | Completed | Plans 02-01 through 02-04 delivered the local webhook harness, explicit submit-result states, truthful feedback, actionable `?ops=1` visibility, and the final contacted-lead SLA-risk fix plus proof across desktop, mobile, and product routes |
| Phase 3 - SEO And Content Trust Hardening | Completed | Plans 03-01 through 03-03 verified: generated routes now ship source-owned metadata, trustworthy machine content, and fallback-only runtime SEO behavior |
| Phase 4 - Generation And Frontend Reliability Stabilization | Queued | Hardens generator/runtime foundations after visible and trust-critical fixes are defined |
| Phase 5 - Launch Verification And Operations Gate | Queued | Final release gate after Phases 1 through 4 |

## Initialized Project Context

- **Core value:** Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.
- **Planning configuration:** `mode=yolo`, `depth=standard`, `parallelization=true`, `model_profile=quality`
- **Roadmap inputs used:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/config.json`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`
- **Primary launch risks:** visible UX defects, unreliable or opaque lead handling, runtime-dependent SEO, generated-content drift, stale assets or generation leftovers, and lack of a repeatable launch check
- **Scope rule:** only launch-critical additions are allowed, and only when required for production readiness

## Next Planning Action

Start the first incomplete Phase 4 plan, using the now-verified generator SEO baseline and content trust path as the stable input to frontend/runtime and generation-pipeline reliability work.

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
- Plan `02-02` completed on 2026-03-20.
- `main.js`, `webapp/main.js`, and `mobile/main.js` now build the same webhook payload contract and return explicit `success`, `skipped`, and `failure` submit states instead of the prior ambiguous boolean/skipped combination.
- Homepage feedback on `/` and `/mobile/` now exposes submit outcomes through `data-submit-state`, and representative browser verification confirmed a product-context payload on `/produtos/retroescavadeiras/580n/` with `uso`, `modelo`, `categoria`, `page_path`, `captured_at`, and `attribution`.
- Missing-webhook runs now emit `lead_submit_skipped`, while a 500-mode mock webhook still preserves the WhatsApp fallback but surfaces `data-submit-state=\"failure\"` and a `lead_submit_error` event with the HTTP status.
- Plan `02-03` completed on 2026-03-20.
- Homepage and product forms in `main.js`, `webapp/main.js`, and `mobile/main.js` now only claim success on real webhook success, keep skipped/failed values visible for retry/manual continuation, and still use the launch-approved WhatsApp fallback intentionally.
- The local `?ops=1` monitor now records `submission_status`, `contact_status`, `submit_reason`, `error_message`, and route/context details so submitted, skipped, failed, pending, and SLA-risk leads are visible during launch checks.
- Phase 2 browser verification now covers success, missing-webhook, and failure runs across `/`, `/mobile/`, and `/produtos/retroescavadeiras/580n/`, plus a 430px-wide parity sweep and explicit ops-mode success/failure/SLA-risk checks.
- Plan `02-04` completed on 2026-03-20.
- `runSlaCheck()` in `main.js`, `webapp/main.js`, and `mobile/main.js` now filters stale leads by `contact_status !== 'contacted'`, matching the existing ops record/update shape and removing the prior false-positive SLA-risk path for contacted leads.
- Focused `?ops=1` verification on `/`, `/mobile/`, and `/produtos/retroescavadeiras/580n/` now proves the submitted stale lead drops out of summary counts, console warnings, and `lead_sla_risk` telemetry immediately after the ops button marks it contacted, while a seeded stale uncontacted lead still keeps the legitimate warning path active.
- Plan `03-01` completed on 2026-03-20.
- `generate_pages.py` now owns canonical, description, Open Graph, Twitter, and JSON-LD output for generated catalog, category, and product routes, using `https://iblmaquinas.com.br` as the source HTML canonical host.
- Representative source inspection on `/produtos/`, `/produtos/retroescavadeiras/`, and `/produtos/retroescavadeiras/580n/` confirmed the shipped HTML now contains metadata and structured data before any runtime script executes.
- Plan `03-02` completed on 2026-03-20.
- `generate_pages.py` now strips zero-width spec-label artifacts, preserves markdown continuation lines in quick specs and technical spec values, and renders the final product CTA with the full model title instead of a brittle token split.
- Representative source-vs-output audits passed for `/produtos/retroescavadeiras/580n/`, `/produtos/escavadeiras-hidraulicas/cx220c-s2/`, `/produtos/escavadeiras-hidraulicas/cx240c-me/`, and `/produtos/minicarregadeiras/sr175b/`, confirming title, category, description, quick specs, and CTA context stay aligned with `scrape_db.json` and the matching `content.md`.
- Plan `03-03` completed on 2026-03-20.
- `main.js`, `webapp/main.js`, and `mobile/main.js` now treat generated-route SEO as source-owned when `/produtos/**` already ships description, canonical, social metadata, and breadcrumb schema in HTML, leaving runtime mutation only as fallback behavior.
- Final browser verification on `/produtos/`, `/produtos/retroescavadeiras/`, `/produtos/retroescavadeiras/580n/`, and `/produtos/escavadeiras-hidraulicas/cx240c-me/` confirmed the DOM keeps the same canonical/meta/schema state as the shipped HTML, with `FAQPage` added only as an intentional product-page supplement.
- Phase 3 verification completed on 2026-03-20.
- `03-VERIFICATION.md` passed with all four SEO requirements satisfied: generated pages now ship metadata and structured data directly in HTML, representative product content matches its source data, and generated-route runtime SEO behavior is fallback-only instead of primary.
- Plan `04-01` completed on 2026-03-20.
- `generate_pages.py` now sorts source assets, synchronizes copied public assets intentionally, preserves managed `*-nobg.png` derivatives, and keeps generated HTML stable across repeated reruns.
- `process_fotos.py`, `remove_bg_batch.py`, and `scrape_specs.py` now expose explicit refresh behavior through `--sync`, `--force`, `--dry-run`, and `--strict` instead of silently relying on stale outputs or partial-success exits.
- Plan `04-02` completed on 2026-03-20.
- `npm run build` now packages the full launch surface, including `produtos/**`, into `dist/`, and representative packaged routes no longer reference raw source `main.js` or `style.css` assets.
- The old Vite starter scaffold under `src/` is now explicitly quarantined through `src/README.md`, making the real production entrypoints unambiguous.
- Plan `04-03` completed on 2026-03-20.
- `docs/OPERATIONS.md` is now the authoritative rebuild guide, backed by package scripts for dry-run asset checks, catalog regeneration, final packaging, and `dist/` verification.
- The documented rebuild flow passed end-to-end: dry-run asset checks were clean, `npm run rebuild:site` regenerated the catalog, rebuilt `dist/`, and verified representative homepage, mobile, catalog, category, and product routes in the packaged artifact.

---
*Last updated: 2026-03-20 after completing Phase 4 plans 04-01 through 04-03*
