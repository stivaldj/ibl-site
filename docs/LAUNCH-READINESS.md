# VARIANT Launch Readiness

**Status:** In Progress  
**Last updated:** 2026-03-20

This report records the latest formal launch-gate run for the current production-hardening milestone.

## Current Gate Status

- Rebuild baseline: passed
- Packaged smoke gate: passed
- Lead gate success mode: pending
- Lead gate failure mode: pending
- Final readiness verdict: pending

## Evidence

- Rebuild baseline:
  - `.tmp/launch-gate/latest/assets-photos-check.log`
  - `.tmp/launch-gate/latest/assets-nobg-check.log`
  - `.tmp/launch-gate/latest/rebuild-site.log`
- Packaged smoke gate:
  - `.tmp/launch-gate/latest/smoke-run.log`
  - `.tmp/launch-gate/latest/smoke.json`

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

Lead verification is still pending before a final readiness verdict can be issued.
