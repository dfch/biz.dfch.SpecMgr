---
classification: null
created: '2026-10-05T09:40:30.333+02:00'
id: feat-189-reduce-agent-round-trips
status: planning
type: feat
updated: '2026-10-05T20:10:52.000+02:00'
version: 1.0.0
---

# Feature: Reduce Agent Round-Trips for Create and Update Operations

## Plan

### Overview

Implements the round-trip-reduction plan drafted in feat-128 Phase 110
(`.specmgr/feat/feat-128-schema-not-used/round-trip-reduction-plan.md`,
GitHub issue #128 question 3): fewer tool round-trips per successful
create/update across the whole-body domains -- explicitly **not** more
schema queries. The plan's Phase 100 evidence (8 controlled fresh-agent
runs, 12-domain schema audit, quantitative baseline) shows the no-prompt
agents already succeed with zero schema fetches using the 1-hop
`get_<d>_template`/`get_<d>_example` tools, that their one failure is the
closed-form prb lead-sentence frame living only in prose they never
fetch (+2 calls on retry), and that the prompt condition costs **more**
round-trips (tsk create 9 vs 5, prb create 9 vs 7), not fewer. The change
inventory (C1-C15) therefore moves the closed-form guidance into the
artifacts agents already fetch (templates, examples, instruction steps),
keeps the schema demoted to constraint discovery, and adds only
non-prescriptive pointers to the always-in-context tool surface; the
measurable targets T1-T3 are in the Acceptance Criteria.

### Requirements

- REQ-001: The markdown-level artifacts a create agent fetches (template/example) carry every closed-form rule the Phase 100 evidence shows agents fail on, verbatim and before the first create call: the prb lead-sentence bracketed frame in the template and example, the tsk task-text fidelity directive, and the req/rsk/qa closed sets as template comments (plan inventory C1-C3, C9-C11; audit gaps 04, 05, 07, 08, 09; instruction gap 3).
- REQ-002: The 12 create instruction files reference the `get_<d>_template`/`get_<d>_example` tools (1 hop) and make the schema fetch conditional, and the 12 update instruction files make the schema fetch conditional on whole-body or structural changes (plan inventory C4, C5; instruction gaps 2, 4).
- REQ-003: The agent-facing metadata names the structure reference without prescribing a fetch: the 12 `create_<d>` tool descriptions plus the generic `update` and `validate` tool descriptions, the 12 schema resource descriptions (usage-oriented, parsed-JSON view, template pointer), and the 24 create/update prompt descriptions (plan inventory C6-C8; audit gaps 11, 12, 13, 15, 16; instruction gap 1).
- REQ-004: The 12 generated schemas carry the closed sets as machine-readable metadata (enum/pattern) emitted via `json_schema_extra` only, with zero change to parse/validation behavior, regenerated with `specmgr schema` and the packaged copies refreshed (plan inventory C13, C14; audit gaps 02-10).
- REQ-005: The absence of a `specmgr://adr/schema` resource is documented as a deliberate exclusion in the `create_adr` tool description (the tool's own typed input parameters are the authoritative ADR structure reference), with no new schema generator entry for adr (plan inventory C15; audit gap 01).
- REQ-006: The re-run of the feat-128 Phase 100 methodology (identical instruction strings and seeds, pinned model, worktree server surface, n>=3 per cell) meets the measurable targets T1-T3, and the outcome is recorded in this feature folder (plan inventory verification phase; the "linked follow-up feature" branch of feat-128 ACC-003).
- REQ-007: The schema access surface converts from the 12 `specmgr://<domain>/schema` resources to 12 `get_<d>_schema` tools under a new ADR extending ddfb1109-422d-4507-8dbc-dc5e4bec9614 and ec9f5262-9912-49d0-903f-fcfb54f28c13; each tool returns the generated schema with a usage-oriented description (absorbing plan C7), the resources are removed, and all plan pointers (C6, C8) name the tool (plan inventory C17; audit gaps 11, 13; instruction gap 4).

### Acceptance Criteria

- [ ] ACC-001: The prb template and prb example both carry the exact bracketed lead-sentence frame, the tsk template's leading comment no longer induces task-text rewrites, and the req/rsk/qa templates name their closed sets in comments -- each modified file round-trips through its domain parser (REQ-001; T1's structural precondition).
- [ ] ACC-002: All 12 create instruction files reference the `get_<d>_template`/`get_<d>_example` tools and carry a conditional schema step, and all 12 update instruction files carry the context-sensitive schema step (REQ-002).
- [ ] ACC-003: The live worktree server surface carries the new clauses -- probed via `tools/list`, `list_resources`, and the prompt metadata (harness `mcp_probe.py`/`mcp_descs.py`): the 12 `create_<d>` + `update` + `validate` tool descriptions, the 12 `get_<d>_schema` tool descriptions (usage-oriented; the 12 `specmgr://<domain>/schema` resources are gone), and the 24 create/update prompt descriptions -- and the `create_adr` description documents the adr schema exclusion; the C17 ADR exists under `docs/adr/` and is listed via `specmgr adr-toc` (REQ-003, REQ-005, REQ-007).
- [ ] ACC-004: `uv run --frozen specmgr schema` exits 0 with the 12 updated `docs/<domain>_schema.json` carrying the inventory's enum/pattern metadata and byte-identical packaged copies, and the parse-behavior invariance tests pass (every closed set accepted/rejected exactly as before the metadata change) (REQ-004).
- [ ] ACC-005: The Phase 130 re-run meets the measurable targets in all n runs of every cell, recorded in `round-trip-rerun.md` in this feature folder -- T1 (create without prompt: prb first-try `create_prb` success, at most 5 calls, 0 validation-failure retries, 0 schema fetches; baseline 7 calls including 1 validation-failure -> retry cycle; tsk at most 5 calls with the requested task texts verbatim; baseline 5 calls with a "Task 1:" prefix deviation) and T2 (create with prompt, both domains: at most 7 calls per successful create, 0 schema fetches, 0 600 s timeouts; baseline 9 calls each with 1 schema fetch on the 2-hop resource route each, and one prb prompt attempt timed out at 600 s) and T3 (update, all four cells: at or below the baseline call count per cell -- tsk 5 no-prompt / 6 prompt, prb 5 / 5 -- with 0 schema fetches for the local edits and 0 closed-form validation failures) (REQ-006).

