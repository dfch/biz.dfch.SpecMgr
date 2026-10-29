---
classification: null
created: '2026-10-26T07:16:20.020+01:00'
id: feat-218-in-tree-spec-artifact-parseability-gate
status: planning
type: feat
updated: '2026-10-29T22:40:07.879+01:00'
version: 1.0.0
---

# Feature: In-Tree Spec Artifact Parseability Gate

## Plan

### Overview

This repo keeps its own planning documents as specmgr FEAT artifacts (one README.md per feature folder under .specmgr/feat/) and its requirements, ADRs and other specmgr documents under docs/. Every one of these documents must be parseable: its frontmatter and full body are checked against its schema by the model-level parser of its domain (for example biz.dfch.specmgr.feat.models.v1.parse_feat). Nothing on the commit path performs that full parse. A body-level defect in any in-tree document is therefore invisible by default: list_feat reads only frontmatter+H1 (the dirty stage, by design: ADR 3982712a's time-qualification) and keeps reporting the document healthy, while every full-parse consumer (the get_feat read path, the reference-graph builders, similarity search) either returns a parse failure or silently drops the document. This was demonstrated in the wild by feat-214 itself: its plan document shipped unparseable in three consecutive commits (f578e69 through 6714117) because its Decisions Made section had been authored as dated bullet lines, which the schema's H4 date-entry form rejects, and the defect surfaced only as an indirect symptom (the document missing from every live reference-graph diagram) during the Phase 130 CLI walkthrough.

This feature closes that defect class for every specmgr artifact type with a new CLI command, `specmgr lint`, that runs the model-level full parse over the documents it is given (or over a whole type, or everything) and reports every failure. The command is used at three scopes, chosen so that cost scales with the size of a change and never with the size of the corpus: the pre-commit hook lints every staged artifact, the CI pull-request step lints every artifact changed against the base branch, and a full-corpus sweep (by type or all types) is available on demand through the CLI only, which also makes it usable later in an automated nightly job. A schema change may break unchanged documents; that is an accepted consequence (see Design Notes), because breaking changes are kept to a minimum and the gate is change-scoped by design.

### Requirements

- REQ-001: A new CLI command `specmgr lint` runs the model-level full parse of the document's own domain over each document it is asked to check, and reports every unparseable document (file path + parse error), not just the first.

- REQ-002: The command supports every specmgr artifact type, and the set of accepted `--type` values is derived from the global domain list (general.tools.\_domains.ALL_DOMAINS: adr plus the whole-body domains), never hand-listed, so that a newly registered domain is lintable without editing the command. The command module stays importable in a `[cli]`-only install: `--type` is a plain string validated against ALL_DOMAINS inside the lazily imported command body (an unknown value is a usage error), not a Typer choice list built at import time.

- REQ-003: The gate must do full parses; it must not be a list-based or frontmatter+H1-only check, because that is precisely the masking mechanism (the dirty stage) that hid the feat-214 defect.

- REQ-004: The command accepts explicit file paths (the hook and CI mode), `--type T` with no paths (sweep every document of that type), and `--all` (sweep every type). Paths given on the command line are linted regardless of any environment variable. Paths and a sweep flag are alternative modes: combining explicit paths with `--all` is a usage error.

- REQ-005: For each path, the document type is inferred from the path layout alone (the containing directory is named after the type, as in `docs/req/x.md`, or the path has the shape `feat/{id}/README.md`), independent of every SPECMGR\_\*\_DIR variable; an explicit `--type` overrides inference. A path whose layout matches no type is a usage error, unless `--skip-unrecognized` is given, in which case it is skipped and counted.

- REQ-006: In sweep mode (`--type` or `--all`), directories come from an explicit `--dir` argument (valid with `--type` only) if given, otherwise from the existing per-domain environment variables and defaults (SPECMGR_ADR_DIR, SPECMGR_DOCS_DIR, SPECMGR_FEAT_DIR). No new environment variable is introduced.

- REQ-007: `docs/adr/README.md` is the generated ADR table of contents, not an ADR; the sweep and the path mode both exclude it (the ADR enumeration helper does not). The rule is exact and type-specific: a file is excluded when its resolved type is adr (inferred or via `--type adr`) and its base name is `README.md`; `feat/{id}/README.md` is a real artifact and is never excluded.

- REQ-008: Exit codes follow the plantuml-check family: 0 every document parsed, 1 at least one document failed to parse (or the mcp extra is missing, as for the diagram command), 2 usage or resolution error (no paths and no sweep flag, an unreadable or missing path, an unrecognized layout without `--skip-unrecognized`, `--dir` without `--type`, explicit paths combined with `--all`, an unknown `--type` value, or `--all` that finds zero documents in total, a probable misconfiguration). A path-mode run in which every given path is skipped or excluded exits 0 with a 0-linted summary. Each invocation prints one summary with the counts linted, failed, skipped and excluded. In contrast, `--type T` against an empty or missing base directory exits 0 with a 0-document summary: a registered-but-empty domain is not a misconfiguration, unlike `--all` finding zero documents in total. The failure report ends with a per-type pointer to the repair flow: for the whole-body domains `/repair {type} {id}`, with the id derived from the path (the folder name for feat, the canonical UUID in the file name for the others), falling back to `/repair {type}` when none can be derived; for ADR, which the repair flow does not cover, a line saying so and that the file is to be fixed manually from the reported error.

- REQ-009: A new local pre-commit hook in .pre-commit-config.yaml runs `specmgr lint --skip-unrecognized` over every staged file matching the in-tree artifact locations (pass_filenames true, require_serial true, one anchored file pattern shared verbatim with the CI step of REQ-010), placed ahead of the broad pytest hook, and the specmgr-coverage-badge hook still follows pytest directly.

- REQ-010: A new step in the existing CI build job lints every artifact changed on a pull request against its base branch, for pull_request events only, pinned to Python 3.13 like the docs drift steps. The step fetches the base ref, selects the changed files with the same anchored pattern as the hook, and skips cleanly when no artifact changed.

- REQ-011: The command's cost is bounded by the number of documents it is given. The full-corpus sweep is never part of the commit path, the CI test suite or the pull-request step.

- REQ-012: The repo's drift-checked and documented surfaces are updated: docs/GENERATED.md and docs/api/ (regenerated), CHANGELOG.md, README.md's CLI section, and AGENTS.md's CLI and pre-commit paragraphs plus its "Still genuinely missing / not yet done" bullet (no validate-equivalent over the repo's own documents via pre-commit or CI), which this feature closes at change scope.

### Acceptance Criteria

- [ ] ACC-001: A temporary document in the feat-214 failure shape (a Decisions Made entry authored as a dated bullet line) makes `specmgr lint <path>` exit 1 with the offending file named and its parse error reported, followed by the whole-body repair pointer (`/repair feat {id}` with the id derived from the folder name).

- [ ] ACC-002: A broken ADR (an AdrParseError case) and a broken document of at least one other whole-body domain each make the command exit 1 with the file named, the ADR failure carrying the "not covered by the repair flow" line instead of a `/repair` pointer; a healthy document of every type exits 0 (the fixtures are the packaged `get_<d>_example` data for the whole-body types and a minimal ADR, each first verified to parse), and a failing document whose id cannot be derived from its path gets the `/repair {type}` fallback pointer.

- [ ] ACC-003: Running `specmgr lint --all` against the current in-tree corpus exits 0, and `specmgr lint --type feat` sweeps every .specmgr/feat/\*/README.md; neither is wired into the hook, CI or the test suite.

- [ ] ACC-004: With SPECMGR_FEAT_DIR and SPECMGR_DOCS_DIR pointed at empty temporary directories, `specmgr lint <in-tree path>` still lints that path, while `specmgr lint --type feat` sweeps the empty directory (proof that paths are env-independent and sweeps honor the variables); `--dir` overrides the variable.

