# Overview
This repo is a static-first Vite site for IBL Máquinas / CASE Construction.
The live browser entrypoints are `index.html`, `mobile/index.html`, and the generated catalog pages under `produtos/**/*.html`.
The active JS runtimes are `webapp/main.js`, `mobile/main.js`, and the root `main.js` used by generated pages.

# Runtime entrypoints
- `index.html` loads `/webapp/main.js` and is the desktop home shell.
- `mobile/index.html` loads `/mobile/main.js` and is the mobile home shell.
- `produtos/**/*.html` is generated content and still loads `/main.js` plus `/style.css`.
- `main.js` at the repo root is not a demo stub; it mirrors the shared browser runtime for generated pages.

# Build and bundling
- `vite.config.js` defines the build with `index.html`, `mobile/index.html`, and every `produtos/**/*.html` file as inputs.
- `package.json` wires `npm run dev`, `npm run build`, `npm run build:site`, and `npm run preview` to Vite.
- `scripts/verify-dist.mjs` checks the packaged `dist/` output for the expected routes and asset references.
- `dist/` is the build artifact; it is generated, not hand-edited.

# Frontend stack
- `package.json` declares `vite`, `@tailwindcss/vite`, `tailwindcss`, `postcss`, `autoprefixer`, and `playwright`.
- `tailwind.config.js` is still present and carries shared theme tokens, animation names, and content globs.
- `webapp/style.css`, `mobile/style.css`, and the root `style.css` are the active Tailwind v4 stylesheets.
- `index.html` and `mobile/index.html` also pull in Phosphor icons and Google Fonts from CDNs.

# Content and generation pipeline
- `generate_pages.py` builds the static catalog under `produtos/` from `Scrape Case/scrape_db.json`.
- `scrape_specs.py` scrapes CASE Sitecore pages into enriched `content.md` files under `Scrape Case/pt-br/southamerica/produtos/...`.
- `process_fotos.py` generates cleaned hero images into `public/case-assets/fotos-processed/`.
- `remove_bg_batch.py` generates selected `*-nobg.png` files into `public/case-assets/...`.
- `src/README.md` documents that the original Vite starter scaffold is no longer part of the live site.

# Scripts worth knowing
- `npm run generate:pages` refreshes the static HTML catalog.
- `npm run assets:photos:sync` and `npm run assets:nobg:sync` refresh image derivatives.
- `npm run scrape:specs` refreshes the scraped model spec markdown.
- `npm run rebuild:site` runs generation, build, and packaged-output verification in one chain.
- `npm run launch:gate:smoke` and `npm run launch:gate:lead` are browser-based checks for packaged routes and lead handling.
- `npm run lead:webhook:mock` starts the local webhook stub used for lead flow verification.

# Styling and assets
- The site sources are mixed between root-level HTML, `webapp/`, `mobile/`, and generated product pages.
- Static assets live in `public/`, `fotos/`, `fotos/svg/`, and the generated `public/case-assets/` tree.
- The catalog content and assets are highly file-driven; the HTML pages are mostly generated from scraped model data and local images.

# Practical notes
- The repo has both root-level and `webapp/` / `mobile/` runtimes, so changes often need to be mirrored deliberately.
- `src/main.js` and `src/counter.js` exist as leftover starter files, but they are not part of the current site shell.
- Python tooling assumes local installs of `Pillow`, `numpy`, `rembg`, `beautifulsoup4`, and `scrapling`; those are not declared in `package.json`.
