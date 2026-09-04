---
classification: null
created: '2026-09-04 21:02:26.742+02:00'
id: feat-46-remove-adr
status: planning
type: feat
updated: '2026-09-04 22:55:15.075+02:00'
version: 1.0.0
---

# Feature: Remove the ADR Artifact Type in Favor of DEC

## Plan

### Overview

The repository currently maintains two overlapping decision-record artifact types: `ADR` (Architecture Decision Record — the original, most complete domain, per `AGENTS.md`) and `DEC` (Decision — a more general decision type introduced later, built on the same generic `models/md` parser). GitHub issue #46 asks that ADR be removed entirely in favor of DEC: every existing ADR document is converted to an equivalent DEC document, every reference to an ADR anywhere in the repository is updated to point at its DEC replacement, and the ADR-specific tooling (MCP tools/resources/prompts, schema package, tests, CI/pre-commit hooks) is deleted. `README.md` already flags ADR as "deprecated, will be phased out, use DEC instead" — this feature completes that phase-out. Per the issue, only this repository's own ADRs are in scope; other repositories using ADRs are explicitly not our concern.

### Requirements

- REQ-001: Every existing `docs/adr/*.md` document (30 total) is converted to an equivalent DEC document that reuses the original ADR's UUID as the new DEC document's `id`.
- REQ-002: Every reference to a converted ADR id anywhere in the repository (source code, `docs/`, `.specmgr/`, `README.md`, `AGENTS.md`, `CHANGELOG.md`, including historical session transcripts) is updated from `ADR <uuid>` to `DEC <uuid>` for that same uuid.
- REQ-003: The `adr` MCP domain package (`src/biz/dfch/specmgr/adr/` — tools, resources, prompts, data) and its schema package (`src/biz/dfch/specmgr/models/adr/`) are removed from `src/`, and `pyproject.toml`'s `[tool.setuptools.package-data]` `"biz.dfch.specmgr.adr"` entry is removed with them.
- REQ-004: All ADR-specific test suites (`tests/adr/`, `tests/models/adr/`) are removed, and cross-cutting tests that assert ADR's inclusion/exclusion behavior (`set_status`, `set_classification`, `_path_safety`, `config` resource, `summary` model, `docs`/`schema`/`mcp_docs` commands) are updated to reflect ADR's removal.
- REQ-005: ADR special-casing is removed from `general/tools/set_status.py` (the adr dispatch branch and `superseded_by` handling), `general/tools/_path_safety.py` (`_UUID_TYPES`), `general/resources/config.py` (the adr `DomainConfig` entry), `general/models/summary.py`, `general/tools/__init__.py`, `server.py` (registration import + docstring), `cli.py`, `models/config_info.py`, and `commands/docs.py` / `commands/schema.py` / `commands/mcp_docs.py`; `commands/adr_toc.py` is deleted outright.
- REQ-006: The `specmgr-adr-toc` pre-commit hook (`.pre-commit-config.yaml` lines 57-66) and the CI "`docs/adr/README.md` is correct" step (`.github/workflows/ci.yml` lines 77-84) are removed.
- REQ-007: The original `docs/adr/*.md` files and the generated `docs/adr/README.md` TOC are archived (not hard-deleted) to a clearly labeled location once every ADR has a converted DEC counterpart.
- REQ-008: `README.md`, `AGENTS.md`, and `CHANGELOG.md` are updated to remove ADR-as-artifact-type language (the deprecated-artifact bullet, `SPECMGR_ADR_DIR` docs, the ADR domain bullet, the "models location" exception paragraph, and every generic-tool description that lists adr as a supported/excluded type), while ADR-id citations are rewritten to their DEC-id equivalents per REQ-002 rather than deleted.
- REQ-009: Generated documentation (`docs/GENERATED.md`, `docs/MCP.md`, `docs/api/*`) is regenerated via `specmgr docs` / `specmgr mcp-docs` after code removal and contains zero leftover adr tool/resource/prompt entries.
- REQ-010: The full local quality gate (ruff format/check, vulture, pytest `-n auto`) passes cleanly after all changes.
- REQ-011: `DecFrontmatter` is extended with the ADR-provenance attributes decided in Task 0.1 (GitHub issue #29), closing that issue before any ADR document is converted to DEC.

### Acceptance Criteria

- [ ] ACC-001: `list_dec` shows 30 additional decisions, each with an `id` matching a previously-existing ADR's `id`, and each parses/validates via `parse_dec`/`validate_dec`.
- [ ] ACC-002: A repo-wide search for the pattern `ADR <uuid>` for any of the 30 migrated uuids returns zero matches outside the archived `docs/adr/` files; the equivalent `DEC <uuid>` citations are present at every one of those locations instead.
- [ ] ACC-003: `src/biz/dfch/specmgr/adr/` and `src/biz/dfch/specmgr/models/adr/` no longer exist on disk, and `pyproject.toml` no longer has a `"biz.dfch.specmgr.adr"` package-data entry.
- [ ] ACC-004: `tests/adr/` and `tests/models/adr/` no longer exist, and `pytest -n auto --cov=src` passes with no adr-related failures or collection errors.
- [ ] ACC-005: `general/tools/set_status.py`, `_path_safety.py`, `general/resources/config.py`, and `models/config_info.py` contain no remaining reference to `"adr"` as a supported type/domain.
- [ ] ACC-006: `.pre-commit-config.yaml` and `.github/workflows/ci.yml` contain no `adr-toc`/`docs/adr/README.md` hook or step.
- [ ] ACC-007: `docs/adr/*.md` and `docs/adr/README.md` exist only under the chosen archive location, clearly marked as superseded by their DEC counterparts.
- [ ] ACC-008: `README.md`'s artifact-type list no longer mentions ADR as a current or deprecated type, `AGENTS.md` no longer describes an `adr` domain bullet or a `models/adr/` exception paragraph, and `CHANGELOG.md` no longer carries any `ADR <uuid>` citation for a migrated id.
- [ ] ACC-009: `docs/GENERATED.md` and `docs/MCP.md`, freshly regenerated, contain zero `adr`-domain tool/resource/prompt entries.
- [ ] ACC-010: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto --cov=src --cov-report=` all pass with no new warnings/failures attributable to this removal.
- [ ] ACC-011: `DecFrontmatter`'s extended schema (Task 0.1/0.2) validates against a sample of the 28 ADRs carrying `date`/`decision-makers` data with zero information loss, `tests/dec/models/v1/test_frontmatter.py` covers the new fields, and GitHub issue #29 is closed.

### Scope

#### Included

- Extending `DecFrontmatter` with the ADR-provenance attributes needed to preserve `date`/`decision-makers`/`consulted`/`informed` (and any DEC-specific equivalents such as `source`/`owner`) end-to-end through conversion, closing GitHub issue #29.
- Converting all 30 existing `docs/adr/*.md` documents into DEC documents that reuse the original ADR UUID as their `id`.
- Archiving the original `docs/adr/` raw files and TOC once conversion is verified.
- A repo-wide find/replace of `ADR <uuid>` to `DEC <uuid>` (same uuid) for all 30 converted ids, across `src/`, `docs/`, `.specmgr/` (including historical session transcripts), `README.md`, `AGENTS.md`, and `CHANGELOG.md`.
- Removing the `adr/` and `models/adr/` source packages and their tests, and the matching `pyproject.toml` package-data entry.
- Removing ADR special-casing from `general/tools/` (`set_status`, `_path_safety`, `config` resource), `server.py`, `cli.py`, `models/config_info.py`, and `commands/` (`adr_toc`, `docs`, `schema`, `mcp_docs`).
- Removing the `specmgr-adr-toc` pre-commit hook and its CI step.
- Updating `README.md`/`AGENTS.md`/`CHANGELOG.md` prose that describes the ADR domain as a current or deprecated artifact type.
- Regenerating `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/*`.
- Re-running the full local quality gate to confirm a clean removal.

#### Explicitly Out Of Scope

- Any changes to other repositories' ADRs (per issue #46: "We do not care about other repos with ADRs").
- Adding new capabilities to the `dec` domain to make it a superset of ADR's fine-grained option-mutation tools (`option_create`/`option_read`/etc.) — DEC already uses the generic whole-body `update` tool per existing design (AGENTS.md).
- Adding a `set_dec_id`-style tool or any other new generic tool; the UUID-preserving rename described in Design Notes is a one-time manual migration step, not a shipped tool capability.
- Rewriting the decision *content* of migrated ADRs beyond what's needed to fit the DEC schema — no re-litigating old decisions.
- Building a reusable, general-purpose ADR-to-DEC conversion CLI command — this is treated as a one-time repository migration.

### Design Notes

`create_dec` always assigns a fresh, server-generated UUID and has no parameter to force a specific `id` (unlike `create_feat`'s optional `id`, or the dedicated `set_feat_id` tool for later renames). Preserving each ADR's original UUID on its DEC counterpart therefore requires a manual step per document, outside the standard tool-only workflow:

1. Call `create_dec` with a body adapted from the ADR's content to the DEC/generic-`models/md` schema (mapping MADR-style sections and `### Option N` sub-sections into DEC's structure).
2. Locate the newly created file under the DEC base directory (default `docs/dec/`, or `SPECMGR_DEC_DIR` if overridden).
3. Rename the file to mirror the old ADR's filename convention adapted to DEC's naming shape, and hand-edit the YAML frontmatter `id` field to reuse the original ADR UUID in place of the freshly minted one.
4. Re-validate the hand-edited file with `parse_dec`/`validate_dec` to confirm the manual edit didn't break the schema.

Because the UUID is preserved end-to-end, reference updates reduce to a simple, low-risk find/replace of `ADR <uuid>` to `DEC <uuid>` for that exact uuid, repo-wide — no separate id-mapping table is needed, and historical citations (including old `.specmgr/` session transcripts) remain accurate and traceable.

`AGENTS.md`'s "Models location" paragraph currently justifies `models/adr/` as "the single exception" to domain-first schema placement; once `adr`/`models/adr` are removed, that paragraph must be rewritten to drop the exception entirely — top-level `models/` then holds only `md/`, `iso25010.py`, and `version_info.py`.

`general/tools/set_status.py`'s `superseded_by` parameter exists solely to support ADR's "superseded by X" status composition. Once ADR (its only consumer) is removed, whether to drop the parameter entirely from the generic tool signature or leave it as a harmless no-op is an open implementation decision, deferred to Phase 4.

This feature also closes GitHub issue #29 ("Artifact type 'Decision' (DEC) need additional attributes from ADR frontmatter"), previously tracked as feat-7's Task 0.33: `DecFrontmatter` currently narrows only `type`/`status` on top of the generic `MarkdownFrontmatter` (`id`/`created`/`updated`/`version`/`classification`) and has no field for any of `AdrFrontmatter`'s `date`/`decision-makers`/`consulted`/`informed` — all four populated on 28 of the 30 real ADRs being converted. Phase 0 below resolves and implements the extension before conversion starts, so no provenance data is lost; Phase 0 must fully complete before Phase 1 begins, since Phase 1's conversion depends on Task 0.1/0.2's `DecFrontmatter` extension existing first. Separately, DEC's `ProsAndCons` model uses a `LITERAL` alias for `## Pros and Cons` and rejects ADR's `## Pros and Cons of the Options` heading text outright — Task 1.2's body adaptation must rewrite that heading, not merely map it structurally.

A parser quirk was discovered while drafting this document: soft-wrapped list/checklist item text (a bullet's text continued onto an indented second physical line) breaks `create_feat`/`validate_feat` with an opaque error. Every list/checklist item in this document is therefore written as a single physical line, however long. This is tracked separately as GitHub issue #99 and is not itself part of this feature's scope.

### Task List

#### Phase 0: Resolve Open Design Questions and Plan Corrections

- [ ] Task 0.1: Resolve GitHub issue #29 ("Artifact type 'Decision' (DEC) need additional attributes from ADR frontmatter") by deciding the exact attribute set `DecFrontmatter` (`dec/models/v1/frontmatter.py`) must gain — at minimum `date`, `decision_makers`, `consulted`, `informed` (the four fields `AdrFrontmatter` defines beyond the shared `MarkdownFrontmatter` base) plus the issue's own named examples `source`/`owner` if still relevant once DEC subsumes ADR's role — and record the decision here in Decisions Made.
- [ ] Task 0.2: Implement the `DecFrontmatter` extension chosen in Task 0.1 (new optional fields, validators, `docs/dec_schema.json` regeneration, docstring updates) and extend `tests/dec/models/v1/test_frontmatter.py` to cover the new fields, closing GitHub issue #29.
- [ ] Task 0.3: Post a comment on GitHub issue #29 cross-referencing this feature (`feat-46-remove-adr`) and its tracking issue #46, and annotate feat-7's Task 0.33 (`.specmgr/feat/feat-7-various-improvements/README.md`) as subsumed by feat-46, mirroring that file's existing Task-0.29-subsumption convention.
- [ ] Task 0.4: Confirm the 28 (of 30) `docs/adr/*.md` documents that populate `date`/`decision-makers` map cleanly onto the Task 0.1 field set, and record how the 2 without that data are handled.
- [ ] Task 0.5: Update the Design Notes' conversion procedure to state explicitly that `## Pros and Cons of the Options` (ADR's heading text) must be rewritten to `## Pros and Cons` during Task 1.2's body adaptation.
- [ ] Task 0.6: Add the following files — found during planning to reference `adr` but omitted from the requirements' file lists before this review — to their respective requirement/scope bullets: `pyproject.toml` (`[tool.setuptools.package-data]`'s `"biz.dfch.specmgr.adr"` entry, REQ-003/Phase 3), `CHANGELOG.md` (11 `ADR <uuid>` citations including one in the still-open `[Unreleased]` section, REQ-002/REQ-008), and `src/biz/dfch/specmgr/models/config_info.py` (adr domain-enumeration docstring, REQ-005).
- [ ] Task 0.7: Add explicit Phase 4 task list entries for updating the cross-cutting test files REQ-004's second clause already promises but the current Task List never assigns: `tests/general/tools/test_set_status.py`, `test_set_classification.py`, `test__path_safety.py`, `tests/general/resources/test_config.py`, `tests/general/models/test_summary.py`, `tests/commands/test_docs.py`, `test_schema.py`, `test_mcp_docs.py`.
- [ ] Task 0.8: Decide the fate of `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` (the 481-line ADR design/plan doc that `AGENTS.md` currently says must be "kept in sync with `src/`") — archive it alongside `docs/adr/` per REQ-007, mark its own status as superseded, or leave it untouched — and update `AGENTS.md`'s reference to it accordingly.
- [ ] Task 0.9: Correct this document's own frontmatter/body inconsistencies found during planning: bump `updated` so it is no earlier than the latest `## Updates` entry timestamp, and reconcile the "hundreds of `ADR <uuid>` citations" wording in Current Status with the actual repo-wide count (983 verified, outside `docs/adr/`).

#### Phase 1: Convert ADR Documents to DEC (preserving UUIDs)

- [ ] Task 1.1: Inventory all 30 `docs/adr/*.md` documents (id, title, body content) as the conversion source list.
- [ ] Task 1.2: For each ADR, call `create_dec` with a body adapted to the DEC/generic-md schema.
- [ ] Task 1.3: For each newly created DEC file, rename it and hand-edit its frontmatter `id` to reuse the original ADR's UUID, then re-validate with `parse_dec`/`validate_dec`.
- [ ] Task 1.4: Spot-check a sample of converted DEC documents against their original ADR content for fidelity (no lost decision text/options/frontmatter provenance).

#### Phase 2: Update All References Repo-Wide

- [ ] Task 2.1: For each of the 30 preserved uuids, find every `ADR <uuid>` occurrence across `src/`, `docs/`, `.specmgr/`, `README.md`, `AGENTS.md`, `CHANGELOG.md`.
- [ ] Task 2.2: Replace each `ADR <uuid>` citation with `DEC <uuid>` (same uuid), preserving surrounding text/formatting.
- [ ] Task 2.3: Update prose descriptions of the artifact type itself (not just id citations) in `README.md`'s artifact list, `AGENTS.md`'s ADR bullet / models-location paragraph / tool-listing sections, and `CHANGELOG.md`'s `[Unreleased]` entry.

#### Phase 3: Remove the ADR Domain Package and Schema

- [ ] Task 3.1: Delete `src/biz/dfch/specmgr/adr/` (tools, resources, prompts, data).
- [ ] Task 3.2: Delete `src/biz/dfch/specmgr/models/adr/`.
- [ ] Task 3.3: Remove the `adr` import from `server.py`'s registration line and its module docstring entries (tools/resources/prompts listings).
- [ ] Task 3.4: Remove `adr_toc` from `cli.py` and delete `commands/adr_toc.py`.
- [ ] Task 3.5: Delete `tests/adr/` and `tests/models/adr/`.
- [ ] Task 3.6: Remove the `"biz.dfch.specmgr.adr"` entry from `pyproject.toml`'s `[tool.setuptools.package-data]`.

#### Phase 4: Remove ADR Special-Casing from Generic/Cross-Cutting Code

- [ ] Task 4.1: Remove the adr dispatch branch (`_TYPE_ADR`, `_set_status_adr`) from `general/tools/set_status.py`, and resolve the `superseded_by` parameter per the Design Notes' open question.
- [ ] Task 4.2: Remove `"adr"` from `general/tools/_path_safety.py`'s `_UUID_TYPES` set and update its docstring/comments.
- [ ] Task 4.3: Remove the adr `DomainConfig` entry from `general/resources/config.py`.
- [ ] Task 4.4: Update docstrings/comments in `general/models/summary.py`, `general/tools/__init__.py`, and `models/config_info.py` that reference adr.
- [ ] Task 4.5: Update `commands/docs.py` and `commands/mcp_docs.py` to drop adr-specific handling; confirm `commands/schema.py`'s existing adr-exclusion note is removed or rephrased as no-longer-relevant.
- [ ] Task 4.6: Update `tests/general/tools/test_set_status.py`, `test_set_classification.py`, and `test__path_safety.py` to drop adr-specific fixtures/assertions and cover the removed dispatch branch's absence.
- [ ] Task 4.7: Update `tests/general/resources/test_config.py` and `tests/general/models/test_summary.py` to drop adr-specific fixtures/assertions.
- [ ] Task 4.8: Update `tests/commands/test_docs.py`, `test_schema.py`, and `test_mcp_docs.py` to drop adr-specific fixtures/assertions.
- [ ] Task 4.9: Re-run vulture/`whitelist.py` check for any new dead-code false positives left behind by the removal.

#### Phase 5: Retire CI/Pre-commit Hooks and Archive Historical ADR Files

- [ ] Task 5.1: Delete `.pre-commit-config.yaml` lines 57-66 (the `specmgr-adr-toc` hook block).
- [ ] Task 5.2: Delete `.github/workflows/ci.yml` lines 77-84 (the "Make sure `docs/adr/README.md` is correct" step).
- [ ] Task 5.3: Move the 30 original `docs/adr/*.md` files and `docs/adr/README.md` to an archive location, clearly labeled as superseded by their DEC counterparts.
- [ ] Task 5.4: Regenerate `docs/GENERATED.md`, `docs/MCP.md`, and `docs/api/*` via `specmgr docs`/`specmgr mcp-docs` and confirm no leftover adr entries.

#### Phase 6: Final Validation

- [ ] Task 6.1: Run the full local quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`) and confirm a clean pass.
- [ ] Task 6.2: Manually review `README.md`, `AGENTS.md`, and `CHANGELOG.md` end-to-end for any remaining ADR-as-artifact-type language.
- [ ] Task 6.3: Confirm `docs/MCP.md`/`GENERATED.md` contain zero adr tool/resource/prompt entries and that `list_dec`/`get_dec` surface all 30 migrated decisions correctly.

## Progress

### Current Status

**As of 2026-09-04**: Feature planned from GitHub issue #46 and a full-repo inventory of the ADR footprint (30 ADR documents; the `adr/` and `models/adr/` packages; 27 dedicated test files; CI/pre-commit hooks; and roughly 1,000 `ADR <uuid>` citations across `AGENTS.md`, `docs/`, `CHANGELOG.md`, and `.specmgr/`). A plan review surfaced a hard prerequisite — GitHub issue #29's `DecFrontmatter` attribute gap — plus several plan-completeness gaps, now tracked as a blocking Phase 0. No conversion or code removal has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 21:40:00.000Z - Plan review: added blocking Phase 0 for issue #29 and other gaps

A plan-review pass (agent-assisted) checked every Requirement/Acceptance-Criterion/Task claim against the actual repo state and found: (1) GitHub issue #29 ("DEC needs additional ADR-style frontmatter attributes"), already tracked as feat-7's Task 0.33 and not-started, is a hard prerequisite for this feature's own fidelity goal — 28 of the 30 ADRs being converted populate `date`/`decision-makers`, which `DecFrontmatter` currently has nowhere to hold; (2) DEC's `## Pros and Cons` heading rejects ADR's `## Pros and Cons of the Options` wording outright; (3) `pyproject.toml`, `CHANGELOG.md`, and `models/config_info.py` reference `adr` but were missing from the requirement file lists; (4) REQ-004's promise to update cross-cutting tests had no corresponding Task List entries; (5) this document's own `## Updates` timestamps ran ahead of its frontmatter `updated` field. Added REQ-011/ACC-011, a new Scope-Included bullet, two new Design Notes paragraphs, and a new blocking Phase 0 (Tasks 0.1-0.9) that resolves all of the above before Phase 1 starts; Phase 4 gained Tasks 4.6-4.8 for the previously-untracked cross-cutting test updates.

#### 2026-09-04 21:20:00.000Z - Design session wrapped up

Closed out the planning session for this feature. While drafting this document, a `models/md` parser quirk was discovered and reported separately as GitHub issue #99 (soft-wrapped list items break `create_feat`/`validate_feat` with an opaque error) — not part of this feature's own scope, but noted here for cross-reference since it was found during this feature's own drafting. See Decisions Made below for the four scoping decisions resolved during the design session.

#### 2026-09-04 00:00:00.000Z - Feature planned

Drafted the phased removal plan for the ADR artifact type (convert to DEC preserving UUIDs, update all references, remove ADR tooling/tests/CI hooks, archive historical files) based on GitHub issue #46 and a full codebase inventory of ADR's footprint.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 21:40:00.000Z - Fold GitHub issue #29 into this feature as a blocking Phase 0

Decided (per explicit direction) that this feature addresses GitHub issue #29 itself, rather than leaving it as a separate feat-7 line item: extending `DecFrontmatter` with ADR-provenance attributes (Task 0.1/0.2) is a blocking Phase 0, sequenced strictly before Phase 1's conversion work, since converting ADRs before DEC can hold their `date`/`decision-makers`/`consulted`/`informed` data would silently lose it. A cross-reference comment will be posted on issue #29 and feat-7's Task 0.33 annotated as subsumed by this feature, mirroring the existing Task-0.29/feat-27 subsumption precedent in feat-7's own README.

#### 2026-09-04 21:20:00.000Z - Scoping decisions for the ADR removal

Four scoping decisions were resolved during the design session, all reflected in Requirements/Scope/Design Notes above: (1) each converted DEC document reuses its source ADR's UUID via a manual create-then-rename-then-hand-edit-id procedure, rather than accepting a fresh UUID and building a separate id-mapping table; (2) because the UUID is preserved, reference updates cover the entire repository, including historical `.specmgr/` session transcripts, not just currently-maintained documentation; (3) the original `docs/adr/*.md` files and TOC are archived rather than hard-deleted once converted, for provenance; (4) the whole removal (doc conversion, reference updates, code/test/CI removal) is delivered as a single phased feature matching the single GitHub issue #46, rather than split across multiple features.

### Related PRs / Commits

- [Issue #46](https://github.com/dfch/biz.dfch.SpecMgr/issues/46): tracking issue for this feature.
- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29): "Artifact type 'Decision' (DEC) need additional attributes from ADR frontmatter" — resolved as this feature's blocking Phase 0, not as feat-7's Task 0.33.
- [Issue #99](https://github.com/dfch/biz.dfch.SpecMgr/issues/99): parser bug discovered while drafting this feature's plan (soft-wrapped list items break `create_feat`/`validate_feat`); tracked independently, not part of this feature's scope.
