---
classification: null
created: '2026-10-26T07:16:20.020+01:00'
id: feat-218-in-tree-spec-artifact-parseability-gate
status: planning
type: feat
updated: '2026-10-26T07:58:00.000Z'
version: 1.0.0
---

# Feature: In-Tree Spec Artifact Parseability Gate

## Plan

### Overview

This repo keeps its own planning documents as specmgr FEAT artifacts (one README.md per feature folder under .specmgr/feat/) and its requirements, ADRs and other specmgr documents under docs/. Every one of these documents must be parseable: its frontmatter and full body are checked against its schema by the model-level parser of its domain (for example biz.dfch.specmgr.feat.models.v1.parse_feat). Nothing on the commit path performs that full parse. A body-level defect in any in-tree document is therefore invisible by default: list_feat reads only frontmatter+H1 (the dirty stage, by design: ADR 3982712a's time-qualification) and keeps reporting the document healthy, while every full-parse consumer (the get_feat read path, the reference-graph builders, similarity search) either returns a parse failure or silently drops the document. This was demonstrated in the wild by feat-214 itself: its plan document shipped unparseable in three consecutive commits (f578e69 through 6714117) because its Decisions Made section had been authored as dated bullet lines, which the schema's H4 date-entry form rejects, and the defect surfaced only as an indirect symptom (the document missing from every live reference-graph diagram) during the Phase 130 CLI walkthrough.

This feature closes that defect class for every specmgr artifact type with a new CLI command, `specmgr lint`, that runs the model-level full parse over the documents it is given (or over a whole type, or everything) and reports every failure. The command is used at three scopes, chosen so that cost scales with the size of a change and never with the size of the corpus: the pre-commit hook lints every staged artifact, the CI pull-request step lints every artifact changed against the base branch, and a full-corpus sweep (by type or all types) is available on demand through the CLI only, which also makes it usable later in an automated nightly job. A schema change may break unchanged documents; that is an accepted consequence (see Design Notes), because breaking changes are kept to a minimum and the gate is change-scoped by design.

### Requirements

- REQ-001: A new CLI command `specmgr lint` runs the model-level full parse of the document's own domain over each document it is asked to check, and reports every unparseable document (file path + parse error), not just the first.

- REQ-002: The command supports every specmgr artifact type, and its `--type` choices are derived from the global domain list (general.tools._domains.ALL_DOMAINS: adr plus the whole-body domains), never hand-listed, so that a newly registered domain is lintable without editing the command.

- REQ-003: The gate must do full parses; it must not be a list-based or frontmatter+H1-only check, because that is precisely the masking mechanism (the dirty stage) that hid the feat-214 defect.

- REQ-004: The command accepts explicit file paths (the hook and CI mode), `--type T` with no paths (sweep every document of that type), and `--all` (sweep every type). Paths given on the command line are linted regardless of any environment variable.

- REQ-005: For each path, the document type is inferred from the path layout alone (the containing directory is named after the type, as in `docs/req/x.md`, or the path has the shape `feat/{id}/README.md`), independent of every SPECMGR_*_DIR variable; an explicit `--type` overrides inference. A path whose layout matches no type is a usage error, unless `--skip-unrecognized` is given, in which case it is skipped and counted.

- REQ-006: In sweep mode (`--type` or `--all`), directories come from an explicit `--dir` argument (valid with `--type` only) if given, otherwise from the existing per-domain environment variables and defaults (SPECMGR_ADR_DIR, SPECMGR_DOCS_DIR, SPECMGR_FEAT_DIR). No new environment variable is introduced.

- REQ-007: `docs/adr/README.md` is the generated ADR table of contents, not an ADR; the sweep and the path mode both exclude it (the ADR enumeration helper does not).

- REQ-008: Exit codes follow the plantuml-check family: 0 every document parsed, 1 at least one document failed to parse (or the mcp extra is missing, as for the diagram command), 2 usage or resolution error (no paths and no sweep flag, an unreadable or missing path, an unrecognized layout without `--skip-unrecognized`, `--dir` without `--type`, or `--all` that finds zero documents in total, a probable misconfiguration). The failure report ends with a pointer to the repair flow (`/repair {type} {id}`).

- REQ-009: A new local pre-commit hook in .pre-commit-config.yaml runs `specmgr lint --skip-unrecognized` over every staged file matching the in-tree artifact locations (pass_filenames true), placed ahead of the broad pytest hook, and the specmgr-coverage-badge hook still follows pytest directly.

- REQ-010: A new step in the existing CI build job lints every artifact changed on a pull request against its base branch, for pull_request events only, pinned to Python 3.13 like the docs drift steps. The step fetches the base ref and skips cleanly when no artifact changed.

- REQ-011: The command's cost is bounded by the number of documents it is given. The full-corpus sweep is never part of the commit path, the CI test suite or the pull-request step.

- REQ-012: The repo's drift-checked and documented surfaces are updated: docs/GENERATED.md and docs/api/ (regenerated), CHANGELOG.md, README.md's CLI section, and AGENTS.md's CLI and pre-commit paragraphs.

### Acceptance Criteria

- [ ] ACC-001: A temporary document in the feat-214 failure shape (a Decisions Made entry authored as a dated bullet line) makes `specmgr lint <path>` exit 1 with the offending file named and its parse error reported, followed by the repair pointer.

- [ ] ACC-002: A broken ADR (an AdrParseError case) and a broken document of at least one other whole-body domain each make the command exit 1 with the file named; a healthy document of every type exits 0.

- [ ] ACC-003: Running `specmgr lint --all` against the current in-tree corpus exits 0, and `specmgr lint --type feat` sweeps every .specmgr/feat/*/README.md; neither is wired into the hook, CI or the test suite.

- [ ] ACC-004: With SPECMGR_FEAT_DIR and SPECMGR_DOCS_DIR pointed at empty temporary directories, `specmgr lint <in-tree path>` still lints that path, while `specmgr lint --type feat` sweeps the empty directory (proof that paths are env-independent and sweeps honor the variables); `--dir` overrides the variable.

- [ ] ACC-005: `specmgr lint docs/adr/README.md --skip-unrecognized` does not treat the ADR table of contents as an ADR, and an unrecognized path without `--skip-unrecognized` exits 2.

- [ ] ACC-006: In a clean local repo, committing a change to any in-tree artifact (a feature README.md or a document under docs/{type}/) triggers the hook, which lints only the staged artifacts and blocks the commit when any of them fails to parse; a commit touching no artifact is unaffected by the new hook.

- [ ] ACC-007: On a pull request that changes one artifact, the CI step lints exactly the changed artifacts and fails on a broken one; on a pull request that changes none, the step is skipped or passes without running a lint.

- [ ] ACC-008: The `--type` choices equal ALL_DOMAINS (a pinning test fails if the command hand-lists a type), and a test pins that the hook's file pattern covers every type in ALL_DOMAINS.

- [ ] ACC-009: The new tests and every drift check (docs/, docs/GENERATED.md, ruff, vulture) are green on Python 3.11, 3.12 and 3.13.

### Scope

#### Included

- The `specmgr lint` command (src/biz/dfch/specmgr/commands/lint.py, registered in cli.py), thin over the existing domain parsers and the _domains registry.

- Unit tests for the command: path-layout inference, type override, `--skip-unrecognized`, the ADR README exclusion, the feat-214-shape fixture in a temporary directory (the in-tree corpus is never mutated), an ADR error case, exit codes, env-variable versus `--dir` precedence, the zero-documents guard, and the derived-type-list pin.

- The local pre-commit hook in .pre-commit-config.yaml and its documentation in AGENTS.md's pre-commit paragraph.

- The pull-request changed-artifacts step in .github/workflows/ci.yml.

- Documentation and drift updates: docs/GENERATED.md and docs/api/ regenerated, CHANGELOG.md, README.md CLI section, AGENTS.md CLI section.

- Close-out: a local walkthrough of the hook, and a `specmgr lint --all` run over the in-tree corpus recorded under Updates, including this feature's own README.md.

#### Explicitly Out Of Scope

- A scheduled (nightly) workflow running `specmgr lint --all`: the command makes it possible; adding the workflow is a follow-up.

- Relocating the domain registry and path helpers so that CLI commands work in a `[cli]`-only install: `specmgr lint` requires the mcp extra, like `specmgr diagram`. Tracked as issue #238 (needs its own ADR).

- Detecting unchanged documents that a schema change breaks: accepted by design. A schema change does not fail the gate on its own commit; the break surfaces on the next edit of an affected document, or in an on-demand or nightly full sweep. Authors repair through the existing repair flow.

- Checking that a frontmatter id equals its containing folder or file name: the gate checks parseability only.

- A full-corpus sweep in the pytest suite, the hook or the pull-request step (REQ-011).

- Pushes to dev or main: the pull-request step is pull_request-only; local enforcement is the hook.

- Repairing any currently unparseable in-tree document (the corpus is green today; the repair goes through the existing repair flow).

- Changes to the list_feat dirty/clean two-stage design, to any document schema, or to any parse_{d} function.

- Any new ADR for this feature (feature-level decisions only, per the Decisions Made log).

### Dependencies

#### Depends On

- FEAT feat-214-rel-invalid-diag (done, PR #216): the feature whose own plan document demonstrated the defect (three unparseable commits) and which recorded issue #218 as this follow-up.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (list_feat dirty/clean time-qualification): documents the masking mechanism that REQ-003 works around.

### Design Notes

Why full parses, never listing: list_feat's request path resolves each folder from a frontmatter+H1-only dirty-stage parse by design (ADR 3982712a), so a listing-based check would reproduce exactly the masking that hid the feat-214 defect for three commits. The command must call each domain's parser on the file's full text.

Why change-scoped, not corpus-scoped: a serial model-level parse of the 89 feature READMEs measured about 124 s (roughly 1.4 s per document, the largest 6 s) on a 120-core machine, and the corpus only grows. A gate whose cost scales with the corpus is unusable on a commit path, and unworkable for a large project with thousands of documents. The hook (staged files) and the CI step (files changed against the base) cost in proportion to the change; the full sweep is an explicit CLI action. The earlier plan for this feature (a pytest sweep plus a hook running the whole sweep, believed to take seconds) was dropped for this reason.

Accepted limitation: because the gate checks only touched documents, a schema or parser change under src/ can leave untouched documents unparseable without failing any gate. This is accepted: breaking schema changes are kept to a minimum, and `specmgr lint --all` (manually or nightly later) finds any that slip through.

Type resolution: path mode infers the type from the path layout alone (the containing directory's name is a member of ALL_DOMAINS, or the path is feat/{id}/README.md), never from the SPECMGR_*_DIR variables, so the hook and CI behave identically on every machine and fixture-pointing test environments cannot divert them. `--type` is the fallback for nonstandard layouts. Sweep mode is where the environment variables apply, via each domain's registered base-dir resolver (WholeBodyDomain.base_dir and iter_paths, plus the ADR equivalents), with `--dir` as the explicit override.

ADR: parse_adr is a pure text parser, so ADR needs one adapter in the command that also catches AdrParseError (a ValueError subclass), the same also_catch pattern validate_adr uses. The whole-body domains raise AssertionError, pydantic.ValidationError or yaml.YAMLError; the command catches these and AdrParseError per file, plus decode errors, so one bad file cannot abort the aggregate report, and reads files as UTF-8. iter_adr_paths yields every *.md in docs/adr including the generated README.md table of contents, so the command filters it out (REQ-007).

Parser, not tool: the command calls the model-level parsers (base library, pydantic only), not the MCP tools, whose wrap_tool_errors context and non-raising ValidateResult shapes a gate does not want; the errors already carry the feat-27 actionable field-path, line and fix-hint shape.

Extra requirement: the registry (general.tools._domains) is imported through packages that eagerly import the mcp extra, so the command imports it lazily and exits 1 with a clear message when the extra is missing, mirroring `specmgr diagram`. Removing that requirement is the follow-up tracked as issue #238.

The hook: id specmgr-lint, entry `uv run --frozen specmgr lint --skip-unrecognized`, pass_filenames true, files limited to the in-tree artifact locations (.specmgr/feat/{id}/README.md and docs/{dir}/*.md; the lint command's own type list decides which of those are artifacts, so the pattern needs no per-type list). It is placed ahead of pytest, and specmgr-coverage-badge stays directly after pytest. It parses the working-tree file contents, not the git index, so a partially staged file is checked as it exists on disk; this is accepted and documented.

The CI step: pull_request events only, in the existing build job, on Python 3.13 only (like the docs drift steps). It needs the base ref (checkout with fetch-depth 0, or an explicit fetch of the base branch), lists changed files with git diff --name-only --diff-filter=ACMR against the merge base, keeps the .md files under .specmgr/ and docs/, and passes them to `specmgr lint --skip-unrecognized`; with an empty list it does nothing. Unlike the earlier plan, this changes the workflow.

### Related Decisions

- FEAT feat-214-rel-invalid-diag (done) + PR #216: the follow-up whose own plan demonstrated the defect and which recorded issue #218.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44: list_feat dirty/clean time-qualification, the masking mechanism the full-parse requirement works around.

- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI", which grounds the hook half of the gate.

- AGENTS.md, "Still genuinely missing / not yet done": the standing note that no validate-equivalent check runs over the repo's own documents via pre-commit or CI. This feature closes it for every artifact type, at change scope.

- Issue #238: decouple the pure path and parse logic from the eager tools packages so registry-backed CLI commands work without the mcp extra (follow-up, needs its own ADR).

### Task List

#### Phase 100: Lint Command

- [ ] Task 100.100: Before coding, confirm how `specmgr diagram` handles a missing mcp extra (the module-level imports in commands/diagram.py suggest a guard exists somewhere) and follow the same pattern for `lint`; record the finding under Updates.

- [ ] Task 100.110: Implement commands/lint.py and register it in cli.py: arguments PATHS, options `--type` (choices derived from ALL_DOMAINS), `--all`, `--dir`, `--skip-unrecognized`; model-level parse per document with a per-domain adapter (whole-body domains via the registry's parse_text, ADR via parse_adr with AdrParseError also caught); catch AssertionError, ValidationError, YAMLError, AdrParseError and decode errors per file; read UTF-8.

- [ ] Task 100.120: Implement path-layout type inference (containing directory in ALL_DOMAINS, or feat/{id}/README.md), the `--type` override, the unrecognized-path handling, the docs/adr/README.md exclusion, and the sweep mode with env-var and `--dir` directory resolution.

- [ ] Task 100.130: Implement reporting and exit codes: every failing (path, error) pair, a summary count (linted, failed, skipped), the repair pointer, exit 0/1/2 per REQ-008, and the zero-documents guard for `--all`.

#### Phase 110: Tests

- [ ] Task 110.100: Unit tests for inference, `--type` override, `--skip-unrecognized`, the ADR README exclusion and usage errors (exit 2), using temporary directories only.

- [ ] Task 110.110: Negative pins: the feat-214-shape fixture (a valid document with a dated-bullet Decisions Made section, built from the packaged feat template) asserting the file name and a recognizable error fragment; an ADR error case; one other whole-body domain; a healthy document of every type exits 0.

- [ ] Task 110.120: Environment tests: with SPECMGR_FEAT_DIR and SPECMGR_DOCS_DIR patched to empty temporary directories, path mode is unaffected, sweep mode honors the variables, and `--dir` overrides; `--all` with zero documents exits 2.

- [ ] Task 110.130: Drift pins: `--type` choices equal ALL_DOMAINS and the command does not hand-list types; the hook's file pattern covers every ALL_DOMAINS type.

#### Phase 120: Pre-commit Hook

- [ ] Task 120.100: Add the specmgr-lint local hook to .pre-commit-config.yaml (pass_filenames true, in-tree artifact file pattern, entry `uv run --frozen specmgr lint --skip-unrecognized`, placed ahead of pytest with specmgr-coverage-badge still directly after pytest) and document it in AGENTS.md's pre-commit paragraph, including the working-tree-versus-index note.

- [ ] Task 120.110: Local walkthrough: (a) a healthy artifact change commits with the hook linting only the staged files; (b) a feat-214-shape defect introduced in a scratch feature README blocks the commit with the file and error reported; (c) revert; (d) a commit touching no artifact does not trigger the hook. Record the outcome under Updates.

#### Phase 130: CI Step

- [ ] Task 130.100: Add the pull_request-only changed-artifacts step to the build job in .github/workflows/ci.yml (Python 3.13 only; base ref fetched; git diff --name-only --diff-filter=ACMR against the merge base; filter to .md under .specmgr/ and docs/; skip cleanly when none), following the workflow's existing pinned-action conventions.

- [ ] Task 130.110: Verify on the feature's own pull request: the step lints exactly the changed artifacts (ACC-007), and a scratch PR commit with a broken artifact fails it, then is reverted.

#### Phase 140: Documentation and Drift

- [ ] Task 140.100: Regenerate docs/GENERATED.md and docs/api/ (specmgr docs), confirm docs/MCP.md and the schema files are unchanged, and add the CHANGELOG.md [Unreleased] entry.

- [ ] Task 140.110: Update README.md's CLI section and AGENTS.md's CLI section for `specmgr lint` (usage, the three scopes, exit codes, the mcp extra requirement and issue #238, the accepted schema-change limitation).

#### Phase 150: Close-out

- [ ] Task 150.100: Run `specmgr lint --all` over the in-tree corpus (exit 0, including this feature's own README.md) and record the result, its duration and the document count under Updates; run the full local quality gate (ruff, vulture, pytest, drift checks).

- [ ] Task 150.110: Confirm ACC-001 through ACC-009, mark all tasks done, update Current Status, and set the status to done.

## Progress

### Current Status

**As of 2026-10-26**: Plan revised after refinement. The original design (a pytest full-corpus sweep plus a full-sweep hook) was replaced by a change-scoped gate built on a new `specmgr lint` command for every artifact type, because a measured full sweep took about 124 s. The new design is recorded under Decisions Made; the registry-relocation follow-up is issue #238. Implementation not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26T07:58:00.000Z - Plan revised after refinement

A refinement pass found the plan's "parses in seconds" claim wrong by about 20x (a serial full parse of 89 feature READMEs took about 124 s), plus gaps in the hook scope, the docs drift, the fixture design and the exception handling. The plan was redesigned: a new `specmgr lint` command for every artifact type; the pre-commit hook lints staged artifacts; a pull-request CI step lints changed artifacts; full-corpus sweeps only via the CLI (by type or all). Corpus counts were removed, the docs/GENERATED.md drift item, the ADR README exclusion and the feat-214 reference tag were added. Follow-up issue #238 was created for the mcp-extra decoupling.

#### 2026-10-26T05:42:45.913Z - Created

Feature plan drafted from issue #218: a full-parseability gate over the repo's own in-tree FEAT corpus (.specmgr/feat/*/README.md), enforced by a plain test in the existing suite and by a new pre-commit hook scoped to the in-tree markdown (local enforcement for docs-only commits, which the broad src/tests-scoped pytest hook skips). The defect class was demonstrated in the wild by feat-214's own plan shipping unparseable in three consecutive commits (f578e69 through 6714117). Superseded in design by the 2026-10-26T07:58:00.000Z entry.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26T07:58:00.000Z - Change-scoped gate via a new lint command (supersedes the earlier planning decisions)

