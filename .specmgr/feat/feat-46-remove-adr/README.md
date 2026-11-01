---
classification: null
created: '2026-09-04T21:02:26.742+02:00'
id: feat-46-remove-adr
status: planning
type: feat
updated: '2026-11-01T07:34:30.000+01:00'
version: 1.0.0
---

# Feature: Remove the ADR Artifact Type in Favor of DEC

## Plan

### Overview

The repository maintains two overlapping decision-record artifact types: `ADR` (the original domain, a bespoke module under `adr/` and `models/adr/`) and `DEC` (the later, more general decision type built on the generic `models/md` parser). GitHub issue #46 asks to remove ADR entirely: every ADR in this repository is converted to a DEC that reuses the ADR's UUID (and its file name), every reference is retargeted from `ADR <uuid>` to `DEC <uuid>`, and the ADR code, tests, hooks and prose are removed. Only this repository's own ADRs are in scope. This plan replaces the earlier 2026-09-04 plan, which predated the shipped DEC sections (GitHub issue #29), the generic `validate` tool, the `specmgr lint` gate and the script-assisted conversion; it keeps that plan's scoping decisions. The work is split into a data rollout (convert, verify, retarget) and a code removal, because the removal must not start before every ADR has a verified DEC.

### Requirements

- REQ-001: Every ADR in `docs/adr/` (46 at the time of the 2026-11-01 survey, listed in the committed manifest `adr-manifest.json`) MUST be converted to a DEC at `docs/dec/<uuid>-<slug>.md` that reuses the ADR's `id` and file name, following the "Convert an ADR to a DEC" SOP (SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a).
- REQ-002: Each DEC's frontmatter `created`/`updated` MUST equal the first/last git commit dates of the ADR file as frozen in the manifest, and no tool may bump them during the migration.
- REQ-003: Supersession MUST be recorded on the superseding DEC only (`## Related Artifacts` → `### Decisions`); the superseded DEC gets `status: superseded` and no outbound reference.
- REQ-004: Every citation of a migrated ADR id (`ADR <full uuid>`, `ADR <8-hex prefix>`, `docs/adr/<file>` paths) in tracked files outside the ADR sources and the generated files MUST be retargeted to the DEC equivalent, using the manifest as the only source of ids; ids that are not migrated ADRs MUST stay untouched.
- REQ-005: The `adr` domain package (`src/biz/dfch/specmgr/adr/`) and its schema package (`src/biz/dfch/specmgr/models/adr/`) MUST be removed together with their tests, the `pyproject.toml` package-data entry, the `adr-toc` command, and the `SPECMGR_ADR_DIR` registry entry and `server.json` manifest entry.
- REQ-006: ADR special-casing MUST be removed from the cross-cutting code: the generic tools (`set_status`'s `superseded_by`/adr branch, `_path_safety`, `update`/`delete`/`edit`/`set_classification`/`validate` dispatch), the domain registry (`_domains.py` and the `WholeBodyOrAdrType` alias), the reference tag vocabulary and diagram palette, `commands/lint.py`, `commands/docs.py`, `commands/schema.py`, `commands/mcp_docs.py`, `cli.py`, `server.py`, `general/resources/config.py`, `models/config_info.py`, `sysrs`' `^(DEC|ADR)` pattern, and the agent prompts that name ADR.
- REQ-007: The `specmgr-adr-toc` pre-commit hook and the CI step checking `docs/adr/README.md` MUST be removed.
- REQ-008: The original ADR files and the generated ADR table of contents MUST be archived (not deleted) under `docs/archive/adr/` once every DEC is verified.
- REQ-009: `README.md`, `AGENTS.md` and `CHANGELOG.md` MUST be updated to drop ADR-as-artifact-type language, with `ADR <uuid>` citations retargeted per REQ-004 instead of deleted, and `CHANGELOG.md` MUST record the breaking removal.
- REQ-010: Generated documentation (`docs/GENERATED.md`, `docs/MCP.md`, `docs/api/*`, the schema JSON copies) MUST be regenerated and contain no `adr` tool, resource, prompt or domain entry.
- REQ-011: The full local quality gate (ruff format and check, vulture, `pytest -n auto`, `specmgr lint --all`) MUST pass after the removal.
- REQ-012: No new ADR MAY be created from the start of the rollout (freeze); new decisions are DEC documents.

### Acceptance Criteria

- [ ] ACC-001: `200-120-verify-converted.sh --require-all` reports every ADR of the manifest converted and zero failing documents, and `list_dec` shows each migrated id as a healthy row with `error_count` 0 (REQ-001, REQ-002, REQ-003).
- [ ] ACC-002: `300-110-find-refs.sh --status retag --tiers ABCD` reports zero hits, and `300-110-find-refs.sh --status ambiguous` reports zero hits (REQ-004).
- [ ] ACC-003: `list_references` on a retargeted live document resolves the DEC for a migrated id with non-null `title` and `path` (REQ-004).
- [ ] ACC-004: `src/biz/dfch/specmgr/adr/` and `src/biz/dfch/specmgr/models/adr/` do not exist, `pyproject.toml` has no `biz.dfch.specmgr.adr` package-data entry, `tests/adr/` and `tests/models/adr/` do not exist, and `specmgr adr-toc` is not a command (REQ-005).
- [ ] ACC-005: `400-110-find-adr-code-refs.sh --gate` exits 0 (REQ-005, REQ-006, REQ-007).
- [ ] ACC-006: `.pre-commit-config.yaml` and `.github/workflows/ci.yml` contain no `adr-toc` hook/step and no `docs/adr/README.md` check; `server.json` and `_envregistry.py` contain no `SPECMGR_ADR_DIR` (REQ-005, REQ-007).
- [ ] ACC-007: `docs/adr/` does not exist and the 46 ADR files plus the TOC exist under `docs/archive/adr/` with a README marking them superseded by their DEC counterparts (REQ-008).
- [ ] ACC-008: `docs/GENERATED.md` and `docs/MCP.md`, freshly regenerated, contain zero `adr` entries and `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` leave no drift (REQ-010).
- [ ] ACC-009: `README.md` and `AGENTS.md` name no `adr` artifact type, domain bullet, models-location exception or `SPECMGR_ADR_DIR`, and `CHANGELOG.md` `[Unreleased]` records the breaking removal (REQ-009).
- [ ] ACC-010: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=` and `specmgr lint --all` all pass (REQ-011).
- [ ] ACC-011: `tests/` contains a regression test asserting that no `adr` tool, resource or prompt is registered on the MCP server (REQ-005, REQ-012).

### Scope

#### Included

- Converting every ADR to a DEC with the script-assisted procedure of the SOP, including the multi-block ADRs once feat-247 is released.
- The throw-away scripts in `bin/` and the committed manifest `adr-manifest.json`.
- Retargeting all citations of migrated ids across `src/`, `tests/`, `docs/`, `.specmgr/` (including historical transcripts), `README.md`, `AGENTS.md`, `CHANGELOG.md` and `.opencode/`.
- Removing the `adr` packages, tests, commands, registry/manifest entries, hook and CI step, and every ADR special case in the cross-cutting code and agent prompts.
- Archiving the ADR sources, regenerating the generated documentation, and updating the prose documents.
- Deciding the fate of `docs/req/req-678319da-...` (the ADR document management requirement), the `sysrs` document that cites ADRs, and the SOP after the migration.

#### Explicitly Out Of Scope

- Other repositories' ADRs (issue #46: "We do not care about other repos with ADRs").
- The DEC parser relaxation for multi-block Decision Outcome (GitHub issue #247, feature feat-247-dec-outcome-blocks), a prerequisite delivered separately.
- Rewriting decision content beyond the mechanical changes of the SOP.
- A reusable conversion command: the scripts are throw-away and removed with the migration.
- The sharded storage layout of GitHub issue #245: the target path `docs/dec/<uuid>-<slug>.md` follows today's flat layout; whichever feature lands second moves the files.
- Fine-grained option tools for DEC (`option_create` and friends); DEC keeps the generic whole-body tools.

### Dependencies

#### Depends On

- FEAT feat-247-dec-outcome-blocks: 20 of the 46 ADRs have a multi-block Decision Outcome that the `dec` parser rejects until it is released.
- SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a: the conversion procedure.

#### Blocks

- Nothing.

### Design Notes

**Scripts, not a command.** The conversion, verification and reference work is done by numbered throw-away scripts in `bin/` (`NNN-MMM-name.sh`, a Python helper `adr_dec_lib.py` shared by them, run with `uv run --frozen python` or `SPECMGR_PYTHON`). `100-110-survey-adrs.sh` classifies every ADR through a trial conversion into the real `parse_dec` and, with `--write`, freezes `adr-manifest.json` (git dates, derived Source and RASCI values, supersession links, wrapped token runs). `200-110-convert-adr.sh` is a dry run unless `--write` and never writes a failing or an existing file. `200-120-verify-converted.sh` checks the frontmatter against the manifest, the H1, the migration entry, fidelity (undoing exactly the allowed changes reproduces the ADR body) and supersession, then runs `specmgr lint --type dec`. `300-110-find-refs.sh` and `300-120-retag-refs.sh` find and retarget citations in tiers (G generated, A live artifacts, B src and tests, C prose, D transcripts), dry run by default; only manifest ids are touched, lines saying "Converted from ADR" are kept, and tier G is regenerated, never edited. `400-110-find-adr-code-refs.sh` is the checklist and `--gate` closes the removal phase. The scripts follow the sibling LlmOps convention (a header comment, `set -euo pipefail`, an embedded Python heredoc).

**Why a manifest.** The DEC `created`/`updated` are the ADR file's first and last commit dates. Any later commit under `docs/adr/` (the retag, the archive move) changes the last date, so the dates are captured once, before such a commit, and conversion and verification read only the manifest.

**Pilot result (2026-11-01, scratch).** Converting `519d1206` (wrapped token), `bfd76370` (wrapped tokens, issue source), `a156fdf9` (superseded) and `8cf940c5` (clean, default source) into a scratch `docs/dec/` verified clean (fidelity, frontmatter, `specmgr lint`); corrupting one converted file made the verifier fail on the parse, the frontmatter and the fidelity check. The pilot files were removed again. The survey classes: 26 clean, 20 blocked by feat-247, 0 needing judgment. `92cc4ce8` (the superseding DEC) is blocked, so its Related Artifacts bullet was verified on a copy with the outcome collapsed to one block.

**Citation tiers.** The retag covers about 2,000 full-uuid citations, 1,500 short-prefix citations and 580 path citations across about 700 files. Retagging tier B (src and tests) edits test fixtures; tests that assert behaviour for a migrated real uuid must be checked against the full test run, and the reference-graph golden fixtures and the config golden are regenerated only where the removal changes them (ADR domain entries), not by the retag. After the removal the `ADR` tag no longer resolves in `list_references`, so remaining `ADR <uuid>` citations in transcripts are retargeted too (tier D, a separate commit).

**Order matters.** Convert all ADRs and verify with `--require-all` before the retag (otherwise a retargeted `DEC <uuid>` does not resolve); retag before the removal (otherwise the removal gate sees thousands of citations); archive the ADR files only after the removal, and run the verifier against the archive with `--adr-dir`.

**The generic `set_status` `superseded_by` parameter** exists only for ADR's `superseded by X` status; it is removed with the adr branch.

Every list item in this document is written as a single physical line (the soft-wrap rule of GitHub issue #99).

### Related Decisions

- None; record a DEC if the removal surfaces a decision beyond the SOP rules.

### Task List

#### Phase 100: Preparation and Pilot

- [x] Task 100.100: Survey the 46 ADRs through a trial conversion into the real `parse_dec` and freeze `adr-manifest.json` (`100-110-survey-adrs.sh --write`).
- [x] Task 100.110: Revise the SOP (SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a) for the script-assisted conversion and the decisions recorded below.
- [x] Task 100.120: Write the scripts `100-110`, `200-110`, `200-120`, `300-110`, `300-120`, `400-110` and the shared helper in `bin/`, and verify them with a scratch pilot including a negative test.
- [ ] Task 100.130: Announce the freeze (no new ADR) in AGENTS.md or the create-adr prompt and commit the manifest, the scripts and the revised SOP before any commit touches `docs/adr/`.
- [ ] Task 100.140: Open the pull request for the preparation (plan, SOP, manifest, scripts) so the conversion is reviewed separately from the code removal.

#### Phase 110: Rollout A - Convert the Clean ADRs

- [ ] Task 110.100: Dry-run `200-110-convert-adr.sh --all` and review the candidate text of one ADR of each kind (clean, wrapped tokens, superseded) with `--show`.
- [ ] Task 110.110: Convert the 26 clean ADRs with `200-110-convert-adr.sh --write` for each id the survey classes `clean`, and commit the DEC files.
- [ ] Task 110.120: Run `200-120-verify-converted.sh` and fix any failing document by extending the script rule, never by hand-editing.
- [ ] Task 110.130: Read back one converted DEC of each kind with `get_dec` and confirm `list_dec` shows healthy rows with `error_count` 0 (SOP Gate 2).

#### Phase 120: Rollout B - Convert the Multi-Block ADRs

- [ ] Task 120.100: Wait for feat-247-dec-outcome-blocks to be released, then re-run `100-110-survey-adrs.sh` (without `--write`) and confirm the 20 blocked ADRs now classify `clean`; any other result is a new rule to add to the scripts.
- [ ] Task 120.110: Convert the remaining ADRs with `200-110-convert-adr.sh --write`, including the superseding `92cc4ce8`, and commit them.
- [ ] Task 120.120: Run `200-120-verify-converted.sh --require-all` (the rollout gate) and the supersession gate `list_references(type="dec", id="92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c")` (SOP Gate 3).

#### Phase 130: Retarget the References

- [ ] Task 130.100: Run `300-110-find-refs.sh` and review the `ambiguous`, `foreign` and `manual` rows; resolve every `manual` `docs/adr/` path citation by hand.
- [ ] Task 130.110: Run `300-120-retag-refs.sh --tiers A --apply`, review the diff and commit (live artifacts first).
- [ ] Task 130.120: Run `300-120-retag-refs.sh --tiers BC --apply`, run the test suite, fix tests that assert behaviour for a migrated uuid, and commit.
- [ ] Task 130.130: Run `300-120-retag-refs.sh --tiers D --apply` for the historical transcripts and sibling files and commit separately.
- [ ] Task 130.140: Confirm `300-110-find-refs.sh --status retag --tiers ABCD` reports zero hits (ACC-002).

#### Phase 140: Remove the ADR Code

- [ ] Task 140.100: Delete `src/biz/dfch/specmgr/adr/` and `src/biz/dfch/specmgr/models/adr/`, remove the `adr` import from `server.py` and its docstring entries, and drop `"biz.dfch.specmgr.adr"` from `pyproject.toml` package-data.
- [ ] Task 140.110: Delete `commands/adr_toc.py` and its registration in `cli.py`, and remove ADR handling from `commands/docs.py`, `commands/schema.py`, `commands/mcp_docs.py` and `commands/lint.py`.
- [ ] Task 140.120: Remove the adr branch and `superseded_by` from `general/tools/set_status.py`, and the adr entries from `_path_safety.py`, `_domains.py` (including the `WholeBodyOrAdrType` alias), `update.py`, `delete.py`, `edit.py`, `set_classification.py`, `validate.py`, `list_references.py`, `get_reference_diagram.py` and `check_translation_drift.py`/`list_languages.py`.
- [ ] Task 140.130: Remove the `ADR` tag from the reference vocabulary (`_references.py`) and the diagram palette (`general/models/reference_graph.py`, `general_reference_graph.md`), and regenerate the reference-graph golden fixtures.
- [ ] Task 140.140: Remove the adr `DomainConfig` and registry entries (`general/resources/config.py`, `models/config_info.py`, `_envregistry.py` `SPECMGR_ADR_DIR`, `server.json`, `_paths.py`) and regenerate the config golden fixture.
- [ ] Task 140.150: Change the `sysrs` `## Decisions` pattern from `^(DEC|ADR)` to DEC only and update the sysrs prompts, instructions and example.
- [ ] Task 140.160: Update the agent prompts, skills and commands that name ADR (`.opencode/agent/phase-implementer.md`, `phase-orchestrator.md`, `command/repair.md`, the create/update prompts of the other domains) and the DEC prompts and examples that compare themselves with ADR.
- [ ] Task 140.170: Delete `tests/adr/` and `tests/models/adr/`, update the cross-cutting tests (`tests/general/tools/`, `tests/general/resources/`, `tests/general/models/`, `tests/commands/`, `tests/models/md/`, `tests/fixtures/`) and add the registration regression test of ACC-011.
- [ ] Task 140.180: Remove the `specmgr-adr-toc` hook from `.pre-commit-config.yaml` and the `docs/adr/README.md` step from `.github/workflows/ci.yml`, and fix the comments there that still name `AdrBody` and `create_adr`.
- [ ] Task 140.190: Run `400-110-find-adr-code-refs.sh` after each task above and finish with `--gate` exiting 0 (ACC-005), then re-run vulture and update `whitelist.py`.

#### Phase 150: Archive, Documents and Generated Docs

- [ ] Task 150.100: Move `docs/adr/*.md` and `docs/adr/README.md` to `docs/archive/adr/` with `git mv`, add a README there marking them superseded by their DEC counterparts, and run `200-120-verify-converted.sh --adr-dir docs/archive/adr`.
- [ ] Task 150.110: Update `README.md`, `AGENTS.md` (the adr domain bullet, the models-location exception paragraph, the generic-tool descriptions, the `.specmgr` guidance that names ADRs) and `CHANGELOG.md` (the breaking removal under `[Unreleased]`).
- [ ] Task 150.120: Decide and apply the fate of `docs/req/req-678319da-...` (ADR document management), the `sysrs` document's ADR references, and the SOP (archive it or keep it as migration history).
- [ ] Task 150.130: Regenerate `docs/GENERATED.md`, `docs/MCP.md`, `docs/api/*` and the schema JSON copies with `specmgr docs`, `specmgr mcp-docs` and `specmgr schema`, and confirm no `adr` entries remain (ACC-008).

#### Phase 160: Final Validation

- [ ] Task 160.100: Run the full local quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src --cov-report=`) and `specmgr lint --all`.
- [ ] Task 160.110: Review `README.md`, `AGENTS.md` and `CHANGELOG.md` end to end for any remaining ADR-as-artifact-type language.
- [ ] Task 160.120: Remove the throw-away scripts and the manifest from the feature folder once the pull request is approved, keeping the manifest's content in the final pull request description, and close issue #46.

## Progress

### Current Status

**As of 2026-11-01**: The plan is rewritten against the current repository. Preparation is done except the freeze announcement and the pull request: the 46 ADRs are surveyed and frozen in `adr-manifest.json` (26 convert and parse today, 20 wait for feat-247, none needs judgment), the SOP is revised, and the scripts are written and pilot-tested in a scratch directory. No DEC has been committed and no code has been removed.

**Handover**: the next step is a plan refinement (feat-refiner) of this plan and of `feat-247-dec-outcome-blocks` before any implementation starts. Open points for the refiner: the 4 ADRs naming several issues (`078bf395`, `750842b2`, `80305c52`, `92cc4ce8`; the first-mentioned issue is used for `## Source`), the fate of `docs/req/req-678319da-...`, the `sysrs` document and the SOP after the migration (Task 150.120), the retag's effect on tier B test fixtures, and the order relative to the sharded layout of issue #245 (ignored for now). The manifest dates are frozen: do not run `100-110-survey-adrs.sh --refresh-dates`. The scripts were pilot-tested only in a scratch `docs/dec/`, which was removed again; `300-120-retag-refs.sh` and `400-110-find-adr-code-refs.sh` were run as dry runs only.

### Blockers

- The 20 ADRs with a multi-block Decision Outcome cannot be converted before feat-247-dec-outcome-blocks (GitHub issue #247) is released; Phase 110 does not depend on it.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 06:34:30.000Z - Plan rewritten, scripts and manifest added

Rewrote the plan after review found the 2026-09-04 plan out of date (30 ADRs instead of 46, a Phase 0 for the already shipped issue #29, a conversion via `create_dec` plus rename, removed tools, stale hook line numbers, a missing inventory of `_envregistry`, `server.json`, `.opencode/`, the `sysrs` pattern, the reference vocabulary and palette, and old task numbering). Merged `dev` into the branch, revised the SOP, wrote the scripts and froze the manifest, and opened issue #247 for the parser prerequisite.

#### 2026-09-04 21:40:00.000Z - Plan review: added blocking Phase 0 for issue #29 and other gaps

Superseded by the 2026-11-01 rewrite: issue #29 shipped as `feat-29-dec-source-roles`, which added body sections instead of frontmatter fields, so Phase 0 was dropped.

#### 2026-09-04 00:00:00.000Z - Feature planned

Drafted the phased removal plan for the ADR artifact type (convert to DEC preserving UUIDs, update all references, remove ADR tooling/tests/CI hooks, archive historical files) based on GitHub issue #46 and a full codebase inventory of ADR's footprint.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 06:34:30.000Z - Conversion, timestamps, supersession and Source decisions

Decided with the maintainer: (1) supersession is recorded on the superseding DEC only, the superseded DEC just gets `status: superseded`; (2) DEC `created`/`updated` equal the ADR file's first/last git commit dates, frozen in a manifest, not the ADR `date` and not the conversion time; (3) the migration `## Updates` entry is dated equal to `updated`; (4) the multi-block Decision Outcome is solved by relaxing the DEC parser in its own feature (issue #247) instead of rewriting decision text; (5) the DEC file name is `<uuid>-<slug>.md`, the ADR file name unchanged; (6) `## Source` is the first-mentioned GitHub issue when the Context names one, otherwise `dfch`; (7) Accountable is `dfch` for every ADR and `user decision` maps to `dfch` in Responsible; (8) conversion and reference work is done by throw-away scripts in `bin/`, not by a shipped command; (9) the sharded layout of issue #245 is ignored for now; (10) from the start of the rollout no new ADR is created.

#### 2026-09-04 21:20:00.000Z - Scoping decisions for the ADR removal

Four scoping decisions were resolved during the first design session and are kept: (1) each converted DEC reuses its source ADR's UUID; (2) reference updates cover the entire repository, including historical `.specmgr/` transcripts; (3) the original ADR files are archived rather than hard-deleted; (4) the whole removal is delivered under the single GitHub issue #46, now as two parts (rollout, removal) of one feature, with the parser prerequisite split out as issue #247.

### Related PRs / Commits

- [Issue #46](https://github.com/dfch/biz.dfch.SpecMgr/issues/46): tracking issue for this feature.
- [Issue #247](https://github.com/dfch/biz.dfch.SpecMgr/issues/247): relax the DEC Decision Outcome to accept multiple blocks, a prerequisite.
- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29): DEC source/roles sections, shipped as `feat-29-dec-source-roles`.
- [Issue #99](https://github.com/dfch/biz.dfch.SpecMgr/issues/99): soft-wrapped list items, the reason for the single-line list items here.
