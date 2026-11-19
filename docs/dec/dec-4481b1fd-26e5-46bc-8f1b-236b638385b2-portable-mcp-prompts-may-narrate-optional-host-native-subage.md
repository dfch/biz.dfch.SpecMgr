---
classification: null
created: '2026-11-16T13:09:22.149+01:00'
id: 4481b1fd-26e5-46bc-8f1b-236b638385b2
status: accepted
type: dec
updated: '2026-11-16T13:09:34.158+01:00'
version: 1.0.0
---

# Portable MCP prompts may narrate optional host-native subagent delegation, degrading gracefully when absent

## Context and Problem Statement

MCP prompts in this codebase return narration text to whatever LLM session invoked them and may name host-native tools the server does not implement: the standing precedent is `create_req`, which narrates "use the `question` tool", and neither `question` nor `TodoWrite` is a tool of this MCP server. The new `implement_feat`/`review_feat` prompts of FEAT feat-263-delegation-prompts (its REQ-001/REQ-002) want to narrate phase-by-phase subagent delegation so that inside OpenCode they drive genuine multi-agent orchestration (the host's `task` tool with a subagent per phase) while staying portable to hosts without such a tool. This decision records the concrete pattern FEAT feat-263-delegation-prompts implements from: whether and how that delegation narration is sanctioned, what the degradation contract is when the host has no delegation tool, and the advisory character of the narration.

## Decision Drivers

- Portability across arbitrary MCP hosts: the prompt must remain usable on a host that exposes no task-delegation tool at all.
- No hard failure when the delegation tool is absent: the narration degrades to direct single-session implementation rather than erroring.
- Consistency with the existing narration-only prompt precedent (e.g. `create_req` naming the `question` tool).
- The plan's ACC-001 requirement that the fallback sentence be explicit in the prompt text.

## Considered Options

- Option 1 (chosen): Narrate OPTIONAL host-native subagent delegation, always with an explicit single-session fallback.
- Option 2: Hard-require a delegation tool (breaks portability -- hosts without a task tool could not use the prompt at all).
- Option 3: No delegation narration (stays portable but forfeits the OpenCode multi-agent benefit the feature exists to deliver).

## Decision Outcome

Option 1: portable MCP prompts may narrate optional host-native subagent delegation by referring to "your host's task-delegation tool, if one exists"; such narration MUST always carry an explicit fallback to direct single-session implementation, and it is advisory markdown -- not a mechanical contract, not a server-side dependency.

### Consequences

- Every future `<verb>_feat`-style prompt follows this shape (optional-delegation naming plus the explicit fallback sentence).
- Prompt/agent/command text duplication across the MCP prompt and the OpenCode-native files is unavoidable and is kept in sync as a standing review-checklist item.
- No new dependency, no new host API, no server-side enforcement.

### Confirmation

Exercised by the `implement_feat`/`review_feat` prompts and their content tests in FEAT feat-263-delegation-prompts Phase 110 (its ACC-001 asserts the optional-delegation naming, the orchestrator-discipline narration, and the explicit fallback sentence).

## Roles and Responsibilities

### Accountable

dfch

### Responsible

- OpenCode agent
- user decision (plan locked during feat-263-delegation-prompts planning)

## Source

GitHub issue #263 (https://github.com/dfch/biz.dfch.SpecMgr/issues/263), tracked as FEAT feat-263-delegation-prompts (REQ-005); the pattern originates in the unstarted remainder of FEAT feat-167-mcp-lifecycle-commands-2 (its Phase 110 / ACC-011), which this feature carries.

## Pros and Cons

### Option 1: Narrate optional delegation with an explicit single-session fallback

Pros: stays fully portable (a host without a delegation tool simply implements the phases itself, one at a time), matches the codebase's standing narration-only precedent, and delivers the OpenCode multi-agent benefit the feature exists for. Cons: the same workflow text is duplicated across the MCP prompt and the OpenCode-native files and must be kept in sync as a standing review-checklist item.

### Option 2: Hard-require a delegation tool

Pros: the narration could then assume delegation and omit the fallback wording. Cons: breaks portability -- a host without a task tool could not use the prompt at all, which no existing prompt in this codebase ever does.

### Option 3: No delegation narration

Pros: maximum portability with nothing to keep in sync. Cons: forfeits the OpenCode multi-agent orchestration benefit the feature exists to deliver, leaving every implementation single-session even where a host could drive it multi-agent.

## More Information

- Inside OpenCode specifically, the narration means: invoke the host's `task` tool with a `subagent_type` per phase (a `phase-implementer` subagent per phase, a `feat-reviewer` subagent for review) under the orchestrator/implementer boundary where the orchestrator never writes files (`edit`/`write` are denied to it) -- genuine multi-agent orchestration, since OpenCode exposes both the specmgr MCP tools and its own native tools in the same session.
- The decision carrier is a DEC (not an ADR -- the ADR domain was retired in favor of DEC by FEAT feat-46-remove-adr).
- DEC e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr/feat/` conventions): the plan-and-progress README layout the `implement_feat`/`review_feat` prompts operate on.

## Updates

### 2026-11-16 12:08:50.000Z - Created

The decision record was drafted as Phase 100 of FEAT feat-263-delegation-prompts, before its Phase 110 instruction files, because its UUID is an input to them.
