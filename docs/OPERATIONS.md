# VARIANT Operations

This is the authoritative rebuild and packaging guide for the production-hardened site.

If this file disagrees with older notes such as `WORKING.md` or `PROJECT_ANALYSIS.md`, follow this file.

## What Counts As Launchable

The launch artifact is `dist/`.

A rebuild is only considered complete when all of these exist and pass verification:

- `dist/index.html`
- `dist/mobile/index.html`
- `dist/produtos/index.html`
- representative category routes under `dist/produtos/**/index.html`
- representative product routes under `dist/produtos/**/**/index.html`
- built JS and CSS assets under `dist/assets/`

## Prerequisites

- Node dependencies installed with `npm install`
- Python 3 available as `python3`
- Optional for upstream refreshes:
  - `rembg` for real image background removal
  - scraper dependencies used by `scrape_specs.py`

The launch rebuild path below works from the checked-in source inputs already present in this repo. Upstream refresh commands are only needed when content or source images must be re-fetched or regenerated.

## Standard Launch Rebuild

Run these commands from `/Users/joseoliveira/CODING/VARIANT`:

```bash
npm run assets:photos:check
npm run assets:nobg:check
npm run rebuild:site
```

What each command does:

- `npm run assets:photos:check`
  - dry-run check for `fotos/ -> public/case-assets/fotos-processed/`
  - also removes nothing from disk; it only reports whether outputs are stale or orphaned
- `npm run assets:nobg:check`
  - dry-run check for curated `*-nobg.png` derivatives under `public/case-assets/**`
- `npm run rebuild:site`
  - regenerates `produtos/**` from the current repo inputs
  - runs the Vite package build
  - verifies representative packaged routes and built assets inside `dist/`

## Upstream Refresh Workflow

Use this only when the underlying source data or source images changed.

### 1. Refresh scraped CASE content

```bash
npm run scrape:specs
```

Equivalent raw command:

```bash
python3 scrape_specs.py --strict
```

### 2. Refresh processed local photos

```bash
npm run assets:photos:sync
```

Use `python3 process_fotos.py --sync --force` when you need a full rebuild regardless of timestamps.

### 3. Refresh curated transparent derivatives

```bash
npm run assets:nobg:sync
```

Use `python3 remove_bg_batch.py --sync --force` when you need a full rebuild regardless of timestamps.

### 4. Refresh the Dynapac catalog (national site)

The Dynapac catalog mirrors the Brazilian site, `dynapac.com/br-pt`. Its
"Produtos" tab hides everything flagged `data-discontinued="true"`
("Interrompido"), so only active models are mirrored. Mesas/screeds are
intentionally excluded: they are paver attachments, not catalog machines.

```bash
npm run dynapac:sync
```

Equivalent raw commands:

```bash
python3 scripts/dynapac-scrape-nacional.py
python3 scripts/dynapac-download-fotos.py
npm run rebuild:site
```

Notes:

- The scraper caches every fetched page under `.tmp/dynapac-br/`. Re-run it with
  `--offline` to rebuild `data/dynapac-db.json` from that cache without touching
  the network. Delete the cache to force a real refresh.
- The photo downloader is idempotent: it skips models that already have a file
  under `fotos-dynapac/`. Use `--force` to re-fetch everything.
- Each model carries fallback image URLs. Dynapac serves photos from two CDNs
  (`pdf.dynapac.com` and `pim.dynapac.com`) and several `/Full/` gallery links
  are dead, so the downloader tries the candidates in order.
- `generate_pages.py` prunes `dynapac/**` pages and `public/dynapac-assets/**`
  images for models that left the catalog. A model discontinued upstream
  disappears from the build on the next rebuild.

### 5. Rebuild the launch artifact

```bash
npm run rebuild:site
```

## Verification Contract

`npm run verify:dist` checks the production artifact for:

- presence of representative homepage, mobile, catalog, category, and product routes
- built JS and CSS asset references in packaged HTML
- absence of raw `/main.js`, `/mobile/main.js`, `/style.css`, and `/mobile/style.css` references in the representative packaged routes

## Bounded Remainder

These items remain explicit but non-blocking after Phase 4:

- Real image regeneration still depends on optional Python packages such as `rembg`; without them, dry-run and sync inspection still work, but actual image rewriting does not.
- `scrape_specs.py` depends on external site availability and scraper runtime dependencies; Phase 4 makes failures explicit with `--strict`, but it does not eliminate upstream network volatility.
- The repo still contains historical notes from pre-hardening analysis, but they are now non-authoritative and point back here.
