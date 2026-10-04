---
classification: null
created: '2026-10-04T12:59:26.936+02:00'
id: feat-128-schema-not-used
status: planning
type: feat
updated: '2026-10-04T18:18:30.910+02:00'
version: 1.0.0
---

# Feature: Make Agents Use Schema Information for Create and Update Operations

## Plan

### Overview

Agents often take several round-trips to create or update specmgr artifacts without querying the domain JSON schema (available as the `specmgr://<domain>/schema` resource for every whole-body domain; adr has no such resource) before authoring the document body (GitHub issue #128). This feature answers three questions: (1) why an agent does not use the schema information, (2) whether the schema is correct, complete, or lacks information, and (3) a plan so that agents use fewer round-trips for create and update operations.

### Requirements

- REQ-001: Document the root causes why agents skip querying the schema before create/update operations, based on the existing prompt flows, tool docstrings, and observed agent sessions.
- REQ-002: Audit the 12 whole-body domains' generated JSON schemas (`specmgr://<domain>/schema`) for correctness and completeness as agent-facing authoring guidance, and record all gaps found -- including, as an explicit finding for question 2, that adr has no schema resource at all (no `specmgr://adr/schema` resource and no generator entry in `commands/schema.py`'s `_GENERATORS`), which is why the audit set is 12, not 13.
- REQ-003: Produce a concrete plan that reduces the number of tool round-trips for create and update operations across the whole-body domains.
- REQ-004: The plan must identify the required changes (prompts, tool docstrings, schema content, new tools or resources) and track them as follow-up work rather than implementing them in this feature.

### Acceptance Criteria

- [ ] ACC-001: The feature (or a linked decision record) contains a written root-cause analysis answering issue #128's question 1, citing at least one concrete instruction gap or observed agent behavior.
- [ ] ACC-002: The schema audit answers question 2 with a gap list (each gap: domain, section, problem, proposed fix) or an explicit documented conclusion that the schemas are complete.
- [ ] ACC-003: The round-trip-reduction plan for question 3 exists as an actionable task list (in this feature or a linked follow-up feature) with at least one measurable target.

### Scope

#### Included

- Investigation of the existing create/update prompt flows, tool docstrings, and resource descriptions across all domains.
- Audit of the generated JSON schema resources of the 12 whole-body domains (adr is the only domain without a `specmgr://<domain>/schema` resource; its absence is a recorded finding, not an audited schema).
- Drafting the round-trip-reduction plan and tracking its implementation as follow-up work.

#### Explicitly Out Of Scope

- Implementing the plan's changes (tracked as follow-up features).
- Changes to the Pydantic models' parsing or validation behavior.
- Performance work on the doc cache or similarity features.

### Dependencies

#### Depends On

- GitHub issue #128 (this feature tracks it).
- Related prior work: feat-94-frontmatter-schema.

#### Blocks

- The follow-up implementation feature created in Phase 110 (id TBD).

### Design Notes

Preliminary observations to confirm in Phase 100: (a) the generated JSON schemas capture section structure (required/optional, minItems) but for free-form markdown sections the expected content shape lives only in the prose descriptions with empty properties, so the `specmgr://<domain>/template` and `specmgr://<domain>/example` resources may carry more actionable authoring guidance; (b) every whole-body create prompt already instructs agents to fetch template/example/schema (step 3) and every whole-body update prompt likewise (step 5), so for prompt-driven flows the gap may be discoverability, perceived cost, or compliance rather than a missing instruction; (c) no `create_<d>` tool description (the agent-visible tools/list metadata) mentions the schema/template/example resources at all, so tool-direct flows that never invoke the prompt get zero pointers -- a distinct discoverability surface to confirm in Phase 100.

### Related Decisions

- feat-94-frontmatter-schema: expose frontmatter created/updated date+time format in JSON Schema as a pattern.
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts organized in .specmgr with feature-driven work units.

### Task List

#### Phase 100: Investigation

- [ ] Task 100.100: Reproduce and document agent round-trip behavior for create/update without a schema query (issue #128 question 1).
- [ ] Task 100.110: Audit the 12 whole-body domains' `specmgr://<domain>/schema` resources for correctness and completeness -- including each resource's agent-facing title/description metadata, whose current wording is provenance-oriented (how it is generated and kept current) rather than usage-oriented (fetch before authoring a body) -- and record adr's missing schema resource as an explicit finding (question 2).
- [ ] Task 100.120: Capture a quantitative round-trip baseline (tool calls per successful create and per successful update, per domain) from observed agent sessions, to ground the ACC-003 measurable target.

#### Phase 110: Planning

- [ ] Task 110.100: Draft the round-trip-reduction plan with concrete prompt, docstring, and schema changes (question 3), explicitly evaluating the `create_<d>`/generic `update` tool descriptions -- the agent-visible tools/list metadata that never mention the schema/template/example resources -- as a candidate fix location alongside prompts and schema content.
- [ ] Task 110.110: Track the plan's implementation as a follow-up feature and cross-reference it from this document.

## Progress

### Current Status

**As of 2026-10-04**: Feature created (status: planning). Investigation of issue #128's three questions has not started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-04T18:16:05.000+02:00 - Plan review: improvements I3/I4 applied

Applied the two remaining review improvements: Task 100.110's audit surface now covers each schema resource's agent-facing title/description metadata (I3, currently provenance-oriented rather than usage-oriented); Task 110.100 now explicitly evaluates the `create_<d>`/generic `update` tool descriptions as a candidate fix location (I4).

#### 2026-10-04T18:06:47.000+02:00 - Plan review: scope fixes

Plan review findings applied: corrected the schema-audit scope from 13 domains to the 12 whole-body domains that actually carry a `specmgr://<domain>/schema` resource (adr has none; recorded as an explicit question-2 finding in REQ-002/Scope/Task 100.110, resolving the audit-vs-plan scope mismatch); added Task 100.120 to capture the quantitative round-trip baseline ACC-003's measurable target needs; extended Design Notes with the tool-description discoverability surface (hypothesis c). Review improvement items (resource-metadata audit surface, tool descriptions as a Phase 110 fix location) were deferred and applied in a subsequent entry.

#### 2026-10-04T12:59:26.635+02:00 - Created

Feature document created from GitHub issue #128 (agents do not use schema information for create and update operations). Plan drafted; investigation pending.

### Related PRs / Commits

- [Issue #128](https://github.com/dfch/biz.dfch.SpecMgr/issues/128): tracking issue for this feature.
