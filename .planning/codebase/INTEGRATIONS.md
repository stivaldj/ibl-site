# Overview
The repo has no backend service, auth system, payment gateway, or database integration.
The actual integrations are browser-delivered analytics, a configurable lead webhook, WhatsApp handoff links, and a Leaflet/OpenStreetMap map.
Most of the external surface area is in `webapp/main.js`, `mobile/main.js`, `index.html`, `mobile/index.html`, and generated `produtos/**/*.html` pages.

# Analytics and tracking
- `VITE_GA4_ID` in `.env.example` enables Google Analytics 4.
- `webapp/main.js` and `mobile/main.js` inject `https://www.googletagmanager.com/gtag/js?id=...` only when the env var is present.
- Lead and CTA events are pushed into `window.dataLayer` and mirrored to `window.gtag(...)` when available.
- Attribution is stored locally in `localStorage` under `ibl_attribution_v1`; there is no server-side attribution store.

# Lead capture
- `VITE_LEAD_WEBHOOK_URL` in `.env.example` controls the lead handoff endpoint.
- `submitLeadToWebhook()` in `webapp/main.js` and `mobile/main.js` POSTs JSON with the lead payload, `page_path`, `captured_at`, and attribution data.
- When the webhook is missing, the runtime marks the attempt as skipped and falls back to WhatsApp.
- The local operations cache lives in `localStorage` under `ibl_lead_ops_v1`.

# Lead test harness
- `scripts/mock-lead-webhook.mjs` is the local webhook stub used to capture and replay lead payloads.
- It listens on `127.0.0.1:8787` by default and accepts `POST /lead`.
- `scripts/launch-gate-lead.mjs` opens desktop, mobile, and product pages in Playwright, submits forms, and verifies the WhatsApp handoff.
- `scripts/launch-gate-smoke.mjs` checks representative packaged routes for raw source refs and missing built assets.

# Map and outbound links
- `webapp/main.js` and `mobile/main.js` use Google Maps search links for unit locations.
- The desktop/home shell also uses Leaflet with OpenStreetMap tiles, loaded from `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`.
- WhatsApp is the primary contact channel, with many `https://wa.me/5567999999999?...` links in `index.html`, `mobile/index.html`, `webapp/main.js`, `mobile/main.js`, and `generate_pages.py`.
- There is no other CRM SDK in the tree; the webhook is the only programmable lead sink.

# Third-party browser assets
- Phosphor icons are loaded from `https://unpkg.com/@phosphor-icons/web` in the HTML shells and in generated pages.
- Fonts are loaded from Google Fonts via `fonts.googleapis.com` and `fonts.gstatic.com` in `index.html`, `mobile/index.html`, and `generate_pages.py`.
- The page shells also rely on browser-loaded CSS and scripts; there is no npm package for icons or fonts.

# Internal content/data integrations
- `generate_pages.py` reads `Scrape Case/scrape_db.json` and local `Scrape Case/pt-br/southamerica/...` content.
- `scrape_specs.py` reaches out to `https://www.casece.com` to refresh product specs from Sitecore HTML.
- `process_fotos.py` and `remove_bg_batch.py` depend on `rembg` to create the transparent image derivatives served from `public/case-assets/`.
- The generated catalog pages link back into the same static site, not to an external CMS runtime.

# What is not integrated
- No email provider, SMS provider, push notification system, or file-upload service is present.
- No OAuth, login, session management, or user profile system is present.
- No CI/CD provider config was found in this repo (`.github/workflows`, `vercel.json`, `netlify.toml`, `Dockerfile`, and compose files are absent).
