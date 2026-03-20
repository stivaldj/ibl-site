# Requirements: VARIANT

**Defined:** 2026-03-20
**Core Value:** Prospects can confidently evaluate equipment and convert into qualified opportunities through a trustworthy, fully functional website.

## v1 Requirements

Requirements for this production-hardening release. These focus on making the current site launchable and safe to extend.

### Experience

- [ ] **EXP-01**: Visitor can navigate homepage, catalog, category pages, and product pages without broken layout, dead-end UI, or misleading interaction patterns
- [ ] **EXP-02**: Visitor gets a coherent and trustworthy visual experience across desktop and mobile entry points
- [ ] **EXP-03**: Visitor can complete the main browsing journey from homepage to category to product detail without UX friction that blocks evaluation
- [ ] **EXP-04**: Visitor can use launch-critical CTAs and navigation elements without placeholder or non-functional links

### Lead Generation

- [ ] **LEAD-01**: Visitor can submit lead intent from homepage and product contexts through a working CTA flow
- [ ] **LEAD-02**: Lead payload sent by webhook includes the fields needed to create opportunities in `ibl-ai-os`
- [ ] **LEAD-03**: Lead submission failures are detectable through clear frontend handling or operational logging paths
- [ ] **LEAD-04**: Lead capture behavior is consistent across desktop and mobile variants

### Content And SEO

- [ ] **SEO-01**: Category and product pages expose accurate metadata, canonical information, and structured data in a production-safe way
- [ ] **SEO-02**: Product content, labels, and machine-specific information remain internally consistent across generated pages
- [ ] **SEO-03**: Visitor can trust that page content matches the machine being viewed, without obvious copy drift or stale artifacts
- [ ] **SEO-04**: Launch-critical pages have stable indexable output that does not depend on fragile client-side metadata injection

### Frontend Reliability

- [ ] **FE-01**: Shared frontend behavior works predictably across homepage, category pages, product pages, and mobile entry points
- [ ] **FE-02**: Critical browser-side logic avoids obvious runtime errors, selector fragility, and dead code that obscures the real production paths
- [ ] **FE-03**: Assets required for launch render correctly without broken references or stale generated leftovers

### Generation Pipeline

- [ ] **GEN-01**: Static generation flow produces reproducible catalog and product pages from source content and assets
- [ ] **GEN-02**: Content and asset generation steps are documented well enough to regenerate production output safely
- [ ] **GEN-03**: Generation process does not silently preserve stale files that can leak outdated content into production

### Quality And Operations

- [ ] **OPS-01**: Project has a practical launch-readiness checklist covering build, smoke test, mobile check, and lead-flow verification
- [ ] **OPS-02**: Production-critical behaviors can be validated before future milestones continue
- [ ] **OPS-03**: Known technical debt that would block safe continuation is identified and reduced to an acceptable level

## v2 Requirements

Deferred until the production baseline is stable.

### Feature Expansion

- **FTR-01**: Site adds broader conversion or merchandising features beyond launch-critical needs
- **FTR-02**: Site introduces major new customer flows not required for current production readiness
- **FTR-03**: Site adds richer backoffice, personalization, or advanced analytics capabilities

### Platform Evolution

- **PLT-01**: Site migrates to a significantly different application architecture or backend model
- **PLT-02**: Site replaces the current static-generation approach with a full rewrite

## Out of Scope

| Feature | Reason |
|---------|--------|
| Broad redesign unrelated to trust, usability, or launch quality | The goal is production hardening, not cosmetic reinvention |
| Major net-new feature roadmap before stabilization | New features would compound existing quality issues |
| Full-stack rebuild or framework migration | Too risky and slow for the current milestone |
| Nice-to-have experiments and growth ideas | They do not materially improve production readiness right now |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXP-01 | Phase 1 - Site Experience Stabilization | Completed |
| EXP-02 | Phase 1 - Site Experience Stabilization | Completed |
| EXP-03 | Phase 1 - Site Experience Stabilization | Completed |
| EXP-04 | Phase 1 - Site Experience Stabilization | Completed |
| LEAD-01 | Phase 2 - Lead Flow Hardening | Completed |
| LEAD-02 | Phase 2 - Lead Flow Hardening | Completed |
| LEAD-03 | Phase 2 - Lead Flow Hardening | Completed |
| LEAD-04 | Phase 2 - Lead Flow Hardening | Completed |
| SEO-01 | Phase 3 - SEO And Content Trust Hardening | Completed |
| SEO-02 | Phase 3 - SEO And Content Trust Hardening | Completed |
| SEO-03 | Phase 3 - SEO And Content Trust Hardening | Completed |
| SEO-04 | Phase 3 - SEO And Content Trust Hardening | Completed |
| FE-01 | Phase 1 - Site Experience Stabilization | Completed |
| FE-02 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |
| FE-03 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |
| GEN-01 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |
| GEN-02 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |
| GEN-03 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |
| OPS-01 | Phase 5 - Launch Verification And Operations Gate | Completed |
| OPS-02 | Phase 5 - Launch Verification And Operations Gate | Completed |
| OPS-03 | Phase 4 - Generation And Frontend Reliability Stabilization | Completed |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after roadmap traceability update*
