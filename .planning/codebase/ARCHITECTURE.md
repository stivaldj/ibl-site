# VARIANT Architecture Map

## Overview
`VARIANT` is a static-site-first frontend for IBL Máquinas / CASE Construction with three live browser entry surfaces, a generated product catalog, and a content pipeline that turns scraped machine data into production HTML.

## Runtime layers
- Desktop home shell: `index.html` loads `/webapp/main.js` and `webapp/style.css`.
- Mobile shell: `mobile/index.html` loads `/mobile/main.js` and `mobile/style.css`.
- Generated catalog pages: `produtos/**/*.html` load `/main.js` and `style.css`.
- Shared behavior is duplicated across `main.js`, `webapp/main.js`, and `mobile/main.js` so generated pages, the desktop shell, and the mobile shell can share lead handling, catalog tools, and SEO fallback logic.

## Entry points and page ownership
- `index.html` is the desktop landing page and the primary browser shell.
- `mobile/index.html` is the mobile-optimized landing page.
- `produtos/index.html`, `produtos/<category>/index.html`, and `produtos/<category>/<model>/index.html` are generated from scraped content and act as the product browsing surface.
- `vite.config.js` builds `index.html`, `mobile/index.html`, and every generated `produtos/**/*.html` file as first-class inputs.

## Content and generation flow
- Scraped source content lives under `Scrape Case/`, especially `Scrape Case/scrape_db.json` and the per-model `content.md` files under `Scrape Case/pt-br/southamerica/produtos/**/`.
- `scrape_specs.py` refreshes the scraped corpus and the catalog index.
- `generate_pages.py` reads `Scrape Case/scrape_db.json` plus each model `content.md`, then writes the full static catalog tree into `produtos/`.
- The generator also copies model-local assets into `public/case-assets/<category>/<model>/` and emits launch-facing metadata and structured data directly into the generated HTML.

## Asset pipeline
- Raw photo input starts in `fotos/`.
- `process_fotos.py` converts and syncs photo derivatives into `public/case-assets/fotos-processed/`.
- `remove_bg_batch.py` manages transparent model assets and other generated derivatives under `public/case-assets/**`.
- `public/` is the deployable static asset root for branding files like `public/ibl-logo.png`, `public/casece-logo.svg`, and the generated case asset tree.

## SEO and source HTML ownership
- Generated category and product pages own their final metadata, canonical tags, Open Graph tags, Twitter tags, and JSON-LD in the HTML source itself.
- `main.js`, `webapp/main.js`, and `mobile/main.js` only act as fallback or enhancement layers on generated routes when the generator has not already provided the baseline.
- The current SEO contract treats `produtos/` as the source of truth for machine pages instead of relying on client-side metadata injection.

## Lead flow architecture
- Lead submission logic is implemented in the shared runtime helpers inside `main.js`, `webapp/main.js`, and `mobile/main.js`.
- The shared flow builds webhook payloads, submits them to `VITE_LEAD_WEBHOOK_URL`, records local ops state, and reflects success or failure in the UI.
- `scripts/mock-lead-webhook.mjs` provides a repo-local webhook target for success and failure verification.
- `scripts/launch-gate-lead.mjs` exercises homepage, mobile, and product lead flows against the local runtime.

## Build and packaging flow
- `npm run generate:pages` runs `generate_pages.py`.
- `npm run build:site` runs `vite build`.
- `npm run rebuild:site` runs generation, build, and `scripts/verify-dist.mjs`.
- `scripts/verify-dist.mjs` checks representative packaged routes in `dist/` for built asset references and absence of raw source runtime links.
- `dist/` is the release artifact and is treated as generated output, not hand-edited source.

## Launch gate and operations flow
- `docs/OPERATIONS.md` is the authoritative rebuild guide.
- `docs/LAUNCH-GATE.md` defines the formal release gate and its evidence location.
- `docs/LAUNCH-READINESS.md` records the most recent executed gate and final readiness verdict.
- `scripts/launch-gate-smoke.mjs` validates representative packaged routes.
- `scripts/launch-gate-lead.mjs` validates lead success and failure modes.

## Important directories
- `produtos/` contains generated catalog, category, and product HTML.
- `public/` contains deployable assets and generated case imagery.
- `Scrape Case/` contains the scraped source corpus and the machine-readable content index.
- `scripts/` contains the verification and gate runners.
- `docs/` contains the operational contract for rebuild and launch readiness.
- `.planning/` contains roadmap, requirements, phase verification, and the codebase maps created for planning.
- `tasks/` is historical sprint material and reference context, not a live runtime layer.

## Practical constraints
- The codebase has intentional duplication across `main.js`, `webapp/main.js`, and `mobile/main.js`; that keeps shells isolated but raises drift risk.
- Tailwind scanning must include generated HTML like `produtos/**/*.html` so page-only classes survive the build.
- The catalog tree in `produtos/` is regenerated from `Scrape Case/` inputs and should be treated as derived output.
- The release workflow depends on the generated HTML, the runtime scripts, and the build artifact all staying in sync.
