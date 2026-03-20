# Phase 2 Research: Lead Flow Hardening

## Overview

Phase 2 is the production-safety pass for the lead path now that Phase 1 has stabilized browse and CTA routing. The critical flow is already present, but it is still mostly client-side behavior layered on top of a static site: homepage and mobile lead forms, product-context lead forms, WhatsApp fallbacks, browser analytics, and an optional webhook to `ibl-ai-os`.

The lead implementation is duplicated across three runtime entrypoints:

- `webapp/main.js` for the desktop homepage
- `mobile/main.js` for the mobile homepage
- `main.js` for generated catalog/category/product pages under `produtos/`

That duplication is the main planning constraint for this phase. Any hardening work has to be applied consistently across all three files or the desktop/mobile/product experiences will drift.

## Lead Surfaces In Scope

The actual customer-facing entry points are:

- Homepage lead form in `index.html` and `mobile/index.html`, anchored at `#captacao-lead`
- Homepage CTA links in `index.html` and `mobile/index.html` that jump to `#captacao-lead`
- Product-context lead form injected into generated product pages at `#produto-contato`
- Product sticky CTA injected by the runtime on product pages, which links to `#produto-contato`
- WhatsApp fallback links on the homepage and product pages
- Optional ops mode in the runtime, enabled with `?ops=1`, which shows the local lead monitor panel

Phase 2 should treat homepage and product-context lead capture as the production paths. The `#captacao-lead` anchor work from Phase 1 is already closed and should be treated as fixed infrastructure, not a new lead feature.

## Relevant Code And Current Lead Architecture

The main architecture facts that matter for planning:

- The repo has no backend service. Lead capture is browser-side only, with an optional webhook POST.
- `webapp/main.js`, `mobile/main.js`, and `main.js` all implement the same lead pipeline: attribution capture, analytics tracking, webhook submission, local ops storage, and WhatsApp fallback.
- `.env.example` documents the only relevant runtime variables for this phase: `VITE_GA4_ID`, `VITE_LEAD_WEBHOOK_URL`, and `VITE_LEAD_SLA_HOURS`.
- `.planning/codebase/INTEGRATIONS.md` confirms the webhook is optional and the ops panel is local-only.
- `.planning/codebase/CONCERNS.md` calls out the biggest trust risks: localStorage-based ops data, client-side webhook posting, and the lack of a retry queue or redaction layer.
- `.planning/codebase/TESTING.md` confirms there is no formal test suite, so verification has to be browser-driven.

The key implementation files to read as the source of truth are:

- `index.html`
- `mobile/index.html`
- `webapp/main.js`
- `mobile/main.js`
- `main.js`
- `.env.example`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/INTEGRATIONS.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/TESTING.md`
- `.planning/phases/01-site-experience-stabilization/01-04-SUMMARY.md`

## Current Payload And Integration Behavior

The webhook submission helper in all three runtimes is `submitLeadToWebhook()`. It builds the payload by merging caller-provided lead fields with:

- `page_path`: `window.location.pathname`
- `captured_at`: ISO timestamp from `new Date().toISOString()`
- `attribution`: data loaded from `localStorage`

The attribution blob currently includes:

- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_content`
- `utm_term`
- `referrer`
- `landing_page`

The homepage form submits these lead fields:

- `nome`
- `telefone`
- `interesse`
- `lead_type: 'home'`
- `lead_channel: 'form_whatsapp'`

The product-context form submits these lead fields:

- `nome`
- `telefone`
- `uso`
- `modelo`
- `categoria`
- `lead_type: 'product'`
- `lead_channel: 'product_form_whatsapp'`

The runtime also records the lead locally before webhook submission with `recordLeadOpsItem()`, which writes to `localStorage` under `ibl_lead_ops_v1`. The attribution data is stored separately under `ibl_attribution_v1`.

Telemetry already exists, but it is mostly client-side:

- `page_view_custom`
- `cta_click`
- `generate_lead`
- `lead_submit_attempt`
- `lead_submit_success`
- `lead_submit_error`
- `lead_sla_risk`

That means the plumbing for observability is present, but the current user-facing behavior does not depend on it.

## Likely Failure Modes And Observability Gaps

The most important current failure modes are not UI bugs, they are silent or ambiguous lead-loss modes:

