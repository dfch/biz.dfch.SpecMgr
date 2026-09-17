---
classification: null
created: '2026-09-17 14:06:49.067+02:00'
id: feat-29-dec-source-roles
status: planning
type: feat
updated: '2026-09-17 14:06:49.067+02:00'
version: 1.0.0
---

# Feature: Add `## Roles and Responsibilities`, `## Tags`, and `## Source` Sections to DEC Documents

## Plan

### Overview

GitHub issue #29 originally asked for `DecFrontmatter` to gain ADR-style attributes (examples given: `source`, `owner`) that plain decisions are missing compared to ADRs. Analysis during planning showed these examples map onto two existing, already-implemented concepts elsewhere in the codebase rather than new frontmatter fields: `owner`/`decision-makers`/`consulted`/`informed` are RASCI roles (already implemented as a body section on `sop`), and `source` is already implemented as REQ's own `## Source` body section. This feature therefore adds three new **body** sections to `dec` documents -- a mandatory `## Roles and Responsibilities` (RASCI), an optional `## Tags` (absorbed from the DEC half of `feat-133-tags-dec-rsk`, issue #133), and a mandatory `## Source` -- and refactors the underlying field/validator logic into shared base classes so `req`, `sop`, and `dec` stop duplicating structurally-identical leaf sections. `DecFrontmatter` itself is not changed.

### Requirements

