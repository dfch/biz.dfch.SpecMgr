---
created: '2026-11-04T13:19:09.333+01:00'
id: feat-0-harness-bundle-sop
status: done
type: feat
updated: '2026-11-04T13:55:31.532+01:00'
version: 1.0.0
---

# Feature: Document the harness-bundle add/change procedure as an SOP

## Plan

### Overview

The harness bundle feature (feat-167-mcp-lifecycle-commands-2, Phase 130)
packages every markdown file under `.opencode/{agent,command,skill}/` into
`src/biz/dfch/specmgr/general/data/general_harness_bundle.json`, which the
`specmgr://harness-bundle` MCP resource serves verbatim; an agent in a
consumer's harness installs those files per the bundle's install protocol.
There is no documented end-to-end procedure for adding or changing a bundled
file, and it carries a non-obvious trap: the count-pin test in
`tests/commands/test_harness_bundle.py` must be updated in the same commit as
the file change, or the pre-commit hook, the CI parity step, and the test
suite fail. This feature records the procedure as a single SOP in `docs/sop/`
(status `draft`) covering all three harness file kinds. Per the user's
decision, no AGENTS.md pointer is added and nothing is committed (the branch
is shared with another agent).

### Requirements

- REQ-001: Exactly one SOP titled "Add or change a harness file (skill, command, or agent) in the specmgr harness bundle" is created in `docs/sop/` with frontmatter `status: draft`, a fresh tool-assigned UUID `id`, and a body matching the approved verbatim draft recorded in Design Notes (the only substitution being the `## Updates` "Created" heading timestamp, set at execution time).

- REQ-002: The SOP is created through the `create_sop` MCP tool (body-only content, no frontmatter); a non-raising `ValidateResult` (`valid: false`) is fixed per its `errors[].message` and retried — nothing is written on a failure.

- REQ-003: The SOP parses and lists healthy: `get_sop(id)` returns a structured document (not a parse-failure result), `list_sop` shows a healthy row (no `<failed to parse>` marker, `error_count` 0), and `uv run --frozen --all-extras specmgr lint <file>` exits 0.

- REQ-004: No file is changed besides the new SOP (and this plan folder): no AGENTS.md change, no code or test change, no bundle regeneration (this feature adds no harness files itself), and no git commit or staging.

### Acceptance Criteria

- [ ] ACC-001: for REQ-001 — `list_sop` shows exactly one new row with the title above, `status: draft`, and a path of `docs/sop/sop-<uuid>-add-or-change-a-harness-file-skill-command-or-agent-in-the-specmgr-harness-bundle.md` (the slug derived from the H1 by the tool).

- [ ] ACC-002: for REQ-002 — the `create_sop` call returns the created document's frontmatter (not a `ValidateResult`), with an `id` that is a fresh UUID not held by any existing SOP.

- [ ] ACC-003: for REQ-003 — `get_sop(id)` parses with every section of the approved draft present (Purpose, Scope, Definitions, Roles and Responsibilities with Accountable + Responsible, Safety and Precautions, the eight-step Procedure, the Related Artifacts bullet for the release SOP, More Information, Updates with the Created entry) and `specmgr lint` exits 0.

- [ ] ACC-004: for REQ-004 — `git status` shows only the new untracked SOP file and this feature folder; `git diff` is empty (no modified tracked file); `git log` shows no new commit.

### Scope

#### Included

- This plan artifact (`.specmgr/feat/feat-0-harness-bundle-sop/README.md`).

- The SOP document itself, its body fixed by the approved verbatim draft recorded in Design Notes.

- Read-only verification of the created SOP (parse, list, lint).

#### Explicitly Out Of Scope

- An AGENTS.md pointer to the SOP (explicitly rejected by the user; SOP only).

- Designing the content of a specific new skill, command, or agent (the SOP's reader's job at execution time).

- Bundling non-markdown assets (the enumeration carries `*.md` only — a design gap to record, not a task of this feature).

