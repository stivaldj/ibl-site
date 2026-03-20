# Plan 03-02 Summary: Content Trust Normalization

## Outcome

Plan `03-02` is complete.

The generator now normalizes launch-visible content artifacts that were previously leaking from `content.md` into generated product pages. The work stayed narrowly scoped to trustworthy output: no source `content.md` files needed editing for this plan.

## What Changed

### Task 1: Harden parsing and rendering against visible content artifacts

Updated `generate_pages.py` to make the parsing and visible rendering path more resilient:

- added `clean_text()` to strip zero-width formatting characters and normalize whitespace
- cleaned parsed title/category/spec keys/spec values before rendering
- taught quick-spec parsing to carry continuation lines instead of dropping them
- taught technical-spec parsing to append continuation lines to the current spec item instead of truncating at the first line
- replaced the fragile CTA heading derived from `title.split()` with a full-title heading via `build_product_cta_heading()`

Regenerated `produtos/**` after the parser/rendering fix so the launch output reflects the normalized content.

### Task 2: Representative source-vs-output trust audit

Ran a direct source-vs-output audit against:

- `Scrape Case/scrape_db.json`
- representative `content.md` files across two categories
- representative generated HTML under `produtos/**`

Audited pages:

- `produtos/retroescavadeiras/580n/index.html`
- `produtos/escavadeiras-hidraulicas/cx220c-s2/index.html`
- `produtos/escavadeiras-hidraulicas/cx240c-me/index.html`
- `produtos/minicarregadeiras/sr175b/index.html`

For each sample, the audit confirmed:

- title in `scrape_db.json` matches `content.md`
- category in `scrape_db.json` matches `content.md`
- generated HTML contains the same title
- generated HTML contains the same category context
- generated HTML contains the source description
- the first two quick specs from source are present in HTML
- the CTA heading now references the full machine title

## Verification

- `python3 generate_pages.py` passed
- `npm run build` passed
- Global generated-route sweep found no remaining launch-visible:
  - zero-width quick-spec labels
  - sampled truncated spec-value fragments that previously appeared in representative pages
  - old CTA phrasing derived from only the first one or two title tokens
- Representative audits across retroescavadeiras, escavadeiras hidráulicas, and minicarregadeiras all passed

## Notable Decisions

- Kept route slugs and source naming as-is for now because no business-approved naming normalization was provided.
- Avoided editing `content.md` source files in this plan because the visible launch defects were fixable in generator parsing/rendering.
- Limited the scope to trust-breaking visible artifacts; broader metadata/schema ownership remains covered by the parallel Phase 3 plan set.

## Files Changed

- `generate_pages.py`
- regenerated `produtos/**/index.html`
- `.planning/phases/03-seo-and-content-trust-hardening/03-02-SUMMARY.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`

## Commits

- `d9e1a74` `fix(03-02): normalize generated product content artifacts`

## Self-Check

- [x] Representative pages across at least two categories were compared against `scrape_db.json` and matching `content.md`
- [x] Sampled generated pages no longer show malformed quick-spec labels or visibly truncated spec values
- [x] Sampled breadcrumbs, page titles, hero copy, and CTA context refer to the same machine identity
- [x] Source-file edits were not required for the issues addressed in this plan
- [x] `npm run build` still passes

## Deviations / Follow-Up

- None blocking this plan.
- Concurrent Phase `03-01` work is also touching `generate_pages.py`; this summary intentionally records only the content-trust changes completed under `03-02`.