Decisions made while revising the plan: (1) Scope: pre-commit validates every staged specmgr artifact, CI validates every artifact changed on a pull request, and the full corpus is checked only through the CLI by type or `--all` (also the later nightly path); a full sweep in the suite or hook was rejected because it cost about 124 s and grows with the corpus. (2) Command name `lint` (not `check`, which collides with the plantuml-check family). (3) All artifact types are covered, including ADR (reusing the pure parse_adr parser with AdrParseError also caught); the `--type` set derives from ALL_DOMAINS. (4) Type inference from the path layout alone (environment-independent), `--type` as the fallback; sweep mode honors the SPECMGR_*_DIR variables, `--dir` overrides. (5) Schema changes may break unchanged documents, which is accepted (breaking changes are kept to a minimum). (6) The command requires the mcp extra like `diagram`; relocating the registry is deferred to issue #238, which will need its own ADR. (7) CI step included in this feature (changes the workflow); the nightly workflow is deferred. (8) Still no ADR for this feature itself. Supersedes the earlier planning decisions (corpus = FEAT only, gate = suite test + hook, no workflow change).

#### 2026-10-26T05:42:45.913Z - Planning decisions (issue #218)

Four planning decisions made while drafting this feature: (1) Corpus = feature plans only; the ADR corpus carries the same defect class but was recorded as a follow-up candidate; (2) Gate = suite test + scoped pre-commit hook, per ADR 9c687bb1's "locally via pre-commit hook, not just CI"; (3) No ADR; the decisions stay feature-level; (4) Title/id = "In-Tree Spec Artifact Parseability Gate" / feat-218-in-tree-spec-artifact-parseability-gate. Decisions (1) and (2) were superseded by the 2026-10-26T07:58:00.000Z entry.

