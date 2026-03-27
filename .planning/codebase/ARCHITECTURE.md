# Architecture

## System Shape

VARIANT is a static, multi-entry marketing and catalog site built with Vite and Tailwind CSS.
The live surface is split across three entry families:

- the homepage in `index.html`
- the mobile landing shell in `mobile/index.html`
- the generated catalog tree under `produtos/**/*.html`

## Runtime Model

The site is mostly client-rendered behavior on top of prebuilt HTML.
The shared browser logic lives in:

- `main.js`
- `webapp/main.js`
- `mobile/main.js`

These files implement analytics, lead capture, local lead ops state, WhatsApp handoff, and scroll/click tracking.
The HTML pages import one of those runtime bundles directly with `<script type="module">`.

## Build Flow

The build pipeline is route-driven rather than component-driven.

1. `generate_pages.py` reads `Scrape Case/scrape_db.json`
2. It writes static product and category pages into `produtos/`
3. `vite.config.js` collects every HTML file under `produtos/` as a build input
4. `npm run build:site` packages the site into `dist/`
5. `scripts/verify-dist.mjs` checks that representative routes were packaged correctly

This means the catalog pages are source artifacts, not runtime-generated views.

## Content And Data Flow

The catalog content flows from scraped content and local assets into generated HTML.

- product metadata is parsed in `generate_pages.py`
- images are served from `public/case-assets/**`
- homepage and product pages link into the same catalog hierarchy
- lead forms post to `VITE_LEAD_WEBHOOK_URL` when configured
- attribution is stored in `localStorage` under `ibl_attribution_v1`

## Shared UI System

The visual language is centralized in Tailwind config and the global CSS entrypoints:

- `tailwind.config.js`
- `style.css`
- `webapp/style.css`
- `mobile/style.css`

These define the CASE brand palette, fonts, grid backgrounds, and motion utilities used by the homepage, mobile shell, and generated catalog pages.

## Entry Points

The important browser entrypoints are:

- `index.html` for the desktop homepage
- `mobile/index.html` for the mobile landing route
- `produtos/index.html` for the catalog index
- `produtos/<category>/index.html` for category pages
- `produtos/<category>/<model>/index.html` for product pages

## External Integrations

The app integrates with a small set of external services:

- Google Analytics via `VITE_GA4_ID`
- a lead webhook via `VITE_LEAD_WEBHOOK_URL`
- WhatsApp handoff links generated in `generate_pages.py` and the browser runtime
- remote icon/font/CDN assets from Phosphor Icons and Google Fonts

## Notable Uncertainties

I could not confirm whether `main.js` and `webapp/main.js` are intentionally duplicated or whether one is a legacy copy.
Both are referenced by checked-in HTML, so the architecture should treat them as independently shipped entrypoints until that is cleaned up.