### Scope

#### Included

- The packaged data files: the prb template and example (lead-sentence frame), the tsk template (comment rewording), the req/rsk/qa templates (closed-set comments), all 12 create instruction files, and all 12 update instruction files.
- The agent-facing metadata clauses: the 12 `create_<d>` tool descriptions, the generic `update` and `validate` tool descriptions, the `create_adr` tool description, the 12 `get_<d>_schema` tool descriptions (new tools) with the 12 schema resources removed, and the 24 create/update prompt descriptions.
- The schema access surface conversion (plan C17): the ADR under `docs/adr/`, the 12 `get_<d>_schema` tools, the 12 resource removals, and the registration updates (`server.py` docstring, `AGENTS.md`, `docs/MCP.md`, `docs/api/`).
- The model `json_schema_extra` metadata for the 12 domains, schema regeneration (`specmgr schema`) with packaged-copy refresh, and the parse-behavior invariance tests.
- The Phase 130 verification re-run: the harness extension to the worktree server, 8 cells x n>=3, and the outcome report in this feature folder.

#### Explicitly Out Of Scope

- Any change to parsing or validation behavior -- the `json_schema_extra` metadata is inert by construction (never `Literal` or `Field(pattern=)`); if a closed set is found that is not already code-enforced, stop and record a decision item instead of starting to enforce it (the enum-vs-validation tension, Design Notes).
- New tools other than the 12 `get_<d>_schema` read tools (plan C17) and new resources.
- An adr schema generator entry (the exclusion is documented instead, REQ-005).
- The generator-level authoring-view / payload split of the schemas (audit gap 14, deferred in the plan) and gap 03's per-leaf content hints (resolved by the resource-description wording plus the schema demotion instead).
- Releasing the changed surface (verification runs against the worktree server; publishing is the release SOP's job, audit gap 16) and any performance work on the doc cache or similarity features.

### Dependencies

#### Depends On

- feat-128-schema-not-used: the investigation feature whose Phase 110 plan this implements -- `.specmgr/feat/feat-128-schema-not-used/round-trip-reduction-plan.md` (change inventory C1-C15, measurable targets T1-T3), grounded in its Phase 100 artifacts (`root-cause-analysis.md`, `schema-audit.md`, `round-trip-baseline.md`, `evidence/`).
- GitHub issue #189 (https://github.com/dfch/biz.dfch.SpecMgr/issues/189): the tracking issue for this feature.

### Design Notes

Direction and why (plan Recommendation): a Direction-2-first hybrid -- reduce
the *need* for the schema (fold the closed-form rules into template/example,
context-sensitive instruction steps, the schema demoted to constraint
discovery) as the primary direction, kept honest by a minimal,
non-prescriptive Direction-1 subset (pointer clauses in tool descriptions,
usage-oriented tool/prompt metadata, metadata-only schema enrichment).
The deciding evidence line: the prompt condition -- the one that actually
makes agents fetch the schema -- cost **more** round-trips (tsk create 9 vs
5, prb create 9 vs 7), while the no-prompt agents' **only** failure was the
closed-form lead-sentence frame they never saw (+2 calls), and every
no-prompt run succeeded with zero schema fetches. Fewer round-trips is
therefore met by moving the missing guidance into the artifacts already
fetched and making the unneeded guidance explicitly optional; the tool-
surface clauses are pointers, never imperatives to fetch. Post-review
revision (2026-10-05, author-directed): the plan's rejected 1-hop
`get_<d>_schema` tool lever was reopened as C17 -- the 12 schema resources
convert to tools (ADR-first, Phase 105), extending the ddfb1109/ec9f5262
tool-over-resource precedent to the last per-domain authoring resource;
T1-T3 are unchanged.

Enum-vs-validation-behavior tension (flagged by the plan, binding for
Phase 120): adding a closed set as a Pydantic `Literal` or
`Field(pattern=)` would **change** validation behavior -- previously
accepted documents could start failing -- which is out of scope for this
feature. The plan's scope rule is therefore binding: C13 emits the sets as
`json_schema_extra` metadata only, which appears in the generated JSON
schema (agent-visible) but is ignored by Pydantic at validation time. Every
closed set in the inventory was verified code-enforced during the Phase 100
audit (per-domain `field_validator` or regex `@alias`), so the metadata
documents behavior that already exists. Task 120.100 re-verifies this per
set with code citations before emitting, and Task 120.110 pins the
invariance with tests; if a set turns out not to be code-enforced, that is
a model-with-schema-metadata decision to raise, not to implement silently.

Phase 130 verification deviations from the Phase 100 baseline (both
recorded in the report): the server surface is the **worktree** (the
changes are not yet released; the published-vs-worktree deltas are
documented in feat-128's `schema-audit.md`), and **n>=3 per cell** (the
baseline's own limitation note recommends it to get a variance estimate;
the baseline was n=1 per cell, one pinned model, one host). Everything else
is held identical: the instruction strings (`evidence/instructions/`), the
seeds (`evidence/seeds/`, fresh UUIDs per the harness), the pinned model
`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`, the 600 s timeout, and the
retry-once protocol. Harness reference:
`.specmgr/feat/feat-128-schema-not-used/evidence/harness/` (`run_all.sh`,
`mcp_probe.py`, `parse_events.py`).

### Related Decisions

- feat-128-schema-not-used (GitHub issue #128): the Phase 110 plan this feature implements -- `round-trip-reduction-plan.md` (Direction 1 vs Direction 2 evaluation, recommendation, change inventory C1-C15, measurable targets T1-T3), grounded in its Phase 100 artifacts `root-cause-analysis.md` (question 1: the four instruction gaps), `schema-audit.md` (question 2: the 16 gaps), and `round-trip-baseline.md` (question 3's baseline).

### Task List

#### Phase 100: P0 -- Closed-Form Rules Into the Artifacts Agents Already Fetch

- [ ] Task 100.100: (C1, C2) Add the exact bracketed lead-sentence frame `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` to the prb template's single leading HTML comment (the model permits exactly one comment between the H1 and the lead sentence; keep the filled-in lead sentence as the concrete instance) and add the same frame comment to the prb example; verify both files round-trip through parse_prb and the existing prb template/example tests pass.
- [ ] Task 100.110: (C3) Reword the tsk template's leading HTML comment: remove the sentence "Number the tasks so that they are easier to track" (observed in the feat-128 baseline to induce "Task 1:" rewrites of the requested task texts) and instead direct keeping each task's text as given by the user, flat checklist, one item per line; the template's own example items (`- [ ] Task 1: ...` / `- [x] Task 2: ...` / `- [ ] Task 3: ...`) carry the "Task N:" prefix too, so reword them to drop it as well, keeping a plain flat checklist; verify the tsk template tests pass.
- [ ] Task 100.120: (C4) Repoint all 12 create instruction files' template/example/schema reference step ("Use the template/example/schema as references"; rsk's variant heading: "Use the template/example/schema and the domain knowledge as references") at (step 3 in req/uc/tsk/qa/gol/rsk/vcr/feat, step 4 in dec/sop/sysrs, step 10 in prb) to the `get_<d>_template`/`get_<d>_example` tools (1 hop) and make the schema fetch conditional -- only on structural uncertainty or when resolving a validation error.
- [ ] Task 100.130: (C5) Make all 12 update instruction files' "Check the schema" step (step 4 in req/uc/tsk/qa/rsk, step 5 in vcr/feat/gol, step 6 in dec/sop/sysrs, step 9 in prb) context-sensitive: fetch the schema only for whole-body rewrites or structural changes (add/remove/rename sections, edit closed-form content), and skip it for local splices where the raw body is already in context (update still validates the result as a whole document).

#### Phase 105: P1-pre -- Schema Access Surface: ADR + `get_<d>_schema` Tools (C17)

- [ ] Task 105.100: (C17) Write the ADR recording the schema access surface conversion -- the 12 `get_<d>_schema` tools replacing the 12 `specmgr://<domain>/schema` resources -- extending ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-reads) and ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (listing) to the last per-domain authoring resource; record the rationale (the plan's P2 enrichment falsifies the zero-constraint rejection argument; the RCA's #1 root cause is discoverability in the always-in-context tool surface; the 2-hop resource route is eliminated; C6/C7 collapse into one surface; 94 -> 106 tool cost acknowledged); create via the `create_adr` MCP tool, validate, register via `specmgr adr-toc`.
- [ ] Task 105.110: (C17) Implement the 12 `get_<d>_schema` tools (one per whole-body domain, mirroring the `get_<d>_template`/`get_<d>_example` tool shape) returning the domain's generated schema with usage-oriented descriptions (absorbing C7: when to fetch -- constraint discovery, structural questions, unresolved validation errors -- what it is -- the parsed-JSON view, not the markdown view, point at the domain template -- provenance sentence kept); remove the 12 `specmgr://<domain>/schema` resources; add registration tests (all 12 tools registered, no schema resources remain) and content-identity tests (each tool's output byte-identical to `docs/<domain>_schema.json`); regenerate `specmgr docs`/`mcp-docs`/`adr-toc` and update the registration surfaces (`server.py` module docstring, `AGENTS.md` per-domain bullets, `docs/MCP.md`).

