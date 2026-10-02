---
classification: null
created: '2026-09-23 23:16:12.456+02:00'
id: feat-150-mcp-lifecycle-commands
status: review
type: feat
updated: '2026-09-30T05:13:02.000Z'
version: 1.0.0
---

# Feature: MCP-Native Feature-Lifecycle Commands (repair, refine_feat, implement_feat, review_feat) + OpenCode Distribution

## Plan

### Overview

GitHub issue #150 asks for five related capabilities that round out the feature/document lifecycle already partially covered by ad hoc OpenCode-only files: (1) a command that repairs an artifact that currently fails to parse, (2) a portable, MCP-native version of the OpenCode-only `implement_feature` workflow, (3) an automatic post-implementation review-and-fix-phase follow-up, (4) a pre-implementation plan-refinement command, and (5) an easy way to get these OpenCode-native commands onto a fresh OpenCode install (and guidance for other hosts, e.g. Claude Code).

The unifying design principle (see Design Notes) is: every new capability gets a **portable MCP prompt** (narration-only text, works in any MCP host, following the existing `create_*`/`update_*`/`implement_task`/`refine`/`compact_history` precedent) *and*, where real file-editing/iteration/multi-agent delegation is required, a **richer OpenCode-native subagent + command** with real permission enforcement (mirroring the existing `phase-orchestrator`/`phase-implementer`/`feat-reviewer`/`ref-finder` precedent). The portable prompt narrates delegation via the *host's own* subagent-delegation tool (e.g. OpenCode's `task` tool) when available, exactly like every existing prompt already narrates host-native tools it doesn't implement itself (`question`, `TodoWrite`) -- it degrades to direct single-session implementation when no such tool exists.

**Phase ordering is deliberately repair-first**: `repair` (Phase 1) has no dependency on the ADR that Phase 4 (implement_feat/review_feat) needs, so it can be implemented, tested, and shipped standalone before any other phase.

**Phase discipline (user requirement, 2026-09-24)**: every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the phase's docs sync travels inside that same commit (see Design Notes, and the phase-end gate task at the end of every phase in the Task List).

### Requirements

