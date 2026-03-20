# Testing And Verification Map

## Current Testing Posture
- This repository does not have a conventional automated test suite. There is no `test` script in `package.json`, no Vitest/Jest/Playwright Test config, and no `*.spec.*` or `*.test.*` tree defining unit coverage.
- Verification is script-driven and evidence-driven instead: build checks, packaged-route assertions, mock-webhook lead checks, and browser smoke evidence.
- `playwright` is now a declared dev dependency in `package.json`, but it is used through custom scripts like `scripts/launch-gate-lead.mjs`, not through Playwright Test.

## Primary Verification Commands
- `npm run build` delegates to `npm run build:site`, which runs the Vite production build.
- `npm run rebuild:site` is the strongest routine rebuild path. It chains `generate_pages.py`, the Vite build, and `scripts/verify-dist.mjs`.
- `npm run verify:dist` validates representative packaged routes under `dist/` and rejects raw source references such as `/main.js` or `/style.css`.
- `npm run launch:gate:smoke` executes `scripts/launch-gate-smoke.mjs` against a served `dist/` artifact and writes `smoke.json` under `.tmp/launch-gate/latest/`.
- `npm run launch:gate:lead` executes `scripts/launch-gate-lead.mjs` with Playwright and verifies homepage, mobile, and representative product lead flows.
- `npm run lead:webhook:mock` runs `scripts/mock-lead-webhook.mjs` as the local success/failure webhook harness for lead verification.
- `npm run playwright:install` is part of the clean-machine prerequisite for browser-based lead verification in `docs/LAUNCH-GATE.md`.

## What Is Actually Covered Today
- Packaged artifact coverage is narrow but concrete. `scripts/verify-dist.mjs` checks `dist/index.html`, `dist/mobile/index.html`, `dist/produtos/index.html`, `dist/produtos/retroescavadeiras/index.html`, and `dist/produtos/retroescavadeiras/580n/index.html`.
- Smoke coverage in `scripts/launch-gate-smoke.mjs` exercises the same representative surfaces over HTTP and requires expected content tokens plus `/assets/` references.
- Lead verification in `scripts/launch-gate-lead.mjs` covers three flows: homepage at `/?ops=1...`, mobile at `/mobile/?ops=1...`, and product at `/produtos/retroescavadeiras/580n/?ops=1...`.
- Lead pass criteria are stricter than a simple submit-state check: the script also requires a WhatsApp handoff URL via captured `window.open` calls.
- Operational visibility is part of the verification posture. Browser code writes lead ops state into `localStorage` under `ibl_lead_ops_v1`, and `?ops=1` is expected to expose that state.

## Gaps And Honest Limits
- There is still no unit coverage for logic in `main.js`, `mobile/main.js`, `webapp/main.js`, `generate_pages.py`, or the Python asset/scrape scripts.
- There is no lint step, formatter step, or static typecheck step declared in `package.json`.
- Launch verification is representative, not exhaustive. It samples one category and one PDP rather than sweeping every generated route under `produtos/**`.
- Browser evidence exists in `.playwright-cli/`, but that directory is historical evidence, not a stable contract or runnable suite.
- Python script verification is operational rather than assertion-based. Success is inferred from exit status, regenerated files, and downstream smoke checks.

## Evidence Locations
- `.tmp/launch-gate/latest/` is the canonical location for current launch-gate evidence such as `smoke.json`, `lead-success.json`, `lead-failure.json`, and copied mock webhook captures.
- `.playwright-cli/` contains earlier manual/exploratory browser snapshots, screenshots, console logs, and network logs.
- `docs/LAUNCH-READINESS.md` is the human-readable summary of the latest formal gate run.
- `docs/LAUNCH-GATE.md` documents the exact execution path and pass criteria the scripts are meant to satisfy.

## Practical Verification Patterns By Change Type
- For changes to generated routes or asset packaging, run `npm run rebuild:site` and then inspect the representative files checked by `scripts/verify-dist.mjs`.
- For changes to launch-critical HTML structure, selectors, or asset references, run `npm run launch:gate:smoke` against a local `python3 -m http.server --directory dist` instance.
- For changes to lead flow, submit messaging, selectors, or webhook behavior, run the two-mode lead gate with `npm run lead:webhook:mock` plus `npm run launch:gate:lead`.
- For changes to runtime logic shared across surfaces, verify all three browser runtimes: `main.js`, `mobile/main.js`, and `webapp/main.js`, even if the formal launch gate only covers homepage, mobile, and one representative PDP.
- For changes to generation scripts like `generate_pages.py`, inspect a representative sample of committed source HTML under `produtos/**` as well as the packaged output in `dist/**`.

## Recommended Review Focus
- Treat selector stability as a test concern. IDs such as `#lead-feedback`, `#product-lead-feedback`, `#lead-form`, and `#product-lead-form` are effectively test interfaces because `scripts/launch-gate-lead.mjs` depends on them.
- Treat `data-submit-state` values as part of the verification API. The current accepted values are `success`, `skipped`, and `failure`.
- Treat route existence and built asset references as release-gate requirements, not optional QA polish.
- Treat mobile parity as real scope. The current launch gate explicitly covers `mobile/index.html` and the mobile lead flow, so desktop-only verification is incomplete.