- [ ] ACC-005: `specmgr lint docs/adr/README.md` (without `--skip-unrecognized`) exits 0, reporting the generated ADR table of contents as excluded (the summary's `excluded` count is 1) rather than as an unrecognized-layout usage error; the exclusion rule is "resolved type adr and base name README.md" and is unconditional (it applies in sweep mode, `--all` and `--type adr`, with or without the flag, also to a README.md in another directory given with `--type adr`, and the file is never parsed or counted as a failure), while `feat/{id}/README.md` is never excluded; an unrecognized path without `--skip-unrecognized` still exits 2.

- [ ] ACC-006: In a clean local repo, committing a change to any in-tree artifact (a feature README.md or a document under docs/{type}/) triggers the hook, which lints only the staged artifacts and blocks the commit when any of them fails to parse; a commit touching no artifact is unaffected by the new hook.

- [ ] ACC-007: On a pull request that changes one artifact, the CI step lints exactly the changed artifacts and fails on a broken one; on a pull request that changes none, the step is skipped or passes without running a lint.

- [ ] ACC-008: The accepted `--type` values equal ALL_DOMAINS at runtime (every member is accepted, any other value exits 2), a pinning test fails if the command hand-lists a type, and an AST pin shows commands/lint.py has no module-level import of the registry or a tools package (so `specmgr version` stays importable in a `[cli]`-only install); a test pins that the hook's file pattern matches a representative path of every type in ALL_DOMAINS and does not match `docs/api/` paths nested deeper than one level, `.specmgr/conventions/` files or `.specmgr/feat/<id>/evidence/` files, and that the CI step uses the identical pattern.

- [ ] ACC-009: The new tests and ruff and vulture are green on Python 3.11, 3.12 and 3.13; the docs drift checks (docs/, docs/GENERATED.md) and the new pull-request lint step run on Python 3.13 only, like the existing drift steps, and are green there.

- [ ] ACC-010: `specmgr lint --type uc` (a registered domain with no in-tree documents; its base directory does not exist) exits 0 with a 0-document summary.

- [ ] ACC-011: Each of the remaining REQ-008 exit-2 usage errors (no paths and no sweep flag, an unreadable or missing path, `--dir` without `--type`, explicit paths combined with `--all`, and `--all` finding zero documents in total) exits 2 with a usage message; the unrecognized-layout case is pinned by ACC-005. An unknown `--type` value likewise exits 2.

- [ ] ACC-012: Positive paths of REQ-005: a path under `docs/{type}/` and a `feat/{id}/README.md` path are linted with the inferred type; `--type` on a path overrides inference; with `--skip-unrecognized` an unrecognized path is skipped, counted in the summary and does not change the exit code.

- [ ] ACC-013: The command does full parses without the list/cache path (REQ-003): a document with a body-level defect that `list_feat`'s dirty stage reports healthy is reported as failed by `specmgr lint`, and a test with `DocCache` patched to fail on any use still passes.

- [ ] ACC-014: A test scanning .pre-commit-config.yaml, .github/workflows/ci.yml and the test suite finds no `specmgr lint --all` or `specmgr lint --type` sweep invocation (REQ-011).

- [ ] ACC-015: At close-out, README.md's CLI section, AGENTS.md's CLI and pre-commit paragraphs and its "Still genuinely missing / not yet done" bullet, CHANGELOG.md [Unreleased], docs/GENERATED.md and docs/api/ all reflect `specmgr lint` (REQ-012; the generated ones by the drift checks, the hand-written ones by inspection at Task 150.110).

- [ ] ACC-016: A path-mode run in which every given path is skipped (`--skip-unrecognized`) or excluded (the ADR README), such as the hook receiving only `docs/appendix/x.md` or `docs/adr/README.md`, exits 0 with a 0-linted summary.

### Scope

#### Included

- The `specmgr lint` command (src/biz/dfch/specmgr/commands/lint.py, registered in cli.py), thin over the existing domain parsers and the \_domains registry, plus its registration artifacts (tests/test_cli.py's pinned command set, the commands/__init__.py exports, the cli.py and commands/__init__.py docstrings, a vulture check).

- Unit tests for the command: path-layout inference, type override, `--skip-unrecognized`, the ADR README exclusion, the feat-214-shape fixture in a temporary directory (the in-tree corpus is never mutated), an ADR error case, healthy fixtures for all 13 types from the packaged examples, the per-type repair pointer, exit codes, env-variable versus `--dir` precedence, the zero-documents guard, the all-skipped-or-excluded exit 0, the derived-type-list and import-safety pins, the hook/CI shared-pattern pin, the DocCache-bypass pin and the no-sweep-on-the-commit-path scan.

- The local pre-commit hook in .pre-commit-config.yaml and its documentation in AGENTS.md's pre-commit paragraph.

- The pull-request changed-artifacts step in .github/workflows/ci.yml.

- Documentation and drift updates: docs/GENERATED.md and docs/api/ regenerated, CHANGELOG.md, README.md CLI section, AGENTS.md CLI and pre-commit paragraphs and its "Still genuinely missing / not yet done" bullet.

- Close-out: a local walkthrough of the hook, and a `specmgr lint --all` run over the in-tree corpus recorded under Updates, including this feature's own README.md.

#### Explicitly Out Of Scope

- A scheduled (nightly) workflow running `specmgr lint --all`: the command makes it possible; adding the workflow is a follow-up (the issue is opened by Task 150.120 and owns the accepted schema-change limitation).

- Relocating the domain registry and path helpers so that CLI commands work in a `[cli]`-only install: `specmgr lint` requires the mcp extra, like `specmgr diagram`. Tracked as issue #238 (needs its own ADR).

- Detecting unchanged documents that a schema change breaks: accepted by design. A schema change does not fail the gate on its own commit; the break surfaces on the next edit of an affected document, or in an on-demand or nightly full sweep. Authors repair through the existing repair flow.

- Checking that a frontmatter id equals its containing folder or file name: the gate checks parseability only.

- A full-corpus sweep in the pytest suite, the hook or the pull-request step (REQ-011).

- Pushes to dev or main: the pull-request step is pull_request-only; local enforcement is the hook.

- Repairing any currently unparseable in-tree document (the corpus is verified green as of the 2026-10-29 sweep: the one unparseable file, the issue #86 sysrs appendix, is generated documentation and was moved out of docs/sysrs/ before implementation, see More Information; any future repair goes through the existing repair flow).

- Changes to the list_feat dirty/clean two-stage design, to any document schema, or to any parse\_{d} function.

- Any new ADR for this feature (feature-level decisions only, per the Decisions Made log).

### Dependencies

#### Depends On

- FEAT feat-214-rel-invalid-diag (done, PR #216): the feature whose own plan document demonstrated the defect (three unparseable commits) and which recorded issue #218 as this follow-up.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (list_feat dirty/clean time-qualification): documents the masking mechanism that REQ-003 works around.

### Design Notes

Why full parses, never listing: list_feat's request path resolves each folder from a frontmatter+H1-only dirty-stage parse by design (ADR 3982712a), so a listing-based check would reproduce exactly the masking that hid the feat-214 defect for three commits. The command must call each domain's parser on the file's full text.

Why change-scoped, not corpus-scoped: a serial model-level parse of the then-89 feature READMEs measured about 124 s (roughly 1.4 s per document, the largest 6 s) on a 120-core machine, and the corpus only grows. A gate whose cost scales with the corpus is unusable on a commit path, and unworkable for a large project with thousands of documents. The hook (staged files) and the CI step (files changed against the base) cost in proportion to the change; the full sweep is an explicit CLI action. The earlier plan for this feature (a pytest sweep plus a hook running the whole sweep, believed to take seconds) was dropped for this reason.

Accepted limitation: because the gate checks only touched documents, a schema or parser change under src/ can leave untouched documents unparseable without failing any gate. This is accepted: breaking schema changes are kept to a minimum, and `specmgr lint --all` (manually, or in the nightly workflow whose follow-up issue Task 150.120 opens, which owns this limitation) finds any that slip through.

Type resolution: path mode infers the type from the path layout alone (the containing directory's name is a member of ALL_DOMAINS, or the path is feat/{id}/README.md), never from the SPECMGR\_\*\_DIR variables, so the hook and CI behave identically on every machine and fixture-pointing test environments cannot divert them. `--type` is the fallback for nonstandard layouts. Sweep mode is where the environment variables apply, via each domain's registered base-dir resolver (WholeBodyDomain.base_dir and iter_paths, plus the ADR equivalents), with `--dir` as the explicit override.

ADR: parse_adr is a pure text parser, so ADR needs one adapter in the command that also catches AdrParseError (a ValueError subclass), the same also_catch pattern validate_adr uses. The whole-body domains raise AssertionError, pydantic.ValidationError or yaml.YAMLError; the command catches the repo's existing tuple for these (`_CAUGHT_EXCEPTIONS` in general/models/validate_result.py, or `DEFAULT_ERROR_TYPES` in general/tools/\_listing.py, imported, not re-listed, so it cannot drift from the other parse-failure channels) plus AdrParseError and decode errors per file, so one bad file cannot abort the aggregate report, and reads files as UTF-8. iter_adr_paths yields every \*.md in docs/adr including the generated README.md table of contents, so the command filters it out. The exclusion rule is exact (REQ-007): the resolved type is adr (inferred from the layout or given by `--type adr`) and the file's base name is `README.md`, in whichever directory. It is type-specific: feat/{id}/README.md is a real feat artifact and is never excluded.

Parser, not tool: the command calls the model-level parsers (base library, pydantic only), not the MCP tools, whose wrap_tool_errors context and non-raising ValidateResult shapes a gate does not want; the errors already carry the feat-27 actionable field-path, line and fix-hint shape.

Extra requirement and `--type`: the registry (general.tools.\_domains) is imported through packages that eagerly import the mcp extra, so the command imports it lazily and exits 1 with a clear message when the extra is missing, mirroring `specmgr diagram` (whose own module-level imports are first checked by Task 100.100, not assumed safe). `cli.py` imports every commands/\* module at module level, so deriving Typer `choices` from ALL_DOMAINS would force a module-level registry import and crash every CLI command, incl. `specmgr version`, in a `[cli]`-only install. `--type` is therefore a plain optional `str`, validated against ALL_DOMAINS inside the lazily imported body (an unknown value exits 2); "derived, never hand-listed" is enforced by tests (Task 110.130), not by Typer. Removing the extra requirement is the follow-up tracked as issue #238.

Repair pointer: the repair flow (`/repair {type} {id}`) covers the whole-body domains only; ADR is out of scope. The command works from a path, and a frontmatter defect can leave a document's own id unreadable, so the pointer's id is derived from the path (the folder name for feat/{id}/README.md, the canonical UUID embedded in the file name for the others), falling back to `/repair {type}`; for ADR the report says the repair flow does not cover it and the file is to be fixed manually from the reported error.

The hook: id specmgr-lint, entry `uv run --frozen specmgr lint --skip-unrecognized`, pass_filenames true, `require_serial: true` (by default pre-commit splits the staged file list into batches and runs them as parallel processes, each printing its own summary, so the output would be interleaved; `require_serial` runs the hook as a single process, giving one ordered report for any realistic staged set. It does not guarantee a single invocation: if the file list exceeds the operating system's argument-length limit, pre-commit still splits it into several sequential invocations, each with its own summary and its own exit code, any non-zero one blocking the commit. This is accepted, and the cost is that a very large staged set is parsed serially instead of in parallel), files limited to the in-tree artifact locations by the anchored pattern `^(\.specmgr/feat/[^/]+/README\.md|docs/[^/]+/[^/]+\.md)$` (the lint command's own type list decides which of the matched files are artifacts, so the pattern needs no per-type list; files it matches but the command skips or excludes, e.g. docs/appendix/\*.md or docs/adr/README.md, pass with a 0-linted summary). It is placed ahead of pytest, and specmgr-coverage-badge stays directly after pytest. It parses the working-tree file contents, not the git index, so a partially staged file is checked as it exists on disk; this is accepted and documented.

The CI step: pull_request events only, in the existing build job, guarded by `matrix.python-version == '3.13' && github.event_name == 'pull_request'` (Python 3.13 only, like the docs drift steps). It fetches the base branch explicitly (a targeted `git fetch`, not a change to the shared checkout's fetch-depth), takes the base ref from an `env:` variable (never inline `${{ }}` in the script), lists changed files with `git diff --name-only -z --diff-filter=ACMR` against the merge base, filters them with the SAME anchored pattern as the hook (not the broader "any .md under .specmgr/ and docs/", which would also match files such as .specmgr/feat/*/evidence/\*\*/docs/tsk/*.md), and passes the NUL-delimited list to `specmgr lint --skip-unrecognized` via xargs -0; with an empty list it does nothing. A drift test pins that hook and CI use the identical pattern. Unlike the earlier plan, this changes the workflow.

### Related Decisions

- FEAT feat-214-rel-invalid-diag (done) + PR #216: the follow-up whose own plan demonstrated the defect and which recorded issue #218.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44: list_feat dirty/clean time-qualification, the masking mechanism the full-parse requirement works around.

- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI", which grounds the hook half of the gate.

- AGENTS.md, "Still genuinely missing / not yet done": the standing note that no validate-equivalent check runs over the repo's own documents via pre-commit or CI. This feature closes it for every artifact type, at change scope; Task 140.110 updates the bullet (REQ-012).

- Follow-up (issue to be opened by Task 150.120): a scheduled (nightly) workflow running `specmgr lint --all`. It is the owner of the accepted limitation that a schema or parser change can break untouched documents without failing any change-scoped gate.

- Issue #238: decouple the pure path and parse logic from the eager tools packages so registry-backed CLI commands work without the mcp extra (follow-up, needs its own ADR).

### Task List

#### Phase 100: Lint Command

- [x] Task 100.100: Before coding, verify with a real import test (not by reading code) whether the CLI modules import with the mcp extra unavailable: block `mcp` (e.g. `sys.modules["mcp"] = None` in a fresh interpreter) and import `biz.dfch.specmgr.commands.diagram` and `biz.dfch.specmgr.cli`, noting that commands/diagram.py imports `general.tools._doc_paths`, `general.tools._path_safety` and `uc.tools._cache` at module level, so it is NOT assumed to be a safe precedent. Decide the guard pattern from the result and record the finding under Updates. Whatever `diagram` turns out to do, `commands/lint.py` itself must have no module-level import of the registry or of any tools package; everything registry-backed is imported inside the command body behind the `ImportError` -> exit 1 guard.

- [x] Task 100.110: Implement commands/lint.py and register it in cli.py: arguments PATHS, options `--type` (a plain optional `str`, validated against ALL_DOMAINS inside the lazily imported body; an unknown value is a usage error, exit 2; never Typer `choices` or a hand-listed set, see Extra requirement), `--all`, `--dir`, `--skip-unrecognized`; model-level parse per document with a per-domain adapter (whole-body domains via the registry's parse_text, ADR via parse_adr); catch the repo's existing parse-failure tuple (`general.models.validate_result._CAUGHT_EXCEPTIONS`, or `general.tools._listing.DEFAULT_ERROR_TYPES`, imported rather than re-listed) plus AdrParseError and decode errors per file; read UTF-8.

- [x] Task 100.120: Implement path-layout type inference (containing directory in ALL_DOMAINS, or feat/{id}/README.md), the `--type` override, the unrecognized-path handling, the ADR README exclusion (unconditional, REQ-007; rule: the resolved type is adr and the file's base name is `README.md`, regardless of directory, and never for other types), the paths-plus-`--all` usage-error guard, and the sweep mode with env-var and `--dir` directory resolution.

- [x] Task 100.130: Implement reporting and exit codes: every failing (path, error) pair, a summary of counts (linted, failed, skipped, excluded; one summary per invocation), the per-type repair pointer (whole-body domains: `/repair {type} {id}` with the id derived from the path, the folder name for feat or the canonical UUID in the file name for the others, falling back to `/repair {type}` when none can be derived; ADR: a "not covered by the repair flow, fix manually" line), exit 0/1/2 per REQ-008, the zero-documents guard for `--all` (exit 2), the empty-domain `--type` behavior (exit 0 with a 0-document summary), and exit 0 with a 0-linted summary when every given path was skipped or excluded.

- [x] Task 100.140: Registration artifacts that must move with the new command: add `lint` to the pinned registered-command set in tests/test_cli.py (and a help smoke), export it from commands/__init__.py (import and `__all__`), update the cli.py and commands/__init__.py module docstrings, and run the vulture check (`specmgr unused-code`), adding to whitelist.py only if a new helper is genuinely flagged.

#### Phase 110: Tests

- [x] Task 110.100: Unit tests for inference, `--type` override, `--skip-unrecognized` (skipped and counted), the ADR README exclusion (unconditional: with and without the flag, in path and sweep mode; `--type adr` on a README.md in another directory; `feat/{id}/README.md` NOT excluded) and usage errors (exit 2, incl. explicit paths combined with `--all` and an unknown `--type` value), using temporary directories only.

- [x] Task 110.110: Negative pins: the feat-214-shape fixture (a valid document with a dated-bullet Decisions Made section, built from the packaged feat template) asserting the file name and a recognizable error fragment; an ADR error case; one other whole-body domain; plus the healthy fixtures: for every whole-body type the packaged `get_<d>_example` data (first verified to parse), for ADR a minimal rendered or copied ADR; each healthy document of every type exits 0. Also pin the per-type repair pointer (whole-body with derived id, whole-body fallback, ADR line).

- [x] Task 110.120: Environment tests: with SPECMGR_FEAT_DIR and SPECMGR_DOCS_DIR patched to empty temporary directories, path mode is unaffected, sweep mode honors the variables, and `--dir` overrides; `--all` with zero documents exits 2; `--type uc` (a registered domain with no in-tree documents) exits 0 with a 0-document summary; a path run where every path is skipped or excluded exits 0 with a 0-linted summary.

- [x] Task 110.130: Drift pins: the runtime `--type` acceptance set equals ALL_DOMAINS, the command contains no hand-listed type and lint.py has no module-level import of the registry or a tools package (AST pin, so `specmgr version` stays importable in a `[cli]`-only install); the hook's file pattern matches one representative path per ALL_DOMAINS type (`.specmgr/feat/feat-1-x/README.md` for feat, `docs/{type}/x.md` for the others) and does NOT match `docs/api/...` with a deeper nesting, `.specmgr/conventions/x.md`, or `.specmgr/feat/<id>/evidence/.../docs/tsk/x.md`; the hook's pattern and the CI step's pattern are identical (the CI step reads the same string).

- [x] Task 110.140: Pins for the remaining requirements: a test that the command parses with the document's own model-level parser and never goes through `DocCache`/`list_<d>` (REQ-003; e.g. a body-level defect that `list_feat`'s dirty stage cannot see is reported, with the cache patched to fail on any use); a test that scans .pre-commit-config.yaml, .github/workflows/ci.yml and the tests for a `specmgr lint --all` / `--type` sweep invocation and finds none (REQ-011).

#### Phase 120: Pre-commit Hook

- [x] Task 120.100: Add the specmgr-lint local hook to .pre-commit-config.yaml (pass_filenames true, the first such hook in the config since every existing local hook uses pass_filenames false, `require_serial: true` so the staged files are linted by one process with one ordered summary instead of parallel batches with interleaved summaries (a staged list longer than the OS argument-length limit is still split into sequential invocations, each with its own summary), an in-tree artifact file pattern following the repo's anchored-regex files: convention, exactly `^(\.specmgr/feat/[^/]+/README\.md|docs/[^/]+/[^/]+\.md)$`, entry `uv run --frozen specmgr lint --skip-unrecognized`, placed ahead of pytest with specmgr-coverage-badge still directly after pytest) and document it in AGENTS.md's pre-commit paragraph, including the working-tree-versus-index note. A commit that stages only files this pattern matches but the command skips or excludes (e.g. docs/appendix/\*.md, docs/adr/README.md) must pass (exit 0, 0-linted summary).

- [x] Task 120.110: Local walkthrough: (a) a healthy artifact change commits with the hook linting only the staged files; (b) a feat-214-shape defect introduced in a scratch feature README blocks the commit with the file and error reported; (c) revert; (d) a commit touching no artifact does not trigger the hook; (e) a commit touching only docs/appendix/\*.md or docs/adr/README.md passes. Record the outcome under Updates.

#### Phase 130: CI Step

- [ ] Task 130.100: Add the pull_request-only changed-artifacts step to the build job in .github/workflows/ci.yml: guard `if: matrix.python-version == '3.13' && github.event_name == 'pull_request'`; fetch the base branch explicitly (a targeted `git fetch` of the base ref, rather than changing the shared checkout's fetch-depth); pass `github.base_ref` through an `env:` variable, never inline `${{ }}` in the script; list changed files with `git diff --name-only -z --diff-filter=ACMR` against the merge base; filter them with the SAME anchored pattern as the hook (Task 120.100); pass the NUL-delimited list to `uv run --frozen --all-extras --python 3.13.13 specmgr lint --skip-unrecognized` via xargs -0 (`--all-extras` is mandatory because the registry import chain forces the mcp extra); skip cleanly when the filtered list is empty; follow the workflow's existing pinned-action conventions.

- [ ] Task 130.110: Verify on the feature's own pull request: the step lints exactly the changed artifacts (ACC-007), and a scratch PR commit with a broken artifact fails it, then is reverted.

#### Phase 140: Documentation and Drift

- [ ] Task 140.100: Regenerate docs/GENERATED.md and docs/api/ (specmgr docs), confirm docs/MCP.md and the schema files are unchanged, and add the CHANGELOG.md [Unreleased] entry.

- [ ] Task 140.110: Update README.md's CLI section and AGENTS.md's CLI section for `specmgr lint` (usage, the three scopes, exit codes, the mcp extra requirement and issue #238, the accepted schema-change limitation), and update AGENTS.md's "Still genuinely missing / not yet done" bullet (no validate-equivalent over the repo's own documents via pre-commit or CI) to say the gap is closed at change scope by the `specmgr lint` hook and CI step, with the full sweep CLI-only.

#### Phase 150: Close-out

- [ ] Task 150.100: Run `specmgr lint --all` over the in-tree corpus (exit 0, including this feature's own README.md) and record the result, its duration and the document count under Updates; run the full local quality gate (ruff, vulture, pytest, drift checks).

- [ ] Task 150.110: Confirm ACC-001 through ACC-016, mark all tasks done, update Current Status, and set the status to done.

- [ ] Task 150.120: Open the follow-up GitHub issue for a scheduled (nightly) `specmgr lint --all` workflow, the owner of the accepted schema-change limitation, and reference it from this plan's Related Decisions and Related PRs / Commits.

## Progress

### Current Status

**As of 2026-10-29**: Phases 100, 110 and 120 complete — Phase 100 implemented the `specmgr lint` command itself plus its registration artifacts, Phase 110 its test suite (one module, `tests/commands/test_lint.py`: 46 tests + 43 subtests, every fixture in a per-test `tempfile` directory — the in-tree corpus is never mutated; see the 2026-10-29T10:00:00.000Z and 2026-10-29T16:21:21.875Z Updates and Decisions Made entries), Phase 120 the `specmgr-lint` pre-commit hook (the config's first `pass_filenames: true` hook, `require_serial`, the canonical anchored in-tree artifact file pattern, ahead of `pytest`) plus its AGENTS.md documentation and the five-case local walkthrough (healthy, defective, non-artifact and skipped-only commits, each immediately undone; see the 2026-10-29T21:40:07.879Z Updates and Decisions Made entries); implementation in progress, Phases 130 through 150 open. The command lints explicit paths (type inferred from the path layout alone, `--type` override, `--skip-unrecognized`), sweeps by type or all (registered base-dir resolvers, `--dir` override, the unconditional ADR README exclusion), runs only model-level full parses, and reports every failure with its per-type repair pointer and the REQ-008 exit 0/1/2 contract. Its module level is import-safe without the mcp extra (Task 100.100's finding: the CLI as it stands already requires the extra to import at all — pre-existing, issue #238 territory), and its registry-backed names load lazily inside the command body behind the exit-1 missing-extra guard. The in-tree corpus is verified by the command's own sweep: `specmgr lint --all` exits 0 with 161 documents linted, 0 failures, 1 excluded (the generated docs/adr/README.md).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-29T21:40:07.879Z - Phase 120 complete (specmgr-lint pre-commit hook; five-case local walkthrough, all commits undone)

Phase 120 added the `specmgr-lint` local hook to `.pre-commit-config.yaml` (Task 120.100) and documented it in AGENTS.md's pre-commit paragraph, including the working-tree-versus-index note. The hook: entry `uv run --frozen specmgr lint --skip-unrecognized`, `pass_filenames: true` (the first hook in the config that passes a file list — every existing local hook uses `pass_filenames: false`), `require_serial: true` (one process, one ordered summary per invocation; a staged list longer than the OS argument-length limit is still split into sequential invocations, each with its own summary), the canonical anchored file pattern `^(\.specmgr/feat/[^/]+/README\.md|docs/[^/]+/[^/]+\.md)$` (unquoted, house style), placed immediately ahead of the `pytest` hook with `specmgr-coverage-badge` still directly after `pytest`. With the hook present, the previously conditional pattern-identity assertion in `TestLintHookPattern` became a hard pin (the test extracts the hook's `files:` value and requires it to equal the canonical constant), and `pre-commit validate-config` passes.

Task 120.110 was executed as five real commits against scratch files, each immediately undone per the protocol; the tree ended at the pre-walkthrough commit 23e2713 with `git status --short` showing only the two Phase 120 files. One deviation from the assumed protocol, with the mechanics that forced it, is recorded in the Decisions Made entry of the same instant: pre-commit 4.6.1 refuses to run the hook set while `.pre-commit-config.yaml` carries an unstaged working-tree change (its `_has_unstaged_config` check is a `git diff --quiet` of the config against the index), so the planned "config sits unstaged" setup was infeasible; the config was staged for each walkthrough commit (and therefore rode along in each scratch commit), and after each `git reset --hard HEAD~1` the two Phase 120 files were restored byte-identical from a pre-walkthrough backup (md5-verified after every reset).

Case (a) — healthy artifact: `.specmgr/feat/feat-999-hook-walkthrough/README.md` was created as a byte-exact copy of the packaged feat template (it parses), staged together with the config, and committed as `git commit -m "walkthrough: healthy artifact (scratch)"`. The hook ran over exactly the staged artifact, and `ruff format` (which also selects markdown) ran over it first and passed:

```text
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/user/.cache/pre-commit/patch1793309686-1772617.
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
specmgr schema (vcr package copy)....................(no files to check)Skipped
specmgr schema (sysrs package copy)..................(no files to check)Skipped
specmgr lint.............................................................Passed
pytest...............................................(no files to check)Skipped
specmgr coverage-badge (CI source-less condition)....(no files to check)Skipped
[INFO] Restored changes from /home/user/.cache/pre-commit/patch1793309686-1772617.
[feat-218-in-tree-spec-artifact-parseability-gate f85dee6] walkthrough: healthy artifact (scratch)
 2 files changed, 117 insertions(+)
 create mode 100644 .specmgr/feat/feat-999-hook-walkthrough/README.md
```

Commit f85dee6 was created (2 files changed: the +25-line hook addition plus the 92-line scratch README), then undone with `git reset --hard HEAD~1` plus the backup restore; the scratch folder was gone and the tree clean at 23e2713. pre-commit swallows a passing hook's stdout, so the hook's own summary line comes from a verbatim re-run of its identical entry command over the same file: `summary: linted=1 failed=0 skipped=0 excluded=0` (exit 0).

Case (b) — feat-214-shape defect: the scratch folder was recreated with the same healthy text and its one Decisions Made H4 date entry changed to a dated bullet line (`#### 2025-06-14 19:22:53.667Z - Placeholder decision` replaced by `- 2025-06-14 19:22:53.667Z - Placeholder decision`), staged, and committed as `git commit -m "walkthrough: defective artifact (scratch)"`. The commit was blocked — `specmgr lint` failed with the file named, the parse error and the repair pointer, and no commit was created (`git log --oneline -1` still 23e2713, exit 1):

```text
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/user/.cache/pre-commit/patch1793309770-1774577.
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
specmgr schema (vcr package copy)....................(no files to check)Skipped
specmgr schema (sysrs package copy)..................(no files to check)Skipped
specmgr lint.............................................................Failed
- hook id: specmgr-lint
- exit code: 1

✗ .specmgr/feat/feat-999-hook-walkthrough/README.md (feat): Feature > Progress > DecisionsMade > DecisionEntry: expected list[DecisionEntry] (heading matching regex '^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+$'), found no match; remaining text starts at line 69 of the normalized body (3 line(s)) and begins with:
- 2025-06-14 19:22:53.667Z - Placeholder decision

A short lead paragraph describing the decision and its rationale.
  repair via: /repair feat feat-999-hook-walkthrough
summary: linted=1 failed=1 skipped=0 excluded=0

pytest...............................................(no files to check)Skipped
specmgr coverage-badge (CI source-less condition)....(no files to check)Skipped
[INFO] Restored changes from /home/user/.cache/pre-commit/patch1793309770-1774577.
```

Case (c) — revert: the blocked case never committed, so the revert is the cleanup itself: `git reset` (unstage the config and the defective README) plus `rm -rf .specmgr/feat/feat-999-hook-walkthrough`; afterwards `git status --short` showed only ` M .pre-commit-config.yaml`, ` M AGENTS.md` and the two scratch files of the later cases, and `git log --oneline -1` was still 23e2713.

Case (d) — non-artifact file: `scratch-root-file.txt` was created at the repo root, staged together with the config, and committed as `git commit -m "walkthrough: non-artifact file (scratch)"`. No hook matched the staged set at all — the new `specmgr lint` hook included, which reported `(no files to check)Skipped` like every other hook — and the commit passed (77c3b68, then undone with `git reset --hard HEAD~1` plus the backup restore; the scratch file was gone):

```text
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/user/.cache/pre-commit/patch1793309812-1775713.
ruff format..........................................(no files to check)Skipped
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
specmgr schema (vcr package copy)....................(no files to check)Skipped
specmgr schema (sysrs package copy)..................(no files to check)Skipped
specmgr lint.........................................(no files to check)Skipped
pytest...............................................(no files to check)Skipped
specmgr coverage-badge (CI source-less condition)....(no files to check)Skipped
[INFO] Restored changes from /home/user/.cache/pre-commit/patch1793309812-1775713.
[feat-218-in-tree-spec-artifact-parseability-gate 77c3b68] walkthrough: non-artifact file (scratch)
 2 files changed, 26 insertions(+)
 create mode 100644 scratch-root-file.txt
```

Case (e) — matched-but-skipped artifact only: `docs/appendix/hook-walkthrough.md` was created (a new file — staging the unmodified `docs/adr/README.md` would be a no-op for pre-commit, and modifying the generated ADR table of contents risks the `specmgr adr-toc` drift hook; the plan's "or" alternative, see the Decisions Made entry), staged together with the config, and committed as `git commit -m "walkthrough: skipped-only artifact (scratch)"`. The hook ran, the command skipped the file as an unrecognized layout and exited 0 with the 0-linted summary, and the commit passed (31437d0, then undone the same way):

```text
[WARNING] Unstaged files detected.
[INFO] Stashing unstaged files to /home/user/.cache/pre-commit/patch1793309833-1776230.
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (sop package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
specmgr schema (vcr package copy)....................(no files to check)Skipped
specmgr schema (sysrs package copy)..................(no files to check)Skipped
specmgr lint.............................................................Passed
pytest...............................................(no files to check)Skipped
specmgr coverage-badge (CI source-less condition)....(no files to check)Skipped
[INFO] Restored changes from /home/user/.cache/pre-commit/patch1793309833-1776230.
[feat-218-in-tree-spec-artifact-parseability-gate 31437d0] walkthrough: skipped-only artifact (scratch)
 2 files changed, 28 insertions(+)
 create mode 100644 docs/appendix/hook-walkthrough.md
```

Again the hook's own summary line is from the verbatim re-run of its identical entry command over the same file: `summary: linted=0 failed=0 skipped=1 excluded=0` (exit 0). After the final undo, `git status --short` showed exactly ` M .pre-commit-config.yaml` and ` M AGENTS.md`, `git log --oneline -1` was 23e2713 (the pre-walkthrough commit), and no scratch file remained anywhere in the tree.

#### 2026-10-29T16:21:21.875Z - Phase 110 complete (lint command test suite: one module, 46 tests + 43 subtests)

Phase 110 implemented the Phase 110 test suite as a single module `tests/commands/test_lint.py` (house style: Typer `CliRunner` over the full app, `unittest` classes, a per-test `tempfile` directory — the in-tree corpus is never mutated). Test inventory by task: Task 110.100 — 18 tests (path-layout inference, the containing-directory rule and the `feat/<id>/README.md` rule; the `--type` override including rescue of a nonstandard layout; `--skip-unrecognized` skipped-and-counted plus the mixed-run exit code; the ADR README exclusion in every pinned shape — inferred and `--type adr` in path mode, with and without the flag, the `--type adr` and `--all` sweeps, a README.md in another directory, and `feat/<id>/README.md` never excluded, with the excluded fixtures carrying garbage content that proves they are never parsed; the exit-2 usage errors, incl. `--type` combined with `--all` and a user-named unreadable path); Task 110.110 — 9 tests (the feat-214-shape fixture built from the packaged feat template by converting its one Decisions Made H4 date entry into a dated bullet line, asserting the file name, the recognizable `DecisionsMade` / `expected list[DecisionEntry]` error fragment and the `/repair feat <folder>` pointer; a structurally broken ADR asserting the `unrecognized H2 heading` fragment, the fix-manually line and the absence of any `/repair` pointer; a broken `req` asserting the recognizable `Requirement > Characteristics` fragment, the lowercased-UUID pointer derived from a mixed-case file name, and the id-less `/repair req` fallback; the healthy fixtures — each of the 12 packaged `get_<d>_example` data files first verified to parse through its own model-level parser, written at a layout the command infers (frontmatter `id` as file name or folder name), plus a minimal rendered ADR, every one exiting 0; and the read-failure pins — a user-named path that fails to decode is exit 1 counted in `linted` (Phase 100 decision 3), a sweep-enumerated unreadable file is exit 1 in contrast to the user-named unreadable path's exit 2, and a feat-typed document at a non-folder-shape path gets the `/repair feat` fallback); Task 110.120 — 6 tests (path mode unaffected by `SPECMGR_DOCS_DIR` / `SPECMGR_FEAT_DIR` / `SPECMGR_ADR_DIR` pointed at empty temporary directories, sweep mode honoring the variables, `--dir` overriding, `--all` with zero documents exiting 2, `--type uc` — a registered domain whose base directory does not exist — exiting 0 with a 0-document summary, and a path run in which every path is skipped or excluded exiting 0 with a 0-linted summary); Task 110.130 — 10 tests (the runtime `--type` acceptance set equals the registry's `ALL_DOMAINS` — all 13 members accepted via an empty-`--dir` sweep, a non-member exiting 2; the AST pins over `commands/lint.py` — module-level imports confined to stdlib, `typer` and the mcp-free `..models.adr` package (no registry, no tools package), and no module-level collection of two or more domain-name string literals; a real in-process import with `mcp` blocked, loading the module from its own file to bypass the package's `__init__`; the canonical hook pattern constant (the plan's anchored regex, defined once in the test module) matching one representative path per `ALL_DOMAINS` type and none of `docs/api/x/y.md` (deeper nesting), `.specmgr/conventions/x.md`, or the evidence-nested `.specmgr/feat/feat-1-x/evidence/some/docs/tsk/x.md`; the conditional hook/CI identity — when `.pre-commit-config.yaml` carries a `specmgr-lint` hook or `ci.yml` carries the lint command, the pattern in that file MUST equal the constant, verified against scratch copies for the quoted, unquoted, wrong-pattern and absent-hook cases; and a fresh-interpreter subprocess pinning the missing-`mcp`-extra guard — exit 1 plus the install message — which cannot fire in-process); Task 110.140 — 3 tests (the feat-214 defect that `read_feat_dirty`'s dirty stage reports healthy is reported failed by the command while the full model-level parse raises; the command still reports the failure with `DocCache.read` / `peek_preloaded` / `read_preloaded` patched to explode on any use; the REQ-011 scan of `.pre-commit-config.yaml`, `.github/workflows/ci.yml` and every source file under `tests/` finding no invocation of the command carrying a sweep flag on the same line, the searched strings built from parts so the test module cannot trip its own scan). Quality gate: `ruff format --check`, `ruff check` and `specmgr unused-code` all green; the full suite is 4872 passed / 18 skipped with total coverage 99% (217 missed statements, up from 228 before Phase 110) and `commands/lint.py` itself at 98% — its only uncovered lines are the missing-extra guard body, exercised by the subprocess test whose separate process does not merge its coverage data.

#### 2026-10-29T10:00:00.000Z - Phase 100 complete (lint command, registration artifacts)

Phase 100 implemented the `specmgr lint` command (src/biz/dfch/specmgr/commands/lint.py, registered in cli.py and commands/__init__.py) per REQ-001 through REQ-008: path mode (type inferred from the path layout alone — the containing directory in ALL_DOMAINS, or the feat/{id}/README.md shape — with the `--type` override and `--skip-unrecognized`), the type sweep (`--type T` from `--dir` or the domain's registered base-dir resolver) and the all sweep (`--all`, with the zero-documents exit-2 guard), the unconditional ADR README exclusion, model-level full parses only (the registry's parse_text adapters for the whole-body domains, parse_adr for ADR; never DocCache, `list_<d>` or an MCP tool), the per-file catch of the imported _CAUGHT_EXCEPTIONS tuple (from general.models.validate_result) plus AdrParseError plus UTF-8 decode errors, and the reporting contract (every failing path + error pair, the per-type repair pointer — /repair {type} {id} with the path-derived id, the feat folder name for feat, the file-name UUID lowercased for the other types, the /repair {type} fallback, and the ADR fix-manually line — plus the one summary of linted/failed/skipped/excluded and the exit 0/1/2 codes). Task 100.100's real import test (a fresh interpreter with sys.modules["mcp"] = None, run as `uv run --frozen python -c`) found that importing biz.dfch.specmgr.commands.diagram and biz.dfch.specmgr.cli both fail with `ModuleNotFoundError: No module named 'mcp.server'`: commands/__init__.py imports every command module, and even adr_toc's module-level `adr.tools._paths` import reaches server.py (adr/__init__ → adr/prompts/create_adr → general/__init__ → general/prompts/compact_history → general/tools/__init__, which eagerly imports every @mcp.tool() module → general/tools/delete → dec/__init__ → dec/prompts/create_dec → server.py's `from mcp.server import MCPServer`), with diagram.py's own module-level general.tools._doc_paths / uc.tools._cache / uc.tools._paths imports as a second, independent entry into the same chain — so diagram is NOT a safe module-level precedent, and the CLI as it stands already requires the mcp extra to import at all (a pre-existing state in issue #238's territory); a boundary test showed that only the top-level models.* packages, _envregistry and plantuml.* import cleanly without mcp, while every general.* import (even general.models.validate_result) fails through the general/__init__ → tools → server chain. The guard pattern chosen and implemented accordingly: lint.py's module level is strictly stdlib + typer + the top-level models.adr parser (verified import-safe), and every registry-backed name (ALL_DOMAINS/ADR/FEAT/whole_body_domain from general.tools._domains, _CAUGHT_EXCEPTIONS from general.models.validate_result, adr_base_dir/iter_adr_paths from adr.tools._paths) loads inside _registry_backed() behind the ImportError → exit 1 guard with the diagram/mcp.py missing-extra message — verified by loading lint.py from its file with mcp blocked (module import OK) and invoking the command (exit 1 with the message). Smoke-tested end to end: healthy feat/req/ADR paths exit 0, a feat-214-shape broken feat README exits 1 with /repair feat {id} (the folder name), a broken ADR exits 1 with the fix-manually line, a non-UTF-8 file exits 1 as a per-file decode failure, docs/adr/README.md is excluded (never parsed, never failed) in path mode, in the --all sweep, and for --type adr on a README.md in another directory, feat/{id}/README.md is never excluded, every REQ-008 exit-2 usage error behaves (no arguments, --dir without --type, paths + --all, unknown --type, unrecognized layout without the flag, --all over three empty base dirs), --type uc over a missing base dir exits 0 with a 0-document summary, a run of all-skipped-or-all-excluded paths exits 0 with a 0-linted summary, and `specmgr lint --all` over the in-tree corpus exits 0 with `summary: linted=161 failed=0 skipped=0 excluded=1` (matching the plan's verified baseline, 2m30s serial). Quality gate: `uv run --frozen ruff format --check` (2118 files already formatted), `uv run --frozen ruff check` (All checks passed), `uv run --frozen specmgr unused-code` (No unused code found; no whitelist.py additions needed), `uv run --frozen pytest -n auto --cov=src --cov-report=` (4826 passed, 18 skipped). Registration artifacts per Task 100.140: tests/test_cli.py's pinned registered-command set now includes lint, plus a TestLintCommand help smoke; commands/__init__.py imports/exports lint and documents its import-safe module level; cli.py's docstring notes lint's mcp-extra requirement and its lazy-registry design. Phases 110 through 150 remain open.

#### 2026-10-29T09:00:00.000Z - Plan amended after third refinement (2 errors, 6 gaps, 4 discrepancies, 5 improvements applied)

A third refinement pass (feat-refiner, read-only) found, and this amendment applied: E1 (REQ-002 versus the lazy import: `--type` is now a plain `str` validated against ALL_DOMAINS in the lazily imported body; REQ-002, REQ-008, ACC-008, Task 100.110 and the Extra requirement note reworded); E2 (the repair pointer is now per type, ADR excluded, with an id-less fallback; REQ-008, ACC-001, Task 100.130); G1 (new Task 100.140 for `tests/test_cli.py`'s pinned command set, the `commands/__init__.py` exports, the `cli.py`/`commands/__init__.py` docstrings and the vulture whitelist check); G2 (AGENTS.md's "Still genuinely missing" bullet added to REQ-012 and Task 140.110); G3 (new ACC-012 to ACC-015 for REQ-005 positive paths, REQ-003 DocCache bypass, REQ-011 no-sweep-on-commit-path and REQ-012 surfaces); G4 (the ADR README exclusion rule pinned: type adr and base name README.md); G5 (fixtures from the packaged `get_<d>_example` data); G6 (all-skipped or all-excluded path run exits 0, pinned by new ACC-016); D1 (one shared anchored file pattern for hook and CI, pinned by a drift test); D2 (an `excluded` counter in the summary); D3 (ACC-009 reworded: tests on 3.11 to 3.13, drift checks and the new CI step on 3.13); D4 (Task 100.100 no longer treats `diagram` as a verified precedent: it runs a real import test with the mcp extra blocked); I1 (reuse `_CAUGHT_EXCEPTIONS`); I2 (precise CI step: 3.13 and pull_request guard, explicit base-ref fetch, `env:`-passed base ref, NUL-delimited file list); I3 (negative cases in the hook-pattern drift pin); I4 (batched-hook output: `require_serial: true` replaces parallel batches with a single process and one ordered summary; one summary per invocation, and still several sequential invocations if the file list exceeds the OS argument-length limit); I5 (owner for the accepted limitation: a Phase 150 task opens the nightly-sweep follow-up issue). Implementation not started.

#### 2026-10-29T06:21:00.000Z - Plan amended after second refinement (corpus verified, edge cases pinned)

A second refinement pass (2026-10-28) ran a full-parse sweep over the in-tree corpus and found the plan's "corpus is green today" premise wrong: exactly one document failed, the issue #86 sysrs appendix (docs/sysrs/sysrs-8d752304-...-appendix.md, added in bca1a87), a manually generated verbatim concatenation of 24 referenced artifacts with no frontmatter of its own. Repairing it to be parseable was rejected as infeasible by design (after its single raw-HTML token, the sysrs parser rejects its H1, which is not the required "System Requirements Specification: ..." heading). It was classified as generated documentation, not a sysrs artifact (the same precedent as docs/api/, docs/GENERATED.md and docs/adr/README.md), and moved to docs/appendix/ on 2026-10-29; the post-move sweep over all 13 types is green (161 documents, 0 failures, 158.4 s serial) and list_sysrs reports zero failed rows. Semantics pinned: `--type T` on an empty or missing base directory exits 0 with a 0-document summary (a registered-but-empty domain is not a misconfiguration, in contrast to `--all` finding zero documents in total), explicit paths combined with `--all` are a usage error (exit 2), and the docs/adr/README.md exclusion is unconditional in path and sweep mode (ACC-005 rewritten). ACC-010 (the empty-domain `--type` case) and ACC-011 (the remaining exit-2 cases) were added. Task 120.100 now notes that the hook is the first pass_filenames: true hook in .pre-commit-config.yaml and that its files: pattern follows the anchored-regex convention; Task 130.100 now states the CI invocation explicitly (the `if: matrix.python-version == '3.13'` guard and `uv run --frozen --all-extras --python 3.13.13 specmgr lint ...`, where `--all-extras` is mandatory because the registry import chain forces the mcp extra). The 89-document counts in Design Notes and the 07:58 Updates entry were corrected to mark them as the at-refinement-time measurement.

#### 2026-10-26T07:58:00.000Z - Plan revised after refinement

A refinement pass found the plan's "parses in seconds" claim wrong by about 20x (a serial full parse of 89 feature READMEs took about 124 s), plus gaps in the hook scope, the docs drift, the fixture design and the exception handling. The plan was redesigned: a new `specmgr lint` command for every artifact type; the pre-commit hook lints staged artifacts; a pull-request CI step lints changed artifacts; full-corpus sweeps only via the CLI (by type or all). Drift-prone corpus counts were removed (the one-time cost measurement, then-89 documents at about 124 s, is retained and marked as at-refinement-time), the docs/GENERATED.md drift item, the ADR README exclusion and the feat-214 reference tag were added. Follow-up issue #238 was created for the mcp-extra decoupling.

#### 2026-10-26T05:42:45.913Z - Created

Feature plan drafted from issue #218: a full-parseability gate over the repo's own in-tree FEAT corpus (.specmgr/feat/\*/README.md), enforced by a plain test in the existing suite and by a new pre-commit hook scoped to the in-tree markdown (local enforcement for docs-only commits, which the broad src/tests-scoped pytest hook skips). The defect class was demonstrated in the wild by feat-214's own plan shipping unparseable in three consecutive commits (f578e69 through 6714117). Superseded in design by the 2026-10-26T07:58:00.000Z entry.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-29T21:40:07.879Z - Phase 120: walkthrough mechanics — pre-commit's unstaged-config refusal, config-in-scratch-commits, and case (e) via docs/appendix

Decisions made while executing the Phase 120 walkthrough, beyond the plan and the orchestrator rulings, scoped to the walkthrough's mechanics: (1) pre-commit 4.6.1 refuses to run the hook set while `.pre-commit-config.yaml` carries an unstaged working-tree change (its `_has_unstaged_config` check is a `git diff --quiet` of the config against the index; observed as `[ERROR] Your pre-commit configuration is unstaged.`), so the assumed protocol of leaving the Phase 120 files unstaged during the walkthrough was infeasible; the config was staged for each walkthrough commit and therefore rode along in each scratch commit (the recorded commits show `2 files changed`), and after each `git reset --hard HEAD~1` the two Phase 120 files were restored byte-identical from a pre-walkthrough backup (md5-verified after every reset) so the tree ended at exactly the pre-walkthrough commit with only the unstaged Phase 120 changes. (2) `git commit -- <pathspec>` was tried and rejected as a way to keep the config out of the scratch commit: git hands the pre-commit hook a temporary `GIT_INDEX_FILE` built from HEAD plus the pathspec, in which the out-of-pathspec config appears unstaged, so the refusal fired twice although the config was staged in the real index (verified: with the config staged, `git diff --quiet .pre-commit-config.yaml` returned 0, yet the pathspec commit still failed the hook's check); plain commits were used instead, and the config's addition is an intentional part of the recorded scratch commits. (3) Case (e) was run with a fresh `docs/appendix/hook-walkthrough.md` (the plan's "or" alternative): staging the unmodified `docs/adr/README.md` would be a no-op for pre-commit (an unmodified file is not in the staged set, so the hook would not run at all), and modifying the generated ADR table of contents risks the `specmgr adr-toc` drift hook, while the appendix file alone fully covers the "matched but skipped by the command, exit 0, 0-linted summary" property (`summary: linted=0 failed=0 skipped=1 excluded=0`).

#### 2026-10-29T16:21:21.875Z - Phase 110: the REQ-011 scan excludes bytecode caches; the missing-extra guard is pinned in a fresh interpreter

Two test-mechanics decisions beyond the plan and the orchestrator rulings, both scoped to this feature's test module: (1) the REQ-011 no-sweep-on-the-commit-path scan covers every source file under `tests/` but excludes the `__pycache__` bytecode caches — a binary "line" of a compiled `.pyc` conflates constants from unrelated source lines (for example `tests/test_cli.py`'s docstring that names the command with a different line's flag tuple), producing false positives that are not invocations; a line-wise scan of the source files is what the "same command line" wording means, and the exclusion is documented in the test's own comment. (2) The missing-`mcp`-extra guard (exit 1 plus the install message) is pinned in a fresh-interpreter subprocess that blocks `mcp` and loads `commands/lint.py` from its own file: in the full test process every module of the registry-backed chain is already in `sys.modules`, so the lazily imported chain imports cleanly and the guard can never fire in-process; the subprocess is the honest simulation of a `[cli]`-only install and reuses the same load-from-file mechanics the in-process import-safety test applies (per the ruling on bypassing the package's `__init__`).

#### 2026-10-29T10:00:00.000Z - Phase 100: `--type`+`--all` combination is a usage error; pointer ids print lowercase; `linted` counts taken-on documents

Decisions made while implementing Phase 100, beyond what the plan already fixed: (1) `--type` combined with `--all` is a usage error (exit 2, "--type and --all are both sweep flags and cannot be combined"): the plan pins paths+--all as a usage error and calls paths and sweep flags "alternative modes" (REQ-004), but never pins the two sweep flags against each other; for a gate, silently narrowing a requested full sweep to one type (e.g. `specmgr lint --type feat --all` sweeping only feat) is a worse failure than an error, so the narrower flag does not win quietly. (2) The repair pointer's id for the UUID-shaped types is printed lowercased: ids are case-insensitive on read, and lowercase is the canonical form, so the printed pointer works as-is with `/repair {type} {id}` (the plan left the as-found/lowercased choice to be made consistently and documented). (3) The summary's `linted` counter counts the documents the gate took on (a parse was attempted — including a UTF-8 decode failure, which is a per-file parse failure, exit 1, per Task 100.110's "decode errors per file", and NOT one of REQ-008's exit-2 "unreadable or missing path" cases, which mean an OSError on a user-named path), and `failed` is the subset of `linted` that raised; in path mode, `linted + skipped + excluded` partitions every given path.

#### 2026-10-29T09:00:00.000Z - Third refinement: import-safe `--type`, per-type repair pointer, pinned exclusion rule, one shared file pattern

Decisions made while amending the plan after the third refinement pass: (1) `--type` is declared as a plain optional `str` and validated against ALL_DOMAINS inside the lazily imported command body (an unknown value is a usage error, exit 2), because deriving Typer `choices` from ALL_DOMAINS at import time would force a module-level import of the registry, and `cli.py` imports every commands/\* module at module level, so every CLI command (incl. `specmgr version`) would crash in a `[cli]`-only install, the exact failure issue #238 describes; the "derived, never hand-listed" property is therefore pinned by a test (runtime acceptance set equals ALL_DOMAINS; no hand-listed type literal; lint.py has no module-level import of the registry) instead of by Typer choices. (2) The repair pointer is per type: whole-body domains get `/repair {type} {id}` with the id derived from the path (the folder name for feat, the canonical UUID embedded in the file name for the others), falling back to `/repair {type}` when no id can be derived; ADR gets a "not covered by the repair flow, fix manually" line instead, since the repair flow is whole-body-only. (3) The ADR README exclusion rule is exactly: the resolved type is adr (inferred or via `--type adr`) and the file's base name is `README.md`; it is type-specific, so `feat/{id}/README.md` stays a feat artifact. (4) One shared file pattern, the anchored hook regex, is used by both the hook and the CI step (the CI filter was previously the broader "any .md under .specmgr/ and docs/", which would also match the evidence files under .specmgr/feat/\*/evidence/); a drift test pins that the two are identical. (5) The summary gains an `excluded` counter next to linted/failed/skipped. (6) A path-mode run in which every path is skipped or excluded exits 0 with a 0-linted summary. (7) Healthy fixtures for all 13 types come from the packaged `get_<d>_example` data (ADR from a minimal rendered or copied ADR), each verified to parse. (8) The per-file exception set reuses the repo's existing parse-failure tuple (`_CAUGHT_EXCEPTIONS`, plus AdrParseError and decode errors) instead of re-listing it. (9) The accepted schema-change limitation gets an owner: a Phase 150 task opens the follow-up issue for the nightly `specmgr lint --all` workflow.

#### 2026-10-29T06:21:00.000Z - Appendix classification and CLI edge-case semantics (second refinement)

Decisions made while amending the plan after the second refinement pass: (1) The issue #86 sysrs appendix (docs/sysrs/sysrs-8d752304-...-appendix.md, commit bca1a87) is generated documentation, not a sysrs artifact: it is a manual verbatim concatenation of 24 referenced artifacts with no frontmatter of its own, and it cannot satisfy the sysrs schema (its H1 is not the required "System Requirements Specification: ..." heading, independent of the single raw-HTML token it also carried). Repairing it in place was rejected as infeasible by design; moving it to docs/appendix/ (out of the scanned sysrs base directory) was chosen over a lint-command exclusion, because the move keeps the invariant that every file in a domain directory is a parseable document true for list_sysrs, the reference-graph builders and similarity search alike, with no permanent special case in the gate. (2) `--type T` against an empty or missing base directory exits 0 with a 0-document summary: a registered-but-empty domain is not a misconfiguration, in contrast to `--all` finding zero documents in total (exit 2, unchanged). (3) Explicit paths and a sweep flag are alternative modes; combining paths with `--all` is a usage error (exit 2). `--type` remains legal with paths, where it overrides inference (REQ-005). (4) The docs/adr/README.md exclusion (REQ-007) is unconditional, in path mode and sweep mode, with or without `--skip-unrecognized`; the file is reported as excluded, never parsed or failed (ACC-005 rewritten to pin exactly that).

#### 2026-10-26T07:58:00.000Z - Change-scoped gate via a new lint command (supersedes the earlier planning decisions)

Decisions made while revising the plan: (1) Scope: pre-commit validates every staged specmgr artifact, CI validates every artifact changed on a pull request, and the full corpus is checked only through the CLI by type or `--all` (also the later nightly path); a full sweep in the suite or hook was rejected because it cost about 124 s and grows with the corpus. (2) Command name `lint` (not `check`, which collides with the plantuml-check family). (3) All artifact types are covered, including ADR (reusing the pure parse_adr parser with AdrParseError also caught); the `--type` set derives from ALL_DOMAINS. (4) Type inference from the path layout alone (environment-independent), `--type` as the fallback; sweep mode honors the SPECMGR\_\*\_DIR variables, `--dir` overrides. (5) Schema changes may break unchanged documents, which is accepted (breaking changes are kept to a minimum). (6) The command requires the mcp extra like `diagram`; relocating the registry is deferred to issue #238, which will need its own ADR. (7) CI step included in this feature (changes the workflow); the nightly workflow is deferred. (8) Still no ADR for this feature itself. Supersedes the earlier planning decisions (corpus = FEAT only, gate = suite test + hook, no workflow change).

#### 2026-10-26T05:42:45.913Z - Planning decisions (issue #218)

Four planning decisions made while drafting this feature: (1) Corpus = feature plans only; the ADR corpus carries the same defect class but was recorded as a follow-up candidate; (2) Gate = suite test + scoped pre-commit hook, per ADR 9c687bb1's "locally via pre-commit hook, not just CI"; (3) No ADR; the decisions stay feature-level; (4) Title/id = "In-Tree Spec Artifact Parseability Gate" / feat-218-in-tree-spec-artifact-parseability-gate. Decisions (1) and (2) were superseded by the 2026-10-26T07:58:00.000Z entry.

### Related PRs / Commits

- Issue #218: https://github.com/dfch/biz.dfch.SpecMgr/issues/218 — the tracking issue for this feature.

- Issue #238: https://github.com/dfch/biz.dfch.SpecMgr/issues/238 — follow-up: decouple the pure path and parse logic from the eager tools packages so CLI commands work in a `[cli]`-only install.

- PR #216: https://github.com/dfch/biz.dfch.SpecMgr/pull/216 — feat-214, the follow-up that recorded issue #218.

- Commits f578e69 through 6714117 — the three consecutive commits in which feat-214's own plan document shipped unparseable (the demonstration case).

### More Information

How the defect hid (three symptoms, all observed on feat-214's plan): (1) list_feat reported the document healthy throughout, because its request path resolves each folder from a frontmatter+H1-only dirty-stage parse, exactly the masking the dirty/clean two-stage design documents (ADR 3982712a); (2) the reference-graph builders' full-parse scan legs silently skipped the document (rulebook §3.4), dropping feat-214 from every live diagram, a symptom noticed only during the Phase 130 CLI walkthrough; (3) CI runs the test suite, but no test or step runs a full parse over the repo's own in-tree documents. Cost: a serial full parse of the feature corpus measured about 124 s for 89 documents at refinement time, which is why the gate is change-scoped and the full sweep is CLI-only. Note: .specmgr/conventions.md and the .specmgr/conventions/ directory are hand-authored documentation, not specmgr-managed artifacts; they are outside the lint layouts by construction. Likewise docs/api/ and docs/GENERATED.md are generated documentation, not artifacts, docs/adr/README.md is the generated ADR table of contents, and the issue #86 sysrs appendix (moved to docs/appendix/ on 2026-10-29, see the Decisions Made entry of the same date) is a manually generated verbatim concatenation of 24 referenced artifacts, not a sysrs document. Corpus verification baseline: a full-parse sweep over all 13 types (2026-10-29, after the move) found 161 documents and 0 failures (158.4 s serial); the one-time cost measurement of about 124 s for the then-89 feature READMEs (Design Notes) remains the basis for the change-scoped design. Sibling-class framing: feat-214 fixed a gate that existed but was env-gated and unconfigured on the commit path (the PlantUML real-parser); this feature fixes the case where the gate does not exist at all.
