# Phase 1 Research: Site Experience Stabilization

## Overview

Phase 1 is about removing the most visible browsing and navigation defects from the current brownfield site, not redesigning it. The scope is the public browsing experience across the homepage, catalog, category pages, product pages, and the mobile entry path. This phase directly covers `EXP-01`, `EXP-02`, `EXP-03`, `EXP-04`, and `FE-01`.

The key planning fact is that the site is split across three runtime surfaces:

- Homepage shell in `index.html`, enhanced by `webapp/main.js`
- Mobile shell in `mobile/index.html`, enhanced by `mobile/main.js`
- Generated catalog and product pages under `produtos/`, enhanced by root `main.js`

That means visible defects are likely to appear in more than one place, and some fixes belong in templates or shared runtime code rather than individual generated HTML files.

## Phase Surfaces In Scope

The phase should explicitly audit these route surfaces:

- Homepage: `/` from `index.html`
- Catalog index: `/produtos/` from `produtos/index.html`
- Category indexes: `/produtos/retroescavadeiras/`, `/produtos/escavadeiras-hidraulicas/`, `/produtos/pas-carregadeiras/`, `/produtos/minicarregadeiras/`, `/produtos/motoniveladoras/`, `/produtos/miniescavadeiras/`, `/produtos/rolo-compactador/`, `/produtos/tratores-de-esteiras/`
- Representative product pages: `/produtos/retroescavadeiras/580n/`, `/produtos/escavadeiras-hidraulicas/cx220c-s2/`, `/produtos/pas-carregadeiras/w20g/`, `/produtos/minicarregadeiras/sr200b/`, `/produtos/motoniveladoras/865b-series-2/`, `/produtos/rolo-compactador/1107ex/`, `/produtos/tratores-de-esteiras/2050m/`
- Mobile entry: `/mobile/` from `mobile/index.html`

The practical planning implication is to sample one page per category and not assume the homepage or catalog proves the whole browsing flow.

## Relevant Code/Files

- `index.html`: homepage content, nav anchors, hero, catalog cards, and the primary lead CTA surface.
- `mobile/index.html`: mobile-specific version of the homepage, with the same content blocks but different spacing and layout behavior.
- `produtos/index.html`: generated catalog landing page with filtering, compare affordances, and category cards.
- `produtos/**/index.html`: generated category and product pages, including breadcrumb, hero, CTA, and footer template output.
- `generate_pages.py`: source of generated header/footer/breadcrumb/product/category templates.
- `main.js`: runtime for generated pages; also handles lead ops, tracking, and product page augmentations.
- `webapp/main.js`: homepage runtime plus catalog/filter/product-page augmentation logic.
- `mobile/main.js`: mobile runtime mirroring the homepage behavior.
- `.planning/codebase/ARCHITECTURE.md`: confirms the static-site split and generation flow.
- `.planning/codebase/CONCERNS.md`: lists the known broken affordances and selector fragility.
- `.planning/codebase/TESTING.md`: confirms there is no formal test suite, so validation is browser-driven.

## Likely Defect Classes To Sweep

- Placeholder or dead links: `generate_pages.py` still emits `href="#"` in footer/company/support/social blocks, and `index.html` also contains placeholder anchors in lower-page content. These are direct `EXP-04` risks because they look interactive but do nothing.
- Misleading CTA states: some visible “Solicitar Orçamento” or social buttons are rendered as inert buttons instead of explicit links or disabled states. If they are not part of the phase-2 lead flow, they should be visually or semantically demoted now.
- Layout breakage on generated pages: the product templates in `generate_pages.py` are long, repetitive, and rendered into many routes. A small spacing or overflow bug there will hit every category/product page at once.
- Mobile/desktop drift: `index.html` and `mobile/index.html` are parallel shells, so a fix in one does not automatically fix the other. This is the main `EXP-02` risk.
- Shared browse behavior drift: `webapp/main.js`, `main.js`, and `mobile/main.js` duplicate behavior for analytics, catalog interactions, product-page enhancements, and local state. Any browse fix must be checked against all three runtimes to satisfy `FE-01`.
- Breadcrumb/navigation inconsistencies: `webapp/main.js` builds breadcrumb schema with broad `nav` selectors, and `generate_pages.py` renders breadcrumb HTML separately. This can cause page-level nav/breadcrumb mismatch or wrong schema on product pages.
- Catalog interaction brittleness: `webapp/main.js` binds filters and compare state to specific pathnames and generated card markup in `produtos/index.html`. If the markup changes, the browse tools can silently stop working.

