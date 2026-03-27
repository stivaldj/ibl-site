# Code Conventions

## Overview

VARIANT is a static-site-first codebase with three runtime entrypoints:

- `main.js` for the desktop homepage and shared runtime behavior
- `webapp/main.js` for the alternate app-style surface
- `mobile/main.js` for the mobile entrypoint

The repo also has repo-local generators and maintenance scripts in `generate_pages.py`, `process_fotos.py`, `remove_bg_batch.py`, `scrape_specs.py`, and `scripts/*.mjs`.

## JavaScript Style

- The main runtime files use ESM imports, `const` for stable bindings, and function declarations for helpers.
- The site JS is mostly semicolon-free and uses single quotes in the runtime files, while Node scripts under `scripts/` are more mixed and include semicolons and double quotes in places.
- Guard clauses are common. Many helpers return early when a DOM node is missing or is not the expected element type.
- Optional chaining and nullish coalescing are used heavily to keep the DOM code resilient.
- Small pure helpers are preferred for state shaping and formatting, such as `createLeadSubmitResult()`, `escapeHtml()`, and `getLeadOpsSubmissionMeta()` in `main.js`.

## DOM And State Patterns

- The site uses direct DOM manipulation instead of a framework abstraction.
- State is stored in `window.localStorage`, `window.dataLayer`, custom events, and in-memory maps/sets.
- Event handlers are attached imperatively with `addEventListener`, usually after querying the required nodes.
- Dynamic UI is built with `document.createElement()` and `innerHTML` in controlled sections, but user-supplied content is escaped first with `escapeHtml()`.
- Runtime features rely on `dataset` attributes for state signaling, such as `data-submit-state` in lead flows.

## Content And Generation

- Generated product routes live under `produtos/**` and are produced by `generate_pages.py`.
- The generator and runtime scripts depend on stable file paths and route structure; these are not abstracted behind a shared routing layer.
- HTML is edited as a mix of source templates and generated output, so route-aware changes need to be checked in both the source generator and representative generated files.

## Styling Conventions

- Styling is split between `style.css`, `webapp/style.css`, and `mobile/style.css`.
- The CSS layer uses Tailwind v4 directives like `@import "tailwindcss";`, `@source`, and `@theme`.
- Design tokens are defined in CSS custom properties such as `--ds-bg-base`, `--ds-accent`, and `--ds-radius-md`.
- Visual style is industrial/dark-mode leaning, with custom accent colors and utility classes like `text-outline`, `industrial-border`, and `tech-grid`.

## Naming And Structure

- Uppercase constants are used for shared keys and status enums, for example `LEAD_OPS_STORAGE_KEY` and `LEAD_SUBMIT_STATUS`.
- Helper names are descriptive and action-oriented, especially around lead capture, telemetry, and SEO injection.
- The repo distinguishes between generated content, runtime scripts, and maintenance scripts by directory rather than by a formal module layer.

## Practical Examples

- Lead flow and telemetry logic: `main.js`, `webapp/main.js`, `mobile/main.js`
- Build and packaging config: `vite.config.js`, `tailwind.config.js`, `package.json`
- Generated content pipeline: `generate_pages.py`
- Local smoke and verification helpers: `scripts/launch-gate-smoke.mjs`, `scripts/launch-gate-lead.mjs`, `scripts/verify-dist.mjs`, `scripts/mock-lead-webhook.mjs`

## Unknowns

- There is no repo-wide lint configuration visible in the checked-in files.
- The codebase does not currently expose a shared component or state library; duplication across the three runtime entrypoints appears intentional.
