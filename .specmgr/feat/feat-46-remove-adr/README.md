---
classification: null
created: '2026-09-04T21:02:26.742+02:00'
id: feat-46-remove-adr
status: progress
type: feat
updated: '2026-11-04T10:23:39.000+01:00'
version: 1.0.0
---

# Feature: Remove the ADR Artifact Type in Favor of DEC

## Plan

### Overview

The repository maintains two overlapping decision-record artifact types: `ADR` (the original domain, a bespoke module under `adr/` and `models/adr/`) and `DEC` (the later, more general decision type built on the generic `models/md` parser). GitHub issue #46 asks to remove ADR entirely: every ADR in this repository is converted to a DEC that reuses the ADR's UUID (and its file name), every reference is retargeted from `ADR <uuid>` to `DEC <uuid>`, and the ADR code, tests, hooks and prose are removed. Only this repository's own ADRs are in scope. This plan replaces the earlier 2026-09-04 plan, which predated the shipped DEC sections (GitHub issue #29), the generic `validate` tool, the `specmgr lint` gate and the script-assisted conversion; it keeps that plan's scoping decisions. The work is split into a data rollout (convert, verify, retarget) and a code removal, because the removal must not start before every ADR has a verified DEC. The preparation (this plan, the frozen manifest, the throw-away scripts, the revised SOP and the AGENTS.md freeze announcement) is committed to the feat-46-remove-adr branch and lands on dev via a preparation pull request; the implementation then runs in a fresh git worktree created from the branch, rollout + retag as one pull request and removal + archive as a second (the 2026-11-04 delivery decision).

### Requirements

