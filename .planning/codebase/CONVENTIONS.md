# Codebase Conventions Map

## Repository Shape
- The live site is a Vite-built static site rooted in `index.html`, `mobile/index.html`, and generated HTML under `produtos/**/index.html`.
- `vite.config.js` dynamically includes every HTML file under `produtos/` as a build entry, so generated route files are first-class build inputs rather than post-build copies.
- `dist/` is the packaged launch artifact, but the editable source-of-truth for content pages remains the checked-in HTML under `produtos/` plus the generator in `generate_pages.py`.
- `src/README.md` exists specifically to quarantine the old scaffolded Vite starter. Treat `src/` as historical noise, not an active app surface.

## JavaScript Style
- Browser logic is plain ES modules with top-level `import './style.css'` in `main.js`, `mobile/main.js`, and `webapp/main.js`.
- Semicolons are generally omitted in frontend files. Object literals and constants are formatted with trailing commas used sparingly; the dominant style is compact and manual.
- Shared constants use `UPPER_SNAKE_CASE`, for example `ANALYTICS_MILESTONES`, `ATTRIBUTION_STORAGE_KEY`, and `LEAD_OPS_STORAGE_KEY` in `main.js`.
- Most behavior is organized as small named functions declared with `function`, not classes or framework components.
- DOM behavior is imperative: `document.querySelector`, `dataset`, `classList`, `localStorage`, and `window` globals are the core API surface.
- Frontend code leans on `import.meta.env` for environment wiring, especially `VITE_GA4_ID` and `VITE_LEAD_WEBHOOK_URL`.

## Duplication Hotspots
- `main.js`, `mobile/main.js`, and `webapp/main.js` are near-parallel runtime copies. When lead logic, analytics, attribution, or ops-state behavior changes in one, assume the same audit is needed in the other two.
- `style.css`, `mobile/style.css`, and `webapp/style.css` repeat the same brand-token and utility-extension pattern, with only surface-specific differences layered on top.
- Lead-flow contracts are intentionally mirrored across the runtime copies, including `data-submit-state`, webhook payload shape, and `ibl_lead_ops_v1` localStorage usage.
- Launch verification scripts in `scripts/launch-gate-smoke.mjs`, `scripts/launch-gate-lead.mjs`, and `scripts/verify-dist.mjs` encode representative route assumptions directly. Those scripts are another maintenance seam when routes or selectors change.

## Naming And Content Patterns
- Product and category routes use lowercase slug directories such as `produtos/retroescavadeiras/` and `produtos/retroescavadeiras/580n/`.
- Asset paths are site-root absolute paths like `/assets/...`, `/case-assets/...`, `/ibl-logo.png`, and `/casece-logo.svg`.
- Processed transparent machine images use the `-nobg.png` suffix under `public/case-assets/**`.
- Planning and operational filenames are explicit and phase-oriented, for example `.planning/phases/05-launch-verification-and-operations-gate/05-02-PLAN.md`.

## Styling Conventions
- Tailwind v4 drives styling through CSS entry files, not a component framework. `style.css` declares `@import "tailwindcss";`, `@source` directives, and `@theme` variables.
- Brand and design-system tokens are split between Tailwind theme variables such as `--color-case-yellow` and site-level CSS custom properties such as `--ds-accent` in `style.css`.
- HTML templates use long utility-class strings directly in markup. There is little abstraction beyond reusable CSS classes like `.industrial-border`, `.hero-circle-glow`, and `.text-outline`.
- Visual language is consistent across surfaces: dark backgrounds, CASE orange accents, bold uppercase headings, industrial borders, and hover-glow effects.

## Generation And Script Conventions
- `generate_pages.py`, `process_fotos.py`, `remove_bg_batch.py`, and `scrape_specs.py` are script-style Python entrypoints rather than reusable packages.
- Those scripts prefer explicit filesystem constants and top-level orchestration over deep abstraction.
- Operational Node scripts under `scripts/*.mjs` are also single-purpose CLIs with local `parseArgs()` helpers and direct `console.error` / `process.exit(1)` failure paths.
- The repo favors executable scripts over test frameworks for verification and maintenance.

## Operational Conventions
- `docs/OPERATIONS.md` is the authoritative rebuild document. If it conflicts with older notes like `WORKING.md` or `PROJECT_ANALYSIS.md`, the operations doc wins.
- `docs/LAUNCH-GATE.md` is the canonical release-check definition. The scripts in `scripts/` are expected to match its pass criteria closely.
- `.tmp/launch-gate/latest/` is the durable evidence location for launch-gate output, while `.playwright-cli/` holds older exploratory browser artifacts.
- The repo treats `?ops=1` as a real operator surface for inspecting lead status and SLA state, not just a local debug trick.

## Practical Editing Guidance
- Before changing route markup or selectors, inspect both the source HTML and the launch-gate scripts because selectors are asserted in `scripts/launch-gate-lead.mjs`.
- Before changing generated product/category structure, inspect both `generate_pages.py` and representative files under `produtos/**` because generated HTML is committed and packaged.
- Before changing lead-flow wording or state names, check all three runtime copies and the launch-readiness docs because the strings and dataset values are part of the verification contract.
- Assume drift risk is highest where the repo mirrors behavior manually instead of importing shared modules.
