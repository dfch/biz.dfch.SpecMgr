---
classification: null
created: '2026-09-17 12:26:44.432+02:00'
id: feat-135-related-artifacts-risks
status: planning
type: feat
updated: '2026-09-17 12:26:44.432+02:00'
version: 1.0.0
---

# Feature: Replace Acceptance Criteria with Risks in Related Artifacts; Validate Cross-Reference Format

## Plan

### Overview

`req`, `gol`, `dec`, and `sop` all share an identical `## Related Artifacts` shape with four (five for `sop`) `### ` cross-reference sub-lists. One of them, `### Acceptance Criteria`, references an artifact type that was never implemented as a standalone domain -- acceptance criteria only exist as `AC-NNN` entries inside a `vcr` (Verification Case Record) document, and VCR already owns the correct, backward-only link (`## Verifies` -> `REQ`/`UC`). This feature removes that dead sub-list from all four domains, replaces it with a new `### Risks` cross-reference to `rsk`, and -- since none of these sub-lists have ever had any format validation -- adds a shared, enforced `"<TYPE> <uuid>: <title>"` format to every sub-list in all four domains, reusing the pattern already proven by `vcr`'s `## Verifies` and `sysrs`'s per-section cross-reference lists (extracted into a new shared `models/md` helper rather than duplicated a third/fourth time).

### Requirements

