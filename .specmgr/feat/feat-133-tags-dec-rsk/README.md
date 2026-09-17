---
classification: null
created: '2026-09-17 07:38:35.189+02:00'
id: feat-133-tags-dec-rsk
status: planning
type: feat
updated: '2026-09-17 07:38:35.189+02:00'
version: 1.0.0
---

# Feature: Add Tags Section to dec and rsk Artifacts

## Plan

### Overview

`req` documents already support an optional, free-form `## Tags` section (a bullet list of labels for grouping/filtering requirements). No other domain has an equivalent. This feature adds the same optional `## Tags` section to `dec` and `rsk`, giving authors a cheap, explicit keyword signal on decisions and risks, and giving the related-artifact similarity engine (feat-134) an extra structured input beyond raw body text.

### Requirements

- REQ-001: `dec` documents may optionally include a `## Tags` section, structurally identical to `req`'s existing `Tags` model (bullet list of free-form labels, `MarkdownListItemWithNotes` items, `min_length=1` when the section is present).
- REQ-002: `rsk` documents may optionally include a `## Tags` section with the same structure.
- REQ-003: Adding `## Tags` must not require any change to any other domain's schema, and must not break parsing of existing `dec`/`rsk` documents that lack the section (it is optional).

### Acceptance Criteria

- [ ] ACC-001: A `dec` document with a `## Tags` section parses, validates, and round-trips through `create_dec`/`get_dec`/`validate` (`type="dec"`).
- [ ] ACC-002: A `rsk` document with a `## Tags` section parses, validates, and round-trips through `create_rsk`/`get_rsk`/`validate` (`type="rsk"`).
- [ ] ACC-003: Existing `dec`/`rsk` documents without `## Tags` continue to parse unchanged.
- [ ] ACC-004: `get_dec_template`/`get_dec_example` and `get_rsk_template`/`get_rsk_example` show `## Tags` as populated example content.
- [ ] ACC-005: `specmgr://dec/schema` and `specmgr://rsk/schema` document the new section.

### Scope

#### Included

- `dec/models/v1/body.py` and `rsk/models/v1/body.py`: new `Tags` model plus optional field on `DecBody`/`RskBody`.
- Schema version bump for both domains, per existing project convention.
- Template/example/schema-resource updates for both domains.
- `dec`/`rsk` create/update prompt instruction updates mentioning Tags as optional (mirroring `req`'s prompt text).
- Unit tests for parsing/validation/rendering of the new section in both domains.

#### Explicitly Out Of Scope

- Tags on any domain other than `dec`/`rsk`.
- Any similarity/search/discovery mechanism that consumes Tags -- tracked separately in feat-134-related-artifact-similarity (issue #134).
- Any closed vocabulary or validation of tag values -- tags stay fully free-form, exactly like `req`'s.

### Dependencies

#### Depends On

- None.

#### Blocks

- None. feat-134 does not require this feature to ship first -- Tags, once present, are simply part of the raw body text feat-134 already plans to embed generically; feat-134 does not depend on Tags existing on dec/rsk to function.

### Design Notes

Reuse `req/models/v1/body.py`'s `Tags` class as the template: a `MarkdownSection2` subclass with an `items: list[MarkdownListItemWithNotes]` field (`min_length=1`), documented as `## Tags` -- a bullet list of free-form labels for grouping/filtering. Confirm the project's existing convention for schema version bumps on an optional-field addition (check prior precedent, e.g. how `req`'s own version was bumped when `## Tags` was first added to it, if recoverable from history) before picking `dec`/`rsk`'s new version numbers.

### Related Decisions

- None yet.

### Task List

#### Phase 1: Schema

- [ ] Task 1.1: Add `Tags` model to `dec/models/v1/body.py`, wire as optional field on `DecBody`, update parser section ordering.
- [ ] Task 1.2: Add `Tags` model to `rsk/models/v1/body.py`, wire as optional field on `RskBody`, update parser section ordering.
- [ ] Task 1.3: Bump `dec` and `rsk` schema `version` per project convention.

#### Phase 2: Templates / Examples / Resources

- [ ] Task 2.1: Update `get_dec_template`/`get_dec_example` data files.
- [ ] Task 2.2: Update `get_rsk_template`/`get_rsk_example` data files.
- [ ] Task 2.3: Update `specmgr://dec/schema` and `specmgr://rsk/schema` resource content.

#### Phase 3: Prompts

- [ ] Task 3.1: Update `dec/prompts/create_dec`/`update_dec` instructions.
- [ ] Task 3.2: Update `rsk/prompts/create_risk`/`update_risk` instructions.

#### Phase 4: Tests & Docs

- [ ] Task 4.1: Unit tests for `Tags` parsing/validation/rendering in `dec`.
- [ ] Task 4.2: Unit tests for `Tags` parsing/validation/rendering in `rsk`.
- [ ] Task 4.3: Update `AGENTS.md`'s `dec`/`rsk` bullets.
- [ ] Task 4.4: Regenerate docs via `specmgr docs`.

## Progress

### Current Status

**As of 2026-09-17**: Planning stage; not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #133 to track adding optional `## Tags` sections to `dec` and `rsk`, split out of a broader related-artifact discovery request (see feat-134-related-artifact-similarity, issue #134, for the companion similarity-engine feature).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Split from the similarity-engine feature

Tags-on-dec/rsk was split into its own small, independent feature/issue (#133) rather than bundled with the larger embedding-similarity engine (#134/feat-134), since it has no new dependencies and can ship independently.

### Related PRs / Commits

- [Issue #133](https://github.com/dfch/biz.dfch.SpecMgr/issues/133): tracking issue for this feature.

### More Information

None.