- Releasing the harness bundle feature (feat-167 is on `dev`, unreleased; the release is the release SOP's domain).

- Executing the SOP for a real new harness file (the SOP documents the procedure for future runs).

### Dependencies

#### Depends On

- feat-167-mcp-lifecycle-commands-2 Phase 130 (harness bundle): the `specmgr harness-bundle` command, the `specmgr-harness-bundle` pre-commit hook, the CI parity step, and the count-pin test — all already present on this `dev` branch.

- The SOP precedents `sop-81d73e92-ed9c-44a8-a475-9256a88cfd6a` (Convert an ADR to a DEC) and `sop-98537416-0e6e-4a02-925f-974a17bfa10a` (Perform a release of biz.dfch.SpecMgr) as structural model and cross-reference target.

#### Blocks

- Nothing.

### Design Notes

Document-type choice — why an SOP:

- **Rejected: an OpenCode skill.** Everything under `.opencode/{agent,command,skill}/` is enumerated into the bundle automatically and shipped into consumers' harnesses with the next PyPI release; a maintainer-only procedure would leak into user installs.
- **Rejected: AGENTS.md alone.** AGENTS.md already documents the mechanism (the CLI entry, the hook, the CI parity step) but is the wrong place for a gated, step-by-step procedure, and the user chose SOP only.
- **Rejected: DEC / txt.** A DEC records a decision, not a procedure; txt is less structured and less discoverable than `list_sop`.
- **Chosen: SOP** — with direct precedent: "Convert an ADR to a DEC" is an agent-executable maintainer-workflow SOP with purpose/scope/definitions/RASCI/safety/steps-with-gates/updates.

SOP schema facts (verified against `get_sop_schema` before drafting): the
mandatory body sections are `## Purpose` and `## Procedure` (at least one
`### Step {N}: {name}`); `## Updates` is optional but, if present, last, with
at least one newest-first entry whose heading is
`### {full ISO 8601} ( - | : ) {title}` (an em-dash separator is rejected);
`create_sop` writes a fresh EN SOP with `status: draft`. An SOP has no
`## Source` section (a DEC/RSK concept).

Execution contract: one `create_sop` call (body-only), the read-back
verifications, no commit. Because the branch is shared with another agent,
the change must stay purely additive.

The approved verbatim SOP body (the single source of truth for the
implementation; the `{current full ISO 8601 timestamp}` placeholder in the
`## Updates` "Created" heading is substituted at execution time with the full
ISO 8601 date+time in milliseconds and an explicit offset, the ` - `
separator):

```markdown
# Add or change a harness file (skill, command, or agent) in the specmgr harness bundle

## Purpose

Document the end-to-end procedure for adding, changing, or removing a markdown
harness file under `.opencode/{agent,command,skill}/` so the change is
reflected deterministically in the packaged
`src/biz/dfch/specmgr/general/data/general_harness_bundle.json` (served verbatim
by the `specmgr://harness-bundle` MCP resource) and passes every drift gate:
the `specmgr-harness-bundle` pre-commit hook, the CI parity step, and the
count-pin test.

## Scope

This SOP covers creating, modifying, or deleting `*.md` files in the scoped
directories; regenerating the bundle; updating the count-pin test; the
verification gates; and the commit.

Out of scope: designing the content of a new skill, command, or agent itself;
non-markdown assets (the enumeration bundles `*.md` only, nothing else ships);
changing the install protocol (the `INSTRUCTIONS` constant in
`commands/harness_bundle.py` is a code change); publishing the package to PyPI
(the release SOP); optional host-surface pin tests under `tests/opencode/`.

## Definitions

- **Harness file**: a markdown file under `.opencode/agent/`,
  `.opencode/command/`, or `.opencode/skill/` that the bundle carries and that
  a consumer-side agent installs into its own harness configuration root per
  the bundle's install protocol.
- **Scoped directory**: one of the exact, singular top-level directory names
  `agent/`, `command/`, `skill/` under `.opencode/` (exact match, nothing else
  under `.opencode/` is bundled). `skill/` holds one subfolder per skill;
  `agent/` and `command/` hold flat files.
- **Bundle**: `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` —
  the single committed package-data file of shape `{"instructions": <module
  constant>, "files": [{"path", "sha256", "content"}]}`, generated
  deterministically (sorted by `.opencode/`-relative path, no timestamps) and
  served verbatim by the `specmgr://harness-bundle` resource.
- **Count pin**: the test
  `tests/commands/test_harness_bundle.py::TestGenerateBundleTextCurrentTree.
  test_current_tree_enumerates_exactly_N_files`, which pins the total number of
  bundled files of the current repo tree and the per-directory counts.
- **Drift**: the committed bundle differing from a fresh in-memory generation
  over the current `.opencode/` tree; the pre-commit hook and the CI parity
  step fail on drift.
- **Stray file**: a `*.md` file at the `.opencode/` top level or under a
  non-scoped directory — warned on stderr, never bundled.

## Roles and Responsibilities

### Accountable

dfch

### Responsible

- the agent executing this SOP (OpenCode)
- the human reviewer confirming the layout and content of the new harness file

## Safety and Precautions

- Only `*.md` files are bundled. A harness file that depends on non-markdown
  assets (scripts, data files) cannot ship via the bundle — stop and record the
  gap; do not improvise.
- Never place maintainer-only or internal files in the scoped directories:
  everything there is shipped into consumers' harnesses with the next release.
- The directory names are singular and exact: a misspelled sibling (e.g.
  `skills/`) becomes a stray directory — warned, never bundled, and invisible
  to the bundle otherwise.
- Never hand-edit the bundle JSON: it is generated byte-deterministically; all
  changes go through `specmgr harness-bundle`.
- The count pin must be updated in the same commit as the harness file change;
  otherwise the pre-commit hook, the CI parity step, and the test suite fail.

## Procedure

### Step 1: Create, change, or remove the harness file

- **Skill**: `.opencode/skill/<skill-name>/SKILL.md` — one subfolder per
  skill; the frontmatter carries `name` and `description` (the OpenCode
  skill-discovery convention, e.g.
  `.opencode/skill/translation-status/SKILL.md`); additional `*.md` assets in
  the folder (e.g. `references/*.md`) are bundled too, recursively.
- **Command**: `.opencode/command/<name>.md` (flat).
- **Agent**: `.opencode/agent/<name>.md` (flat).

The file must be decodable as UTF-8 — a non-decodable scoped file is a usage
error of the generator (exit 2, nothing written).

### Step 2: Regenerate the bundle

From the repo root: `uv run --frozen specmgr harness-bundle`. Exit 0 on
success with a summary line (file count, bytes, output path). The generator
warns on stderr for every stray markdown file outside the scope.

### Step 3: Update the count pin

In `tests/commands/test_harness_bundle.py`,
`test_current_tree_enumerates_exactly_N_files`: bump the total file count and
the per-directory counts (`{"agent": A, "command": C, "skill": S}`) by the
markdown files added or removed; rename the test method if its `N` prefix
changed. Optionally update the count stated in the module docstring (it is
already stale — the pin is the assertion, not the docstring).

### Step 4: Gate 1 — no drift

Re-run `uv run --frozen specmgr harness-bundle` and
`git diff --exit-code -- src/biz/dfch/specmgr/general/data/general_harness_
bundle.json`; both must be clean (generation is idempotent; the on-disk tree
and the committed bundle agree).

### Step 5: Gate 2 — tests

`uv run --frozen pytest tests/commands/test_harness_bundle.py
tests/general/resources/test_harness_bundle.py` — green (count pin, committed-
bundle drift pin, resource test).

### Step 6: Gate 3 — lint

`uv run --frozen ruff format --check && uv run --frozen ruff check` (Step 3
touched Python).

### Step 7: Commit

Stage the harness file(s), the regenerated bundle, and the test change
together and commit. The `specmgr-harness-bundle` pre-commit hook (files
pattern `^\.opencode/(agent|command|skill)/.*\.md$`) regenerates on commit; if
it fails on diff, stage the regenerated bundle and commit again. The CI parity
step (Python 3.13-pinned) enforces the same.

### Step 8: Record deviations

If any rule required a judgment call (an applied default, a layout exception),
prepend a newest-first entry to this SOP's own `## Updates` recording the file
affected and the rule applied.

## Related Artifacts

### Sops

- SOP 98537416-0e6e-4a02-925f-974a17bfa10a: Perform a release of biz.dfch.SpecMgr

  The bundle ships with the next release; a harness file added per this SOP
  reaches consumers only after it.

## More Information

Mechanics live in `src/biz/dfch/specmgr/commands/harness_bundle.py`
(`_SCOPED_DIRS`, the `INSTRUCTIONS` install protocol, `generate_bundle_text`),
the `specmgr://harness-bundle` resource in `general/resources/`, the
`specmgr-harness-bundle` hook in `.pre-commit-config.yaml`, the 3.13-pinned CI
parity step in `.github/workflows/ci.yml`, and the AGENTS.md CLI section. The
harness bundle (feat-167-mcp-lifecycle-commands-2, Phase 130) is on `dev` and
not yet released. Harness files with repo-side contracts may optionally carry
pin tests under `tests/opencode/` (precedents: `test_skill_uc_diagram.py`,
`test_skill_feat_numbering.py`).

## Updates

### {current full ISO 8601 timestamp} - Created

Drafted to document the add/change/remove procedure for the files bundled by
`specmgr harness-bundle`, after the question of how a new skill becomes part
of the `specmgr://harness-bundle` resource; the count-pin test update (Step 3)
is the non-obvious trap the procedure encodes.
```

### Related Decisions

- feat-167-mcp-lifecycle-commands-2 (Phase 130): the harness bundle and its install protocol — the subject the SOP documents.

- sop-98537416-0e6e-4a02-925f-974a17bfa10a (SOP): Perform a release of biz.dfch.SpecMgr — cross-referenced from the new SOP's Related Artifacts.

### Task List

#### Phase 100: Create the SOP

- [x] Task 100.100: Assemble the SOP body from the verbatim draft in Design Notes; substitute the `{current full ISO 8601 timestamp}` placeholder in the `## Updates` "Created" heading with the execution-time timestamp (full ISO 8601, milliseconds, explicit offset, the ` - ` separator).

- [x] Task 100.110: Call `create_sop` with the body (no frontmatter). If it returns the non-raising `ValidateResult` (`valid: false`), fix per `errors[].message` and retry until the created document's frontmatter is returned; record the assigned UUID.

- [x] Task 100.120: Verify: `get_sop(id)` parses with `status: draft` and every draft section present; `list_sop` shows a healthy row (`error_count` 0); `uv run --frozen --all-extras specmgr lint docs/sop/<file>` exits 0.

- [x] Task 100.130: Verify no side effects: `git status` shows only the new untracked SOP file and this feature folder; `git diff` is empty; no new commit in `git log`.

- [x] Task 100.140: Report the SOP's `id` and path to the user, and stop — do not commit and do not stage (the user's explicit instruction).

