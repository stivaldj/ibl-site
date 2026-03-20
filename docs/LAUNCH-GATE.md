# VARIANT Launch Gate

This is the formal production-readiness gate for the current milestone.

Use this file when you need to answer one question:

**Is the hardened site ready to continue toward production with objective evidence?**

## Scope

The gate covers the production-critical surfaces already hardened in Phases 1 through 4:

1. rebuild and packaging
2. packaged-route smoke checks
3. mobile route coverage
4. lead-flow verification in success and failure modes

## Evidence Location

All gate evidence is written under:

- `.tmp/launch-gate/latest/`

The final Phase 5 launch-readiness report will summarize this evidence, but the raw gate artifacts should live in that directory.

## Lead Gate Runtime Prerequisite

On a clean machine, install the repo dependencies and Chromium once before running the lead gate:

```bash
npm install
npm run playwright:install
```

## Gate Steps

### 1. Rebuild Baseline

Run:

```bash
npm run assets:photos:check
npm run assets:nobg:check
npm run rebuild:site
```

Pass criteria:

- both dry-run asset checks complete without errors
- `npm run rebuild:site` completes successfully
- `npm run verify:dist` passes inside the rebuild flow

### 2. Packaged Smoke Gate

Serve the launch artifact:

```bash
python3 -m http.server 4173 --directory dist
```

Then run:

```bash
npm run launch:gate:smoke -- --base-url http://127.0.0.1:4173 --evidence-dir .tmp/launch-gate/latest
```

Pass criteria:

- representative homepage, mobile, catalog, category, and product routes return HTTP 200
- representative packaged routes still reference built `/assets/*` files
- representative packaged routes do not fall back to raw `/main.js`, `/mobile/main.js`, `/style.css`, or `/mobile/style.css`

### 3. Lead Gate: Success Mode

Start the success webhook harness:

```bash
npm run lead:webhook:mock -- --mode success --port 8787 --capture-file .tmp/launch-gate/latest/mock-success.json
```

Start a local runtime with the webhook URL wired:

```bash
VITE_LEAD_WEBHOOK_URL=http://127.0.0.1:8787/lead npm run dev -- --host 127.0.0.1 --port 4174
```

Then run:

```bash
npm run launch:gate:lead -- --base-url http://127.0.0.1:4174 --expected-status success --evidence-file .tmp/launch-gate/latest/lead-success.json
```

Pass criteria:

- homepage lead flow reaches `data-submit-state="success"`
- mobile lead flow reaches `data-submit-state="success"`
- representative product lead flow reaches `data-submit-state="success"`
- homepage, mobile, and product flows all open a WhatsApp handoff URL
- webhook capture exists and contains payload evidence

### 4. Lead Gate: Failure Mode

Start the failure webhook harness:

```bash
npm run lead:webhook:mock -- --mode failure --port 8788 --capture-file .tmp/launch-gate/latest/mock-failure.json
```

Start a local runtime with the failure webhook URL wired:

```bash
VITE_LEAD_WEBHOOK_URL=http://127.0.0.1:8788/lead npm run dev -- --host 127.0.0.1 --port 4175
```

Then run:

```bash
npm run launch:gate:lead -- --base-url http://127.0.0.1:4175 --expected-status failure --evidence-file .tmp/launch-gate/latest/lead-failure.json
```

Pass criteria:

- homepage lead flow reaches `data-submit-state="failure"`
- mobile lead flow reaches `data-submit-state="failure"`
- representative product lead flow reaches `data-submit-state="failure"`
- homepage, mobile, and product flows all open the WhatsApp fallback instead of claiming false success

## Readiness Decision

A run is ready to pass the launch gate when:

- rebuild baseline passes
- packaged smoke gate passes
- success-mode lead gate passes
- failure-mode lead gate passes
- any remaining caveats are explicitly bounded and non-blocking

If any gate step fails, the site is not ready for production continuation until the failure is fixed or explicitly re-scoped.