- If `VITE_LEAD_WEBHOOK_URL` is missing, `submitLeadToWebhook()` returns `{ ok: false, skipped: true }` and the caller still continues to WhatsApp, so the user gets no visible indication that the webhook never fired.
- If the webhook returns a non-2xx response or the fetch throws, the code logs `lead_submit_error` and returns `{ ok: false, skipped: false }`, but the form flow still shows success text, opens WhatsApp, and resets the form.
- There is no retry queue, backoff, or offline recovery. A transient failure is effectively a lost webhook submission unless the browser/operator manually retries.
- The only operational visibility is the optional local `ops=1` panel and console logging. That does not help with shared production observability or post-factum diagnosis across devices.
- The ops panel and lead history are browser-profile local. Clearing storage, switching browsers, incognito mode, or a second device will lose that state.
- Because the runtime is duplicated across `webapp/main.js`, `mobile/main.js`, and `main.js`, any fix that lands in only one file will create a desktop/mobile/generated-page mismatch.
- The form UX is optimistic: it always moves to WhatsApp after attempting the webhook, even if the webhook failed. That may be acceptable as fallback behavior, but it is not currently honest about success.

## Recommended Audit / Fix Sequence

1. Confirm the exact opportunity-creation schema expected by `ibl-ai-os` before changing payload field names or dropping any fields.
2. Decide whether the webhook is the primary success criterion or whether WhatsApp remains the fallback path even when the webhook fails.
3. Change `submitLeadToWebhook()` so callers can distinguish success, skipped, and failed states and so the UI can respond accordingly.
4. Update homepage and product-form feedback so the message reflects actual webhook outcome instead of always saying the request was sent.
5. Mirror the same change in `webapp/main.js`, `mobile/main.js`, and `main.js` in one pass.
6. Re-run the phase on representative desktop, mobile, and generated product routes after each behavior change.

## Risks And Dependencies

- The `ibl-ai-os` webhook schema is not defined in this repo, so Phase 2 cannot assume which fields are required without external confirmation.
- `localStorage` is convenient for the ops panel, but it is not durable enough to be the only production detection path.
- If browser storage is blocked or cleared, attribution and ops history degrade silently.
- If WhatsApp stays as the fallback path, there is a product decision to make about whether fallback should happen on every submit attempt or only after confirmed webhook success.
- There is no automated test suite, so regressions in one of the three runtimes can easily slip through unless browser validation is explicit and repeated.
- The lead flow depends on client-side execution. If JavaScript fails, the forms render but do not submit anything.

## Validation Architecture

Validation for this phase should be browser-first and should verify both functional delivery and failure visibility.

- Build gate: run `npm run build` before any browser checks to catch syntax, import, or runtime bundling regressions.
- Desktop smoke: validate the homepage lead form on `/` and at least one generated product page under `/produtos/**` in a desktop viewport.
- Mobile smoke: repeat the same flow on `/mobile/` and at least one generated product page in a narrow viewport to confirm parity.
- Payload check: inspect the network request body for the webhook and confirm the emitted JSON includes the expected lead fields, `page_path`, `captured_at`, and `attribution`.
- Failure-path check: test with `VITE_LEAD_WEBHOOK_URL` unset and with a failing endpoint so the UI behavior, analytics, and console output are understood before implementation is approved.
- Ops-mode check: open the site with `?ops=1` and confirm the local lead panel reflects recorded items and SLA risk behavior.
- Telemetry check: confirm the expected events are emitted on submit attempt, success, failure, and CTA click.
- Parity check: run the same flow in `webapp/main.js`, `mobile/main.js`, and `main.js`-backed routes so no runtime diverges from the others.

The acceptance bar for this phase should be that a lead submission either clearly succeeds or clearly fails, the fallback path is intentional, and the team can prove what happened from browser evidence rather than assuming the webhook worked.

## Open Questions / Assumptions

- What exact fields does `ibl-ai-os` require to create an opportunity?
- Should WhatsApp open only after confirmed webhook success, or is it intentionally the fallback even when the webhook fails?
- Is the local `ops=1` panel sufficient operational visibility for launch, or does Phase 2 need a more durable logging path?
- Should webhook failures surface as an inline error, a warning state, or a hard stop before WhatsApp opens?
- Do we want lead capture to be available when `VITE_LEAD_WEBHOOK_URL` is unset, or should that be treated as a launch blocker in production?
