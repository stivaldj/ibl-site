# Production Hardening Roadmap: VARIANT

**Prepared:** 2026-03-20
**Initiative type:** Brownfield production-readiness hardening
**Primary reference:** `.planning/PROJECT.md`

## Intent

This roadmap hardens the existing site for production launch. It prioritizes visible defects, trust, lead reliability, SEO correctness, generation stability, and repeatable launch verification before any non-essential additions.

Only launch-critical additions are allowed, and only when they are required to make the existing site production-safe.

## Sequencing Principles

1. Fix the most visible customer-facing breakage first.
2. Stabilize lead capture before expanding anything around it.
3. Remove trust and SEO fragility from generated pages before launch.
4. Reduce generator, asset, and runtime fragility so future work does not compound current risks.
5. End with an explicit launch gate instead of ad hoc validation.

## Phase Summary

| Phase | Name | Primary outcome | Requirements |
|-------|------|-----------------|--------------|
| Phase 1 | Site Experience Stabilization | Core browsing and CTA experience works cleanly across desktop and mobile | EXP-01, EXP-02, EXP-03, EXP-04, FE-01 |
| Phase 2 | Lead Flow Hardening | Lead capture becomes reliable, consistent, and observable | LEAD-01, LEAD-02, LEAD-03, LEAD-04 |
| Phase 3 | SEO And Content Trust Hardening | Generated pages ship trustworthy, indexable, machine-correct content | SEO-01, SEO-02, SEO-03, SEO-04 |
| Phase 4 | Generation And Frontend Reliability Stabilization | Frontend/runtime and generation pipeline become deterministic and safe to maintain | FE-02, FE-03, GEN-01, GEN-02, GEN-03, OPS-03 |
| Phase 5 | Launch Verification And Operations Gate | Launch readiness is validated through a repeatable production check | OPS-01, OPS-02 |

## Phase Details

### Phase 1: Site Experience Stabilization

**Goal:** Remove the most visible browsing, layout, and navigation defects across the existing homepage, catalog, category pages, product pages, and mobile entry points.

**Why first:** The current site already functions, but visible UX defects and broken affordances undermine trust immediately. Those issues should be stabilized before deeper hardening work.

**Requirements covered:** EXP-01, EXP-02, EXP-03, EXP-04, FE-01

**Work focus:**
- Audit homepage, catalog, category, product, and mobile routes for layout, navigation, CTA, and interaction failures.
- Fix dead-end UI, misleading affordances, placeholder links, and inconsistent entry-point behavior.
- Normalize shared browsing behavior where homepage, catalog, product, and mobile paths drift today.

**Observable success criteria:**
1. Representative homepage, catalog, category, product, and mobile routes render without obvious overlap, clipping, dead-end UI, or broken interaction states.
2. The main browse journey from homepage to category to product detail completes cleanly on desktop and mobile without blockers.
3. Launch-critical CTAs and navigation targets resolve to real destinations or explicit non-interactive states instead of placeholders.
4. Shared browsing interactions behave consistently enough that the same core actions work across homepage, generated pages, and mobile entry points.

**Execution progress:**
- Plan `01-01` completed on 2026-03-20. Desktop `/` and mobile `/mobile/` entry shells now share aligned browse/contact CTAs, explicit disabled placeholder states, and a local coverage summary panel that keeps shell-level smoke checks clean.
- Plan `01-02` completed on 2026-03-20. Generated catalog/category/product templates now ship real browse-safe actions, shared title/mobile CTA guards, and a verified launch-category route sweep across `/produtos/**`.
- Plan `01-03` completed on 2026-03-20. Shared browse-runtime sections in `main.js`, `webapp/main.js`, and `mobile/main.js` now agree on delegated CTA tracking, page-level breadcrumb schema targeting, and representative desktop/mobile route validation through `/produtos/retroescavadeiras/580n/`.
- Plan `01-04` completed on 2026-03-20. Generated catalog/category/product contact CTAs now resolve to the real homepage lead anchor `/#captacao-lead`, representative generated CTA clicks land on the homepage lead section, and Phase 1 is fully closed.

### Phase 2: Lead Flow Hardening

**Goal:** Make existing lead capture flows dependable enough for production use and safe enough to operate.

**Why here:** Once users can browse the site cleanly, the next launch risk is losing or silently failing lead submissions.

**Requirements covered:** LEAD-01, LEAD-02, LEAD-03, LEAD-04

**Work focus:**
- Validate homepage and product-context CTA lead flows end to end.
- Confirm payload shape matches what `ibl-ai-os` needs for opportunity creation.
- Add failure handling and operational visibility so broken submissions are detectable.
- Eliminate desktop/mobile inconsistencies in lead capture behavior.

