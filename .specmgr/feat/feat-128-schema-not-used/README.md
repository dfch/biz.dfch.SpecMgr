---
classification: null
created: '2026-10-04T12:59:26.936+02:00'
id: feat-128-schema-not-used
status: done
type: feat
updated: '2026-10-07T06:21:40.890Z'
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

- [x] ACC-001: The feature (or a linked decision record) contains a written root-cause analysis answering issue #128's question 1, citing at least one concrete instruction gap or observed agent behavior. Met in Phase 100 (commit b2d2c98): root-cause-analysis.md in this folder answers question 1 from 8 controlled fresh-agent runs -- 0/4 no-prompt and 0/2 prompt-update runs fetched the schema while the prompt-create runs did (2/2), the update prompts' unconditional "Check the schema" step was skipped 2/2, and four concrete instruction gaps are cited (silent `create_<d>`/update/validate tool descriptions, context-insensitive update step, the prb lead-sentence frame absent from template/example and the schema's machine layer, and the 2-hop resource route plus non-invocable MCP prompts on the opencode host).
- [x] ACC-002: The schema audit answers question 2 with a gap list (each gap: domain, section, problem, proposed fix) or an explicit documented conclusion that the schemas are complete. Met in Phase 100 (commit b2d2c98): schema-audit.md in this folder records the gap list as 16 quadruples (domain, section, problem, proposed fix) -- zero enum across all 12 schemas, only the two feat-94 timestamp patterns, properties: {} markdown leaves per-domain counts, the closed-vocabulary absences, the provenance-oriented resource and schema-silent prompt metadata (verbatim), and adr's missing schema resource with code citations (commands/schema.py \_GENERATORS, adr/resources/).
- [x] ACC-003: The round-trip-reduction plan for question 3 exists as an actionable task list (in this feature or a linked follow-up feature) with at least one measurable target. Met in Phase 110 (commit 00cd7cb): round-trip-reduction-plan.md in this folder holds the plan (Direction-1 vs Direction-2 evaluation, Direction-2-first recommendation, change inventory C1-C15, measurable targets T1-T3 stated as baseline -> target -> measurement), and its actionable task list lives in the linked follow-up feature feat-189-reduce-agent-round-trips (4 phases, 16 tasks, T1-T3 in its ACC-005).

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

- feat-189-reduce-agent-round-trips (GitHub issue #189) -- the implementation of the round-trip-reduction plan drafted in Phase 110.

### Design Notes

Preliminary observations to confirm in Phase 100: (a) the generated JSON schemas capture section structure (required/optional, minItems) but for free-form markdown sections the expected content shape lives only in the prose descriptions with empty properties, so the `specmgr://<domain>/template` and `specmgr://<domain>/example` resources may carry more actionable authoring guidance -- the third review verified that the loss extends beyond free-form sections: all 12 generated schemas carry zero `enum` and only the two feat-94 frontmatter timestamp `pattern`s, every markdown leaf (`MarkdownParagraph`/`MarkdownListItem`) renders as `properties: {}`, and all domain closed vocabularies/regex aliases (REQ `Level`'s RFC 2119 set, RSK 5x5/TARA, VCR DTAIS/AC-NNN, TSK checkbox markers, status values) are absent from the schemas, appearing at most as prose 'e.g.' examples; (b) every whole-body create prompt contains a dedicated template/example/schema reference step ('Use the template/example/schema as references'; rsk's variant heading: 'Use the template/example/schema and the domain knowledge as references') at step 3 in req/uc/tsk/qa/gol/rsk/vcr/feat, step 4 in dec/sop/sysrs, step 10 in prb and every whole-body update prompt a dedicated 'Check the schema' step (step 4 in req/uc/tsk/qa/rsk, step 5 in vcr/feat/gol, step 6 in dec/sop/sysrs, step 9 in prb) -- step numbers verified across all 24 instruction files in the third review -- so for prompt-driven flows the gap may be discoverability, perceived cost, or compliance rather than a missing instruction; (c) no `create_<d>` tool description (the agent-visible tools/list metadata) mentions the schema/template/example resources at all, so tool-direct flows that never invoke the prompt get zero pointers (verified in the third review); (d) the schemas describe the parsed JSON document shape (property names like `statement`/`characteristics`), not the markdown the agent authors, so the prompts' 'confirm field names' instruction conflates two artifact layers; and MCP prompts are pull-based -- an agent must explicitly invoke the prompt, so in tool-direct flows the prompts' schema instructions are architecturally invisible, whereas tool/resource description metadata is always in the agent's context (the create/update prompts' own `title`/`description` metadata is likewise silent about the schema, verified in the third review).