## Progress

### Current Status

**As of 2026-11-04**: done. The SOP was created via `create_sop` with the
verbatim approved body; assigned id `f772476e-16a3-498e-9002-6a93ade787f8`,
`status: draft`, file
`docs/sop/sop-f772476e-16a3-498e-9002-6a93ade787f8-add-or-change-a-harness-
file-skill-command-or-agent-in-the-s.md`. All verification gates passed
(`get_sop` parsed with every section present, `list_sop` healthy row with
`error_count` 0, `specmgr lint` exit 0) and the side-effect check confirmed a
purely additive footprint with no new commit (nothing was committed, per the
user's instruction).

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-04 13:55:31.532+01:00 - SOP created and verified

`create_sop` wrote the SOP with the verbatim approved body (the only
substitution: the `## Updates` "Created" heading timestamp
`2026-11-04T13:53:22.689+01:00`); assigned id
`f772476e-16a3-498e-9002-6a93ade787f8`, `status: draft`. All Task 100.120
gates passed (parse, list, lint exit 0); Task 100.130 confirmed no side
effects and no commit.

#### 2026-11-04 13:19:09.333+01:00 - Created

Drafted after the user's question about what it takes to add a new skill to
the `specmgr://harness-bundle` resource. The session established the procedure
(file layout, `specmgr harness-bundle` regeneration, the count-pin test
update, the drift/test/lint gates, the commit) and the documentation form: one
SOP covering all three harness file kinds, status `draft`, no AGENTS.md
pointer, no commit (the branch is shared with another agent). The approved
verbatim SOP body is recorded in Plan → Design Notes.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-04 13:19:09.333+01:00 - Document as an SOP, not as a skill or an AGENTS.md section

Everything under `.opencode/{agent,command,skill}/` is bundled automatically
and shipped into consumers' harnesses, so a maintainer-only procedure cannot
be a skill; AGENTS.md already documents the mechanism, and the user chose SOP
only. The SOP domain carries direct precedent for an agent-executable
maintainer workflow ("Convert an ADR to a DEC").

#### 2026-11-04 13:19:09.333+01:00 - Cover all three harness file kinds; status draft; no commit

The user confirmed: scope is agent/command/skill (the mechanics are identical
for all three and the count-pin trap applies to any of them), the SOP is
created with `status: draft`, and the work is not committed.

### Related PRs / Commits

- None yet.

### More Information

Mechanics referenced by the SOP: `src/biz/dfch/specmgr/commands/
harness_bundle.py` (`_SCOPED_DIRS`, `INSTRUCTIONS`, `generate_bundle_text`),
the `specmgr://harness-bundle` resource (`general/resources/`), the
`specmgr-harness-bundle` hook in `.pre-commit-config.yaml`, the
Python 3.13-pinned CI parity step in `.github/workflows/ci.yml`, the count-pin
test in `tests/commands/test_harness_bundle.py`, the resource test in
`tests/general/resources/test_harness_bundle.py`, and the AGENTS.md CLI
section.
