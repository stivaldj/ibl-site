# Structure

## Top Level

The repository is organized around a static site plus the tools that generate and verify it.

- `index.html` is the main homepage entry
- `mobile/` contains the mobile-specific route
- `produtos/` contains generated catalog pages
- `public/` contains stable assets served as-is
- `scripts/` contains build and launch verification helpers
- `docs/` contains operational guidance
- `tasks/` contains milestone notes and planning artifacts
- `Scrape Case/` holds upstream scraped product data
- `src/` is intentionally not the live app source tree

## Primary Pages

- `index.html` is the desktop marketing homepage
- `mobile/index.html` is the mobile landing page
- `produtos/index.html` is the catalog landing page
- `produtos/escavadeiras-hidraulicas/index.html` and sibling folders are category pages
- `produtos/retroescavadeiras/580n/index.html` and sibling folders are product pages

## Generated Catalog Tree

The `produtos/` tree is generated and maintained by `generate_pages.py`.
Its shape mirrors the product taxonomy:

- `produtos/<category>/index.html`
- `produtos/<category>/<model>/index.html`

Representative categories currently include:

- `produtos/escavadeiras-hidraulicas/`
- `produtos/minicarregadeiras/`
- `produtos/miniescavadeiras/`
- `produtos/motoniveladoras/`
- `produtos/pas-carregadeiras/`
- `produtos/retroescavadeiras/`
- `produtos/rolo-compactador/`
- `produtos/tratores-de-esteiras/`

## Asset Layout

Static assets live under `public/` and are referenced directly by the HTML pages.

- `public/case-assets/**` stores model and category imagery
- `public/casece-logo.svg` and `public/ibl-logo.png` are the brand assets
- `public/favicon.ico` is the site favicon

The generated pages depend on these paths staying stable.

## Source And Tooling Files

- `main.js` and `webapp/main.js` contain the shared runtime behavior
- `mobile/main.js` mirrors the same runtime for the mobile route
- `style.css`, `webapp/style.css`, and `mobile/style.css` contain the shared visual system
- `tailwind.config.js` defines the Tailwind theme and content scan roots
- `vite.config.js` defines multi-entry packaging, including all generated product HTML
- `package.json` defines scripts for build, page generation, and launch checks

## Operational And Verification Files

- `docs/OPERATIONS.md` is the authoritative rebuild guide
- `docs/LAUNCH-READINESS.md` records the last verified launch gate
- `scripts/verify-dist.mjs` validates the packaged artifact
- `scripts/launch-gate-smoke.mjs` checks representative routes
- `scripts/launch-gate-lead.mjs` exercises lead submission flows
- `scripts/mock-lead-webhook.mjs` simulates webhook responses during gate runs

## Planning And History

- `.planning/STATE.md` records the current planning state
- `.planning/codebase/` now holds the refreshed codebase map
- `tasks/` contains historical sprint notes and design work from earlier phases

## Practical Notes

The repository is intentionally flat at runtime: the HTML files, shared scripts, and generated pages are the shipped product.
There is no long-lived application server in the repo; the important boundary is between source generators and packaged static output.