- REQ-001: Every ADR in `docs/adr/` (46 at the time of the 2026-11-01 survey, listed in the committed manifest `adr-manifest.json`) MUST be converted to a DEC at `docs/dec/<uuid>-<slug>.md` that reuses the ADR's `id` and file name, following the "Convert an ADR to a DEC" SOP (SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a).
- REQ-002: Each DEC's frontmatter `created`/`updated` MUST equal the first/last git commit dates of the ADR file as frozen in the manifest, and no tool may bump them during the migration.
- REQ-003: Supersession MUST be recorded on the superseding DEC only (`## Related Artifacts` → `### Decisions`); the superseded DEC gets `status: superseded` and no outbound reference.
- REQ-004: Every citation of a migrated ADR id (`ADR <full uuid>`, `ADR <8-hex prefix>`, `docs/adr/<file>` paths) in tracked files outside the ADR sources and the generated files MUST be retargeted to the DEC equivalent, using the manifest as the only source of ids; ids that are not migrated ADRs MUST stay untouched.
- REQ-005: The `adr` domain package (`src/biz/dfch/specmgr/adr/`) and its schema package (`src/biz/dfch/specmgr/models/adr/`) MUST be removed together with their tests, the `pyproject.toml` package-data entry, the `adr-toc` command, and the `SPECMGR_ADR_DIR` registry entry and `server.json` manifest entry.
- REQ-006: ADR special-casing MUST be removed from the cross-cutting code: the generic tools (`set_status`'s `superseded_by`/adr branch, `_path_safety`, `update`/`delete`/`edit`/`set_classification`/`validate` dispatch), the domain registry (`_domains.py` and the `WholeBodyOrAdrType` alias), the reference tag vocabulary and diagram palette, `commands/lint.py`, `commands/docs.py`, `commands/schema.py`, `commands/mcp_docs.py`, `commands/diagram.py`'s help text, `cli.py`, `server.py`, `general/resources/config.py`, `models/config_info.py`, `sysrs`' `^(DEC|ADR)` pattern, and the agent prompts that name ADR.
- REQ-007: The `specmgr-adr-toc` pre-commit hook and the CI step checking `docs/adr/README.md` MUST be removed.
- REQ-008: The original ADR files and the generated ADR table of contents MUST be archived (not deleted) under `docs/archive/adr/` once every DEC is verified.
- REQ-009: `README.md`, `AGENTS.md` and `CHANGELOG.md` MUST be updated to drop ADR-as-artifact-type language, with `ADR <uuid>` citations retargeted per REQ-004 instead of deleted, and `CHANGELOG.md` MUST record the breaking removal.
- REQ-010: Generated documentation (`docs/GENERATED.md`, `docs/MCP.md`, `docs/api/*`, the schema JSON copies, and the packaged `general/data/general_harness_bundle.json`) MUST be regenerated and contain no `adr` tool, resource, prompt or domain entry.
- REQ-011: The full local quality gate (ruff format and check, vulture, `pytest -n auto`, `specmgr lint --all`) MUST pass after the removal.
- REQ-012: No new ADR MAY be created from the start of the rollout (freeze); new decisions are DEC documents; the checkable trace is the freeze sentence in AGENTS.md's `adr` bullet, committed before any commit touches `docs/adr/`.

### Acceptance Criteria

- [ ] ACC-001: `200-120-verify-converted.sh --require-all` reports every ADR of the manifest converted and zero failing documents, and `list_dec` shows each migrated id as a healthy row with `error_count` 0 (REQ-001, REQ-002, REQ-003).
- [ ] ACC-002: `300-110-find-refs.sh --status retag --tiers ABCD` reports zero hits, and `300-110-find-refs.sh --status ambiguous` reports zero hits (REQ-004).
- [ ] ACC-003: `list_references` on a retargeted live document resolves the DEC for a migrated id with non-null `title` and `path` (REQ-004).
- [ ] ACC-004: `src/biz/dfch/specmgr/adr/` and `src/biz/dfch/specmgr/models/adr/` do not exist, `pyproject.toml` has no `biz.dfch.specmgr.adr` package-data entry, `tests/adr/` and `tests/models/adr/` do not exist, and `specmgr adr-toc` is not a command (REQ-005).
- [ ] ACC-005: `400-110-find-adr-code-refs.sh --gate` exits 0, run at the end of Phase 160 after the Phase 150 prose changes have landed (REQ-005, REQ-006, REQ-007).
- [ ] ACC-006: `.pre-commit-config.yaml` and `.github/workflows/ci.yml` contain no `adr-toc` hook/step and no `docs/adr/README.md` check; `server.json` and `_envregistry.py` contain no `SPECMGR_ADR_DIR` (REQ-005, REQ-007).
- [ ] ACC-007: `docs/adr/` does not exist and the 46 ADR files plus the TOC exist under `docs/archive/adr/` with a README marking them superseded by their DEC counterparts (REQ-008).
- [ ] ACC-008: `docs/GENERATED.md` and `docs/MCP.md`, freshly regenerated, contain zero `adr` entries and `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` leave no drift (REQ-010).
- [ ] ACC-009: `README.md` and `AGENTS.md` name no `adr` artifact type, domain bullet, models-location exception or `SPECMGR_ADR_DIR`, and `CHANGELOG.md` `[Unreleased]` records the breaking removal (REQ-009).
- [ ] ACC-010: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto --cov=src --cov-report=` and `specmgr lint --all` all pass (REQ-011).
- [ ] ACC-011: `tests/` contains a regression test asserting that no `adr` tool, resource or prompt is registered on the MCP server (REQ-005).

### Scope

#### Included

- Converting every ADR to a DEC with the script-assisted procedure of the SOP, including the multi-block ADRs (the feat-247 prerequisite is merged to dev; Phase 120 verifies the re-survey).
- The throw-away scripts in `bin/` and the committed manifest `adr-manifest.json`.
- Retargeting all citations of migrated ids across `src/`, `tests/`, `docs/`, `.specmgr/` (including historical transcripts), `README.md`, `AGENTS.md`, `CHANGELOG.md` and `.opencode/`.
- Removing the `adr` packages, tests, commands, registry/manifest entries, hook and CI step, and every ADR special case in the cross-cutting code and agent prompts.
- Archiving the ADR sources, regenerating the generated documentation, and updating the prose documents.
- Deciding the fate of `docs/req/req-678319da-...` (the ADR document management requirement), the `sysrs` document that cites ADRs, and the SOP after the migration.

#### Explicitly Out Of Scope

- Other repositories' ADRs (issue #46: "We do not care about other repos with ADRs").
- The DEC parser relaxation for multi-block Decision Outcome (GitHub issue #247, feature feat-247-dec-outcome-blocks), a prerequisite delivered separately and merged to dev (`68ed2d1`).
- Rewriting decision content beyond the mechanical changes of the SOP.
- A reusable conversion command: the scripts are throw-away and removed with the migration.
- The sharded storage layout of GitHub issue #245: the target path `docs/dec/<uuid>-<slug>.md` follows today's flat layout; whichever feature lands second moves the files.
- Fine-grained option tools for DEC (`option_create` and friends); DEC keeps the generic whole-body tools.

### Dependencies

#### Depends On

- FEAT feat-247-dec-outcome-blocks: released — merged to dev via PR #252 (`68ed2d1`); the 20 ADRs it blocked convert cleanly under the merged parser (trial-verified 2026-11-03/2026-11-04, re-verified by the Phase 120.100 re-survey).
- SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a: the conversion procedure (revised for the script-assisted flow, committed to this branch).

#### Blocks

- Nothing. (Once this feature lands on dev, the mutual FEAT reference with feat-247-dec-outcome-blocks forms a harmless 2-node cycle in the reference graph — expected for a dependency pair, not a defect; the SOP dependency line is prose-only because SOP is not a reference-tag vocabulary member.)

### Design Notes

**Scripts, not a command.** The conversion, verification and reference work is done by numbered throw-away scripts in `bin/` (`NNN-MMM-name.sh`, a Python helper `adr_dec_lib.py` shared by them, run with `uv run --frozen --extra mcp python` or a `SPECMGR_PYTHON` override — the `mcp` extra is required by the three trial-conversion scripts (100-110, 200-110, 200-120), whose `parse_error` imports the real `parse_dec` (the `dec` package's eager `__init__` chain reaches `server.py`, the third-party `mcp` package) and `200-120`'s embedded `specmgr lint` (needs `cli`, included by `mcp`); the reference-scanning scripts (300-*, 400-*) stay on base dependencies). `100-110-survey-adrs.sh` classifies every ADR through a trial conversion into the real `parse_dec` and, with `--write`, freezes `adr-manifest.json` (git dates, derived Source and RASCI values, supersession links, wrapped token runs). `200-110-convert-adr.sh` is a dry run unless `--write` and never writes a failing or an existing file. `200-120-verify-converted.sh` checks the frontmatter against the manifest, the H1, the migration entry, fidelity (undoing exactly the allowed changes reproduces the ADR body) and supersession, then runs `specmgr lint --type dec`. `300-110-find-refs.sh` and `300-120-retag-refs.sh` find and retarget citations in tiers (G generated, A live artifacts, B src and tests, C prose, D transcripts), dry run by default; only manifest ids are touched, lines saying "Converted from ADR" are kept, and tier G is regenerated, never edited. `400-110-find-adr-code-refs.sh` is the checklist and its final `--gate` (Phase 160.110) closes the removal phase. The scripts follow the sibling LlmOps convention (a header comment, `set -euo pipefail`, an embedded Python heredoc).

**Why a manifest.** The DEC `created`/`updated` are the ADR file's first and last commit dates. Any later commit under `docs/adr/` (the retag, the archive move) changes the last date, so the dates are captured once, before such a commit, and conversion and verification read only the manifest.

**Pilot result (2026-11-01, scratch).** Converting `519d1206` (wrapped token), `bfd76370` (wrapped tokens, issue source), `a156fdf9` (superseded) and `8cf940c5` (clean, default source) into a scratch `docs/dec/` verified clean (fidelity, frontmatter, `specmgr lint`); corrupting one converted file made the verifier fail on the parse, the frontmatter and the fidelity check. The pilot files were removed again. The survey classes: 26 clean, 20 blocked by feat-247, 0 needing judgment. `92cc4ce8` (the superseding DEC) is blocked, so its Related Artifacts bullet was verified on a copy with the outcome collapsed to one block.

**Citation tiers.** The retag covers about 2,000 full-uuid citations, 1,500 short-prefix citations and 580 path citations across about 700 files. Retagging tier B (src and tests) edits test fixtures; tests that assert behaviour for a migrated real uuid must be checked against the full test run, and the reference-graph golden fixtures and the config golden are regenerated only where the removal changes them (ADR domain entries), not by the retag. After the removal the `ADR` tag no longer resolves in `list_references`, so remaining `ADR <uuid>` citations in transcripts are retargeted too (tier D, a separate commit).

**Order matters.** Convert all ADRs and verify with `--require-all` before the retag (otherwise a retargeted `DEC <uuid>` does not resolve); retag before the removal (otherwise the removal gate sees thousands of citations); archive the ADR files only after the removal, and run the verifier against the archive with `--adr-dir`.

**The generic `set_status` `superseded_by` parameter** exists only for ADR's `superseded by X` status; it is removed with the adr branch.

**Delivery (2026-11-04).** The preparation — this plan, the frozen manifest, the scripts, the revised SOP, the AGENTS.md freeze announcement and the feat-247 closeout (commit `7e3d63f`) — is committed to the feat-46-remove-adr branch, merged to current origin/dev (which carries the feat-247 prerequisite and the new set domain of feat-173), and lands on dev via a preparation pull request. The implementation runs in a fresh git worktree created from the branch: rollout + retag (Phases 110-130) as one pull request, removal + archive (Phases 140-160) as a second. The pre-rewrite branch state and the former worktree are obsolete.

**Phase 110/120 membership.** After the feat-247 merge, the live survey classifies all 46 ADRs clean, which would empty Phase 120 if the live class were the selection source. The two-phase split is therefore kept by selecting phase membership from the frozen manifest's class field (26 clean / 20 blocked-by-247, the 2026-11-01 survey result); the live re-survey (Tasks 110.100/120.100) is a verification gate, not a selection source, and additionally checks that the on-disk ADR id set still equals the manifest's 46 (a 47th ADR stops the rollout — feat-245-shard-docs plans to create one under docs/adr/).

**400-110 gate rework (2026-11-04).** The gate is a file-prefix exclusion over git-grep output; it now excludes docs/adr/ (sources), docs/archive/ (future archive), docs/api/ (generated), .specmgr/feat/ (all historical feature documents — the Phase 130 retag retargets their `ADR <uuid>` citations, their ADR prose stays, per the gate's stated intent), evals/c4-skills/results/ (committed measurement outputs), CHANGELOG.md (history; the previous `CHANGELOG.md$` alternative was dead code against `path:line:content` output), and the 46 converted-DEC stems read from the manifest (their verbatim body prose legitimately keeps the word ADR; the fidelity gate forbids rewriting it, and a non-manifest docs/dec/ file must still be caught). The final `--gate` runs at 160.110, after the Phase 150 prose changes (AGENTS.md, README.md, the sysrs/req/SOP fates) have landed, not at the end of Phase 140 where it depended on them.

Every list item in this document is written as a single physical line (the soft-wrap rule of GitHub issue #99).

### Related Decisions

- None; record a DEC if the removal surfaces a decision beyond the SOP rules.

### Task List

#### Phase 100: Preparation and Pilot

- [x] Task 100.100: Survey the 46 ADRs through a trial conversion into the real `parse_dec` and freeze `adr-manifest.json` (`100-110-survey-adrs.sh --write`).
- [x] Task 100.110: Revise the SOP (SOP 81d73e92-ed9c-44a8-a475-9256a88cfd6a) for the script-assisted conversion and the decisions recorded below.
- [x] Task 100.120: Write the scripts `100-110`, `200-110`, `200-120`, `300-110`, `300-120`, `400-110` and the shared helper in `bin/`, and verify them with a scratch pilot including a negative test.
- [x] Task 100.130: Announce the freeze (no new ADR) in the AGENTS.md `adr` bullet and commit the manifest, the scripts and the revised SOP before any commit touches `docs/adr/` — done 2026-11-04 as part of the preparation landing on this branch.
- [x] Task 100.140: Land the preparation (plan, SOP, manifest, scripts, freeze announcement) so the implementation can start from a fresh git worktree — done 2026-11-04 by committing the preparation to this branch (supersedes the original preparation-PR approach; the branch lands on dev via its preparation pull request).

#### Phase 110: Rollout A - Convert the Clean ADRs

- [x] Task 110.100: Re-run `100-110-survey-adrs.sh` without `--write` and require the on-disk `docs/adr/` id set to equal the manifest's 46 with no `needs-judgment` row (a 47th ADR, e.g. from the sharded-storage work of GitHub issue #245, stops the rollout: record it, extend the manifest with `--force` keeping the frozen dates, re-verify); then dry-run `200-110-convert-adr.sh --all` and review the candidate text of one ADR of each kind (clean, wrapped tokens, superseded) with `--show`.
- [ ] Task 110.110: Convert the 26 ADRs the frozen manifest classifies `clean` with `200-110-convert-adr.sh --write` for each of those ids, and commit the DEC files.
- [ ] Task 110.120: Run `200-120-verify-converted.sh` and fix any failing document by extending the script rule, never by hand-editing.
- [ ] Task 110.130: Read back one converted DEC of each kind present in this phase (clean, wrapped tokens, superseded — the superseding kind converts in Phase 120) with `get_dec` and confirm `list_dec` shows healthy rows with `error_count` 0 (SOP Gate 2).

#### Phase 120: Rollout B - Convert the Multi-Block ADRs

- [ ] Task 120.100: The feat-247-dec-outcome-blocks prerequisite is merged to dev (`68ed2d1`): re-run `100-110-survey-adrs.sh` without `--write`, re-check the on-disk id set against the manifest's 46, and confirm all 46 ADRs now classify `clean` (trial-verified 2026-11-03/2026-11-04 through the merged parser with the plan's own `convert()`; any other result is a new rule to add to the scripts).
- [ ] Task 120.110: Convert the remaining 20 ADRs the frozen manifest classifies `blocked-by-247` with `200-110-convert-adr.sh --write`, including the superseding `92cc4ce8`, and commit them.
- [ ] Task 120.120: Run `200-120-verify-converted.sh --require-all` (the rollout gate), the supersession gate `list_references(type="dec", id="92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c")` (SOP Gate 3), and read back the superseding `92cc4ce8` with `get_dec`.

#### Phase 130: Retarget the References

- [ ] Task 130.100: Run `300-110-find-refs.sh` and review the `ambiguous`, `foreign` and `manual` rows; resolve every `manual` `docs/adr/` path citation by hand.
- [ ] Task 130.110: Run `300-120-retag-refs.sh --tiers A --apply`, review the diff and commit (live artifacts first).
- [ ] Task 130.120: Run `300-120-retag-refs.sh --tiers BC --apply`, run the test suite, fix tests that assert behaviour for a migrated uuid, and commit.
- [ ] Task 130.130: Run `300-120-retag-refs.sh --tiers D --apply` for the historical transcripts and sibling files and commit separately.
- [ ] Task 130.140: Confirm `300-110-find-refs.sh --status retag --tiers ABCD` reports zero hits (ACC-002).

#### Phase 140: Remove the ADR Code

- [ ] Task 140.100: Delete `src/biz/dfch/specmgr/adr/` and `src/biz/dfch/specmgr/models/adr/`, remove the `adr` import from `server.py` and its docstring entries, drop `"biz.dfch.specmgr.adr"` from `pyproject.toml` package-data, and fix the three unowned importers in the same commit: the ADR re-export block in `src/biz/dfch/specmgr/models/__init__.py`, the ADR leg in `general/tools/_reference_graph.py` (`adr.tools._io`/`_paths` imports, `AdrParseError`, the `ADR` constant, the per-domain maps), and the `ADR` import in `general/tools/_language_guard.py` (which breaks when 140.120 drops the `ADR` entry from `_domains.py`).
- [ ] Task 140.110: Delete `commands/adr_toc.py` and its registration in `cli.py`, and remove ADR handling from `commands/docs.py`, `commands/schema.py`, `commands/mcp_docs.py`, `commands/lint.py` and the 14-domain help text in `commands/diagram.py`.
- [ ] Task 140.120: Remove the adr branch and `superseded_by` from `general/tools/set_status.py`, and the adr entries from `_path_safety.py`, `_domains.py` (including the `WholeBodyOrAdrType` alias), `update.py`, `delete.py`, `edit.py`, `set_classification.py`, `validate.py`, `list_references.py`, `get_reference_diagram.py` and `check_translation_drift.py`/`list_languages.py`.
- [ ] Task 140.130: Remove the `ADR` tag from the reference vocabulary (`_references.py`) and from the 16-entry diagram palette (`general/models/reference_graph.py`, `general_reference_graph.md`), and regenerate the reference-graph golden fixtures, reworking or removing the synthetic ADR-side fixture `tests/fixtures/reference-graphs/wide/adr-a001.md` and the never-cached-ADR-leg test logic in `test__reference_graph.py`, `test_get_reference_diagram*.py` and `tests/plantuml/test_reference_graph_subset.py`.
- [ ] Task 140.140: Remove the adr `DomainConfig` and registry entries (`general/resources/config.py`, `models/config_info.py`, `_envregistry.py` `SPECMGR_ADR_DIR`, `server.json`, `_paths.py`), regenerate the config golden fixture, and move the `README.md` Environment Variables `SPECMGR_ADR_DIR` lines into the same commit (`tests/test_envregistry_coverage.py` pins registry-to-README-to-`server.json` fidelity, so a split commit would fail the suite).
- [ ] Task 140.150: Change the `sysrs` `## Decisions` pattern from `^(DEC|ADR)` to DEC only and update the sysrs prompts, instructions and example.
- [ ] Task 140.160: Update the agent prompts, skills and commands that name ADR (`.opencode/agent/phase-implementer.md`, `phase-orchestrator.md`, `command/repair.md`, the create/update prompts of the other domains) and the DEC prompts and examples that compare themselves with ADR, then regenerate `general/data/general_harness_bundle.json` with `specmgr harness-bundle` (the bundle embeds the `.opencode` files edited here).
- [ ] Task 140.170: Delete `tests/adr/` and `tests/models/adr/`, update the cross-cutting tests (`tests/general/tools/`, `tests/general/resources/`, `tests/general/models/`, `tests/commands/` — including re-anchoring `tests/commands/test_harness_bundle.py`'s hook-ordering assertion, which dies with the `specmgr-adr-toc` hook —, `tests/models/md/`, `tests/fixtures/`), the tests/ root (`tests/test_agent_facing_wording.py`'s `create_adr` description clauses, `tests/test_cli.py`'s adr-toc surface line, `tests/test_schema_surface_registration.py`, `tests/test_envregistry*.py`) and `tests/dec/models/v1/test_adr_outcome_fixtures.py` with its `tests/fixtures/dec-outcome-blocks/adr-*-outcome.md` fixtures (feat-247's ADR-derived regression fixtures: keep as historical evidence with the ADR wording updated, or re-id as synthetic fixtures in the `wide/adr-a001.md` pattern — decide at the task and record it in Decisions Made), and add the registration regression test of ACC-011.
- [ ] Task 140.180: Remove the `specmgr-adr-toc` hook from `.pre-commit-config.yaml` and the `docs/adr/README.md` step from `.github/workflows/ci.yml`, and fix the comments there that still name `AdrBody` and `create_adr`.
- [ ] Task 140.190: Run `400-110-find-adr-code-refs.sh` as a non-gating checklist after each task above (record the residual per-area counts in an Updates entry), then re-run vulture and update `whitelist.py`; the final `--gate` runs at 160.110 (ACC-005), after the Phase 150 prose changes have landed.
- [ ] Task 140.200: Sweep the surviving ADR prose the 140.190 checklist surfaces outside the deleted packages: the `general/tools/__init__.py` module docstring; the stale adr-structurally-excluded (issue #46) wording in `find_related.py`, `find_similar_text.py` and `_similarity_corpus.py`; the dead `adr.tools._paths` references in `general/tools/_doc_paths.py`; the dead `models/adr/v1/summary` `AdrSummary` reference in `general/models/summary.py`; the ADR mentions in `general/models/translation_drift.py`, `invalid_status_result.py`, `similarity_hit.py`, `update_result.py`, `reference.py` and `heading_table.py`; the ADR docstrings in `models/md/common_sections.py` (the slated-for-removal (issue #46) note becomes past tense), `frontmatter.py`, `_errors.py`, `_timestamps.py` and `_frontmatter_parse.py`; the ADR mentions in the uc rulebook `uc/data/uc_plantuml.md`; `general/prompts/repair.py`, `translate_artifact.py` and `compact_history.py` and `general/data/general_i18n.md`, `general_repair_instructions.md` and `general_translate_artifact_instructions.md`; the ADR example reference shapes in `feat/data/feat_template.md`, `feat_example.md` and `feat_create_instructions.md` (switch to `DEC <uuid>`); the ADR comparison wording in `dec/data/dec_create_instructions.md`, `dec_update_instructions.md` and the `dec/models/v1/body.py` docstrings (so both `dec_schema.json` copies regenerate clean); the per-domain tool docstrings' e.g.-adr enumeration prose across every domain including the new set domain of feat-173; the MADR attribution block and the stale `doc/adr-tool-plan.md` pointer in `NOTICE` (drop the attribution for the removed code, or reword for DEC's MADR-style headings if part of the block covers other kept third-party content — record the choice in Decisions Made); the code samples in `.specmgr/conventions.md`; and the AGENTS.md section citation in `evals/c4-skills/README.md`, then regenerate the affected schema JSON copies with `specmgr schema`.

#### Phase 150: Archive, Documents and Generated Docs

- [ ] Task 150.100: Move `docs/adr/*.md` and `docs/adr/README.md` to `docs/archive/adr/` with `git mv`, add a README there marking them superseded by their DEC counterparts, and run `200-120-verify-converted.sh --adr-dir docs/archive/adr`.
- [ ] Task 150.110: Update `README.md`, `AGENTS.md` (the adr domain bullet — including removing the freeze sentence added in 100.130 —, the models-location exception paragraph, the generic-tool descriptions, the `.specmgr` guidance that names ADRs) and `CHANGELOG.md` (the breaking removal under `[Unreleased]`).
- [ ] Task 150.120: Decide and apply the fates: (a) `docs/req/req-678319da-...` (ADR Document Management) — set it to `rejected` via the generic `set_status` tool and amend its Description to note the removal per issue #46 (its stale 28-existing-ADRs count and present-tense tool surface are false after the removal, and the sysrs document references it); (b) the sysrs document (`docs/sysrs/sysrs-8d752304-...`) — a whole-document ADR-prose pass, not just its eight retagged bullets (the fourteen-domains enumeration, the adr update_section/option-tools example, the set_status fourteenth-domain note, the CLI adr-toc mention, the definitions entries, the already-accepted-ADRs count and the sequence-diagram CLI label); (c) the conversion SOP 81d73e92 — archive it to `docs/archive/sop/` (keeping it in `docs/sop/` is incompatible with the 400-110 gate, which runs at 160.110 after this task).
- [ ] Task 150.130: Regenerate `docs/GENERATED.md`, `docs/MCP.md`, `docs/api/*` and the schema JSON copies with `specmgr docs`, `specmgr mcp-docs` and `specmgr schema`, and `general/data/general_harness_bundle.json` with `specmgr harness-bundle`, and confirm no `adr` entries remain (ACC-008).

#### Phase 160: Final Validation

- [ ] Task 160.100: Run the full local quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto --cov=src --cov-report=`) and `specmgr lint --all`.
- [ ] Task 160.110: Run the final `400-110-find-adr-code-refs.sh --gate` (moved from 140.190; the Phase 150 prose has landed by now) and require exit 0 (ACC-005), then review `README.md`, `AGENTS.md` and `CHANGELOG.md` end to end for any remaining ADR-as-artifact-type language.
- [ ] Task 160.120: Remove the throw-away scripts and the manifest from the feature folder once the pull request is approved, keeping the manifest's content in the final pull request description, and close issue #46.

## Progress

### Current Status

**As of 2026-11-04**: The plan is updated for execution and the preparation is committed to this branch, which is merged to current origin/dev (carrying the feat-247 prerequisite, `68ed2d1`, and the new set domain of feat-173, PR #254). The feat-46 refinement pass (feat-refiner) verified the merged prerequisite end-to-end — a trial conversion of all 46 ADRs through the merged parser with the plan's own `convert()` yields 46/46 clean, 0 needs-judgment — and its findings are applied to this plan and the scripts: the 400-110 gate is reworked (manifest-aware converted-DEC exclusion, the dead CHANGELOG anchor fixed) and its final run moved to Phase 160, the Phase 140 inventory gains the three unowned importers, the dev-new test couplings and the new 140.200 prose-sweep task, the Phase 150 fates are fixed (sysrs whole-document pass, `req-678319da` rejected, SOP archived), and the phase membership of the two-phase rollout is sourced from the frozen manifest's class field. Phase 100 is complete including the AGENTS.md freeze announcement and the feat-247 closeout (commit `7e3d63f`, GitHub issue #247 closed). Phase 110 has started: Task 110.100 is complete (re-survey `46 ADRs: {'clean': 46}` with the on-disk id set equal to the manifest's 46, the `200-110 --all` dry run 46/46 clean, one `--show` candidate reviewed per kind), and the three trial-conversion scripts' interpreter default was fixed to `uv run --frozen --extra mcp python` (a fresh worktree `.venv` is base-only, and the `parse_dec` import chain needs the `mcp` extra). No DEC has been committed and no code has been removed.

**Handover**: the pre-rewrite branch state and the former worktree are obsolete. Create a fresh git worktree from this branch and start at Task 110.100: re-run the survey without `--write`, require the on-disk ADR id set to equal the manifest's 46, then convert the 26 manifest-clean ADRs (Phase 110) and the 20 manifest-blocked-by-247 ADRs (Phase 120, after its re-survey confirms all 46 clean). The manifest dates are frozen: never run `100-110-survey-adrs.sh --refresh-dates`. Rollout + retag (Phases 110-130) ships as one pull request, removal + archive (Phases 140-160) as a second, after the preparation pull request (this branch state) is merged.

### Blockers

- None. (The feat-247 prerequisite is merged to dev, `68ed2d1`; GitHub issue #247 closed 2026-11-04.)

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-04 09:23:39.000Z - Task 110.100 done: re-survey 46/46 clean; script interpreter default fixed

- Fixed a fresh-worktree failure of the three trial-conversion scripts (`100-110-survey-adrs.sh`, `200-110-convert-adr.sh`, `200-120-verify-converted.sh`): their `SPECMGR_PYTHON` default (`uv run --frozen python`) syncs a fresh worktree `.venv` to base dependencies only, but `adr_dec_lib.parse_error` imports the real `parse_dec`, whose `dec` package `__init__` chain reaches `server.py` and the third-party `mcp` package — `ModuleNotFoundError: No module named 'mcp'` (the library's documented extras split). The default is now `uv run --frozen --extra mcp python` (also covers `200-120`'s embedded `specmgr lint`, which needs `cli`, included by `mcp`); the `SPECMGR_PYTHON` override is unchanged, and the reference-scanning scripts (300-*, 400-*) keep the base-only default by design.
- Task 110.100 verification (all read-only, no `--write`): the re-survey reports `46 ADRs: {'clean': 46}` — no `needs-judgment` and no `blocked-by-247` under the merged feat-247 parser, confirming the handover claim — and the on-disk `docs/adr/` id set equals the manifest's 46 (nothing missing, nothing extra, no 47th ADR).
- `200-110-convert-adr.sh --all` dry run: 46/46 `clean`, exit 0; candidate text reviewed with `--show` for one ADR of each kind — `519d1206` (wrapped token run `validate\_<d>` now a code span, the `## Pros and Cons` heading rename, Responsible `OpenCode agent` + `dfch` from the `user decision` mapping), `a156fdf9` (superseded: `status: superseded`, no outbound reference, no Related Artifacts on the superseded side), `8cf940c5` (clean with default Source/Responsible `dfch`).
- Frontmatter `updated` bumped; Task 110.100 marked complete.

#### 2026-11-04 05:14:00.000Z - Plan updated for execution; preparation committed to the branch

- Merged origin/dev into the branch (commit `63eb0f4`): the feat-247 prerequisite (`68ed2d1`) and the new set domain (feat-173, PR #254) are now in the tree; the preparation files (this plan, the manifest, the scripts, the SOP) were merge-untouched, and the branch's former state is superseded.
- Ran the feat-refiner pass over the plan: empirical trial conversion of all 46 ADRs through the merged `parse_dec` with the plan's own `convert()` = 46/46 clean, 0 needs-judgment (including `7a626b12`'s wrapped `<jar>`/`<args>` multi-block outcome, `bfd76370`'s wrapped `<domain>` tokens and `92cc4ce8`'s superseder bullet); the gate simulation showed the `400-110 --gate` unreachable as written (the converted DECs' own verbatim prose, the historical `.specmgr/feat` documents, NOTICE and the evals results all sit outside its EXCLUDE, and the prose it depends on lands in Phase 150).
- Applied the findings to the plan and the scripts: E1/D2/I2 the 400-110 gate rework (file-prefix EXCLUDE over git-grep output, manifest-aware converted-DEC stems, the dead `CHANGELOG.md$` anchor fixed, final `--gate` moved to 160.110); E2 the three unowned importers (`models/__init__.py`, `general/tools/_reference_graph.py`, `general/tools/_language_guard.py`) added to 140.100; E3 the `tests/commands/test_harness_bundle.py` hook-ordering re-anchor named in 140.170; E4 the README Environment-Variables lines moved into the 140.140 commit; G1/I3 the new 140.200 prose-sweep task (incl. the set-domain docstrings, NOTICE and the `specmgr harness-bundle` regeneration, added to REQ-010); G2 the on-disk-set==manifest guard in 110.100/120.100 (feat-245-shard-docs plans a 47th ADR under docs/adr/); G3 the sysrs whole-document pass; G4 the `req-678319da` fate fixed (rejected + note); G5 the SOP archived to docs/archive/sop/ before the final gate; D1 the stale 26/20 wait-for-release wording updated (the prerequisite is released); D3 the freeze's checkable trace is the AGENTS.md bullet (REQ-012 dropped from ACC-011); D4/D5 the reference-cycle note and the Phase 110/120 read-back kinds recorded; I6 the re-survey expectation recorded as a verified fact; I7 the 200-120 frontmatter check gains `classification: null`.
- Delivery decision (maintainer, 2026-11-04): the preparation is committed to this branch and lands on dev via a preparation pull request (not a direct dev commit — dev is occupied with other tasks); the implementation starts in a fresh git worktree created from the branch, rollout + retag as one pull request and removal + archive as a second; the freeze is announced in the AGENTS.md `adr` bullet (the `create_adr` prompt wording is test-pinned by `tests/test_agent_facing_wording.py` and deleted in Phase 140 anyway).
- feat-247 closeout (separate commit `7e3d63f`): its plan marked done with all nine ACCs met, and GitHub issue #247 closed.
- Frontmatter `status` moved `planning` -> `progress` and `updated` bumped; Tasks 100.130/100.140 marked complete with their re-scoped wording.

#### 2026-11-01 06:34:30.000Z - Plan rewritten, scripts and manifest added

Rewrote the plan after review found the 2026-09-04 plan out of date (30 ADRs instead of 46, a Phase 0 for the already shipped issue #29, a conversion via `create_dec` plus rename, removed tools, stale hook line numbers, a missing inventory of `_envregistry`, `server.json`, `.opencode/`, the `sysrs` pattern, the reference vocabulary and palette, and old task numbering). Merged `dev` into the branch, revised the SOP, wrote the scripts and froze the manifest, and opened issue #247 for the parser prerequisite.

#### 2026-09-04 21:40:00.000Z - Plan review: added blocking Phase 0 for issue #29 and other gaps

Superseded by the 2026-11-01 rewrite: issue #29 shipped as `feat-29-dec-source-roles`, which added body sections instead of frontmatter fields, so Phase 0 was dropped.

#### 2026-09-04 00:00:00.000Z - Feature planned

Drafted the phased removal plan for the ADR artifact type (convert to DEC preserving UUIDs, update all references, remove ADR tooling/tests/CI hooks, archive historical files) based on GitHub issue #46 and a full codebase inventory of ADR's footprint.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-04 05:14:00.000Z - Delivery, rollout-shape and Phase 150 fate decisions

- (1) The preparation lands on dev via a preparation pull request from this branch (not a direct dev commit, because dev is occupied with other tasks); the implementation starts in a fresh git worktree created from the branch; rollout + retag (Phases 110-130) is one pull request and removal + archive (Phases 140-160) a second.
- (2) The two-phase rollout split (26 clean in Phase 110, 20 in Phase 120) is kept although all 46 ADRs now parse clean under the merged feat-247 parser: phase membership is selected from the frozen manifest's class field (the stable 2026-11-01 survey result), the live re-survey is verification only — the split keeps the conversion commits small and reviewable and preserves the permanent task numbering.
- (3) The freeze (REQ-012) is announced in the AGENTS.md `adr` bullet, not the `create_adr` prompt: the prompt's agent-facing description is pinned by `tests/test_agent_facing_wording.py` and is deleted in Phase 140 anyway.
- (4) feat-247-dec-outcome-blocks is closed out as part of this preparation (commit `7e3d63f`, GitHub issue #247 closed): its code is merged (`68ed2d1`), its gate was green, and the merged relaxation is trial-verified 46/46 over the whole ADR corpus.
- (5) The Phase 150 fates are fixed: `docs/req/req-678319da-...` (ADR Document Management) is set to rejected with a Description note citing issue #46 (its stale counts and present-tense tool surface are false after the removal, and the sysrs document references it); the sysrs document gets a whole-document ADR-prose pass, not just its retagged bullets; the conversion SOP is archived to `docs/archive/sop/` (keeping it in `docs/sop/` is incompatible with the 400-110 gate, which runs at 160.110 after 150.120).
- (6) The 400-110 gate is reworked to be manifest-aware (converted-DEC stems excluded, historical `.specmgr/feat` documents excluded, the dead CHANGELOG anchor fixed) and its final `--gate` runs at 160.110, after the Phase 150 prose changes — the E1 rework makes ACC-005 reachable.

#### 2026-11-01 06:34:30.000Z - Conversion, timestamps, supersession and Source decisions

Decided with the maintainer: (1) supersession is recorded on the superseding DEC only, the superseded DEC just gets `status: superseded`; (2) DEC `created`/`updated` equal the ADR file's first/last git commit dates, frozen in a manifest, not the ADR `date` and not the conversion time; (3) the migration `## Updates` entry is dated equal to `updated`; (4) the multi-block Decision Outcome is solved by relaxing the DEC parser in its own feature (issue #247) instead of rewriting decision text; (5) the DEC file name is `<uuid>-<slug>.md`, the ADR file name unchanged; (6) `## Source` is the first-mentioned GitHub issue when the Context names one, otherwise `dfch`; (7) Accountable is `dfch` for every ADR and `user decision` maps to `dfch` in Responsible; (8) conversion and reference work is done by throw-away scripts in `bin/`, not by a shipped command; (9) the sharded layout of issue #245 is ignored for now; (10) from the start of the rollout no new ADR is created.

#### 2026-09-04 21:20:00.000Z - Scoping decisions for the ADR removal

Four scoping decisions were resolved during the first design session and are kept: (1) each converted DEC reuses its source ADR's UUID; (2) reference updates cover the entire repository, including historical `.specmgr/` transcripts; (3) the original ADR files are archived rather than hard-deleted; (4) the whole removal is delivered under the single GitHub issue #46, now as two parts (rollout, removal) of one feature, with the parser prerequisite split out as issue #247.

### Related PRs / Commits

- [Issue #46](https://github.com/dfch/biz.dfch.SpecMgr/issues/46): tracking issue for this feature.
- [Issue #247](https://github.com/dfch/biz.dfch.SpecMgr/issues/247): relax the DEC Decision Outcome to accept multiple blocks, a prerequisite — merged to dev via PR #252 (`68ed2d1`), closed out by commit `7e3d63f`.
- [PR #254](https://github.com/dfch/biz.dfch.SpecMgr/pull/254): the feat-173 set domain into origin/dev — its e.g.-adr enumeration prose is part of the 140.200 sweep.
- [Issue #29](https://github.com/dfch/biz.dfch.SpecMgr/issues/29): DEC source/roles sections, shipped as `feat-29-dec-source-roles`.
- [Issue #99](https://github.com/dfch/biz.dfch.SpecMgr/issues/99): soft-wrapped list items, the reason for the single-line list items here.
