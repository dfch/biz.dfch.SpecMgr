---
classification: null
created: '2026-09-17 07:38:35.189+02:00'
id: feat-133-tags-dec-rsk
status: planning
type: feat
updated: '2026-09-17 15:00:00.000+02:00'
version: 1.0.0
---

# Feature: Add Tags Section to rsk Artifacts (originally dec and rsk; see Overview)

## Plan

### Overview

`req` documents already support an optional, free-form `## Tags` section (a bullet list of labels for grouping/filtering requirements). No other domain has an equivalent. This feature was originally scoped to add the same optional `## Tags` section to both `dec` and `rsk`, giving authors a cheap, explicit keyword signal on decisions and risks, and giving the related-artifact similarity engine (feat-134) an extra structured input beyond raw body text. **This feature is now RSK-only**: the DEC half was absorbed into and shipped as part of `feat-29-dec-source-roles` (GitHub issue #29), since that feature was touching `dec/models/v1/body.py` in the same pass anyway (see this file's own "Decisions Made" log for the rescoping rationale). Only the `rsk` half of the original scope remains here.

### Requirements

- REQ-001: `rsk` documents may optionally include a `## Tags` section, structurally identical to `req`'s existing `Tags` model (bullet list of free-form labels, `MarkdownListItemWithNotes` items, `min_length=1` when the section is present).
- REQ-002: Adding `## Tags` must not require any change to any other domain's schema, and must not break parsing of existing `rsk` documents that lack the section (it is optional).

### Acceptance Criteria

- [ ] ACC-001: A `rsk` document with a `## Tags` section parses, validates, and round-trips through `create_rsk`/`get_rsk`/`validate` (`type="rsk"`).
- [ ] ACC-002: Existing `rsk` documents without `## Tags` continue to parse unchanged.
- [ ] ACC-003: `get_rsk_template`/`get_rsk_example` show `## Tags` as populated example content.
- [ ] ACC-004: `specmgr://rsk/schema` documents the new section.

### Scope

#### Included

- `rsk/models/v1/body.py`: new `Tags` model plus optional field on `RskBody`.
- Schema version bump, per existing project convention.
- Template/example/schema-resource updates.
- `rsk` create/update prompt instruction updates mentioning Tags as optional (mirroring `req`'s prompt text).
- Unit tests for parsing/validation/rendering of the new section.

#### Explicitly Out Of Scope

- Tags on any domain other than `rsk`.
- `dec`'s own `## Tags` section -- shipped in `feat-29-dec-source-roles`
  (GitHub issue #29), which absorbed this feature's original DEC half
  since it was already touching `dec/models/v1/body.py`. See that
  feature's own README for the full DEC-side design.
- Any similarity/search/discovery mechanism that consumes Tags -- tracked separately in feat-134-related-artifact-similarity (issue #134).
- Any closed vocabulary or validation of tag values -- tags stay fully free-form, exactly like `req`'s.

### Dependencies

#### Depends On

- None.

#### Blocks

- None. feat-134 does not require this feature to ship first -- Tags, once present, are simply part of the raw body text feat-134 already plans to embed generically; feat-134 does not depend on Tags existing on dec/rsk to function.

### Design Notes

Reuse `req/models/v1/body.py`'s `Tags` class as the template: a `MarkdownSection2` subclass with an `items: list[MarkdownListItemWithNotes]` field (`min_length=1`), documented as `## Tags` -- a bullet list of free-form labels for grouping/filtering. Confirm the project's existing convention for schema version bumps on an optional-field addition (check prior precedent, e.g. how `req`'s own version was bumped when `## Tags` was first added to it, if recoverable from history) before picking `rsk`'s new version number.

Note (added 2026-09-17, rescoping): the original design intended to reuse the very same `req`-derived pattern for both `dec` and `rsk`. `feat-29-dec-source-roles` shipped the DEC half using a different mechanism than a plain copy-paste of `req`'s `Tags` class -- it introduced a shared `models/md/common_sections.py` base-class module for `Source`/RASCI sections and, while it was there, added `dec`'s own `Tags` model directly (not derived from the new shared bases, since `Tags` itself was not part of that feature's shared-base-class scope). This feature's own `rsk`-side implementation should still follow this section's original precedent-reuse guidance (copy `req`'s `Tags` shape directly) -- there is no shared `Tags` base class to subclass.

### Related Decisions

- None yet.

### Task List

#### Phase 1: Schema

- [ ] Task 1.1: Add `Tags` model to `rsk/models/v1/body.py`, wire as optional field on `RskBody`, update parser section ordering.
- [ ] Task 1.2: Bump `rsk` schema `version` per project convention.

  (Former Task 1.1, the `dec`-side twin of the above, shipped as part of
  `feat-29-dec-source-roles`, issue #29, and is no longer tracked here;
  former Task 1.3 covered both domains' version bumps and is now the
  single `rsk`-only Task 1.2 above.)

#### Phase 2: Templates / Examples / Resources

- [ ] Task 2.1: Update `get_rsk_template`/`get_rsk_example` data files.
- [ ] Task 2.2: Update `specmgr://rsk/schema` resource content.

  (Former Task 2.1, the `dec`-side template/example update, and the
  `dec` half of former Task 2.3's schema-resource update both shipped as
  part of `feat-29-dec-source-roles`, issue #29, and are no longer
  tracked here.)

#### Phase 3: Prompts

- [ ] Task 3.1: Update `rsk/prompts/create_risk`/`update_risk` instructions.

  (Former Task 3.1, the `dec/prompts/create_dec`/`update_dec` instruction
  update, shipped as part of `feat-29-dec-source-roles`, issue #29, and
  is no longer tracked here.)

#### Phase 4: Tests & Docs

- [ ] Task 4.1: Unit tests for `Tags` parsing/validation/rendering in `rsk`.
- [ ] Task 4.2: Update `AGENTS.md`'s `rsk` bullet.
- [ ] Task 4.3: Regenerate docs via `specmgr docs`.

  (Former Task 4.1, the `dec`-side unit tests, shipped as part of
  `feat-29-dec-source-roles`, issue #29, and is no longer tracked here;
  former Task 4.3's `dec` half of the `AGENTS.md` update also shipped
  there. Former Tasks 4.2/4.4 are renumbered 4.1/4.3 above.)

## Progress

### Current Status

**As of 2026-09-17**: Rescoped to RSK-only (see "Decisions Made" below);
planning stage, not started on the remaining `rsk`-only scope.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:01.000Z - Rescoped to RSK-only

Dropped every `dec`-related requirement/acceptance-criterion/task from
this feature's plan: the DEC half of the original scope (`## Tags` on
`dec`) shipped as part of `feat-29-dec-source-roles` (GitHub issue #29),
which absorbed it while already touching `dec/models/v1/body.py` for its
own `## Roles and Responsibilities`/`## Source` work. This feature now
tracks only the `rsk`-side `## Tags` addition. A comment was posted on
GitHub issue #133 noting the absorption. See "Decisions Made" below for
the rationale.

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #133 to track adding optional `## Tags` sections to `dec` and `rsk`, split out of a broader related-artifact discovery request (see feat-134-related-artifact-similarity, issue #134, for the companion similarity-engine feature).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:01.000Z - Rescope to RSK-only; DEC half absorbed by feat-29

`feat-29-dec-source-roles` (GitHub issue #29) independently needed to
touch `dec/models/v1/body.py` for its own `## Roles and Responsibilities`
and `## Source` sections, and its own "Decisions Made" log records the
decision to absorb this feature's DEC half (`## Tags` on `dec`) into that
pass rather than keep it as a separate cross-feature dependency (recorded
there, not here, since feat-29 is the feature that actually implemented
and shipped it). Consequence: this feature (`feat-133-tags-dec-rsk`) is
rescoped to RSK-only -- every `dec`-related requirement, acceptance
criterion, and task is dropped from this plan (not renumbered with gaps,
since nothing outside this file referenced the old numbering), and the
Overview/Scope/Design Notes sections above are updated to reflect the
narrower scope.

#### 2026-09-17 00:00:00.000Z - Split from the similarity-engine feature

Tags-on-dec/rsk was split into its own small, independent feature/issue (#133) rather than bundled with the larger embedding-similarity engine (#134/feat-134), since it has no new dependencies and can ship independently.

### Related PRs / Commits

- [Issue #133](https://github.com/dfch/biz.dfch.SpecMgr/issues/133): tracking issue for this feature.
- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29) /
  `feat-29-dec-source-roles`: shipped this feature's original DEC half
  (`## Tags` on `dec`) as part of its own Phase 2 work; see
  `.specmgr/feat/feat-29-dec-source-roles/README.md` for the implementation
  details.

### More Information

None.