**Observable success criteria:**
1. Lead intent can be submitted successfully from both homepage and product contexts on representative desktop and mobile paths.
2. The webhook payload contains the required opportunity-creation fields and uses a stable contract.
3. Failed submissions surface through clear frontend feedback, operational logging, or another defined detection path instead of failing silently.
4. Desktop and mobile lead flows follow the same launch-approved behavior for field handling, CTA behavior, and submission outcomes.

**Execution progress:**
- Plan `02-01` completed on 2026-03-20. The repo now includes a local mock lead webhook harness with success/failure modes, curl-verified JSON capture, a package command at `npm run lead:webhook:mock`, and `.env.example` guidance that points Phase 2 verification at `http://127.0.0.1:8787/lead` instead of assuming a live external endpoint.
- Plan `02-02` completed on 2026-03-20. `main.js`, `webapp/main.js`, and `mobile/main.js` now share one lead payload builder and one explicit submit-result contract, browser verification confirmed homepage/mobile/product payload parity against the local mock webhook, and the missing-webhook plus 500-webhook paths now surface distinct `skipped` and `failure` runtime states.
- Plan `02-03` completed on 2026-03-20. Homepage and product forms now tell the truth about webhook success/skips/failures, `?ops=1` exposes submitted/skipped/failed/pending/SLA-risk lead states with immediate updates, and the final Phase 2 browser sweep passed across `/`, `/mobile/`, and `/produtos/retroescavadeiras/580n/` in both default desktop and 430px-wide mobile verification.
- Plan `02-04` completed on 2026-03-20. The last SLA-risk false positive is gone because all three runtime copies now key off `contact_status`, and focused `?ops=1` verification proved contacted leads stop contributing to counts, warnings, and `lead_sla_risk` telemetry on `/`, `/mobile/`, and `/produtos/retroescavadeiras/580n/` while a real stale uncontacted lead still triggers the intended alert path.
- Phase 2 is complete. Lead feedback, fallback behavior, payload parity, and local launch observability now meet the production-hardening bar defined for this phase without the previous contacted-lead SLA-risk bug.

### Phase 3: SEO And Content Trust Hardening

**Goal:** Ship generated category and product pages with trustworthy metadata and machine-correct content directly in production HTML.

**Why here:** Trust and search readiness are currently weakened by runtime SEO injection and content drift. Those risks should be removed before launch.

**Requirements covered:** SEO-01, SEO-02, SEO-03, SEO-04

**Work focus:**
- Move launch-critical metadata, canonical tags, and structured data into the generation path where needed.
- Correct breadcrumb/schema/canonical behavior on generated pages.
- Audit product/category copy against source content to reduce drift and stale artifacts.
- Ensure launch-critical pages remain indexable without depending on fragile client-side SEO enhancement.

**Observable success criteria:**
1. Representative category and product pages contain correct metadata, canonical information, and structured data in the shipped HTML.
2. Machine names, labels, specs, and descriptive copy remain internally consistent across generated pages for sampled launch categories.
3. No representative launch page shows obvious machine mismatch, stale copy artifacts, or trust-breaking content drift.
4. Launch-critical generated pages remain SEO-complete and indexable even when client-side metadata enhancement does not run.

**Execution progress:**
- Plan `03-01` completed on 2026-03-20. `generate_pages.py` now emits canonical, description, Open Graph, Twitter, and JSON-LD directly into generated catalog, category, and product HTML, and representative source inspection proved the shipped files are SEO-complete before runtime execution.
- Plan `03-02` completed on 2026-03-20. Generated product output now normalizes malformed quick-spec labels, preserves continuation lines in visible spec values, and uses full model titles in CTA context, with representative audits confirming source/output alignment against `scrape_db.json` and `content.md`.
- Plan `03-03` completed on 2026-03-20. `main.js`, `webapp/main.js`, and `mobile/main.js` now treat generated-route SEO as fallback-only when `/produtos/**` already ships the Phase 3 head baseline, and representative browser verification confirmed the final DOM keeps the same canonical/meta/schema state as the shipped HTML while adding `FAQPage` only as an intentional product-page supplement.
- Phase 3 is complete. Verification passed against `SEO-01`, `SEO-02`, `SEO-03`, and `SEO-04`, confirming generated pages are source-HTML SEO-complete, machine-correct on the sampled launch set, and no longer depend on runtime metadata injection for first-pass indexability.

### Phase 4: Generation And Frontend Reliability Stabilization

**Goal:** Reduce the runtime, asset, and generation fragility that would otherwise keep reintroducing production defects.

**Why here:** After the site is usable, converting it into a stable operating baseline requires deterministic generation, cleaner runtime paths, and removal of blocking technical debt.

**Requirements covered:** FE-02, FE-03, GEN-01, GEN-02, GEN-03, OPS-03