#### Phase 110: P1 -- Non-Prescriptive Pointers in Always-In-Context Metadata

- [ ] Task 110.100: (C6) Add one non-prescriptive clause to each of the 12 `create_<d>` tool descriptions and to the generic `update` and `validate` tool descriptions naming the domain's `get_<d>_schema` tool (and the `get_<d>_template`/`get_<d>_example` tools) as the structure reference (available from Phase 105) -- a pointer, never an imperative to fetch.
- [ ] Task 110.120: (C8) Add one clause to the 24 create/update prompt descriptions naming the `get_<d>_schema` (and the `get_<d>_template`/`get_<d>_example`) tools as the structure reference.
- [ ] Task 110.130: (C9, C10, C11) Fold the remaining closed sets into the templates as HTML comments: the req template's `## Level` section names the full RFC 2119 set (`MUST`/`SHOULD`/`MUST NOT`/`SHOULD NOT`/`MAY` -- the set must match req's `_LEVEL_PATTERN` verbatim), the rsk template names the TARA 4-word set (pointing at `specmgr://rsk/tara`) and the Probability/Impact 1-5 range (pointing at `specmgr://rsk/risk-matrix`), the qa template's question prefix spells the rule (single category digit, 4-digit zero-padded per-category sequence); verify each modified template round-trips through its domain parser.
- [ ] Task 110.140: (C12) Verify the vcr template already carries the DTAIS set and the `AC-NNN (Method):` heading shape in its prose (verified present, no-op for those); the `full`/`partial`/`none` coverage set appears only as the filled-in `partial` instance -- fold the coverage set in as a comment the same way as Task 110.130.

