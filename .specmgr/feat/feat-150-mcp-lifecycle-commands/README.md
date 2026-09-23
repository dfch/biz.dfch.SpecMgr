---
classification: null
created: '2026-09-23 23:16:12.456+02:00'
id: feat-150-mcp-lifecycle-commands
status: planning
type: feat
updated: '2026-09-23 23:16:19.527+02:00'
version: 1.0.0
---

# Feature: MCP-Native Feature-Lifecycle Commands (make_valid, refine_feat, implement_feat, review_feat) + OpenCode Distribution

## Plan

### Overview

GitHub issue #150 asks for five related capabilities that round out the feature/document lifecycle already partially covered by ad hoc OpenCode-only files: (1) a command that repairs an artifact that currently fails to parse, (2) a portable, MCP-native version of the OpenCode-only `implement_feature` workflow, (3) an automatic post-implementation review-and-fix-phase follow-up, (4) a pre-implementation plan-refinement command, and (5) an easy way to get these OpenCode-native commands onto a fresh OpenCode install (and guidance for other hosts, e.g. Claude Code).

The unifying design principle (see Design Notes) is: every new capability gets a **portable MCP prompt** (narration-only text, works in any MCP host, following the existing `create_*`/`update_*`/`implement_task`/`refine` precedent) *and*, where real file-editing/iteration/multi-agent delegation is required, a **richer OpenCode-native subagent + command** with real permission enforcement (mirroring the existing `phase-orchestrator`/`phase-implementer`/`feat-reviewer`/`ref-finder` precedent). The portable prompt narrates delegation via the *host's own* subagent-delegation tool (e.g. OpenCode's `task` tool) when available, exactly like every existing prompt already narrates host-native tools it doesn't implement itself (`question`, `TodoWrite`) -- it degrades to direct single-session implementation when no such tool exists.

**Phase ordering is deliberately make_valid-first**: `make_valid` (Phase 1) has no dependency on the ADR that Phase 4 (implement_feat/review_feat) needs, so it can be implemented, tested, and shipped standalone before any other phase.

### Requirements

