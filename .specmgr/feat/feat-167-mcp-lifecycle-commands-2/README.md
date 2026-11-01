---
classification: null
created: '2026-09-28T05:48:11.107+02:00'
id: feat-167-mcp-lifecycle-commands-2
status: review
type: feat
updated: '2026-11-01T16:41:33.451+01:00'
version: 1.0.0
---

# Feature: MCP-Native Feature-Lifecycle Commands II (refine_feat, implement_feat, review_feat) + OpenCode Distribution

## Plan

### Overview

This feature carries the remaining scope of GitHub issue #150 ("MCP-Native Feature-Lifecycle Commands") that was not yet started when that feature's own Phase 0 (`get_<d>` parse-failure error channel) and Phase 1 (`repair`) were implemented, reviewed, and merged as feat-150-mcp-lifecycle-commands. That feature is closed out at its Phase 0 + Phase 1 scope; the remaining four items -- (1) a portable, MCP-native version of the OpenCode-only `implement_feature` workflow, (2) an automatic post-implementation review-and-fix-phase follow-up, (3) a pre-implementation plan-refinement command, and (4) an easy way to get these OpenCode-native commands onto a fresh OpenCode install -- are tracked here, under GitHub issue #167.

The split (rather than continuing inside feat-150's own plan document) is because GitHub issue #163 (feat-163-feat-numbering) introduces a stricter FEAT Task List numbering scheme -- 3-digit `#### Phase NNN: {title}` headings and `- [ ] Task NNN.MMM: {text}` checklist items, both shape-enforced by the schema, gap-friendly and permanent once assigned -- with an explicit no-migration policy for existing plan documents. This feature is authored directly in that new scheme from the start, so it never needs migration, rather than mixing schemes inside feat-150's already-merged plan or renumbering already-shipped content referenced elsewhere in the repo (AGENTS.md, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c, `CHANGELOG.md`, `server.py`'s module docstring).

The unifying design principle carried over from feat-150 (see Design Notes) is unchanged: every new capability gets a **portable MCP prompt** (narration-only text, works in any MCP host, following the existing `create_*`/`update_*`/`implement_task`/`refine`/`compact_history`/`repair` precedent) *and*, where real file-editing/iteration/multi-agent delegation is required, a **richer OpenCode-native subagent + command** with real permission enforcement (mirroring the existing `phase-orchestrator`/`phase-implementer`/`feat-reviewer`/`ref-finder`/`doc-repairer` precedent). The distribution item (REQ-007/008/009) is the deliberate exception to the prompt half of that principle: its agent-facing carrier is the `specmgr://harness-bundle` resource's own `instructions` field, not a prompt (OpenCode exposes no MCP prompt surface to the agent -- see Design Notes).

**Phase discipline (user requirement, carried over from feat-150, 2026-09-24)**: every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches) and exactly one Conventional Commit; the phase's docs sync travels inside that same commit.

### Requirements

- REQ-001: A new `feat/prompts/refine_feat.py` MCP prompt, signature `refine_feat(id)`, narrates a pre-implementation plan-readiness review (testable ACs, phase ordering/dependencies, scope clarity, unresolved decisions) that is fully MCP-native: read via `get_feat(id, raw=True)`, ask the user via the `question` tool, apply edits via the generic `update(type="feat", id, content, offset/limit)` tool (line-range preferred), and re-check via `validate(type="feat", content, full=True)` -- host file tools only as a fallback when those specmgr tools are unavailable.

- REQ-002: A new `.opencode/agent/feat-planner.md` subagent implements REQ-001 with real file access, with its plan-README-only edit scope enforced mechanically rather than by prose: `edit`/`write` permission rules `{"*": deny, ".specmgr/feat/**/README.md": allow}` (OpenCode's `edit` permission patterns match file paths, last matching rule wins), `read`/`glob`/`grep`/`list`/`question`/`todowrite` allowed, `task` denied, `bash` denied -- plus `.opencode/command/refine-feature.md` (`/refine-feature <id>`, `agent: feat-planner`).

- REQ-003: A new `feat/prompts/implement_feat.py` MCP prompt narrates orchestrator discipline (read plan, phase-by-phase `TodoWrite`, delegate each phase via the host's subagent-delegation tool when available, verify before advancing, never write code directly), names the new delegation-pattern ADR (Phase 110) by UUID, mentions the REQ-006 review-fix loop, and falls back to direct single-session implementation when no delegation tool exists.

- REQ-004: A new `feat/prompts/review_feat.py` MCP prompt narrates `feat-reviewer.md`'s existing review checklist and report format portably, including the new conditional "Proposed Fix Phase" section (REQ-005).

- REQ-005: `.opencode/agent/feat-reviewer.md`'s report format gains a new, conditional "Proposed Fix Phase" section: a ready-to-paste block for the plan's `### Task List` -- a `#### Phase NNN: Fix phase (review cycle k)` heading using the next unused phase number (never renumbering existing phases) plus `- [ ] Task NNN.MMM` items derived strictly from the report's own Errors/Gaps/Inconsistencies (Code Smells/Improvements/Positives stay advisory), with any item that needs a user decision explicitly flagged `[NEEDS DECISION]` rather than guessed at.

- REQ-006: `.opencode/agent/phase-orchestrator.md` (and `implement_feat`'s narration, REQ-003) gain a final review-fix loop: after the plan's final verification phase, run the reviewer; if it proposes a fix phase, resolve any `[NEEDS DECISION]` items with the user via `question`, then delegate the fix phase to one more `phase-implementer` cycle exactly like a normal phase -- with the delegation prompt instructing the implementer to first append the reviewer's ready-to-paste block to the plan's Task List, since the orchestrator itself cannot edit files (`edit`/`write` are denied to it); repeat until the reviewer reports no Errors, Gaps, or Inconsistencies left, capped at 3 review-fix cycles (after which remaining findings are handed to the user instead of auto-fixed again).

- REQ-007: The repo-root `.opencode/{agent,command,skill}/` files remain the canonical working copy (singular directory names, per the 2026-09-23 decision; `skill/` holds one subfolder per skill, the only nested layout). A flat `specmgr harness-bundle` CLI command (`[cli]`-only -- no `mcp` import) deterministically enumerates every `*.md` under exactly those three top-level directories (recursive, sorted by `path`, exact directory-name match -- nothing else under `.opencode/` is bundled: `node_modules/`, `package.json`/`package-lock.json`, and similarly-named directories such as `zZz-skill/` are structurally excluded) into a single package-data file `general/data/general_harness_bundle.json` of shape `{"instructions": <module constant>, "files": [{"path", "sha256", "content"}]}` -- `path` relative to `.opencode/`, `content` the file's verbatim text, `sha256` of that text; serialized via `json.dumps(indent=2, ensure_ascii=False)` + trailing newline, no timestamps, so two runs over an unchanged tree are byte-identical. `pyproject.toml` gains the `[tool.setuptools.package-data]` entry for that one file; a pre-commit local drift hook (regenerate + fail on diff, files `^\.opencode/(agent|command|skill)/.*\.md$`, mirroring the existing `specmgr-schema-*` hooks) plus a CI parity check in the 3.13 job keep the bundle from drifting; the resource (REQ-008) serves the file via `read_packaged_text("general", "harness_bundle", "json")` (the `_packaged_data` convention), so it works identically from an editable checkout and a real, non-editable install.

- REQ-008: A new `specmgr://harness-bundle` MCP resource (`application/json`, `general/resources/harness_bundle.py`, the `rasci.py` pattern: `read_packaged_text` + a fail-fast parse on every call, the raw text returned unchanged) serves the bundle verbatim. The bundle's top-level `instructions` field (the module constant emitted by the REQ-007 generator) carries the complete agent-driven install protocol: pick the harness config root (project `./.opencode/` or global `~/.config/opencode/`) via the harness's own config skill (OpenCode: `customize-opencode`); per file, target = root + `path`, using the root's existing plural-variant directory (e.g. `agents/`) when one is already present there so no file is registered twice; missing target => write `content` byte-exact (no reformatting, rewrapping, or linting); sha256-identical target => skip; differing target => ask the user (OpenCode: the `question` tool) and write on approval; re-read and sha256-verify every write; report installed/skipped/updated/failed per file; never read/write/merge `opencode.json` (MCP server configuration stays the README's "Add to OpenCode" section's job). There is deliberately no install CLI, no `--force`, no sibling-directory detection code, and no MCP prompt for this flow: OpenCode exposes MCP *tools* but not MCP *prompts* to the agent (verified against a live session -- this server's registered prompts have no agent-visible surface, while `list_mcp_resources`/`read_mcp_resource` do), so the resource -- with its self-describing `instructions` field -- is the agent's sole discoverable entry point, and the install's overwrite policy becomes a conversational decision instead of a flag.

- REQ-009: README.md gains a new section placed immediately after the existing "Add to OpenCode" section (which it references for MCP server setup rather than duplicating): the agent-driven install (one line: ask your agent to install the specmgr harness files -- it reads `specmgr://harness-bundle` and follows the bundle's `instructions` field), what gets installed (every `.opencode/{agent,command,skill}/*.md` file), and the manual/Claude-Code path -- Claude Code's structurally similar `.claude/agents/*.md`/`.claude/commands/*.md` convention is called out explicitly with a short hand-ported frontmatter example, along with the permission-model gap (OpenCode's per-pattern bash/edit rules vs. Claude Code's coarse tool allow-list) that means these are hand-ported, simplified equivalents, not an automatic translation.

### Acceptance Criteria

- [ ] ACC-001: `refine_feat(id)` MCP prompt exists, is registered, and its instructions name `get_feat(id, raw=True)`, the generic `update` tool (`type="feat"`), and `validate` (`type="feat"`, `full=True`) as the read/apply/re-check path.

- [ ] ACC-002: `/refine-feature <id>` successfully edits a fixture plan's README in place after a manual smoke test.

- [ ] ACC-003: `implement_feat(id)` MCP prompt exists, is registered, and its instructions explicitly name the host's task-delegation tool as optional (never assumed present), the new delegation-pattern ADR (Phase 110) by UUID, and the review-fix loop.

- [ ] ACC-004: `review_feat(id)` MCP prompt exists, is registered, and mirrors `feat-reviewer.md`'s checklist and report format including the conditional "Proposed Fix Phase" section.

- [ ] ACC-005: `feat-reviewer.md`'s report format documents the "Proposed Fix Phase" section -- the ready-to-paste Task-List block shape (next unused phase number, `- [ ] Task NNN.MMM` items derived from Errors/Gaps/Inconsistencies only) and the `[NEEDS DECISION]` flagging rule.

- [ ] ACC-006: `phase-orchestrator.md`'s workflow documents the capped (3-cycle) review-fix loop, its exit criterion (reviewer reports no Errors, Gaps, or Inconsistencies), and the append-the-fix-phase delegation step (the implementer appends, not the orchestrator).

- [ ] ACC-007: The bundle file `general/data/general_harness_bundle.json` is byte-identical to a fresh `specmgr harness-bundle` run (the drift hook is green), contains exactly the enumerated `.opencode/{agent,command,skill}/` markdown files (sorted by `path`, each with a correct `sha256` and verbatim `content`), excludes everything else under `.opencode/` (`node_modules/`, `package.json`/`package-lock.json`, top-level or similarly-named directories), and `specmgr://harness-bundle` returns it verbatim (the returned text `json.loads`-parses to the same file list).

- [ ] ACC-008: An agent that follows only the bundle's `instructions` field installs every file into a fresh temp harness config root byte-exact (each written file's sha256 matches the bundle's), skips sha256-identical pre-existing files, and asks before overwriting a differing one -- pinned by a committed end-to-end walkthrough fixture (the feat-185-uc-diagrams ACC-002 precedent) -- and the generator's enumeration (completeness, ordering, exclusions, determinism) is covered by unit tests.

- [ ] ACC-009: README.md has the new section immediately after "Add to OpenCode", documenting the agent-driven install (referencing that section for server setup), what gets installed, and the manual Claude Code path.

- [ ] ACC-010: `AGENTS.md` (the `feat/` bullet), `docs/GENERATED.md`/`docs/MCP.md` (via `specmgr docs`/`specmgr mcp-docs` regeneration), `CHANGELOG.md`, and `server.py`'s module docstring list the 3 new MCP prompts, the new flat `specmgr harness-bundle` CLI command, and the new `specmgr://harness-bundle` resource -- each synced inside its own phase's single commit.

- [ ] ACC-011: A new ADR documents the "portable MCP prompt narrates optional host-native subagent delegation" pattern.

### Scope

#### Included

- 3 new MCP prompts (`refine_feat`, `implement_feat`, `review_feat`) and their packaged instruction data files.

- 1 new OpenCode subagent (`feat-planner`) and 1 new OpenCode command (`/refine-feature`).

- Targeted edits to 4 existing OpenCode files: `feat-reviewer.md` (the Proposed Fix Phase section) and `phase-orchestrator.md` (the review-fix loop) for the review-fix loop, `implement-feature.md` (doc update mentioning the automatic review-fix step, plus its "a a" typo fix), and `review-feature.md` (its body re-enumerates the report sections and would go stale without the new conditional section).

- The `.opencode/` layout normalization: the user-made-on-disk `skills/` -> `skill/` merge (4 skills; `skill/` is now the single skill directory, 6 skills, one subfolder each) committed, and the stale references it broke fixed -- 2 red test files in `tests/opencode/`, stale docstrings, `AGENTS.md`, `README.md` (Phase 125).

- Packaging: the single generated bundle file `general/data/general_harness_bundle.json`, the flat `specmgr harness-bundle` CLI command, the pre-commit drift hook, the CI parity check, and the `pyproject.toml` package-data entry (REQ-007).

- The `specmgr://harness-bundle` MCP resource with its `instructions`-field install protocol (REQ-008).

- The README.md section (agent-driven install + Claude Code path) + its Table of Contents entry (REQ-009).

- AGENTS.md/CHANGELOG/generated-docs/server.py-docstring updates, one per phase, inside that phase's own single commit.

- One new ADR for the portable-prompt-narrates-delegation pattern.

#### Explicitly Out Of Scope

- Any change to `.opencode/agent/phase-implementer.md`, `.opencode/agent/ref-finder.md`, `.opencode/agent/doc-repairer.md`, `/refs`, `/repair`, or `/release` (unaffected; `doc-repairer`/`repair` shipped under feat-150).

- Any change to `general/prompts/compact_history.py`.

- Any read/write/merge of the user's `opencode.json` by the install flow (MCP server configuration stays the README's documented job).

- Building an OpenCode plugin (`config()` hook) for zero-copy distribution -- noted as a possible future enhancement, not built now.

- Auto-generating Claude-Code-flavored `.claude/agents`/`.claude/commands` files from the OpenCode ones -- hand-ported/simplified equivalents are documented instead, given the permission-model mismatch.

- Any change to the generic `validate`/`update`/`set_status` tools themselves (this feature builds on them as-is).

- Enforcing any of this via pre-commit/CI (matches the repo's existing "no `validate_adr`-in-CI yet" gap, unaffected by this feature) -- except the REQ-007 bundle drift check, which is a build-consistency gate in the same class as the existing `specmgr-schema-*` hooks, not a document-validation gate.

- A `specmgr opencode install`-style CLI installer (sibling-directory detection, `--force`, `--global`/`--local` flags): replaced by the agent-driven install over the `specmgr://harness-bundle` resource (2026-10-31 re-scope, see Design Notes and Decisions Made).

- An ADR for the distribution/packaging decision itself: it was plan-scoped (this document's own Design Note, unshipped) with no prior ADR to overturn, so the 2026-10-31 re-scope rewrites this plan in place and records the decision under Decisions Made instead.

- A dedicated MCP prompt narrating the install flow: OpenCode exposes MCP tools but not prompts to the agent (verified against a live session), so the bundle's `instructions` field carries the protocol (REQ-008).

- Migrating feat-150-mcp-lifecycle-commands's own plan document (or any other pre-existing `.specmgr/feat/*/README.md`) to this document's Phase/Task numbering scheme -- out of scope for feat-163 itself, deferred to a future extension of the existing TSK `tsk-2687d267`.

### Dependencies

#### Depends On

- feat-150-mcp-lifecycle-commands (GitHub issue #150, Phase 0 + Phase 1: the `repair`/`ParseFailureResult`/`doc-repairer` precedent this work's prompt/agent/command shape follows; this feature is the split-off remainder of that same issue).

- feat-163-feat-numbering (GitHub issue #163): this document's own `Phase NNN`/`Task NNN.MMM` Task List numbering scheme.

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

- feat-27-validation / feat-81-83-validation (the enriched validate errors `refine_feat`'s `validate` re-check relies on).

- feat-31-feature (the `feat` domain itself, whose generic `update`/`validate` adapters make `refine_feat` fully MCP-native).

- The `specmgr-schema-*` pre-commit hooks as the model for REQ-007's bundle drift hook (the same two-copy + regenerate + fail-on-diff pattern, collapsed to one file).

- Phase 120 (`implement_feat`/`review_feat`) depends on Phase 110's new ADR (its UUID is an input to Phase 120's instruction files); Phase 100 (`refine_feat`) has no such dependency.

- Phase 125 (`.opencode/` layout normalization) precedes Phase 130 (the bundle is generated over the normalized tree); neither depends on Phases 100-120, so the distribution slice (125 + 130) can be implemented before any of them -- Phase 125 is complete (2026-10-31, commit `10b032f` + closeout; see Progress), so Phase 130 can start immediately at Task 130.100.

#### Blocks

- None known.

### Design Notes

**Phase discipline (user requirement, carried over from feat-150, 2026-09-24).** Every phase ends with the full quality gate -- `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, the full test suite `uv run --frozen pytest -n auto --cov=src --cov-report=`, plus every doc-drift check the phase touches (`specmgr docs`, `specmgr mcp-docs`, and `specmgr adr-toc` for Phase 110) -- and exactly one Conventional Commit for that phase; the phase's docs sync (server.py docstring, AGENTS.md bullet(s), CHANGELOG entry, regenerated docs) travels inside that same commit, never as a follow-up.

**`refine_feat` is MCP-native.** The plan README is a parseable document, so its whole read/apply/re-check path is specmgr tooling: `get_feat(id, raw=True)`, the generic `update(type="feat", id, content, offset/limit)` (line-range preferred, so unchanged regions stay byte-identical), and `validate(type="feat", content, full=True)`. Host file tools are only a fallback for hosts that cannot reach those tools.

**Portable-prompt-narrates-delegation pattern.** An MCP prompt never executes tool calls itself -- it returns text to whatever LLM session invoked it, exactly like every existing prompt in this codebase (`create_req` says "use the `question` tool"; neither `question` nor `TodoWrite` is implemented by this MCP server). `implement_feat`/`review_feat` extend this same precedent one step further: they narrate delegating work to a subagent via "your host's task-delegation tool, if one exists." Inside OpenCode, that's a real instruction to use the `task` tool (genuine multi-agent orchestration, since OpenCode exposes both the `specmgr` MCP tools and its own native tools in the same session). On a host with no such tool, the same text degrades to "implement it yourself, one phase at a time" -- never a hard failure. This is the subject of the new ADR (ACC-011), needed before Phase 120 but not before Phase 100.

**Prompt/agent/command text duplication is unavoidable.** OpenCode exposes MCP *tools* but not MCP *prompts* as slash commands (its MCP documentation covers tools only), so the OpenCode agent/command files cannot delegate to the packaged prompt text -- each carries its own copy of the same workflow. This duplication is accepted; keeping prompt \<-> agent \<-> command wording in sync is a standing review-checklist item (the `feat-reviewer` Consistency checklist already flags wording drift between paired artifacts).

**Review-fix loop (capped, aligned exit criterion).** Capped at 3 automatic review-fix cycles (configurable only in the prose instructions, not a hard machine limit -- these are markdown-narrated workflows, not code). The loop exits when the reviewer reports no Errors, Gaps, or Inconsistencies -- the same set REQ-005's fix phase derives tasks from (Code Smells/Improvements/Positives stay advisory), so a cycle never ends with the fix phase still re-deriving the same inconsistency. Any findings still open after 3 cycles are handed to the user instead of auto-fixed again. The orchestrator cannot append the proposed fix phase itself (`edit`/`write` are denied to it), so the fix phase's `phase-implementer` is delegated with an explicit first step: append the reviewer's ready-to-paste block to the plan's Task List (next unused phase number, no renumbering of existing phases).

**Packaging: root-canonical, single generated bundle file (user decision, 2026-09-24; re-scoped 2026-10-31).** The wheel only ships what lives under `src/` (`pyproject.toml`'s `[tool.setuptools.packages.find] where = ["src"]` + explicit `[tool.setuptools.package-data]` entries; there is no `MANIFEST.in`), so the installable harness files are a generated artifact -- one file, `general/data/general_harness_bundle.json`, under the `_packaged_data` convention. The repo-root `.opencode/` stays the canonical working copy; `specmgr harness-bundle` regenerates the bundle from it, and a pre-commit local drift hook (regenerate + fail on diff, scoped to `^.opencode/(agent|command|skill)/.*\.md$`) plus a CI parity check (3.13 job, alongside `specmgr docs`/`specmgr adr-toc`) keep the two from drifting -- the same two-copy pattern the repo already runs for the 12 packaged JSON Schema copies (the `specmgr-schema-*` hooks in `.pre-commit-config.yaml`), collapsed from a directory tree to a single file. The resource serves the file via `importlib.resources` (`read_packaged_text`), so it works identically from an editable checkout and a real PyPI install. Re-scoped 2026-10-31 (user decision, GitHub issue #167): the original design (a generated *tree* `general/data/opencode/{agent,command}/` + a `specmgr opencode sync`/`install` CLI with sibling-directory detection and `--force`) was replaced by this single-bundle + agent-driven-install design. Alternatives considered and rejected in 2026-09: package-copy-canonical (changes the repo's own dev workflow) and a build-time copy hook (non-standard build machinery); alternatives rejected in the 2026-10-31 re-scope: a manifest + per-file resource pair (no per-session cost benefit -- MCP resources are pull-based, content enters context only on read -- and install is a rare event, so the added surface buys nothing) and a markdown-delimited envelope (delimiter-collision risk; JSON is unambiguous and carries per-file `sha256` for free). No ADR: the replaced decision was plan-scoped and unshipped, with no prior ADR to overturn.

**Agent-driven install over the bundle resource (2026-10-31).** The bundle's `instructions` field is the entire install protocol; the agent of the active harness reads `specmgr://harness-bundle` (discoverable via `list_mcp_resources`) and installs per the protocol: harness config root via the harness's own config skill (OpenCode: `customize-opencode`), target = root + `path` (the root's existing plural-variant directory when present, so no file registers twice), byte-exact write, sha256 skip/ask/verify loop, `question`-tool drift policy, no `opencode.json` touch. The bundle is all-inclusive by design -- the new commands' dependency closure needs the existing agents (`/implement-feature` drives `phase-orchestrator` -> `phase-implementer`; `/refs` drives `ref-finder`; `/repair` drives `doc-repairer`, shipped under feat-150), and a partial install would silently break that closure. This replaces the planned `specmgr opencode install` CLI: the consumer of these files is an agent session (which already holds file-write permission and harness knowledge), "where to put files" is the harness vendor's own skill's job, and the overwrite policy becomes a conversational decision instead of a `--force` flag. Accepted costs: a first install burns tens of K tokens (read + write of the ~75 KB bundle, once per harness setup / specmgr upgrade), and determinism rests on the `instructions` byte-exact + sha256-verify mandate instead of a byte copy -- hence the pinned end-to-end walkthrough fixture (Task 130.150, the feat-185-uc-diagrams ACC-002 precedent). No MCP prompt carries the flow: OpenCode exposes MCP tools but not prompts to the agent (verified against a live session -- this server's registered prompts have no agent-visible surface while `list_mcp_resources`/`read_mcp_resource` do), so a prompt would be an undeliverable artifact.

**OpenCode permission model for the new agent.** `edit` permission patterns match file paths with the last matching rule winning (opencode.ai/docs/permissions), so `feat-planner`'s plan-README-only scope is mechanically enforced (`{"*": deny, ".specmgr/feat/**/README.md": allow}` on `edit`/`write`), not just prose discipline. The new agent denies `bash` and `task` and declares every permission it relies on explicitly (`read`/`glob`/`grep`/`list`/`question`/`todowrite`), matching the existing agents' explicitness.

**Naming.** `feat-planner.md` (agent) / `refine-feature.md` (command); `feat.prompts.refine_feat`/`implement_feat`/`review_feat` keep the `<verb>_<domain>` prompt-naming convention feat-150's own `general.prompts.repair` was a deliberate exception to (it is cross-cutting, this is domain-scoped). The distribution surface takes the flat artifact-noun CLI name `specmgr harness-bundle` (the `specmgr docs`/`specmgr adr-toc`/`specmgr mcp-docs` precedent) -- no nested Typer sub-application, since the 2026-10-31 re-scope left exactly one stage -- and the resource URI `specmgr://harness-bundle`.

### Related Decisions

- feat-150-mcp-lifecycle-commands (GitHub issue #150): the `repair` prompt/`doc-repairer` subagent/`ParseFailureResult` precedent this feature's prompt/agent/command shape follows; also the origin of the Design Notes/Decisions carried over verbatim below.

- feat-163-feat-numbering (GitHub issue #163): the FEAT Phase/Task numbering scheme this document is authored in from the start.

- New ADR (Phase 110, before Phase 120): "Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent" -- architecture-level, affects any future `<verb>_feat`-style prompt, so it gets a full ADR per this repo's own ADR-vs-feature-log convention. Its UUID is an input to Phase 120's instruction files and is recorded here once created.

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

### Task List

#### Phase 100: refine_feat

- [ ] Task 100.100: `feat/prompts/refine_feat.py` (`refine_feat(id)`) + `feat/data/feat_refine_instructions.md` (the MCP-native `get_feat`/`update`/`validate` path) + registration in `feat/prompts/__init__.py`.

- [ ] Task 100.110: `.opencode/agent/feat-planner.md` (path-scoped `edit`/`write` permission rules per REQ-002) + `.opencode/command/refine-feature.md` (`agent: feat-planner`).

- [ ] Task 100.120: `tests/feat/prompts/test_refine_feat.py` + manual smoke test (ACC-002).

- [ ] Task 100.130: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 100.140: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 110: ADR for portable-delegation pattern

- [ ] Task 110.100: Write the new ADR (see Related Decisions) in `docs/adr/` per the repo's ADR conventions, regenerate `specmgr adr-toc` (pre-commit hook), set its status to `accepted`, and record its UUID in this README's Related Decisions -- needed before Phase 120 (its UUID is an input to Phase 120's instruction files).

- [ ] Task 110.110: Phase-end gate: full quality gate green (including the `specmgr adr-toc` drift check), then exactly one Conventional Commit for the phase.

#### Phase 120: implement_feat + review_feat + auto fix-phase loop

- [ ] Task 120.100: `feat/prompts/implement_feat.py` + `feat/data/feat_implement_instructions.md` + registration, narrating the optional-delegation pattern from Design Notes, naming the Phase 110 ADR by UUID, and mentioning the review-fix loop.

- [ ] Task 120.110: `feat/prompts/review_feat.py` + `feat/data/feat_review_instructions.md` + registration, mirroring `feat-reviewer.md`'s checklist/report format including the conditional "Proposed Fix Phase" section.

- [ ] Task 120.120: Extend `.opencode/agent/feat-reviewer.md`'s report format with the conditional, ready-to-paste "Proposed Fix Phase" block + the `[NEEDS DECISION]` flagging rule (REQ-005).

- [ ] Task 120.130: Extend `.opencode/agent/phase-orchestrator.md`'s Workflow section with the capped review-fix loop (REQ-006: exit on no Errors/Gaps/Inconsistencies, the implementer-appends-the-fix-phase delegation step); update `.opencode/command/implement-feature.md`'s prose to mention the automatic review-fix step and fix its "a a" typo; update `.opencode/command/review-feature.md`'s body so its report-section enumeration includes the new conditional section.

- [ ] Task 120.140: Update `implement_feat`'s narration to mention the same review-fix loop, for portable-host parity.

- [ ] Task 120.150: `tests/feat/prompts/test_implement_feat.py` + `tests/feat/prompts/test_review_feat.py` + manual smoke test.

- [ ] Task 120.160: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `specmgr docs`/`specmgr mcp-docs` regeneration, `CHANGELOG.md` entry.

- [ ] Task 120.170: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 125: .opencode/ layout normalization

- [x] Task 125.100: Commit the already-made-on-disk `skills/` -> `skill/` merge (4 skills: `feat-numbering`, `refine-feature`, `review-feature`, `specmgr-refs`; `skill/` is now the single skill directory, 6 skills, one subfolder each) and fix the stale references it broke: `tests/opencode/test_skill_feat_numbering.py` + `tests/opencode/test_skill_specmgr_refs.py` (path constants + docstrings; both red until fixed), `tests/opencode/test_skill_uc_diagram.py` (its module docstring's dual-layout prose), `tests/opencode/__init__.py` (module docstring), `AGENTS.md` (the `specmgr-refs` path in the `general/` bullet), `README.md` (the `specmgr-refs` path). Gate: the full test suite green.

- [x] Task 125.110: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 130: Distribution (harness bundle + agent-driven install)

- [x] Task 130.100: `commands/harness_bundle.py`: the flat `specmgr harness-bundle` command (`[cli]`-only -- no `mcp` import): reads the repo-root layout from CWD (like `specmgr docs`/`specmgr adr-toc`; a missing `.opencode/` directory is a usage error, exit 2, nothing written) and enumerates every `*.md` recursively under exactly `.opencode/{agent,command,skill}/` (exact top-level directory-name match; sorted by `path`; a stray `*.md` at `.opencode/` top level or under a non-scoped directory -- `node_modules/`, `package.json`/`package-lock.json`, or a similarly-named directory such as the former `zZz-skill/` -- warns on stderr and is never bundled; the current tree is 24 files: 6 in `agent/`, 10 in `command/`, 8 in `skill/*/`), emit `{"instructions": <module constant, the REQ-008 protocol text verbatim>, "files": [{"path", "sha256", "content"}]}` via `json.dumps(indent=2, ensure_ascii=False)` + trailing newline (no timestamps -- two runs over an unchanged tree are byte-identical) to `src/biz/dfch/specmgr/general/data/general_harness_bundle.json`; print a summary line (file count, total bytes, output path); register in `cli.py` (the `from .commands import (...)` block + `app.command()(harness_bundle)`) + export in `commands/__init__.py`; add `"data/*.json"` to the existing `"biz.dfch.specmgr.general"` entry in `pyproject.toml`'s `[tool.setuptools.package-data]` (currently `["data/*.md", "data/headings/*.json"]`; `data/*.json` matches top-level JSON only, the bundle will be the first); run the command once and commit the generated bundle.

- [x] Task 130.110: Pre-commit local drift hook `specmgr-harness-bundle` in the docs-drift family (after the `specmgr-mcp-docs`/`specmgr-adr-toc` block, before `specmgr-lint`): `entry: bash -c 'uv run --frozen specmgr harness-bundle && git diff --exit-code -- src/biz/dfch/specmgr/general/data/general_harness_bundle.json'`, `language: system`, `pass_filenames: false`, `files: ^\.opencode/(agent|command|skill)/.*\.md$` (the `specmgr-adr-toc` entry shape) + the CI parity check in the `build` job, Python 3.13-pinned like the `specmgr docs`/`adr-toc`/`mcp-docs` steps (`if: matrix.python-version == '3.13'`, `uv run --frozen --all-extras --python 3.13.13 specmgr harness-bundle && git diff --exit-code -- src/biz/dfch/specmgr/general/data/general_harness_bundle.json`, with the same `::error::` hint wording).

- [x] Task 130.120: `general/resources/harness_bundle.py`: the `specmgr://harness-bundle` resource (`application/json`, `read_packaged_text("general", "harness_bundle", "json")` + fail-fast `json.loads` -- no model, the bundle has no schema of its own -- + the raw text returned unchanged, the `rasci.py` pattern) + registration in `general/resources/__init__.py` (import + its docstring bullet).

- [x] Task 130.130: `tests/commands/test_harness_bundle.py` (determinism: two runs byte-identical; enumeration completeness: the current tree's 24 files, plus a tmp-fixture copy of the scoped dirs gains a file and the generated bundle contains it with the correct sha256; exclusions: `node_modules/`, `package.json`/`package-lock.json`, a similarly-named sibling directory, and top-level stray `*.md` never appear; path ordering; `instructions` present) + `tests/general/resources/test_harness_bundle.py` (the resource returns the on-disk bundle byte-identically and it `json.loads`-parses to the full file list; the `test_rasci.py` precedent) + the hook diff-detection test.

- [x] Task 130.140: README.md: the new section immediately after `### Add to OpenCode` (the agent-driven install one-liner + what gets installed + the manual Claude Code path, per REQ-009, referencing that section for server setup) + the README Table of Contents entry.

- [x] Task 130.150: End-to-end walkthrough fixture (the feat-185-uc-diagrams ACC-002 precedent): a fresh temp harness config root, an agent run that installs strictly from the bundle's `instructions` field, every file verified sha256-clean (plus the skip behavior against a pre-identical file and the ask behavior against a pre-differing one), the transcript committed under `tests/fixtures/`. Requires a user-led fresh agent session (the implementing agent cannot self-produce it); the phase commit (Task 130.170) waits on this.

- [x] Task 130.160: Docs sync: `AGENTS.md` (the Developer Commands/CLI section: the new flat `specmgr harness-bundle` command; the `general/resources` bullet: the new resource; the pre-commit paragraph: the new hook), `server.py`'s module docstring (Resources list), `specmgr docs` + `specmgr mcp-docs` regeneration, `CHANGELOG.md` entry. No `specmgr adr-toc` (no ADR), no `specmgr schema` (no model), no `server.json` (env-var-only manifest).

- [x] Task 130.170: Phase-end gate: the full quality gate green -- `uv run --frozen ruff format --check && uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, plus this phase's doc-drift checks (`specmgr docs` + `specmgr mcp-docs`, no diff) -- then exactly one Conventional Commit for the phase.

#### Phase 140: Final Verification

- [ ] Task 140.100: Walk every Acceptance Criterion above (ACC-001..ACC-011) with concrete evidence.

- [ ] Task 140.110: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

## Progress

### Current Status

**As of 2026-11-01**: Phase 130 (Distribution) is fully implemented. Tasks 130.100-130.140 and 130.160 (the flat `specmgr harness-bundle` CLI command, the generated 24-file bundle `general/data/general_harness_bundle.json`, the `specmgr://harness-bundle` resource, the pre-commit + CI drift guards, the test suites, the README section + TOC entry, and the docs sync) are committed as `10a0184`. Task 130.150 (the end-to-end walkthrough fixture) is done: an agent run in a fresh, hermetic OpenCode 2.2.5 container (no repo mount, verified-empty OC state) installed strictly from the bundle's `instructions` field -- 22 installed (new) / 1 skipped (sha256-identical pre-existing) / 1 updated (approved overwrite of a pre-differing file) / 0 failed -- independently re-verified host-side at 24/24 byte-exact against the committed bundle, and pinned by `tests/fixtures/harness-bundle/install.walkthrough.md`. Phase 130 is now complete: every task 130.100-130.170 is done -- the implementation is committed as `10a0184`, the walkthrough is pinned by `tests/fixtures/harness-bundle/install.walkthrough.md`, and Task 130.170's phase-end gate was re-run green by the orchestrator, closing the phase out with its own single Conventional Commit. The next action is the feature-level closeout (`status` -> `review`); Phases 100-120 and 140 stay deferred -- they have no dependency on 125/130. Per user direction, the feature has now moved to `review` for the completed distribution slice (Phase 125 + Phase 130), with Phases 100-120 and 140 deferred pending the review outcome.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 15:41:33.454Z - Status set to review: distribution slice (Phase 125 + 130) complete

Per user direction, the feature moves from `planning` to `review` now that the distribution slice (Phase 125 + Phase 130) is complete. Phase 130 is closed: implementation committed as `10a0184`, and the end-to-end walkthrough fixture plus the Phase 130 closeout (Tasks 130.150/130.170 bookkeeping) as `60bf2cf`. Phases 100-120 (`refine_feat` / the delegation-pattern ADR / `implement_feat` + `review_feat`) and Phase 140 (final verification over all ACCs) remain deferred and are out of scope for this review for now.

#### 2026-11-01 14:48:36.549Z - Task 130.150 done: end-to-end install walkthrough in a fresh hermetic OpenCode container, pinned by a committed fixture

Executed the ACC-008 end-to-end walkthrough in a fresh `ghcr.io/anomalyco/opencode:2.2.5` container (Alpine) -- hermetic: no mount of this repo, verified-empty OpenCode state (the global config held only OpenCode's own `service.json`; no pre-existing `agent/`/`command/`/`skill/` harness files), model `vllm-sys0/qwen3.8-27b-bf16-896k` (local vLLM at 127.0.0.1:8081), the `specmgr` MCP server hosted on the host (streamable-http at 127.0.0.1:8099, CWD = the scratch project, so only the packaged resources were exposed, never this repo's documents). The scratch project (`/work/scratch-project`) was pre-seeded with exactly two harness files to exercise the protocol's conditional branches: `agent/ref-finder.md` byte-identical to the bundle (the SKIP case) and `command/refs.md` pre-modified with a `[WALKTHROUGH-PREMODIFIED] ` marker in its description line (the ASK case). The prompt sent was exactly "Install the specmgr harness files". The agent followed only the bundle's `instructions` field and reported 22 installed / 1 skipped / 1 updated (approved overwrite) / 0 failed; the orchestrator independently re-verified the final scratch tree host-side at 24/24 byte-exact against the committed bundle (0 missing, 0 mismatched, 0 extra, `opencode.json` intact). Pinned by `tests/fixtures/harness-bundle/install.walkthrough.md` (the feat-185-uc-diagrams ACC-002 precedent). Transient environment notes recorded there: the container's first `read_mcp_resource` hit a one-off OC 2.2.5 client error (`ReferenceError: Unknown identifier 'globalThis'`, retry succeeded, content always from the MCP resource), host-side MCP hosting (Alpine/musl cannot spawn the dev venv's glibc Python), and the agent's own first-pass `sed` delimiter hiccup (idempotent re-run). Task 130.150 is checked off; only Task 130.170's phase-end gate + commit remains (the orchestrator).

#### 2026-11-01 09:55:32.096Z - Phase 130 implemented (Tasks 130.100-140/160): harness bundle + resource + guards + docs, gate green

Implemented the Phase 130 distribution slice in the working tree (uncommitted -- the orchestrator commits at Task 130.170). New files: `src/biz/dfch/specmgr/commands/harness_bundle.py` (the flat, `[cli]`-only `specmgr harness-bundle` command: CWD-anchored repo layout, exact `{agent,command,skill}` scoping, sorted enumeration, stray warnings on stderr, `json.dumps(indent=2, ensure_ascii=False)` + trailing newline, the `INSTRUCTIONS` install-protocol constant, exit 2 on a missing `.opencode/`); the generated `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` (24 files: 6 agent/ + 10 command/ + 8 skill/*/, 91905 bytes; summary line: `✓ Wrote 24 harness file(s) (91905 bytes) to <repo>/src/biz/dfch/specmgr/general/data/general_harness_bundle.json`); `src/biz/dfch/specmgr/general/resources/harness_bundle.py` (the `specmgr://harness-bundle` resource, `rasci.py` pattern: packaged read + fail-fast `json.loads`, raw text unchanged); `tests/commands/test_harness_bundle.py` + `tests/general/resources/test_harness_bundle.py` (25 new tests: determinism, the pinned 24-file enumeration, sha256/content fidelity, exclusions + stray warnings, the exit-2 usage error, the committed-bundle byte-identity drift pin, the hook/CI shape pins per the `test_lint.py` precedent, the resource's on-disk byte-identity + fresh-read + fail-fast pins). Modified: `cli.py`/`commands/__init__.py` (registration/export), `general/resources/__init__.py` (import + docstring bullet + `__all__`), `pyproject.toml` (`"data/*.json"` into the existing `"biz.dfch.specmgr.general"` package-data entry), `.pre-commit-config.yaml` (the `specmgr-harness-bundle` hook after `specmgr-adr-toc`, before `specmgr-lint`), `.github/workflows/ci.yml` (the 3.13-pinned parity step after the `docs/MCP.md` step), `README.md` (the "Installing the specmgr Harness Files" section after "Add to OpenCode" + its TOC entry), `AGENTS.md` (Developer Commands line, the CLI-section bullet, the `general/resources/` enumeration, the pre-commit paragraph), `server.py` (the module docstring's Resources list), `CHANGELOG.md` (the `[Unreleased]` Added entry), and the two live surface pins (`tests/test_cli.py`'s registered-command set gains `harness-bundle`; `tests/test_schema_surface_registration.py`'s resource total 41 -> 42). Gate evidence (2026-11-01): `ruff format --check` (all files already formatted) + `ruff check` (all checks passed); `vulture src/ whitelist.py --min-confidence 60` (clean, no new whitelist entry needed); full suite `pytest -n auto` (5639 passed / 18 skipped); `specmgr docs` + `specmgr mcp-docs` regenerated with only the intended drift (2 new `docs/api/` pages, the index, `GENERATED.md`'s test count, `docs/MCP.md`'s resource row, the `server.md`/`general.resources.md` pages). Remaining: Task 130.150 (the end-to-end walkthrough fixture -- requires a user-led fresh agent session), then Task 130.170 (phase-end gate re-run + the single Conventional Commit).

#### 2026-10-31 21:37:20.303Z - Phase 130 task text refined against the verified tree (full gate made explicit)

Tasks 130.100-130.170 refined against the verified repo state (2026-10-31, read-only checks -- no code change): the CWD anchor + missing-dir exit-2 behavior, the exact `cli.py` registration site, the precise `pyproject.toml` edit (`"data/*.json"` into the existing `"biz.dfch.specmgr.general"` package-data entry), and the current 24-file tree with the real exclusion set (130.100); the exact hook entry shape/placement (`specmgr-adr-toc` family, before `specmgr-lint`) + the 3.13-pinned `build`-job CI step mirroring `ci.yml`'s `specmgr docs`/`adr-toc`/`mcp-docs` steps (130.110); the explicit no-model `json.loads` fail-fast (130.120); the pinned enumeration count + test homes per the `test_rasci.py`/`tests/commands/` precedents (130.130); the `### Add to OpenCode` README anchor (130.140); the user-involvement flag (130.150); the corrected docs-sync surface -- no `adr-toc`/`schema`/`server.json` (130.160); and the explicit full-gate command block in the phase-end task (130.170). The 125 -> 130 Dependencies note records that 125 is complete and 130 starts at Task 130.100.

#### 2026-10-31 21:29:01.822Z - Phase 125 closed out: code already landed in 10b032f, full gate re-verified

Task 125.100's code work was executed after the 08:34:48Z handover note, in commit `10b032f` (`test(opencode): repoint skill pins to .opencode/skill/ after consolidation`): the 2 red test files (`tests/opencode/test_skill_feat_numbering.py`, `tests/opencode/test_skill_specmgr_refs.py`) re-pointed to `.opencode/skill/` (path constants + docstrings), `tests/opencode/test_skill_uc_diagram.py`'s and `tests/opencode/__init__.py`'s module docstrings fixed, and the stale `specmgr-refs` paths in `AGENTS.md` + `README.md` corrected. Closeout verification (2026-10-31): `tests/opencode/` green (88 passed) and the full quality gate re-run green -- `ruff format --check` (2258 files already formatted), `ruff check` (all checks passed), `vulture` (clean), full suite 5614 passed / 18 skipped; the doc-drift checks (`specmgr docs`/`mcp-docs`/`adr-toc`) are N/A for this phase (no `src/` change in 125). The handover note's repo-state details are stale: the branch moved further (v0.38.0 release commits since) and the untracked `zZz-skill/` directory no longer exists. Tasks 125.100/125.110 are checked off; the next action is Task 130.100.

#### 2026-10-31 08:34:48.566Z - Handover: session ended, Phase 125 is next (repo state for a fresh agent)

Handover notes for the agent starting fresh. The Task List (Phase 125: Tasks 125.100/125.110; Phase 130: Tasks 130.100-130.170) is the authoritative task text; everything below is the session state and the settled design decisions.

**Branch / repo state.** Local `dev` is 4 commits ahead of `origin/dev`, unpushed: 2 structurizr spike docs, `chore(opencode): consolidate .opencode/skills/ into .opencode/skill/`, and `docs(feat-167): re-scope distribution to harness-bundle resource + agent-driven install`. The feat-197-i18n PR (#243, commit `2ceeba5`) was pulled and the 4 commits rebased onto it; `AGENTS.md`/`README.md` are the post-i18n versions now. Pushing has not been requested -- leave the branch local.

**Currently red (Phase 125's exact target).** The committed `skills/` -> `skill/` merge left 2 test files red: `tests/opencode/test_skill_feat_numbering.py` and `tests/opencode/test_skill_specmgr_refs.py` pin the old `.opencode/skills/...` paths (path constants + docstrings). Stale prose (not failing): `tests/opencode/test_skill_uc_diagram.py`'s module docstring (describes the former dual `skill/`+`skills/` layout as "the repo's deliberate choice"), `tests/opencode/__init__.py`'s module docstring (".opencode/skill/ and .opencode/skills/"), the `specmgr-refs` path in `AGENTS.md` and in `README.md` (both say `.opencode/skills/specmgr-refs/SKILL.md`, now `.opencode/skill/specmgr-refs/SKILL.md`). Post-rebase line numbers differ from any pre-rebase scan -- re-scan with `grep -rn "opencode/skills/" tests/ AGENTS.md README.md .specmgr/conventions/` and fix every hit against the post-i18n tree (i18n's own new references already use the singular `skill/` and are correct).

**Bundle tree (Phase 130).** `.opencode/` now holds 24 bundle files: 6 in `agent/`, 10 in `command/` (i18n added `translate.md` + `translation-status.md`), 8 in `skill/` (i18n added `translate-artifact/` + `translation-status/`). An empty, untracked `zZz-skill/` directory sits in the working tree: git cannot commit it, the generator's exact-name scoping excludes it -- delete it or leave it, it changes nothing.

**Settled decisions -- do not re-litigate (all recorded in Design Notes / Decisions Made / the REQ-ACC text):**

- No ADR for the packaging/distribution decision (it was plan-scoped, unshipped; no prior ADR to overturn).
- No MCP prompt for the install flow: OpenCode exposes no prompt surface to the agent (verified live in the handing-over session); the `specmgr://harness-bundle` resource is the sole discoverable entry point, and its `instructions` JSON field carries the complete protocol (wording in REQ-008).
- Single blob resource, not manifest + per-file: MCP resources are pull-based (zero per-session context cost; verified live) and install is a rare event, so the split buys nothing.
- Bundle shape: `{"instructions", "files": [{"path", "sha256", "content"}]}` -- no `harness` field, no `version` field (user decision); `path` relative to `.opencode/`; deterministic `json.dumps(indent=2, ensure_ascii=False)` + trailing newline; no timestamps (two runs over an unchanged tree must be byte-identical).
- Generator: flat `specmgr harness-bundle` command (no Typer sub-application -- one stage, and the repo's documented Typer single-command pitfall applies), `[cli]`-only (no `mcp` import), exact top-level directory names `{agent, command, skill}` (singular), recursive `*.md`, sorted by path; a stray `*.md` at `.opencode/` top level or under a non-scoped directory warns on stderr and is never bundled.
- Data file: `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` (the `_packaged_data` convention: `read_packaged_text("general", "harness_bundle", "json")`) + one `pyproject.toml` package-data entry.
- Guards: pre-commit hook `specmgr-harness-bundle` (regenerate + `git diff --exit-code`, files `^\.opencode/(agent|command|skill)/.*\.md$`, the `specmgr-adr-toc` entry shape) + CI parity check in the 3.13 job.
- Phase discipline: every phase = full quality gate (ruff format/check, vulture, full pytest, doc-drift checks) + exactly one Conventional Commit, docs sync inside it. Commit style `type(scope): summary`; do not push (not requested).
- Task 130.150 (the end-to-end walkthrough fixture) needs a real, fresh agent session that installs strictly from the bundle's `instructions` field -- plan for user involvement at that step (the feat-185-uc-diagrams ACC-002 precedent); the implementing agent cannot fully self-produce it.

**Immediate next action.** Task 125.100 (fix the 2 red test files + the stale references above; gate green), then Task 125.110 (one commit), then Phase 130 in task order. Phases 100-120 (`refine_feat` / delegation ADR / `implement_feat`+`review_feat`) stay deferred -- they have no dependency on 125/130.

#### 2026-10-31 06:58:19.585Z - Distribution re-scoped: single harness-bundle resource + agent-driven install

The planned Phase 130 (a `specmgr opencode sync`/`install` CLI over a generated package *tree* `general/data/opencode/{agent,command}/`) was re-scoped at the user's direction into a simpler agent-driven design: a flat `specmgr harness-bundle` command generates one package file (`general/data/general_harness_bundle.json`, `{"instructions", "files": [{path, sha256, content}]}`) by enumerating `.opencode/{agent,command,skill}/` (singular directory names; `skill/` the only nested layout), served by a single `specmgr://harness-bundle` resource whose `instructions` field carries the whole install protocol -- the agent of the active harness reads the resource (discoverable via `list_mcp_resources`, zero per-session cost: MCP resources are pull-based) and installs the files into its own config directory (OpenCode: via the `customize-opencode` skill). No install CLI, no `--force`, no sibling-directory detection, no MCP prompt (OpenCode exposes no prompt surface to the agent), no ADR (the replaced decision was plan-scoped and unshipped). REQ-007/008/009, ACC-007/008/009/010, Scope, the Packaging/Distribution Design Notes, the Naming note, and Phase 130's tasks were rewritten accordingly; a new Phase 125 commits the user's already-made-on-disk `skills/` -> `skill/` merge and fixes its stale references (2 test files red, docstrings, `AGENTS.md`, `README.md`). Phases 100-120 and the delegation ADR (ACC-011) are untouched. Recorded on GitHub issue #167.

#### 2026-09-28 03:46:33.000Z - Created

Drafted this feature by splitting the not-yet-started remainder (originally Phases 2-6) of feat-150-mcp-lifecycle-commands (GitHub issue #150) into a new feature, tracked under a new GitHub issue, #167, and authored directly in the feat-163-feat-numbering (GitHub issue #163) Phase/Task numbering scheme (`Phase NNN`/`Task NNN.MMM`) from the start. Requirements/Acceptance Criteria were renumbered from REQ-001 / ACC-001 (feat-150's REQ-003..011 -> REQ-001..009, ACC-003..013 -> ACC-001..011); the Task List's five remaining phases were renumbered Phase 100/110/120/130/140 (step-10 tasks within each); Scope, Dependencies, Design Notes, and Decisions Made were carried over verbatim where still applicable, dropping everything specific to feat-150's own Phase 0/1 (the `repair`/`ParseFailureResult` implementation, now referenced here only as a Dependency).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 06:58:19.585Z - Distribution: single generated bundle file served as one MCP resource, installed by the harness's own agent

User decision (2026-10-31, GitHub issue #167), replacing the 2026-09-24 "root .opencode/ canonical, generated package copy" design's CLI-installer half: the bundle is one JSON file (manifest + verbatim content + per-file sha256; no `harness` field, no `version` field), the `specmgr://harness-bundle` resource is the agent's discoverable entry point (MCP resources are pull-based -- zero per-session context cost; verified live against this harness), the install protocol lives in the bundle's `instructions` field (harness config root via the harness's own config skill, byte-exact write, sha256 skip/ask/verify loop, never touch `opencode.json`), and the `specmgr opencode install` CLI + its sibling-detection/`--force` machinery are dropped. Rationale: the consumer of these files is an agent session that already holds file-write permission and harness knowledge, and a prompt carrier was rejected because OpenCode exposes no MCP prompt surface to the agent. No ADR: the replaced decision was plan-scoped (this document's own Design Note, unshipped) with no prior ADR to overturn. The two-copy drift guard survives in single-file form (pre-commit hook + CI parity check). Partially supersedes the 2026-09-24 20:57:07 packaging decision: the root-canonical + generated-copy + drift-check principle stands; the directory-tree copy + `sync`/`install` CLI do not.

#### 2026-09-24 20:57:09.000Z - Phase discipline: one commit per phase, full quality gate before it

User requirement (2026-09-24, carried over from feat-150): each phase is exactly one Conventional Commit, preceded by the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches), with the phase's docs sync inside the same commit. Enforced via a phase-end gate task per phase in the Task List and a Design Notes section.

#### 2026-09-24 20:57:08.000Z - Review-fix loop exits when no Errors, Gaps, or Inconsistencies remain

Chosen over "no Errors/Gaps" so the loop's exit criterion matches REQ-005's task-derivation set (a fix phase derives tasks from Errors/Gaps/Inconsistencies); Code Smells/Improvements/Positives stay advisory. The 3-cycle cap is unchanged. Carried over from feat-150.

#### 2026-09-24 20:57:07.000Z - Packaging: root .opencode/ canonical, generated package copy with drift check

The wheel only ships what lives under `src/`, so the installable OpenCode file copy is generated under `general/data/opencode/{agent,command}/` from the repo-root `.opencode/` by `specmgr opencode sync`, guarded by a pre-commit local drift hook and a CI parity check -- the same two-copy pattern the repo already runs for the packaged JSON Schema copies. Alternatives considered and rejected: package-copy-canonical (changes the repo's own dev workflow) and a build-time copy hook (non-standard build machinery). Carried over from feat-150.

#### 2026-09-23 09:02:00.000Z - Portable prompt + optional host-delegation pattern

`implement_feat`/`review_feat` narrate delegation via the host's own task-delegation tool when present, degrading to direct implementation otherwise, rather than either (a) requiring OpenCode specifically or (b) losing real subagent orchestration. See Design Notes. Carried over from feat-150.

#### 2026-09-23 09:01:00.000Z - Review-fix loop capped at 3 cycles

Chosen over an uncapped loop to bound the automatic review-to-fix-to-re-review cycle; remaining findings after 3 cycles go to the user instead. Carried over from feat-150.

#### 2026-09-23 09:00:30.000Z - `.opencode/agent`/`command` singular naming confirmed correct

No rename needed -- OpenCode accepts singular and plural directory names at both global and project scope. Carried over from feat-150.

### Related PRs / Commits

- GitHub issue #167 (this feature's own tracking issue).

### More Information

Source: https://github.com/dfch/biz.dfch.SpecMgr/issues/167 (split from https://github.com/dfch/biz.dfch.SpecMgr/issues/150)
