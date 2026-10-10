# AGENTS.md

Quick reference for OpenCode agents working on **biz.dfch.SpecMgr** — an artifact manager for system specifications.

## Status: domain packages implemented (the per-domain bullets below are the live enumeration)

Each package below follows the domain-first layout from ADR
ece4554b-725c-4f76-bc04-5d2b760363d2 ("Organize the codebase by
document-type domain: domain-first hierarchy for tools/prompts/resources,
shared versioned models") — one bullet per implemented package, document
type or cross-cutting:

- **`adr/`** (Architecture Decision Records) — the original, most complete
  domain. `adr/tools/` has 11 `@mcp.tool()` wrappers (`get_adr`, `list_adr`,
  `create_adr`, `update_frontmatter`, `update_section`,
  `option_list`/`option_create`/`option_read`/`option_update`/
  `option_delete`, `validate_adr`); ADR status changes go through the
  generic `set_status` tool in `general/tools/` (called with
  `type="adr"`, ADR-only `superseded_by`); `adr/resources/` exposes
  `specmgr://adr/{id}` only — no `specmgr://adr/list` (listing is the
  `list_adr` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13);
  `adr/prompts/` has
  narrated `create_adr`/`update_adr` prompts plus step-gated
  `create_adr_test`/`update_adr_test` A/B variants (see
  ADR ddd038f0-ae16-4f4b-beef-df06f7ed226f). Its Pydantic
  schema uniquely lives under the shared top-level `models/adr/` (not
  `adr/models/`) — see the "models location" note below.
- **`req/`** (Requirements) — `req/tools/` (`create_req`, `parse_req`,
  `list_req`); whole-body and line-range
  updates go through the generic `update` tool in `general/tools/`
  (`type="req"`), status changes through the generic `set_status` tool
  (`type="req"`), classification changes through the generic
  `set_classification` tool (`type="req"`), deletions through the generic
  `delete` tool (`type="req"`), disk-free/id-free dry-run content
  validation through the generic `validate` tool (`type="req"`) — the
  former `validate_req` tool was removed in favor of it
  (feat-81-83-validation); `req/resources/` (`specmgr://req/schema`,
  `specmgr://req/example`, `specmgr://req/template`; no `specmgr://req/{id}`
  — id-based reads are `get_req`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://req/list` —
  listing is the `list_req` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now also
  carries `error_count` and reports a failed-to-parse document inline
  (marker `title`/`status`, `error`, plus a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3); `req/prompts/`
  (`create_req`/`update_req`). Its schema lives at `req/models/v1/`, inside
  the domain package itself, not under top-level `models/`.
- **`uc/`** (Use Cases) — same tools/resources/prompts shape as `req/` but
  for use cases (`create_uc`, `parse_uc`,
  `list_uc`, `get_uc`, `get_uc_example`, `get_uc_template`), plus the
  read-only diagram surface (feat-185-uc-diagrams Phase 120, thin over the
  Phase 110 `uc/models/v2/renderer.py` + the import-free `plantuml/`
  package): `get_uc_diagram` (per-UC usecase diagram by id) and
  `get_uc_sequence_skeleton` (the deterministic sequence skeleton by id;
  UNATTRIBUTED markers where the §2.9.3 attribution cannot pre-fill) —
  both `_path_safety`-guarded and cache-aware, an existing-but-broken UC
  returning the non-raising `ParseFailureResult` per the feat-150
  precedent; `get_use_case_package_diagram` (multi-UC package diagram;
  `ids=None` = every UC in `list_uc` order, delegated to the `list_uc`
  tool; an id missing on disk or existing-but-broken becomes a skipped
  slot whose references take the deterministic unresolvable-note path —
  the render never fails on an id; a wrong-format id is a `ValueError`
  before any file access); `validate_plantuml` (the strict validation
  chain over diagram text — structure pre-flight always, then the single
  first-set-wins source or the all-unset structure-only floor — non-raising
  `PlantumlValidationResult`); `get_uc_plantuml_template`/
  `get_uc_plantuml_example` (the packaged PlantUML-source template/example,
  verbatim); and `plantuml_encode` (the classic `SoWkI…`-form URL text
  encoding — the `{enc}` payload of `GET {base}/svg/{enc}`; the tool takes
  no base URL, so it returns the encoding itself; fully offline); whole-body and
  line-range updates go through the generic
  `update` tool in `general/tools/` (`type="uc"`), status changes through
  the generic `set_status` tool (`type="uc"`), classification changes
  through the generic `set_classification` tool (`type="uc"`), deletions
  through the generic `delete` tool (`type="uc"`), disk-free/id-free
  dry-run content validation through the generic `validate` tool
  (`type="uc"`) — the former `validate_uc` tool was removed in favor of it
  (feat-81-83-validation), and the `get_uc` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
   text as-is (the text `update`'s `offset`/`limit` index into), with
   optional read-style `offset`/`limit` windowing of that raw read
   (raw-only; out-of-range values clamp, never error); no
  `specmgr://uc/{id}` resource for the same reason as
  REQ, and no `specmgr://uc/list` resource either — listing is the
  `list_uc` tool (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose
  `PagedResult` now also carries `error_count` and reports a
  failed-to-parse document inline (with a resolved `path`) rather than
   silently dropping it,
   feat-81-83-validation Phase 3), plus the static
   domain-knowledge resource `specmgr://uc/plantuml` — the frozen
   UC → PlantUML mapping and validation rulebook (raw markdown,
   `text/markdown`; feat-185-uc-diagrams Phase 100 — the normative spec
   for everything diagram-related in this domain) — and the packaged
   PlantUML-source pair `specmgr://uc/plantuml-template` /
   `specmgr://uc/plantuml-example` (the sequence-skeleton template and
   the complete, fully attributed "Buy Goods" sequence example; raw
   PlantUML source, `text/plain` — not markdown, not specmgr documents:
   no frontmatter, not `validate`-able; feat-185-uc-diagrams Phase 120);
  `uc/models/v2/renderer.py` — the three deterministic renderers the
  rulebook specifies (feat-185-uc-diagrams Phase 110): `render_uc_diagram`
  (the v1-port, rulebook §2.5–§2.6 — byte-for-byte the §2.6 reference
  rendering for the packaged example), `render_use_case_package` (multi-UC
  package diagram, §2.7–§2.8 — takes resolved `PackageDocument` facts, not
  directory handles), and `render_uc_sequence_skeleton` (§2.9 — the
  deterministic skeleton whose UNATTRIBUTED markers the Phase 120 prompt
  flow attributes); golden-pinned under `tests/fixtures/uc-diagrams/`
  (ACC-001); the skeleton imports the shared UNATTRIBUTED marker constant
  from the cross-cutting `plantuml/` package (see below) so renderer and
  structure checker cannot drift; the packaged
  `uc/data/uc_plantuml_template.md` / `uc_plantuml_example.md`
  single-diagram data files ship here too (their MCP tools/resources
  landed in Phase 120);
  `uc/prompts/` (`create_uc`/`update_uc`, plus
  `generate_uc_sequence_diagram` — the rulebook §3.8 agent flow for one
  use case's sequence diagram: read-first `specmgr://uc/plantuml`,
  `TodoWrite` plan, `get_uc` (a `ParseFailureResult` stops the flow), the
  §2.11 Subfunction judgment, `get_uc_sequence_skeleton`, attribution of
  every `UNATTRIBUTED` marker (the `question` tool MUST be used whenever
  not confident; pre-filled arrows are positional, not semantic, and may
  be corrected), the zero-marker rule, the `validate_plantuml` loop
  (green at the highest available layer before writing;
  `source_state != ok` with a source set ⇒ report + do not write; all
   unset ⇒ write with the `' validated: structure-only` header as the
   file's first line), the host-native write to
   `diagrams/uc/<id>.sequence.puml` (no specmgr tool writes `.puml`), and
   never commit), plus the OpenCode host surface (feat-185-uc-diagrams
   Phase 140 — the trio pattern of the `general` bullet's `repair` trio,
   minus a dedicated subagent: the flow is the prompt itself): the
   self-triggering `uc-diagram` skill
   (`.opencode/skill/uc-diagram/SKILL.md` — thin; points at the
   `generate_uc_sequence_diagram` prompt, the read-first
   `specmgr://uc/plantuml` rulebook, the deterministic-only CLI
   (`specmgr diagram uc` / `--check`, `plantuml-check`, `plantuml-encode`),
   and carries the plantuml-mcp watch note — prefer a host-configured
   plantuml MCP check/render tool if present, no dependency), and the
   `/uc-diagram <id>` command (`.opencode/command/uc-diagram.md` — runs the
   same prompt flow for the given UC id and reports per its step 10);
   pinned by `tests/opencode/test_skill_uc_diagram.py`. The Phase 140
   end-to-end walkthrough record (ACC-002: the question transcript, the
   validation verdict, the execution method) is committed as
   `tests/fixtures/uc-diagrams/buy-goods.sequence.walkthrough.md` alongside
   the pure, comment-free `buy-goods.sequence.walkthrough.puml` (the
   ACC-001 pinning test's source of truth). Schema at
   `uc/models/v1/` (legacy) and `uc/models/v2/` (current),
   inside the domain package, not `models/uc/`.
- **`tsk/`** (Task Lists) — same shape again (`create_tsk`,
  `parse_tsk`, `list_tsk`, `get_tsk`, `get_tsk_example`,
  `get_tsk_template`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="tsk"`), status changes through the generic
  `set_status` tool (`type="tsk"`), classification changes through the
  generic `set_classification` tool (`type="tsk"`), deletions through the
  generic `delete` tool (`type="tsk"`), and the `get_tsk` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
   text as-is (the text `update`'s `offset`/`limit` index into), with
   optional read-style `offset`/`limit` windowing of that raw read
   (raw-only; out-of-range values clamp, never error); disk-free/id-free
   dry-run content validation through the generic `validate` tool
   (`type="tsk"`) — the former `validate_tsk` tool was removed in favor of
   it (feat-81-83-validation); plus a distinct
  `implement_task` prompt (reads a task list via `get_tsk`, builds a
  `TodoWrite` list from its items, and uses the `question` tool to resolve
  ambiguity). Its resources are the usual `specmgr://tsk/schema`/
  `specmgr://tsk/example`/`specmgr://tsk/template` only — no
  `specmgr://tsk/{id}` and no `specmgr://tsk/list` resource (listing is
  the `list_tsk` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose
  `PagedResult` now also carries `error_count` and reports a
  failed-to-parse document inline (with a resolved `path`) rather than
  silently dropping it,
  feat-81-83-validation Phase 3). Schema
  at `tsk/models/v1/`, inside the domain package.
- **`qa/`** (Question and Answer) — same tools/resources/prompts shape as
  `req/`/`tsk/` but for requirements-elicitation Q&A interviews (`create_qa`,
  `parse_qa`, `list_qa`, `get_qa`, `get_qa_example`,
  `get_qa_template`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="qa"`), status changes through the generic
  `set_status` tool (`type="qa"`), classification changes through the
  generic `set_classification` tool (`type="qa"`), deletions through the
  generic `delete` tool (`type="qa"`), disk-free/id-free dry-run content
  validation through the generic `validate` tool (`type="qa"`) — the
  former `validate_qa` tool was removed in favor of it
  (feat-81-83-validation), and the `get_qa` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
   text as-is (the text `update`'s `offset`/`limit` index into), with
   optional read-style `offset`/`limit` windowing of that raw read
   (raw-only; out-of-range values clamp, never error); `qa/resources/`
  (`specmgr://qa/schema`, `specmgr://qa/example`,
  `specmgr://qa/template`; no `specmgr://qa/{id}` — id-based reads are
  `get_qa`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://qa/list` — listing is the `list_qa` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now also
  carries `error_count` and reports a failed-to-parse document inline
  (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3);
  `qa/prompts/`
  (`create_qa`/`update_qa`, plus `refine`). Schema at `qa/models/v2/`,
  inside the domain package, not `models/qa/` — QA is a single-schema
  (v2-only) domain: every question/answer category holds zero or more
  adjacent, un-headed pairs (`<!-- optional comment -->` +
  `> **<d>.<NNNN>**: {question}` block quote + free-form answer prose)
  directly inside a category section, no heading of its own per pair —
  each question carries the mandatory bold question-number prefix
  `**<d>.<NNNN>**: ` (single category digit per Q&A-bearing section,
  4-digit zero-padded per-category sequence; enforced by
  `QaQuestionAnswer`'s own `field_validator` in `qa/models/v2/`,
  feat-156), and an unanswered question carries a `TODO: ` placeholder
  (e.g. `TODO: answer pending`) as its answer text — a pure authoring
  convention, not parsed or validated — which replaced the legacy
  `_(awaiting response)_` marker the `refine` prompt previously shipped
  (feat-156 REQ-007/009) — plus a `## Elicitation Context` section
  (structurally identical to, but not one of, the 9 ISO/IEC 25010:2023
  characteristic sections) between `## General` and
  `## Functional Suitability`. An earlier `qa/models/v1/` schema (one
  `### {heading}` H3 per question/answer pair) existed alongside v2 during
  feat-14 and was removed entirely once every QA MCP tool/resource/prompt
  was repointed at v2 (feat-14 Phase 8) — there is no version-gate or
  dual-schema read support: a document shaped for the removed v1 schema
  fails v2 parsing with a structural
  `AssertionError`/`pydantic.ValidationError`, not a migration-specific
  error.
- **`prb/`** (Problem Statement) — same tools/resources/prompts shape as
  `req/`/`tsk`/`qa` but for Six-Sigma-style problem statements
  (`create_prb`, `parse_prb`, `list_prb`,
  `get_prb`, `get_prb_example`, `get_prb_template`); whole-body and
  line-range updates go through the generic
  `update` tool in `general/tools/` (`type="prb"`), status changes through
  the generic `set_status` tool (`type="prb"`), classification changes
  through the generic `set_classification` tool (`type="prb"`), deletions
  through the generic `delete` tool (`type="prb"`), and the `get_prb` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `offset`/`limit` index into), with
  optional read-style `offset`/`limit` windowing of that raw read
  (raw-only; out-of-range values clamp, never error); disk-free/id-free
  dry-run content validation through the generic `validate` tool
  (`type="prb"`) — the former `validate_prb` tool was removed in favor
  of it (feat-81-83-validation); `prb/resources/`
  (`specmgr://prb/schema`,
  `specmgr://prb/example`, `specmgr://prb/template`; no
  `specmgr://prb/{id}` — id-based reads are `get_prb`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://prb/list` — listing
  is the `list_prb` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose
  `PagedResult` now also carries `error_count` and reports a
  failed-to-parse document inline (with a resolved `path`) rather than
  silently dropping it,
  feat-81-83-validation Phase 3);
  `prb/prompts/` (`create_prb`/`update_prb`, narrated `TodoWrite` +
  `question`-tool-driven 5W2H interview flows). `create_prb` accepts an
  optional `qa_id` parameter that carries over already-answered 5W2H
  questions from a linked QA document, scanning all 10 Q&A-holding
  categories (`## Elicitation Context` plus the nine ISO/IEC 25010:2023
  characteristics), not just `## Elicitation Context`, pre-filling only
  the sub-questions a QA pair actually answers and asking the rest via
  the `question` tool as before. Every PRB now also carries a mandatory
  `problem_statement` lead paragraph (no heading of its own, directly
  under the H1, before `## Current State`) holding one sentence following
  a fixed template, enforced by a code-level `field_validator` — an
  in-place, **BREAKING** `prb/models/v1` schema evolution (not a new
  `prb/models/v2`): a pre-existing PRB document without the lead
  paragraph fails `parse_prb`/`get_prb` until it is added, and
  `update_prb`'s prompt instructions guide that recovery (re-read via
  `get_prb(id, raw=True)`, derive/confirm the sentence, insert it under
  the H1, then proceed) (feat-132-prb-update). Schema at
  `prb/models/v1/`, inside the domain package, not top-level
  `models/`.
- **`gol/`** (Goal) — same tools/resources/prompts shape as
  `req/`/`prb/` but for high-level business goals (the strategic
  "what the organization wants to achieve" level that sits above
  individual requirements) (`create_gol`,
  `parse_gol`, `list_gol`, `get_gol`,
  `get_gol_example`, `get_gol_template`); whole-body and line-range
  updates go through the generic
  `update` tool in `general/tools/` (`type="gol"`), status changes through
  the generic `set_status` tool (`type="gol"`), classification changes
  through the generic `set_classification` tool (`type="gol"`), deletions
  through the generic `delete` tool (`type="gol"`), disk-free/id-free
  dry-run content validation through the generic `validate` tool
  (`type="gol"`) — the former `validate_gol` tool was removed in favor of
  it (feat-81-83-validation), and the `get_gol` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
   body text as-is (the text `update`'s `offset`/`limit` index into), with
   optional read-style `offset`/`limit` windowing of that raw read
   (raw-only; out-of-range values clamp, never error); `gol/resources/`
   (`specmgr://gol/schema`,
  `specmgr://gol/example`, `specmgr://gol/template`; no
  `specmgr://gol/{id}` — id-based reads are `get_gol`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://gol/list` —
  `list_gol` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now also
  carries `error_count` and reports a failed-to-parse document inline
  (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3);
  `gol/prompts/`
  (`create_gol`/`update_gol`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_gol` first checks
   `list_gol` for a near-duplicate goal). Its schema lives at
   `gol/models/v1/`, inside the domain package, not top-level
   `models/`. The body mirrors REQ minus the `## Characteristics`
  and `## Level` sections (see `.specmgr/feat/feat-18-goal/README.md`).
- **`rsk/`** (Risk) — same tools/resources/prompts shape as
  `req/`/`prb/` but for risk-register entries (the scenario decomposed
  into `## Cause`/`## Trigger`/`## Consequence`, a 5x5 probability/impact
  assessment BEFORE mitigation (`## Initial Assessment`) and the same 5x5
  AFTER mitigation (`## Residual Assessment`) with the value in the H3
  heading itself (`### Probability {1..5}` / `### Impact {1..5}`, regex
  `@alias`-constrained, derived zone `level` always computed from the
  product), a TARA response strategy `## Strategy` (closed 4-value set
  `transfer`/`accept`/`reduce`/`avoid`), plus, after `## Residual
  Assessment`, the tail sections in body order: an optional `## Owner`
  (single-line value naming the responsible person/role), an optional
  `## Tags` (bullet list of free-form labels; `Tags.items` is now
  `list[MarkdownListItemWithNotes]`, so a loose-list continuation
  paragraph under a tag is captured in the item's `notes` instead of
  being silently dropped — structurally identical to `req`/`dec`/`gol`'s
  own `Tags`, `feat-102-133-rsk-tags-source`, GitHub issue #133), a
  mandatory `## Source` (single-line value naming the origin/authority of
  the risk, e.g. the QA document, discussion, or report it derives from —
  a thin `SourceBase` subclass in `rsk/models/v1/body.py`, each domain
  declaring and owning its own concrete leaf class per the domain-first
  convention, added by `feat-102-133-rsk-tags-source`, GitHub issue #102),
  and an optional `## More Information` (free-form))
  (`parse_rsk`, `get_rsk`, `list_rsk`, `get_rsk_example`,
  `get_rsk_template`, `create_rsk`); whole-body and line-range updates
  go through the generic `update` tool in `general/tools/`
  (`type="rsk"`), status changes through the generic `set_status` tool
  (`type="rsk"`), classification changes through the generic
  `set_classification` tool (`type="rsk"`), deletions through the generic
  `delete` tool (`type="rsk"`), and the `get_rsk` tool takes `raw: bool = False` —
   `raw=True` returns the frontmatter-stripped body text as-is (the text
   `update`'s `offset`/`limit` index into), with optional read-style
   `offset`/`limit` windowing of that raw read (raw-only; out-of-range
   values clamp, never error); disk-free/id-free dry-run content
   validation through the generic `validate` tool (`type="rsk"`) — the
   former `validate_rsk` tool was removed in favor of it
   (feat-81-83-validation); `rsk/resources/`
  (`specmgr://rsk/schema`, `specmgr://rsk/example`,
  `specmgr://rsk/template`, plus two static domain-knowledge resources
  `specmgr://rsk/tara` — what TARA is and when/how to apply each of the
  four words — and `specmgr://rsk/risk-matrix` — the 5x5 scale anchors,
  zone table, and product thresholds; no `specmgr://rsk/{id}` — id-based
  reads are `get_rsk`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://rsk/list` — `list_rsk` ships as a paged tool from day one,
  ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, and its `RskSummary` lines
  carry the residual-risk coordinates so a register-wide risk-matrix view
  can be built from the listing alone; its `PagedResult` now also carries
  `error_count` and reports a failed-to-parse document inline as a
  sentinel-derived failed row (`rsk.tools._sentinel`), with a resolved `path`
  like every other domain, rather than silently
  dropping it, feat-81-83-validation Phase 3); `rsk/prompts/`
   (`create_risk`/`update_risk` — the issue's literal wording, not the
   `rsk`-prefixed convention the tools/resources use). Its schema lives at
   `rsk/models/v1/`, inside the domain package, not top-level
   `models/`.
- **`dec/`** (Decision) — same tools/resources/prompts shape as
  `req/`/`prb/` but for decisions in general (not architecture-only)
  (`parse_dec`, `get_dec`, `list_dec`, `get_dec_example`,
  `get_dec_template`, `create_dec`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="dec"`), status
  changes through the generic `set_status` tool (`type="dec"`),
  classification changes through the generic `set_classification` tool
  (`type="dec"`), deletions through the generic `delete` tool
  (`type="dec"`), and
   the `get_dec` tool takes `raw: bool = False` — `raw=True` returns
   the frontmatter-stripped body text as-is (the text `update`'s
   `offset`/`limit` index into), with optional read-style `offset`/`limit`
   windowing of that raw read (raw-only; out-of-range values clamp, never
   error); disk-free/id-free dry-run content
   validation through the generic `validate` tool (`type="dec"`) — the
   former `validate_dec` tool was removed in favor of it
   (feat-81-83-validation); `dec/resources/`
  (`specmgr://dec/schema`, `specmgr://dec/example`,
  `specmgr://dec/template`; no `specmgr://dec/{id}` — id-based reads
  are `get_dec`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://dec/list` — `list_dec` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now
  also carries `error_count` and reports a failed-to-parse document
  inline (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3); `dec/prompts/`
  (`create_dec`/`update_dec`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_dec` first checks
  `list_dec` for a near-duplicate decision). Its schema lives at
  `dec/models/v1/`, inside the domain package, not top-level
  `models/`. A DEC keeps the ADR's general structure (MADR-style
  headings, `Options` collection) but is built on the generic
  `models/md` parser with the GOL/RSK/QA simple surface — no
  fine-grained mutation tools, no renderer: writes persist the
  caller's raw validated body byte-for-byte. Since `feat-29-dec-source-roles`
  (GitHub issue #29), a `dec` document also carries three new body
  sections between `## Decision Outcome` and `## Related Artifacts`: a
  mandatory `## Roles and Responsibilities` (RASCI — `### Accountable`
  single mandatory paragraph and `### Responsible` mandatory bullet list
  (>=1 item) are always required, unlike SOP's own optional-as-a-whole
  equivalent, since a decision must always have a named accountable
  owner; `### Support`/`### Consulted`/`### Informed` stay independently
  optional), an optional `## Tags` (bullet list of free-form labels,
  structurally identical to `req`'s own, absorbing the DEC half of
  `feat-133-tags-dec-rsk`, issue #133), and a mandatory `## Source`
  (structurally identical to `req`'s own). This is what the original
  issue's "ADR-style attributes such as `source`/`owner`" request
  resolved to — new **body** sections, not new `DecFrontmatter` fields;
  `DecFrontmatter` itself is unchanged. `Source` and the six RASCI
  classes (`Accountable`/`Responsible`/`Support`/`Consulted`/`Informed`/
  `RolesAndResponsibilities`) now live as shared base classes in the
  top-level `models/md/common_sections.py`, which `req`'s own `Source`
  and `sop`'s own six RASCI classes were refactored to subclass instead
  of duplicating the field/validator logic — `dec`'s new concrete
  classes subclass the same bases, each domain still declaring and
  owning its own concrete leaf class per the domain-first convention;
  see the "models location" note below for why this shared-base-class
  module, unlike a document type's own schema, is intentionally
  top-level rather than domain-local. See
  `.specmgr/feat/feat-29-dec-source-roles/README.md` for the full design.
- **`sop/`** (Standard Operating Procedure) — same tools/resources/prompts
  shape as `dec/` but for structured, step-by-step operational documents
  with a RASCI-style responsibility assignment and a closed
  approval/effectivity lifecycle (`create_sop`, `parse_sop`, `list_sop`,
  `get_sop`, `get_sop_example`, `get_sop_template`); `sop` is the **first
  domain built dispatch-only from day
  one** (ADR 36905d5b-8057-4294-8665-c7eed5534db0) — it has NO per-domain
  `update_sop`/`set_status_sop`/`set_classification_sop` tools at all, so
  whole-body
  and line-range updates go through the generic `update` tool in
  `general/tools/` (`type="sop"`), status changes through the generic
  `set_status` tool (`type="sop"`), classification changes through the
  generic `set_classification` tool (`type="sop"`), and deletions
  through the generic
  `delete` tool (`type="sop"`), and the `get_sop` tool takes
  `raw: bool = False` —
   `raw=True` returns the frontmatter-stripped body text as-is (the text
   `update`'s `offset`/`limit` index into), with optional read-style
   `offset`/`limit` windowing of that raw read (raw-only; out-of-range
   values clamp, never error); disk-free/id-free dry-run content
   validation through the generic `validate` tool (`type="sop"`) — the
   former `validate_sop` tool was removed in favor of it
   (feat-81-83-validation); `sop/resources/`
  (`specmgr://sop/schema`, `specmgr://sop/example`,
  `specmgr://sop/template`; no `specmgr://sop/{id}` — id-based reads
  are `get_sop`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://sop/list` — `list_sop` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now
  also carries `error_count` and reports a failed-to-parse document
  inline (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3); `sop/prompts/`
  (`create_sop`/`update_sop`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_sop` first checks
  `list_sop` for a near-duplicate SOP; both prompts include an explicit
  `specmgr://rasci` read-first step before `## Roles and Responsibilities`,
  and `update_sop` names the GENERIC `update`/`set_status` tools with
  `type="sop"`). Its schema lives at `sop/models/v1/`, inside the domain
  package, not top-level `models/`. An SOP is built on the generic
  `models/md` parser with the GOL/RSK/QA/DEC simple surface — no
  fine-grained mutation tools, no renderer: writes persist the
  caller's raw validated body byte-for-byte. `sop` relies on the
  cross-cutting `specmgr://rasci` resource (REQ-011, see `general/`
  below) for the generic RASCI role definitions used by its
  `## Roles and Responsibilities` section, not a domain-local one.
- **`feat/`** (Feature) — formalizes the ad hoc `.specmgr/feat/<id>/
  README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e) into a
  real, schema-backed domain, and is the one domain in this codebase whose
  own addressing genuinely deviates from every other domain's precedent
  (ADR 8cf940c5-3100-485c-a12d-14b59b631712): `id` is a chosen
  `feat-NNN-slug` — the containing folder's own name, not a
  server-generated UUID — and documents live one-per-folder as
  `<base>/<id>/README.md` (a fixed filename), not flat files directly
  under the base directory. This bespoke, folder-per-document addressing
  is hand-rolled in `feat/tools/_paths.py` (ADR-style, like `adr/tools/
  _paths.py`), **not** built on the shared flat-file
  `general/tools/_doc_paths.py` every other whole-body domain uses;
  `SPECMGR_FEAT_DIR` overrides the base directory (mandatory-in-spirit
  test-isolation env var, same as every other domain's own equivalent).
   All 7 tools (`create_feat`, `set_feat_id`, `parse_feat`, `list_feat`,
   `get_feat`, `get_feat_example`, `get_feat_template`);
   `create_feat` accepts an optional, caller-chosen `id`
  (a full `feat-NNN-slug`, validated against that shape) and, when `id`
  is omitted, now defaults to `feat-0-<slug-from-title>` — not an
  auto-incrementing number — failing with `FileExistsError` before any
  write if the resulting id/folder already exists (whenever the content is valid); `set_feat_id(id,
  new_id)` is the one tool that renames an existing feature's id
  afterwards (e.g. once a GitHub issue number becomes known), atomically
  renaming `<base>/<id>/` to `<base>/<new_id>/` and rewriting the
  frontmatter `id`, leaving the body byte-identical, and returning the
  renamed document's frontmatter only (no body), consistent with the
  other write tools — a bespoke
  `feat`-only tool, distinct from the generic `update`/`set_status`
  dispatch tools below. Whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="feat"`), status
  changes through the generic `set_status` tool (`type="feat"`),
  classification changes through the generic `set_classification` tool
  (`type="feat"`), and
  deletions through the generic `delete` tool (`type="feat"`) — no
  `update_feat`/`set_status_feat`/`set_classification_feat` of its own — and the
   `get_feat` tool takes `raw: bool = False` — `raw=True` returns the
   frontmatter-stripped
   body text as-is (the text `update`'s `offset`/`limit` index into),
   with optional read-style `offset`/`limit` windowing of that raw read
   (raw-only; out-of-range values clamp, never error);
  disk-free/id-free dry-run content validation through the generic
  `validate` tool (`type="feat"`) — the former `validate_feat` tool was
  removed in favor of it (feat-81-83-validation);
  `feat/resources/` (`specmgr://feat/schema`, `specmgr://feat/example`,
  `specmgr://feat/template`; no `specmgr://feat/{id}` — id-based reads
  are `get_feat`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://feat/list` — `list_feat` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now
  also carries `error_count` and reports a failed-to-parse folder inline, with a resolved `path`
  (feat-81-83-validation Phase 4 retrofitted `FeatSummary`'s own `path` to
  match) rather than silently dropping it, feat-81-83-validation Phase 3);
  `feat/prompts/`
  (`create_feat`/`update_feat`, narrated instruction flows; `create_feat`
  first checks `list_feat` for a near-duplicate feature). Its schema
  lives at `feat/models/v1/`, inside the domain package, not top-level
  `models/`. `FeatSummary`'s own separate `path` field was removed in
  feat-81-83-validation Phase 4 -- it now inherits the same, resolved
  `path: str` field every other whole-body domain's summary also carries
  via the shared `DocSummary` base (feat-81-83-validation Phase 3/4), no
  longer a `feat`-only divergence. Unlike every other domain, though,
   `feat`'s own workflow -- direct hand/agent editing of
   `.specmgr/feat/<id>/README.md` -- treats this shared `path` as a
   first-class, sanctioned read/edit entry point by original design, not
    merely an incidental convenience every other domain only gained
    later. That direct-file-editing workflow must keep the generic
    `update` tool's coordinate mismatch in mind: a raw on-disk `.md`
    file's line numbers are never `update`'s `offset`/`limit` body-line
    coordinates (the YAML frontmatter block is variable-length), so the
    only safe source of coordinates is `get_feat(id, raw=True)`
    (optionally `numbered=True`), never a raw file read minus an assumed
    constant (feat-153-off-by-n, GitHub issue #153, ADR
    19ff316b-cd11-41a7-a616-ffd84917da51). See
   `.specmgr/feat/feat-31-feature/README.md` for the full
   design. `list_feat` is the one `list_<d>` tool backed by a two-stage
   dirty/clean `DocCache` instead of the generic `build_summaries` sweep
   every other domain uses (feat-187-list-feat-timeout, GitHub issue #187,
   ADR 3982712a-a46b-4b2b-809f-9c6925a49b44): its request path resolves
   every folder from one file read plus the clean (full-parse) cache's
   own parse-free `peek_preloaded` lookup, falling back on a miss to a
   second, feat-local "dirty" `DocCache` instance (`feat/tools/_cache.py`)
   whose own `parse_fn` is frontmatter-plus-H1 only (never a full body
   parse) -- so the very first `list_feat` call against a cold server
   process already returns the complete directory (`total` correct from
   call one) well under any client request timeout, closing the tool's
   own cold-scan timeout (348.6 s measured over this repo's corpus at one
   point) at the root. Each row follows a three-tier failure-visibility
   contract: a clean-stage success or failure is today's exact row
   (byte-identical to `get_feat`'s `ParseFailureResult.error`, by
   construction); a dirty-stage success is a *transiently* healthy row
   (correct `id`/`title`/`status`, but a body-level defect this file may
   have is not yet visible); a dirty-stage failure is either a tier-1
   malformed-frontmatter row (byte-identical to `get_feat` by
   construction, since both stages run the identical `parse_frontmatter`
   call) or a tier-2 missing/wrong-shape-H1 row (a dirty-stage-specific
   `error` text that converges to byte-identical only once a full parse
   has passed that file). This time-qualifies the `list_<d>`/`get_<d>`
   error byte-identity property (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c)
   for `feat` only -- `get_feat` remains the unconditional, full-fidelity
   authority throughout; every other domain's property is unchanged. A
   unified background daemon thread (`specmgr-startup-warmup`, spawned by
   `general.tools._startup_warmup.start_startup_warmup` from `server.py`'s
   lifespan hook) runs, in order, the `feat` frontmatter warmup phase, the
   `feat` full-parse warmup phase (both in `feat/tools/_warmup.py`'s
   `warmup_feat_caches()`, a plain, synchronously callable function the
   thread merely calls), and then the pre-existing, unchanged feat-134
   similarity warmup (`warmup_similarity_cache`) -- replacing the
   similarity-only `start_similarity_warmup` thread that previously ran
   alone, so at most one heavy, GIL-holding background phase runs at a
   time instead of two in parallel. A new presence flag,
   `SPECMGR_FEAT_WARMUP_DISABLED`, gates the two `feat` phases only (the
   pre-existing `SPECMGR_SIMILARITY_DISABLED` still gates the similarity
   phase only); when both flags are set, no thread starts at all (reported
   by `specmgr://config`'s own `feat_warmup_disabled` field, mirroring
   `SimilarityConfig.disabled`'s own precedent).
- **`vcr/`** (Verification Case Record) — same tools/resources/prompts
  shape as `req/`/`prb/`/`dec/` but for how a single REQ/UC is verified: a
  `## Verifies` single-value cross-reference (exactly one mandatory
  `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase, not a
  bullet list — a single-value field is structurally incapable of holding
  more than one reference), a `## Coverage` closed-vocabulary outcome
  signal (`full`/`partial`/`none`, mirroring RSK's `## Strategy` idiom),
  and a `## Acceptance Criteria` collection of `### AC-NNN (Method): ...`
  entries (3-digit zero-padded number, DEC-`Option`-style numbered H3, no
  per-AC mutation tools; `Method` is a closed **DTAIS** vocabulary —
  Demonstration, Test, Analysis, Inspection, Special — parsed from the
  heading itself via regex, RSK `Probability`/`Impact`-style; each entry
  optionally carries a free-form `description` paragraph and/or a
  `#### Test Steps` numbered procedure; a `model_validator` rejects
  duplicate `AC-NNN` numbers), plus optional `## More Information`/
   `## Updates` (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`,
   `get_vcr_example`, `get_vcr_template`); whole-body and line-range updates go through the
   generic `update` tool in `general/tools/` (`type="vcr"`), status
   changes through the generic `set_status` tool (`type="vcr"`),
   classification changes through the generic `set_classification` tool
   (`type="vcr"`), deletions through the generic `delete` tool
   (`type="vcr"`), and the
    `get_vcr` tool takes `raw: bool = False` — `raw=True` returns the
    frontmatter-stripped body text as-is (the text `update`'s
    `offset`/`limit` index into), with optional read-style `offset`/`limit`
    windowing of that raw read (raw-only; out-of-range values clamp, never
    error); disk-free/id-free dry-run content validation through the
    generic `validate` tool (`type="vcr"`) — the former `validate_vcr`
    tool was removed in favor of it (feat-81-83-validation);
    `vcr/resources/` (`specmgr://vcr/schema`,
  `specmgr://vcr/example`, `specmgr://vcr/template`; no
  `specmgr://vcr/{id}` — id-based reads are `get_vcr`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://vcr/list` —
  `list_vcr` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now also
  carries `error_count` and reports a failed-to-parse document inline
  (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3);
  `vcr/prompts/`
  (`create_vcr`/`update_vcr`). Its schema lives at `vcr/models/v1/`,
  inside the domain package, not top-level `models/`. The closed DTAIS
  method vocabulary its `## Acceptance Criteria` depends on is documented
  by the cross-cutting `specmgr://dtais` resource, which lives in
  `general/resources/`, not `vcr/resources/`, since it is domain-knowledge
  other document types may also want to reference (mirroring RSK's
  `specmgr://rsk/tara` shape). See `.specmgr/feat/feat-33-vcr/README.md`
  for the full design.
- **`sysrs/`** (System Requirements Specification) — an aggregator document
  type that ties together already-existing specmgr artifacts (`gol`, `prb`,
  `qa`, `uc`, `req`, `rsk`, `dec`/`adr`, `vcr`) into one coherent, navigable
  specification via per-section, type-tagged cross-reference lists (bullets
  shaped `<TYPE> <uuid>: <title>` plus an optional per-bullet notes
  paraphrase, mirroring VCR's `_VERIFIES_PATTERN` precedent) rather than
  duplicating their content — e.g. `### Goals` accepts only `GOL` bullets,
  `## Decisions` accepts `DEC` or `ADR`, and the nine `## Requirements` H3s
  plus the six `## Other Characteristics` H3s each accept only `REQ`.
   `sysrs` is, like `sop`/`vcr`, built dispatch-only from day one (ADR
   36905d5b-8057-4294-8665-c7eed5534db0) — no per-domain `update_sysrs`/
   `set_status_sysrs`/`validate_sysrs` tools of its own; whole-body and
   line-range updates go
   through the generic `update` tool in `general/tools/` (`type="sysrs"`),
   status changes through the generic `set_status` tool (`type="sysrs"`),
   classification changes through the generic `set_classification` tool
   (`type="sysrs"`), deletions through the generic `delete` tool
   (`type="sysrs"`), and disk-free/id-free dry-run content validation
   through the generic `validate` tool (`type="sysrs"`) — the former
   `validate_sysrs` tool was removed in favor of it
   (feat-81-83-validation). 6 tools (`create_sysrs`, `parse_sysrs`, `list_sysrs`,
   `get_sysrs`, `get_sysrs_example`, `get_sysrs_template`);
   the `get_sysrs` tool takes `raw: bool = False` — `raw=True` returns the
  frontmatter-stripped body text as-is (the text `update`'s `offset`/`limit`
  index into), with optional read-style `offset`/`limit` windowing of that
  raw read (raw-only; out-of-range values clamp, never error). 3 resources
  in `sysrs/resources/` (`specmgr://sysrs/schema`, `specmgr://sysrs/example`,
  `specmgr://sysrs/template`; no `specmgr://sysrs/{id}` — id-based reads are
  `get_sysrs`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://sysrs/list` — `list_sysrs` ships as a paged tool from day one,
  ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, whose `PagedResult` now also
  carries `error_count` and reports a failed-to-parse document inline
  (with a resolved `path`) rather than silently dropping it,
  feat-81-83-validation Phase 3).
  2 prompts in `sysrs/prompts/`
  (`create_sysrs`/`update_sysrs` — `create_sysrs` first checks `list_sysrs`
  for a near-duplicate and reads the existing cross-cutting
  `specmgr://iso25010` resource for the nine canonical ISO/IEC 25010:2023
  characteristic names used to group `## Requirements` (no new `general`
  resource is introduced); `update_sysrs` names the generic
  `update`/`set_status` tools with `type="sysrs"`). Its schema lives at
  `sysrs/models/v1/`, inside the domain package, not top-level `models/`.
  See `.specmgr/feat/feat-32-sysrs/README.md` for the full design.
  - **`general/`** — cross-cutting, non-domain-specific package:
    `general/tools/` (`mdformat`, formats a markdown file in place while
    preserving YAML frontmatter blocks; `update`, the generic whole-body
    *and* line-range replace for the whole-body domains — `type` is
    one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs, read-style
    `offset`/`limit` body-line coordinates (`offset` = 1-based first line,
    `limit` = count; omitted `limit` = through end of body, `0` = pure
    insert, `offset` `N+1` = append; strict validation, never clamped),
    `offset`/`limit` address the frontmatter-stripped body, never the raw
    on-disk `.md` file (the YAML frontmatter block is variable-length, so
    a raw file read's line numbers are never the same as body-line
    coordinates — the only safe source of coordinates is a
    `get_<d>(id, raw=True)` read, never a raw file read minus an assumed
    constant), and a success return of `UpdateResult` — `frontmatter`
    (the updated frontmatter only, no body) plus `snippet`, `None` in
    whole-body mode and, in range mode, the before/after window of the
    touched range (dropped lines numbered pre-splice, inserted lines
    numbered post-splice, up to 2 unchanged context lines per side),
    bounded by the touched range rather than the document size (the
    whole-body-equivalent `offset=1` + omitted-`limit` range returns
    `snippet=None` too; feat-153-off-by-n, GitHub issue #153, ADR
    19ff316b-cd11-41a7-a616-ffd84917da51),
    splice-then-validate-whole — and now with two non-raising failure
    channels (feat-170-update-edit-parse-failure, GitHub issue #170, ADR
    b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, case 4 of the ADR 519d1206
    non-raising-structured-result chain): on a target id whose only
    matching on-disk file fails to parse it returns the non-raising
    `ParseFailureResult` (`error`/`path`/`id`, the same parse defect as
    the domain's `list_<d>` failed row for the same file) instead of
    raising the domain's not-found error (a truly-absent id still
    raises), and a content-validation failure on the submitted new
    content (or, in range mode, on the spliced result) returns the
    non-raising `ValidateResult` (`valid=False`, single
    `errors[].message` capped at 300 chars exactly as the generic
    `validate` tool caps it, feat-110) instead of raising
    `AssertionError`/`pydantic.ValidationError` — `edit` (below) gains
    the same two channels for the post-edit result, and
    `set_status`/`set_classification` (below) gain the
    `ParseFailureResult` channel too — while every caller-usage
    `ValueError` (invalid id shape, unknown `type`, range-coordinate
    misuse, `edit`'s pre-dispatch OC-parity guards and stage-1 match
    guards, `set_status`'s `superseded_by` misuse) still raises — with
    the one sub-case where `update`/`set_classification`'s `type="adr"`
    (a well-formed UUID id, so it passes the id-shape validation) raises
    the plain `KeyError` from the dispatch-table lookup instead (a
    direct-Python-caller outcome only, unreachable through the server's
    12-value `type` enum) — `set_status`'s out-of-vocabulary
    `InvalidStatusResult` (case 2 of the same chain, ADR
    b399f1ce-ed42-4929-b01c-7a57d18e8014) still runs pre-lock/pre-load
    (first), and nothing is written in any failure case; a fifth extension
    of the same chain (feat-204-create-error, GitHub issue #204, ADR
    f14f125e-eaad-4f4f-a6fd-3c931bed726e) gives every `create_<d>` tool (the
    12 whole-body domains) the non-raising `ValidateResult` for a
    content-validation failure of the caller-submitted body (nothing
    written), and every `parse_<d>` tool the same for an existing-but-broken
    file — `parse_<d>`'s `OSError`-family file-access errors from
    `Path.read_text()` and every caller-usage `ValueError`/`FileExistsError`
    (incl. `create_feat`'s guards, whose execution order relative to content
    validation is unchanged: a compound failure returns `ValidateResult`
    first, "first-in-execution-order wins") still raise;
    `_CAUGHT_EXCEPTIONS`/`_MAX_VALIDATE_ERROR_CHARS` are defined in
    `general/models/validate_result.py` and re-exported by
    `general/tools/validate.py` (their one source of truth); `edit`, the
    generic surgical exact-match
    string replacement of an existing document's frontmatter-stripped body
    across the whole-body domains (`type` is one of
    req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; `adr` excluded —
    unlike `update`/`delete`/`set_classification`, an explicit pre-dispatch
    `ValueError` for an unknown or `adr` `type`, following the generic
    `validate` tool's precedent): `old_str` must match the on-disk body
    byte-exactly (no line-ending normalization), must be unique unless
    `replace_all`, then the *edited* body must still validate as a whole
    document — written to disk only if both stages pass, nothing written on
    any failure (the file stays byte-unchanged; an empty `new_str` is a
    pure deletion, legal iff the edited body validates); returns the
    updated frontmatter only (`updated` bumped), with an invalid `id` a
    `ValueError` before any file access (feat-159-edit, GitHub issue #159);
    `set_status`, the generic status change for
    every
    domain incl. adr — `superseded_by` is ADR-only, composing
    `"superseded by X"`; `set_classification`, the generic free-text
    `classification` frontmatter field change for the whole-body
    domains only — `type` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs
    (`adr` excluded, same as `update`/`delete`, since ADR's separate
    `AdrFrontmatter` model is out of scope), bumping `updated` and leaving
    the body and every other frontmatter field untouched, with a
    blank/whitespace-only value clearing `classification` back to
    `None`/absent; `delete`, the generic type-dispatched hard-delete
    for the whole-body domains — `type` is one of
    req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs (`adr` excluded), every one of these
    domains implements a `delete` adapter in that one tool (a future domain
    adds its own adapter there, never a per-domain `delete_<d>` tool),
    resolving by `id`, taking the domain's own lock, and returning the
    deleted path; `validate`, the generic, disk-free/id-free dry-run
    content validator for the same whole-body domains (`adr`
    excluded, `validate_adr` remains its own standalone tool) —
    replacing the former per-domain `validate_<d>` tools
    (feat-81-83-validation, ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6);
    it is the one generic tool here whose entire surface is non-raising
    structured results: it never raises for a
    content-validation failure, always returning
    `{valid: bool, errors: list[{message: str}]}`, only raising
    `ValueError` for a `full`/content-shape mismatch or an unsupported
    `type` (the four generic mutation tools' non-raising branches, above,
    cover content-validation and existing-document-parse-failure only —
    their caller-usage `ValueError`s still raise); `find_related`, the generic cross-domain semantic-similarity
    search for the documents most related to an existing document, given
    its `type`/`id`, across every whole-body domain (`adr` excluded
    structurally), ranked by cosine similarity of local sentence
    embeddings (the `similarity` extra, `fastembed`/`bge-small`),
    excluding the source document itself; `find_similar_text`, the same
    ranking for a free-form `query` text (the pre-creation
    dedup/discovery companion of `find_related`). Both return up to
    `top_k` (default 10, validated 1..100) ranked `{type, id, title,
    status, path, score}` hit rows (an unparseable candidate appears with
    `id = null` and the `<failed to parse>` marker title/status), and
    both return the structured, non-raising `{available: false, reason,
    message}` result whenever the embedding feature is unavailable
    (`SPECMGR_SIMILARITY_DISABLED` present, or the backend/model fails to
    load) — the tools always register; availability is decided at call
    time (feat-134-related-artifact-similarity, ADR
    750842b2-aca4-4649-ba0c-855ec8e1f505). `list_references`, the generic,
    cross-domain cross-reference listing tool (feat-144-ref-artifact,
    GitHub issue #144) — takes a *source* document's `type` (one of
    adr/req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) + `id`,
    regex-scans the source's frontmatter-stripped body for `<TYPE>
    <id>` references (the reference-tag vocabulary
    GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS/FEAT; case-insensitive tag,
    space/tab/dash separator, anywhere in a line; the UUID tags
    carry a canonical uuid id, while FEAT carries the full
    `feat-NNN-slug` id or the bare `feat-NNN` number), dedupes repeated
    occurrences (first-occurrence order), resolves each unique
    reference in its target domain (cache-backed; ADR excluded from
    the cache), and returns a paged `PagedResult[ReferenceRow]` — one
    row per unique reference carrying `type`/`id`/`title` (the
    referenced document's H1)/`path` (resolved absolute file path); a
    reference that cannot be resolved on disk is a row with null
    `title`/`path` and the target domain's not-found message in
    `error` — it never raises; `max_results`/`offset` paging with the
    same clamp-not-error contract as every `list_*` tool (default 25,
    cap 100). It applies the same `_path_safety` guards: an invalid
    source `type`/`id` (path-injection attempt or wrong-format id) is
    a `ValueError` before any filesystem access, and a missing source
    raises the source domain's not-found error, identical to `get_<d>`.
    The OpenCode-native counterparts are the `ref-finder` subagent
    (`.opencode/agent/ref-finder.md`), the `/refs <type> <id>` command
    (`.opencode/command/refs.md`, `agent: ref-finder`), and the
    self-triggering `specmgr-refs` OpenCode Skill
    (`.opencode/skills/specmgr-refs/SKILL.md`, feat-152, GitHub issue
    #152) that routes single-document requests to `list_references`
    and codifies the graph/batch/reverse workflows.
    On a successful write, `set_status` (its non-`adr`
    adapters), `set_classification`, and every per-domain
    `create_<d>` tool return the domain's frontmatter object only (no
    body) — small and bounded regardless of document size, unlike an
    append-only document's ever-growing body — with the `adr` dispatch
    branch of `set_status` and every ADR-specific tool (`create_adr`,
    `update_frontmatter`, `update_section`, the `option_*` tools) excluded,
    still returning the full document with `body` intact
    (feat-69-update-context); `update` is the deliberate exception to that
    frontmatter-only precedent — since feat-153-off-by-n (GitHub issue
    #153, ADR 19ff316b-cd11-41a7-a616-ffd84917da51) it returns the
    `UpdateResult` wrapper instead: the same per-domain frontmatter object
    under `frontmatter`, plus `snippet`, which is `None` in whole-body mode
    and, in range mode, the before/after window of the touched range
    (bounded by the touched range rather than the document size), so the
    "small and bounded" property now holds for the snippet via that
    bounded-by-touched-range contract. `general/resources/`
    (`specmgr://version` — the package version plus the installed
    `fastembed` version (or `null` when the `similarity` extra is missing,
    feat-134 Phase 7), `specmgr://config` — every domain's resolved base
    directory plus whether its `SPECMGR_*_DIR` env var is set, and since
    feat-134 Phase 7 a static `similarity` section
    (`extra_installed`/`disabled`/`model_name`/`cache_dir`), plus since
    feat-185-uc-diagrams Phase 120 a static `plantuml` section
    (`jar`/`bin`/`url` each presence-only `{set: bool}` + `selected` —
    the first-set-wins source per rulebook §3.2, `"none"` when all unset;
    never a value of the three `SPECMGR_PLANTUML_*` vars),
    `specmgr://ears` — the EARS requirement-phrasing templates (feat-92),
    `specmgr://iso25010` — the ISO/IEC 25010:2023
    quality model, `specmgr://dtais` — the DTAIS verification-method
    vocabulary VCR's `## Acceptance Criteria` depends on, kept here rather
    than under `vcr/resources/` since it is domain-knowledge other document
    types may also want to reference, and `specmgr://rasci` — the generic
    RASCI responsibility-assignment framework, REQ-011; motivated by `sop`
      but not scoped to it), and `general/prompts/` (`compact_history` — rotates
      older `Recent Updates` entries out of any feature folder's `README.md`
      into a sibling `history.md`; `repair` (feat-150-mcp-lifecycle-commands,
      GitHub issue #150, Phase 1) — cross-cutting, takes `type` (one of the
      whole-body domains; ADR is explicitly out of scope — it is not a
      whole-body domain and has no generic dry-run `validate` tooling) plus an
      optional `id`, and narrates the host-native repair loop for a document
      that fails to parse: discover it via `get_<d>(id)`'s non-raising
      `ParseFailureResult`-shaped result (with an `id` — the result carries
      `error`, the parse-failure message, byte-identical to
      `list_<d>()`'s failed-row `error` for the same file (identical field
      path and cause, including the trailing pydantic documentation line —
      feat-162-doc-cache-exception-footer, GitHub issue #162), plus `path`, the
      absolute on-disk file; a truly absent id still raises the domain's
      not-found error;
      ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) or `list_<d>()`'s `<failed
      to parse>` failed row (without one), read the raw file with the host's
      own file-read tool
      (no specmgr MCP tool can return the raw content of a document that fails
      to parse, and the generic `update` (or `edit`) tool is structurally unable to repair
      one — its per-domain adapters re-parse the existing document before it
      can write anything and, for a broken one, return the non-raising
      `ParseFailureResult` instead of writing or raising (a truly-absent id
      still raises the domain's not-found error)),
      fix only what the enriched error addresses while preserving the
      frontmatter `id`/`created`/`status`/`version` byte-for-byte and leaving
      `updated` untouched (a repair is not an edit), loop the generic
      `validate` tool with `full=True` over the full raw text until green,
      write the repaired text back to the same path via the host's own
      file-write tool — never via `update` (or `edit`) — and then confirm the repair
      against the file as it now exists on disk with one more real
      `get_<d>(id)`/`list_<d>()` call, degrading to diagnose-only (report the
      error and the proposed fix, touch nothing) on a host without file
      read/write tools; the OpenCode-native counterparts are the
      `doc-repairer` subagent (`.opencode/agent/doc-repairer.md`), the
      `/repair <type> [id]` command (`.opencode/command/repair.md`,
      `agent: doc-repairer`), and the self-triggering `repair` OpenCode Skill
      (`.opencode/skill/repair/SKILL.md`, REQ-012) that defers to
       `doc-repairer` via the `task` tool when available). Every `get_<d>` tool for the whole-body
     domains additionally
     takes a `raw: bool = False` parameter — `raw=True` returns the
     frontmatter-stripped body text as-is (the text `update`'s
     `offset`/`limit` index into), with optional read-style `offset`/`limit`
     windowing of that raw read (raw-only; out-of-range values clamp, never
     error) and an optional `numbered: bool = False` parameter
     (feat-153-off-by-n, GitHub issue #153, ADR
     19ff316b-cd11-41a7-a616-ffd84917da51; raw-only — combining `numbered`
     with `raw=False` raises `ValueError`, like `offset`/`limit`) — when
     `numbered=True`, every returned body line is prefixed with its 1-based
     absolute body-line number in the `"<n>: "` form (plain decimal, no
     padding); windowed reads number from the clamped offset and never
     restart at 1 within a window, so a number seen in the output can be fed
     straight back into `update`'s `offset`; `numbered=False` output stays
     byte-identical to the plain `raw=True` text; and, per feat-150's
     precedent below, a numbered read of a document that exists but fails to
     parse still returns the `ParseFailureResult`, never numbered text.
     `get_<d>` for the 12 whole-body domains
    (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`;
    `get_adr` excluded) additionally returns a structured, non-raising
    `ParseFailureResult` (`general/models/parse_failure_result.py`;
    `error`/`path`/`id`) for a document that exists but fails to parse,
    instead of raising the domain's not-found error — its `error` text
    is byte-identical to that domain's `list_<d>` failed-row
    `error` for the same file (identical field path and cause, including the trailing
    pydantic documentation line —
    feat-162-doc-cache-exception-footer, GitHub issue #162), and `raw=True` on a broken document still
    returns the result (never a raw `str`); a healthy document's shape and every other outcome
    are unchanged (feat-150-mcp-lifecycle-commands Phase 1a, ADR
    9080b37c-82b3-4f63-81f1-79641d0bf14c — the third extension of the
    ADR 519d1206 client-side-`isError`-truncation workaround chain after
    `validate` and `set_status`'s invalid-status case). `get_<d>` (every
    domain, incl. `get_adr`), `update`, and
   `set_status` apply the same `general/tools/_path_safety` guards `delete`
   already had (feat-38-39-41-43-44 Phase 4, extending feat-36-delete, ADR
   1af6787b-eaab-4e8f-888f-531c1e76c19d): validate `id` for path-injection/
   wrong-format before any filesystem access, and confine the resolved path
   to the domain's own base directory after resolution — `_path_safety`'s
   UUID-shaped domains now include `adr`; `delete` itself is unchanged.

**Models location — a real, intentional divergence, not an oversight**:
the rule is domain-first — every document type keeps its schema inside
its own domain package (`<domain>/models/vN/`); building a new document
type requires no edit to this paragraph. The single exception is ADR:
its schema (`AdrFrontmatter`, `AdrBody`, `AdrOption`, `Adr`, `parse_adr`,
`render_adr`) stays under the shared top-level `models/adr/` package
because it predates the domain-first refactor and has no dependency on
`mcp`/`tools`/`resources`/`prompts`. Top-level `models/` therefore holds
`adr/` (the exception) plus only shared cross-domain modules —
`iso25010.py`, `md/` (markdown-section building blocks), and
`version_info.py` — don't assume any other doc type's schema lives there.
A third, non-model top-level package also exists: **`plantuml/`**
(feat-185-uc-diagrams Phase 110, ADR
7a626b12-b189-4561-a51d-ffb2e9e193b4) — the cross-cutting, **import-free**
(no `biz.dfch.specmgr.*` imports anywhere in it; the dependency direction
is always specmgr-domain → `plantuml`, never the reverse — e.g.
`uc/models/v2/renderer.py` imports the shared UNATTRIBUTED marker constant
from `plantuml/structure.py`) and **stdlib-only** (no new dependency or
extra) PlantUML support library: `encode.py` (the classic URL text
encoder — the `SoWkI…` form, rulebook §5.1), `structure.py` (the two-mode structure checker + the shared
marker constant), `backends.py` (jar/bin local backends, incl. the crash
detection on the raw byte stream), `url.py` (the single-endpoint `/svg/`
matrix classifier — the frozen §5.2 rows incl. the recognised
200+crash-page INVALID row (the known 1.2026.8 self-message/note-left shape
bug; amended 2026-10-06)), and `chain.py` (the strict first-set-wins,
no-fall-through validation chain over exactly three env vars + the
non-raising result model). It is deliberately extractable but not a separate
PyPI library, and nothing in it registers with the MCP server itself — the
wrapping diagram tools/resources live in the `uc` domain (see the `uc/`
bullet above, feat-185-uc-diagrams Phase 120).

`server.py`'s own module docstring is the single most authoritative,
currently-maintained list of every resource/tool/prompt this MCP server
registers — read it before consulting this file for specifics, and update
it whenever you add/remove/rename a resource, tool, or prompt.
`docs/MCP.md` is the auto-generated (via `specmgr mcp-docs`), user-facing
mirror of that same registration and must never be hand-edited.

Still genuinely missing / not yet done (don't assume otherwise):
- No `validate_adr` (or the generic `validate` tool, for the other
  whole-body domains) tool runs over the repo's
  own documents yet via pre-commit or CI. (ADR
  9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
  locally via pre-commit hook, not just CI")
- No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
  docstring already reserving a spot for it ("... and later `ac`") — the
  convention for adding it (or any future domain) is fixed by ADR
  36905d5b-8057-4294-8665-c7eed5534db0, refined by ADR
  c4efbde6-fd19-4aa8-8668-95316ed62dcc: first register the domain's name
  in `general/tools/_domains.py`'s `WHOLE_BODY_DOMAINS` once (in canonical
  position), then one dispatch entry to each of the two generic tools in
   `general/tools/` (`update`'s `type`, `set_status`'s `type`), one `delete`
   adapter in the generic `delete` tool, one `edit` adapter in the generic
   `edit` tool, plus a `raw` parameter on the new
  `get_<d>` tool — not new `update_<d>`/`set_status_<d>`/`delete_<d>` tools.

`feat-27-validation` (closed 2026-09-01, GitHub issue #27, subsuming feat-7's
Task 0.29) made every `parse_<d>`/`create_<d>`/`validate_<d>` tool's and the
generic `update`/`set_status` tools' `AssertionError`/`pydantic.ValidationError`/
`yaml.YAMLError` messages actionable: each now carries a document-relative
field path, a 1-based line reference into the mdformat-normalized body, and a
cause/fix hint (e.g. a bare `<word>` token parsed as raw HTML, or a `+`/`-`/`*`-
prefixed line starting a stray CommonMark list), with domain + tool + channel
context prepended by the shared `models/md/_errors.wrap_tool_errors` wrapper —
same exception types throughout, messages only (no new exception types).

`feat-99-list-item` (GitHub issue #99) added
`MarkdownListItem.single_line_text(self, *, expected: str) -> str`
(`models/md/markdown_list_item.py`): a shared guard that rejects a
soft-wrapped (CommonMark lazy-continuation) list item with an actionable
`AssertionError` (field path, 1-based line, an explicit "soft-wrapped/
lazy-continuation list items are not supported" cause, and a "join onto
one physical line" fix hint), called before a domain's own marker/pattern
regex ever runs against `.text`. Wired into every structurally-checked
`MarkdownListItem` subclass found across every `models/md` whole-body
domain: `tsk.TaskItem.checked`/`.description`, `feat.RequirementItem.
description` (`feat.AcceptanceCriterionItem.criterion_description` and
`feat.FeatTaskItem.task_description` are covered transitively via
`TaskItem.description`, no direct wiring needed),
`rsk.ThresholdItem.low`/`.high`/`.zone`, and `rsk.StrategyItem.strategy`.
Free-form list items (e.g. `req`'s `## Tags`) and anything whose own regex
already uses `re.DOTALL` (e.g. `rsk.QuadrantItem`/`MitigationItem`/
`StatusItem`) are unaffected and must not call this guard — see
`.specmgr/conventions.md`'s "Markdown Authoring (List Items Must Not
Soft-Wrap)" section for the full authoring/implementation convention.

`feat-107-doc-cache` (GitHub issue #107) added a process-local,
per-domain, content-hash-validated in-memory read cache
(`general/tools/_doc_cache.py`'s `DocCache` class, one module-level
singleton per domain in each domain's own `tools/_cache.py`, mirroring the
existing per-domain `threading.Lock` registries in `_lock.py`) for every
generic whole-body domain (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`,
`dec`, `sop`, `feat`, `vcr`, `sysrs`), eliminating the redundant
markdown-it/Pydantic re-parsing cost `get_*`/`list_*` previously paid on
every single call against an unchanged file — the real fix for the
CPU-bound, GIL-holding bottleneck behind issue #107's reported timeouts
(the MCP SDK already thread-pools every sync tool call via
`anyio.to_thread.run_sync`, so a second thread pool would not have
helped). Wired into each domain's `read_<domain>`, `find_<domain>_path`'s
scan (via `general.tools._doc_paths.find_doc_path_by_id`'s `read_fn`/
`reconcile_fn` parameters), `list_<domain>`'s reconcile-on-scan, write-path
cache warming (`create_<domain>`, and the generic `update`/`set_status`/
`set_classification` tools), and cache invalidation (the generic `delete`
tool) — plus `feat`'s own bespoke integration (`feat/tools/_cache.py`,
since its hand-rolled `_paths.py`/`set_feat_id` never route through
`general.tools._doc_paths`), including `set_feat_id`'s cache-entry move
from the old path to the new one, hooked in only after `write_feat_file`
succeeds. ADR (`models/adr/v1`) is explicitly, permanently excluded from
this cache mechanism, since it is expected to be phased out later and does
not justify its own independently-implemented cache module — see ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d for the full rationale. That ADR
refines, not replaces, ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's
"filesystem is the sole source of truth" invariant: every cache access
re-validates the file's current content hash before deciding whether to
skip re-parsing, so a stale entry is structurally impossible — it can only
ever cost one extra parse, never an incorrect result.

`feat-187-list-feat-timeout` (GitHub issue #187) fixed `list_feat`'s
cold-scan timeout (ADR 3982712a-a46b-4b2b-809f-9c6925a49b44) by adding two
additive, generic `DocCache` primitives in `general/tools/_doc_cache.py`
— `peek_preloaded(path, text)` (a valid stored result, document or
cacheable failure, or `None`, never parses, materializing like `read`'s
own hit branch) and `read_preloaded(path, text, parse_fn)` (hit/miss
semantics identical to `read`, just handed already-read `text`) — with
`read` itself refactored onto `read_preloaded` (behavior-preserving; the
pre-existing `test__doc_cache.py` suite, including the feat-162 footer
tests, needed no changes). Both primitives exist so a caller holding two
`DocCache` instances for the same domain (`feat`'s clean/dirty pair, see
the `feat/` bullet above) can resolve one file read against both stages
without a second, independent re-read of the same file — the same
single-read, TOCTOU-safe discipline `read` itself already established
(feat-107-doc-cache Phase 6, REQ-007), extended rather than re-derived.
The pre-existing feat-134 similarity warmup's own startup thread/gate
(`general.tools._similarity_search.start_similarity_warmup`) was retired
in the same feature: `general.tools._startup_warmup.start_startup_warmup`
is the new, single entry point `server.py`'s `_lifespan` calls, spawning
one daemon thread (`specmgr-startup-warmup`) that runs the `feat`
frontmatter phase, the `feat` full-parse phase, and then the unchanged
`warmup_similarity_cache()` body, in that order — `warmup_similarity_cache`
itself (its own availability-probe-first/crash-containment/never-raising
body, and the demand path it shares the cache with) is otherwise
unchanged; only the startup orchestration moved.

Don't assume any domain package exists beyond the
per-domain bullets in the Status section above (each with its respective
`tools`/`prompts`/`resources` sub-packages, per the exceptions noted
there), or anything in `general/resources/` beyond the `general/` package
bullet's own enumeration above — check first.

## Project Shape

- **Type**: Python library + optional CLI + optional MCP server, in one repo
- **Namespace**: `biz.dfch.specmgr` in `src/biz/dfch/specmgr/` — `biz`/`biz/dfch`
  are implicit namespace packages (no `__init__.py` in those two dirs; only the
  leaf `specmgr/` has one)
- **Package manager**: `uv` (not pip) — lockfile is committed, use `--frozen`
- **Python**: `requires-python = ">=3.11"` (3.11–3.13 tested in CI); local dev
  defaults to 3.13 via `.python-version` — two separate settings, keep in
  sync intentionally, not by accident

## Development Artifacts (`.specmgr/`)

Per ADR e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development
artifacts in `.specmgr` with feature-driven work units"), development
planning/progress artifacts live under `.specmgr/`, separate from published
documentation in `docs/`:

```
.specmgr/
└── feat/
    └── feat-NNN-slug/              # One folder per GitHub issue
        ├── README.md               # Feature plan + progress (mandatory)
        └── history.md              # Archived older "Recent Updates" entries (optional)
```

- **Naming convention**: `feat-NNN-slug`, where `NNN` is the GitHub issue
  number. Work started without an issue yet uses `feat-0-slug` (issue number
  `0`) until/unless an issue is later opened for it.
- **Single `README.md` per feature** combines the plan (requirements,
  acceptance criteria, scope, dependencies, design notes) and progress
  (current status, blockers, recent updates, decisions made) — there is no
  separate `progress.md`; status lives inline on each task line, edited in
  place rather than duplicated.
- **Template**: The canonical feature template/example is the packaged
  data behind the `get_feat_template` / `get_feat_example` MCP tools
  (`src/biz/dfch/specmgr/feat/data/`). There is no hand-copied
  `_template` file — copy the tools' output when starting a new
  feature folder. See feat-93 for the consolidation.
- **Frontmatter**: every feature `README.md` starts with a minimal YAML
  frontmatter block — `id` (the `feat-NNN-slug` folder name itself, not a
  generated UUID), `version` (semver, starts at `1.0.0`), `status`
  (`planning` | `progress` | `review` | `done`), and `created`/`updated`
  (full ISO 8601 date+time — `yyyy-MM-dd` + `T` or space + `HH:mm:ss.SSS` +
  `Z`/`±HH:mm`; the MCP writes the `T`-separated canonical form and both
  separators are accepted on read, ADR
  8c889262-152b-4b8e-ae2c-75371f7a9edf; `updated` bumped on every
  substantive edit). There is no
  separate `GitHub Issue` field/body-line: the issue number is the `NNN`
  infix already embedded in `id`/the folder name (`feat-NNN-slug`) — `0`
  means no issue yet — so it is never duplicated elsewhere in the file. See
  ADR e369ee2e-3353-4f92-991c-6367d76d832e's Option 1 for the full
  rationale.
- **`doc/` has been migrated** into this structure — development planning docs
   now live in `.specmgr/feat/` with their respective feature folders.
- **No CI/pre-commit enforcement** exists for `.specmgr/` content — unlike
  `docs/adr/`, there is no `validate_adr`-equivalent check and no `adr-toc`-
  equivalent generation step wired into hooks or CI for feature folders.
- **No live citations of feature-folder sibling files**: a feature folder may
  contain other local files beyond `README.md`/optional `history.md`
  (session transcripts, reference copies, templates, etc.), but nothing in
  `src/`, `tests/`, or `AGENTS.md` may cite them by path — anything needing
  a stable, live citation from code must be a proper specmgr artifact
  (normally its own ADR).
- **ADR vs. feature-level "Decisions Made" log**: a decision belongs in a
  full ADR (`docs/adr/`) if it's architecture/structure-level, affects more
  than one feature or the repo as a whole, or reverses/supersedes a previous
  ADR. It belongs in the feature's own "Decisions Made" log instead if it's
  scoped entirely to that feature's implementation details. When in doubt,
  write the ADR.
- Existing feature folders: do not enumerate them here — the list grows
  constantly and any copy kept in this file immediately drifts out of date.
  Use the `list_feat` MCP tool (or browse `.specmgr/feat/` directly) to see
  the current, authoritative set.

## Developer Commands

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen pre-commit install                                     # one-time: enable pre-commit hooks
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen vulture src/ whitelist.py --min-confidence 60          # dead-code check (enforced)
uv run --frozen pytest -n auto --cov=src --cov-report=                # tests (parallel, pytest-xdist)
scripts/release.sh help                                            # staged release automation (SOP 98537416; README "Make a Release")
uv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md
uv run --frozen specmgr adr-toc                                        # regenerate docs/adr/README.md (ADR table of contents)
uv run --frozen specmgr unused-code                                    # report unused code in src/ (same check as the vulture hook)
uv run --frozen specmgr unused-code --test                             # report symbols only referenced from tests/, never src/
uv run --frozen specmgr version                                        # run the CLI
```

### Using a different Python version

The project defaults to Python 3.13 (see `.python-version`). To use a different version (e.g., 3.12), add `--python X.Y` to **both** `uv sync` and `uv run` commands, and include `--all-extras` on the `uv run` call:

```bash
uv sync --all-extras --frozen --python 3.12
uv run --frozen --all-extras --python 3.12 specmgr docs
```

Without `--all-extras` on `uv run`, only base dependencies are installed, causing `ModuleNotFoundError` for CLI/MCP extras like `typer`.

`pylint` only sees files tracked by git (`git ls-files`) — new files must be
`git add`ed before it will lint them, both locally and in CI.

`pre-commit install` is one-time per clone (see `.pre-commit-config.yaml`):
runs `ruff format`/`ruff check`, `vulture`, a local `specmgr docs` hook
(scoped to `src/**/*.py` changes), a local `specmgr adr-toc` hook (scoped to
`docs/adr/**/*.md` changes), and the other doc/schema drift checks, then the
full test suite (scoped to `src/**/*.py`/`tests/**/*.py` changes, run via
`pytest`/`pytest-xdist` in parallel, `-n auto`) and `specmgr coverage-badge`
last, before every commit, so a broken test or drift in
`docs/api/`/`docs/GENERATED.md`/`docs/adr/README.md` gets caught locally
instead of failing later in CI. The `pytest` hook is deliberately ordered
last (not right after `vulture`) so every faster check fails fast first;
running the suite in parallel also cut its own wall time from 9-11 minutes
(serial `coverage run -m unittest discover`) to roughly a minute measured on
the primary dev machine. `specmgr coverage-badge` must stay immediately
after it, since it reads the `.coverage` data `pytest-cov` just produced.
(ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
locally via pre-commit hook, not just CI") If a commit is blocked by a dangling
or stale `INSTALL_PYTHON` pointer in the shared `.git/hooks/pre-commit` (e.g. it
points at a deleted worktree venv and the hook aborts with `` `pre-commit` not
found ``), treat this as a true error and stop — do not attempt auto-repair from
within a worktree; ask the user to re-run `uv run --frozen pre-commit install`
in the main repo (`~/src/biz.dfch.SpecMgr`, the `dev` branch) to restore the
canonical pointer.

## Extras split (base library has no CLI/MCP deps)

`dependencies` in `pyproject.toml` is only `pydantic` + `python-dotenv`, so the
library is usable standalone. `typer`/`rich` live in the `cli` extra, `mcp` in
the `mcp` extra, and `fastembed` (the local sentence-embedding backend behind
`general/tools/find_related`/`find_similar_text`) in the `similarity` extra —
opt-in on top of `mcp`, not bundled with it, so installing `mcp` alone never
pulls in the embedding model/backend. **Never** import `cli.py` or
`server.py` from `src/biz/dfch/specmgr/__init__.py` — that would force those
extras onto every consumer of the base library.

## CLI (`cli.py`)

- Typer app, entry point `specmgr` (`pyproject.toml` `[project.scripts]`);
  `python -m biz.dfch.specmgr` (`__main__.py`) runs the same Typer `app()`.
- **Gotcha**: with only one `@app.command()` registered, Typer collapses to a
  single top-level command and drops subcommand dispatch (`specmgr version`
  would fail with "unexpected extra argument"). An explicit `@app.callback()`
  (see `_callback` in `cli.py`) forces Typer to keep treating it as a command
  group — keep that callback even after a second command is added, don't
  assume it becomes dead code to remove.
- `specmgr diagram uc [ids|all] --out <dir> [--check]` (feat-185-uc-diagrams
  Phase 130, `commands/diagram.py` — the one Typer sub-command group,
  registered via `app.add_typer`): writes the deterministic per-UC usecase
  diagrams (`<id>.usecase.puml`) + the multi-UC `package.puml` over exactly
  the invoked UCs (default `--out` = CWD-relative `diagrams/uc/`, rulebook
  §2.10); `all` renders every UC in `list_uc` order (incl. `Subfunction`
  level — the §2.11 judgment is agent-path only) and skips existing-but-
  broken documents (their references take the package's deterministic note);
  `--check` regenerates in memory and byte-diffs usecase + package only
  (missing files count as differing, no writes). **Deterministic-only — it
  never creates, overwrites, reads, or diffs `<id>.sequence.puml`**
  (agent-owned), and written artifacts carry no structure-only header.
  Thin over the Phase 120 `get_use_case_package_diagram` resolution
  (lazy import — needs the `mcp` extra; missing extra ⇒ exit 1) + the pure
  Phase 110 renderers. Exit codes: **0** written / no diff, **1** diff found
  (`--check`) / missing `mcp` extra, **2** usage-or-render error (wrong-
  format id before any file access, an explicitly requested id missing on
  disk or existing-but-broken — the parse error is reported, a render
  failure, `all` combined with ids).
- `specmgr plantuml-check <path...>` (feat-185-uc-diagrams Phase 130,
  `commands/plantuml_check.py`): validates any `.puml` file(s) — agent-
  owned sequence files included, no specmgr document needed — through the
  strict chain (`plantuml.chain.validate_plantuml` over the file text); per
  file it prints the verdict (`checked_by`/`valid`/`rendered`/`source_
  state`) + every finding as `{path}:{line}: {message} (fix: {fix_hint})`.
  Exit codes (worst applicable wins, severity **2 > 3 > 1 > 0**): **0** all
  valid at the highest available layer (incl. the all-unset structure-only
  floor), **1** any structure-red or source-invalid, **2** selected source
  misconfigured/unavailable (chain hard failure) or a usage error (non-
  `.puml` / unreadable / missing path — all reported before any chain run),
  **3** inconclusive (persistent after the chain's one retry; also the URL
  matrix's undetermined request/encode-error rows — never INVALID).
- `specmgr plantuml-encode <path|->` (feat-185-uc-diagrams Phase 130,
  `commands/plantuml_encode.py`): prints the classic `SoWkI…`-form URL
  encoding (`plantuml.encode.encode_puml` — the `{enc}` payload of
  `GET {base}/svg/{enc}`; no base URL is taken, so the encoding itself is
  printed) of a file's or stdin's (`-`) diagram source; fully offline.
  Exit codes: **0** printed, **2** usage error (missing/unreadable file,
  empty input).

## MCP server (`server.py`)

- Builds the `MCPServer` instance (`mcp` object) and a no-op `_lifespan`,
  then imports every domain package (`adr`, `dec`, `feat`, `general`,
  `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `tsk`, `uc`, `vcr`) as its last line purely
  for the side effect of
  running their `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` decorators.
  When adding a new domain, add its import to that same last line —
  forgetting it means the new tools/resources/prompts silently never
  register.
- **`specmgr mcp`** (`commands/mcp.py`) *does* start the server —
  `mcp_server.run(transport="stdio")` by default, or
  `mcp_server.run(transport="sse", host=..., port=...)` via
  `--transport sse`/`-t sse`. `python -m biz.dfch.specmgr mcp` and
  `uvx --from "biz-dfch-specmgr[mcp]" specmgr mcp` both work identically
  (see `README.md`'s "Add to OpenCode" section) — don't assume the server
  has no working entry point.

## CI / Release

- Branches: `dev` (default, feature work) → `main` (stable) → tag.
- `.github/workflows/ci.yml`: ruff + pylint (`|| true`) + vulture + unittest
  run on matrix 3.11/3.12/3.13 via `uv sync --frozen --all-extras` (unit
  tests run via `pytest`/`pytest-xdist`, `-n auto`, not raw `unittest`), but
  `specmgr docs` and `specmgr adr-toc` drift checks run **only on Python
  3.13** (pinned, since different Python versions generate different
  docstring formatting in the API docs, and we want consistent ADR TOC
  generation).
- `.github/workflows/publish.yml` exists and has shipped `v0.1.0`, `v0.2.0`,
  `v0.2.1` to PyPI/the MCP Registry, triggered on `v*` tags.
- Version bumps: update `version` in `pyproject.toml` (single source) and
  move `CHANGELOG.md`'s `[Unreleased]` into a dated section, same commit.
- Don't block on `gh pr checks --watch` for CI results -- duration is
  variable across the 3.11/3.12/3.13 matrix and can exceed a single
  tool-call timeout. Poll instead: call `gh pr checks <pr-number>`
  (without `--watch`) repeatedly, optionally `sleep 30 &&` before each
  call, until every check reports a final state.

## Coding Standards

See `.specmgr/conventions.md` for detailed coding requirements and conventions:
- Python version and type notation
- Assert statement guidelines
- Variable naming (use `result` for return values)
- Comparison constants
- Mandatory type hints
- Documentation requirements for classes, attributes, and functions

- Formatter/linter: `ruff` (enforced, not black), line length 120.
- `pylint` is advisory fallback only (see pylint caveat above).

## Generated Documentation

See [`docs/GENERATED.md`](docs/GENERATED.md), auto-generated by `specmgr
docs` (implemented-domain list, per-module docstrings, and test-file count).
This pointer is permanent and hand-written — it is never regex-spliced or
otherwise auto-edited; only `docs/GENERATED.md` itself is regenerated.
