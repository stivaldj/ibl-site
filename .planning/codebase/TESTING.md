# Testing And Verification

## Overview

This repo does not appear to have a conventional unit test suite. I did not find `vitest`, `jest`, `cypress`, or a `test` script in `package.json`.

Validation is instead centered on build-time checks, route smoke checks, and browser-driven launch-gate scripts.

## Script-Level Verification

The primary verification commands declared in `package.json` are:

- `npm run build`
- `npm run build:site`
- `npm run rebuild:site`
- `npm run verify:dist`
- `npm run launch:gate:smoke`
- `npm run launch:gate:lead`
- `npm run playwright:install` installs Chromium for the lead gate

The supporting content and evidence flow is documented in:

- `docs/OPERATIONS.md`
- `docs/LAUNCH-GATE.md`
- `docs/LAUNCH-READINESS.md`

## What Each Check Covers

- `npm run assets:photos:check` and `npm run assets:nobg:check` are dry-run asset validation steps before a rebuild.
- `npm run rebuild:site` regenerates `produtos/**`, runs the Vite build, and then verifies the built artifact.
- `scripts/verify-dist.mjs` checks that representative packaged routes exist in `dist/` and that HTML references built `/assets/*` files instead of raw source entry files.
- `scripts/launch-gate-smoke.mjs` fetches representative routes from a served `dist/` build and checks for HTTP 200, built asset references, and the absence of raw `/main.js` or `/style.css` links.
- `scripts/launch-gate-lead.mjs` uses Playwright to exercise homepage, mobile, and representative product lead flows in both success and failure modes.
- `scripts/mock-lead-webhook.mjs` provides a local webhook harness so lead submission can be validated without external infrastructure.

## Evidence And Artifacts

- Formal launch-gate evidence is written under `.tmp/launch-gate/latest/`.
- The smoke gate writes `smoke.json`.
- The lead gate writes `lead-success.json` and `lead-failure.json`.
- The mock webhook can persist captured request payloads to a caller-specified JSON file.

## Browser Coverage

- Lead verification is browser-based and checks that the submit flow still opens the WhatsApp handoff URL.
- The official gate documents both success and failure expectations, so the browser checks are not limited to happy-path behavior.
- Mobile coverage is explicit in the lead gate and packaged smoke gate.

## Gaps And Unknowns

- No automated unit or integration test suite is checked in.
- No lint or formatting script is declared in `package.json`.
- The repo’s verification contract is therefore build-and-smoke oriented rather than test-runner oriented.