#### Phase 120: P2 -- Schema Metadata Enrichment (Metadata Only)

- [ ] Task 120.100: (C13) For each of the 12 domains, first verify with code citations that every closed set in the plan inventory (status enum; req Level; tsk checkbox + update-entry heading; qa question prefix; prb lead-sentence pattern + 5W2H heading; rsk TARA + Probability/Impact heading; vcr DTAIS + coverage + AC-NNN heading) is already code-enforced, then emit the sets as `json_schema_extra` metadata (`enum`/`pattern`) on the relevant model fields -- metadata only, never `Literal` or `Field(pattern=)`, which would change validation behavior.
- [ ] Task 120.110: (C14) Regenerate the 12 schemas (`uv run --frozen specmgr schema`), refresh the packaged `data/<domain>_schema.json` copies per the existing drift check, and add parse-behavior invariance tests: every closed-set fixture previously accepted or rejected is accepted or rejected identically after the metadata change.
- [ ] Task 120.120: (C15) Add one clause to the `create_adr` tool description documenting the deliberate absence of the `specmgr://adr/schema` resource (the tool's own typed input parameters are the authoritative ADR structure reference); do not add an adr entry to `commands/schema.py`'s `_GENERATORS`.

#### Phase 130: Verification -- Re-Run the Phase 100 Methodology, Check T1-T3

- [ ] Task 130.100: Extend the harness (reused from `.specmgr/feat/feat-128-schema-not-used/evidence/harness/`: `run_all.sh`, `mcp_probe.py`, `parse_events.py`, `instructions/`, `seeds/`) so the opencode runs register the worktree's specmgr server instead of the published uvx server (per-run-directory project opencode config), and probe the live surface (`tools/list` + `list_resources` + prompt metadata) to record the worktree-surface deviation in the report.
- [ ] Task 130.110: Re-run all 8 cells (tsk + prb x create + update x with/without prompt) with the identical instruction strings and seeds, n>=3 per cell, the pinned model, the 600 s timeout, and the retry-once protocol.
- [ ] Task 130.120: Check the measurable targets -- T1 (create without prompt: tsk at most 5 calls with the requested task texts verbatim; prb first-try `create_prb` success, at most 5 calls, 0 validation-failure retries, 0 schema fetches), T2 (create with prompt: at most 7 calls per successful create in both domains, 0 schema fetches, 0 timeouts), T3 (update: at or below the baseline call count per cell, 0 schema fetches for local edits, 0 closed-form validation failures) -- and write the outcome report `round-trip-rerun.md` in this feature folder, with each target holding in all n runs of the cell.
- [ ] Task 130.130: Update this feature's Progress with the verification outcome; if any target is missed, add a corrective task using in-between numbering (e.g. Phase 135) rather than renumbering, and leave feat-128's ACC-003 closure to the feat-128 reviewer.

## Progress

### Current Status

**As of 2026-10-05**: Feature created (status: planning). feat-128 complete through Phase 110 (planning); this feature's implementation pending.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-05T20:10:52.000+02:00 - Plan revision: schema access surface converts to `get_<d>_schema` tools (C17)

Plan revision (author-directed, post-implementation review of feat-128): the plan's rejected 1-hop `get_<d>_schema` tool lever is reopened as C17 -- the 12 `specmgr://<domain>/schema` resources convert to 12 `get_<d>_schema` tools, ADR-first (the full rationale is recorded in feat-128's Decisions Made entry of the same date). This document amended accordingly: new Phase 105 (P1-pre) with Task 105.100 (write the ADR, extending ddfb1109-422d-4507-8dbc-dc5e4bec9614 and ec9f5262-9912-49d0-903f-fcfb54f28c13) and Task 105.110 (implement the 12 tools, remove the 12 resources, registration + content-identity tests, doc regeneration); REQ-007 added; ACC-003 revised to probe the 12 `get_<d>_schema` tool descriptions and the C17 ADR; Scope updated (Included gains the conversion; Out Of Scope now reads "new tools other than the 12 `get_<d>_schema` read tools"); Design Notes updated (usage-oriented tool/prompt metadata, post-review sentence). Task 110.100 (C6) and Task 110.120 (C8) retargeted to name the tools; Task 110.110 (C7) removed -- superseded by C17 -- leaving its number as a deliberate gap (no renumbering of 110.120/110.130/110.140). T1-T3, all other phase numbers, and the frontmatter status (`planning`) are unchanged.

#### 2026-10-05T09:40:30.000+02:00 - Created

Feature created to track the implementation of the round-trip-reduction
plan drafted in feat-128 Phase 110
(`.specmgr/feat/feat-128-schema-not-used/round-trip-reduction-plan.md`;
GitHub issue #128 question 3). The plan's change inventory (C1-C15) is the
phase-structured Task List above -- Phase 100: P0 template/example folds
and instruction-step changes; Phase 110: P1 non-prescriptive metadata
pointers and the remaining closed-form folds; Phase 120: P2 metadata-only
schema enrichment and the adr exclusion note; Phase 130: verification
re-run of the Phase 100 methodology checking the measurable targets T1-T3
(Acceptance Criteria). Tracked under GitHub issue #189.
