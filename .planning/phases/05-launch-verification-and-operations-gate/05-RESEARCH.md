# Phase 5 Research: Launch Verification And Operations Gate

## Overview

Phase 5 is not another stabilization pass. Phases 1 through 4 already hardened the customer experience, lead flow, SEO/content trust, and generation/build reliability.

That means the final phase should answer one narrow operational question:

**Can another operator run one repeatable launch gate and decide, from evidence, whether the site is ready for production continuation?**

The goal is to turn the now-hardened behavior into an explicit release decision process.

## What Phase 5 Inherits

The repo already contains most of the technical ingredients needed for a launch gate:

- Phase 1 verified representative browse routes and the real `#captacao-lead` CTA contract.
- Phase 2 added a local mock lead webhook harness with success and failure modes plus actionable `?ops=1` observability.
- Phase 3 moved metadata and trust-critical content into generated HTML.
- Phase 4 created an authoritative rebuild workflow in `docs/OPERATIONS.md` and made `npm run build` / `npm run rebuild:site` produce an honest full-site `dist/` artifact.

Phase 5 therefore does **not** need to invent new runtime infrastructure. It needs to package these checks into one named launch gate, make the evidence reproducible, and capture the decision outcome cleanly.

## Current Verification Reality

The repo currently has strong but fragmented evidence:

- phase-specific verification reports under `.planning/phases/**`
- plan summaries with targeted browser and filesystem checks
- package scripts for rebuild and artifact verification
- a local lead mock server for success/failure contract checks

What is still missing is one practical launch-readiness checklist that:

1. runs in a defined order
2. covers the full production-critical surface
3. records pass/fail evidence in one place
4. makes launch continuation a clear decision instead of an implicit conclusion from scattered docs

That is exactly the gap between Phase 4 and `OPS-01` / `OPS-02`.

## Production-Critical Surface To Gate

From the prior phases and current repo shape, the final launch gate must cover four surfaces.

### 1. Rebuild and packaging

This is now the mandatory first step because `dist/` is the launch artifact.

Required evidence:

- `npm run assets:photos:check`
- `npm run assets:nobg:check`
- `npm run rebuild:site`
- representative packaged routes present in `dist/`
- representative packaged routes reference built assets, not source runtime files

### 2. Browse smoke

The customer-facing routes that matter most are already known from prior phases:

- `/`
- `/mobile/`
- `/produtos/`
- one representative category route
- one representative product route

The launch gate should verify these routes in the packaged artifact or a production-like served artifact, not just in source files.

### 3. Lead-flow gate

Phase 2 already established the local mock webhook contract, so the final release gate should re-use it rather than inventing another verification path.

Minimum launch-critical lead evidence:

- homepage lead flow under webhook success mode
- representative product-context lead flow under webhook success mode
- failure-mode verification proves the UI does not claim false success
- ops/observability path still surfaces actionable evidence for skipped/failed/stale states

### 4. Final decision output

The repo still lacks one operator-facing deliverable that answers:

- what was checked
- what passed
- what failed or remained bounded
- whether the site is ready to proceed to production continuation

Phase 5 should produce that explicitly.

## Constraints And Risks

### Browser automation remains environment-sensitive

Earlier phases already encountered Chrome-launch issues in this environment. That means the launch gate should prefer a layered verification strategy:

- first filesystem/build checks
- then HTTP-level packaged-route checks
- then browser-level checks where the environment supports them

The plan should not assume that one specific browser automation path is always available.

### Lead verification depends on local runtime wiring

The lead harness is local and safe, but the launch gate must still control:

- mock server mode
- target port/path
- runtime webhook URL
- where captured payload evidence is stored

This needs to be codified, not left to memory.

### Final launch output must stay repo-native

The best Phase 5 result is not a Notion checklist or tribal QA ritual. It should live in the repo as:

- an operations checklist/runbook
- a launch evidence report
- commands/scripts that directly support the gate

## Recommended Plan Shape

The cleanest split is:

1. codify the launch gate and evidence collection workflow
2. execute the gate end-to-end across rebuild, browse, and lead surfaces
3. publish the launch decision and bounded remainder in one final report

This ordering matters:

- first define the gate
- then run it on the actual hardened system
- then capture the decision and any remaining non-blockers

## Validation Architecture

Phase 5 validation should be evidence-first and artifact-first.

- Rebuild validation:
  - run the documented rebuild commands from `docs/OPERATIONS.md`
  - confirm `dist/` contains the representative launch routes
- Packaged browse validation:
  - serve `dist/` locally
  - verify representative homepage, mobile, catalog, category, and product routes return successfully
  - confirm representative packaged HTML references built assets
- Lead validation:
  - start the local mock webhook in success mode and capture payload evidence
  - verify homepage and representative product lead submissions against the local runtime
  - repeat in failure mode and confirm truthful error behavior
- Output validation:
  - a single launch checklist or gate doc exists
  - a single final launch report exists
  - the final report records pass/fail outcomes and any bounded remainder

Representative acceptance coverage should include:

- `npm run assets:photos:check`
- `npm run assets:nobg:check`
- `npm run rebuild:site`
- representative served packaged routes:
  - `/`
  - `/mobile/`
  - `/produtos/`
  - `/produtos/retroescavadeiras/`
  - `/produtos/retroescavadeiras/580n/`
- lead verification on:
  - homepage
  - representative product page
  - success mode
  - failure mode

## Open Questions / Assumptions

- Assumption: launch readiness for this milestone means “safe to continue toward production” rather than “public deployment performed from this repo in this phase.”
- Assumption: the final gate should rely on the local mock webhook for repeatability, not on the external `ibl-ai-os` environment.
- Assumption: if browser automation is unavailable again, the launch gate may fall back to HTTP-level and filesystem-backed evidence as long as the limitation is recorded explicitly.
