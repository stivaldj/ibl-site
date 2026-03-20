# Phase 4 Research: Generation And Frontend Reliability Stabilization

## Overview

Phase 4 starts after the customer-facing trust surface is already stabilized:

- Phase 1 fixed browse and CTA defects
- Phase 2 stabilized lead flow and local observability
- Phase 3 moved SEO ownership into generated HTML and cleaned representative machine-content drift

That means Phase 4 should not spend time re-solving visible launch trust problems. Its job is to harden the foundation underneath them so future changes do not silently reintroduce production defects.

The remaining launch-critical reliability risks are concentrated in three places:

1. the Python generation and asset-processing pipeline
2. the honesty of the build/deploy artifact
3. dead or misleading frontend surface area that obscures the real production paths

## Current Generation Pipeline Reality

The actual site is assembled through multiple disconnected steps:

1. `scrape_specs.py` refreshes scraped model content into per-model `content.md` files and updates `Scrape Case/scrape_db.json`
2. `process_fotos.py` generates transparent processed photos into `public/case-assets/fotos-processed/`
3. `remove_bg_batch.py` creates a smaller curated set of `-nobg.png` assets directly under `public/case-assets/{category}/{model}/`
4. `generate_pages.py` reads `scrape_db.json` and `content.md`, copies model-local source assets into `public/case-assets/{category}/{model}/`, and writes generated catalog/category/product HTML into `produtos/`
5. `vite build` produces `dist/` for the two Vite entry shells only

There is no single repo-native command that rebuilds the full launch artifact from source content through generated HTML through deployable output.

## Confirmed Pipeline Findings

### HTML generation is currently stable on immediate rerun

Re-running `python3 generate_pages.py` against unchanged inputs produced the same SHA-256 digest for the full `produtos/**/*.html` tree:

- file count: 41
- digest before rerun == digest after rerun

This matters because Phase 4 should not over-rotate into “HTML determinism” as a speculative risk. The immediate current evidence says the generated HTML tree is stable once the inputs are unchanged.

### Asset sync is still additive, not self-cleaning

`generate_pages.py` copies model assets from source into `public/case-assets/{category}/{model}/`, but it never removes files that no longer belong there.

Direct comparison showed:

- source-tracked model assets: 32
- public model assets: 40
- extra public assets: 8
- missing public assets: 0

The extras are all `-nobg.png` derivatives such as:

- `escavadeiras-hidraulicas/cx220c-s2/cx220c-nobg.png`
- `pas-carregadeiras/w20g/w20g-nobg.png`
- `retroescavadeiras/580n/580n-nobg.png`

These files are not inherently wrong, but they prove the public asset tree is not a pure projection of source assets. Once a file lands there, the current pipeline will happily keep serving it unless someone removes it manually.

### Asset-processing scripts cache by “exists” and therefore hide source changes

Both image scripts short-circuit on existing output:

- `process_fotos.py`: `if dst.exists(): [SKIP] already exists`
- `remove_bg_batch.py`: `if dst.exists(): [SKIP] ... already exists`

This means corrected source images, updated rembg behavior, or refined cleanup parameters will not propagate on rerun unless the destination files are deleted first. That is a direct reliability problem for `GEN-01` and `GEN-03`.

### `generate_pages.py` still has a residual nondeterminism vector in asset choice

`copy_assets()` still iterates source files with unsorted `iterdir()` and returns the first copied asset as the hero image candidate. The HTML rerun remained stable in the current dataset, but the implementation still leaves room for filesystem-order drift or environment-specific ordering in future asset sets.

Phase 4 should remove that implementation risk even though the immediate rerun happened to be stable.

## Build Artifact Honesty Findings

The most important Phase 4 discovery is that `vite build` does **not** currently create a launch-complete artifact for the whole site.

Observed facts:

- `vite.config.js` only declares `index.html` and `mobile/index.html` as build inputs
- `dist/` contains:
  - desktop and mobile Vite output
  - copied static `public/` assets under `dist/case-assets`
- `dist/` does **not** contain:
  - `produtos/index.html`
  - `produtos/{category}/{model}/index.html`
  - root `main.js`
  - root `style.css`
  - `webapp/main.js`
  - `mobile/main.js`

