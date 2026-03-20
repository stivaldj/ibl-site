# Phase 3 Research: SEO And Content Trust Hardening

## Overview

Phase 3 is the trust and indexability pass for the generated catalog, category, and product pages under `produtos/`. Phase 1 already stabilized browse behavior, and Phase 2 stabilized lead handling. The next launch blocker is that the generated HTML is still not SEO-complete at delivery time and still allows machine-content issues to leak into production.

The main architecture fact for this phase is simple:

- `generate_pages.py` generates the shipped HTML for `produtos/index.html`, `produtos/{categoria}/index.html`, and `produtos/{categoria}/{modelo}/index.html`
- those shipped pages currently include only charset, viewport, fonts, icon script, and runtime bootstrap in `<head>`
- launch-critical metadata, canonical tags, and JSON-LD are still injected later by `setupSeoEnhancements()` in `main.js`, `webapp/main.js`, and `mobile/main.js`

That makes Phase 3 primarily a generator hardening phase, with a smaller runtime follow-up to ensure the client-side code no longer acts as the only SEO source of truth.

## Current Production SEO Architecture

The relevant implementation split is:

- `generate_pages.py` emits the HTML for the generated pages
- `HEAD_TEMPLATE` currently ships:
  - charset
  - viewport
  - icon script
  - Google Fonts links
  - `/main.js`
  - minimal anti-FOUC style
- generated pages do **not** ship:
  - meta description
  - canonical link
  - Open Graph tags
  - Twitter tags
  - JSON-LD
- `main.js` function `setupSeoEnhancements()` injects all of the above at runtime by querying:
  - `document.querySelector('title')`
  - `document.querySelector('h1')`
  - `document.querySelector('main p')`
  - `document.querySelector('main img')`
  - `[data-breadcrumb-nav]`

The same SEO helper exists in:

- `main.js`
- `webapp/main.js`
- `mobile/main.js`

That duplication matters, but the generated-route dependency is the material launch risk because crawlers and link unfurlers can see the shipped HTML before JavaScript enhancement runs.

## Confirmed Phase 3 Gaps

The current generated pages under `produtos/` were sampled and all representative pages are missing the expected SEO primitives in source HTML:

- `produtos/index.html`
- `produtos/retroescavadeiras/index.html`
- `produtos/retroescavadeiras/580n/index.html`

For those shipped files, source HTML currently lacks:

- `<meta name="description">`
- `<link rel="canonical">`
- Open Graph tags such as `og:title`, `og:description`, `og:url`
- Twitter tags
- JSON-LD scripts

A repo-wide sample over `produtos/*/*/index.html` reported 96 missing-item findings across product pages for just:

- description meta
- canonical
- JSON-LD

This is not an isolated regression. It is the current generation model.

## Content Source Of Truth

The generator uses `Scrape Case/scrape_db.json` as the top-level inventory and then reads each model’s `content.md` from paths stored in the database:

- total categories: 8
- total models: 32
- all 32 model paths currently have a `content.md`

The actual authoritative content inputs for product pages are:

- `Scrape Case/scrape_db.json`
- `Scrape Case/pt-br/southamerica/produtos/**/models/**/content.md`
- model asset directories under those same source folders

`parse_content_md()` currently extracts:

- `title`
- `category`
- `description`
- `summary_specs`
- `tech_groups`
- `assets_local`

This is enough data to generate production-safe metadata and structured data directly in Python. Phase 3 does not need a new content backend; it needs better use of the existing inputs.

## Content Trust Findings

The good news is that the generated product pages largely mirror the current `content.md` source faithfully for title, description, and visible specs. That means the content drift problem is not random mutation during rendering; it is primarily a source-quality and normalization problem.

The problems visible from the sample set are:

- mixed naming conventions in source titles, such as `Serie 2`, `Série 2`, `Series 2`, and English model descriptors like `Mass Excavator`
- category/model naming inconsistencies between category page context and product title context
- malformed quick-spec labels, for example the `580N` page ships a `Potência Bruta` label with invisible leading characters
- some technical spec values are truncated at line breaks because `parse_content_md()` reads only single markdown bullet lines and does not join continuation lines
- the generator uses `title.split()[0]` and `title.split()[1]` to build the final CTA heading, which can produce awkward or incomplete machine references for long model names

