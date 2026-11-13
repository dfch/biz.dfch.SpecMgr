---
status: accepted
decision-makers: dfch
id: bc5e18ad-6bbf-4265-bae4-3e34984a2d29
version: 1.0.0
---

# Generic base frontmatter model for markdown document types (models/md/frontmatter.py)

## Context and Problem Statement

feat-5-md-model-parser's REQ-006 needs a typed frontmatter model layered on top of the already-working python-frontmatter-based stripping (frontmatter.loads(text).content/.metadata). The only existing typed frontmatter model, AdrFrontmatter (models/adr/v1/frontmatter.py), is tailored specifically to the ADR/MADR shape (id, version, status, date, decision_makers, consulted, informed) and has no document-type discriminator. As additional document types (uc, req, ...) are introduced on top of the generic heading-recursion engine (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae), each would otherwise need to hand-roll its own frontmatter model from scratch, duplicating the same handful of core fields (id, created, updated, status, version) per type -- the same scaling problem 832cd6c1 already solved for section bodies, just one layer up in the document.

## Decision Drivers

Reusability of core frontmatter fields across current and future document types without duplicating them per type; ability to discriminate which document type a frontmatter block belongs to before/without knowing which concrete body model to parse into; preserving models/md/'s existing no-dependency-on-models/adr/v1/ invariant (ADR 832cd6c1); not forcing an unrelated, unscoped migration of the already-shipped, MADR-specific AdrFrontmatter; avoiding a new cross-cutting shared-validator module before there is a second consumer that actually needs it.

## Considered Options

Option 1 (adopted): a generic base class MarkdownFrontmatter (models/md/frontmatter.py) with core fields id, type, created, updated, status, version; each document type subclasses it and adds its own fields, pinning `type` to a fixed Literal[...] value as a discriminator; AdrFrontmatter stays independent and unconverted for now. Option 2: no shared base at all -- each document type defines its own independent frontmatter model from scratch, exactly as AdrFrontmatter does today. Option 3: retrofit AdrFrontmatter immediately to subclass the new base.

## Decision Outcome

Adopt Option 1. Add models/md/frontmatter.py defining MarkdownFrontmatter(BaseModel) with exactly these core fields: id: str | None (specmgr-assigned identifier), type: str (document-type discriminator, overridden by each subclass as a fixed Literal[...], e.g. Literal["uc"]), created: str | None, updated: str | None, status: str (default "draft"), version: str (schema version, mirroring AdrFrontmatter's CURRENT_SCHEMA_VERSION pattern but as its own constant local to models/md/). Document-type-specific frontmatter models (e.g. a future UcFrontmatter) subclass MarkdownFrontmatter, add their own fields, and pin `type` to their own fixed Literal value. models/md/frontmatter.py owns its own small, private validator helpers (blank-to-none, status-default-on-blank, version-format validation), independent of models/adr/v1/_util.py -- no shared cross-package validator module is introduced at this time. AdrFrontmatter (models/adr/v1/frontmatter.py) is explicitly left unchanged and is NOT converted to subclass MarkdownFrontmatter as part of this decision.

### Consequences

Future document types (uc, req, ...) get a consistent, reusable core frontmatter shape plus a type discriminator without hand-rolling a new model from scratch each time, and a generic loader can eventually dispatch on `type` alone before knowing which concrete body model applies. models/md/ remains free of any import dependency on models/adr/v1/, consistent with 832cd6c1. This does introduce some near-duplicate validator logic between models/adr/v1/_util.py and its models/md/ counterpart, and leaves two independent, not-yet-unified frontmatter model families in the codebase (ADR's vs. everything else's) -- an accepted, explicitly temporary inconsistency; a later decision may converge AdrFrontmatter onto MarkdownFrontmatter once there is appetite to touch the ADR pipeline, but that is not decided or scheduled here.

### Confirmation

Verify models/md/frontmatter.py has no import dependency on models/adr/v1/. Verify MarkdownFrontmatter declares exactly id, type, created, updated, status, version as its core fields. Verify a concrete document-type subclass can narrow `type` to a fixed Literal[...] value and that Pydantic rejects a mismatched `type` value at validation time. Verify models/adr/v1/frontmatter.py (AdrFrontmatter) is untouched by this change.

## More Information

Tracked in .specmgr/feat/feat-5-md-model-parser/README.md (GitHub issue #5), REQ-006/Task 4.1. Related: ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae (generic heading-recursion engine this frontmatter model sits alongside, models/md/'s no-dependency-on-models/adr/v1/ invariant).