## Recommended Audit And Fix Sequence

1. Start with a route inventory and visual baseline for the homepage, catalog, one page per category, and the mobile entry. Do not begin by editing generated HTML blindly.
2. Audit the homepage and mobile shell first, since they are the most visible entry points and expose the main nav/hero/CTA patterns.
3. Audit `produtos/index.html` next, because the catalog is where browse-path friction will show up first: filter chips, compare controls, category cards, and card-to-category navigation.
4. Sweep the category and product templates in `generate_pages.py` for repeated defects, especially footers, breadcrumbs, CTA affordances, and image/card spacing.
5. Only after shared template fixes are clear, touch page-specific exceptions in `index.html` or `mobile/index.html`.
6. Regenerate or re-serve the affected generated pages after every template fix so the planner does not accidentally optimize stale output.

## Risks And Dependencies

- The repo has no dedicated automated test suite, so regressions are easy to miss unless validation is explicit and route-based.
- `produtos/` is generated content, not a hand-edited source tree. Planning should prefer changing `generate_pages.py` and re-rendering rather than patching many output files directly.
- The runtime split means a visual fix in one entry point can be incomplete if the same behavior exists in `webapp/main.js`, `main.js`, and `mobile/main.js`.
- Some visible buttons may actually be placeholders for future lead flow work. This phase should not accidentally create scope creep into Phase 2; it should either wire a real destination or convert the control into an explicit non-interactive state.
- External assets and CDNs remain part of the page shell. Phase 1 should treat broken or missing asset behavior as a visible browsing defect, but not as a rebuild of the asset pipeline.

## Validation Architecture

Validation for this phase should be browser-first and route-specific, with `npm run build` as the minimum compile gate. Because there is no formal test runner, the planning assumption should be:

- Build gate: run `npm run build` to catch broken imports, broken generated-page references, and CSS/runtime regressions in the Vite entrypoints.
- Desktop smoke set: open `/`, `/produtos/`, at least one category page, and at least one product page at a wide viewport and verify no overlap, clipping, or dead-end CTA states.
- Mobile smoke set: repeat the same flow at a narrow viewport against `mobile/index.html` and the same generated product/category pages to catch layout drift and touch-target failures.
- Journey check: confirm the main browse path works end to end from homepage hero/catalog entry to category to product detail without a broken back-link or misleading anchor.
- CTA check: confirm every launch-critical visible CTA either resolves to a real destination or is intentionally styled as non-interactive; no `href="#"` should remain on customer-facing affordances.
- Console/network check: verify there are no obvious client errors or failed asset fetches on the audited routes, especially on generated pages where template defects will repeat.
- Route sampling: validate at least one representative page from each category in `produtos/` so fixes do not only work for the retroescavadeira path.

The practical acceptance bar for Phase 1 is that the site feels coherent across the same browsing path on desktop and mobile, and that the visible navigation/CTA surface no longer contains obvious fake interactions.

## Open Questions / Assumptions

- Assumption: Phase 1 should fix shared templates and runtimes first, then any page-specific exceptions, rather than patching many generated HTML files by hand.
- Assumption: lead capture behavior that would require backend or webhook work stays out of scope until Phase 2, unless a CTA is currently broken or misleading.
- Open question: which exact product pages should be treated as canonical smoke targets for the phase plan beyond the samples listed above.
- Open question: whether any homepage/footer links should be fully removed instead of being pointed to temporary real destinations.
- Open question: whether the generated catalog compare/filter affordances are in scope for polish only, or whether they need full stabilization as part of the browse journey.