This matches earlier operational notes from Phase 1 and Phase 3:

- `vite preview` is not a faithful representation of the generated `produtos/**` tree
- generated-route verification had to use the local source tree rather than a production-like packaged artifact

This is the central Phase 4 reliability issue. Today, “build passes” does not mean “launch artifact is complete”.

## Frontend Surface Reliability Findings

### Dead Vite scaffold still exists and still appears relevant enough to mislead

The repo still contains the untouched Vite starter scaffold:

- `src/main.js`
- `src/counter.js`
- `src/style.css`

Those files are not part of the real entry paths, but they still:

- exist in the repo
- are referenced in `tailwind.config.js`
- look like normal application source to a future maintainer

This is exactly the kind of dead surface area that satisfies the “obscures the real production paths” part of `FE-02`.

### Tailwind configuration is split-brain but recoverable

The real stylesheets already use Tailwind v4 `@source` correctly:

- `style.css` scans `./index.html` and `./produtos/**/*.html`
- `webapp/style.css` scans `../index.html` and `../produtos/**/*.html`
- `mobile/style.css` scans `./index.html` and `../produtos/**/*.html`

But `tailwind.config.js` still points at `./src/**/*.{js,ts,jsx,tsx}`, which reinforces the dead scaffold and no longer describes the live code paths accurately.

This is mostly a maintainability/reliability issue, not a styling failure, because the live CSS files already carry the real scan declarations.

## Documentation And Operator Workflow Findings

There is no current operator-facing source of truth that cleanly explains:

- which scripts must run, and in what order, to rebuild the launchable site
- what “done” means for `public/`, `produtos/`, and `dist/`
- whether `dist/` is supposed to be the deployable artifact or whether deployment still depends on the repo root tree
- how to verify that a rerun did not leave stale assets or missing generated routes behind

Existing materials such as `WORKING.md`, `PROJECT_ANALYSIS.md`, and `tasks/todo.md` are historical or aspirational. They are not a current operational rebuild manual.

That leaves `GEN-02` clearly unresolved.

## Recommended Plan Shape

The cleanest Phase 4 split is:

1. pipeline and asset hygiene
2. production artifact completeness and dead-surface quarantine
3. documented rebuild workflow plus final rebuild verification

This ordering matters:

- first make the source-generation pipeline safe to rerun
- then make the packaged/served artifact honest
- then document and verify the real rebuild path end-to-end

## Validation Architecture

Validation for this phase should be filesystem-first and rebuild-first.

- Pipeline checks:
  - run the relevant Python generators and processors
  - prove reruns do not silently preserve stale output
  - prove asset selection is deterministic
- Artifact checks:
  - run the production packaging path
  - confirm representative generated routes and their required runtime/style assets exist in the final output
  - confirm launch-critical assets resolve from the packaged artifact, not just from the source tree
- Frontend checks:
  - verify dead scaffold surface is removed or clearly quarantined
  - verify the real production entrypoints remain the only obvious supported paths
- Documentation checks:
  - operator docs must give one reproducible rebuild sequence
  - verification should be executable from the documented commands rather than relying on tribal knowledge

Representative acceptance coverage should include:

- filesystem inspection of `public/`, `produtos/`, and `dist/`
- `python3 generate_pages.py`
- any hardened asset-processing command paths introduced in this phase
- `npm run build` or a replacement packaging command
- packaged-route existence checks for:
  - `/`
  - `/mobile/`
  - `/produtos/`
  - one representative category route
  - one representative product route

## Open Questions / Assumptions

- Assumption: the right Phase 4 outcome is either a deployable `dist/` for the full site or an explicit documented decision that deployment is source-tree-based with a verified copy/sync step. “Ambiguous build output” is not acceptable after this phase.
- Assumption: generated `-nobg.png` derivatives are valid launch assets, but Phase 4 should make their lifecycle explicit rather than leave them as unmanaged extras.
- Assumption: the untouched `src/` scaffold should be removed or clearly quarantined unless a real production path still depends on it.