These issues do not all need a full editorial rewrite. The high-value production move is to prevent obvious trust-breaking artifacts from shipping and to define one repeatable source-vs-output audit for representative categories and models.

## Category And Catalog Page Constraints

Category pages and the products index have less structured source content than product pages. They still need production-safe metadata and canonical tags, but they will probably require derived descriptions rather than scraped long-form copy.

Current derivation options already available in code:

- category name
- category badge
- model count
- first model image

That is enough to synthesize honest SEO descriptions such as:

- category scope
- available model count
- official dealer / support positioning

The same applies to `/produtos/`, which can derive metadata from category count and total model count.

## Runtime SEO Dependency Risk

`setupSeoEnhancements()` is still valuable as a defensive fallback, but it is fragile as a primary mechanism:

- it derives description from the first paragraph under `<main>`
- it derives image from the first image under `<main>`
- it derives breadcrumb schema from DOM structure
- it only emits `Product` schema for routes matching `/produtos/{categoria}/{modelo}/`
- it mutates metadata after load instead of guaranteeing it in delivered HTML

Once the generator emits correct metadata, the runtime should stop being the source of truth for generated pages. At minimum, Phase 3 should ensure:

- source HTML is already SEO-complete for representative generated routes
- runtime enhancement does not override correct generated metadata with weaker DOM-derived values
- any remaining runtime behavior is strictly fallback or additive

## Recommended Plan Shape

The safest execution order is:

1. generator-level metadata and schema foundations
2. content trust normalization and representative source/output audit
3. runtime fallback reduction plus final verification on source HTML and browser behavior

That sequence matches the actual risk surface:

- first make generated HTML correct
- then make the machine content trustworthy
- then ensure the runtime is no longer masking generator defects

## Validation Architecture

Validation for this phase should prove both SEO completeness and content trust from the shipped HTML, not only from a hydrated browser DOM.

- Build gate: run `npm run build`
- Generation gate: run `python3 generate_pages.py` and confirm representative generated files update as expected
- Source-HTML inspection: verify representative pages contain description, canonical, OG/Twitter tags, and JSON-LD directly in file contents before JavaScript runs
- Route coverage:
  - `/produtos/`
  - one representative category such as `/produtos/retroescavadeiras/`
  - multiple representative products including one simple model and one long-name model such as:
    - `/produtos/retroescavadeiras/580n/`
    - `/produtos/escavadeiras-hidraulicas/cx220c-s2/`
    - `/produtos/escavadeiras-hidraulicas/cx240c-me/`
- Content audit: compare sampled generated output against the matching `content.md` and `scrape_db.json` source for title, category, description, summary specs, and major trust-sensitive labels
- Runtime check: open representative routes in the browser and confirm the final DOM still reflects the intended canonical/schema/meta state without double-injecting contradictory values
- Negative checks:
  - no representative generated page depends on runtime injection for its first valid canonical/meta/schema presence
  - no representative page ships obvious malformed labels, truncated spec fragments, or category/model mismatch in the visible hero and breadcrumb

The acceptance bar for Phase 3 should be that a crawler reading the shipped file and a user reading the visible page both see the same machine identity and the same trustworthy page description.

## Risks And Dependencies

- Category and catalog descriptions will likely need derived copy because there is no category-level long-form source file today.
- Some source `content.md` files already contain inconsistent naming or formatting; Phase 3 should normalize launch-visible output but should not turn into a full editorial rewrite across all 32 models.
- The asset pipeline remains nondeterministic because `copy_assets()` uses unsorted `iterdir()` order, but that belongs mainly to Phase 4 unless it directly blocks stable OG/image selection here.
- The generated pages still load third-party icons and fonts; this is not the main Phase 3 concern unless it blocks source HTML completeness.

## Open Questions / Assumptions

- Assumption: canonical URLs should use the live production host `https://iblmaquinas.com.br` for generated routes, matching `index.html` and `mobile/index.html`.
- Assumption: Phase 3 should preserve existing route paths and slug shapes even if some source titles are linguistically inconsistent.
- Assumption: visible copy cleanup should focus on trust-breaking artifacts and machine mismatch, not a full content rewrite for every product.
- Open question: should OG images keep using the first model asset, or should Phase 3 only stabilize the metadata plumbing and leave deterministic asset choice to Phase 4?