Phase 100 artifacts (written 2026-10-05; sibling files of this README): `root-cause-analysis.md` -- the written answer to issue #128 question 1 (ACC-001), hypotheses (a)-(d) adjudicated against 8 controlled agent runs with four concrete instruction gaps; `schema-audit.md` -- the ACC-002 gap list (16 quadruples), the adr-missing finding with code citations, the resource/prompt/tool metadata audit (verbatim strings), the per-domain closed-vocabulary baseline verification, the packaged-vs-docs drift check, and the published-vs-worktree surface diff; `round-trip-baseline.md` -- the ACC-003 grounding tables (per-run + domain x operation aggregates, payload sizes, schema-fetch counts) and the explicit baseline numbers Phase 110 may use; `evidence/` -- raw `--format json` event streams (11 files: smoke, prompt-surface probe, the 8 formal runs, plus the one recorded retry attempt), `manifest.md` (verbatim instruction strings, seeds, metrics, verdicts, harness incident, the verbatim agent-facing metadata record), `final-docs/` (the eight success-verdict documents), the rendered prompts, and the harness scripts.

Phase 110 artifacts (written 2026-10-05; sibling file of this README plus a new feature): `round-trip-reduction-plan.md` -- the written answer to issue #128 question 3 (ACC-003): the goal statement, the explicit evaluation of Direction 1 (increase schema discoverability/usage) and Direction 2 (reduce the *need* for the schema), the recommendation (Direction-2-first hybrid), the change inventory C1-C15 plus the post-review C17 (schema resource -> `get_<d>_schema` tool conversion, ADR-first) mapped to the 16 audit gaps and the 4 instruction gaps, and the measurable targets T1-T3 stated against the Phase 100 baseline; and the follow-up feature `feat-189-reduce-agent-round-trips` (GitHub issue #189), whose phase-structured Task List (Phase 100 P0, Phase 105 P1-pre, Phase 110 P1, Phase 120 P2, Phase 130 verification) is the plan's actionable implementation inventory.

### Related Decisions

- feat-94-frontmatter-schema: expose frontmatter created/updated date+time format in JSON Schema as a pattern.
- ADR e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts organized in .specmgr with feature-driven work units.

### Task List

#### Phase 100: Investigation