**Work focus:**
- Harden critical browser-side logic and remove or quarantine misleading dead production surface area.
- Fix broken asset references, stale generated leftovers, and nondeterministic asset selection.
- Make generation output reproducible and safer to rerun.
- Document the real regeneration workflow and bound the remaining technical debt that could block future phases.

**Observable success criteria:**
1. Representative homepage, generated catalog pages, product pages, and mobile routes avoid critical runtime errors and known fragile selectors in normal launch flows.
2. Launch-critical assets resolve correctly on representative routes without broken references or stale leftovers appearing in served output.
3. Re-running generation with unchanged inputs produces stable output rather than silent drift from ordering or stale-file retention.
4. The regeneration workflow is documented clearly enough for an operator to rebuild launch content and assets safely.
5. Technical debt that would block safe continuation is either reduced within this phase or captured as an explicit bounded remainder that no longer blocks launch.

**Execution progress:**
- Plan `04-01` completed on 2026-03-20. `generate_pages.py` now sorts and synchronizes model assets deterministically, audited stale leftovers are removed during sync, and the helper scripts now expose explicit refresh and failure semantics through `--sync`, `--force`, `--dry-run`, and `--strict`.
- Plan `04-02` completed on 2026-03-20. `vite build` now packages the full launch surface, including `produtos/**`, into `dist/`, and the old Vite starter scaffold has been quarantined so maintainers stop treating `src/` as a live production path.
- Plan `04-03` completed on 2026-03-20. `docs/OPERATIONS.md` now defines one authoritative rebuild workflow, package scripts expose the supported commands directly, and the documented `npm run rebuild:site` path passed end-to-end with representative packaged-route verification against `dist/`.
- Phase 4 is complete. Verification passed for `FE-02`, `FE-03`, `GEN-01`, `GEN-02`, `GEN-03`, and `OPS-03`, confirming the repo now has deterministic enough reruns, honest packaging, and explicit operational rebuild guidance for launch continuation.

### Phase 5: Launch Verification And Operations Gate

**Goal:** Define and use a repeatable release gate for the hardened site before future milestone work resumes.

**Why last:** Launch validation should verify the hardened system that emerges from Phases 1 through 4, not the pre-hardened baseline.

**Requirements covered:** OPS-01, OPS-02

**Work focus:**
- Create the practical launch-readiness checklist.
- Define smoke-test coverage for homepage, catalog, product, and mobile entry points.
- Include lead-flow verification in the release gate.
- Capture what evidence is required to declare the site ready for production continuation.

**Observable success criteria:**
1. A single launch-readiness checklist exists covering build verification, smoke testing, mobile validation, and lead-flow checks.
2. Production-critical behaviors can be validated through named steps on representative homepage, catalog, product, and mobile routes.
3. Lead-flow verification is part of the release gate rather than a separate informal check.
4. Readiness can be declared against explicit pass criteria and evidence instead of ad hoc judgment.

## Requirement Coverage Matrix

| Requirement | Assigned phase |
|-------------|----------------|
| EXP-01 | Phase 1 - Site Experience Stabilization |
| EXP-02 | Phase 1 - Site Experience Stabilization |
| EXP-03 | Phase 1 - Site Experience Stabilization |
| EXP-04 | Phase 1 - Site Experience Stabilization |
| FE-01 | Phase 1 - Site Experience Stabilization |
| LEAD-01 | Phase 2 - Lead Flow Hardening |
| LEAD-02 | Phase 2 - Lead Flow Hardening |
| LEAD-03 | Phase 2 - Lead Flow Hardening |
| LEAD-04 | Phase 2 - Lead Flow Hardening |
| SEO-01 | Phase 3 - SEO And Content Trust Hardening |
| SEO-02 | Phase 3 - SEO And Content Trust Hardening |
| SEO-03 | Phase 3 - SEO And Content Trust Hardening |
| SEO-04 | Phase 3 - SEO And Content Trust Hardening |
| FE-02 | Phase 4 - Generation And Frontend Reliability Stabilization |
| FE-03 | Phase 4 - Generation And Frontend Reliability Stabilization |
| GEN-01 | Phase 4 - Generation And Frontend Reliability Stabilization |
| GEN-02 | Phase 4 - Generation And Frontend Reliability Stabilization |
| GEN-03 | Phase 4 - Generation And Frontend Reliability Stabilization |
| OPS-03 | Phase 4 - Generation And Frontend Reliability Stabilization |
| OPS-01 | Phase 5 - Launch Verification And Operations Gate |
| OPS-02 | Phase 5 - Launch Verification And Operations Gate |

## Exit Condition For This Roadmap

This roadmap is complete when each phase has a detailed execution plan and all 21 v1 requirements remain mapped to exactly one phase without scope leakage into deferred v2 work.

---
*Last updated: 2026-03-20 after Phase 4 verification*
