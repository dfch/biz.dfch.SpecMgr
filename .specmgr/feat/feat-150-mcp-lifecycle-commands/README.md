---
classification: null
created: '2026-09-23 23:16:12.456+02:00'
id: feat-150-mcp-lifecycle-commands
status: planning
type: feat
updated: '2026-09-25 01:59:26.385+02:00'
version: 1.0.0
---

# Feature: MCP-Native Feature-Lifecycle Commands (make_valid, refine_feat, implement_feat, review_feat) + OpenCode Distribution

## Plan

### Overview

GitHub issue #150 asks for five related capabilities that round out the feature/document lifecycle already partially covered by ad hoc OpenCode-only files: (1) a command that repairs an artifact that currently fails to parse, (2) a portable, MCP-native version of the OpenCode-only `implement_feature` workflow, (3) an automatic post-implementation review-and-fix-phase follow-up, (4) a pre-implementation plan-refinement command, and (5) an easy way to get these OpenCode-native commands onto a fresh OpenCode install (and guidance for other hosts, e.g. Claude Code).

The unifying design principle (see Design Notes) is: every new capability gets a **portable MCP prompt** (narration-only text, works in any MCP host, following the existing `create_*`/`update_*`/`implement_task`/`refine`/`compact_history` precedent) *and*, where real file-editing/iteration/multi-agent delegation is required, a **richer OpenCode-native subagent + command** with real permission enforcement (mirroring the existing `phase-orchestrator`/`phase-implementer`/`feat-reviewer`/`ref-finder` precedent). The portable prompt narrates delegation via the *host's own* subagent-delegation tool (e.g. OpenCode's `task` tool) when available, exactly like every existing prompt already narrates host-native tools it doesn't implement itself (`question`, `TodoWrite`) -- it degrades to direct single-session implementation when no such tool exists.

**Phase ordering is deliberately make_valid-first**: `make_valid` (Phase 1) has no dependency on the ADR that Phase 4 (implement_feat/review_feat) needs, so it can be implemented, tested, and shipped standalone before any other phase.

**Phase discipline (user requirement, 2026-09-24)**: every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the phase's docs sync travels inside that same commit (see Design Notes, and the phase-end gate task at the end of every phase in the Task List).

### Requirements

