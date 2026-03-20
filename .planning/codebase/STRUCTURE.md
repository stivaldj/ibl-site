# VARIANT Repository Structure

## Top-level map
The repository is organized around live entry pages, generated catalog output, source content, deployable assets, scripts, and planning docs.

## Live entry surfaces
- `index.html` is the desktop entry shell.
- `mobile/index.html` is the mobile entry shell.
- `main.js` is the shared runtime for generated catalog/category/product pages under `produtos/`.
- `webapp/main.js` and `webapp/style.css` power the desktop home experience.
- `mobile/main.js` and `mobile/style.css` power the mobile home experience.
- `style.css` is the shared base stylesheet used by generated pages and the Vite build context.

## Generated site tree
- `produtos/` is the generated static catalog tree.
- `produtos/index.html` is the catalog landing page.
- `produtos/<category>/index.html` is a generated category page such as `produtos/retroescavadeiras/index.html`.
- `produtos/<category>/<model>/index.html` is a generated product page such as `produtos/retroescavadeiras/580n/index.html`.
- The `produtos/` tree is derived from the scraper corpus and should be regenerated rather than hand-edited.

## Source content and asset inputs
- `Scrape Case/scrape_db.json` is the catalog index used by page generation.
- `Scrape Case/pt-br/southamerica/**/content.md` contains the structured machine content used to build each product page.
- `Scrape Case/pt-br/southamerica/**/assets/` holds source assets copied into the public asset tree.
- `fotos/` contains raw photo inputs for derivative generation.
- `public/` is the static deploy asset root and contains branding files plus generated case assets.

## Generation and transform scripts
- `generate_pages.py` turns the scraped data into `produtos/**` HTML and copies the related assets into `public/case-assets/**`.
- `process_fotos.py` transforms raw photos into processed assets under `public/case-assets/fotos-processed/`.
- `remove_bg_batch.py` manages transparent image derivatives and synchronization of generated assets.
- `scrape_specs.py` refreshes the scraped CASE source corpus and the `scrape_db.json` index.

## Build, verification, and launch tooling
- `vite.config.js` registers the root home page, mobile page, and all generated `produtos/**/*.html` files as build inputs.
- `package.json` defines the primary commands: `generate:pages`, `build:site`, `rebuild:site`, `verify:dist`, `launch:gate:smoke`, `launch:gate:lead`, and `lead:webhook:mock`.
- `scripts/verify-dist.mjs` verifies the built `dist/` artifact.
- `scripts/launch-gate-smoke.mjs` checks representative packaged routes.
- `scripts/launch-gate-lead.mjs` checks homepage, mobile, and product lead flows.
- `scripts/mock-lead-webhook.mjs` provides the local webhook harness used during gate runs.

## Build output and release artifacts
- `dist/` is the packaged release artifact produced by Vite.
- `dist/index.html`, `dist/mobile/index.html`, and `dist/produtos/**/index.html` are the shipped HTML outputs.
- `dist/assets/` contains bundled JS and CSS assets referenced by the packaged pages.

## Planning and operations docs
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` define milestone scope and requirement coverage.
- `.planning/phases/**/` holds phase plans, summaries, and verification evidence.
- `.planning/codebase/` stores the repository maps and related planning docs.
- `docs/OPERATIONS.md` is the authoritative rebuild guide.
- `docs/LAUNCH-GATE.md` is the formal release gate.
- `docs/LAUNCH-READINESS.md` records the latest gate verdict and evidence.

## Historical and supporting areas
- `tasks/` contains historical sprint notes and backlog-style context.
- `src/` is the old Vite starter scaffold and is not a live entry point.
- `WORKING.md` and `PROJECT_ANALYSIS.md` are legacy reference notes.
- `.tmp/` stores gate evidence and other ephemeral runtime artifacts.
- `node_modules/` is local dependency state only and should not be treated as source.

## How data moves through the repo
- Scraped CASE data starts in `Scrape Case/`.
- `generate_pages.py` converts that data into `produtos/` HTML and copies assets into `public/case-assets/**`.
- `vite build` packages the live entries and generated catalog into `dist/`.
- The launch gate reads from `dist/` and from the runtime helpers in `scripts/`.

## Where to make changes
- Home page copy or behavior: `index.html` and `webapp/`.
- Mobile behavior: `mobile/`.
- Catalog/product templates: `generate_pages.py`.
- Scraped source shape: `scrape_specs.py`.
- Image processing: `process_fotos.py` and `remove_bg_batch.py`.
- Build behavior: `vite.config.js`, `package.json`, and `scripts/`.
- Operational policy: `docs/`.

## Directory-level conventions
- Category slugs use kebab-case, for example `produtos/retroescavadeiras/` and `produtos/escavadeiras-hidraulicas/`.
- Product pages are one level deeper under the model slug, for example `produtos/retroescavadeiras/580n/`.
- Processed derivative files commonly use the `-nobg.png` suffix.
- Generated assets live under `public/case-assets/<category>/<model>/`.