- REQ-001: `DecFrontmatter` is not changed by this feature; `id`/`version`/`status` remain exactly as they are today (no `date`/`decision-makers`/`consulted`/`informed`/`source`/`owner` frontmatter fields are added).
- REQ-002: `dec` documents gain a mandatory `## Roles and Responsibilities` section: `### Accountable` (single mandatory paragraph, the decision-maker/owner) and `### Responsible` (mandatory bullet list, >=1 item) are always required once the section exists, and since the section itself is mandatory on every `dec` document, every decision always names an accountable owner; `### Support`/`### Consulted`/`### Informed` remain independently optional bullet lists that may be present with zero items.
- REQ-003: `dec` documents gain an optional `## Tags` section, structurally identical to `req`'s existing `Tags` model (bullet list of `MarkdownListItemWithNotes`, `min_length=1` when present), absorbing the DEC half of `feat-133-tags-dec-rsk` (issue #133).
- REQ-004: `dec` documents gain a mandatory `## Source` section, structurally identical in shape to `req`'s existing `## Source` (single mandatory paragraph naming the origin/authority of the decision).
- REQ-005: The three new `dec` sections appear in this exact order: `## Roles and Responsibilities`, then `## Tags`, then `## Source`, positioned after `## Decision Outcome` and before `## Related Artifacts`.
- REQ-006: `Source` and the six RASCI classes (`Accountable`/`Responsible`/`Support`/`Consulted`/`Informed`/`RolesAndResponsibilities`) are implemented via shared base classes in a new `models/md/common_sections.py` module; `req`'s existing `Source` and `sop`'s existing six RASCI classes are refactored to subclass those bases instead of duplicating field/validator definitions, and `dec`'s new classes subclass the same bases; every domain still declares and owns its own concrete class in its own package, matching the domain-first convention.
- REQ-007: No new ADR is written for the shared-base-class decision; a "Decisions Made" log entry in this feature's own README documents the rationale instead.
- REQ-008: `feat-133-tags-dec-rsk` (issue #133) is rescoped to RSK-only once this feature ships DEC's Tags section, with a note in its own README pointing at this feature, and a brief comment posted on GitHub issue #133 noting the absorption.
- REQ-009: Every phase of this feature's own Task List that touches any `src/**/*.py` file ends with a full local quality gate (`ruff format --check`, `ruff check`, `vulture`, `specmgr docs`, `specmgr mcp-docs`, `specmgr schema` for all 12 registered types plus their packaged per-domain copies, `pytest -n auto --cov=src --cov-report=`, `specmgr coverage-badge`) run and passing before that phase's own commit, since `models/md` and every domain's `models/v1`(or `v2`) package are matched by the `specmgr-schema*` pre-commit hooks' file-scope regex and force full-repo schema regeneration on every touch, not just the touched domain's own.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-002 -- a `dec` document with `## Roles and Responsibilities` present (Accountable + Responsible, optionally Support/Consulted/Informed) parses via `parse_dec`/`get_dec`, and a `dec` document missing the section entirely fails validation.
- [ ] ACC-002: Verifies REQ-003 -- a `dec` document with `## Tags` parses/validates/round-trips through `create_dec`/`get_dec`/`validate` (`type="dec"`), and a `dec` document without `## Tags` still parses successfully (optional).
- [ ] ACC-003: Verifies REQ-004 -- a `dec` document with `## Source` present parses, and a `dec` document missing `## Source` fails validation.
- [ ] ACC-004: Verifies REQ-005 -- a `dec` document with the new sections out of their required relative order fails validation.
- [ ] ACC-005: Verifies REQ-006 -- `req/models/v1/body.py::Source` and `sop/models/v1/body.py`'s six RASCI classes are refactored to subclass the new `models/md/common_sections.py` base classes, and the full existing REQ and SOP test suites still pass unchanged.
- [ ] ACC-006: Verifies REQ-006 -- `dec/models/v1/body.py::RolesAndResponsibilities`/`Source` subclass the shared bases and correctly match their expected headings without redeclaring `@alias`, confirmed by a unit test.
- [ ] ACC-007: Verifies REQ-008 -- `feat-133-tags-dec-rsk/README.md`'s Requirements/Acceptance Criteria/Task List no longer mention `dec`, and a comment referencing this feature is posted on GitHub issue #133.
- [ ] ACC-008: Verifies REQ-009 -- every phase's commit in this feature's history passes the full local pre-commit hook chain with no follow-up "fix docs/schema drift" commit needed afterward.

### Scope

#### Included

- `models/md/common_sections.py`: new shared base classes (`SourceBase`, `AccountableBase`, `ResponsibleBase`, `SupportBase`, `ConsultedBase`, `InformedBase`, `RolesAndResponsibilitiesBase`).
- `dec/models/v1/body.py`: new `RolesAndResponsibilities` (mandatory), `Tags` (optional), `Source` (mandatory) sections; DEC schema `version` bump.
- `req/models/v1/body.py` and `sop/models/v1/body.py`: refactor existing `Source`/RASCI classes to subclass the shared bases (behavior-preserving).
- DEC packaged template/example data and `dec_schema.json` (docs copy and packaged copy) updates.
- `dec/prompts/create_dec`/`update_dec` instruction updates.
- Unit tests for all of the above.
- Docs regeneration (`docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`, all 12 `docs/*_schema.json`).
- `AGENTS.md` update for the `dec/` bullet.
- `feat-7-various-improvements/README.md` Task 0.33 update (split out into this feature, mirroring Task 0.32's own precedent).
- `feat-133-tags-dec-rsk/README.md` rescoping to RSK-only.
- GitHub issue #29 and #133 comments.

#### Explicitly Out Of Scope

- RSK's own `## Tags` section -- stays with `feat-133-tags-dec-rsk`.
- Any change to `DecFrontmatter` itself.
- Any change to SOP's own optional-as-a-whole `## Roles and Responsibilities` cardinality -- SOP keeps its section optional; only its field/validator implementation is refactored to share code, not its cardinality.
- A dedicated ADR for the shared-base-class decision -- a feature-level Decisions Made entry is used instead, per explicit user decision.

### Dependencies

#### Depends On

- None.

#### Blocks

- None directly; `feat-133-tags-dec-rsk`'s remaining RSK-only scope is unaffected and does not block on this feature landing first, but its README is edited by this feature to drop the DEC half.

### Design Notes

RASCI shape decision: DEC intentionally diverges from SOP's own cardinality. SOP made the whole `## Roles and Responsibilities` section optional (a procedure might not need explicit roles), with `### Accountable`/`### Responsible` only forced once the section is present. DEC makes the whole section mandatory on every document, because a decision must always have a named accountable owner -- there is no such thing as a decision with nobody responsible for it. `### Support`/`### Consulted`/`### Informed` stay independently optional under DEC too, exactly like SOP.

Alias inheritance, verified empirically: `@alias(...)` sets `cls._alias_metadata` as a plain Python class attribute at decoration time, and `match_alias()` reads it via `getattr(cls, "_alias_metadata", None)`, which follows normal MRO-based attribute lookup. A live test during planning confirmed a subclass that never redeclares `_alias_metadata` correctly inherits it from its base class, and `match_alias` matches correctly against the inherited value. Consequence: `@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)` needs to be declared exactly once, on the shared `RolesAndResponsibilitiesBase` in `models/md/common_sections.py` -- `sop.RolesAndResponsibilities` and `dec.RolesAndResponsibilities` both inherit it automatically and do not need to redeclare `@alias` themselves. `Source`/`Accountable`/`Responsible`/`Support`/`Consulted`/`Informed` need no `@alias` at all, base or subclass, since their default `SPACE_SEPARATED`-derived heading text (computed from the actual runtime class's own `__name__` at match time, not at decoration time) already equals the desired heading text for those already-matching class names.

Section order: mirrors REQ's own precedent of `## Tags` immediately preceding `## Source` (REQ's field order is Priority, then Tags, then Source). DEC's new block sits right after `## Decision Outcome` (its `### Consequences`/`### Confirmation` sub-sections) and right before `## Related Artifacts`.

Tags absorption: `feat-133-tags-dec-rsk` (issue #133) already independently planned an identical `## Tags` shape for both `dec` and `rsk`. Since this feature touches `dec/models/v1/body.py` anyway, it absorbs the DEC half of that work in the same pass, leaving `feat-133-tags-dec-rsk` scoped to RSK only.

Pre-commit hook scope, verified by reading `.pre-commit-config.yaml`: the `specmgr-schema` hook (and its 12 per-domain `specmgr-schema-{type}-package` siblings) match any `.py` file under the `dec`/`feat`/`gol`/`prb`/`qa`/`req`/`rsk`/`sop`/`sysrs`/`tsk`/`uc`/`vcr` `models/v1`(or `v2`) packages, or `models/md`. Because `models/md` is one of the literal alternation branches, editing `models/md/common_sections.py` in Phase 1 alone -- before `dec` is even touched -- already forces regeneration of every registered domain's `docs/*_schema.json` and packaged copy, by design (a shared-model change can change any domain's generated tool parameter schema). Every phase from Phase 1 onward must therefore run the full regen/verify checklist in REQ-009, not just a final "docs" phase at the end.

### Related Decisions

- None yet -- see this feature's own "Decisions Made" log below for the shared-base-class rationale instead of a dedicated ADR.

### Task List

#### Phase 0: Feature Folder

- [x] Task 0.1: Create this feature folder (`feat-29-dec-source-roles`) via `create_feat`, capturing the full design discussed with the user.

#### Phase 1: Shared Base Classes

- [ ] Task 1.1: Add `models/md/common_sections.py` with `SourceBase`, `AccountableBase`, `ResponsibleBase`, `SupportBase`, `ConsultedBase`, `InformedBase`, `RolesAndResponsibilitiesBase` (the last decorated once with `@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)`).
- [ ] Task 1.2: Refactor `req/models/v1/body.py::Source` to subclass `SourceBase`; confirm REQ's existing test suite passes unchanged.
- [ ] Task 1.3: Refactor `sop/models/v1/body.py`'s six RASCI classes to subclass the new bases; confirm SOP's existing test suite passes unchanged.
- [ ] Task 1.4: Run this phase's full quality gate (REQ-009) and commit.

#### Phase 2: DEC Schema

- [ ] Task 2.1: Add mandatory `RolesAndResponsibilities` (subclassing the Phase 1 bases) to `dec/models/v1/body.py`.
- [ ] Task 2.2: Add optional `Tags` to `dec/models/v1/body.py`, absorbing the DEC half of `feat-133-tags-dec-rsk`.
- [ ] Task 2.3: Add mandatory `Source` (subclassing `SourceBase`) to `dec/models/v1/body.py`.
- [ ] Task 2.4: Wire the three new fields into `Decision`'s field declaration order per REQ-005 and bump DEC's schema `version`.
- [ ] Task 2.5: Add unit tests for DEC's three new sections (parser/body/summary), mirroring `tests/sop/models/v1/test_body.py` and `tests/req/models/v1/test_body.py`.
- [ ] Task 2.6: Run this phase's full quality gate (REQ-009) and commit.

#### Phase 3: Templates, Examples, Schema Resource

- [ ] Task 3.1: Update DEC's packaged template/example data files to include the three new sections with representative content.
- [ ] Task 3.2: Add/adjust a test asserting the packaged DEC template/example still parse successfully with the new mandatory sections present.
- [ ] Task 3.3: Run this phase's full quality gate (REQ-009) and commit.

#### Phase 4: Prompts

- [ ] Task 4.1: Update `dec/prompts/create_dec.py` instructions to mention the three new sections and reference `specmgr://rasci` for RASCI role definitions.
- [ ] Task 4.2: Update `dec/prompts/update_dec.py` instructions similarly.
- [ ] Task 4.3: Run this phase's full quality gate (REQ-009) and commit.

#### Phase 5: Docs and Housekeeping

- [ ] Task 5.1: Update `AGENTS.md`'s `dec/` bullet to mention the three new sections and the shared-base-class refactor.
- [ ] Task 5.2: Update `feat-7-various-improvements/README.md`'s Task 0.33 entry to "split out into `feat-29-dec-source-roles`".
- [ ] Task 5.3: Update `feat-133-tags-dec-rsk/README.md` to drop DEC from scope, pointing at this feature for the DEC half.
- [ ] Task 5.4: Post a comment on GitHub issue #29 summarizing the shipped design.
- [ ] Task 5.5: Post a comment on GitHub issue #133 noting DEC's Tags half was absorbed into issue #29.
- [ ] Task 5.6: Run this phase's full quality gate (REQ-009), commit, and mark this feature's status `done`.

## Progress

### Current Status

**As of 2026-09-17**: Planning complete; Phase 0 (this README) done. Phase 1 not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #29 ("Artifact type 'Decision' (DEC) need additional attributes from ADR frontmatter"), originally tracked as Task 0.33 in `feat-7-various-improvements`. Split into its own feature folder after design discussion concluded the scope required new DEC body sections (not frontmatter fields), a cross-domain shared-base-class refactor, and absorption of `feat-133-tags-dec-rsk`'s DEC half.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:03.000Z - Absorbed feat-133's DEC half

Decided to absorb the DEC half of `feat-133-tags-dec-rsk` (issue #133, `## Tags` section) into this feature rather than keep it as a separate dependency, since both touch `dec/models/v1/body.py` in the same pass. `feat-133-tags-dec-rsk` is rescoped to RSK-only as part of this feature's Phase 5, with a comment posted on issue #133 noting the absorption.

#### 2026-09-17 00:00:02.000Z - DEC's Roles and Responsibilities is mandatory, unlike SOP's

Decided DEC's `## Roles and Responsibilities` section is mandatory as a whole (SOP's own equivalent stays optional), because a decision must always have a named accountable owner -- this was the direct resolution of the original issue's "owner"/decision-maker concern.

#### 2026-09-17 00:00:01.000Z - Shared base classes instead of a dedicated ADR

Chose to implement `Source` and the RASCI classes as shared base classes in `models/md/common_sections.py`, with each domain (`req`/`sop`/`dec`) declaring its own thin concrete subclass, rather than writing a dedicated ADR for the decision. This is treated as a lower-risk extension of `models/md`'s existing generic-base-class pattern (every domain already inherits `MarkdownSection1`/`MarkdownSection2`/`MarkdownSection3` etc. from there) rather than a novel precedent of sharing whole concrete domain classes across packages, so a feature-level log entry here is proportionate instead of a full ADR.

### Related PRs / Commits

- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29): tracking issue for this feature.
- [Issue #133](https://github.com/dfch/biz.dfch.SpecMgr/issues/133): DEC's `## Tags` half absorbed from this issue; `feat-133-tags-dec-rsk` retains the RSK half.

### More Information

None.
