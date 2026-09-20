---
classification: null
created: '2026-09-17 07:38:35.189+02:00'
id: feat-102-133-rsk-tags-source
status: planning
type: feat
updated: '2026-09-21 00:06:15.836+02:00'
version: 1.0.0
---

# Feature: rsk `## Source` (mandatory) + `## Tags` item-type alignment (issues #102 + #133)

## Plan

### Overview

This feature closes two GitHub issues whose remaining scope both lands on the `rsk` domain: **#133** ("Add optional `## Tags` sections to the `dec` and `rsk` artifact types") and **#102** ("Add optional 'Source' field to DEC and RSK (like REQ already has)").

**Audit (2026-09-20): both issues are already ~75% shipped on `dev` (v0.29.0).**

- The DEC halves of *both* issues shipped via `feat-29-dec-source-roles` (issue #29, merged as `248568c`): `dec` gained a mandatory `## Roles and Responsibilities`, an optional `## Tags` (absorbing the DEC half of #133), and a mandatory `## Source` (the DEC half of #102).
- The RSK half of #133 **already exists**: `Risk` has carried `tags: Tags | None` since the rsk domain was created (feat-15 -- the only commit in `rsk/models/v1/body.py`'s history) -- schema, template, example, prompt, and tests all in place. This file's original #133-only plan (2026-09-17) was written without knowing that.
- The RSK half of #102 is the **only genuinely missing piece**: `Risk` has no `## Source` section.

The remaining scope is therefore:

1. (#133) Align rsk's `## Tags` item type from plain `MarkdownListItem` to `MarkdownListItemWithNotes`, matching `req`/`dec`/`gol` (rsk is the one outlier of the four; the issue's own wording -- "mirroring the existing `req` Tags convention" -- asks for exactly this).
2. (#102) Add `## Source` to rsk as a **mandatory** section (a user decision recorded in Decisions Made -- it deliberately diverges from the issue's "optional" wording, for consistency with the shipped REQ/DEC design): a thin `SourceBase` subclass in `rsk/models/v1/body.py`, declared between `## Tags` and `## More Information`.
3. Close both issues, fix `AGENTS.md`'s `rsk` bullet (which documents none of `## Owner`/`## Tags`/`## More Information` at all), and consolidate this stale #133-only plan folder (renamed to `feat-102-133-rsk-tags-source` in Phase 0, multi-issue naming per the `feat-81-83-validation` / `feat-104-109-...` precedent).

**This feature is BREAKING** -- via the mandatory `## Source` only: any existing `rsk` document lacking `## Source` fails to parse via `get_rsk`/`parse_rsk`/`update`/`create_rsk` round-trips until the section is added; `list_rsk` degrades gracefully (inline failed-entry row, per feat-81-83-validation). The Tags alignment is a strict parsing superset and breaks no existing document. Precedent for the breaking treatment: `feat-29-dec-source-roles`.

**Orchestration note**: this plan was written at planning time (2026-09-20) and is **not yet implemented**. It is intended to be executed by an Orchestrator agent in a later session: one `phase-implementer` dispatch per phase (REQ-015), one commit per phase (REQ-016), and the full local quality gate after every phase (REQ-014) -- this README is the single source of truth for what is/isn't done.

### Requirements

- REQ-001: rsk's `Tags.items` becomes `list[MarkdownListItemWithNotes]` (structurally identical to `req`/`dec`/`gol`'s `Tags`); plain single-line tags still parse unchanged; loose-list continuation paragraphs under a tag are captured in `item.notes` instead of being silently dropped.
- REQ-002: `Risk` gains a **mandatory** `## Source` section: a thin `class Source(SourceBase)` (domain-first convention, mirroring `req.Source`/`dec.Source` including the domain-neutral field-description wording note from feat-29 REQ-016), with a required `source` field of that type declared between `tags` and `more_information` (REQ's own tag->source adjacency; `more_information` stays last, as in every other domain); `body.py`'s module docstring layout diagram and field-order sentence are updated in the same change.
- REQ-003: `_SENTINEL_RSK_TEXT` in `src/biz/dfch/specmgr/rsk/tools/_sentinel.py` gains a `## Source` section in the **same phase** as the REQ-002 schema change -- the sentinel is a full, valid RSK document parsed at import time via the real `parse_rsk` pipeline (no bypass), so without it a new mandatory section breaks the `rsk.tools._sentinel` import -- and with it `list_rsk` -- at module load; its dedicated test class (`tests/rsk/tools/test__sentinel.py`) is purpose-built to surface exactly this.
- REQ-004: No other domain's schema is touched, and the shared `SourceBase` in `models/md/common_sections.py` is not modified (rsk declares and owns its own concrete `Source` subclass, per the domain-first convention).
- REQ-005: No schema `version` bump: this is an in-place, **breaking** `rsk/models/v1` evolution (precedents: feat-29's no-bump finding -- `SCHEMA_COMMENT_VERSION` only bumps for a breaking generated-schema change requiring a new `vN` sibling package -- and feat-132's explicit in-place breaking v1 evolution, not a new v2).
- REQ-006: `rsk/data/rsk_template.md` and `rsk/data/rsk_example.md` gain `## Source` between `## Tags` and `## More Information` (template: placeholder line in template style; example: representative provenance content); `rsk_schema.json` is regenerated in both copies (docs and packaged) and marks `source` as required.
- REQ-007: Prompt instruction data updated: `rsk/data/rsk_create_instructions.md` lists `## Source` as mandatory in its structure recap and adds it to the mandatory gather step; `rsk/data/rsk_update_instructions.md`'s step 3 body-change field list names `source` as mandatory (not among the optionals); `tests/rsk/prompts/test_create_risk.py` and `test_update_risk.py` text assertions updated to match; the rsk prompt *module* docstrings do not enumerate body sections (unlike the dec precedent), so no `.py` change is needed in `rsk/prompts/`.
- REQ-008: Every test fixture containing a full RSK document is updated to include `## Source` -- verified by `grep -rl "## Cause" tests/` to be exactly these 15 files: `tests/rsk/models/v1/{test_body,test_parser,test_summary}.py`, `tests/rsk/tools/{test_create_rsk,test_get_rsk,test__io,test_list_rsk,test_parse_rsk,test__paths,test__write}.py`, and `tests/general/tools/{test_update,test_delete,test_set_status,test_set_classification,test_validate}.py` (the generic cross-domain suites each carry their own local minimal rsk body by design -- intentional duplication, updated in place, not re-pointed); a new shared fixture helper `tests/rsk/tools/_helpers.py` carrying a `MANDATORY_SOURCE` snippet mirrors `tests/dec/tools/_helpers.py` (including its documented leading-`\n` call-site convention and mdformat-normalization subtlety from feat-29 Task 7.3), and the per-tool rsk test files import from it rather than duplicating the literal.
- REQ-009: New unit tests: a rsk document with `## Source` parses; a rsk document missing `## Source` fails validation with the raised `AssertionError`/`ValidationError` **message content asserted** (field path + 1-based line, not just the exception type); a misordering regression test places `## Source` out of position (before `## Tags`, or after `## More Information`) and asserts the raised `AssertionError` (feat-29 REQ-015/ACC-014 precedent -- spot-check by temporarily reordering `Risk`'s field declarations that the test fails without the guard, then restore immediately, leaving no reverted state in the diff); Tags-alignment tests (plain tags parse unchanged; a loose-list continuation under a tag is captured in `item.notes` and round-trips).
- REQ-010: `AGENTS.md`'s `rsk` bullet documents the mandatory `## Source`, the `## Tags` alignment to `MarkdownListItemWithNotes`, and the previously-undocumented optional `## Owner`/`## Tags`/`## More Information` sections, with a reference to this feature.
- REQ-011: `CHANGELOG.md` gains an `[Unreleased]` entry: `### Added` -- rsk `## Source` (mandatory), explicitly marked `**BREAKING**` with a short before/after markdown migration snippet (feat-29 REQ-011 precedent); `### Changed` -- rsk `## Tags` item type aligned to `MarkdownListItemWithNotes` (non-breaking: notes captured instead of dropped).
- REQ-012: This README's Decisions Made log and the known-limitations note in Design Notes record the planning-time decisions (mandatory cardinality against the issue's own "optional" wording; Tags alignment; folder consolidation) and the backward incompatibility -- the Decisions Made entries and the known-limitations note exist as of the 2026-09-20 rewrite (below), and their final verification is Task 5.3.
- REQ-013: GitHub issue close-out: #133 receives a comment (rsk `## Tags` has existed since feat-15; the DEC half shipped in feat-29; the remaining deliverable -- the WithNotes alignment -- ships in Phase 1) and is closed at the end of Phase 1; #102 receives a comment (the DEC half shipped in feat-29; the RSK half ships in this feature as **mandatory**, with a breaking note and a pointer to the CHANGELOG migration snippet) and is closed at the end of Phase 5.
- REQ-014: Every phase ends with the full local quality gate run and passing **before that phase's own commit**: `ruff format --check`, `ruff check`, `vulture`, `specmgr docs`, `specmgr mcp-docs`, `specmgr schema` for all 12 registered types plus their packaged per-domain copies, `pytest -n auto --cov=src --cov-report=`, `specmgr coverage-badge` (feat-29 REQ-009 precedent -- touching `rsk/models/v1` or `models/md` forces full-repo schema regeneration via the `specmgr-schema*` pre-commit hooks' file-scope regex, so the gate is full-scope from Phase 1 onward, not just a final "docs" phase).
- REQ-015: Each of Phases 1-5 is implemented by exactly one dedicated `phase-implementer` subagent dispatch off this README (one phase per dispatch; the orchestrating main session reads this file and reports back between dispatches, never implementing a phase inline) -- the feat-29 REQ-010 precedent; Phase 0 is pure setup (branch/commit/rename) and may be done by the orchestrator directly.
- REQ-016: **Every commit made for this feature (Phase 0 through Phase 5, including Phase 0's own setup commits) mentions both tracking issues in the commit message using GitHub's `#` syntax -- `#102` and `#133` --** so the eventual PR merge links and closes both issues; follow the repo's observed `type(scope): subject (#issue) (#PR)` squash-merge style with both issue references present, e.g. `feat(rsk): add mandatory ## Source section and align ## Tags item type (#102) (#133)` -- the phase number may appear in the subject or body, but the two `#`-issue references are mandatory in every commit message.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 -- a rsk document with plain `## Tags` items parses unchanged, and a tag carrying a loose-list continuation paragraph has it captured in `item.notes` and round-trips through `create_rsk`/`parse_rsk`.
- [ ] ACC-002: Verifies REQ-002 -- a rsk document with `## Source` parses via `parse_rsk`/`get_rsk`, and a rsk document missing `## Source` fails validation with the raised message content asserted (not just the exception type).
- [ ] ACC-003: Verifies REQ-002 -- a rsk document with `## Source` out of its required position (before `## Tags`, or after `## More Information`) fails validation, with the `AssertionError` asserted.
- [ ] ACC-004: Verifies REQ-003 -- `rsk.tools._sentinel` imports cleanly and `tests/rsk/tools/test__sentinel.py` is green after the schema change (the sentinel document carries `## Source`).
- [ ] ACC-005: Verifies REQ-006 -- `get_rsk_template`/`get_rsk_example` return documents with `## Source` positioned between `## Tags` and `## More Information` (both parsing successfully), and the regenerated `docs/rsk_schema.json` and packaged `rsk/data/rsk_schema.json` mark `source` as required.
- [ ] ACC-006: Verifies REQ-007 -- the create instructions list `## Source` as mandatory (never-skippable create-flow wording per the feat-29 dec precedent), the update instructions' step 3 names it, and both prompt test files pass on the updated text.
- [ ] ACC-007: Verifies REQ-008/REQ-009 -- the full `pytest` suite is green with every full-RSK-document fixture updated, and no test passes "for the wrong reason" (message content asserted where required).
- [ ] ACC-008: Verifies REQ-010 -- `AGENTS.md`'s rsk bullet lists the mandatory `## Source` and the optional `## Owner`/`## Tags`/`## More Information` sections with their cardinalities and the WithNotes note.
- [ ] ACC-009: Verifies REQ-011 -- `CHANGELOG.md`'s `[Unreleased]` carries the BREAKING-marked rsk `## Source` entry with a before/after migration snippet, plus the Tags-alignment `Changed` entry.
- [ ] ACC-010: Verifies REQ-012 -- this README's Decisions Made log and the known-limitations note in Design Notes are complete and current.
- [ ] ACC-011: Verifies REQ-013 -- GitHub issues #133 and #102 are closed, each with its described comment.
- [ ] ACC-012: Verifies REQ-014/REQ-015/REQ-016 -- every phase's commit passes the full quality gate with no follow-up drift-fix commit needed, Phases 1-5 each consist of exactly one `phase-implementer` dispatch, and **every commit message on the feature branch contains both `#102` and `#133`**.

### Scope

#### Included

- `rsk/models/v1/body.py`: the `Tags.items` type change; the new `Source` class + mandatory field; the module docstring layout/order updates.
- `rsk/tools/_sentinel.py`: `## Source` added to `_SENTINEL_RSK_TEXT`.
- Packaged data: `rsk/data/rsk_template.md`, `rsk/data/rsk_example.md`, `rsk/data/rsk_create_instructions.md`, `rsk/data/rsk_update_instructions.md`; regenerated `rsk_schema.json` (docs + packaged copies).
- New `tests/rsk/tools/_helpers.py`; updates to the 15 full-RSK-document test fixtures (REQ-008 list); the new unit tests (REQ-009); the updated prompt tests.
- `AGENTS.md` (rsk bullet), `CHANGELOG.md` (`[Unreleased]`), this README (final Progress close-out in Phase 5), GitHub issue comments + closes for #102 and #133.

#### Explicitly Out Of Scope

- Any change to `req`/`dec`/`gol`/`sop` schemas, templates, prompts, or tests (all four already carry their respective sections).
- The pre-existing, unrelated drift that `gol.Source` subclasses `MarkdownSection2` rather than the shared `SourceBase` -- noted here for awareness only, not fixed by this feature.
- RASCI/`Roles and Responsibilities` on rsk -- issue #102's original "owner" concern is already satisfied by rsk's existing optional `## Owner` section.
- Any closed vocabulary or value validation for tags (free-form, exactly like `req`'s).
- Any similarity/search/discovery mechanism consuming Tags or Source -- tracked separately in feat-134-related-artifact-similarity (issue #134), which embeds raw body text and has no dependency on this feature.
- `RskSummary`/`list_rsk` row shape (Source/Tags are not carried on summary rows; the sentinel's derived worst-case fields are unaffected).

### Dependencies

#### Depends On

- None -- `feat-29-dec-source-roles` (issue #29) is already merged on `dev` (`248568c`); nothing else blocks this feature.

#### Blocks

- None directly.

### Design Notes

- **Field order**: `... residual_assessment -> owner -> tags -> source -> more_information`. REQ's own precedent is `## Tags` immediately preceding `## Source`; `## More Information` stays last, as in every other domain. `Risk`'s field declaration order enforces the markdown order (the `models.md` engine distributes text among declared fields in that order).
- **`Source` class shape**: a thin `class Source(SourceBase)` subclass with a domain-specific docstring mirroring `req.Source`/`dec.Source`, including the note that the generated JSON Schema's `value` field description comes from `SourceBase` and is intentionally domain-neutral ("this document") -- the feat-29 REQ-016 wording-drift precedent. No `@alias` needed: the default `SPACE_SEPARATED` heading derived from the runtime class name yields `## Source` exactly (verified twice in feat-29 for `req`/`dec`). The `*Base` classes themselves are not parseable directly (their suffixed names derive the wrong heading) -- only the correctly-named concrete subclass is ever used as a field type.
- **Cardinality is mandatory (user decision)**: the issue's own wording suggested "optional", but the user explicitly chose mandatory for consistency with the shipped REQ/DEC design, after the feat-29 breaking implications were laid out. Consequences handled exactly per the feat-29 precedent: import-time sentinel update (REQ-003), ~15 test-fixture files (REQ-008), a `CHANGELOG.md` BREAKING entry + migration snippet (REQ-011), the known-limitations note below, and `list_rsk` graceful degradation (already in place from feat-81-83-validation).
- **No version bump** (REQ-005): field additions to an existing `models/v1` package -- even mandatory, breaking ones -- do not bump `SCHEMA_COMMENT_VERSION` (which only tracks breaking generated-schema-structure changes requiring a new `vN` package); the prb feat-132 precedent did exactly this in-place breaking evolution.
- **Tags alignment is a strict parsing superset**: `MarkdownListItemWithNotes` subclasses `MarkdownListItem` and only adds `notes: list[MarkdownParagraph] | None = None`. Plain single-line tags parse identically; the only observable change is that loose-list continuation paragraphs under a tag are captured (in `notes`) instead of being dropped from the model. The feature's breaking impact therefore comes solely from the mandatory `## Source`.
- **Fixture helper convention**: `tests/rsk/tools/_helpers.py` mirrors `tests/dec/tools/_helpers.py` -- a single `MANDATORY_SOURCE` dedented snippet (leading `\n`, so per-tool call sites that already end their preceding fixture text with a blank line don't double up; mdformat normalization absorbs the difference before `parse_rsk` ever sees it -- the exact subtlety documented in feat-29 Task 7.3). `tests/general/tools/` files keep their own local minimal bodies (intentional duplication) and are updated in place, not re-pointed at the helper.
- **Pre-commit hook scope**: the `specmgr-schema` hook and its 12 per-domain siblings match any `.py` under `rsk/models/v1` (and `models/md`), so every code phase forces full-repo schema regeneration -- which is why REQ-014's gate is full-scope per phase, and why only the touched domain's generated content should change (`rsk_schema.json` + the touched modules' `docs/api/` pages); any wider drift is a defect to investigate, not to absorb.
- **Commit message convention (REQ-016)**: every commit references both `#102` and `#133` so the PR merge links/closes both issues. Observed repo style is `type(scope): subject (#issue) (#PR)` (e.g. `248568c` = `feat: add ... (#29) (#136)`, `27dcd4e` = `docs(132): feat-132-prb-update (#138)`); the two issue references both appear, e.g. `docs(rsk): plan feat-102-133 combined feature (#102) (#133)`.
- **Known limitations (accepted)**:
  - **Backward compatibility (BREAKING)**: `## Source` is mandatory on every rsk document. Any `rsk` document created before this feature ships and lacking that section will fail to parse via `get_rsk`/`parse_rsk`/`update`/`create_rsk` (though `list_rsk` degrades gracefully, reporting it as a failed entry inline rather than raising). This is an accepted, documented breaking change on this pre-1.0 project -- the same treatment feat-29 chose for DEC; the migration snippet lives in `CHANGELOG.md` (REQ-011).
  - The Phase 0 `set_feat_id` rename makes the historical folder-name reference in `feat-29-dec-source-roles/README.md` ("see `feat-133-tags-dec-rsk`") stale -- accepted; that reference is historical prose, not a live link, and feat-29's README is a `done` feature not to be reopened.
  - `gol.Source`'s pre-existing derivation from `MarkdownSection2` (not the shared `SourceBase`) is noted but left untouched (out of scope).
  - **feat-schema note for the implementer**: `feat-29-dec-source-roles/README.md` itself uses a standalone `### Known Limitations` H3 that the current feat schema does *not* declare -- its README currently fails `parse_feat` for exactly that reason. This feature therefore carries its known limitations as bolded content under this `Design Notes` section, not as a heading of its own; do not reintroduce a `### Known Limitations` heading.

### Related Decisions

- None yet -- see this feature's own Decisions Made log below (the planning-time decisions are already recorded there); no dedicated ADR is written for the in-place breaking v1 evolution (the feat-132/feat-29 precedent of feature-level logging is followed).

### Task List

#### Phase 0: Branch + folder consolidation (setup; orchestrator-direct)

- [ ] Task 0.1: Create branch `feat-102-133-rsk-tags-source` from `dev` (the working tree carries the planning-time README rewrite).
- [ ] Task 0.2: Commit the README rewrite (this combined plan) -- commit message per REQ-016, e.g. `docs(rsk): plan feat-102-133 combined feature (rsk mandatory Source + Tags alignment) (#102) (#133)`.
- [ ] Task 0.3: Run `set_feat_id(feat-133-tags-dec-rsk -> feat-102-133-rsk-tags-source)` (rewrites the frontmatter `id`, bumps `updated`, leaves the body byte-identical) -- commit per REQ-016, e.g. `docs(feat): rename feat-133-tags-dec-rsk to feat-102-133-rsk-tags-source (#102) (#133)`.
- [ ] Task 0.4: Run the quality gate (REQ-014) -- docs-only, expected no-op; verify no drift before proceeding to Phase 1.

#### Phase 1: #133 -- Tags item-type alignment (closes #133)

- [ ] Task 1.1: In `rsk/models/v1/body.py`, change `Tags.items` from `list[MarkdownListItem]` to `list[MarkdownListItemWithNotes]` (update the import from `...models.md`; add a docstring note that rsk mirrors `req`/`dec`/`gol`'s `Tags` shape, per issue #133).
- [ ] Task 1.2: In `tests/rsk/models/v1/test_body.py`, confirm plain tags parse unchanged (existing assertions still hold) and add a test: a tag with a loose-list continuation paragraph has it captured in `item.notes` and round-trips.
- [ ] Task 1.3: Quality gate (REQ-014) -- expect changes in `rsk_schema.json` (both copies; the Tags items schema gains the `notes` property) and in the touched module's `docs/api/` page from the docstring note; commit per REQ-016, e.g. `feat(rsk): align ## Tags item type to MarkdownListItemWithNotes (req/dec/gol parity) (#102) (#133)`.
- [ ] Task 1.4: Post the GitHub comment on issue #133 per REQ-013 and close the issue.

#### Phase 2: #102 -- mandatory `## Source` schema (BREAKING)

- [ ] Task 2.1: In `rsk/models/v1/body.py`, add `class Source(SourceBase)` (thin subclass; domain docstring + the domain-neutral field-description wording note mirroring `req.Source`/`dec.Source`), add the required `source` field between `tags` and `more_information`, and update the module docstring's layout diagram (add the `## Source` line) and its field-order sentence.
- [ ] Task 2.2: In `rsk/tools/_sentinel.py`, add a `## Source` section to `_SENTINEL_RSK_TEXT` positioned before its `## More Information` (the sentinel has no `## Owner`/`## Tags`, so it goes directly ahead of `## More Information`).
- [ ] Task 2.3: Create `tests/rsk/tools/_helpers.py` with the shared `MANDATORY_SOURCE` snippet (see Design Notes -- fixture helper convention).
- [ ] Task 2.4: Update every full-RSK-document fixture to include `## Source` (the verified 15-file list in REQ-008); the per-tool rsk test files import `MANDATORY_SOURCE` from the new helper.
- [ ] Task 2.5: Add the new unit tests per REQ-009: parses-with-source; fails-without (message content asserted); misordering regression (`## Source` before `## Tags`; after `## More Information`) with the temporary-field-reorder spot-check that the test genuinely depends on the order guard (restore immediately; leave no reverted state in the diff).
- [ ] Task 2.6: Quality gate (REQ-014) -- expect `rsk_schema.json` (both copies; `source` now required) + the touched modules' API docs; full suite green; commit per REQ-016, e.g. `feat(rsk): add mandatory ## Source section (BREAKING for pre-existing rsk documents) (#102) (#133)`.

#### Phase 3: #102 -- template, example, schema resource

- [ ] Task 3.1: In `rsk/data/rsk_template.md`, add `## Source` between `## Tags` and `## More Information` with a placeholder line in template style (e.g. "The origin or authority of this risk -- the QA document, discussion, or report it derives from.").
- [ ] Task 3.2: In `rsk/data/rsk_example.md`, add `## Source` with representative provenance content (e.g. "QA interview 2026-09-17 -- risk elicitation for the document-processing upload pipeline (issue #15's worked example).").
- [ ] Task 3.3: Confirm `specmgr schema` regenerates `docs/rsk_schema.json` + packaged `rsk/data/rsk_schema.json` with `source` required (verified in the gate; the data files themselves are not regenerated).
- [ ] Task 3.4: Quality gate (REQ-014); commit per REQ-016, e.g. `feat(rsk): document mandatory ## Source in template and example (#102) (#133)`.

#### Phase 4: #102 -- prompts

- [ ] Task 4.1: In `rsk/data/rsk_create_instructions.md`, add a `## Source` bullet to the structure recap (mandatory single-line value: the origin/authority of the risk, e.g. the QA document or discussion it derives from) positioned between the `## Tags` and `## More Information` bullets, and add source to the mandatory elicit list in step 2 (the current "optionally owner, tags, and more information" stays as-is).
- [ ] Task 4.2: In `rsk/data/rsk_update_instructions.md`, add the mandatory single-line `source` value to step 3's body-change enumeration (which currently lists the mandatory `cause`/`trigger`/`consequence`/`scope`/assessments/`strategy`/`mitigation` fields, then "any of the optional `owner`/`tags`/`more_information` sections").
- [ ] Task 4.3: Update `tests/rsk/prompts/test_create_risk.py` and `test_update_risk.py` text assertions for the new instruction content.
- [ ] Task 4.4: Quality gate (REQ-014) -- expect no `specmgr docs` content change (no `.py` docstrings touched); commit per REQ-016, e.g. `feat(rsk): narrate mandatory ## Source in create/update prompts (#102) (#133)`.

#### Phase 5: Docs, housekeeping, close-out

- [ ] Task 5.1: In `AGENTS.md`'s rsk bullet (REQ-010), document the mandatory `## Source`, the `## Tags` WithNotes alignment, and the previously-undocumented optional `## Owner`/`## More Information` sections (worded like the `dec` bullet's own section enumeration), referencing this feature.
- [ ] Task 5.2: In `CHANGELOG.md`'s `[Unreleased]` (REQ-011), add `### Added` -- rsk `## Source` (mandatory), `**BREAKING**`-marked with a before/after migration snippet; and `### Changed` -- rsk `## Tags` item type aligned to `MarkdownListItemWithNotes` (non-breaking).
- [ ] Task 5.3: In this README (REQ-012 close-out), verify the Design Notes' known-limitations note is current, add the final dated Updates entry, check every Acceptance Criterion box that is met, set frontmatter `status` to `done`, and bump `updated`.
- [ ] Task 5.4: Post the GitHub comment on issue #102 per REQ-013 (DEC half shipped via feat-29/issue #29; RSK half shipped here as **mandatory** -- breaking note + pointer to the CHANGELOG migration snippet) and close the issue.
- [ ] Task 5.5: Quality gate (REQ-014); commit per REQ-016, e.g. `docs(rsk): AGENTS.md/CHANGELOG close-out for rsk Source + Tags alignment (#102) (#133)`; final check that every commit on the branch contains both `#102` and `#133` in its message (REQ-016/ACC-012).

## Progress

### Current Status

**As of 2026-09-20**: **Planning.** This README has been replaced with the combined #102 + #133 plan (see Updates below); nothing is implemented yet. The remaining scope is small and fully scoped: one mandatory section added to one domain (`rsk` `## Source`, breaking per the feat-29 treatment) plus a one-line `## Tags` item-type alignment that closes #133. Implementation is deferred to a later session: an Orchestrator agent should execute Phase 0 directly, then dispatch Phases 1-5 one `phase-implementer` each (REQ-015), with the full quality gate after every phase (REQ-014) and both `#102` and `#133` in every commit message (REQ-016).

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-20 08:07:44.000Z - Combined plan written (this README replaced); implementation deferred

Rewrote this feature's plan from a stale #133-only scope into the combined #102 + #133 plan above, after a full audit of `dev` (v0.29.0): (1) the DEC halves of *both* issues already shipped via `feat-29-dec-source-roles` (issue #29, merged as `248568c`) -- DEC `## Tags` and DEC `## Source` (mandatory); (2) the RSK half of #133 already exists -- `Risk` has carried `tags: Tags | None` since the rsk domain was created (feat-15; the only commit in `rsk/models/v1/body.py`'s history), with template/example/prompt/test coverage complete -- the original 2026-09-17 plan here was written without knowing that; (3) the RSK half of #102 is the only genuinely missing piece. User decisions recorded (see Decisions Made): rsk `## Source` is **mandatory** (diverging from the issue's "optional" wording, for consistency with the shipped REQ/DEC design -- breaking, feat-29 treatment) and rsk `## Tags` aligns to `MarkdownListItemWithNotes` (req/dec/gol parity; strict parsing superset). Also recorded: the folder will be renamed to `feat-102-133-rsk-tags-source` in Phase 0 (`set_feat_id`), every commit must reference both issues with `#` syntax (REQ-016), the import-time sentinel in `rsk/tools/_sentinel.py` must gain `## Source` in the same phase as the schema change (REQ-003), and -- discovered while validating this rewrite against the feat schema -- that a standalone `### Known Limitations` heading is not part of the current feat schema (feat-29's own merged README fails `parse_feat` for exactly that reason), so this plan carries its known limitations inside Design Notes instead. No code, tests, or docs outside this README were changed -- planning only. Frontmatter `status` remains `planning`; `updated` bumped.

#### 2026-09-17 00:00:01.000Z - Rescoped to RSK-only

Dropped every `dec`-related requirement/acceptance-criterion/task from this feature's plan: the DEC half of the original scope (`## Tags` on `dec`) shipped as part of `feat-29-dec-source-roles` (GitHub issue #29), which absorbed it while already touching `dec/models/v1/body.py` for its own `## Roles and Responsibilities`/`## Source` work. This feature now tracks only the `rsk`-side `## Tags` addition. A comment was posted on GitHub issue #133 noting the absorption. See "Decisions Made" below for the rationale.

#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #133 to track adding optional `## Tags` sections to `dec` and `rsk`, split out of a broader related-artifact discovery request (see feat-134-related-artifact-similarity, issue #134, for the companion similarity-engine feature).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-20 08:07:44.000Z - Commit messages must reference both issues with `#` syntax

User requirement, recorded as REQ-016/ACC-012: every commit made for this feature (Phase 0 through Phase 5, including Phase 0's own setup commits) mentions both `#102` and `#133` in the commit message using GitHub's `#` syntax, so the eventual PR merge links and closes both issues. Follows the repo's observed `type(scope): subject (#issue) (#PR)` squash-merge style with both issue references present.

#### 2026-09-20 08:07:44.000Z - rsk `## Source` is mandatory, not optional (user decision)

Issue #102's own wording suggested an optional `## Source`. After the feat-29 breaking implications were laid out (existing rsk documents fail to parse until `## Source` is added; `list_rsk` degrades gracefully; ~15 test fixtures churned; a CHANGELOG migration snippet required), the user explicitly chose **mandatory**, for consistency with the shipped REQ and DEC design (both have mandatory `## Source` via REQ's own schema and feat-29). Consequence: this feature is a breaking, in-place `rsk/models/v1` evolution (no version bump, per REQ-005's precedents), treated exactly per feat-29 -- see the known-limitations note in Design Notes.

#### 2026-09-20 08:07:44.000Z - rsk `## Tags` aligns to `MarkdownListItemWithNotes` (user decision)

rsk's long-shipped `## Tags` used plain `MarkdownListItem` while `req`/`dec`/`gol` all use `MarkdownListItemWithNotes` (which captures loose-list continuation paragraphs in `notes` instead of silently dropping them). The user chose to align rsk (issue #133 asks to "mirror the existing `req` Tags convention"; this plan's predecessor specified `MarkdownListItemWithNotes` in its original REQ-001). The change is a strict parsing superset -- plain tags parse identically -- so it introduces no breakage of its own; the feature's breaking impact comes solely from the mandatory `## Source`.

#### 2026-09-20 08:07:44.000Z - Consolidated #102 into this feature; folder rename planned

Issue #102 (no feature folder existed for it) is consolidated into this feature because both issues reduce to the same domain (`rsk`), the same mechanism (a `SourceBase`-derived mandatory section + a Tags item-type alignment), and the same "already half-shipped, needs closing out" character -- the DEC halves of both shipped via feat-29. Single feature, separate phases, full quality gate per phase (user requirement). The folder is renamed `feat-133-tags-dec-rsk` -> `feat-102-133-rsk-tags-source` in Phase 0 via `set_feat_id` (multi-issue naming precedent: `feat-81-83-validation`, `feat-104-109-...`); the folder was in `planning` state with no branch and no commits, so the rename is cost-free.

#### 2026-09-17 00:00:01.000Z - Rescope to RSK-only; DEC half absorbed by feat-29

`feat-29-dec-source-roles` (GitHub issue #29) independently needed to touch `dec/models/v1/body.py` for its own `## Roles and Responsibilities` and `## Source` sections, and its own "Decisions Made" log records the decision to absorb this feature's DEC half (`## Tags` on `dec`) into that pass rather than keep it as a separate cross-feature dependency (recorded there, not here, since feat-29 is the feature that actually implemented and shipped it). Consequence: this feature (`feat-133-tags-dec-rsk`) is rescoped to RSK-only -- every `dec`-related requirement, acceptance criterion, and task is dropped from this plan (not renumbered with gaps, since nothing outside this file referenced the old numbering), and the Overview/Scope/Design Notes sections above are updated to reflect the narrower scope.

#### 2026-09-17 00:00:00.000Z - Split from the similarity-engine feature

Tags-on-dec/rsk was split into its own small, independent feature/issue (#133) rather than bundled with the larger embedding-similarity engine (#134/feat-134), since it has no new dependencies and can ship independently.

### Related PRs / Commits

- [Issue #102](https://github.com/dfch/biz.dfch.SpecMgr/issues/102): tracking issue for the rsk `## Source` half of this feature (the DEC half shipped via feat-29-dec-source-roles, issue #29).
- [Issue #133](https://github.com/dfch/biz.dfch.SpecMgr/issues/133): tracking issue for the `## Tags` alignment (the DEC half shipped via feat-29-dec-source-roles, issue #29; the rsk `## Tags` section itself has existed since feat-15).
- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29) / `feat-29-dec-source-roles`: shipped both issues' DEC halves (DEC `## Tags` and DEC `## Source`); its README's historical pointer to the old `feat-133-tags-dec-rsk` folder name goes stale at the Phase 0 rename (accepted -- see Design Notes' known limitations).
- No branch/commits exist for this feature yet; Phase 0 creates branch `feat-102-133-rsk-tags-source` from `dev`.

### More Information

None.