- REQ-001: A new `general/prompts/make_valid.py` MCP prompt narrates discovering a failed-to-parse document (via `list_<d>`'s failed-row `path`/`error`), editing the raw file to address the enriched error, and looping the generic `validate(type, content, full=True)` tool to green before writing back.

- REQ-002: A new `.opencode/agent/doc-fixer.md` subagent (edit/write allowed, `task` denied) implements REQ-001's loop with real file access, plus a `.opencode/command/make-valid.md` (`/make-valid <type> <id>`) wrapper.

- REQ-003: A new `feat/prompts/refine_feat.py` MCP prompt narrates a pre-implementation plan-readiness review (testable ACs, phase ordering/dependencies, scope clarity, unresolved decisions) against an existing `.specmgr/feat/<id>/README.md`, asking the user via the `question` tool and then editing the plan directly.

- REQ-004: A new `.opencode/agent/feat-planner.md` subagent (edit allowed, scoped to the plan README; `task` denied) implements REQ-003 with real file access, plus `.opencode/command/refine-feature.md` (`/refine-feature <id>`).

- REQ-005: A new `feat/prompts/implement_feat.py` MCP prompt narrates orchestrator discipline (read plan, phase-by-phase `TodoWrite`, delegate each phase via the host's subagent-delegation tool when available, verify before advancing, never write code directly), falling back to direct single-session implementation when no delegation tool exists.

- REQ-006: A new `feat/prompts/review_feat.py` MCP prompt narrates `feat-reviewer.md`'s existing review checklist and fixed report format portably.

- REQ-007: `.opencode/agent/feat-reviewer.md`'s report format gains a new, conditional "Proposed Fix Phase" section: a ready-to-append phase (numbered tasks derived strictly from its own Errors/Gaps/Inconsistencies), explicitly flagging any item that needs a user decision rather than guessing at one.

- REQ-008: `.opencode/agent/phase-orchestrator.md` (and `implement_feat`'s narration) gain a final review-fix loop: after the plan's phases complete, run the reviewer; if it proposes a fix phase, resolve any flagged decisions with the user via `question`, then delegate the fix phase to one more `phase-implementer` cycle exactly like a normal phase; repeat until the reviewer reports no Errors/Gaps left, capped at 3 review-fix cycles (after which remaining findings are handed to the user instead of auto-fixed again).

- REQ-009: A new `specmgr opencode install [--global|--local] [--force]` CLI subcommand packages this repo's `.opencode/agent/*.md` + `.opencode/command/*.md` files as package data and copies them to `~/.config/opencode/` (global) or `./.opencode/` (local).

- REQ-010: README.md documents the manual/Claude-Code path: Claude Code's structurally similar `.claude/agents/*.md`/`.claude/commands/*.md` convention is called out explicitly, along with the permission-model gap (OpenCode's per-pattern bash/edit rules vs. Claude Code's coarse tool allow-list) that means these are hand-ported, simplified equivalents, not an automatic translation.

### Acceptance Criteria

- [ ] ACC-001: `make_valid(type, id)` MCP prompt exists, is registered, and its instructions correctly reference `list_<d>`/`validate`/`update`.

- [ ] ACC-002: `/make-valid <type> <id>` successfully drives `doc-fixer` to repair a deliberately-broken fixture document (parse fails before, succeeds after) in a manual smoke test.

- [ ] ACC-003: `refine_feat(id)` MCP prompt exists and is registered.

- [ ] ACC-004: `/refine-feature <id>` successfully edits a fixture plan's README in place after a manual smoke test.

- [ ] ACC-005: `implement_feat(id)` MCP prompt exists, is registered, and its instructions explicitly name the host's task-delegation tool as optional (never assumed present).

- [ ] ACC-006: `review_feat(id)` MCP prompt exists and is registered.

- [ ] ACC-007: `feat-reviewer.md`'s report format documents the "Proposed Fix Phase" section and its decision-flagging rule.

- [ ] ACC-008: `phase-orchestrator.md`'s workflow documents the capped (3-cycle) review-fix loop.

- [ ] ACC-009: `specmgr opencode install --local` and `--global` both copy every `.opencode/agent/*.md` + `.opencode/command/*.md` file to the target location, refuse to overwrite without `--force`, and are covered by unit tests.

- [ ] ACC-010: README.md has a new section documenting the CLI installer and the manual Claude Code path.

- [ ] ACC-011: `AGENTS.md`, `docs/GENERATED.md`/`docs/MCP.md`, `CHANGELOG.md`, and `server.py`'s module docstring are updated to list the 4 new MCP prompts.

- [ ] ACC-012: A new ADR documents the "portable MCP prompt narrates optional host-native subagent delegation" pattern.

### Scope

#### Included

- 4 new MCP prompts (`make_valid`, `refine_feat`, `implement_feat`, `review_feat`) and their packaged instruction data files.

- 2 new OpenCode subagents (`doc-fixer`, `feat-planner`) and 2 new OpenCode commands (`/make-valid`, `/refine-feature`).

- Targeted edits to the 2 existing OpenCode files (`feat-reviewer.md`, `phase-orchestrator.md`) for the review-fix loop; `implement-feature.md` gets a short doc update mentioning the automatic review step.

- New `specmgr opencode install` CLI subcommand + packaged `.opencode` data + tests.

- README/AGENTS.md/CHANGELOG/generated-docs updates.

- One new ADR for the portable-prompt-narrates-delegation pattern.

#### Explicitly Out Of Scope

- Any change to `.opencode/agent/phase-implementer.md`, `.opencode/agent/ref-finder.md`, `/refs`, or `/release` (unaffected).

- Building an OpenCode plugin (`config()` hook) for zero-copy distribution -- noted as a possible future enhancement, not built now.

- Auto-generating Claude-Code-flavored `.claude/agents`/`.claude/commands` files from the OpenCode ones -- hand-ported/simplified equivalents are documented instead, given the permission-model mismatch.

- Any change to the generic `validate`/`update`/`set_status` tools themselves (REQ-001/002 build on them as-is).

- Enforcing any of this via pre-commit/CI (matches the repo's existing "no `validate_adr`-in-CI yet" gap, unaffected by this feature).

### Dependencies

#### Depends On

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 / c4efbde6-fd19-4aa8-8668-95316ed62dcc (dispatch-only domain convention, followed by `make_valid`'s generic shape).

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

- feat-27-validation / feat-81-83-validation (the enriched validate errors and failed-row `list_<d>` mechanism `make_valid` builds on).

- feat-31-feature (the `feat` domain itself).

- Phase 4 (implement_feat/review_feat) depends on Phase 3's new ADR; Phase 1 (make_valid) deliberately does not.

#### Blocks

- None known.

### Design Notes

**Portable-prompt-narrates-delegation pattern (the item-2 resolution).** An MCP prompt never executes tool calls itself -- it returns text to whatever LLM session invoked it, exactly like every existing prompt in this codebase (`create_req` says "use the `question` tool"; neither `question` nor `TodoWrite` is implemented by this MCP server). `implement_feat`/`review_feat` extend this same precedent one step further: they narrate delegating work to a subagent via "your host's task-delegation tool, if one exists." Inside OpenCode, that's a real instruction to use the `task` tool (genuine multi-agent orchestration, since OpenCode exposes both the `specmgr` MCP tools and its own native tools in the same session). On a host with no such tool, the same text degrades to "implement it yourself, one phase at a time" -- never a hard failure. This is the subject of the new ADR (ACC-012), needed before Phase 4 but not before Phase 1.

**Review-fix loop cap.** Capped at 3 automatic review-fix cycles (configurable only in the prose instructions, not a hard machine limit -- these are markdown-narrated workflows, not code) to avoid an unbounded loop; any findings still open after 3 cycles are handed to the user instead of auto-fixed again.

**`.opencode/agent`/`command` singular directory naming is correct as-is** -- OpenCode accepts both singular and plural forms at both global and project scope (confirmed via the `customize-opencode` skill's authoritative reference table); no rename needed.

**Naming.** New OpenCode files: `doc-fixer.md` (agent) / `make-valid.md` (command); `feat-planner.md` (agent) / `refine-feature.md` (command). New MCP prompts follow the existing `<verb>_<domain>` convention: `general.prompts.make_valid` (cross-cutting, takes `type`+`id`, mirrors `general/tools/validate.py`'s shape), `feat.prompts.refine_feat`/`implement_feat`/`review_feat`.

**Distribution.** `specmgr opencode install` ships as a new Typer command in `cli.py`, backed by packaged data (the same `.opencode/agent`/`command` files, added as package data so they travel with the wheel). A future OpenCode-plugin-based (`config()` hook) zero-copy alternative was considered but is out of scope for this feature.

### Related Decisions

- New ADR (to be created before Phase 4): "Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent" -- architecture-level, affects any future `<verb>_feat`-style prompt, so it gets a full ADR per this repo's own ADR-vs-feature-log convention.

### Task List

#### Phase 1: make_valid (no ADR dependency -- implement first)

- [ ] Task 1.1: `general/data/general_make_valid_instructions.md` + `general/prompts/make_valid.py` + registration in `general/prompts/__init__.py`.

- [ ] Task 1.2: `.opencode/agent/doc-fixer.md` + `.opencode/command/make-valid.md`.

- [ ] Task 1.3: `tests/general/prompts/test_make_valid.py` (registration + template substitution, matching existing prompt test patterns).

- [ ] Task 1.4: Docs sync: `AGENTS.md`'s `general/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

#### Phase 2: refine_feat

- [ ] Task 2.1: `feat/prompts/refine_feat.py` + packaged instructions + registration.

- [ ] Task 2.2: `.opencode/agent/feat-planner.md` + `.opencode/command/refine-feature.md`.

- [ ] Task 2.3: Tests + manual smoke test (ACC-004).

#### Phase 3: ADR for portable-delegation pattern

- [ ] Task 3.1: Write and record the new ADR (see Related Decisions) -- needed before Phase 4.

#### Phase 4: implement_feat + review_feat + auto fix-phase loop

- [ ] Task 4.1: `feat/prompts/implement_feat.py` + packaged instructions + registration, narrating the optional-delegation pattern from Design Notes.

- [ ] Task 4.2: `feat/prompts/review_feat.py` + packaged instructions + registration, mirroring `feat-reviewer.md`'s checklist/report format.

- [ ] Task 4.3: Extend `.opencode/agent/feat-reviewer.md`'s report format with the conditional "Proposed Fix Phase" section + decision-flagging rule (REQ-007).

- [ ] Task 4.4: Extend `.opencode/agent/phase-orchestrator.md`'s Workflow section with the capped review-fix loop (REQ-008); update `.opencode/command/implement-feature.md`'s prose to mention it.

- [ ] Task 4.5: Update `implement_feat`'s narration to mention the same review-fix loop, for portable-host parity.

- [ ] Task 4.6: Tests + manual smoke test.

#### Phase 5: Distribution

- [ ] Task 5.1: `specmgr opencode install [--global|--local] [--force]` Typer subcommand in `cli.py`.

- [ ] Task 5.2: Package `.opencode/agent/*.md` + `.opencode/command/*.md` as installable package data (`pyproject.toml`/`MANIFEST` updates as needed).

- [ ] Task 5.3: Unit tests for the installer (copy behavior, `--force` overwrite guard, global vs. local target resolution).

- [ ] Task 5.4: README.md section: how to run the installer, plus the manual/Claude Code guidance (REQ-010).

#### Phase 6: Final Verification

- [ ] Task 6.1: Walk every Acceptance Criterion above with concrete evidence.

## Progress

### Current Status

**As of 2026-09-23**: Plan created, reordered so Phase 1 (`make_valid`) has no dependency on the ADR now scheduled for Phase 3. Not yet started -- a subsequent agent/session should pick up Phase 1 first (see Task List).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-23 09:00:00.000Z - Plan created

Investigated existing `.opencode/` agents/commands, the generic dispatch pattern, and OpenCode's own docs/skill for agent/command/plugin conventions, then drafted this plan against GitHub issue #150's 5 items, reordered per user request so `make_valid` (Phase 1) can be implemented and shipped standalone first. No implementation has started yet -- this commit is plan-only.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
