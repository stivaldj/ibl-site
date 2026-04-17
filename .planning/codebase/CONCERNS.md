# Overview

`ibl-site` is now a shipped v1.0 static marketing/catalog stack with a hardened launch baseline. The biggest launch blockers have been removed, but the codebase still carries a few bounded risks: generated-content drift, external service dependencies, and maintenance overhead from duplicated browser/runtime logic.

# Stabilized areas

- Lead capture is now materially safer than the original baseline. `webapp/main.js`, `mobile/main.js`, and `main.js` share a stable lead contract, and the formal gate in `docs/LAUNCH-GATE.md` now enforces homepage, mobile, and representative product proof with WhatsApp handoff.
- SEO trust is mostly source-owned now. Generated `produtos/**/*.html` pages ship the important metadata baseline directly, while the runtime SEO layer in `webapp/main.js` and `mobile/main.js` is fallback-only rather than the primary source of truth.
- Rebuild and packaging are documented and repeatable. `docs/OPERATIONS.md`, `scripts/verify-dist.mjs`, and `package.json` now define a dist-first workflow instead of leaving operators to infer release steps.
- The old external launch-gate fallback path was a real milestone risk, but the Phase 6 closeout work was explicitly created to remove that contract drift. The current map should treat the gate as repo-native, not as an open dependency gap.

# Confirmed technical debt

- `generate_pages.py` still emits repeated page templates for catalog, category, product, and footer blocks. That is acceptable for a generated site, but it makes large-scale content changes expensive and increases the chance of template drift.
- `produtos/**/*.html` is still very verbose and largely duplicated markup. That is not a bug, but it does mean any structural change has a wide blast radius.
- `src/main.js`, `src/counter.js`, and `src/style.css` remain scaffold leftovers relative to the real production entrypoints in `index.html` and `mobile/index.html`. They are quarantined, but they can still mislead a future maintainer who assumes `src/` is live production code.
- The traceability and milestone files in `.planning/` now say the baseline is complete, but they still need active maintenance so the docs do not drift back out of sync with shipped behavior.

# Fragile workflows / operational risks

- `generate_pages.py`, `scrape_specs.py`, `process_fotos.py`, and `remove_bg_batch.py` still form a multi-step content pipeline. Even after the hardening work, a partial rerun can leave the HTML, image assets, and source content temporarily out of sync if an operator skips the documented sequence.
- `scrape_specs.py` still depends on upstream CASE page structure and network availability. The risk is bounded, but it remains an external volatility point when refreshing product data.
- `docs/OPERATIONS.md` correctly documents the rebuild path, but that path remains a process dependency. If someone bypasses it, they can still produce stale or partial output.
- `scripts/launch-gate-lead.mjs` and `scripts/launch-gate-smoke.mjs` are now part of the release proof, so changes there have higher-than-normal operational impact. A small logic regression could invalidate the milestone evidence even when the site itself still works.

# Security and privacy concerns

- `webapp/main.js` and `mobile/main.js` persist lead and attribution state in `localStorage` under browser-readable keys such as `ibl_lead_ops_v1` and `ibl_attribution_v1`. That is operationally useful, but it also means the browser profile is now a data-bearing surface.
- Lead submission still posts JSON to a configurable webhook via `VITE_LEAD_WEBHOOK_URL`. The repo controls the client contract, but the final safety and retention posture still depends on the downstream `ibl-ai-os` environment.
- External assets are still loaded from third-party origins in `index.html`, `mobile/index.html`, and generated pages, including Google Fonts, Phosphor icons, and other browser-delivered resources. That expands the supply-chain and availability surface compared with a fully local bundle.

# Performance and maintainability concerns

- The site is still a static-first app with duplicated behavior across `webapp/main.js`, `mobile/main.js`, and `main.js`. That keeps the runtime simple, but it raises the cost of any future behavior change because fixes must stay in sync across three entry scripts.
- Generated pages lean on repeated HTML rather than shared runtime components. This is fine for launch, but it means performance tuning and content corrections are mostly template work, not isolated component work.
- `setupSeoEnhancements()` in `webapp/main.js` and `mobile/main.js` still inspects live DOM structure. Even as fallback-only code, it remains brittle if headings, breadcrumbs, or form structure change without review.
- The codebase still relies on browser-delivered CSS/JS and network resources for some page adornments. That is acceptable for the current baseline, but it should stay on the watch list for resilience and performance regressions.

# Bounded external dependencies

- Optional image regeneration still depends on `rembg` and other Python image tooling referenced in `docs/OPERATIONS.md`.
- Upstream content refresh still depends on the external CASE source and its scraper/runtime assumptions in `scrape_specs.py`.
- The final commercial acceptance check still depends on the target `ibl-ai-os` environment, which is outside this repo’s control.
- The launch gate itself depends on the local browser automation/tooling contract described in `docs/LAUNCH-GATE.md` and `package.json`, but that dependency is now bounded to the repo rather than another workspace.

# What to watch next

1. Keep `docs/LAUNCH-GATE.md`, `docs/LAUNCH-READINESS.md`, and `docs/OPERATIONS.md` aligned with the actual scripts so the evidence trail stays trustworthy.
2. Prefer changes in `generate_pages.py` and `webapp/main.js` that reduce duplication instead of adding more ad hoc page-specific exceptions.
3. Treat any refresh of product data, image processing, or scraped content as a full pipeline event, not a one-file edit.
4. Watch for regressions in `produtos/**/*.html` whenever the generator, content source, or asset pipeline changes.
