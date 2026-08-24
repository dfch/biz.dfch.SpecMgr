---
id: feat-15-add-artifact-type-risk
version: 1.0.0
status: planning
created: 2026-08-24
updated: 2026-08-24
---

# Feature: Add artifact type Risk (rsk)

## Plan

### Overview

Add a new markdown artifact type, `Risk` (abbreviation `rsk`), for maintaining risk
registers in system specifications. Every risk decomposes its scenario into
separate `## Cause`, `## Trigger`, and `## Consequence` sections, carries a 5x5
probability/impact assessment BEFORE mitigation (`## Initial Assessment`) and
the same 5x5 assessment AFTER mitigation (`## Residual Assessment`), a TARA
response strategy (`## Strategy`: transfer / accept / reduce / avoid), and the
treatment measures bridging the two (`## Mitigation`), scoped to the affected
system(s) (`## Scope`). `rsk` follows the domain-first hierarchy and MCP
surface already established by `req`/`tsk` (ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/resources shape
almost exactly (per GitHub issue #15).

### Requirements

- [ ] REQ-001: Define the `rsk` markdown schema — frontmatter (`type="rsk"`,
  6-value status set: `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`,
  default `open`) and body (H1 title, optional leading comment, mandatory
  `## Cause`, mandatory `## Trigger`, mandatory `## Consequence`, mandatory
  `## Scope` list (>=1 affected system/component), mandatory `## Initial
  Assessment` (5x5: H3 headings `### Probability {1..5}` / `### Impact
  {1..5}`, value in the heading, derived level), mandatory `## Strategy`
  (TARA 4-value closed set: `transfer`/`accept`/`reduce`/
  `avoid`), mandatory `## Mitigation`, mandatory `## Residual Assessment`
  (5x5, same shape as initial), optional `## Owner`, optional `## Tags`
  list, optional `## More Information`)
- [ ] REQ-002: Pydantic models for `rsk` documents (`rsk/models/v1/` —
  domain-first path, mirroring `tsk/models/v1/` and `req/models/v1/`)
- [ ] REQ-003: Parse and validate `rsk` documents from markdown
  (`parse_rsk`, mirroring `parse_tsk`/`parse_req`)
- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface plus the
  feat-13 listing contract: `parse_rsk`, `get_rsk_example`,
  `get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`,
  `delete_rsk` (stub), `validate_rsk`, `get_rsk`, and the paged `list_rsk`
  tool (`max_results`/`offset`, `PagedResult[RskSummary]`, skip-and-
  continue on unparseable files — mirroring `tsk/tools/list_tsk.py` and
  feat-13's shared paging contract)
- [ ] REQ-005: MCP resources: `specmgr://rsk/example`, `/schema`,
  `/template` (no `/list` — listing is the paged `list_rsk` tool per
  feat-13 / ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), plus two new static
  domain-knowledge resources: `specmgr://rsk/tara` (what TARA is, the four
  valid strategy words, when and how to apply each) and
  `specmgr://rsk/risk-matrix` (the 5x5 matrix: scale anchors, zone table,
  product thresholds — what 'high risk' and 'low risk' mean)
- [ ] REQ-006: MCP prompts — `create_risk`, `update_risk` (narrated tool
  sequences, mirroring `req/prompts/create_req.py`/`update_req.py` and
  `tsk/prompts/create_task.py`/`update_task.py`)
- [ ] REQ-007: Packaged example/template/schema data plus the two
  domain-knowledge documents (`rsk/data/`: `rsk_example.md`,
  `rsk_template.md`, `rsk_schema.json`, `rsk_tara.md`,
  `rsk_risk_matrix.md`) via the existing generic
  `general/tools/_packaged_data.py`, with the matching `pyproject.toml`
  package-data entry, pre-commit hook, and CI step
- [ ] REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema`
  (new `rsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept
  drift-free via pre-commit/CI

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/rsk_schema.json`,
  `specmgr://rsk/schema`), reference `rsk` document (`rsk_reference.md`)
  round-trips through the parser (`test_parses_full_reference_document`),
  including both 5x5 assessments (probability/impact bounded 1..5, derived
  level zone correct)
- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required/optional
  fields correctly, including the `Assessment` probability/impact/derived-level
  split, the TARA closed set, `Scope` (>=1) and the `Tags`/`Owner`/
  `More Information` absent-vs-present cases (`tests/rsk/models/v1/`)
- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree;
  malformed input raises (structural `AssertionError` / field-level
  `pydantic.ValidationError`, matching `req`/`tsk`'s error-channel convention)
  — `tests/rsk/models/v1/test_parser.py`
- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and
  registered (confirmed present in regenerated `docs/MCP.md`), with
  `create_rsk`/`update_rsk` validating body-only content the same way
  `create_req`/`update_req`/`create_tsk`/`update_tsk` do, and `list_rsk`
  returning one-line `RskSummary` entries that include the residual-risk
  fields (`residual_probability`/`residual_impact`/`residual_product`)
  with correct paging/clamping per the feat-13 contract
- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and
  registered (confirmed present in regenerated `docs/MCP.md`), with
  `specmgr://rsk/tara` documenting exactly the four valid TARA words and
  `specmgr://rsk/risk-matrix`'s zone table matching the model's
  derived-`level` mapping (threshold test)
- [ ] ACC-006: Verifies REQ-006 — `create_risk`/`update_risk` prompts narrate
  the correct tool sequence (`tests/rsk/prompts/`)
- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
  real, non-editable install, mirroring `req`'s (feat-6 Task 5.1) and `tsk`'s
  (feat-10 ACC-007) own verification
- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation

### Scope

**Included in this feature:**

- Specification of the `rsk` markdown schema (frontmatter + body), including
  the cause/trigger/consequence scenario split, the 5x5 initial/residual
  assessment, the TARA strategy set, and the before/after-mitigation
  structure
- Pydantic models, parser, and schema generation under `rsk/models/v1/`
- Full MCP surface (tools/resources/prompts/packaged data) mirroring
  `req`/`tsk`, including the feat-13 paged `list_rsk` tool and the two new
  domain-knowledge resources (`specmgr://rsk/tara`,
  `specmgr://rsk/risk-matrix`)
- Tests mirroring `tests/req/`'s and `tests/tsk/`'s layout and coverage

**Explicitly out of scope:**

- Aggregated, register-wide views (e.g. a combined risk-matrix chart across
  all `rsk` documents) — `RskSummary` (one line of the paged `list_rsk`
  tool) carries `initial_level`/`residual_level`/`strategy` plus the
  residual-risk coordinates per document precisely so such a view can be
  built later without reading each document
- Cross-referencing/linking `rsk` documents to other artifact types
  (REQ/UC/ADR) — not part of this feature
- Risk relationships (dependency, correlation, common-cause analysis)
- A `specmgr rsk-toc`-equivalent generation command or its own CI/pre-commit
  drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`
  already provide generically

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (id-based reads as a tool, not a resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 + the feat-13 paging machinery
  (`general/tools/_paging.py`, `general/models/summary.py::DocSummary`,
  `PagedResult`), `general/tools/_doc_paths.py` and `_packaged_data.py`,
  the existing `models/md` engine — in particular
  `MarkdownSection1WithComment`, `MarkdownSection2`, `MarkdownSection3`,
  the generic `list[MarkdownStr]` engine (`process_list_field`), and the
  regex `@alias` heading-constraint mechanism (`AliasType.REGEX` +
  `match_alias`'s `re.fullmatch`; precedents: `tsk`'s free-form `### `
  `UpdateEntry`, ADR's numbered `### Option N:` headings)
- Blocks: None identified yet

### Design Notes

- **Body shape** — `Risk` (the body's H1 class) subclasses the existing
  `MarkdownSection1WithComment` mixin (`models/md/`), reusing it as-is (no
  new mixin needed):

  ```
  # {H1 title}
  <!-- optional leading comment -->            comment: MarkdownComment | None

  ## Cause                                     cause: MarkdownStr  (mandatory)
  {Why the risk exists — the root condition}

  ## Trigger                                   trigger: MarkdownStr  (mandatory)
  {What sets the risk event in motion}

  ## Consequence                                consequence: MarkdownStr  (mandatory)
  {What happens if the risk event occurs}

  ## Scope                                     scope: list[MarkdownStr]  (>=1)
  - {Affected system / component}
  - {Another affected system / component}

  ## Initial Assessment                        initial_assessment: Assessment
  ### Probability {1..5}                       probability: leaf H3 (value in heading)
  ### Impact {1..5}                            impact: leaf H3 (value in heading)

  ## Strategy                                  strategy: str  (TARA closed 4-value set)
  {transfer | accept | reduce | avoid}

  ## Mitigation                                mitigation: MarkdownStr  (mandatory)
  {Treatment measures; "none" if strategy is accept}

  ## Residual Assessment                       residual_assessment: Assessment
  ### Probability {1..5}                       probability: leaf H3 (value in heading)
  ### Impact {1..5}                            impact: leaf H3 (value in heading)

  ## Owner                                     owner: MarkdownStr | None
  {Responsible person / role}

  ## Tags                                      tags: list[MarkdownStr] | None
  - {tag}

  ## More Information                          more_information: MarkdownStr | None
  {Free-form}
  ```

  Order is enforced by the model: title -> optional comment -> Cause ->
  Trigger -> Consequence -> Scope -> Initial Assessment -> Strategy ->
  Mitigation -> Residual Assessment -> optional Owner -> optional Tags ->
  optional More Information. The scenario sections (Cause/Trigger/
  Consequence) lead the document; the before/after pair (Initial Assessment
  ... Residual Assessment) is separated by exactly the sections that explain
  the delta: `Strategy` (chosen TARA response) and `Mitigation` (the
  measures taken).

- **Assessment structure (initial/residual)** — each assessment is one cell
  of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;
  1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...
  5 = severe), carried by exactly two leaf H3 sections under the H2
  heading, with the value *in the heading itself*:

  ```
  ## Initial Assessment
  ### Probability 4
  ### Impact 3
  ```

  Each H3 is a `MarkdownSection3` leaf with a regex `@alias` —
  `^Probability [1-5]$` / `^Impact [1-5]$` — enforced by `match_alias`
  (`re.fullmatch`) at parse time: the engine's first-class
  heading-constraint mechanism (same family as `tsk`'s free-form `### `
  `UpdateEntry` and ADR's numbered `### Option N:` headings). The range is
  baked into the regex itself, so `### Probability 6`, `### Probability`
  (missing value), and `### Impact` before `### Probability` (wrong order)
  all fail the parse eagerly — no `TaskItem`-style lazy-computed-field gap
  and no custom list-item marker parsing (the parser is MarkdownIt
  commonmark without a GFM plugin, which is exactly why `tsk` needed its
  `TaskItem` workaround for checkboxes — not needed here). The heading
  text is retained by the engine (`_value`/`.text`), so each leaf exposes
  the digit as a computed `value: int`; the H2 `Assessment` derives the
  zone `level` from the product of the two values (probability x impact):

  | p \ i | 1      | 2      | 3      | 4        | 5         |
  |-------|--------|--------|--------|----------|-----------|
  | 5     | medium | high   | high   | very high| very high |
  | 4     | low    | medium | high   | high     | very high |
  | 3     | low    | medium | medium | high     | very high |
  | 2     | low    | low    | medium | medium   | high      |
  | 1     | low    | low    | low    | low      | medium    |

  Zone thresholds on the product: 1-4 `low`, 5-9 `medium`, 10-14 `high`,
  15-25 `very high`.

  **Worked example** (risk: untrusted file uploads parsed by an unmaintained
  parser library, affecting the document-processing subsystem):

  ```
  ## Cause
  The parser library has no security updates since 2021.

  ## Trigger
  An uploaded file exploits a known format flaw.

  ## Consequence
  Remote code execution in the document-processing subsystem; other
  subsystems unaffected (isolated network zone).

  ## Scope
  - document-processing subsystem

  ## Initial Assessment
  ### Probability 4
  ### Impact 3

  ## Strategy
  reduce

  ## Mitigation
  Replace the parser with a maintained library; restrict uploads to a
  format whitelist.

  ## Residual Assessment
  ### Probability 2
  ### Impact 3
  ```

  Initial cell 4 x 3 = 12 -> `high`; residual cell 2 x 3 = 6 -> `medium`:
  the mitigation moved the risk one zone down. That before/after pair is the
  register's audit trail — a sensible `reduce` strategy must show
  residual < initial (the example's annotations are for readability only;
  the document stores the two H3 heading values, and `level` is always
  computed, never written).

- **No eager-validation `model_validator` needed for `Assessment`** —
  unlike `tsk.Task`'s `_validate_items_eagerly` (which exists because a
  `TaskItem`'s checkbox marker is free text the commonmark parser accepts,
  so a malformed marker only surfaces when a lazy computed field is
  accessed), a malformed `Assessment` heading (`### Probability 6`,
  `### Probability`, wrong order) fails at parse time via the `match_alias`
  assertion in `MarkdownSection.from_text` — and every tool path parses
  (there is no direct-construction path), so there is no
  silent-construction gap. The implementer must not blindly copy `tsk`'s
  workaround (user-approved decision, 2026-08-24).

- **Strategy (TARA)** — `## Strategy` is a single-line H2 section whose
  content is validated against the closed 4-value set `transfer`/`accept`/
  `reduce`/`avoid` — the TARA framework's risk-response strategies
  (Transfer, Accept, Reduce, Avoid; cf.
  https://www.consuunt.com/tara-framework/) — same narrowing approach
  `ReqFrontmatter` applies to its `status` field, at body-section level.
  Mandatory: every risk in a register has a disposition. Only the four valid
  TARA words are accepted; anything else (e.g. the TARRA-era words
  `tolerate`/`assign`/`recover`) is a validation error.

- **Frontmatter status** — `open`/`mitigating`/`accepted`/`occurred`/
  `closed`/`dropped`, default `open`: a purpose-fit risk lifecycle (user-
  selected 2026-08-24) rather than reusing REQ's 7-value ADR-like set —
  `open` = identified and monitored; `mitigating` = treatment in progress;
  `accepted` = residual risk formally accepted; `occurred` = the risk event
  materialized (tracked as incident); `closed` = resolved/expired; `dropped`
  = removed from the register (not a real risk, duplicate, or out of scope).

- **List summary** — `RskSummary` (one line of the paged `list_rsk` tool's
  output — no `specmgr://rsk/list` resource, per feat-13) carries
  `id`/`title`/`status`/`ref` plus `initial_level`, `residual_level`,
  `strategy`, the first `scope` entry, and the residual-risk coordinates
  `residual_probability`, `residual_impact`, and `residual_product` (the
  risk product, probability x impact — the matrix coordinate that
  determines the residual zone), so a register-wide risk-matrix view can
  be built from the listing alone.

- **Domain-knowledge resources** — `specmgr://rsk/tara` and
  `specmgr://rsk/risk-matrix` are static packaged markdown documents,
  served as raw text (`text/markdown`, mirroring
  `specmgr://tsk/example`/`/template`) rather than parsed into structured
  models — the audience is an LLM agent that needs to read guidance, not
  code that needs data (`specmgr://iso25010`'s structured parse is the
  precedent for machine-readable reference data; these are prose). Content
  is drafted in Phase 1 from this plan's Design Notes, so the TARA words
  and the zone table have a single source of truth:
  - `rsk_tara.md` — what TARA is (Transfer, Accept, Reduce, Avoid), the
    four valid `## Strategy` words verbatim (exactly the model's closed
    set), when and how to apply each (low probability / high impact ->
    transfer; high / high -> avoid; high probability / low impact ->
    reduce; low / low -> accept), and how the strategy interacts with
    `## Mitigation` and the frontmatter `status` vocabulary
  - `rsk_risk_matrix.md` — the probability/impact scale anchors (1 = rare
    ... 5 = almost certain; 1 = negligible ... 5 = severe), the 5x5 zone
    table, the product thresholds (1-4 low, 5-9 medium, 10-14 high,
    15-25 very high) — i.e. what 'high risk' and 'low risk' mean — and the
    initial/residual reading rule (a `reduce` strategy implies
    residual < initial)
  A test guards the documented zone thresholds against the model's
  derived-`level` mapping (ACC-005).

- **Prompt naming** — `create_risk`/`update_risk` follow the
  `tsk`-prompt precedent of the issue's literal wording (issue #15 names
  both), not the `rsk`-prefixed convention the tools/resources use.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a
  tool (get_rsk), not a resource

No new ADR is anticipated for this feature — the `Assessment` 5x5 parsing
approach, the TARA closed set, and the 6-value status set are scoped enough
to log only in this file's own Decisions Made, not a full ADR.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

**Execution approach** (confirmed 2026-08-24, see Decisions Made): the
Orchestrator/Phase-Implementer pattern. Each phase below is delegated to the
`phase-implementer` subagent as one unit, which implements the phase end to
end (code, its own mirrored tests, the phase-end quality gate — full
`unittest` suite + ruff format/check + vulture — and this plan's Progress
section update), then stops and reports. After every phase, the orchestrator
verifies the results independently (re-runs the quality gate, reviews the
phase diff, checks the evidence against the phase's tasks) but changes
nothing: a failing verification re-delegates the phase to `phase-implementer`
with the findings, it is not patched by the orchestrator. One Conventional
Commit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with
`phase-implementer` replacing the `implementation-specialist` that feature
used. Before Phase 1, the current plan state is committed on its own as
`docs(feat-15): plan risk (RSK) artifact type feature` (the `feat-10`
precedent, `5985a1d`), so that each phase's commit contains only that
phase's changes.

#### Phase 1: Specification (commit 1)

- [ ] Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` —
  `RskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["rsk"]`,
  6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/
  `dropped`) — depends on: none — status: not-started
- [ ] Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`,
  `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with
  `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/
  `mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;
  `Assessment` (new `MarkdownSection2`: two mandatory leaf-H3 children
  `Probability`/`Impact`, each a `MarkdownSection3` with regex `@alias`
  `^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced
  eagerly by `match_alias` at parse time; computed `value: int` per leaf;
  derived `level` computed field on `Assessment` from the product zones) —
  depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: Create a reference `rsk` document (`rsk_reference.md`)
  exercising every field (cause/trigger/consequence, full initial +
  residual 5x5 pair, all mandatory and optional sections), used as the
  parser's round-trip test fixture — depends on: Task 1.2 — status:
  not-started (placed at
  `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md`, mirroring
  `tsk_reference.md`'s own location convention, not `rsk/data/`)
- [ ] Task 1.4: `tests/rsk/models/v1/test_frontmatter.py`,
  `test_body.py`/`test_assessment.py` — structural + validation tests
  mirroring `tests/tsk/models/v1/`: status set, 5x5 heading-value bounds
  (`### Probability 0`/`6` rejected) and derived-level zones (all four zone
  boundaries: 4/5, 9/10, 14/15), missing heading value and wrong H3-order
  rejection, TARA closed   set, `Scope` >=1, `Tags`/`Owner`/`More
  Information` absent-vs-present —
  depends on: Task 1.3 — status: not-started
- [ ] Task 1.5: Draft the two packaged domain-knowledge documents
  (`rsk_tara.md`, `rsk_risk_matrix.md`) from this plan's Design Notes —
  TARA: what/when/how for each of the four valid words, interaction with
  `## Mitigation`/`status`; risk matrix: scale anchors, zone table,
  product thresholds, initial/residual reading rule — placed in this
  feature folder until Phase 3 packages them into `rsk/data/` (mirroring
  the `rsk_reference.md` location convention) — depends on: Task 1.2 —
  status: not-started

#### Phase 2: Pydantic Models & Parser (commit 2)

- [ ] Task 2.1: `rsk/models/v1/document.py` (`RskDocument(frontmatter,
  body)`, mirroring `TskDocument`) — depends on: Task 1.3 — status:
  not-started
- [ ] Task 2.2: Implement `parse_rsk(text: str) -> RskDocument` (mirrors
  `parse_tsk`/`parse_req`) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary`, a subclass of
  `general/models/summary.py::DocSummary` mirroring `TskSummary`, with
  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the
  residual-risk coordinates `residual_probability`/`residual_impact`/
  `residual_product` (risk product), for the `list_rsk` tool) — depends on:
  Task 2.1 — status: not-started
- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/TSK's own Task 2.4
  audits) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.5: Draft `rsk_schema.json` via `generate_rsk_schema()`
  (mirroring `generate_req_schema`/`generate_tsk_schema` in
  `commands/schema.py`, calling `RskDocument.model_json_schema()`) +
  register `"rsk"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.6: `tests/rsk/models/v1/test_parser.py` — mirrors
  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,
  defaults-when-absent, invalid status, malformed structure, out-of-range
  or missing assessment heading value, invalid TARA word, missing Scope
  entry) — depends on: Task 2.2, Task 2.5 — status: not-started

#### Phase 3: MCP Surface (commit 3)

- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
  thin wrappers over `general/tools/_doc_paths.py` (mirrors
  `tsk/tools/_paths.py` etc. exactly; no new env-var/base-dir wiring needed
  — `doc_base_dir("rsk")` resolves to `{SPECMGR_DOCS_DIR or docs}/rsk`
  generically, verified) — depends on: Task 2.2 — status: not-started
- [ ] Task 3.2: `parse_rsk(path: str) -> RskDocument` tool wrapper
  (`rsk/tools/parse_rsk.py`, mirroring `tsk/tools/parse_tsk.py` — reads a
  filepath from disk, delegates to the model-layer `parse_rsk`) — depends
  on: Task 3.1 — status: not-started
- [ ] Task 3.3: `create_rsk(content: str) -> RskDocument` tool (body-only
  content, MCP builds frontmatter: `id`, `type="rsk"`, `status="open"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status:
  not-started
- [ ] Task 3.4: `update_rsk(id, content) -> RskDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.5: `set_status_rsk(id, status) -> RskDocument` tool (only path
  that changes `status`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.6: `delete_rsk(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: not-started
- [ ] Task 3.7: `validate_rsk(content, full=False) -> bool` tool — depends
  on: none — status: not-started
- [ ] Task 3.8: `get_rsk(id) -> RskDocument` tool (id-based single-document
  read; tool, not resource — per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614)
  — depends on: Task 3.1 — status: not-started
- [ ] Task 3.9: `get_rsk_example`/`get_rsk_template` tools + packaged data
  (`rsk/data/rsk_example.md`, `rsk/data/rsk_template.md`) via
  `general/tools/_packaged_data.py` — depends on: Task 1.3 — status:
  not-started
- [ ] Task 3.10: `specmgr://rsk/schema` resource (packaged
  `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`; no `/list`
  resource — listing is the `list_rsk` tool, Task 3.14) — depends on:
  Task 3.1, Task 2.5 — status: not-started
- [ ] Task 3.11: `specmgr://rsk/example` and `specmgr://rsk/template`
  resources — depends on: Task 3.9 — status: not-started
- [ ] Task 3.12: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.rsk` (`data/*.md`, `data/*.json`), pre-commit hook +
  CI step for the packaged `rsk_schema.json` copy (mirroring
  `specmgr-schema-tsk-package`) — depends on: Task 2.5 — status:
  not-started
- [ ] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — narrate
  the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)
  — depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10 — status: not-started
- [ ] Task 3.14: `rsk/tools/list_rsk.py` — the paged `list_rsk` tool
  (`max_results`/`offset` -> `PagedResult[RskSummary]`, mirroring
  `tsk/tools/list_tsk.py` + feat-13's shared paging contract, with the
  residual-risk fields from Task 2.3) — depends on: Tasks 3.1, 2.3 —
  status: not-started
- [ ] Task 3.15: `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix`
  resources (`rsk/resources/tara.py`, `rsk/resources/risk_matrix.py` — raw
  packaged markdown via `read_packaged_text`, mirroring
  `tsk/resources/tsk_example.py`) + packaged copies `rsk/data/
  rsk_tara.md`/`rsk_risk_matrix.md` from the Phase 1 drafts (Task 1.5) —
  depends on: Tasks 1.5, 3.1 — status: not-started
- [ ] Task 3.16: `tests/rsk/tools/test_list_rsk.py` (paging contract,
  clamping, skip-on-broken-file, residual fields present and correct) +
  `tests/rsk/resources/test_tara.py`/`test_risk_matrix.py` (registered,
  packaged content resolves from the source tree, `rsk_risk_matrix.md`'s
  documented zone thresholds match the model's derived-`level` mapping) —
  depends on: Tasks 3.14, 3.15 — status: not-started
- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers)
  AND update `server.py`'s module docstring (AGENTS.md: it is the
  authoritative, currently-maintained registration list) — the 5 resources
  (`specmgr://rsk/schema`, `/example`, `/template`, `/tara`,
  `/risk-matrix`), the 10 tools (`parse_rsk`, `get_rsk`, `list_rsk`,
  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,
  `set_status_rsk`, `delete_rsk` stub, `validate_rsk`), the 2 prompts
  (`create_risk`, `update_risk`), plus the "RSK has no
  `specmgr://rsk/{id}` resource" note in the docstring's existing
  per-domain pattern — depends on: Tasks 3.2-3.16 — status: not-started
- [ ] Task 3.18: `tests/rsk/tools/...`, `tests/rsk/resources/...`,
  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/
  resources/`/`tests/tsk/prompts/` layout (Task 3.16's tests live under the
  same tree) — depends on: Tasks 3.1-3.17 — status: not-started

#### Phase 4: Docs, CI wiring & final verification (commit 4)

- [ ] Task 4.1: `specmgr docs` regeneration (new `rsk` modules picked up) —
  depends on: Phase 1-3 complete — status: not-started
- [ ] Task 4.2: `specmgr mcp-docs` regeneration (new tools/resources/
  prompts appear in `docs/MCP.md`) — depends on: Phase 3 complete — status:
  not-started
- [ ] Task 4.3: CI wiring — confirm the Python-3.13-only `specmgr schema`/
  `specmgr docs`/`specmgr mcp-docs` steps in `.github/workflows/ci.yml`
  cover `rsk` with no separate per-type step needed (registry-driven,
  mirroring `req`/`tsk`'s own wiring) — depends on: Task 4.1, Task 4.2 —
  status: not-started
- [ ] Task 4.4: Final verification pass — walk every ACC-001..008 below and
  confirm each is actually satisfied; run the full quality gate (ruff
  format/check, pylint advisory, vulture, unittest, `specmgr docs`,
  `specmgr schema`, `specmgr mcp-docs` drift checks) once more end-to-end —
  depends on: Tasks 4.1-4.3 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder
created from `.specmgr/_template/v1/README.md`. Full schema and MCP surface
proposed (see Design Notes and Task List), mirroring `feat-10` (tsk)'s
4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead
of TARRA, cause/trigger/consequence split into separate sections,
assessment values moved from list items to H3 headings with regex `@alias`
constraints, execution pinned to the Orchestrator/Phase-Implementer
pattern, two domain-knowledge resources `specmgr://rsk/tara` +
`specmgr://rsk/risk-matrix` added, `list_rsk` summary lines carry the
residual-risk coordinates, and listing corrected to the paged `list_rsk`
tool per feat-13). Awaiting final review before Phase 1 starts.

### Blockers

None.

### Recent Updates

#### 2026-08-24T15:04:31+02:00 (newest)

- Completed: pre-implementation audit (user request) — verified
  non-gaps: `general/tools/_doc_paths.py` is fully generic (no
  env-var/base-dir task needed for `rsk`: `doc_base_dir("rsk")` ->
  `{SPECMGR_DOCS_DIR or docs}/rsk`), the packaged-data glob `data/*.md`
  already covers `rsk_tara.md`/`rsk_risk_matrix.md`, and the
  registry-driven `specmgr docs`/`mcp-docs`/`schema` CI steps cover `rsk`
  automatically. Fixes applied: Task 3.17 now includes the `server.py`
  module-docstring update (AGENTS.md mandates it as the authoritative
  registration list — 5 resources, 10 tools, 2 prompts, plus the "no
  `specmgr://rsk/{id}` resource" note); Task 2.3 states `RskSummary`
  subclasses `DocSummary` explicitly; Task 3.1 notes no base-dir wiring is
  needed; a Design Notes entry records that no eager-validation
  `model_validator` is needed for `Assessment` (parse-time `match_alias`
  suffices); the Execution approach records the baseline plan commit before
  Phase 1
- Next: baseline commit `docs(feat-15): plan risk (RSK) artifact type
  feature`, then HOLD — Phase 1 is deliberately not dispatched (user
  instruction 2026-08-24)
- Notes: see the two new Decisions Made entries below (user-approved)

#### 2026-08-24T14:09:54+02:00

- Completed: added two requirements per user feedback — (1) new static
  domain-knowledge resources `specmgr://rsk/tara` (what TARA is, the four
  valid words, when and how to apply each) and `specmgr://rsk/risk-matrix`
  (scale anchors, zone table, product thresholds — what 'high risk' and
  'low risk' mean), raw packaged markdown, content drafted in Phase 1
  (Task 1.5) from the plan's Design Notes with a threshold test against the
  model's derived-`level` mapping; (2) the `list_rsk` summary lines now
  carry the residual risk's `residual_probability`/`residual_impact`/
  `residual_product` (risk product). Also corrected the plan against
  feat-13 (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13): there is no
  `specmgr://rsk/list` resource — listing is the paged `list_rsk` tool
  (REQ-004/REQ-005, Task 2.3, new Tasks 3.14-3.16, old Tasks 3.14/3.15
  renumbered to 3.17/3.18). GitHub issue #15 updated to match
- Next: user review; then Phase 1 (Specification)
- Notes: see the two new Decisions Made entries below

#### 2026-08-24T13:40:33+02:00

- Completed: confirmed the execution approach with the user — the
  Orchestrator/Phase-Implementer pattern: `phase-implementer` subagent per
  phase (end to end: code, tests, phase-end quality gate, this plan's
  Progress section update, then stop and report); the orchestrator (main
  session) verifies each phase's results — independent quality-gate re-run
  + diff review — but changes nothing, re-delegating the phase to
  `phase-implementer` with the findings on failure; one Conventional Commit
  per verified phase. Execution approach, Decisions Made, and Current
  Status updated to pin this down
- Next: user review of the revised `Assessment` structure (H3 headings, see
  the 13:07:31 entry); then Phase 1 (Specification)
- Notes: no separate `phase-orchestrator` agent type is registered in this
  environment — the orchestrator role is fulfilled by the main session

#### 2026-08-24T13:07:31+02:00

- Completed: revised the `Assessment` structure per user proposal —
  probability/impact are no longer list items (`- Probability: N`) under
  the H2 but leaf H3 sections with the value in the heading
  (`### Probability 4` / `### Impact 3`), each a `MarkdownSection3` with a
  regex `@alias` (`^Probability [1-5]$` / `^Impact [1-5]$`) enforced by
  `match_alias` (`re.fullmatch`) at parse time. Rationale: the regex alias
  is the engine's first-class heading-constraint mechanism (same family as
  `tsk`'s `UpdateEntry`), enforces the heading word, the digit, and the
  1..5 range eagerly at parse time — replacing the planned `TaskItem`-style
  custom list-item leaf (a workaround for the parser's missing GFM
  list-marker support, with its own lazy-computed-field eager-validation
  history); confirmed against the engine source before adopting
- Next: user review; then Phase 1 (Specification)
- Notes: see the new Decisions Made entry below

#### 2026-08-24T11:55:11+02:00

- Completed: revised the plan per user feedback — (1) `## Strategy`
  corrected from the TARRA 5-value set to the TARA 4-value closed set
  `transfer`/`accept`/`reduce`/`avoid` (the valid TARA words, per the TARA
  framework, https://www.consuunt.com/tara-framework/); only those four
  words are accepted; (2) the single `## Description` section replaced by
  three separate mandatory H2 sections `## Cause`, `## Trigger`,
  `## Consequence`; (3) added a Design Notes entry explaining the
  initial/residual assessment structure (5x5 zone table with product
  thresholds) plus a worked example showing a `reduce` strategy moving the
  risk from `high` (4x3=12) to `medium` (2x3=6); GitHub issue #15's body
  updated to match
- Next: user review; then Phase 1 (Specification)
- Notes: see the two new Decisions Made entries below (supersede the
  earlier TARRA and single-`Description` decisions)

#### 2026-08-24T11:31:28+02:00

- Completed: opened GitHub issue #15 ("Add artifact type Risk"); created
  branch `feat-15-add-artifact-type-risk` from `dev`; drafted this feature
  plan (schema with 5x5 initial/residual assessment, strategy set,
  6-value status, scope/tags/owner/more-information) modeled on
  `feat-10-add-artifact-type-tasklist` — the first draft's strategy set and
  single-`Description` section were revised the same day (see the entry
  above and Decisions Made)
- Next: user review of the proposed attribute set (Design Notes); then
  Phase 1 (Specification)
- Notes: `Assessment` parsing reuses `tsk.TaskItem`'s custom-list-item-leaf +
  eager-validation precedent; no new ADR anticipated

### Decisions Made

- **2026-08-24**: Target GitHub issue #15, opened up front (no earlier issue
  describes this feature) — rationale: the `feat-NNN-slug` convention
  embeds the issue number; opening it first avoids the branch/folder rename
  pass `feat-10` did when its local branch predated its issue number.
- **2026-08-24**: Frontmatter `status` is the 6-value set `open`/
  `mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open` —
  rationale: user-selected (question, 2026-08-24); purpose-fit to a risk
  lifecycle rather than reusing REQ's 7-value ADR-like set or tsk's 4-value
  todo set.
- **2026-08-24**: Before/after mitigation is modeled as two separate
  `Assessment` sections (`## Initial Assessment` and `## Residual
  Assessment`), each 5x5 (probability 1..5, impact 1..5), with `## Strategy`
  and `## Mitigation` between them — rationale: user requirement for "a
  separate risk matrix impact/probability of 5x5 for BEFORE and AFTER
  mitigation (residual risk)"; the juxtaposition makes the mitigation
  effect directly auditable (a sensible `reduce` strategy shows
  residual < initial).
- **2026-08-24**: The derived risk `level` (`low`/`medium`/`high`/`very_
  high`) is a computed field from the probability x impact product zones
  (1-4 low, 5-9 medium, 10-14 high, 15-25 very high), never stored in the
  markdown — rationale: keeps the 5x5 mapping in one place and avoids stale
  derived values on round-trip, following `tsk.TaskItem.checked`'s
  computed-field convention.
- **2026-08-24** (superseded): `## Strategy` was initially proposed as the
  TARRA 5-value set `tolerate`/`assign`/`reduce`/`recover`/`avoid`, and the
  risk scenario was initially a single `## Description` section — superseded
  by the two decisions below.
- **2026-08-24**: `## Strategy` is the TARA 4-value closed set
  `transfer`/`accept`/`reduce`/`avoid` (Transfer, Accept, Reduce, Avoid —
  the TARA framework, https://www.consuunt.com/tara-framework/), mandatory,
  single-line validated; only those four valid TARA words are accepted —
  rationale: user correction with reference (the initially proposed "TARRA"
  set was the wrong acronym); same narrowing approach `ReqFrontmatter` uses
  for its `status` field.
- **2026-08-24**: The risk scenario is split into three separate mandatory
  H2 sections `## Cause` (root condition), `## Trigger` (what sets the event
  in motion), `## Consequence` (what happens if it occurs) — rationale:
  user requirement; each scenario aspect gets its own validated section
  instead of one mixed free-text blob, keeping cause/trigger/consequence
  mechanically checkable (all three present and non-blank).
- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected
  system/component); `## Owner`, `## Tags`, `## More Information` are
  optional — rationale: scope answers "which system is affected" and is
  central to a risk (user requirement); the remaining three follow ADR's
  optional `more_information` precedent and keep the schema lean.
- **2026-08-24**: `Assessment`'s probability/impact are leaf H3 sections
  with the value in the heading (`### Probability {1..5}`, `### Impact
  {1..5}`), each constrained by a regex `@alias` (`^Probability [1-5]$` /
  `^Impact [1-5]$`) and enforced eagerly by `match_alias` (`re.fullmatch`)
  at parse time — rationale: user proposal; this is the `models/md`
  engine's first-class heading-constraint mechanism (same family as `tsk`'s
  free-form-`### ` `UpdateEntry` and ADR's numbered `Option N:` headings),
  it validates the heading word, the digit, and the 1..5 range in one check
  at parse time, and it replaces the originally planned
  `- Probability: N` list-item leaf — a `TaskItem`-style workaround for
  the parser's missing GFM list-marker support, with its own
  lazy-computed-field eager-validation history (supersedes the
  assessment-shape detail of the earlier before/after-mitigation decision,
  which stands otherwise).
- **2026-08-24**: Execution follows the Orchestrator/Phase-Implementer
  pattern — each phase is delegated to the `phase-implementer` subagent
  (one phase end to end: code, tests, phase-end quality gate, this plan's
  Progress section update, then stop and report); after every phase the
  orchestrator verifies the results (independent quality-gate re-run + diff
  review) but changes nothing, re-delegating the phase with the findings on
  failure — rationale: user-stated intent (2026-08-24); the
  `phase-implementer` agent type is purpose-built for exactly this (one
  phase of a `.specmgr/feat/<id>/README.md` plan, driven by an orchestrator,
  not intended for direct selection), and no separate `phase-orchestrator`
  agent type is registered in this environment, so the orchestrator role is
  fulfilled by the main session. Replaces the `implementation-specialist`
  delegation named in the original Execution approach (the pattern
  `feat-10` used).
- **2026-08-24**: Two static domain-knowledge resources —
  `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` — are served as raw
  packaged markdown (`text/markdown`) rather than parsed into structured
  models — rationale: user requirement (the resources shall help the agent
  understand what TARA is, when and how to use it, and what 'high risk' /
  'low risk' means); the audience is an LLM agent reading guidance, which
  mirrors the `specmgr://tsk/example`/`/template` text resources, while
  `specmgr://iso25010`'s structured parse is the precedent for
  machine-readable reference data. Content is drafted in Phase 1 (Task 1.5)
  from this plan's Design Notes so the TARA words and the zone table have a
  single source of truth; a test guards the documented zone thresholds
  against the model's derived-`level` mapping.
- **2026-08-24**: `RskSummary` (one line of the paged `list_rsk` tool)
  carries the residual risk's `residual_probability`/`residual_impact`/
  `residual_product` in addition to `initial_level`/`residual_level`/
  `strategy`/first `scope` entry — rationale: user requirement ("impact,
  probability, risk product for the residual risk"); `residual_product`
  (probability x impact) is the matrix coordinate that determines the
  residual zone, so a register-wide risk-matrix view can be built from the
  listing alone.
- **2026-08-24**: Corrected REQ-005 against feat-13 — no
  `specmgr://rsk/list` resource; listing is the paged `list_rsk` tool
  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: MCP resources cannot take
  arbitrary parameters, and `max_results`/`offset` paging needs exactly
  that) — rationale: the plan originally mirrored feat-10's (pre-feat-13)
  resource list; verified against `tsk/tools/list_tsk.py` and
  `tsk/resources/` (no list resource) before correcting.
- **2026-08-24**: `Assessment` does *not* get a `tsk.Task`-style
  `_validate_items_eagerly` `model_validator` — rationale: a malformed
  assessment heading fails at parse time via the `match_alias` assertion in
  `MarkdownSection.from_text` (unlike `TaskItem`'s checkbox marker, which
  is free text the commonmark parser accepts), and every tool path parses,
  so there is no silent-construction gap (user-approved, 2026-08-24).
- **2026-08-24**: The current plan state is committed on its own as
  `docs(feat-15): plan risk (RSK) artifact type feature` before Phase 1 —
  rationale: `feat-10` precedent (`5985a1d`); keeps each phase's commit
  containing only that phase's changes (user-approved, 2026-08-24).

### Related PRs / Commits

No PR opened yet. Work happens on branch `feat-15-add-artifact-type-risk`
(from `dev`), one Conventional Commit per phase (see Execution approach).
