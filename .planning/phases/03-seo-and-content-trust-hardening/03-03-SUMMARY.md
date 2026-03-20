# Plan 03-03 Summary: Runtime SEO Fallback Reduction

## Outcome

Plan `03-03` is complete.

Generated-route SEO is now source-owned first and runtime-owned only as fallback. The three runtime entry files no longer overwrite canonical/meta/schema on generated `produtos/` routes when the shipped HTML already contains the Phase 3 baseline.

## What Changed

### Task 1: Downgrade generated-route SEO runtime code from primary source to fallback behavior

Updated the SEO enhancement section in:

- `main.js`
- `webapp/main.js`
- `mobile/main.js`

The runtime now:

- detects when a generated `/produtos/**` route already ships the required SEO baseline in source HTML
- skips unconditional overwrites of description, canonical, Open Graph, Twitter, and product/breadcrumb schema on those generated routes
- still adds `FAQPage` JSON-LD on product pages when FAQ content exists and that schema is not already present
- preserves the old metadata-building path as a conservative fallback when the baseline is absent
- aligns `og:type` with page kind in the fallback path (`product` for product pages, `website` otherwise)

### Task 2: Final source-first verification pass

Ran the final verification in two layers:

1. Raw-file inspection of representative generated routes:
   - `produtos/index.html`
   - `produtos/retroescavadeiras/index.html`
   - `produtos/retroescavadeiras/580n/index.html`
   - `produtos/escavadeiras-hidraulicas/cx240c-me/index.html`
2. Browser verification on the same routes through the local Vite dev server

The browser pass confirmed the final DOM kept the same title, description, canonical URL, Open Graph title/type, and expected JSON-LD types already present in source HTML. Product pages also added `FAQPage` as intended without contradicting the generator-owned `Product` and `BreadcrumbList` schema.

## Verification

- `npm run build` passed
- Raw-file inspection confirmed source HTML already contains description, canonical, Open Graph, Twitter, and JSON-LD on representative catalog, category, and product routes
- Browser verification on:
  - `/produtos/`
  - `/produtos/retroescavadeiras/`
  - `/produtos/retroescavadeiras/580n/`
  - `/produtos/escavadeiras-hidraulicas/cx240c-me/`
  confirmed:
  - final `document.title` matches source HTML
  - final canonical matches source HTML
  - final meta description matches source HTML
  - final `og:title` and `og:type` remain coherent
  - generated routes retain `CollectionPage` or `Product` plus `BreadcrumbList`
  - product routes add `FAQPage` only as additive runtime behavior
- Runtime parity checks confirmed:
  - `main.js == mobile/main.js` for the SEO fallback section
  - `webapp/main.js` carries the same fallback logic and generated-route baseline guard

## Files Changed

- `main.js`
- `webapp/main.js`
- `mobile/main.js`
- `.planning/phases/03-seo-and-content-trust-hardening/03-03-SUMMARY.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`

## Commits

- `633cc36` `fix(03-03): make generated route seo runtime fallback-only`

## Notable Decisions

- Treated generator-owned metadata on `/produtos/**` as authoritative once the expected baseline exists in `<head>`.
- Kept FAQ schema injection as the only additive runtime SEO behavior on representative product pages.
- Avoided regenerating `produtos/**` in this plan because the source HTML baseline was already established by `03-01` and verified by `03-02`.

## Self-Check

- [x] `npm run build` passed
- [x] Raw-file inspection confirmed representative generated routes are SEO-complete before JavaScript
- [x] Browser inspection confirmed no contradictory canonical/meta/schema state after runtime execution
- [x] `main.js`, `webapp/main.js`, and `mobile/main.js` remain aligned for retained fallback behavior
- [x] No representative generated route depends on runtime injection for first valid canonical, description, or schema presence

## Deviations / Follow-Up

- No blocker.
- The final phase-level verification should use this plan’s source-vs-DOM evidence as the closeout basis for `SEO-01` and `SEO-04`.
