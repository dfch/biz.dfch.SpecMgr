---
classification: null
created: '2026-10-04T12:59:26.936+02:00'
id: feat-128-schema-not-used
status: planning
type: feat
updated: '2026-10-04T20:22:01.000+02:00'
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

#### Blocks

- The follow-up implementation feature created in Phase 110 (id TBD).

### Design Notes

Preliminary observations to confirm in Phase 100: (a) the generated JSON schemas capture section structure (required/optional, minItems) but for free-form markdown sections the expected content shape lives only in the prose descriptions with empty properties, so the `specmgr://<domain>/template` and `specmgr://<domain>/example` resources may carry more actionable authoring guidance -- the third review verified that the loss extends beyond free-form sections: all 12 generated schemas carry zero `enum` and only the two feat-94 frontmatter timestamp `pattern`s, every markdown leaf (`MarkdownParagraph`/`MarkdownListItem`) renders as `properties: {}`, and all domain closed vocabularies/regex aliases (REQ `Level`'s RFC 2119 set, RSK 5x5/TARA, VCR DTAIS/AC-NNN, TSK checkbox markers, status values) are absent from the schemas, appearing at most as prose 'e.g.' examples; (b) every whole-body create prompt contains a dedicated 'Use the template/example/schema as references' step (step 3 in req/uc/tsk/qa/gol/vcr/feat, step 4 in dec/sop/sysrs, step 10 in prb) and every whole-body update prompt a dedicated 'Check the schema' step (step 4 in req/uc/tsk/qa/rsk, step 5 in vcr/feat/gol, step 6 in dec/sop/sysrs, step 9 in prb) -- step numbers verified across all 24 instruction files in the third review -- so for prompt-driven flows the gap may be discoverability, perceived cost, or compliance rather than a missing instruction; (c) no `create_<d>` tool description (the agent-visible tools/list metadata) mentions the schema/template/example resources at all, so tool-direct flows that never invoke the prompt get zero pointers (verified in the third review); (d) the schemas describe the parsed JSON document shape (property names like `statement`/`characteristics`), not the markdown the agent authors, so the prompts' 'confirm field names' instruction conflates two artifact layers; and MCP prompts are pull-based -- an agent must explicitly invoke the prompt, so in tool-direct flows the prompts' schema instructions are architecturally invisible, whereas tool/resource description metadata is always in the agent's context (the create/update prompts' own `title`/`description` metadata is likewise silent about the schema, verified in the third review).

### Related Decisions

- feat-94-frontmatter-schema: expose frontmatter created/updated date+time format in JSON Schema as a pattern.
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts organized in .specmgr with feature-driven work units.

### Task List

#### Phase 100: Investigation

- [ ] Task 100.100: Reproduce and document agent round-trip behavior for create/update without a schema query (issue #128 question 1) with a fixed methodology: two domains (one simple, e.g. tsk, one complex, e.g. prb or dec) x create and update, a fresh MCP-only agent, one controlled run with and one without the prompt pre-invoked.
- [ ] Task 100.110: Audit the 12 whole-body domains' `specmgr://<domain>/schema` resources for correctness and completeness -- including each resource's agent-facing title/description metadata, whose current wording is provenance-oriented (how it is generated and kept current) rather than usage-oriented (fetch before authoring a body) -- and record adr's missing schema resource as an explicit finding (question 2); also audit the create/update prompts' own `title`/`description` metadata (currently silent about the schema), and verify per domain the closed-vocabulary baseline recorded in Design Notes (a) (zero `enum`, two timestamp `pattern`s, `properties: {}` leaves) into concrete gap entries.
- [ ] Task 100.120: Capture a quantitative round-trip baseline (tool calls per successful create and per successful update, per domain) from observed agent sessions, to ground the ACC-003 measurable target, including per-domain schema payload size (KB) and schema-fetch counts per session to ground the 'perceived cost' hypothesis.

#### Phase 110: Planning

- [ ] Task 110.100: Draft the round-trip-reduction plan with concrete prompt, docstring, and schema changes (question 3), explicitly evaluating the `create_<d>`/generic `update` tool descriptions -- the agent-visible tools/list metadata that never mention the schema/template/example resources -- as a candidate fix location alongside prompts and schema content, and explicitly evaluating the opposite direction -- reducing the *need* for the schema (markdown-level guidance via template/example, richer `validate` error messages, the schema demoted to constraint discovery) rather than increasing schema usage -- since REQ-003/ACC-003 require fewer round-trips, not more schema queries.
- [ ] Task 110.110: Track the plan's implementation as a follow-up feature and cross-reference it from this document.

## Progress

### Current Status

**As of 2026-10-04**: Feature created (status: planning). Investigation of issue #128's three questions has not started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-04T20:22:01.000+02:00 - Plan review: third-round fixes applied

Third plan review (2 errors, 5 gaps, 3 discrepancies, 8 improvements, 6 verified positives); plan edits applied, implementation not started. Applied: corrected Design Notes (b) step numbers to the verified per-domain values (create: step 3 in req/uc/tsk/qa/gol/vcr/feat, step 4 in dec/sop/sysrs, step 10 in prb; update: step 4 in req/uc/tsk/qa/rsk, step 5 in vcr/feat/gol, step 6 in dec/sop/sysrs, step 9 in prb); extended Design Notes (a) with the verified closed-vocabulary baseline (all 12 schemas: zero `enum`, two timestamp `pattern`s, `properties: {}` markdown leaves); added Design Notes (d) on the markdown-to-JSON impedance mismatch and pull-based MCP prompt delivery; specified the Task 100.100 reproduction methodology; added the create/update prompts' `title`/`description` metadata to the Task 100.110 audit surface; extended Task 100.120 with schema payload size (KB) and schema-fetch counts; added the 'reduce the need for the schema' alternative direction to Task 110.100; removed the feat-94-frontmatter-schema line from Depends On (closed context, already listed under Related Decisions). Prior-round audit trail: the second review's I3/I4 are recoverable from the 18:06:47 deferral note, its I1/I2 are unrecoverable and are recorded here as lost.

#### 2026-10-04T18:16:05.000+02:00 - Plan review: improvements I3/I4 applied

Applied the two remaining review improvements: Task 100.110's audit surface now covers each schema resource's agent-facing title/description metadata (I3, currently provenance-oriented rather than usage-oriented); Task 110.100 now explicitly evaluates the `create_<d>`/generic `update` tool descriptions as a candidate fix location (I4).

#### 2026-10-04T18:06:47.000+02:00 - Plan review: scope fixes

Plan review findings applied: corrected the schema-audit scope from 13 domains to the 12 whole-body domains that actually carry a `specmgr://<domain>/schema` resource (adr has none; recorded as an explicit question-2 finding in REQ-002/Scope/Task 100.110, resolving the audit-vs-plan scope mismatch); added Task 100.120 to capture the quantitative round-trip baseline ACC-003's measurable target needs; extended Design Notes with the tool-description discoverability surface (hypothesis c). Review improvement items (resource-metadata audit surface, tool descriptions as a Phase 110 fix location) were deferred and applied in a subsequent entry.

#### 2026-10-04T12:59:26.635+02:00 - Created

Feature document created from GitHub issue #128 (agents do not use schema information for create and update operations). Plan drafted; investigation pending.

### Related PRs / Commits

- [Issue #128](https://github.com/dfch/biz.dfch.SpecMgr/issues/128): tracking issue for this feature.