### Related PRs / Commits

- Issue #218: https://github.com/dfch/biz.dfch.SpecMgr/issues/218 — the tracking issue for this feature.

- Issue #238: https://github.com/dfch/biz.dfch.SpecMgr/issues/238 — follow-up: decouple the pure path and parse logic from the eager tools packages so CLI commands work in a `[cli]`-only install.

- PR #216: https://github.com/dfch/biz.dfch.SpecMgr/pull/216 — feat-214, the follow-up that recorded issue #218.

- Commits f578e69 through 6714117 — the three consecutive commits in which feat-214's own plan document shipped unparseable (the demonstration case).

### More Information

How the defect hid (three symptoms, all observed on feat-214's plan): (1) list_feat reported the document healthy throughout, because its request path resolves each folder from a frontmatter+H1-only dirty-stage parse, exactly the masking the dirty/clean two-stage design documents (ADR 3982712a); (2) the reference-graph builders' full-parse scan legs silently skipped the document (rulebook §3.4), dropping feat-214 from every live diagram, a symptom noticed only during the Phase 130 CLI walkthrough; (3) CI runs the test suite, but no test or step runs a full parse over the repo's own in-tree documents. Cost: a serial full parse of the feature corpus measured about 124 s for 89 documents at refinement time, which is why the gate is change-scoped and the full sweep is CLI-only. Note: .specmgr/conventions.md and the .specmgr/conventions/ directory are hand-authored documentation, not specmgr-managed artifacts; they are outside the lint layouts by construction. Likewise docs/api/ and docs/GENERATED.md are generated documentation, not artifacts, and docs/adr/README.md is the generated ADR table of contents. Sibling-class framing: feat-214 fixed a gate that existed but was env-gated and unconfigured on the commit path (the PlantUML real-parser); this feature fixes the case where the gate does not exist at all.