- [x] Task 100.100: Reproduce and document agent round-trip behavior for create/update without a schema query (issue #128 question 1) with a fixed methodology: two domains (one simple, e.g. tsk, one complex, e.g. prb or dec) x create and update, a fresh MCP-only agent, one controlled run with and one without the prompt pre-invoked.
- [x] Task 100.110: Audit the 12 whole-body domains' `specmgr://<domain>/schema` resources for correctness and completeness -- including each resource's agent-facing title/description metadata, whose current wording is provenance-oriented (how it is generated and kept current) rather than usage-oriented (fetch before authoring a body) -- and record adr's missing schema resource as an explicit finding (question 2); also audit the create/update prompts' own `title`/`description` metadata (currently silent about the schema), and verify per domain the closed-vocabulary baseline recorded in Design Notes (a) (zero `enum`, two timestamp `pattern`s, `properties: {}` leaves) into concrete gap entries.
- [x] Task 100.120: Capture a quantitative round-trip baseline (tool calls per successful create and per successful update, per domain) from observed agent sessions, to ground the ACC-003 measurable target, including per-domain schema payload size (KB) and schema-fetch counts per session to ground the 'perceived cost' hypothesis.

#### Phase 110: Planning

- [x] Task 110.100: Draft the round-trip-reduction plan with concrete prompt, docstring, and schema changes (question 3), explicitly evaluating the `create_<d>`/generic `update` tool descriptions -- the agent-visible tools/list metadata that never mention the schema/template/example resources -- as a candidate fix location alongside prompts and schema content, and explicitly evaluating the opposite direction -- reducing the *need* for the schema (markdown-level guidance via template/example, richer `validate` error messages, the schema demoted to constraint discovery) rather than increasing schema usage -- since REQ-003/ACC-003 require fewer round-trips, not more schema queries.
- [x] Task 110.110: Track the plan's implementation as a follow-up feature and cross-reference it from this document.

## Progress

### Current Status

**As of 2026-10-05**: Feature complete, status moving to review. Phase 100 (Investigation) answered issue #128 question 1 (root-cause-analysis.md: discoverability plus a rational skip of a 2-hop, constraint-free fetch; the only closed-form rule agents failed on lived in prose they never saw) and question 2 (schema-audit.md: 16 gap quadruples, adr has no schema resource at all), and captured the quantitative baseline (round-trip-baseline.md); Phase 110 (Planning) answered question 3 with round-trip-reduction-plan.md (Direction-2-first hybrid, measurable targets T1-T3) tracked as the follow-up feature feat-189-reduce-agent-round-trips (GitHub issue #189). All three acceptance criteria met (evidence inline above).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-05T20:10:52.000+02:00 - Plan revision: C17 `get_<d>_schema` tool conversion adopted

Plan revision (author-directed, post-implementation review): in `round-trip-reduction-plan.md`, Direction-1 lever 3 (the 1-hop `get_<d>_schema` tool) is reopened and adopted as C17 -- a dated revision paragraph after the rejection text carries the five rationale points (the plan's own P2 falsifies the zero-constraint argument; the RCA's #1 root cause is discoverability in the always-in-context tool surface; the ddfb1109/ec9f5262 precedent generalizes to the last per-domain authoring resource; C6/C7 collapse into the tool description; 94 -> 106 tool cost acknowledged with T2's 0-fetch target unchanged); the change inventory gains a C17 row (P1-pre, Phase 105) and the C7 row is marked superseded (ids are permanent); the priority order gains a P1-pre (Phase 105) bullet between P0 and P1, and the P1 bullet now reads "C6-C12 (C7 superseded by C17)". The follow-up feature `feat-189-reduce-agent-round-trips` is amended to match (new Phase 105 with the ADR + tool tasks, Tasks 110.100/110.120 retargeted, Task 110.110 removed leaving its number gap, REQ-007/ACC-003/Scope/Design Notes updates, its own Updates entry). No status changes: feat-128 stays `review` on PR #191, feat-189 stays `planning`; the PR is not merged.

### Decisions Made

#### 2026-10-05T20:10:52.000+02:00 - Plan revision: schema access surface converts to `get_<d>_schema` tools (C17)

Author-directed post-implementation-review decision: the plan's rejected Direction-1 lever 3 (the 1-hop `get_<d>_schema` tool per domain) is reopened and adopted as C17 -- the 12 `specmgr://<domain>/schema` resources convert to 12 `get_<d>_schema` tools (resources removed), ADR-first, extending the house precedents ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-reads moved to the `get_<d>` tool, `/{id}` resource dropped) and ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (listing moved to the `list_<d>` tool, `/list` resource dropped) to the last remaining per-domain authoring resource. Two of the plan's rejection arguments no longer hold: the plan's own P2 (C13/C14, `json_schema_extra` enum/pattern enrichment) falsifies the "zero-constraint machine layer" argument -- the schema becomes constraint-bearing -- and the RCA's #1 root cause (discoverability in the always-in-context tool surface; 0/4 no-prompt runs ever entered the resource layer) shows a resource description cannot fix what only a tool description can. Template and example are already tools (`get_<d>_template`/`get_<d>_example`), so the conversion makes the domain authoring surface 100% tool-based; C6 (pointer clauses) and C7 (usage-oriented rewording) collapse into the `get_<d>_schema` tool description, and the 2-hop resource route (instruction gap 4) is eliminated. Cost acknowledged: 94 -> 106 always-in-context tools (terse descriptions). T2's "0 schema fetches" target is unchanged -- the conversion makes the designated constraint-discovery fallback path cheap and findable; it never prescribes a fetch. The ADR is to be written as feat-189's first implementation task (new Phase 105, P1-pre, before the C6/C8 pointer retargeting that names the tool).

#### 2026-10-05T09:42:25.000+02:00 - Phase 110: direction choice, rejections, and the flagged scope tension

Phase 110 plan decisions (all recorded in `round-trip-reduction-plan.md`): (1) **Direction** -- a Direction-2-first hybrid (reduce the *need* for the schema) is recommended over Direction 1 (increase schema discoverability/usage); the evidence line that decided it: the prompt condition -- the one that actually makes agents fetch the schema -- cost MORE round-trips (tsk create 9 vs 5, prb create 9 vs 7), while the no-prompt agents' only failure was the closed-form prb lead-sentence frame they never saw (+2 calls), and every no-prompt run succeeded with zero schema fetches -- so REQ-003's "fewer round-trips, not more schema queries" is met by moving the missing guidance into the artifacts already fetched and making the unneeded guidance explicitly optional; the retained D1 subset is strictly non-prescriptive (pointer clauses in tool descriptions, usage-oriented resource/prompt metadata, metadata-only schema enrichment). (2) **Rejections/deferrals** -- the 1-hop `get_<d>_schema` tool is rejected (the observed success path needs no schema at all; the schema's machine layer carries zero constraints; +12 tools would bloat the always-in-context surface); the gap 14 authoring-view payload split is deferred (no observed failure it fixes; after the demotion the fetch is rare); the missing adr schema resource is documented as a deliberate exclusion in the `create_adr` description rather than adding a 13th generator (ADR is the phasing-out domain, and `create_adr`'s own typed input parameters already carry the structure). (3) **Scope tension flagged (binding for the follow-up feature's Phase 120)** -- emitting the closed sets as a Pydantic `Literal`/`Field(pattern=)` would change validation behavior (previously accepted documents could start failing), so the plan mandates `json_schema_extra`-only metadata: agent-visible in the generated schema, inert in Pydantic; every closed set in the inventory was verified code-enforced during the Phase 100 audit, so the metadata documents existing behavior, and parse-behavior invariance tests pin that (feat-189-reduce-agent-round-trips Task 120.100/120.110).

#### 2026-10-05T07:44:27.000+02:00 - Phase 100 run-harness decisions (as implemented)

The binding user-approved harness design was implemented with these recorded choices: (1) the two domains are **tsk** (simple) and **prb** (complex; the plan allowed "prb or dec", prb was picked for its mandatory lead-sentence template + 7 5W2H headings, which exercises the closed-form guidance that lives only in prose); (2) all 8 formal runs are fresh, non-interactive `opencode run` sessions (opencode v1.18.34) in bare temp dirs under `/tmp/opencode/feat128/runs/`, model pinned to `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2` (the orchestrator's model) with `--format json` as the primary evidence source, run sequentially against the published 0.34.0 specmgr MCP server so no `SPECMGR_*_DIR` env var ever points at the repo (zero repo pollution, verified); (3) the **prompt-pre-invoked mechanism actually used is harness-fetched** -- a probe run proved a fresh opencode session cannot invoke MCP prompts natively at all (reply `NO_PROMPT_TOOL`, zero tool calls), so the four `-prompt` runs had their domain prompt rendered out-of-band by a throwaway Python MCP client (`get_prompt` against the same uvx server) and prepended to the instruction verbatim between BEGIN/END markers; (4) the update prompts' required `id` argument was filled with the placeholder `UNKNOWN` (never the seed UUID) in both conditions, so document discovery via `list_<d>`/`get_<d>` stays part of the measured round trip; (5) update runs were seeded by the harness writing a parseable document directly into `<run-dir>/docs/<domain>/<uuid>.md` (fresh UUIDs, valid frontmatter, `status: active`) before launch; (6) per-run protocol: 600 s timeout, retry once with the identical instruction on a hung/failed run and record both attempts (applied to `prb-create-prompt`, whose attempt 1 timed out mid-draft and whose retry is the formal result); (7) a harness incident (a mis-built second runner re-executed two create cells into already-populated dirs) was detected, the contaminated outputs discarded, all dirs wiped and re-seeded, and the whole 8-run sequence re-executed from a clean state -- the incident is documented in `evidence/manifest.md` and excluded from the baseline; (8) findings live as sibling files of this README (`root-cause-analysis.md`, `schema-audit.md`, `round-trip-baseline.md`, `evidence/`), no YAML frontmatter (they are not specmgr documents; feat-9 precedent), formatted with `specmgr mdformat`.

### Related PRs / Commits

- [Issue #128](https://github.com/dfch/biz.dfch.SpecMgr/issues/128): tracking issue for this feature.
