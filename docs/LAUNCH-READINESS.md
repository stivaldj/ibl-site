# VARIANT Launch Readiness

**Status:** Ready for production continuation  
**Last updated:** 2026-03-20

This report records the latest formal launch-gate run for the current production-hardening milestone.

## Current Gate Status

- Rebuild baseline: passed
- Packaged smoke gate: passed
- Lead gate success mode: passed
- Lead gate failure mode: passed
- Final readiness verdict: ready for production continuation

## Evidence

- Rebuild baseline:
  - `.tmp/launch-gate/latest/assets-photos-check.log`
  - `.tmp/launch-gate/latest/assets-nobg-check.log`
  - `.tmp/launch-gate/latest/rebuild-site.log`
- Packaged smoke gate:
  - `.tmp/launch-gate/latest/smoke-run.log`
  - `.tmp/launch-gate/latest/smoke.json`
- Lead gate success mode:
  - `.tmp/launch-gate/latest/lead-success.log`
  - `.tmp/launch-gate/latest/lead-success.json`
  - `.tmp/launch-gate/latest/mock-success.json`
- Lead gate failure mode:
  - `.tmp/launch-gate/latest/lead-failure.log`
  - `.tmp/launch-gate/latest/lead-failure.json`
  - `.tmp/launch-gate/latest/mock-failure.json`

## Rebuild Baseline Outcome

The documented baseline commands from [LAUNCH-GATE.md](/Users/joseoliveira/CODING/VARIANT/docs/LAUNCH-GATE.md) were executed successfully:

```bash
npm run assets:photos:check
npm run assets:nobg:check
npm run rebuild:site
```

Observed result:

- both asset dry-run checks completed without errors
- `npm run rebuild:site` completed successfully
- `dist/` was rebuilt and re-verified through `npm run verify:dist`

## Packaged Smoke Outcome

The packaged launch artifact was served locally and checked with:

```bash
npm run launch:gate:smoke -- --base-url http://127.0.0.1:4273 --evidence-dir .tmp/launch-gate/latest
```

Observed result:

- representative homepage, mobile, catalog, category, and product routes all returned HTTP 200
- representative packaged routes kept built `/assets/*` references
- no representative packaged route fell back to raw `/main.js`, `/mobile/main.js`, `/style.css`, or `/mobile/style.css`

## Lead Gate Outcome

The lead gate was executed against local runtimes wired to the repo-local webhook mock in both success and failure modes.

Success mode command:

```bash
npm run launch:gate:lead -- --base-url http://127.0.0.1:4274 --expected-status success --evidence-file .tmp/launch-gate/latest/lead-success.json
```

Observed result:

- homepage lead flow reached `data-submit-state="success"`
- representative product lead flow reached `data-submit-state="success"`
- both flows still opened the WhatsApp handoff URL
- webhook capture evidence exists in `.tmp/launch-gate/latest/mock-success.json`

Failure mode command:

```bash
npm run launch:gate:lead -- --base-url http://127.0.0.1:4275 --expected-status failure --evidence-file .tmp/launch-gate/latest/lead-failure.json
```

Observed result:

- homepage lead flow reached `data-submit-state="failure"`
- representative product lead flow reached `data-submit-state="failure"`
- both flows still opened the WhatsApp fallback URL instead of claiming false success
- webhook failure capture evidence exists in `.tmp/launch-gate/latest/mock-failure.json`

## Final Verdict

**Ready for production continuation.**

The formal launch gate passed across:

- rebuild baseline
- packaged-route smoke checks
- mobile route coverage
- homepage lead flow in success and failure modes
- representative product lead flow in success and failure modes

## Bounded Remainder

These items remain explicit but non-blocking:

- Real image regeneration still depends on optional Python packages such as `rembg`; the gate verifies the current shipped assets and rebuild path, not reinstallation of that optional stack.
- Upstream content refresh still depends on the external CASE site and scraper runtime dependencies; the current gate validates the hardened local rebuild path and packaged output, not live upstream availability.
- The gate validates the browser-side webhook contract using the local mock harness. Final external `ibl-ai-os` endpoint acceptance remains an environment-level check outside this repo.