- REQ-001: A new `general/prompts/repair.py` MCP prompt, signature `repair(type, id=None)`, narrates discovering a failed-to-parse document (with `id`: confirm via `get_<d>(id)`'s wrapped parse error -- since Phase 1a (REQ-013) this is delivered as the non-raising `ParseFailureResult`-shaped result (the same parse defect as `list_<d>`'s failed-row `error` for the same file -- the trailing pydantic documentation line may differ by read order, Option B 2026-09-26) rather than a raised error; without `id`: scan `list_<d>()` for the failed row, whose `title`/`status` carry the `<failed to parse>` marker and whose `id` is null while `ref`/`path`/`error` are populated), reading the raw file via the host's own file-read tool (no MCP tool can return raw content of a document that fails to parse: `get_<d>(raw=True)` and the generic `update` both re-parse the existing document first, and `update`'s per-domain adapters convert that failure into the domain's not-found error before any write), fixing only what the enriched error addresses while preserving the frontmatter `id`/`created`/`status`/`version` byte-for-byte (and leaving `updated` untouched -- a repair is not an edit), looping the generic `validate(type, content, full=True)` tool over the full raw text until green, writing the repaired full text back to the same path via the host's own file-write tool -- explicitly NOT via the generic `update` tool, which is structurally unable to repair a document that fails to parse -- and then confirming the repair actually succeeded by calling `get_<d>(id)` again (or, when no `id` was given, `list_<d>()` again to confirm the row's `<failed to parse>` marker and `error` are gone) against the file as it now exists on disk, since the host's file-write tool operates outside the MCP server's control and could still produce a file that differs from the text that was validated (encoding, line-ending, or partial-write differences); when the host has no file read/write tools the prompt degrades to diagnose-only (report the error and the proposed fix, touch nothing); `type` is one of the 12 whole-body domains -- ADR is explicitly out of scope (it has no generic `validate`/`parse` tooling).

- REQ-002: A new `.opencode/agent/doc-repairer.md` subagent implements REQ-001's loop with real file access, declaring every permission it relies on explicitly: `read`/`glob`/`grep`/`list`/`question`/`todowrite` allowed, `edit`/`write` allowed workspace-wide (the broken document may live under any domain base directory), `task` denied, `bash` denied -- plus a `.opencode/command/repair.md` (`/repair <type> [id]`, `$1`/`$2` positionals, `agent: doc-repairer`) wrapper.

- REQ-003: A new `feat/prompts/refine_feat.py` MCP prompt, signature `refine_feat(id)`, narrates a pre-implementation plan-readiness review (testable ACs, phase ordering/dependencies, scope clarity, unresolved decisions) that is fully MCP-native: read via `get_feat(id, raw=True)`, ask the user via the `question` tool, apply edits via the generic `update(type="feat", id, content, offset/limit)` tool (line-range preferred), and re-check via `validate(type="feat", content, full=True)` -- host file tools only as a fallback when those specmgr tools are unavailable.

- REQ-004: A new `.opencode/agent/feat-planner.md` subagent implements REQ-003 with real file access, with its plan-README-only edit scope enforced mechanically rather than by prose: `edit`/`write` permission rules `{"*": deny, ".specmgr/feat/**/README.md": allow}` (OpenCode's `edit` permission patterns match file paths, last matching rule wins), `read`/`glob`/`grep`/`list`/`question`/`todowrite` allowed, `task` denied, `bash` denied -- plus `.opencode/command/refine-feature.md` (`/refine-feature <id>`, `agent: feat-planner`).

- REQ-005: A new `feat/prompts/implement_feat.py` MCP prompt narrates orchestrator discipline (read plan, phase-by-phase `TodoWrite`, delegate each phase via the host's subagent-delegation tool when available, verify before advancing, never write code directly), names the Phase 3 ADR by UUID, mentions the REQ-008 review-fix loop, and falls back to direct single-session implementation when no delegation tool exists.

- REQ-006: A new `feat/prompts/review_feat.py` MCP prompt narrates `feat-reviewer.md`'s existing review checklist and report format portably, including the new conditional "Proposed Fix Phase" section (REQ-007).

- REQ-007: `.opencode/agent/feat-reviewer.md`'s report format gains a new, conditional "Proposed Fix Phase" section: a ready-to-paste block for the plan's `### Task List` -- a `#### Phase N: Fix phase (review cycle k)` heading using the next unused phase number (never renumbering existing phases) plus `- [ ] Task N.M` items derived strictly from the report's own Errors/Gaps/Inconsistencies (Code Smells/Improvements/Positives stay advisory), with any item that needs a user decision explicitly flagged `[NEEDS DECISION]` rather than guessed at.

- REQ-008: `.opencode/agent/phase-orchestrator.md` (and `implement_feat`'s narration, REQ-005) gain a final review-fix loop: after the plan's final verification phase, run the reviewer; if it proposes a fix phase, resolve any `[NEEDS DECISION]` items with the user via `question`, then delegate the fix phase to one more `phase-implementer` cycle exactly like a normal phase -- with the delegation prompt instructing the implementer to first append the reviewer's ready-to-paste block to the plan's Task List, since the orchestrator itself cannot edit files (`edit`/`write` are denied to it); repeat until the reviewer reports no Errors, Gaps, or Inconsistencies left, capped at 3 review-fix cycles (after which remaining findings are handed to the user instead of auto-fixed again).

- REQ-009: The repo-root `.opencode/{agent,command}/*.md` files remain the canonical working copy; a generated package copy under `general/data/opencode/{agent,command}/` ships in the wheel, produced by a new `specmgr opencode sync` CLI stage, kept in sync by a new pre-commit local drift hook (sync, then fail on diff -- mirroring the existing `specmgr-schema-*` hooks) plus a CI parity check in the 3.13 job; `pyproject.toml` gains the `[tool.setuptools.package-data]` globs for the new subdirectory; the installer (REQ-010) must read the package copy via `importlib.resources`, since a CWD-relative `.opencode/` does not exist in a real, non-editable install.

- REQ-010: A new `specmgr opencode install [--global|--local] [--force]` CLI subcommand -- a nested `opencode` Typer sub-application in `commands/opencode.py` registered on `cli.py` via `app.add_typer` (the one-module-per-command convention) alongside `sync` -- copies every one of the 12 agent+command `.md` files (the 4 existing agents + 2 new agents, the 4 existing commands + 2 new commands; the new commands' dependency closure needs the existing agents) from the package copy to `~/.config/opencode/` (global) or `./.opencode/` (local), into the target's existing `agent(s)/`/`command(s)/` sibling directory when one exists (OpenCode accepts both singular and plural) and into singular `agent/`+`command/` otherwise; per file: identical content is a silent no-op, differing content is refused (listing the files) unless `--force`; the command never reads or writes `opencode.json` (MCP server configuration stays the README's job) and prints a reminder pointing at the README's "Add to OpenCode" section.

- REQ-011: README.md gains a new section placed immediately after the existing "Add to OpenCode" section (which it references for MCP server setup rather than duplicating): the CLI installer (usage, what gets copied, target semantics) plus the manual/Claude-Code path -- Claude Code's structurally similar `.claude/agents/*.md`/`.claude/commands/*.md` convention is called out explicitly with a short hand-ported frontmatter example, along with the permission-model gap (OpenCode's per-pattern bash/edit rules vs. Claude Code's coarse tool allow-list) that means these are hand-ported, simplified equivalents, not an automatic translation.

- REQ-012: A new `.opencode/skill/repair/SKILL.md` OpenCode Skill (added 2026-09-25 following a design-clarification pass -- see QA 76229d40-55e9-4640-9249-c391e1f3e84c question 0.0020), `name: repair`, whose `description` frontmatter triggers the model when it organically encounters a failed-to-parse document mid-execution (not only via an explicit `/repair` invocation); its body stays thin, deferring to the `doc-repairer` subagent via the `task` tool when available and otherwise narrating the same condensed host-native loop `general.prompts.repair` describes, so the workflow has no fourth independent copy to keep in sync.

- REQ-013: A `get_<d>` parse-failure error channel (feat-150-mcp-lifecycle-commands Phase 1a, the narrow third extension of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising structured-result workaround chain after `validate` and `set_status`'s invalid-status case): a new shared `ParseFailureResult` model (`general/models/parse_failure_result.py`, fields `error`/`path`/`id`) returned by all 12 `get_<d>` tools (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`; ADR excluded) when the requested id resolves to an on-disk file that exists but fails to parse, instead of raising the domain's `XNotFoundError` -- for both `raw=False` and `raw=True` (a broken document never returns raw text, preserving the invariant that no specmgr MCP tool can return the raw content of a document that fails to parse); `error` carries the same parse defect as the domain's `list_<d>` failed-row `error` for the same file (identical field path and cause; the trailing pydantic documentation line may differ by read order/cache state, since `DocCache`'s exception reconstruction drops it -- Option B, 2026-09-26, follow-up issue for the str-faithful reconstruction), and the success wire shape stays byte-identical via the SDK's `model_dump(exclude_none=True)`; a truly absent id still raises the domain's not-found error and an invalid id shape still raises `ValueError` before any file access. Backed by a new shared `find_parse_failure(base_dir, id_, read_fn)` helper for the 11 flat-file domains (which does NOT change `find_doc_path_by_id`'s documented skip behavior) and a bespoke `find_feat_parse_failure(base_dir, id_)` for `feat`; `update`/`delete`/`set_status`/`set_classification`/`validate`/`list_references` are unchanged.

### Acceptance Criteria

- [x] ACC-001: `repair(type, id=None)` MCP prompt exists, is registered, and its instructions name `list_<d>`'s failed-row discovery and `get_<d>`'s failure confirmation, direct the raw read and the write-back at the host's own file tools with an explicit note that the generic `update` tool cannot repair a document that fails to parse, loop the generic `validate(type, content, full=True)` tool, require a post-write confirmation via `get_<d>(id)`/`list_<d>()` against the file as it now exists on disk, state the diagnose-only degradation, and state the ADR exclusion.

- [x] ACC-002: `/repair <type> <id>` successfully drives `doc-repairer` to repair a deliberately-broken fixture document (parse fails before, succeeds after) in a manual smoke test.

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

- [x] ACC-014: `.opencode/skill/repair/SKILL.md` exists with a `name: repair` and a trigger `description` covering an organically-encountered failed-to-parse document, and its body defers to `doc-repairer` via the `task` tool when available, else narrates the condensed host-native loop.

- [x] ACC-015: `get_<d>` on a broken document returns `ParseFailureResult` with `error` + absolute `path` for all 12 whole-body domains (incl. `feat`), `error` text carries the same parse defect as `list_<d>`'s failed-row `error` for the same file (identical field path and cause; the trailing pydantic documentation line may differ by read order/cache state -- Option B, 2026-09-26), healthy-document results are byte-identical to the pre-change shape, and a truly absent id still raises the domain's not-found error.

- [x] ACC-016: A new ADR in `docs/adr/` documents the decision, is status `accepted`, and is recorded in Related Decisions.

### Scope

#### Included

- 4 new MCP prompts (`repair`, `refine_feat`, `implement_feat`, `review_feat`) and their packaged instruction data files.

- 2 new OpenCode subagents (`doc-repairer`, `feat-planner`) and 2 new OpenCode commands (`/repair`, `/refine-feature`).

- 1 new OpenCode skill (`.opencode/skill/repair/SKILL.md`, REQ-012) for organic, non-`/repair`-invoked discovery of a failed-to-parse document.

- Targeted edits to the 4 existing OpenCode files: `feat-reviewer.md` (the Proposed Fix Phase section) and `phase-orchestrator.md` (the review-fix loop) for the review-fix loop, `implement-feature.md` (doc update mentioning the automatic review-fix step, plus its "a a" typo fix), and `review-feature.md` (its body re-enumerates the report sections and would go stale without the new conditional section).

- Packaging: the generated package copy under `general/data/opencode/`, the `specmgr opencode sync` stage, the pre-commit drift hook, the CI parity check, and the `pyproject.toml` package-data globs (REQ-009).

- The `specmgr opencode install` CLI subcommand + tests (REQ-010).

- The README.md section (installer + Claude Code path) + its Table of Contents entry (REQ-011).

- AGENTS.md/CHANGELOG/generated-docs/server.py-docstring updates, one per phase, inside that phase's own single commit.

- One new ADR for the portable-prompt-narrates-delegation pattern.

- The `ParseFailureResult` model (`general/models/parse_failure_result.py`) + the 12 `get_<d>` parse-failure conversions (+ the shared `find_parse_failure` helper and the bespoke `feat` one) + Phase 1a's own ADR (REQ-013, ACC-015/ACC-016) -- the `get_<d>` parse-failure error channel, implemented and committed before Phase 1's narration refinement and commit.

#### Explicitly Out Of Scope

- Any change to `.opencode/agent/phase-implementer.md`, `.opencode/agent/ref-finder.md`, `/refs`, or `/release` (unaffected).

- Any change to `general/prompts/compact_history.py` -- its docstring's claim that feature folders "have no dedicated parser/get/update MCP tools" is stale since feat-31 (the generic `update`/`get_feat` tools exist now); that is a separate small fix.

- Any read/write/merge of the user's `opencode.json` by the installer (MCP server configuration stays the README's documented job).

- Building an OpenCode plugin (`config()` hook) for zero-copy distribution -- noted as a possible future enhancement, not built now.

- Auto-generating Claude-Code-flavored `.claude/agents`/`.claude/commands` files from the OpenCode ones -- hand-ported/simplified equivalents are documented instead, given the permission-model mismatch.

- Any change to the generic `validate`/`update`/`set_status` tools themselves (REQ-001/002 build on them as-is; REQ-001's write-back is host-native precisely because `update` cannot repair a broken document).

- The str-faithful `DocCache` exception reconstruction (Option A) that would restore the full byte-identical `get_<d>`/`list_<d>` error-text invariant -- deferred to a follow-up issue (Task 1a.8); Option B's qualified claims stand until it ships (2026-09-26 decision).

- Enforcing any of this via pre-commit/CI (matches the repo's existing "no `validate_adr`-in-CI yet" gap, unaffected by this feature) -- except the REQ-009 package-copy drift check, which is a build-consistency gate in the same class as the existing `specmgr-schema-*` hooks, not a document-validation gate.

- Extending the REQ-009/REQ-010 packaging/installer (`specmgr opencode sync`/`install`) to also cover the new `.opencode/skill/` directory -- Phase 5's scope stays `{agent,command}` only for this feature, as originally worded; broadening it to include `skill/` is a natural, low-risk follow-up, deliberately left as an open item rather than silently folded into REQ-009/010 here.

### Dependencies

#### Depends On

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 / c4efbde6-fd19-4aa8-8668-95316ed62dcc (dispatch-only domain convention, followed by `repair`'s generic shape).

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

- feat-27-validation / feat-81-83-validation (the enriched validate errors and the failed-row `list_<d>` mechanism `repair` builds on).

- feat-31-feature (the `feat` domain itself, whose generic `update`/`validate` adapters make `refine_feat` fully MCP-native).

- The `specmgr-schema-*` pre-commit hooks as the model for REQ-009's package-copy drift hook (the same two-copy + regenerate + fail-on-diff pattern).

- Phase 4 (implement_feat/review_feat) depends on Phase 3's new ADR (its UUID is an input to Phase 4's instruction files); Phase 1 (repair) deliberately does not.

- Phase 1's `repair` with-id narration is written against REQ-013's `get_<d>` parse-failure contract (Phase 1a); Phase 1a is implemented and committed before Phase 1's narration refinement and commit.

#### Blocks

- None known.

### Design Notes

**Phase discipline (user requirement, 2026-09-24).** Every phase ends with the full quality gate -- `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, the full test suite `uv run --frozen pytest -n auto --cov=src --cov-report=`, plus every doc-drift check the phase touches (`specmgr docs`, `specmgr mcp-docs`, and `specmgr adr-toc` for Phase 3) -- and exactly one Conventional Commit for that phase; the phase's docs sync (server.py docstring, AGENTS.md bullet(s), CHANGELOG entry, regenerated docs) travels inside that same commit, never as a follow-up. The Task List makes this explicit with a phase-end gate task (Task N.5/N.6/N.7/N.8) at the end of every phase.

**Why `repair` cannot use the generic `update` for the write-back.** `update`'s per-domain adapters resolve the existing document via `load_by_id`, which fully re-parses it; a document that fails to parse converts that failure into the domain's not-found error before anything is written (`req/tools/_io.py:72-112`; every `_update_<d>` adapter in `general/tools/update.py` takes the same shape). The raw read and the raw write-back therefore must be host-native file tools -- the same precedent `compact_history` already sets (its instructions "rely entirely on the LLM's own file read/edit/write tools, not on any specmgr tool"). A host without file tools gets the diagnose-only degradation: the prompt still reports the enriched error and the proposed fix, it just cannot apply it.

**Post-write confirmation closes the loop (REQ-001, added 2026-09-25 following a design-clarification pass).** Looping `validate(type, content, full=True)` over the in-memory text before writing only proves the text `repair` is *about* to write is well-formed -- it says nothing about the bytes the host's file-write tool actually put on disk (encoding, line-ending, or partial-write differences are all outside the MCP server's control, since the write itself is host-native, not a specmgr tool call). `repair`'s loop therefore does not end at a green `validate` result: it makes one more, real MCP tool call after the write -- `get_<d>(id)` (or, when no `id` was given, `list_<d>()` again, checking that the row's `<failed to parse>` marker and `error` are gone) -- against the file as it now exists on disk. Only a real parse of the real file counts as success. This also answers what Task 1.3's own unit test can and cannot prove: since `repair` is a narration-only MCP prompt (it returns text, it never executes a repair itself), `test_repair.py` can only assert that the *returned instructions* mention this post-write confirmation step, not that a real repair round-trips -- the real end-to-end proof is ACC-002's manual smoke test against a genuinely broken fixture document.

**`refine_feat` is MCP-native (unlike `repair`).** The plan README is a parseable document, so its whole read/apply/re-check path is specmgr tooling: `get_feat(id, raw=True)`, the generic `update(type="feat", id, content, offset/limit)` (line-range preferred, so unchanged regions stay byte-identical), and `validate(type="feat", content, full=True)`. Host file tools are only a fallback for hosts that cannot reach those tools.

**Portable-prompt-narrates-delegation pattern (the item-2 resolution).** An MCP prompt never executes tool calls itself -- it returns text to whatever LLM session invoked it, exactly like every existing prompt in this codebase (`create_req` says "use the `question` tool"; neither `question` nor `TodoWrite` is implemented by this MCP server). `implement_feat`/`review_feat` extend this same precedent one step further: they narrate delegating work to a subagent via "your host's task-delegation tool, if one exists." Inside OpenCode, that's a real instruction to use the `task` tool (genuine multi-agent orchestration, since OpenCode exposes both the `specmgr` MCP tools and its own native tools in the same session). On a host with no such tool, the same text degrades to "implement it yourself, one phase at a time" -- never a hard failure. This is the subject of the new ADR (ACC-013), needed before Phase 4 but not before Phase 1.

**Prompt/agent/command text duplication is unavoidable.** OpenCode exposes MCP *tools* but not MCP *prompts* as slash commands (its MCP documentation covers tools only), so the OpenCode agent/command files cannot delegate to the packaged prompt text -- each carries its own copy of the same workflow. This duplication is accepted; keeping prompt \<-> agent \<-> command wording in sync is a standing review-checklist item (the `feat-reviewer` Consistency checklist already flags wording drift between paired artifacts).

**Review-fix loop (capped, aligned exit criterion).** Capped at 3 automatic review-fix cycles (configurable only in the prose instructions, not a hard machine limit -- these are markdown-narrated workflows, not code). The loop exits when the reviewer reports no Errors, Gaps, or Inconsistencies -- the same set REQ-007's fix phase derives tasks from (Code Smells/Improvements/Positives stay advisory), so a cycle never ends with the fix phase still re-deriving the same inconsistency. Any findings still open after 3 cycles are handed to the user instead of auto-fixed again. The orchestrator cannot append the proposed fix phase itself (`edit`/`write` are denied to it), so the fix phase's `phase-implementer` is delegated with an explicit first step: append the reviewer's ready-to-paste block to the plan's Task List (next unused phase number, no renumbering of existing phases).

**Packaging: root-canonical, generated package copy (user decision, 2026-09-24).** The wheel only ships what lives under `src/` (`pyproject.toml`'s `[tool.setuptools.packages.find] where = ["src"]` + explicit `[tool.setuptools.package-data]` globs; there is no `MANIFEST.in`), so the installable `.opencode` copy is a generated artifact under `general/data/opencode/{agent,command}/`. The repo-root `.opencode/` stays the canonical working copy; `specmgr opencode sync` regenerates the package copy from it, and a pre-commit local drift hook (sync + fail on diff, scoped to `^.opencode/(agent|command)/.*\.md$`) plus a CI parity check (3.13 job, alongside `specmgr docs`/`specmgr adr-toc`) keep the two from drifting -- the same two-copy pattern the repo already runs for the 12 packaged JSON Schema copies (the `specmgr-schema-*` hooks in `.pre-commit-config.yaml`). The installer reads the package copy via `importlib.resources` (the `_packaged_data` convention), so it works identically from an editable checkout and a real PyPI install.

**Distribution target semantics.** `specmgr opencode install` copies all 12 files (6 agents + 6 commands, existing + new) by design -- the new commands' dependency closure needs the existing agents (`/implement-feature` drives `phase-orchestrator` -> `phase-implementer`; `/refs` drives `ref-finder`). OpenCode accepts both singular and plural directory names at project and global scope (its documentation; this machine itself uses `agent/`+`command/` in-project and `agents/` globally), so the installer detects an existing `agent(s)/`/`command(s)/` sibling at the target and defaults to singular `agent/`+`command/`. Per file: identical content is a silent no-op (re-install is idempotent), differing content is refused with the file list unless `--force`. The installer never touches `opencode.json` -- MCP server setup (including the documented unsafe-bare-`uvx` caveat) stays the README's "Add to OpenCode" section's job. It does not yet cover the new `.opencode/skill/` directory (see Explicitly Out Of Scope).

**OpenCode permission model for the new agents.** `edit` permission patterns match file paths with the last matching rule winning (opencode.ai/docs/permissions), so `feat-planner`'s plan-README-only scope is mechanically enforced (`{"*": deny, ".specmgr/feat/**/README.md": allow}` on `edit`/`write`), not just prose discipline. Both new agents deny `bash` and `task` and declare every permission they rely on explicitly (`read`/`glob`/`grep`/`list`/`question`/`todowrite`), matching the existing agents' explicitness.

**OpenCode Skill for organic discovery (REQ-012, added 2026-09-25 via QA 76229d40-55e9-4640-9249-c391e1f3e84c question 0.0020).** The `/repair` command and `doc-repairer` subagent both need an explicit human (or orchestrator) invocation; neither helps when an agent organically stumbles onto a failed-to-parse document mid-task, with no human around to type `/repair`. OpenCode Skills close that gap: they are listed automatically in every agent's system prompt and self-trigger when a task matches the skill's own `description`, per OpenCode's Skills documentation. `.opencode/skill/repair/SKILL.md` is kept deliberately thin -- a trigger `description` plus an instruction to prefer delegating to `doc-repairer` via the `task` tool when available, falling back to the same condensed host-native loop `general.prompts.repair` already narrates -- rather than a fourth independent copy of the repair workflow to keep in sync (see "Prompt/agent/command text duplication is unavoidable" above, which this skill now also participates in).

**Naming.** New OpenCode files: `doc-repairer.md` (agent) / `repair.md` (command) / `.opencode/skill/repair/SKILL.md` (skill, `name: repair`, singular directory matching this repo's existing `agent/`+`command/` convention); `feat-planner.md` (agent) / `refine-feature.md` (command). `general.prompts.repair` is a deliberate exception to the `<verb>_<domain>` prompt-naming convention: it is cross-cutting (takes `type` + optional `id`, not tied to one domain), so it instead follows the short, bare-word precedent this repo already uses for cross-cutting, type-dispatched tools -- `validate`, `delete`, `list_references` -- and pairs naturally with `validate` in a "validate, then repair" idiom; the domain-scoped `feat.prompts.refine_feat`/`implement_feat`/`review_feat` keep the `<verb>_<domain>` convention as usual (decision recorded in the linked QA, question 0.0010).

### Related Decisions

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to `get_<d>`'s parse-failure case", Phase 1a, status `accepted`): the narrow third extension of the ADR 519d1206 client-side-`isError`-truncation workaround chain after `validate` and `set_status`'s invalid-status case (ADR b399f1ce), backing REQ-013 (the `get_<d>` parse-failure error channel).

- New ADR (Phase 3, before Phase 4): "Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent" -- architecture-level, affects any future `<verb>_feat`-style prompt, so it gets a full ADR per this repo's own ADR-vs-feature-log convention. Its UUID is an input to Phase 4's instruction files and is recorded here once created.

- User decisions recorded in the Decisions Made log below (2026-09-24): one commit per phase with the full quality gate; the review-fix loop's exit criterion (Errors/Gaps/Inconsistencies); the root-canonical/generated-package-copy packaging strategy.

### Task List

#### Phase 100: `get_<d>` parse-failure error channel (repair prerequisite -- implement before Phase 1's commit)

- [x] Task 100.100: `ParseFailureResult` model in `general/models/parse_failure_result.py` (fields `error`/`path`/`id`, mirroring `invalid_status_result.py`'s shape) + registration in `general/models/__init__.py`.

- [x] Task 100.110: the shared `find_parse_failure(base_dir, id_, read_fn) -> tuple[Path, str] | None` helper in `general/tools/_doc_paths.py` (scans for the file whose stem encodes `id_` as a hyphen-bounded token -- the flat-file naming is `<type>-<id>-<slug>.md` -- and reports a parse-failing file's `(path, str(exc))`, `None` otherwise; `find_doc_path_by_id`'s documented skip behavior unchanged) + the bespoke `find_feat_parse_failure(base_dir, id_)` in `feat/tools/_paths.py` (no scan -- the folder name IS the id).

- [x] Task 100.120: the 12 `get_<d>` conversions (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs): on `<D>NotFoundError` from `load_by_id`, run the helper, `assert_within`, return `ParseFailureResult(error, path, id)`; re-raise otherwise. Union return annotation `<D>Document | str | ParseFailureResult`, description/docstring note (consistent across all 12), `raw=True` never returns a broken document's raw text.

- [x] Task 100.130: the new ADR in `docs/adr/` ("Extend the non-raising structured-result workaround to `get_<d>`'s parse-failure case", status `accepted`, ADR 519d1206-chain third case) + `specmgr adr-toc` regeneration.

- [x] Task 100.140: tests -- per-domain (all 12: broken → `ParseFailureResult` with `error`/`path`/`id` (no raise); healthy → today's exact shape (raw=False model, raw=True str); absent id → domain `XNotFoundError`; `raw=True` on broken → `ParseFailureResult` (never a str); invalid id shape → `ValueError`), the `error`-text consistency vs `list_<d>` (all 12), the shared-helper unit tests, and the `ParseFailureResult` model test.

- [x] Task 100.150: docs sync -- `server.py` module docstring (the `get_<d>` `ParseFailureResult` note), `AGENTS.md` `general/` bullet, `CHANGELOG.md` (`Added` for the model/helpers + `Changed` for the `get_*` contract), `specmgr docs`/`specmgr mcp-docs` regeneration (also picks up the uncommitted Phase 1 `repair` prompt -- expected).

- [x] Task 100.160: Phase-end gate: full quality gate green (ruff format/check, vulture, full pytest, `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` drift), then exactly one Conventional Commit for the phase.

- [x] Task 100.170: (follow-up issue #162) Option B amendment pass (2026-09-26 decision): qualify the error-text consistency claim at every remaining site -- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (Decision Outcome item 3 + Consequences + Confirmation), the `ParseFailureResult` docstring (`general/models/parse_failure_result.py`), the `repair` instructions' step 1 with-id line (`general/data/general_repair_instructions.md`), `repair.py`'s module docstring + `@mcp.prompt` description, the `doc-repairer` agent / `repair` skill wording if it repeats the claim, `AGENTS.md`/`CHANGELOG.md`/`server.py` wording, regenerated `docs/MCP.md` + `docs/api` -- and relax the 12 order-dependent `error`-text identity tests to content-based assertions (identical field path and cause); then file the follow-up issue for Option A (str-faithful `DocCache._fresh_exception` reconstruction) carrying its full spec (root cause, affected surface, acceptance criteria, doc-restoration list) and record the issue number here.

#### Phase 110: repair (no ADR dependency -- implement first)

- [x] Task 110.100: `general/data/general_repair_instructions.md` (host-native read/write, the explicit no-`update` note, the post-write `get_<d>`/`list_<d>` confirmation step, the diagnose-only degradation, the frontmatter-preservation rule, the ADR exclusion) + `general/prompts/repair.py` (`repair(type, id=None)`) + registration in `general/prompts/__init__.py`.

- [x] Task 110.110: `.opencode/agent/doc-repairer.md` (full explicit permission frontmatter per REQ-002) + `.opencode/command/repair.md` (`$1`/`$2`, `agent: doc-repairer`).

- [x] Task 110.120: `.opencode/skill/repair/SKILL.md` (REQ-012: `name: repair` frontmatter, a trigger `description` covering an organically-encountered failed-to-parse document, a thin body deferring to `doc-repairer` via the `task` tool when available, else narrating the condensed host-native loop mirroring `general/data/general_repair_instructions.md`).

- [x] Task 110.130: `tests/general/prompts/test_repair.py` (registration + template substitution + asserting the rendered instructions mention the post-write `get_<d>`/`list_<d>` confirmation step, matching existing prompt test patterns -- since `repair` is narration-only text, this test can only check what the instructions say, not execute an actual repair; the real end-to-end proof is ACC-002's manual smoke test).

- [x] Task 110.140: Docs sync: `AGENTS.md`'s `general/` bullet (including the new `.opencode/skill/repair/` skill), `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [x] Task 110.150: Phase-end gate: full quality gate green (ruff format/check, vulture, full pytest, `specmgr docs`/`specmgr mcp-docs` drift), then exactly one Conventional Commit for the phase.

#### Phase 120: refine_feat

- [ ] Task 120.100: `feat/prompts/refine_feat.py` (`refine_feat(id)`) + `feat/data/feat_refine_instructions.md` (the MCP-native `get_feat`/`update`/`validate` path) + registration in `feat/prompts/__init__.py`.

- [ ] Task 120.110: `.opencode/agent/feat-planner.md` (path-scoped `edit`/`write` permission rules per REQ-004) + `.opencode/command/refine-feature.md` (`agent: feat-planner`).

- [ ] Task 120.120: `tests/feat/prompts/test_refine_feat.py` + manual smoke test (ACC-004).

- [ ] Task 120.130: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 120.140: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 130: ADR for portable-delegation pattern

- [ ] Task 130.100: Write the new ADR (see Related Decisions) in `docs/adr/` per the repo's ADR conventions, regenerate `specmgr adr-toc` (pre-commit hook), set its status to `accepted`, and record its UUID in this README's Related Decisions -- needed before Phase 4 (its UUID is an input to Phase 4's instruction files).

- [ ] Task 130.110: Phase-end gate: full quality gate green (including the `specmgr adr-toc` drift check), then exactly one Conventional Commit for the phase.

#### Phase 140: implement_feat + review_feat + auto fix-phase loop

- [ ] Task 140.100: `feat/prompts/implement_feat.py` + `feat/data/feat_implement_instructions.md` + registration, narrating the optional-delegation pattern from Design Notes, naming the Phase 3 ADR by UUID, and mentioning the review-fix loop.

- [ ] Task 140.110: `feat/prompts/review_feat.py` + `feat/data/feat_review_instructions.md` + registration, mirroring `feat-reviewer.md`'s checklist/report format including the conditional "Proposed Fix Phase" section.

- [ ] Task 140.120: Extend `.opencode/agent/feat-reviewer.md`'s report format with the conditional, ready-to-paste "Proposed Fix Phase" block + the `[NEEDS DECISION]` flagging rule (REQ-007).

- [ ] Task 140.130: Extend `.opencode/agent/phase-orchestrator.md`'s Workflow section with the capped review-fix loop (REQ-008: exit on no Errors/Gaps/Inconsistencies, the implementer-appends-the-fix-phase delegation step); update `.opencode/command/implement-feature.md`'s prose to mention the automatic review-fix step and fix its "a a" typo; update `.opencode/command/review-feature.md`'s body so its report-section enumeration includes the new conditional section.

- [ ] Task 140.140: Update `implement_feat`'s narration to mention the same review-fix loop, for portable-host parity.

- [ ] Task 140.150: `tests/feat/prompts/test_implement_feat.py` + `tests/feat/prompts/test_review_feat.py` + manual smoke test.

- [ ] Task 140.160: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 140.170: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 150: Distribution

- [ ] Task 150.100: `commands/opencode.py`: the `opencode` Typer sub-application with the `sync` stage (repo-root `.opencode/{agent,command}/*.md` -> `general/data/opencode/{agent,command}/` package copy) and `install [--global|--local] [--force]` (REQ-010 semantics: package-data source via `importlib.resources`, all 12 files, sibling-directory detection, per-file no-op/refuse/`--force`, no `opencode.json` touch); register via `app.add_typer` in `cli.py`; export in `commands/__init__.py`.

- [ ] Task 150.110: Generate the initial package copy; add the `pyproject.toml` `[tool.setuptools.package-data]` globs for `general/data/opencode/`; add the pre-commit local drift hook (sync + fail on diff, files `^.opencode/(agent|command)/.*\.md$`); add the CI parity check to the 3.13 job alongside the `specmgr docs`/`specmgr adr-toc` drift checks.

- [ ] Task 150.120: `tests/commands/test_opencode.py` (sync idempotence/drift detection, install copy behavior, sibling-directory detection, `--force` overwrite guard, global vs. local target resolution, package-data sourcing) + a manual `specmgr opencode install --local` smoke in a temp directory (ACC-009/ACC-010).

- [ ] Task 150.130: README.md: the new section immediately after "Add to OpenCode" (installer + manual Claude Code path per REQ-011, referencing that section for server setup) + the README Table of Contents entry.

- [ ] Task 150.140: Docs sync: `AGENTS.md`'s CLI section (the new `specmgr opencode` subcommand), `specmgr docs` regeneration (the `commands/` module in `docs/api/`), `CHANGELOG.md` entry.

- [ ] Task 150.150: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 160: Final Verification

- [ ] Task 160.100: Walk every Acceptance Criterion above (ACC-001..ACC-014) with concrete evidence.

- [ ] Task 160.110: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

## Progress

### Current Status

**As of 2026-09-27**: Phase 1a (`get_<d>` parse-failure error channel, REQ-013/ACC-015/ACC-016) and Phase 1 (repair, REQ-001/REQ-002/REQ-012), including Task 1a.8's Option B amendment pass, are implemented, gate-green, and committed (5c94030, b82eef4, af93f96, 10a4b62). ACC-001, ACC-002, ACC-014, ACC-015, and ACC-016 are met; post-implementation review (PR #155) approved with two doc fixes, now applied (the no-generic-write-tool narration extended to the merged `edit` tool; ACC-014 checked). The plan's own parse failure (bare `<d>` html_inline tokens, plus two further model violations the `<d>` error had masked: the `Phase 1a:` Task List heading and the two-paragraph 2026-09-25 19:49:40.000Z update entry) was repaired as part of this closeout. Status moves to `review` via the orchestrator's `set_status` call; remaining: push, PR, post-implementation review. Phases 2-6 remain unstarted (user scope: Phase 1 only).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-28 03:46:33.000Z - Split: Phases 2-6 moved to feat-167-mcp-lifecycle-commands-2 (GitHub issue #167)

This feature's scope is hereby fixed to Phase 0 (`get_<d>` parse-failure error channel) and Phase 1 (`repair`) only, both already implemented and merged (PR #155); the remaining four items from this feature's own GitHub issue #150 -- `refine_feat`/`feat-planner` (Phase 2), the portable-prompt-narrates-delegation ADR (Phase 3), `implement_feat`/`review_feat` plus the review-fix loop (Phase 4), and OpenCode distribution (Phase 5), plus their own final verification (Phase 6) -- are split into a new feature, feat-167-mcp-lifecycle-commands-2, tracked under a new GitHub issue, #167 (cross-referenced both ways: this note here, and a comment on issue #150 pointing at #167), because GitHub issue #163 (feat-163-feat-numbering) introduces a stricter FEAT Task List numbering scheme (`Phase NNN`/`Task NNN.MMM`) with an explicit no-migration policy for existing plan documents, and continuing Phases 2-6 inside this already-merged plan would have meant either mixing schemes in one document or renumbering already-shipped Phase 0/1 content referenced elsewhere in the repo (AGENTS.md, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c, `CHANGELOG.md`, `server.py`'s docstring); the Phase 2-6 sections, REQ-003..012, and ACC-003..013 above are left exactly as originally planned, as historical context only -- they are not implemented under this feature and their checkboxes are not expected to be checked here.

#### 2026-09-28 02:57:00.000Z - Post-review polish: repair narration wording (A3/A4) fixed, find_parse_failure edge-case tests added (B2)

Additional small findings from an earlier informal review pass (not the formal PR #155 feat-reviewer, which already approved with its own two fixes in 4ac7d41) are now applied. (1) `general/data/general_repair_instructions.md`'s without-id discovery bullet no longer tells the model to "remember the row's `id`" for a failed list row -- a failed row's `id` is always `null` by construction, so there was nothing to remember there; the frontmatter id, if any, only becomes recoverable after the raw read in step 2. (2) Both `general_repair_instructions.md` and `.opencode/agent/doc-repairer.md`'s post-write confirmation steps now say the healthy row's `error` field is "absent" rather than "`null`", matching the actual `exclude_none` serialization. (3) `find_parse_failure`'s previously-untested defensive branches now have coverage: `tests/general/tools/test__doc_paths.py` gains the prefix-only-match arm (`<id>-<slug>.md`, no type prefix), the two-name-matches-are-ambiguous arm (returns `None`), and the vanished-file-mid-scan (`FileNotFoundError`) arm (returns `None`); `tests/feat/tools/test__paths.py` gains the equivalent vanished-file arm for `find_feat_parse_failure` (no multi-match case applies there -- the folder name IS the id, there is no scan). No behavior change anywhere.

#### 2026-09-27 19:22:54.000Z - Post-implementation review fixes (PR #155)

Post-implementation review of the Phase 1 scope (PR #155) approved with minor doc fixes only -- no Errors, Gaps, or Inconsistencies in scope. Fixes now applied: (1) the merged dev tree (feat-159) added a second generic write tool, `edit`, whose per-domain adapters re-parse the existing document first (each calls the domain's `load_by_id`) and so convert a parse failure into the domain's not-found error before any write, exactly like `update` -- the no-generic-write-tool narration therefore now names both tools at every site: `general/data/general_repair_instructions.md` (intro note + step 5), `general/prompts/repair.py` (module docstring + `@mcp.prompt` description), `.opencode/agent/doc-repairer.md` (frontmatter description, intro mechanism note, step 5), `.opencode/skill/repair/SKILL.md` (step 2 note, step 5), `AGENTS.md`'s `repair` description (both of its no-write-tool clauses), `server.py`'s General-prompts `repair` line, and the CHANGELOG `repair` `Added` entry; (2) `server.py`'s Path-safety paragraph now also enumerates `edit` among the tools applying the `general/tools/_path_safety` guards (its registration text mentions only the id-`ValueError` half); (3) ACC-014 checked -- the review verified `.opencode/skill/repair/SKILL.md` exists and meets every sub-claim. Docs regenerated (`specmgr docs`/`specmgr mcp-docs`) and the full quality gate re-run green.

#### 2026-09-27 14:26:34.000Z - Feature closeout (Phase 1 scope)

The plan's own parse failure was discovered when the orchestrator's `set_status` call failed with the wrapped `html_inline '<d>'` error -- the exact failure class REQ-001's `repair` prompt targets. Repaired per that prompt's own rules (the bare `<d>` tokens wrapped in code spans, frontmatter preserved, oracle `parse_feat` green), together with two further model violations the `<d>` error had masked: the `Phase 1a:` Task List heading (changed to the repo-standard `Phase 0:` prerequisite heading -- no existing phase or task number renumbered) and the two-paragraph 2026-09-25 19:49:40.000Z update entry (merged into the single paragraph the model allows, no text change). Marked done: Tasks 1a.7/1.5 (both phase-end gates ran green; the phases committed as 5c94030 and b82eef4) and ACC-001/002/015/016 (evidence: the `repair` prompt registered with its instructions verified against the code; two ACC-002 smoke runs, the second on the refined narration, passed end-to-end with zero improvisation; the 12-domain `ParseFailureResult` tests plus a live smoke; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c accepted and recorded). The implementation commit list is recorded under Related PRs / Commits. Status moves to `review` via the orchestrator's `set_status` call; Phases 2-6 remain unstarted (user scope: Phase 1 only).

#### 2026-09-27 11:22:10.000Z - Task 1a.8: Option B amendment pass applied at every remaining site; follow-up issue #162 filed

Applied the Option B amendment pass (text/docstring/description only -- no code-behavior changes): (1) ADR 9080b37c body -- Decision Outcome item 3 rewritten to the qualified invariant (same parse defect, identical field path and cause; the trailing pydantic documentation line may differ by read order/cache state, so the two are the same defect, not byte-equal text; Option B, 2026-09-26; str-faithful reconstruction tracked as follow-up issue #162; tests relaxed accordingly, upgrade-ready re-tightening per #162's doc-restoration list), item 2's "matches `list_feat`'s failed-row error text" phrasing aligned to it, and the Confirmation section qualified likewise (title/H1/frontmatter untouched). (2) `ParseFailureResult` module + class docstrings (`general/models/parse_failure_result.py`). (3) `find_parse_failure` docstring + the module-docstring companion passage (`general/tools/_doc_paths.py` -- the passage was an unlisted site, qualified too). (4) `find_feat_parse_failure` docstring (`feat/tools/_paths.py`). (5) All 12 `get_<d>` tool descriptions + Returns-section docstrings (ADR citation kept; the code side drops the issue number for brevity -- "Option B, 2026-09-26 -- the str-faithful reconstruction is tracked as a follow-up issue" -- consistent across all 12). (6) `general/data/general_repair_instructions.md` step 1 with-id line (narration voice: same parse defect, treat the two texts as the same defect, not byte-equal). (7) `general/prompts/repair.py` module docstring + `@mcp.prompt` description. (8) `.opencode/agent/doc-repairer.md` + `.opencode/skill/repair/SKILL.md` (both repeated the claim; qualified in their voice). (9) `AGENTS.md` repair description clause + Phase 1a `ParseFailureResult` note (the latter also carries issue #162). (10) `CHANGELOG.md` -- the `repair` `Added` entry clause, the Phase 1a `Changed` entry (issue #162 cited), and that entry's stale "narrates reading the wrapped parse error from `get_<d>(id)`" forward reference updated to the non-raising `ParseFailureResult`-shaped-result wording. (11) `server.py` module docstring -- the Phase 1a note (issue #162 cited) + the `repair` line. (12) `tests/general/prompts/test_repair.py` -- the pinned narration wording replaced (now asserts the same-parse-defect and not-byte-equal phrasing). (13) The 12 `tests/<d>/tools/test_get_<d>.py` consistency tests relaxed from strict `get_error == list_row_error` to content-based: a per-file `_strip_pydantic_footer` helper strips the optional trailing pydantic documentation line (regex per the plan) from both texts before the equality, plus the core defect content of the fixture's structural parse failure asserted present in both -- each site carries the one-line Option B comment (restore plain equality when issue #162 ships; see its doc-restoration list). `tests/general/tools/test__doc_paths.py` and `tests/general/models/test_parse_failure_result.py` checked: no `error`-text identity assertions live there (simulated-reader / pure-model tests), untouched. Filed the Option A follow-up issue: **#162** (https://github.com/dfch/biz.dfch.SpecMgr/issues/162) with its full spec (root cause, impact surface, acceptance criteria, doc-restoration list). Regenerated docs: `specmgr docs` + `specmgr mcp-docs` (docs/MCP.md + 16 docs/api pages: the 12 get tools, `repair`, `_doc_paths`, `feat/_paths`, `parse_failure_result`, `server`); `specmgr adr-toc` verified a no-op (docs/adr/README.md untouched -- ADR title/status unchanged). Quality gate green: `ruff format --check` (1723 files already formatted), `ruff check` (all checks passed), `vulture` (no output), `pytest -n auto --cov=src` (3481 passed), and the second-regeneration no-op drift checks (`git diff --exit-code`) for all three doc generators. Awaiting the orchestrator's commit.

#### 2026-09-26 17:01:41.000Z - ACC-002 re-run passed on the refined narration; error-text identity claim refuted -- Option B chosen

Re-ran the ACC-002 smoke test against the refined (Phase 1a-based) narration: the with-id branch now works end-to-end with zero improvisation for `req` -- direct `get_req` on the broken fixture returned `ParseFailureResult` (defect + absolute `path`, returned NOT raised), raw read -> smallest fix -> one green `validate(full=True)` -> byte-exact write-back -> post-write `get_req` returned the parsed document (`level: MUST`); `list_req` `error_count` 0; a truly absent id still raises the domain not-found error; fixture cleaned up, tree clean. The audit, however, refuted the documented "`error` is byte-identical to `list_<d>`'s failed-row `error`" invariant: `DocCache` re-raises a *reconstructed* exception on every warm cache hit (`general/tools/_doc_cache.py::_fresh_exception`), and its `ValidationError` reconstruction drops pydantic's trailing documentation line ("For further information visit https://errors.pydantic.dev/...") -- so `get_<d>`'s `error` (always a warm read: its own id-scan precedes the helper's read) is footer-less while a first `list_<d>()` row in a process is footer-carrying; identity holds only by read-order luck (fresh process, get-first: equal; list-first: not -- proven in fresh-process ordering tests). Functionally harmless (both variants pin the same fix). Per the user decision (2026-09-26), Option B: qualify the claim at every site now (this update covers REQ-013/ACC-015; Task 1a.8 covers the rest) and defer the str-faithful reconstruction (Option A -- ~2-4x the effort, risk concentrated in shared feat-107 plumbing, no functional need today) to a follow-up issue carrying its full spec. Pre-existing wart also noted for that follow-up: `list_<d>()`'s row `error` text is itself unstable across repeated calls in one process (footer on first read, footer-less on warm re-reads).

#### 2026-09-26 13:15:00.000Z - Phase 1 `repair` narration refined to the committed Phase 1a contract

After Phase 1a's commit (5c94030), refined the `repair` feature's wording to REQ-013's `get_<d>` contract: (1) `general/data/general_repair_instructions.md` -- step 1's with-id branch now reads the non-raising parse-failure result `get_<type>(id)` returns (`error` -- the parse-failure message, the same text `list_<type>()`'s failed row carries -- plus the absolute `path`) instead of a raised, wrapped parse error, and covers the truly-absent-id case (still raises the domain's not-found error -> ask via `question`, or scan `list_<type>()`'s failed rows) and the parses-cleanly case (nothing to repair -> report and stop); step 1's without-id branch now describes the row's `error` as the parse failure (field path and cause -- a 1-based line reference and fix hint for structural failures, the violated pattern and offending value for closed-vocabulary failures); step 6's with-id states the new success/failure shapes (success is the parsed document -- a real parse of the real file on disk -- rather than a result carrying `error`; if it still returns the `error`/`path` result the on-disk file is still broken -> re-read, compare against the validated text, fix, repeat from step 4); steps 2-5, the no-`update` notes, the frontmatter-preservation rule, the diagnose-only degradation, and the scope/ADR exclusion are unchanged. (2) `general/prompts/repair.py` -- module docstring and `@mcp.prompt` `description` updated to the new mechanism (the result-carries-`error`/`path` wording, every one of the whole-body domains, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c cited); behavior and the `Raises` section unchanged. (3) `tests/general/prompts/test_repair.py` -- the assertions pinning the old wording replaced (`test_get_parse_failure_result_named` for the with-id result, the without-id parse-failure wording, the step-6 with-id shapes); every test that remained true (registration, packaged-data, `ValueError`s, interpolation, post-write confirmation, diagnose-only, ADR exclusion) is unchanged -- all 21 pass. (4) Docs sync for the `repair` feature only: the `repair` descriptions in AGENTS.md's `general/` bullet, CHANGELOG's `## [Unreleased]` `Added` entry, and `server.py`'s module docstring now carry the non-raising `ParseFailureResult`-shaped-result wording (ADR 9080b37c cited); the Phase 1a portions of those files are untouched, and `specmgr docs`/`specmgr mcp-docs` were regenerated. (5) The same uniform with-id/step-6 wording was also applied to `.opencode/agent/doc-repairer.md` and `.opencode/skill/repair/SKILL.md` (see Decisions Made).

#### 2026-09-25 19:49:40.000Z - Phase 1a (`get_<d>` parse-failure error channel) implemented, gate green

Implemented Tasks 1a.1-1a.6 (REQ-013 / ACC-015 / ACC-016): (1) a new shared, non-raising `ParseFailureResult` model (`general/models/parse_failure_result.py`, fields `error`/`path`/`id`) mirroring `InvalidStatusResult`'s shape and registered in `general/models/__init__.py` -- the third member of the ADR 519d1206 client-side-`isError`-truncation workaround chain after `validate` and `set_status`'s invalid-status case (ADR b399f1ce). (2) A new shared helper `general.tools._doc_paths.find_parse_failure(base_dir, id_, read_fn) -> tuple[Path, str] | None` for the 11 flat-file domains (scans for the single file whose stem encodes `id_` as a hyphen-bounded token -- the flat-file naming is `<type>-<id>-<slug>.md`, so a bare `stem.startswith(f"{id_}-")` prefix would never match -- and reports a parse-failing file's `(path, str(exc))`, `None` otherwise; `find_doc_path_by_id`'s documented skip behavior is unchanged) plus a bespoke `feat.tools._paths.find_feat_parse_failure(base_dir, id_)` for `feat` (no scan -- the folder name IS the id). (3) All 12 `get_<d>` tools now, on the domain's `XNotFoundError` from `load_by_id`, run the helper, `assert_within`, and return `ParseFailureResult(error, path, id)` (a truly absent id still re-raises; `raw=True` on a broken document never returns raw text); the return annotation widens to `<D>Document | str | ParseFailureResult` and the description/docstring note is worded consistently across all 12. (4) A new ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to `get_<d>`'s parse-failure case", status `accepted`) + `specmgr adr-toc`. (5) Tests: per-domain (all 12: broken / `raw=True`-broken / healthy / absent / invalid-shape), the `error`-text consistency vs `list_<d>` (all 12), the shared-helper unit tests, and the model test. (6) Docs sync: `server.py` module docstring, `AGENTS.md` `general/` bullet, `CHANGELOG.md` (`Added` + `Changed`), `specmgr docs`/`specmgr mcp-docs` (which also pick up the uncommitted Phase 1 `repair` prompt -- expected and flagged for the commit message). The `error`-text consistency invariant holds because both `ParseFailureResult.error` and the `list_<d>` failed-row `error` are `str()` of the same domain parse exception captured through the same cache-backed `read_<d>` reader; the `get_<d>` path deliberately does NOT reuse `load_by_id`'s own wrapped "could not be read as a valid ... document" message (which prepends tool-specific framing that `list_<d>` does not carry).

#### 2026-09-25 09:08:00.000Z - Phase 1 (repair) implemented, gate green

Implemented Tasks 1.1-1.4: (1) `general/prompts/repair.py` (`repair(type, id=None)`, registered in `general/prompts/__init__.py`) with its instructions in `general/data/general_repair_instructions.md` -- the full REQ-001 loop: discovery (`get_<d>(id)`'s wrapped enriched parse error with an id, `list_<d>()`'s `<failed to parse>` failed row without), the host-native raw read and write-back with the explicit note that no specmgr MCP tool can return the raw content of a document that fails to parse and that the generic `update` tool is structurally unable to repair one, the frontmatter `id`/`created`/`status`/`version` byte-for-byte preservation + `updated`-untouched rule, the `validate(type, content, full=True)` loop, the post-write `get_<d>(id)`/`list_<d>()` confirmation against the file as it now exists on disk, the diagnose-only degradation, and the ADR exclusion; `type` validates against `general.tools._domains.WHOLE_BODY_DOMAINS` (single source of truth) and fails fast with an actionable `ValueError` for `adr`/unknown/blank inputs, case-insensitively. (2) `.opencode/agent/doc-repairer.md` (explicit `read`/`glob`/`grep`/`list`/`question`/`todowrite` allows, workspace-wide `edit`/`write` allows, `task`/`bash` denies, plus an explicit `external_directory: deny` -- see Decisions Made) and `.opencode/command/repair.md` (`$1`/`$2` positionals, `agent: doc-repairer`). (3) `.opencode/skill/repair/SKILL.md` (REQ-012: `name: repair`, a trigger description for organically-encountered failed-to-parse documents, a thin body deferring to `doc-repairer` via `task` when available, else the condensed host-native loop). (4) `tests/general/prompts/test_repair.py` (21 tests: content assertions on the rendered instructions including ACC-001's key post-write-confirmation assertion, fast-fail `ValueError` tests, packaged-data fresh-read/`FileNotFoundError` tests, and live `mcp.list_prompts()` registration), plus the docs sync (AGENTS.md `general/` bullet, `server.py` module docstring, regenerated `docs/api/`+`docs/GENERATED.md`+`docs/MCP.md`, CHANGELOG `## [Unreleased]` entry). Task 1.5's quality gate is green; the orchestrator makes the single Conventional Commit.

#### 2026-09-24 20:57:10.000Z - Plan refined after full review pass

Reviewed the plan against the codebase, the OpenCode docs/config schema, and issue #150's five items (all remain covered). Corrected `repair`'s write-back mechanism (host-native file write, not the generic `update` tool -- whose adapters re-parse the existing document and raise the domain not-found error before any write: `req/tools/_io.py:72-112`), made `refine_feat` fully MCP-native via `get_feat(raw=True)`/`update(type="feat")`/`validate(type="feat")`, split the old REQ-009 into packaging (REQ-009) and the installer command (REQ-010), aligned the review-fix loop's exit criterion with its task-derivation set (Errors/Gaps/Inconsistencies), added the ready-to-paste fix-phase block shape and the implementer-appends delegation step, extended scope to the 4th existing OpenCode file (`review-feature.md`'s stale section enumeration, plus `implement-feature.md`'s "a a" typo), added per-phase docs-sync tasks (Phases 2/4/5) and phase-end gate + one-commit tasks (all phases), moved the README section to directly after "Add to OpenCode", and renumbered the acceptance criteria to ACC-001..ACC-013.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26 17:01:41.000Z - Option B: qualify the get/list error-text consistency claim now; defer Option A (str-faithful cache reconstruction) to a follow-up issue

User decision (2026-09-26), after the ACC-002 re-run audit refuted the byte-identical error-text invariant (root cause: `DocCache._fresh_exception` drops pydantic's footer line on warm re-raises). Chosen over Option A (fix the reconstruction now): (a) no functional impact -- the smoke test proved the repair loop works with zero improvisation under either text variant; (b) Option A is ~2-4x the effort of B with its risk concentrated in one delicate shared function (feat-107 plumbing used by every read path; it must reproduce pydantic v2's `str()` byte-for-byte, including the versioned footer URL, while keeping fresh-exception semantics); (c) B is upgrade-ready -- every claim site is identified now and the 12 consistency tests are relaxed to content-based assertions at a known target state, so Option A's later ship is a small re-tightening (ADR line, docstrings, narration, REQ-013/ACC-015 wording, tests back to order-independent identity) rather than a rewrite; (d) the Phase 1a commit message's now-stale claim is immutable history -- the ADR/docstrings carry the qualified truth. Residual accepted cost until Option A ships: `list_<d>()` row text differs between consecutive calls in one process, and `get_<d>`/`list_<d>` texts can differ by exactly the trailing pydantic documentation line. The follow-up issue (filed under Task 1a.8) carries Option A's full spec: root cause, affected surface, acceptance criteria (cold == warm `str()` for ValidationError/AssertionError/YAMLError; order-independent get/list identity; list-row stability across calls), and the doc-restoration list.

#### 2026-09-26 13:15:00.000Z - Wording-refinement scope: the doc-repairer/SKILL copies updated too

The refinement's explicit change list named `general_repair_instructions.md`, `repair.py`, `test_repair.py`, and the `repair`-specific wording in AGENTS.md/CHANGELOG/`server.py`, but not the `.opencode/agent/doc-repairer.md` and `.opencode/skill/repair/SKILL.md` copies. Settled: apply the same minimal wording updates there (with-id discovery, step-6 confirmation shapes, the skill's trigger description) as well, because those files narrate the same with-id mechanism to a runtime LLM -- leaving them stale would ship instructions factually wrong for 11 of the 12 whole-body domains under REQ-013 (`get_<d>` returns a result, it does not raise the wrapped error) -- and the plan's own Design Notes make prompt \<-> agent \<-> command wording sync a standing review-checklist item. If the orchestrator prefers the `.opencode` files to stay as-committed until a later pass, that is a revert of a few small hunks.

#### 2026-09-25 19:49:40.000Z - `get_<d>` parse-failure error channel: explicit error attribute on the result, narrow get-only scope

User decision (2026-09-25), after cost analysis: an explicit error attribute on the `get_*` result (a non-raising `ParseFailureResult`), chosen over exception enrichment. Rationale: ~0 tokens on the success path (the MCP SDK serializes with `model_dump(exclude_none=True)`, so the new union member only materializes on the failure path); host-independent delivery per the ADR 519d1206 chain (today's smoke test reproduced the truncation on this OpenCode host -- `get_req`'s exception text was swallowed to a bare "Error executing tool get_req" while `list_req()`'s failed-row `error` passed intact); and the union-result precedent already twice established (b399f1ce). Scope is deliberately narrow and get-only: a shared `find_parse_failure` helper for the 11 flat-file domains + a bespoke `feat` one, with `find_doc_path_by_id`'s skip behavior and `update`/`delete`/`set_*`/`validate`/`list_references` all unchanged. This is the third documented asymmetric tool contract in the ADR 519d1206 chain (after `validate` and `set_status`'s invalid-status case), recorded in ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c.

#### 2026-09-25 09:08:00.000Z - doc-repairer: explicit external_directory deny (workspace-only writes)

REQ-002's permission list names `read`/`glob`/`grep`/`list`/`question`/`todowrite` (allow), `edit`/`write` (allow workspace-wide), `task`/`bash` (deny) but leaves `external_directory` open. Chosen: an explicit `external_directory: {"*": deny}` entry, over (a) leaving it at OpenCode's default `ask` and (b) mirroring `ref-finder`'s allow-list. Rationale: `doc-repairer` is the one agent in the set that WRITES document files, so an out-of-workspace write surface should be a deliberate, user-approved act -- an explicit deny makes the scope boundary mechanical (a `SPECMGR_*_DIR` pointing outside the workspace is a misconfiguration the agent reports, not a file it silently edits), and it keeps REQ-002's "declare every permission it relies on explicitly" reading consistent: the agent relies on workspace-only file access. The agent body's Hard rules name this explicitly ("Stay inside the workspace ... stop and report"). `ref-finder` stays unchanged (read-only, its allow-list is about its own global-config reads).

#### 2026-09-25 08:30:00.000Z - Added REQ-012 (OpenCode Skill) and REQ-001's post-write confirmation step

Two follow-up decisions from QA 76229d40-55e9-4640-9249-c391e1f3e84c: (1) Added REQ-012/ACC-014/Task 1.2b for `.opencode/skill/repair/SKILL.md` (question 0.0020), a thin skill that self-triggers on an organically-encountered failed-to-parse document and defers to `doc-repairer` via the `task` tool; flagged as a known, deliberately deferred gap that Phase 5's REQ-009/REQ-010 packaging/installer does not yet cover the new `skill/` directory. (2) Extended REQ-001/ACC-001/Task 1.1/Task 1.3 with a post-write confirmation step: after the host-native write-back, `repair` must call `get_<d>(id)` (or `list_<d>()` without an `id`) again to confirm the file as it now exists on disk actually parses, since the pre-write in-memory `validate` result cannot prove what the host's file-write tool put on disk; Task 1.3's own test can only assert the instructions narrate this step, since an MCP prompt is narration-only and cannot execute a real repair itself.

#### 2026-09-25 08:00:00.000Z - Renamed `make_valid`/`doc-fixer` to `repair`/`doc-repairer`

Resolved via QA 76229d40-55e9-4640-9249-c391e1f3e84c, question 0.0010 (reopened after an earlier "confirmed as-is" pass): `make_valid` broke the repo's short, bare-word naming precedent for cross-cutting, type-dispatched tools/prompts (`validate`, `delete`, `list_references`) and did not match the `doc-fixer` subagent's own fix-oriented naming. Renamed the MCP prompt to `general.prompts.repair(type, id=None)`, the OpenCode command to `/repair` (`.opencode/command/repair.md`), and the OpenCode subagent to `.opencode/agent/doc-repairer.md` -- `repair` pairs naturally with the existing `validate` tool ("validate, then repair") and `doc-repairer` now shares the same verb root as the prompt/command it wraps. Applied throughout this README (Requirements, Acceptance Criteria, Scope, Dependencies, Design Notes, Task List) before Phase 1 implementation started, so this is a pure planning-doc rename with zero migration cost.

#### 2026-09-24 20:57:09.000Z - Phase discipline: one commit per phase, full quality gate before it

User requirement (2026-09-24): each phase is exactly one Conventional Commit, preceded by the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches), with the phase's docs sync inside the same commit. Enforced via a phase-end gate task per phase in the Task List and a Design Notes section.

#### 2026-09-24 20:57:08.000Z - Review-fix loop exits when no Errors, Gaps, or Inconsistencies remain

Chosen over "no Errors/Gaps" so the loop's exit criterion matches REQ-007's task-derivation set (a fix phase derives tasks from Errors/Gaps/Inconsistencies); Code Smells/Improvements/Positives stay advisory. The 3-cycle cap is unchanged.

#### 2026-09-24 20:57:07.000Z - Packaging: root .opencode/ canonical, generated package copy with drift check

The wheel only ships what lives under `src/`, so the installable OpenCode file copy is generated under `general/data/opencode/{agent,command}/` from the repo-root `.opencode/` by `specmgr opencode sync`, guarded by a pre-commit local drift hook and a CI parity check -- the same two-copy pattern the repo already runs for the packaged JSON Schema copies. Alternatives considered and rejected: package-copy-canonical (changes the repo's own dev workflow) and a build-time copy hook (non-standard build machinery).

#### 2026-09-23 09:03:00.000Z - repair implemented first, independent of the new ADR

The portable-prompt-narrates-delegation ADR (Phase 3) is only needed by Phase 4 (`implement_feat`/`review_feat`); `repair` has no such dependency, so it was moved to Phase 1 and the ADR moved to Phase 3.

#### 2026-09-23 09:02:00.000Z - Portable prompt + optional host-delegation pattern

`implement_feat`/`review_feat` narrate delegation via the host's own task-delegation tool when present, degrading to direct implementation otherwise, rather than either (a) requiring OpenCode specifically or (b) losing real subagent orchestration. See Design Notes.

#### 2026-09-23 09:01:00.000Z - Review-fix loop capped at 3 cycles

Chosen over an uncapped loop to bound the automatic review-to-fix-to-re-review cycle; remaining findings after 3 cycles go to the user instead.

#### 2026-09-23 09:00:30.000Z - `.opencode/agent`/`command` singular naming confirmed correct

No rename needed -- OpenCode accepts singular and plural directory names at both global and project scope.

### Related PRs / Commits

- PR: https://github.com/dfch/biz.dfch.SpecMgr/pull/155 (plan refinement, 2026-09-24; implementation of the Phase 1 scope merged into the same PR, 2026-09-27)

- Commits: 5c94030 (Phase 1a + Phase 1 initial), b82eef4 (Phase 1 narration refinement), af93f96 (Option B decision record), 10a4b62 (Task 1a.8 Option B amendment pass, issue #162)

### More Information

Source: https://github.com/dfch/biz.dfch.SpecMgr/issues/150
