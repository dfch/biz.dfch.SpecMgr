---
classification: null
created: '2026-11-15T06:29:34.876+01:00'
id: feat-263-delegation-prompts
status: done
type: feat
updated: '2026-11-17T10:04:39.919+01:00'
version: 1.0.0
---

# Feature: Portable Feature-Lifecycle Prompts II (delegation DEC, implement_feat, review_feat, review-fix loop)

## Plan

### Overview

This feature carries the unstarted remainder of feat-167-mcp-lifecycle-commands-2 (GitHub issue #167), carved out on 2026-11-15 by the D1 rescope decision. feat-167 shipped and closed its distribution slice (Phase 125 + Phase 130: the `specmgr harness-bundle` CLI, the `specmgr://harness-bundle` resource, the README install section) and Phase 100 (`refine_feat`, the `feat-planner` agent, `/plan-feature`) plus the review-fix phases 150-180. What was never started and moves here: (1) the DEC documenting the portable-prompt-narrates-optional-delegation pattern (feat-167 Phase 110, ACC-011), (2) the `implement_feat` and `review_feat` MCP prompts (feat-167 REQ-003/REQ-004, Phase 120), (3) the conditional "Proposed Fix Phase" section of `feat-reviewer.md` (REQ-005), (4) the capped review-fix loop in `phase-orchestrator.md` and `implement_feat`'s narration (REQ-006), and (5) the final verification (feat-167 Phase 140).

Requirement and acceptance IDs are renumbered from 001 in this plan; the mapping to feat-167's IDs is: REQ-001 = feat-167 REQ-003, REQ-002 = REQ-004, REQ-003 = REQ-005, REQ-004 = REQ-006, REQ-005 = Phase 110 / ACC-011 (which had no REQ of its own); ACC-001 = ACC-003, ACC-002 = ACC-004, ACC-003 = ACC-005, ACC-004 = ACC-006, ACC-005 = ACC-011. The unifying design principle is unchanged from feat-150/feat-167: every capability gets a portable MCP prompt (narration-only text that works in any MCP host) and, where real file editing or multi-agent delegation is needed, an OpenCode-native subagent or command with real permission enforcement.

The reason for the carve-out (rather than continuing inside feat-167) is release-gate attribution: the release precheck's closeout gate attributes a merged PR to a feature folder by head-ref name (exact folder id, else the `feat-<NNN>-` prefix). feat-167's work ran on a bare `feat-167` branch against the folder `feat-167-mcp-lifecycle-commands-2`, so PR #260 was never attributed. This feature's branch MUST be named exactly like its folder (`feat-263-delegation-prompts`) so the gate attributes its delivery.

### Requirements

- REQ-001: A new `feat/prompts/implement_feat.py` MCP prompt narrates orchestrator discipline (read plan, phase-by-phase `TodoWrite`, delegate each phase via the host's subagent-delegation tool when available, verify before advancing, never write code directly), names the new delegation-pattern DEC (Phase 100) by UUID, mentions the REQ-004 review-fix loop, and falls back to direct single-session implementation when no delegation tool exists.

- REQ-002: A new `feat/prompts/review_feat.py` MCP prompt narrates `feat-reviewer.md`'s existing review checklist and report format portably, including the new conditional "Proposed Fix Phase" section (REQ-003).

- REQ-003: `.opencode/agent/feat-reviewer.md`'s report format gains a new, conditional "Proposed Fix Phase" section: a ready-to-paste block for the plan's `### Task List` -- a `#### Phase NNN: Fix phase (review cycle k)` heading using the next unused phase number (never renumbering existing phases) plus `- [ ] Task NNN.MMM` items derived strictly from the report's own Errors/Gaps/Discrepancies (Improvements/Positives stay advisory), with any item that needs a user decision explicitly flagged `[NEEDS DECISION]` rather than guessed at.

- REQ-004: `.opencode/agent/phase-orchestrator.md` (and `implement_feat`'s narration, REQ-001) gain a final review-fix loop: once the plan's final verification phase has walked the acceptance criteria (the feature is at `review`, not yet `done`), run the reviewer; if it proposes a fix phase, resolve any `[NEEDS DECISION]` items with the user via `question`, then delegate the fix phase to one more `phase-implementer` cycle exactly like a normal phase -- with the delegation prompt instructing the implementer to first append the reviewer's ready-to-paste block to the plan's Task List, since the orchestrator itself cannot edit files (`edit`/`write` are denied to it); repeat until the reviewer reports no Errors, Gaps, or Discrepancies left, capped at 3 review-fix cycles (after which remaining findings are handed to the user instead of auto-fixed again); the feature is set to `done` only after the loop exits clean.

- REQ-005: A new DEC documents the pattern "portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent", with status `accepted`, authored before the `implement_feat`/`review_feat` instruction files because its UUID is an input to them.

### Acceptance Criteria

- [x] ACC-001: `implement_feat(id)` MCP prompt exists, is registered, and its instructions explicitly name the host's task-delegation tool as optional (never assumed present), narrate the orchestrator discipline (verify before advancing, never write code directly), state the fallback to direct single-session implementation when no delegation tool exists, name the new delegation-pattern DEC by UUID, and mention the review-fix loop.

- [x] ACC-002: `review_feat(id)` MCP prompt exists, is registered, and mirrors `feat-reviewer.md`'s checklist and report format including the conditional "Proposed Fix Phase" section.

- [x] ACC-003: `feat-reviewer.md`'s report format documents the "Proposed Fix Phase" section -- the ready-to-paste Task-List block shape (next unused phase number, `- [ ] Task NNN.MMM` items derived from Errors/Gaps/Discrepancies only) and the `[NEEDS DECISION]` flagging rule.

- [x] ACC-004: `phase-orchestrator.md`'s workflow documents the capped (3-cycle) review-fix loop, its exit criterion (reviewer reports no Errors, Gaps, or Discrepancies), the resolution of `[NEEDS DECISION]` items with the user via `question`, the append-the-fix-phase delegation step (the implementer appends, not the orchestrator), and that the `done` closeout happens only after a clean loop exit (verify at `review`, loop, then `done`).

- [x] ACC-005: A new DEC under `docs/dec/` documents the "portable MCP prompt narrates optional host-native subagent delegation" pattern, has status `accepted`, and its UUID is recorded in this plan's Related Decisions and named by `implement_feat`'s instructions.

### Scope

#### Included

- 2 new MCP prompts (`implement_feat`, `review_feat`) and their packaged instruction data files.

- Targeted edits to 4 existing OpenCode files: `feat-reviewer.md` (the Proposed Fix Phase section) and `phase-orchestrator.md` (the review-fix loop), `implement-feature.md` (prose mentioning the automatic review-fix step, plus its "a a" typo fix at line 23), and `review-feature.md` (its body re-enumerates the report sections and would go stale without the new conditional section).

- One new DEC for the portable-prompt-narrates-delegation pattern.

- The docs sync of the prompt phase: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `CHANGELOG.md`, `specmgr docs`/`specmgr mcp-docs`, and the harness bundle regeneration (`.opencode/` files change).

#### Explicitly Out Of Scope

- Anything feat-167 already shipped: `refine_feat`, `feat-planner`, `/plan-feature`, the harness bundle and its resource, the README install section.

- Any change to `.opencode/agent/phase-implementer.md`, `.opencode/agent/ref-finder.md`, `.opencode/agent/doc-repairer.md`, `.opencode/agent/feat-refiner.md`, `/refs`, `/repair`, `/release`, or `/refine-feature`.

- Any change to the generic `validate`/`update`/`set_status` tools themselves.

- Enforcing the prompts' narrated workflow mechanically; they are markdown-narrated, not code.

### Dependencies

#### Depends On

- FEAT feat-167-mcp-lifecycle-commands-2 (GitHub issue #167): its shipped Phase 100 + Phase 130 surface -- the `refine_feat` prompt shape this feature's prompts mirror, and the harness bundle that must be regenerated when `.opencode/` files change.

- FEAT feat-46-remove-adr (GitHub issue #46): the ADR domain is retired; the decision carrier is a DEC under `docs/dec/`.

- FEAT feat-150-mcp-lifecycle-commands (GitHub issue #150): the `repair` prompt/`doc-repairer` precedent.

- FEAT feat-163-feat-numbering (GitHub issue #163): this document's Phase/Task numbering scheme.

- Phase 110 (`implement_feat`/`review_feat`) depends on Phase 100's DEC (its UUID is an input to Phase 110's instruction files).

#### Blocks

- None known.

### Design Notes

**Portable-prompt-narrates-delegation pattern.** An MCP prompt never executes tool calls itself -- it returns text to whatever LLM session invoked it, exactly like every existing prompt in this codebase (`create_req` says "use the `question` tool"; neither `question` nor `TodoWrite` is implemented by this MCP server). `implement_feat`/`review_feat` extend this precedent one step further: they narrate delegating work to a subagent via "your host's task-delegation tool, if one exists." Inside OpenCode that is a real instruction to use the `task` tool (genuine multi-agent orchestration, since OpenCode exposes both the `specmgr` MCP tools and its own native tools in the same session). On a host with no such tool, the same text degrades to "implement it yourself, one phase at a time" -- never a hard failure. This is the subject of the new DEC (ACC-005).

**Prompt/agent/command text duplication is unavoidable.** OpenCode exposes MCP tools but not MCP prompts as slash commands, so the OpenCode agent/command files cannot delegate to the packaged prompt text -- each carries its own copy of the same workflow. Keeping prompt, agent and command wording in sync is a standing review-checklist item (the `feat-reviewer` checklist's Documentation item).

**Review-fix loop (capped, aligned exit criterion).** Capped at 3 automatic review-fix cycles (configurable only in the prose instructions, not a hard machine limit). The loop exits when the reviewer reports no Errors, Gaps, or Discrepancies -- the same set REQ-003's fix phase derives tasks from (Improvements/Positives stay advisory), so a cycle never ends with the fix phase re-deriving the same discrepancy. Findings still open after 3 cycles are handed to the user. The orchestrator cannot append the proposed fix phase itself (`edit`/`write` are denied to it), so the fix phase's `phase-implementer` is delegated with an explicit first step: append the reviewer's ready-to-paste block to the plan's Task List.

**Targets' current state (verified 2026-11-15).** `.opencode/command/review-feature.md` enumerates the report as `Errors (E1, ...) / Gaps (G1, ...) / Discrepancies (D1, ...) / Improvements (I1, ...) / Positives (P1, ...)` -- the conditional "Proposed Fix Phase" section is added to that enumeration. The "a a" typo is at `.opencode/command/implement-feature.md` line 23 (`run the review-feature agent for a a post-implementation review` -> `for a post-implementation review`). The harness bundle currently holds 32 files; `tests/commands/test_harness_bundle.py` pins the count and must be updated if a file is added (this feature adds none, but every edited `.opencode/` file changes its bundle entry).

**Phase discipline.** Every phase ends with the quality gate and exactly one Conventional Commit; the phase's docs sync travels inside that same commit. Phase 100 (a DEC plus this plan) needs only the light gate (ruff format/check, vulture, full pytest, `specmgr lint` on this README and the new DEC) -- creating a DEC under `docs/dec/` changes neither `src/` nor `.opencode/`, so no `docs`/`mcp-docs`/`harness-bundle` regeneration. Phase 110 changes `src/` and `.opencode/`, so it needs the full gate including `specmgr docs`, `specmgr mcp-docs` and `specmgr harness-bundle` regenerate-then-no-diff.

**Operational gotchas.** (1) This README is a specmgr `feat` document: list items (Requirements, Acceptance Criteria, Out-of-Scope and Task lines) are ONE physical line -- soft-wrapping one fails the feat schema; after edits the whole document must full-parse (`uv run --frozen specmgr lint .specmgr/feat/feat-263-delegation-prompts/README.md` -> exit 0). (2) Any change to a `.opencode/{agent,command,skill}/*.md` file requires `uv run --frozen specmgr harness-bundle` in the SAME commit (the pre-commit drift hook enforces it). (3) Adding test files requires a manual `uv run --frozen specmgr docs` regeneration of `docs/GENERATED.md` in the same commit: the specmgr-docs pre-commit hook is scoped to `src/` changes only. (4) Branch name = folder name, for release-gate attribution (see Overview). (5) Stale `__pycache__`-only directory shells pollute `specmgr docs`; check before regenerating. (6) The MCP server attached to this worktree currently runs the last published release (v0.38.0 -- checkable in `specmgr://config`: it still has the `adr` domain, no `set` domain, no feat-108 status FSM, and the pre-feat-247 DEC model), so MCP-side parse/resolution/status results can disagree with the dev-code CLI; the plan's CLI gates (`specmgr lint`, pre-commit) are the authority (observed: the server reports this plan's referenced DEC e369ee2e and ~20 other corpus documents as not-found while dev-code `specmgr lint` passes them).

### Related Decisions

- FEAT feat-167-mcp-lifecycle-commands-2 (GitHub issue #167): the parent feature; its Decisions Made log carries the origin of the delegation pattern and the review-fix loop decisions.

- DEC 4481b1fd-26e5-46bc-8f1b-236b638385b2: "Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent" -- architecture-level, affects any future `<verb>_feat`-style prompt, so it gets a full DEC; its UUID is an input to Phase 110's instruction files (named by implement_feat per ACC-005).

- DEC e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions).

### Task List

#### Phase 100: Portable-delegation DEC

- [x] Task 100.100: As its first action, set this feature's status `planning` -> `progress` (generic `set_status(type="feat")`; the feat FSM is planning -> progress -> review -> done, so no later task may skip a hop). Then write the new DEC (see Related Decisions) in `docs/dec/` via the `dec` domain (`create_dec`, which writes `status: draft`, then the generic `set_status(type="dec")` twice: `draft` -> `proposed`, then `proposed` -> `accepted` -- dev's DEC status FSM (feat-108) forbids the one-hop `draft` -> `accepted`; the two-hop sequence is valid under both published and dev tooling), and record the DEC's UUID in this README's Related Decisions -- needed before Phase 110 (its UUID is an input to Phase 110's instruction files).

- [x] Task 100.110: Phase-end gate: ruff format/check, vulture, the full test suite, and `specmgr lint` on this README and the new DEC (no `docs`/`mcp-docs`/`harness-bundle` regeneration -- neither `src/` nor `.opencode/` changes), then exactly one Conventional Commit for the phase.

#### Phase 110: implement_feat + review_feat + review-fix loop

- [x] Task 110.100: `feat/prompts/implement_feat.py` + `feat/data/feat_implement_instructions.md` + registration in `feat/prompts/__init__.py`, narrating the optional-delegation pattern from Design Notes, naming the Phase 100 DEC by UUID, and describing the review-fix loop (REQ-001, REQ-004).

- [x] Task 110.110: `feat/prompts/review_feat.py` + `feat/data/feat_review_instructions.md` + registration, mirroring `feat-reviewer.md`'s checklist and report format including the conditional "Proposed Fix Phase" section (REQ-002).

- [x] Task 110.120: Extend `.opencode/agent/feat-reviewer.md`'s report format with the conditional, ready-to-paste "Proposed Fix Phase" block and the `[NEEDS DECISION]` flagging rule (REQ-003).

- [x] Task 110.130: Extend `.opencode/agent/phase-orchestrator.md`'s Workflow section with the capped review-fix loop (REQ-004: exit on no Errors/Gaps/Discrepancies, `[NEEDS DECISION]` resolution via the `question` tool, the implementer-appends-the-fix-phase delegation step, and the verify-at-`review` -> loop -> `done`-only-after-clean-exit ordering); update `.opencode/command/implement-feature.md`'s prose to mention the automatic review-fix step, fix its "a a" typo at line 23, and align its line-21 status prose with the feat FSM (narrate the valid `progress` -> `review` hop, with the `planning` -> `progress` start hop from Task 100.100 as its precondition); update `.opencode/command/review-feature.md`'s report-section enumeration to include the new conditional section.

- [x] Task 110.140: `tests/feat/prompts/test_implement_feat.py` + `tests/feat/prompts/test_review_feat.py` (content assertions for ACC-001/ACC-002, the registration pins, and the `tests/general/tools/test_i18n_feat_adr_exclusion.py` `_FEAT_PROMPTS` pin gaining both prompts) + a manual smoke test: in a fresh session, invoke `implement_feat(<id>)` and `review_feat(<id>)` and confirm the `$id` substitution renders (no unsubstituted placeholder, no KeyError) and both prompts appear in the registered prompt surface; record the evidence so the Phase 120 ACC walk is reproducible.

- [x] Task 110.150: Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `CHANGELOG.md` `[Unreleased]` entry, `specmgr docs` + `specmgr mcp-docs` regeneration, and `specmgr harness-bundle` regeneration (the four edited `.opencode/` files change their bundle entries; the count stays 32).

- [x] Task 110.160: Phase-end gate: full quality gate green (ruff format/check, vulture, full pytest, `specmgr docs` + `specmgr mcp-docs` + `specmgr harness-bundle` regenerate-then-no-diff, `specmgr lint` on this README), then set this feature's status `progress` -> `review` (generic `set_status(type="feat")`) and make exactly one Conventional Commit for the phase (the status change rides in the same commit).

#### Phase 120: Final Verification

- [x] Task 120.100: At status `review` (set in Task 110.160), walk every Acceptance Criterion above (ACC-001..ACC-005) with concrete evidence and check them off, then run the REQ-004 review-fix loop; set the feature status `review` -> `done` only after the loop exits clean (no Errors, Gaps, or Discrepancies).

- [x] Task 120.110: Phase-end gate: full quality gate green, then exactly one Conventional Commit for the phase.

#### Phase 130: Fix phase (review cycle 1)

- [x] Task 130.100: Close G1 -- narrate the fallback for a reviewer report that carries Errors/Gaps/Discrepancies but no "Proposed Fix Phase" block (e.g. re-run the reviewer once, then hand the findings to the user as after the 3-cycle cap), keeping both mirror copies word-for-word aligned with each other: .opencode/agent/phase-orchestrator.md:107-119 and src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md:83-95. The phase-orchestrator edit is an `.opencode/` file, so `uv run --frozen specmgr harness-bundle` regeneration rides in the same commit, and any phrase newly asserted by the content tests in tests/feat/prompts/test_implement_feat.py:147-156 / tests/feat/prompts/test_review_feat.py gains its pin there.

- [x] Task 130.110: Fix D1 -- bring the two mirror copies of the conditional "Proposed Fix Phase" section into agreement by adding the agent file's worked example block (the `Phase 120` heading example with its three task items) to the end of section 5 of src/biz/dfch/specmgr/feat/data/feat_review_instructions.md:152-169, matching .opencode/agent/feat-reviewer.md:203-212 (no harness-bundle regeneration needed -- the changed file is under `src/`; extend tests/feat/prompts/test_review_feat.py:179-212 with a pin for the example's heading/task shape if desired).

- [x] Task 130.120: Resolve D2 -- (user decision 2026-11-16: option (a), the narration mirrors the agent file's "ask the user to confirm, then commit"): align src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md's commit step with .opencode/agent/phase-orchestrator.md step 6; no agent/command file change.

#### Phase 140: Fix phase (review cycle 2)

- [x] Task 140.100: Fix D1 -- the narration's `done`-closeout bullet omits the commit that the agent file's step 10 carries; add the closeout commit to src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md:81-84 mirroring .opencode/agent/phase-orchestrator.md:128-131 (e.g. "...set the feature status `done` with the generic `set_status` tool (`type="feat"`), commit the closeout, and report the final summary to the user"), and pin the new phrase in tests/feat/prompts/test_implement_feat.py (extend test_done_only_after_clean_exit or add a sibling test, following the D2/G1 pin precedent at :136-141/:165-177). No harness-bundle or docs regeneration needed -- the changed files are under `src/` only and the `@mcp.prompt` description/docstring stay accurate.

#### Phase 150: Fix phase (post-done review)

- [x] Task 150.100: Fix D1 (post-done review, user-run feat-reviewer report of 2026-11-17: no Errors/Gaps, one Discrepancy, two advisory Improvements) -- the `feat` domain package docstring's prompt enumeration is stale (pre-existing since feat-167 Phase 100; Task 110.150's docs sync named AGENTS.md/server.py/CHANGELOG but not this per-domain docstring, so the stale text survived into the committed generated mirror): extend the "Prompts:" sentence in src/biz/dfch/specmgr/feat/__init__.py to all five prompts (``create_feat(topic)``/``update_feat(id, instructions=None)``/``refine_feat(id)``/``implement_feat(id)``/``review_feat(id)``) with a one-sentence role note per new prompt mirroring AGENTS.md's `feat/` bullet (feat-263-delegation-prompts Phase 110, GitHub issue #263), pin the enumeration with a new test (every name in `feat/prompts/__init__.py`'s `__all__` must appear in the domain package docstring), and regenerate `specmgr docs` (docs/api/biz.dfch.specmgr.feat.md mirror; docs/GENERATED.md test-file count) -- `specmgr mcp-docs` and `specmgr harness-bundle` are expected byte-identical (no prompt-surface or `.opencode/` change); update this plan's Progress (Current Status, a dated Updates entry, a Decisions Made entry recording the scope decision: D1 fixed, I1/I2 carried advisory, status stays `done` with no FSM hop -- a post-done correction on the unmerged branch) and re-stamp the frontmatter `updated`; Improvements I1 (the `review-feature` skill's one-line summary omits the conditional "Proposed Fix Phase" section) and I2 (the `implement-feature` command's "commit, push and create a pr" wording, retained by the plan's D2 decision) are deliberately not fixed (the loop's strict derivation rule: Improvements never derive tasks).

## Progress

### Current Status

**As of 2026-11-17**: Done. The REQ-004 review-fix loop ran 3 cycles and exited clean (unchanged history); a user-run post-done review of 2026-11-17 reported one Discrepancy (D1, the stale `feat` package docstring prompt enumeration) fixed as Phase 150 on the unmerged branch (delivery is now 7 commits atop dev), status stays `done` (no FSM hop); carried advisory (not fixed): this review's I1 (the `review-feature` skill summary omits the conditional "Proposed Fix Phase" section; operationally harmless, would require a harness-bundle regeneration) and I2 (the `implement-feature` command push wording, retained by the D2 decision).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-17 09:04:39.000Z - Phase 150: Fix phase (post-done review) complete (D1)

The user-run post-done feat-reviewer review of 2026-11-17 reported no Errors and no Gaps, one Discrepancy (D1), and two advisory Improvements (I1/I2). D1: the "Prompts:" sentence of the `feat` domain package docstring in src/biz/dfch/specmgr/feat/__init__.py enumerated only create_feat/update_feat/refine_feat -- stale since feat-167 Phase 100 (Task 110.150's docs sync named AGENTS.md/server.py/CHANGELOG but not this per-domain docstring) -- so the stale text had propagated into the committed generated mirror docs/api/biz.dfch.specmgr.feat.md. D1 fix: the "Prompts:" sentence now covers all five prompts, `implement_feat` and `review_feat` each gaining a one-sentence role note mirroring AGENTS.md's `feat/` bullet (the orchestrator-discipline narration with the optional-delegation pattern per DEC 4481b1fd and the capped review-fix loop; the portable `feat-reviewer` checklist/report-format mirror including the conditional "Proposed Fix Phase" section); the new pin test tests/feat/test_package_docstring.py asserts the five prompt names and, as the drift pin, every name in feat/prompts/__init__.py's `__all__` against the domain package docstring; `specmgr docs` regenerated docs/api/biz.dfch.specmgr.feat.md (the docstring mirror) and docs/GENERATED.md (test-file count 501 -> 502) -- the only two changed generated files; `specmgr mcp-docs` and `specmgr harness-bundle` both ended byte-identical (no prompt-surface or `.opencode/` change). Scope decision: only D1 fixed -- I1 (the `review-feature` skill's one-line summary omits the conditional "Proposed Fix Phase" section; operationally harmless, would require touching `.opencode/` and a harness-bundle regeneration) and I2 (the `implement-feature` command's "commit, push and create a pr" wording, retained by this plan's D2 decision) are carried advisory, per the loop's strict derivation rule (Improvements never derive tasks); the feature status stays `done` with no FSM hop (a post-done correction on the unmerged branch, no PR open yet). Gate evidence: ruff format/check clean, vulture clean, full pytest green (the two new pin tests pass, no regressions), specmgr lint exit 0 on this README. Task 150.100 checked off.

#### 2026-11-17 06:32:09.000Z - Done: REQ-004 review-fix loop exited clean at cycle 3; status review -> done

Cycle 3 of the REQ-004 review-fix loop came back clean: the feat-reviewer's report carried no Errors, Gaps, or Discrepancies, and the reviewer re-ran the full gate -- pytest 6115 passed / 18 skipped, ruff format/check + vulture clean, specmgr lint 2/2 on this plan + DEC 4481b1fd, the harness bundle 32/32 sha256-verified, and docs in sync. The loop's step-10 closeout then set the feature status `review` -> `done` (the generic `set_status(type="feat")`, legal under the dev feat FSM) -- the hop Task 120.100 waits for. Tasks 120.100/120.110 are now checked off: 120.100's full scope (the ACC-001..ACC-005 walk at `review`, the loop run, the `done` hop only after a clean exit) is complete, and 120.110's gate is green, its single Conventional Commit being the orchestrator's next action. Carried advisory Improvements (not findings -- the loop's advisory rule leaves them out of the fix scope): I1 -- the AGENTS.md host-surface sentence for the feat lifecycle prompts, deliberately deferred; I2 -- the DEC filename's cosmetic mid-word slug truncation by the pre-existing 60-char slugify, out of scope for this feature.

#### 2026-11-17 05:32:35.000Z - Phase 140: Fix phase (review cycle 2) complete (D1)

Review cycle 2 (REQ-004 loop) verified the cycle-1 fixes (G1/D1/D2) as genuinely closed and reported exactly one new Discrepancy (orchestrator-verified): the narration's done-closeout bullet in src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md step 4 (lines 81-84) said 'set the feature status `done` with the generic `set_status` tool (`type="feat"`) and report the final summary to the user' -- no commit -- while .opencode/agent/phase-orchestrator.md step 10 (lines 128-131) carries 'Set the feature status to `done` (the generic `set_status` tool, `type="feat"`), commit, and report the final summary to the user' (mirror drift under the standing prompt/agent/command sync obligation, DEC 4481b1fd's Consequences). Task 140.100: the done bullet now reads 'exit -- set the feature status `done` with the generic `set_status` tool (`type="feat"`), commit the closeout, and report the final summary to the user.' (data file lines 81-85; the settled wording's 'commit the closeout' sits where the agent file's bare 'commit' sits in its step-10 sentence); no `.opencode/` file, no docs/prompt-description change (implement_feat.py's @mcp.prompt description 'done only after a clean exit' and module docstring 'the done closeout only after a clean loop exit' stay accurate and are byte-unchanged). Pin: tests/feat/prompts/test_implement_feat.py gains test_done_closeout_carries_the_commit (the full corrected closeout sentence, including 'commit the closeout', against the normalized rendered text; sibling of test_done_only_after_clean_exit, per the D2/G1 pin precedent). Gate green: ruff format/check, vulture, full pytest, specmgr docs + specmgr mcp-docs + specmgr harness-bundle regenerate-then-no-diff (all seven tracked files byte-identical this time -- no .opencode/ or prompt-description input changed), and specmgr lint on this README (full feat parse); Task 140.100 checked off. The REQ-004 loop re-runs the reviewer (cycle 3, the cap) before the done closeout and the Phase 120 commit.

#### 2026-11-17 01:18:32.000Z - Phase 130: Fix phase (review cycle 1) complete (G1/D1/D2)

Review cycle 1 (REQ-004 loop) produced no Errors, one Gap (G1), two Discrepancies (D1/D2), one advisory Improvement (I1, not implemented), and four Positives; the reviewer's ready-to-paste block was appended verbatim to the Task List as Phase 130 before the fixes. Task 130.100 (G1): the non-conforming-reviewer-report fallback is now narrated in both mirror copies, word-for-word aligned -- .opencode/agent/phase-orchestrator.md's Workflow step 9 (after the 'commit it as in step 6' sentence) and src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md step 4 (a new bullet between the block-present bullet and the Repeat-until bullet): 'If the report contains any Errors, Gaps, or Discrepancies but omits the conditional "Proposed Fix Phase" block (a non-conforming report -- the block is mandated by the reviewer's own report format), re-run the reviewer once; if the re-run still reports findings without the block, hand the findings to the user (as after the 3-cycle cap) and exit the loop without further cycles -- the re-run neither resets nor extends the 3-cycle cap, and the loop never stalls on a non-conforming report.' Task 130.110 (D1): the portable mirror src/biz/dfch/specmgr/feat/data/feat_review_instructions.md section 5 gains the worked example verbatim from .opencode/agent/feat-reviewer.md -- the 'Example (a plan whose highest existing phase is Phase 110, review cycle 1):' lead-in plus the fenced '#### Phase 120: Fix phase (review cycle 1)' block with its three Task 120.100/120.110/120.120 items -- closing the mirror drift (no harness-bundle regeneration: the changed file is under src/). Task 130.120 (D2, resolved with the user: option (a)): the narration mirrors the agent file's 'ask the user to confirm, then commit' -- feat_implement_instructions.md step 2's verify/commit bullet now reads 'mark the phase complete in the TodoWrite list, ask the user to confirm, then commit the phase as one Conventional Commit', step 3's single-session fallback commits 'as in step 2's own commit rule' (one source of the commit behavior), and neither .opencode/agent/phase-orchestrator.md (step 6, the winning side) nor .opencode/command/implement-feature.md (the user's per-flow 'commit without asking' override) was touched; the Task 130.120 line was updated in place with the resolution and its [NEEDS DECISION] flag removed. Test pins: tests/feat/prompts/test_implement_feat.py gains test_review_fix_loop_non_conforming_report_fallback (the G1 sentence verbatim) and test_commit_asks_user_to_confirm_first (the D2 confirm-first phrasing, both steps); tests/feat/prompts/test_review_feat.py gains test_conditional_proposed_fix_phase_worked_example (the D1 example's lead-in, heading, and first/last task lines). Gate green: ruff format/check, vulture, full pytest, specmgr docs + specmgr mcp-docs + specmgr harness-bundle regenerate-then-no-diff (the harness bundle was regenerated for the phase-orchestrator.md edit and left in the tree), specmgr lint on this README, and the plan's full feat parse; Tasks 130.100/130.110/130.120 are checked off. The REQ-004 loop re-runs the reviewer (cycle 2) before the done closeout and the Phase 120 commit.

#### 2026-11-16 17:06:20.000Z - Phase 120: ACC-001..ACC-005 walked and checked off (evidence)

Task 120.100's walk portion executed at status `review` (precondition confirmed in the plan's frontmatter, both by raw read and by the live `get_feat`): ACC-001 -- `src/biz/dfch/specmgr/feat/prompts/implement_feat.py` + `src/biz/dfch/specmgr/feat/data/feat_implement_instructions.md` (the DEC UUID :7; the verbatim optional-delegation phrase + `never assumed present` :9-11; the phase-by-phase `TodoWrite` list :14-15; verify-before-advancing incl. re-run gate / inspect diff / confirm ACs :48-51; `Never write or edit code files yourself -- delegate all implementation.` :56-57; the single-session fallback :63-64 + `This is never a hard failure` :68; the loop pins: the feature is then at `review`, not yet `done` :75-76, the `done` closeout happens only after a clean loop exit :80-82, `[NEEDS DECISION]` resolved via `question` :86-87, `capped at 3 review-fix cycles` :94-95, `Stop at review until the loop exits clean` :106-107); registered at `docs/MCP.md:1876` with the exactly-once pin in `tests/feat/prompts/test_implement_feat.py::TestImplementFeatRegistration` (run: 19 passed, 4 subtests, exit 0). ACC-002 -- `src/biz/dfch/specmgr/feat/prompts/review_feat.py` + `src/biz/dfch/specmgr/feat/data/feat_review_instructions.md` (the nine ISO/IEC 25010:2023 characteristics :51-96; the three checklist layers :45/:98/:112; the five report sections `## Errors`/`## Gaps`/`## Discrepancies`/`## Improvements`/`## Positives` in order :128/:131/:134/:137/:140; report-only :147; the conditional-section pins :152-153/:157-158/:163-164/:167-169); the portability cross-check against `.opencode/agent/feat-reviewer.md` (the same five sections :162-176, the same conditional section :182-212); registered at `docs/MCP.md:1918` with `tests/feat/prompts/test_review_feat.py::TestReviewFeatRegistration` (run: 22 passed, 16 subtests, exit 0). ACC-003 -- `.opencode/agent/feat-reviewer.md`'s `### Proposed Fix Phase (conditional)` section :182 (the heading rule :189-194, the task rule :195-198, the `[NEEDS DECISION]` rule :199-201, the example block :203-212). ACC-004 -- `.opencode/agent/phase-orchestrator.md`'s Workflow step 8 `Finish (at review)` :101-105, step 9 `Review-fix loop (capped at 3 cycles)` incl. the `question` resolution :106-119, and step 10 `Done closeout (only after a clean loop exit)` :120-123. ACC-005 -- DEC `docs/dec/dec-4481b1fd-26e5-46bc-8f1b-236b638385b2-portable-mcp-prompts-may-narrate-optional-host-native-subage.md` (frontmatter id :4, status :5; H1 :11; Decision Outcome :30-32), this plan's Related Decisions bullet (body line 95), and `feat_implement_instructions.md:7` naming the UUID. Task 120.100/120.110 remain unchecked: the REQ-004 review-fix loop, the `review` -> `done` hop, and the phase commit are orchestrator work.

#### 2026-11-16 13:53:09.000Z - Phase 110 complete (implement_feat + review_feat + review-fix loop)

Phase 110 (Tasks 110.100-110.160) implemented and gated. Shipped: `feat/prompts/implement_feat.py` + `feat/data/feat_implement_instructions.md` (the orchestrator-discipline narration: read the plan in full, a phase-by-phase `TodoWrite` list, each phase delegated to a fresh subagent via "your host's task-delegation tool, if one exists" (DEC 4481b1fd-26e5-46bc-8f1b-236b638385b2, never assumed present), independently verify each subagent's result before advancing (re-run the phase gate, inspect the diff, confirm the acceptance criteria), never write or edit code files yourself, the explicit fallback to direct single-session implementation, and the capped review-fix loop -- 3 cycles, `[NEEDS DECISION]` resolved via the `question` tool, the implementer appends the reviewer's ready-to-paste fix phase, `done` only after a clean loop exit) and `feat/prompts/review_feat.py` + `feat/data/feat_review_instructions.md` (the portable feat-reviewer mirror: the nine ISO/IEC 25010:2023 characteristics + the feature-plan convention layer + the optional local layer, the five report sections as TSK-compatible checklist items each with a file:line citation, report-only, and the conditional "Proposed Fix Phase" section -- NEXT UNUSED phase number, tasks derived STRICTLY from Errors/Gaps/Discrepancies, the `[NEEDS DECISION]` flagging rule), both registered in `feat/prompts/__init__.py`. Four OpenCode files edited: `feat-reviewer.md` gains the conditional Proposed Fix Phase block + the `[NEEDS DECISION]` rule; `phase-orchestrator.md`'s Workflow gains the capped 3-cycle review-fix loop with the verify-at-`review` -> loop -> `done`-only-after-clean-exit ordering; `implement-feature.md` gains the automatic review-fix step prose, the FSM-aligned `progress` -> `review` status hop (precondition: the `planning` -> `progress` start hop at the first implementation action) and its "a a" typo fix; `review-feature.md`'s report-section enumeration gains the conditional section. Tests: `tests/feat/prompts/test_implement_feat.py` + `tests/feat/prompts/test_review_feat.py` (the ACC-001/ACC-002 content assertions + the registration pins) and the `_FEAT_PROMPTS` pin in `tests/general/tools/test_i18n_feat_adr_exclusion.py` (gains both prompts). Smoke-test evidence: both prompts render with the `$id` substitution (no unsubstituted placeholder, no KeyError) and both appear in the registered prompt surface of the dev-CLI `specmgr mcp-docs` regeneration (`docs/MCP.md`, 35 -> 37 prompts) -- a literal fresh-host MCP session is not reproducible from this environment (the session server predates the prompts, Operational gotcha 6). Docs sync: `AGENTS.md`'s `feat/` bullet, `server.py`'s module docstring, `CHANGELOG.md` `[Unreleased]`, and the three regenerations (`specmgr docs`, `specmgr mcp-docs`, `specmgr harness-bundle` -- only the four edited `.opencode/` files' sha256/content entries changed, the 32-file count pin unchanged). Gate green: ruff format/check (2381 files), vulture, full pytest (6111 passed / 18 skipped), regenerate-then-no-diff (byte-identical), and `specmgr lint` on this README; feature status moved `progress` -> `review` (the phase commit is the orchestrator's).

#### 2026-11-16 12:15:57.000Z - Phase 100 complete (DEC 4481b1fd-26e5-46bc-8f1b-236b638385b2 accepted)

DEC created via the `dec` domain with the two-hop `draft` -> `proposed` -> `accepted` status sequence (the plan's E1 fix), UUID recorded in Related Decisions, feature status moved `planning` -> `progress`, phase gate green (ruff/vulture/pytest/specmgr lint).

#### 2026-11-16 11:20:00.000Z - Plan refined per feat-refiner report (E1/E2, G1-G4, D1, I1/I2/I4 applied)

Applied the user-approved feat-refiner findings of 2026-11-16: Task 100.100 now uses the two-hop `draft` -> `proposed` -> `accepted` DEC status sequence (E1); explicit feature status hops `planning` -> `progress` (Task 100.100) and `progress` -> `review` (Task 110.160) were added (E2); final verification now runs at `review` with the `done` closeout only after a clean REQ-004 loop exit (G1, see Decisions Made); ACC-001/ACC-004 pin the previously unpinned REQ-001/REQ-004 clauses (G2/G3); the five declaration-site feature references gained `FEAT` tags (G4); Operational gotcha (6) records the stale v0.38.0 session MCP server (I1); Tasks 110.130/110.140 were extended (I2/I4). Frontmatter `updated` re-stamped (D1).

#### 2026-11-16 07:22:23.000Z - Renamed to feat-263-delegation-prompts (GitHub issue #263)

GitHub issue #263 was opened for this feature; the folder was renamed `feat-0-delegation-prompts` -> `feat-263-delegation-prompts` via `set_feat_id` (frontmatter `id` rewritten by the tool). The body's self-references (the Overview's branch name, the gotcha-1 `specmgr lint` path, Current Status's branch name) were updated to the new id. The implementation branch must be named exactly `feat-263-delegation-prompts`, cut from `dev`.

#### 2026-11-15 05:30:00.000Z - Created: carved out of feat-167 (D1 rescope)

Created from the unstarted remainder of feat-167-mcp-lifecycle-commands-2 (its Phase 110, Phase 120 and Phase 140, REQ-003..REQ-006 and ACC-003..ACC-006/ACC-011), renumbered from 001. The Task texts were refreshed against the post-ADR-removal tree (the decision carrier is a DEC, no `adr-toc` regeneration) and the 32-file harness bundle.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-17 09:04:39.000Z - Post-done D1 fixed as Phase 150 without a status hop; I1/I2 carried advisory

The user-run post-done feat-reviewer review of 2026-11-17 reported no Errors, no Gaps, one Discrepancy (D1: the stale `feat` domain package docstring prompt enumeration -- the "Prompts:" sentence in src/biz/dfch/specmgr/feat/__init__.py named only create_feat/update_feat/refine_feat, pre-existing since feat-167 Phase 100, propagated into the committed generated mirror docs/api/biz.dfch.specmgr.feat.md), and two advisory Improvements (I1: the `review-feature` skill's one-line summary omits the conditional "Proposed Fix Phase" section; I2: the `implement-feature` command's "commit, push and create a pr" wording). Decision: fix D1 only, on the unmerged branch (no PR open yet, so the correction lands pre-merge). The feature status stays `done` -- no status hop is needed or legal (the feat FSM has no `done` -> `progress` transition; the plan's 2026-11-16 decision anticipated post-done awkwardness) and content edits do not change status. I1 stays advisory per the strict derivation rule (Improvements never derive tasks) and is operationally harmless (the skill defers to the agent file verbatim); fixing it would mean touching `.opencode/` and regenerating the harness bundle, outside this phase's scope. I2 is retained by this plan's own D2 decision (the command file is the user's per-flow override). The phase heading reads "post-done review" rather than the loop's "review cycle k" because the REQ-004 loop (capped at 3 cycles) already exited clean and this is a standalone user-initiated review, not a loop cycle.

#### 2026-11-17 01:18:32.000Z - D2 resolution: option (a) -- the narration mirrors the agent file's confirm-then-commit

The user chose option (a) for Task 130.120 (review cycle 1): the portable narration's commit step mirrors .opencode/agent/phase-orchestrator.md step 6 ('Ask the user to confirm, then stage and commit that phase as one Conventional Commit'), not .opencode/command/implement-feature.md's per-flow 'Commit without asking me first, but do not push' override, which stays as the user wrote it. Rationale: the agent file is the standing orchestrator behavior the narration mirrors (the plan's own prompt/agent/command sync obligation), while the command file is the user's per-flow override for that one host surface; the narration therefore carries the confirm-first rule in step 2 as the single source, and step 3's single-session fallback references it ('commit as in step 2's own commit rule').

#### 2026-11-16 11:20:00.000Z - Final verification runs at `review`; `done` only after a clean review-fix loop exit

Adopted resolution of the feat-refiner's G1: Task 120.100 walks the acceptance criteria while the feature is at `review` (set in Task 110.160), the REQ-004 review-fix loop runs from there, and the `done` closeout happens only after a clean loop exit. Rationale: as originally written, a reviewer finding after `done` would require an unstated `done` -> `progress` hop, and dev's feat FSM makes `planning`/`progress` -> `done` illegal; this matches feat-167's actual cycles 1-4 (loop at `review`, `done` closeout only after clean exit).

#### 2026-11-15 05:30:00.000Z - Carve the unstarted feat-167 phases into this feature (D1, option b)

The user chose to rescope rather than continue on the bare `feat-167` branch (option a) or keep the status quo (option c). Rationale: the release precheck's closeout gate attributes merged PRs to a feature folder by head-ref name, and feat-167's bare branch name made PR #260 invisible to it. A fresh feature whose branch equals its folder name restores attribution, and feat-167 can close to `done` for the slice it actually shipped.