- REQ-001: A new `general/prompts/make_valid.py` MCP prompt, signature `make_valid(type, id=None)`, narrates discovering a failed-to-parse document (with `id`: confirm via `get_<d>(id)`'s wrapped parse error; without `id`: scan `list_<d>()` for the failed row, whose `title`/`status` carry the `<failed to parse>` marker and whose `id` is null while `ref`/`path`/`error` are populated), reading the raw file via the host's own file-read tool (no MCP tool can return raw content of a document that fails to parse: `get_<d>(raw=True)` and the generic `update` both re-parse the existing document first, and `update`'s per-domain adapters convert that failure into the domain's not-found error before any write), fixing only what the enriched error addresses while preserving the frontmatter `id`/`created`/`status`/`version` byte-for-byte (and leaving `updated` untouched -- a repair is not an edit), looping the generic `validate(type, content, full=True)` tool over the full raw text until green, and writing the repaired full text back to the same path via the host's own file-write tool -- explicitly NOT via the generic `update` tool, which is structurally unable to repair a document that fails to parse; when the host has no file read/write tools the prompt degrades to diagnose-only (report the error and the proposed fix, touch nothing); `type` is one of the 12 whole-body domains -- ADR is explicitly out of scope (it has no generic `validate`/`parse` tooling).

- REQ-002: A new `.opencode/agent/doc-fixer.md` subagent implements REQ-001's loop with real file access, declaring every permission it relies on explicitly: `read`/`glob`/`grep`/`list`/`question`/`todowrite` allowed, `edit`/`write` allowed workspace-wide (the broken document may live under any domain base directory), `task` denied, `bash` denied -- plus a `.opencode/command/make-valid.md` (`/make-valid <type> [id]`, `$1`/`$2` positionals, `agent: doc-fixer`) wrapper.

- REQ-003: A new `feat/prompts/refine_feat.py` MCP prompt, signature `refine_feat(id)`, narrates a pre-implementation plan-readiness review (testable ACs, phase ordering/dependencies, scope clarity, unresolved decisions) that is fully MCP-native: read via `get_feat(id, raw=True)`, ask the user via the `question` tool, apply edits via the generic `update(type="feat", id, content, offset/limit)` tool (line-range preferred), and re-check via `validate(type="feat", content, full=True)` -- host file tools only as a fallback when those specmgr tools are unavailable.

- REQ-004: A new `.opencode/agent/feat-planner.md` subagent implements REQ-003 with real file access, with its plan-README-only edit scope enforced mechanically rather than by prose: `edit`/`write` permission rules `{"*": deny, ".specmgr/feat/**/README.md": allow}` (OpenCode's `edit` permission patterns match file paths, last matching rule wins), `read`/`glob`/`grep`/`list`/`question`/`todowrite` allowed, `task` denied, `bash` denied -- plus `.opencode/command/refine-feature.md` (`/refine-feature <id>`, `agent: feat-planner`).

- REQ-005: A new `feat/prompts/implement_feat.py` MCP prompt narrates orchestrator discipline (read plan, phase-by-phase `TodoWrite`, delegate each phase via the host's subagent-delegation tool when available, verify before advancing, never write code directly), names the Phase 3 ADR by UUID, mentions the REQ-008 review-fix loop, and falls back to direct single-session implementation when no delegation tool exists.

- REQ-006: A new `feat/prompts/review_feat.py` MCP prompt narrates `feat-reviewer.md`'s existing review checklist and report format portably, including the new conditional "Proposed Fix Phase" section (REQ-007).

- REQ-007: `.opencode/agent/feat-reviewer.md`'s report format gains a new, conditional "Proposed Fix Phase" section: a ready-to-paste block for the plan's `### Task List` -- a `#### Phase N: Fix phase (review cycle k)` heading using the next unused phase number (never renumbering existing phases) plus `- [ ] Task N.M` items derived strictly from the report's own Errors/Gaps/Inconsistencies (Code Smells/Improvements/Positives stay advisory), with any item that needs a user decision explicitly flagged `[NEEDS DECISION]` rather than guessed at.

- REQ-008: `.opencode/agent/phase-orchestrator.md` (and `implement_feat`'s narration, REQ-005) gain a final review-fix loop: after the plan's final verification phase, run the reviewer; if it proposes a fix phase, resolve any `[NEEDS DECISION]` items with the user via `question`, then delegate the fix phase to one more `phase-implementer` cycle exactly like a normal phase -- with the delegation prompt instructing the implementer to first append the reviewer's ready-to-paste block to the plan's Task List, since the orchestrator itself cannot edit files (`edit`/`write` are denied to it); repeat until the reviewer reports no Errors, Gaps, or Inconsistencies left, capped at 3 review-fix cycles (after which remaining findings are handed to the user instead of auto-fixed again).

- REQ-009: The repo-root `.opencode/{agent,command}/*.md` files remain the canonical working copy; a generated package copy under `general/data/opencode/{agent,command}/` ships in the wheel, produced by a new `specmgr opencode sync` CLI stage, kept in sync by a new pre-commit local drift hook (sync, then fail on diff -- mirroring the existing `specmgr-schema-*` hooks) plus a CI parity check in the 3.13 job; `pyproject.toml` gains the `[tool.setuptools.package-data]` globs for the new subdirectory; the installer (REQ-010) must read the package copy via `importlib.resources`, since a CWD-relative `.opencode/` does not exist in a real, non-editable install.

- REQ-010: A new `specmgr opencode install [--global|--local] [--force]` CLI subcommand -- a nested `opencode` Typer sub-application in `commands/opencode.py` registered on `cli.py` via `app.add_typer` (the one-module-per-command convention) alongside `sync` -- copies every one of the 12 agent+command `.md` files (the 4 existing agents + 2 new agents, the 4 existing commands + 2 new commands; the new commands' dependency closure needs the existing agents) from the package copy to `~/.config/opencode/` (global) or `./.opencode/` (local), into the target's existing `agent(s)/`/`command(s)/` sibling directory when one exists (OpenCode accepts both singular and plural) and into singular `agent/`+`command/` otherwise; per file: identical content is a silent no-op, differing content is refused (listing the files) unless `--force`; the command never reads or writes `opencode.json` (MCP server configuration stays the README's job) and prints a reminder pointing at the README's "Add to OpenCode" section.

- REQ-011: README.md gains a new section placed immediately after the existing "Add to OpenCode" section (which it references for MCP server setup rather than duplicating): the CLI installer (usage, what gets copied, target semantics) plus the manual/Claude-Code path -- Claude Code's structurally similar `.claude/agents/*.md`/`.claude/commands/*.md` convention is called out explicitly with a short hand-ported frontmatter example, along with the permission-model gap (OpenCode's per-pattern bash/edit rules vs. Claude Code's coarse tool allow-list) that means these are hand-ported, simplified equivalents, not an automatic translation.

### Acceptance Criteria

- [ ] ACC-001: `make_valid(type, id=None)` MCP prompt exists, is registered, and its instructions name `list_<d>`'s failed-row discovery and `get_<d>`'s failure confirmation, direct the raw read and the write-back at the host's own file tools with an explicit note that the generic `update` tool cannot repair a document that fails to parse, loop the generic `validate(type, content, full=True)` tool, state the diagnose-only degradation, and state the ADR exclusion.

- [ ] ACC-002: `/make-valid <type> <id>` successfully drives `doc-fixer` to repair a deliberately-broken fixture document (parse fails before, succeeds after) in a manual smoke test.

- [ ] ACC-003: `refine_feat(id)` MCP prompt exists, is registered, and its instructions name `get_feat(id, raw=True)`, the generic `update` tool (`type="feat"`), and `validate` (`type="feat"`, `full=True`) as the read/apply/re-check path.

- [ ] ACC-004: `/refine-feature <id>` successfully edits a fixture plan's README in place after a manual smoke test.

- [ ] ACC-005: `implement_feat(id)` MCP prompt exists, is registered, and its instructions explicitly name the host's task-delegation tool as optional (never assumed present), the Phase 3 ADR by UUID, and the review-fix loop.

- [ ] ACC-006: `review_feat(id)` MCP prompt exists, is registered, and mirrors `feat-reviewer.md`'s checklist and report format including the conditional "Proposed Fix Phase" section.

- [ ] ACC-007: `feat-reviewer.md`'s report format documents the "Proposed Fix Phase" section -- the ready-to-paste Task-List block shape (next unused phase number, `- [ ] Task N.M` items derived from Errors/Gaps/Inconsistencies only) and the `[NEEDS DECISION]` flagging rule.

- [ ] ACC-008: `phase-orchestrator.md`'s workflow documents the capped (3-cycle) review-fix loop, its exit criterion (reviewer reports no Errors, Gaps, or Inconsistencies), and the append-the-fix-phase delegation step (the implementer appends, not the orchestrator).

- [ ] ACC-009: The package copy under `general/data/opencode/` is byte-identical to the repo-root `.opencode/{agent,command}/` (the drift hook is green), and the installer sources its files exclusively from the package copy via `importlib.resources`.

- [ ] ACC-010: `specmgr opencode install --local` and `--global` both copy every one of the 12 agent+command files to the target location (existing `agent(s)/`/`command(s)/` sibling detected, singular default), are silent no-ops for identical files, refuse differing overwrites without `--force`, and are covered by unit tests.

- [ ] ACC-011: README.md has the new section immediately after "Add to OpenCode", documenting the CLI installer (referencing that section for server setup) and the manual Claude Code path.

- [ ] ACC-012: `AGENTS.md` (the `general/` and `feat/` bullets), `docs/GENERATED.md`/`docs/MCP.md` (via `specmgr docs`/`specmgr mcp-docs` regeneration), `CHANGELOG.md`, and `server.py`'s module docstring list the 4 new MCP prompts and the new `specmgr opencode` CLI subcommand -- each synced inside its own phase's single commit.

- [ ] ACC-013: A new ADR documents the "portable MCP prompt narrates optional host-native subagent delegation" pattern.

### Scope

#### Included

- 4 new MCP prompts (`make_valid`, `refine_feat`, `implement_feat`, `review_feat`) and their packaged instruction data files.

- 2 new OpenCode subagents (`doc-fixer`, `feat-planner`) and 2 new OpenCode commands (`/make-valid`, `/refine-feature`).

- Targeted edits to the 4 existing OpenCode files: `feat-reviewer.md` (the Proposed Fix Phase section) and `phase-orchestrator.md` (the review-fix loop) for the review-fix loop, `implement-feature.md` (doc update mentioning the automatic review-fix step, plus its "a a" typo fix), and `review-feature.md` (its body re-enumerates the report sections and would go stale without the new conditional section).

- Packaging: the generated package copy under `general/data/opencode/`, the `specmgr opencode sync` stage, the pre-commit drift hook, the CI parity check, and the `pyproject.toml` package-data globs (REQ-009).

- The `specmgr opencode install` CLI subcommand + tests (REQ-010).

- The README.md section (installer + Claude Code path) + its Table of Contents entry (REQ-011).

- AGENTS.md/CHANGELOG/generated-docs/server.py-docstring updates, one per phase, inside that phase's own single commit.

- One new ADR for the portable-prompt-narrates-delegation pattern.

#### Explicitly Out Of Scope

- Any change to `.opencode/agent/phase-implementer.md`, `.opencode/agent/ref-finder.md`, `/refs`, or `/release` (unaffected).

- Any change to `general/prompts/compact_history.py` -- its docstring's claim that feature folders "have no dedicated parser/get/update MCP tools" is stale since feat-31 (the generic `update`/`get_feat` tools exist now); that is a separate small fix.

- Any read/write/merge of the user's `opencode.json` by the installer (MCP server configuration stays the README's documented job).

- Building an OpenCode plugin (`config()` hook) for zero-copy distribution -- noted as a possible future enhancement, not built now.

- Auto-generating Claude-Code-flavored `.claude/agents`/`.claude/commands` files from the OpenCode ones -- hand-ported/simplified equivalents are documented instead, given the permission-model mismatch.

- Any change to the generic `validate`/`update`/`set_status` tools themselves (REQ-001/002 build on them as-is; REQ-001's write-back is host-native precisely because `update` cannot repair a broken document).

- Enforcing any of this via pre-commit/CI (matches the repo's existing "no `validate_adr`-in-CI yet" gap, unaffected by this feature) -- except the REQ-009 package-copy drift check, which is a build-consistency gate in the same class as the existing `specmgr-schema-*` hooks, not a document-validation gate.

### Dependencies

#### Depends On

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 / c4efbde6-fd19-4aa8-8668-95316ed62dcc (dispatch-only domain convention, followed by `make_valid`'s generic shape).

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

- feat-27-validation / feat-81-83-validation (the enriched validate errors and the failed-row `list_<d>` mechanism `make_valid` builds on).

- feat-31-feature (the `feat` domain itself, whose generic `update`/`validate` adapters make `refine_feat` fully MCP-native).

- The `specmgr-schema-*` pre-commit hooks as the model for REQ-009's package-copy drift hook (the same two-copy + regenerate + fail-on-diff pattern).

- Phase 4 (implement_feat/review_feat) depends on Phase 3's new ADR (its UUID is an input to Phase 4's instruction files); Phase 1 (make_valid) deliberately does not.

#### Blocks

- None known.

### Design Notes

**Phase discipline (user requirement, 2026-09-24).** Every phase ends with the full quality gate -- `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, the full test suite `uv run --frozen pytest -n auto --cov=src --cov-report=`, plus every doc-drift check the phase touches (`specmgr docs`, `specmgr mcp-docs`, and `specmgr adr-toc` for Phase 3) -- and exactly one Conventional Commit for that phase; the phase's docs sync (server.py docstring, AGENTS.md bullet(s), CHANGELOG entry, regenerated docs) travels inside that same commit, never as a follow-up. The Task List makes this explicit with a phase-end gate task (Task N.5/N.6/N.7/N.8) at the end of every phase.

**Why `make_valid` cannot use the generic `update` for the write-back.** `update`'s per-domain adapters resolve the existing document via `load_by_id`, which fully re-parses it; a document that fails to parse converts that failure into the domain's not-found error before anything is written (`req/tools/_io.py:72-112`; every `_update_<d>` adapter in `general/tools/update.py` takes the same shape). The raw read and the raw write-back therefore must be host-native file tools -- the same precedent `compact_history` already sets (its instructions "rely entirely on the LLM's own file read/edit/write tools, not on any specmgr tool"). A host without file tools gets the diagnose-only degradation: the prompt still reports the enriched error and the proposed fix, it just cannot apply it.

**`refine_feat` is MCP-native (unlike `make_valid`).** The plan README is a parseable document, so its whole read/apply/re-check path is specmgr tooling: `get_feat(id, raw=True)`, the generic `update(type="feat", id, content, offset/limit)` (line-range preferred, so unchanged regions stay byte-identical), and `validate(type="feat", content, full=True)`. Host file tools are only a fallback for hosts that cannot reach those tools.

**Portable-prompt-narrates-delegation pattern (the item-2 resolution).** An MCP prompt never executes tool calls itself -- it returns text to whatever LLM session invoked it, exactly like every existing prompt in this codebase (`create_req` says "use the `question` tool"; neither `question` nor `TodoWrite` is implemented by this MCP server). `implement_feat`/`review_feat` extend this same precedent one step further: they narrate delegating work to a subagent via "your host's task-delegation tool, if one exists." Inside OpenCode, that's a real instruction to use the `task` tool (genuine multi-agent orchestration, since OpenCode exposes both the `specmgr` MCP tools and its own native tools in the same session). On a host with no such tool, the same text degrades to "implement it yourself, one phase at a time" -- never a hard failure. This is the subject of the new ADR (ACC-013), needed before Phase 4 but not before Phase 1.

**Prompt/agent/command text duplication is unavoidable.** OpenCode exposes MCP *tools* but not MCP *prompts* as slash commands (its MCP documentation covers tools only), so the OpenCode agent/command files cannot delegate to the packaged prompt text -- each carries its own copy of the same workflow. This duplication is accepted; keeping prompt \<-> agent \<-> command wording in sync is a standing review-checklist item (the `feat-reviewer` Consistency checklist already flags wording drift between paired artifacts).

**Review-fix loop (capped, aligned exit criterion).** Capped at 3 automatic review-fix cycles (configurable only in the prose instructions, not a hard machine limit -- these are markdown-narrated workflows, not code). The loop exits when the reviewer reports no Errors, Gaps, or Inconsistencies -- the same set REQ-007's fix phase derives tasks from (Code Smells/Improvements/Positives stay advisory), so a cycle never ends with the fix phase still re-deriving the same inconsistency. Any findings still open after 3 cycles are handed to the user instead of auto-fixed again. The orchestrator cannot append the proposed fix phase itself (`edit`/`write` are denied to it), so the fix phase's `phase-implementer` is delegated with an explicit first step: append the reviewer's ready-to-paste block to the plan's Task List (next unused phase number, no renumbering of existing phases).

**Packaging: root-canonical, generated package copy (user decision, 2026-09-24).** The wheel only ships what lives under `src/` (`pyproject.toml`'s `[tool.setuptools.packages.find] where = ["src"]` + explicit `[tool.setuptools.package-data]` globs; there is no `MANIFEST.in`), so the installable `.opencode` copy is a generated artifact under `general/data/opencode/{agent,command}/`. The repo-root `.opencode/` stays the canonical working copy; `specmgr opencode sync` regenerates the package copy from it, and a pre-commit local drift hook (sync + fail on diff, scoped to `^.opencode/(agent|command)/.*\.md$`) plus a CI parity check (3.13 job, alongside `specmgr docs`/`specmgr adr-toc`) keep the two from drifting -- the same two-copy pattern the repo already runs for the 12 packaged JSON Schema copies (the `specmgr-schema-*` hooks in `.pre-commit-config.yaml`). The installer reads the package copy via `importlib.resources` (the `_packaged_data` convention), so it works identically from an editable checkout and a real PyPI install.

**Distribution target semantics.** `specmgr opencode install` copies all 12 files (6 agents + 6 commands, existing + new) by design -- the new commands' dependency closure needs the existing agents (`/implement-feature` drives `phase-orchestrator` -> `phase-implementer`; `/refs` drives `ref-finder`). OpenCode accepts both singular and plural directory names at project and global scope (its documentation; this machine itself uses `agent/`+`command/` in-project and `agents/` globally), so the installer detects an existing `agent(s)/`/`command(s)/` sibling at the target and defaults to singular `agent/`+`command/`. Per file: identical content is a silent no-op (re-install is idempotent), differing content is refused with the file list unless `--force`. The installer never touches `opencode.json` -- MCP server setup (including the documented unsafe-bare-`uvx` caveat) stays the README's "Add to OpenCode" section's job.

**OpenCode permission model for the new agents.** `edit` permission patterns match file paths with the last matching rule winning (opencode.ai/docs/permissions), so `feat-planner`'s plan-README-only scope is mechanically enforced (`{"*": deny, ".specmgr/feat/**/README.md": allow}` on `edit`/`write`), not just prose discipline. Both new agents deny `bash` and `task` and declare every permission they rely on explicitly (`read`/`glob`/`grep`/`list`/`question`/`todowrite`), matching the existing agents' explicitness.

**Naming.** New OpenCode files: `doc-fixer.md` (agent) / `make-valid.md` (command); `feat-planner.md` (agent) / `refine-feature.md` (command). New MCP prompts follow the existing `<verb>_<domain>` convention: `general.prompts.make_valid` (cross-cutting, takes `type` + optional `id` -- shaped like `general.tools.list_references`, which is itself the id-based cross-domain generic; `general/tools/validate.py` is disk-free/id-free and is the loop's check tool, not the prompt's shape model), and `feat.prompts.refine_feat`/`implement_feat`/`review_feat`.

### Related Decisions

- New ADR (Phase 3, before Phase 4): "Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent" -- architecture-level, affects any future `<verb>_feat`-style prompt, so it gets a full ADR per this repo's own ADR-vs-feature-log convention. Its UUID is an input to Phase 4's instruction files and is recorded here once created.

- User decisions recorded in the Decisions Made log below (2026-09-24): one commit per phase with the full quality gate; the review-fix loop's exit criterion (Errors/Gaps/Inconsistencies); the root-canonical/generated-package-copy packaging strategy.

### Task List

#### Phase 1: make_valid (no ADR dependency -- implement first)

- [ ] Task 1.1: `general/data/general_make_valid_instructions.md` (host-native read/write, the explicit no-`update` note, the diagnose-only degradation, the frontmatter-preservation rule, the ADR exclusion) + `general/prompts/make_valid.py` (`make_valid(type, id=None)`) + registration in `general/prompts/__init__.py`.

- [ ] Task 1.2: `.opencode/agent/doc-fixer.md` (full explicit permission frontmatter per REQ-002) + `.opencode/command/make-valid.md` (`$1`/`$2`, `agent: doc-fixer`).

- [ ] Task 1.3: `tests/general/prompts/test_make_valid.py` (registration + template substitution, matching existing prompt test patterns).

- [ ] Task 1.4: Docs sync: `AGENTS.md`'s `general/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 1.5: Phase-end gate: full quality gate green (ruff format/check, vulture, full pytest, `specmgr docs`/`specmgr mcp-docs` drift), then exactly one Conventional Commit for the phase.

#### Phase 2: refine_feat

- [ ] Task 2.1: `feat/prompts/refine_feat.py` (`refine_feat(id)`) + `feat/data/feat_refine_instructions.md` (the MCP-native `get_feat`/`update`/`validate` path) + registration in `feat/prompts/__init__.py`.

- [ ] Task 2.2: `.opencode/agent/feat-planner.md` (path-scoped `edit`/`write` permission rules per REQ-004) + `.opencode/command/refine-feature.md` (`agent: feat-planner`).

- [ ] Task 2.3: `tests/feat/prompts/test_refine_feat.py` + manual smoke test (ACC-004).

- [ ] Task 2.4: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 2.5: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 3: ADR for portable-delegation pattern

- [ ] Task 3.1: Write the new ADR (see Related Decisions) in `docs/adr/` per the repo's ADR conventions, regenerate `specmgr adr-toc` (pre-commit hook), set its status to `accepted`, and record its UUID in this README's Related Decisions -- needed before Phase 4 (its UUID is an input to Phase 4's instruction files).

- [ ] Task 3.2: Phase-end gate: full quality gate green (including the `specmgr adr-toc` drift check), then exactly one Conventional Commit for the phase.

#### Phase 4: implement_feat + review_feat + auto fix-phase loop

- [ ] Task 4.1: `feat/prompts/implement_feat.py` + `feat/data/feat_implement_instructions.md` + registration, narrating the optional-delegation pattern from Design Notes, naming the Phase 3 ADR by UUID, and mentioning the review-fix loop.

- [ ] Task 4.2: `feat/prompts/review_feat.py` + `feat/data/feat_review_instructions.md` + registration, mirroring `feat-reviewer.md`'s checklist/report format including the conditional "Proposed Fix Phase" section.

- [ ] Task 4.3: Extend `.opencode/agent/feat-reviewer.md`'s report format with the conditional, ready-to-paste "Proposed Fix Phase" block + the `[NEEDS DECISION]` flagging rule (REQ-007).

- [ ] Task 4.4: Extend `.opencode/agent/phase-orchestrator.md`'s Workflow section with the capped review-fix loop (REQ-008: exit on no Errors/Gaps/Inconsistencies, the implementer-appends-the-fix-phase delegation step); update `.opencode/command/implement-feature.md`'s prose to mention the automatic review-fix step and fix its "a a" typo; update `.opencode/command/review-feature.md`'s body so its report-section enumeration includes the new conditional section.

- [ ] Task 4.5: Update `implement_feat`'s narration to mention the same review-fix loop, for portable-host parity.

- [ ] Task 4.6: `tests/feat/prompts/test_implement_feat.py` + `tests/feat/prompts/test_review_feat.py` + manual smoke test.

- [ ] Task 4.7: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 4.8: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 5: Distribution

- [ ] Task 5.1: `commands/opencode.py`: the `opencode` Typer sub-application with the `sync` stage (repo-root `.opencode/{agent,command}/*.md` -> `general/data/opencode/{agent,command}/` package copy) and `install [--global|--local] [--force]` (REQ-010 semantics: package-data source via `importlib.resources`, all 12 files, sibling-directory detection, per-file no-op/refuse/`--force`, no `opencode.json` touch); register via `app.add_typer` in `cli.py`; export in `commands/__init__.py`.

- [ ] Task 5.2: Generate the initial package copy; add the `pyproject.toml` `[tool.setuptools.package-data]` globs for `general/data/opencode/`; add the pre-commit local drift hook (sync + fail on diff, files `^.opencode/(agent|command)/.*\.md$`); add the CI parity check to the 3.13 job alongside the `specmgr docs`/`specmgr adr-toc` drift checks.

- [ ] Task 5.3: `tests/commands/test_opencode.py` (sync idempotence/drift detection, install copy behavior, sibling-directory detection, `--force` overwrite guard, global vs. local target resolution, package-data sourcing) + a manual `specmgr opencode install --local` smoke in a temp directory (ACC-009/ACC-010).

- [ ] Task 5.4: README.md: the new section immediately after "Add to OpenCode" (installer + manual Claude Code path per REQ-011, referencing that section for server setup) + the README Table of Contents entry.

- [ ] Task 5.5: Docs sync: `AGENTS.md`'s CLI section (the new `specmgr opencode` subcommand), `specmgr docs` regeneration (the `commands/` module in `docs/api/`), `CHANGELOG.md` entry.

- [ ] Task 5.6: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 6: Final Verification

- [ ] Task 6.1: Walk every Acceptance Criterion above (ACC-001..ACC-013) with concrete evidence.

- [ ] Task 6.2: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

## Progress

### Current Status

**As of 2026-09-24**: Plan refined after a full review pass against the codebase (see Updates): `make_valid`'s repair loop corrected to host-native file read/write (the generic `update` tool is structurally unable to repair a document that fails to parse), `refine_feat` made fully MCP-native, the old REQ-009 split into packaging (REQ-009: root-canonical + generated package copy + `specmgr opencode sync` + pre-commit/CI drift check, per user decision) and the installer command (REQ-010: all 12 files, sibling-directory detection, per-file no-op/refuse/`--force`, never touches `opencode.json`), the review-fix loop's exit criterion aligned to Errors/Gaps/Inconsistencies (per user decision), and one-commit-per-phase + full-quality-gate discipline added (per user requirement). Not yet started -- a subsequent agent/session should pick up Phase 1 first (see Task List).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-24 20:57:10.000Z - Plan refined after full review pass

Reviewed the plan against the codebase, the OpenCode docs/config schema, and issue #150's five items (all remain covered). Corrected `make_valid`'s write-back mechanism (host-native file write, not the generic `update` tool -- whose adapters re-parse the existing document and raise the domain not-found error before any write: `req/tools/_io.py:72-112`), made `refine_feat` fully MCP-native via `get_feat(raw=True)`/`update(type="feat")`/`validate(type="feat")`, split the old REQ-009 into packaging (REQ-009) and the installer command (REQ-010), aligned the review-fix loop's exit criterion with its task-derivation set (Errors/Gaps/Inconsistencies), added the ready-to-paste fix-phase block shape and the implementer-appends delegation step, extended scope to the 4th existing OpenCode file (`review-feature.md`'s stale section enumeration, plus `implement-feature.md`'s "a a" typo), added per-phase docs-sync tasks (Phases 2/4/5) and phase-end gate + one-commit tasks (all phases), moved the README section to directly after "Add to OpenCode", and renumbered the acceptance criteria to ACC-001..ACC-013.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-24 20:57:09.000Z - Phase discipline: one commit per phase, full quality gate before it

User requirement (2026-09-24): each phase is exactly one Conventional Commit, preceded by the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches), with the phase's docs sync inside the same commit. Enforced via a phase-end gate task per phase in the Task List and a Design Notes section.

#### 2026-09-24 20:57:08.000Z - Review-fix loop exits when no Errors, Gaps, or Inconsistencies remain

Chosen over "no Errors/Gaps" so the loop's exit criterion matches REQ-007's task-derivation set (a fix phase derives tasks from Errors/Gaps/Inconsistencies); Code Smells/Improvements/Positives stay advisory. The 3-cycle cap is unchanged.

#### 2026-09-24 20:57:07.000Z - Packaging: root .opencode/ canonical, generated package copy with drift check

The wheel only ships what lives under `src/`, so the installable OpenCode file copy is generated under `general/data/opencode/{agent,command}/` from the repo-root `.opencode/` by `specmgr opencode sync`, guarded by a pre-commit local drift hook and a CI parity check -- the same two-copy pattern the repo already runs for the packaged JSON Schema copies. Alternatives considered and rejected: package-copy-canonical (changes the repo's own dev workflow) and a build-time copy hook (non-standard build machinery).

#### 2026-09-23 09:03:00.000Z - make_valid implemented first, independent of the new ADR

The portable-prompt-narrates-delegation ADR (Phase 3) is only needed by Phase 4 (`implement_feat`/`review_feat`); `make_valid` has no such dependency, so it was moved to Phase 1 and the ADR moved to Phase 3.

#### 2026-09-23 09:02:00.000Z - Portable prompt + optional host-delegation pattern

`implement_feat`/`review_feat` narrate delegation via the host's own task-delegation tool when present, degrading to direct implementation otherwise, rather than either (a) requiring OpenCode specifically or (b) losing real subagent orchestration. See Design Notes.

#### 2026-09-23 09:01:00.000Z - Review-fix loop capped at 3 cycles

Chosen over an uncapped loop to bound the automatic review-to-fix-to-re-review cycle; remaining findings after 3 cycles go to the user instead.

#### 2026-09-23 09:00:30.000Z - `.opencode/agent`/`command` singular naming confirmed correct

No rename needed -- OpenCode accepts singular and plural directory names at both global and project scope.

### Related PRs / Commits

- (none yet)

### More Information

Source: https://github.com/dfch/biz.dfch.SpecMgr/issues/150