- REQ-001: `AcceptanceCriteria`/`acceptance_criteria` MUST be removed entirely from `RelatedArtifacts` in `req`, `gol`, `dec`, and `sop`.
- REQ-002: A new `Risks`/`risks` cross-reference sub-list (to `rsk`) MUST be added to `RelatedArtifacts` in `req`, `gol`, `dec`, and `sop`, in the slot `AcceptanceCriteria` occupied.
- REQ-003: `Goals`/`goals` MUST remain unchanged (present, in scope) in all four domains -- it is not added to `vcr`, and `rsk` getting its own `Related Artifacts` section is explicitly out of scope here.
- REQ-004: Every cross-reference sub-list item (`Requirements`, `Decisions`, `Goals`, `Risks`, and `sop`'s `Sops` self-reference) MUST be validated against a common format: `"<TYPE> <uuid>: <title>"` (space-separated, lowercase 8-4-4-4-12 hex UUID, full-line match), reusing a single shared validator rather than a fourth independent reimplementation.
- REQ-005: `Decisions` MUST accept only the `DEC` type tag (not `DEC|ADR`), since `adr` is slated for removal as an artifact type (issue #46).
- REQ-006: Every affected sub-list's items MUST support an optional trailing notes paragraph (`MarkdownListItemWithNotes`), mirroring `sysrs`'s existing shape.
- REQ-007: The shared validator/pattern logic MUST live in `models/md`, and `sysrs`/`vcr` MUST be refactored to reuse it instead of keeping their own independent, duplicated implementations.
- REQ-008: Packaged examples, templates, and create/update instructions for `req`/`gol`/`dec`/`sop` MUST be updated so none of them drift from the new schema (no stale Acceptance Criteria mentions, no unvalidated example bullets).
- REQ-009: The 14 real, on-disk REQ documents (`docs/req/*.md`) whose `### Goals` bullet currently uses the unvalidated `GOL-<uuid>` (dash) form MUST be migrated to the enforced `GOL <uuid>` (space) form via the proper `update` tool.

### Acceptance Criteria

- [ ] ACC-001: `req`/`gol`/`dec`/`sop`'s `RelatedArtifacts` model no longer has an `acceptance_criteria` field, and `AcceptanceCriteria` is not exported from any of their `models/v1/__init__.py`.
- [ ] ACC-002: `req`/`gol`/`dec`/`sop`'s `RelatedArtifacts` model has a `risks` field backed by a `Risks` class that accepts a well-formed `RSK <uuid>: <title>` bullet and rejects a malformed one (wrong tag, bad uuid, missing title).
- [ ] ACC-003: `Requirements`/`Decisions`/`Goals` (and `sop`'s `Sops`) each reject a bullet using the wrong type tag, an uppercase or malformed UUID, a dash instead of a space, or a missing title -- and accept the well-formed form.
- [ ] ACC-004: `Decisions` rejects an `ADR <uuid>: <title>` bullet (DEC-only, no dual-tag acceptance).
- [ ] ACC-005: A bullet with a trailing indented notes paragraph parses into `.notes`, and a bare bullet leaves `.notes` as `None`, for every affected sub-list.
- [ ] ACC-006: `models/md` exposes a single shared cross-reference validator/pattern helper, and `sysrs`/`vcr` are refactored to call it (their own existing tests still pass unmodified in behavior).
- [ ] ACC-007: Every packaged `req`/`gol`/`dec`/`sop` example and template parses via its own `parse_<domain>` and contains no `Acceptance Criteria` mentions; create/update instructions document the enforced format explicitly.
- [ ] ACC-008: All 14 real `docs/req/*.md` documents' `### Goals` bullets use the `GOL <uuid>: <title>` (space) form and still parse via `parse_req`.
- [ ] ACC-009: `uv run --frozen specmgr schema` and `uv run --frozen specmgr docs` produce no further drift after implementation (clean `git status` on `docs/`).

### Scope

#### Included

- Model changes (`body.py` + `models/v1/__init__.py`) for `req`, `gol`, `dec`, `sop`.
- New shared cross-reference validator module in `models/md`, plus a refactor of `sysrs`/`vcr` to reuse it.
- Packaged data updates (`*_example.md`, `*_template.md`, `*_create_instructions.md`, `*_update_instructions.md`) for the four domains.
- Migration of the 14 live `docs/req/*.md` documents' `### Goals` bullets to the new format.
- Full test coverage: shared-validator unit tests, per-domain format matrix tests, notes-capture tests, updated example/template resource tests.
- Schema/docs regeneration (`specmgr schema`, `specmgr docs`).

#### Explicitly Out Of Scope

- Any change to `vcr`, `feat`, `uc`, `tsk`, `qa`, `prb`, `sysrs`, or `adr`'s own schemas beyond the internal, behavior-preserving refactor of `sysrs`/`vcr`'s validator implementation.
- Adding a `## Related Artifacts` section (or a `Goals` reference) to `vcr` -- its `## Verifies` link already covers this transitively via `REQ`/`UC`.
- Giving `rsk` its own `## Related Artifacts` section -- a separate, future decision.
- Any existence-check against the referenced id (still purely a format check, not a "does this id actually exist" check) -- deferred to a future cross-reference-validation feature, consistent with `feat-134-related-artifact-similarity`'s own explicit exclusion of this.
- Exposing the format constraint in the generated JSON Schema -- a pre-existing limitation shared with `vcr`/`sysrs`, not fixed here; the create/update instructions text is the only documentation surface for it.

### Dependencies

#### Depends On

- None.

#### Blocks

- None.

### Design Notes

**Shared validator (`models/md`)**: new module (e.g. `models/md/_cross_reference.py`) exporting `UUID_PATTERN` (the shared lowercase 8-4-4-4-12 hex fragment, generalized from `sysrs`'s local `_UUID_PATTERN`), a pattern-builder for one or more type tags, and `validate_cross_reference_items(items, pattern)` (generalized from `sysrs`'s local `_validate_cross_reference_items`: `re.fullmatch` + `re.DOTALL`, actionable `ValueError`). `sysrs` and `vcr` are refactored to import from here instead of keeping independent copies.

**Per-domain model changes** (`req`, `gol`, `dec`, `sop`): remove `AcceptanceCriteria`/`acceptance_criteria`; add `Risks` (`MarkdownSection3`, `items: list[MarkdownListItemWithNotes]`, validated against `^RSK {uuid}: .+$`) + `risks` field; add `field_validator`s to the existing `Requirements` (`^REQ {uuid}: .+$`), `Decisions` (`^DEC {uuid}: .+$`, DEC-only), `Goals` (`^GOL {uuid}: .+$`); `sop`'s `Sops` self-ref gets `^SOP {uuid}: .+$`. All these sub-lists' `items` type changes from `MarkdownListItem` to `MarkdownListItemWithNotes` (already imported in each of these files for `## Tags`).

**Known, accepted limitation**: the new format constraint is invisible in the generated JSON Schema, since it's enforced via a Pydantic `field_validator` on a `@computed_field` (`MarkdownListItem.text`), not a schema-declared `Field(pattern=...)` string. This mirrors `vcr`/`sysrs`'s existing behavior and is not something this feature fixes.

**Migration**: the 14 real `docs/req/*.md` documents (created for `feat-84-specmgr-sysrs`) currently populate `### Goals` with the unvalidated `GOL-<uuid>: <title>` (dash) form. These are rewritten to `GOL <uuid>: <title>` (space) via the `update`/`update_section` MCP tool, not a manual file edit, to keep the documents' round-trip integrity intact. No other real `req`/`gol`/`dec`/`sop` document on disk has populated `Related Artifacts` content (confirmed: no `docs/dec/` directory exists yet; `docs/gol/`, `docs/sop/` have none populated).

### Related Decisions

- None yet. This is an implementation-level schema change scoped to `req`/`gol`/`dec`/`sop` plus an internal `models/md`/`sysrs`/`vcr` refactor; it does not by itself warrant a new ADR/DEC per this repo's own ADR-vs-feature-log guidance (`AGENTS.md`).

### Task List

#### Phase 1: Shared Cross-Reference Validator (`models/md`)

- [ ] Task 1.1: Implement `models/md/_cross_reference.py` (`UUID_PATTERN`, pattern-builder, `validate_cross_reference_items`), export from `models/md/__init__.py`.
- [ ] Task 1.2: Refactor `sysrs/models/v1/body.py` to use the shared helper instead of its local `_UUID_PATTERN`/`_validate_cross_reference_items`; confirm existing `tests/sysrs/` suite stays green unmodified.
- [ ] Task 1.3: Refactor `vcr/models/v1/body.py`'s `_VERIFIES_PATTERN`/validator to reuse the shared `UUID_PATTERN`; confirm existing `tests/vcr/` suite stays green unmodified.
- [ ] Task 1.4: New `tests/models/md/test_cross_reference.py` (valid match, wrong tag, malformed uuid, missing title, multi-tag pattern, DOTALL soft-wrap case).

#### Phase 2: Model Changes (req, gol, dec, sop)

- [ ] Task 2.1: `req/models/v1/body.py` + `__init__.py` -- remove `AcceptanceCriteria`, add `Risks`, add format validators to `Requirements`/`Decisions`/`Goals`, upgrade items to `MarkdownListItemWithNotes`.
- [ ] Task 2.2: Same for `gol/models/v1/body.py` + `__init__.py`.
- [ ] Task 2.3: Same for `dec/models/v1/body.py` + `__init__.py`.
- [ ] Task 2.4: Same for `sop/models/v1/body.py` + `__init__.py`, plus `Sops` self-ref format validator.

#### Phase 3: Packaged Data (req, gol, dec, sop)

- [ ] Task 3.1: Update `req/data/{req_example.md,req_template.md,req_create_instructions.md}` (no `req_update_instructions.md` mention was found).
- [ ] Task 3.2: Update `gol/data/{gol_example.md,gol_template.md,gol_create_instructions.md}`.
- [ ] Task 3.3: Update `dec/data/{dec_example.md,dec_template.md,dec_create_instructions.md}`.
- [ ] Task 3.4: Update `sop/data/{sop_example.md,sop_template.md,sop_create_instructions.md}` (check for an update-instructions file too).

#### Phase 4: Live Data Migration

- [ ] Task 4.1: Migrate all 14 `docs/req/*.md` documents' `### Goals` bullet from `GOL-<uuid>` to `GOL <uuid>` via the `update` tool.

#### Phase 5: Tests (req, gol, dec, sop)

- [ ] Task 5.1: `req` -- retarget ACC tests to Risks; add format-validation matrix for Requirements/Decisions/Goals/Risks; add notes-capture tests; update `test_parser.py`.
- [ ] Task 5.2: `gol` -- same, plus `tests/gol/resources/` if it asserts on Related Artifacts content.
- [ ] Task 5.3: `dec` -- same, plus update `tests/dec/resources/test_dec_example.py`.
- [ ] Task 5.4: `sop` -- same, including `Sops` self-ref matrix, plus update `tests/sop/resources/test_sop_example.py`.

#### Phase 6: Regeneration

- [ ] Task 6.1: `uv run --frozen specmgr schema` (+ the four per-domain `--output-dir` package copies).
- [ ] Task 6.2: `uv run --frozen specmgr docs`.
- [ ] Task 6.3: Full test suite + lint gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`).

## Progress

### Current Status

**As of 2026-09-17**: Planning stage; not started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #135 to remove the never-implemented Acceptance Criteria cross-reference from REQ/GOL/DEC/SOP's Related Artifacts, replace it with a validated Risks reference, and enforce a common cross-reference format, following a design discussion covering scope (all four domains, not just REQ), the GOL-reference question (kept, not extended to VCR/RSK), and the validation-format question (none exists today; a shared validator will be extracted into `models/md`).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-17 00:00:00.000Z - Scope is all four domains, not REQ-only

`req`, `gol`, `dec`, and `sop` all share the exact same `RelatedArtifacts` shape (copy-pasted), so the Acceptance-Criteria-removal/Risks-addition/format-validation change applies uniformly to all four, keeping them consistent rather than introducing drift.

#### 2026-09-17 00:00:00.000Z - Goals reference kept, not extended

`### Goals` stays as-is in `req`/`gol`/`dec`/`sop` (upward "why does this exist" traceability, already in live use by the `feat-84-specmgr-sysrs` REQ documents). It is deliberately not added to `vcr` (already reachable transitively via `REQ`/`UC`, avoiding a duplicated/drift-prone skip-level link). `rsk` gaining its own `Related Artifacts` section is deferred as a separate decision.

#### 2026-09-17 00:00:00.000Z - Shared validator extracted rather than duplicated again

The `"<TYPE> <uuid>: <title>"` format-validation pattern already exists independently in both `vcr` (`## Verifies`) and `sysrs` (per-section cross-reference lists). Rather than reimplementing it a third and fourth time in `req`/`gol`/`dec`/`sop`, a shared helper is extracted into `models/md` and `sysrs`/`vcr` are refactored to use it too.

### Related PRs / Commits

- [Issue #135](https://github.com/dfch/biz.dfch.SpecMgr/issues/135): tracking issue for this feature.

### More Information

None.
