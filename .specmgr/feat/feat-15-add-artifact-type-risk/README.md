---
id: feat-15-add-artifact-type-risk
version: 1.0.0
status: planning
created: 2026-08-24
updated: 2026-08-25
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

   | p \ i | 1        | 2        | 3         | 4         | 5         |
   |-------|----------|----------|-----------|-----------|-----------|
   | 5     | medium   | high     | very high | very high | very high |
   | 4     | low      | medium   | high      | very high | very high |
   | 3     | low      | medium   | medium    | high      | very high |
   | 2     | low      | low      | medium    | medium    | high      |
   | 1     | low      | low      | low       | low       | medium    |

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

- [x] Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` —
  `RskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["rsk"]`,
  6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/
  `dropped`) — depends on: none — status: done
- [x] Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`,
  `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with
  `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/
  `mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;
  `Assessment` (new `MarkdownSection2`: two mandatory leaf-H3 children
  `Probability`/`Impact`, each a `MarkdownSection3` with regex `@alias`
  `^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced
  eagerly by `match_alias` at parse time; computed `value: int` per leaf;
  derived `level` computed field on `Assessment` from the product zones) —
  depends on: Task 1.1 — status: done
- [x] Task 1.3: Create a reference `rsk` document (`rsk_reference.md`)
  exercising every field (cause/trigger/consequence, full initial +
  residual 5x5 pair, all mandatory and optional sections), used as the
  parser's round-trip fixture — depends on: Task 1.2 — status:
  done (placed at
  `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md`, mirroring
  `tsk_reference.md`'s own location convention, not `rsk/data/`)
- [x] Task 1.4: `tests/rsk/models/v1/test_frontmatter.py`,
  `test_body.py`/`test_assessment.py` — structural + validation tests
  mirroring `tests/tsk/models/v1/`: status set, 5x5 heading-value bounds
  (`### Probability 0`/`6` rejected) and derived-level zones (all four zone
  boundaries: 4/5, 9/10, 14/15), missing heading value and wrong H3-order
  rejection, TARA closed   set, `Scope` >=1, `Tags`/`Owner`/`More
  Information` absent-vs-present —
  depends on: Task 1.3 — status: done
- [x] Task 1.5: Draft the two packaged domain-knowledge documents
  (`rsk_tara.md`, `rsk_risk_matrix.md`) from this plan's Design Notes —
  TARA: what/when/how for each of the four valid words, interaction with
  `## Mitigation`/`status`; risk matrix: scale anchors, zone table,
  product thresholds, initial/residual reading rule — placed in this
  feature folder until Phase 3 packages them into `rsk/data/` (mirroring
  the `rsk_reference.md` location convention) — depends on: Task 1.2 —
  status: done

#### Phase 2: Pydantic Models & Parser (commit 2)

- [x] Task 2.1: `rsk/models/v1/document.py` (`RskDocument(frontmatter,
  body)`, mirroring `TskDocument`) — depends on: Task 1.3 — status: done
- [x] Task 2.2: Implement `parse_rsk(text: str) -> RskDocument` (mirrors
  `parse_tsk`/`parse_req`) — depends on: Task 2.1 — status: done
- [x] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary`, a subclass of
  `general/models/summary.py::DocSummary` mirroring `TskSummary`, with
  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the
  residual-risk coordinates `residual_probability`/`residual_impact`/
  `residual_product` (risk product), for the `list_rsk` tool — carried by
  a `from_document(document, ref)` classmethod factory that derives every
  risk-specific field from the parsed assessments' computed
  `level`/`value` fields) — depends on: Task 2.1 — status: done
- [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/TSK's own Task 2.4
  audits — audited, no gaps found: Phase 1's body/assessment fields and
  the new `RskSummary` fields carry descriptions; `RskDocument`'s
  `frontmatter`/`body` and `RskFrontmatter`'s inherited fields are bare,
  exactly like REQ/TSK's audited state) — depends on: Task 2.1 — status:
  done
- [x] Task 2.5: Draft `rsk_schema.json` via `generate_rsk_schema()`
  (mirroring `generate_req_schema`/`generate_tsk_schema` in
  `commands/schema.py`, calling `RskDocument.model_json_schema()`) +
  register `"rsk"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`) — depends on: Task 2.1 — status: done
- [x] Task 2.6: `tests/rsk/models/v1/test_parser.py` — mirrors
  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,
  defaults-when-absent, invalid status, malformed structure, out-of-range
  or missing assessment heading value, invalid TARA word, missing Scope
  entry) — plus `tests/rsk/models/v1/test_summary.py` covering
  `RskSummary`'s `DocSummary` inheritance, its `from_document` factory,
  and the coordinate bounds — depends on: Task 2.2, Task 2.5 — status:
  done

#### Phase 3: MCP Surface (commit 3)

- [x] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
  thin wrappers over `general/tools/_doc_paths.py` (mirrors
  `tsk/tools/_paths.py` etc. exactly; no new env-var/base-dir wiring needed
  — `doc_base_dir("rsk")` resolves to `{SPECMGR_DOCS_DIR or docs}/rsk`
  generically, verified) — depends on: Task 2.2 — status: done
- [x] Task 3.2: `parse_rsk(path: str) -> RskDocument` tool wrapper
  (`rsk/tools/parse_rsk.py`, mirroring `tsk/tools/parse_tsk.py` — reads a
  filepath from disk, delegates to the model-layer `parse_rsk`) — depends
  on: Task 3.1 — status: done
- [x] Task 3.3: `create_rsk(content: str) -> RskDocument` tool (body-only
  content, MCP builds frontmatter: `id`, `type="rsk"`, `status="open"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status: done
- [x] Task 3.4: `update_rsk(id, content) -> RskDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: done
- [x] Task 3.5: `set_status_rsk(id, status) -> RskDocument` tool (only path
  that changes `status`) — depends on: Task 3.1 — status: done
- [x] Task 3.6: `delete_rsk(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: done
- [x] Task 3.7: `validate_rsk(content, full=False) -> bool` tool — depends
  on: none — status: done
- [x] Task 3.8: `get_rsk(id) -> RskDocument` tool (id-based single-document
  read; tool, not resource — per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614)
  — depends on: Task 3.1 — status: done
- [x] Task 3.9: `get_rsk_example`/`get_rsk_template` tools + packaged data
  (`rsk/data/rsk_example.md` — a copy of Phase 1's `rsk_reference.md`,
  `rsk/data/rsk_template.md` — a valid, fully-parseable skeleton with a
  deadbeef-style id that round-trips through `parse_rsk` (tested)) via
  `general/tools/_packaged_data.py` — depends on: Task 1.3 — status: done
- [x] Task 3.10: `specmgr://rsk/schema` resource (packaged
  `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`; no `/list`
  resource — listing is the `list_rsk` tool, Task 3.14) — depends on:
  Task 3.1, Task 2.5 — status: done
- [x] Task 3.11: `specmgr://rsk/example` and `specmgr://rsk/template`
  resources — depends on: Task 3.9 — status: done
- [x] Task 3.12: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.rsk` (`data/*.md`, `data/*.json`), pre-commit hook +
  CI step for the packaged `rsk_schema.json` copy (mirroring
  `specmgr-schema-tsk-package`; `rsk/models/v1` also added to the `files:`
  trigger of all five existing `specmgr-schema*` hooks, and the stale
  generic-hook description fixed) — depends on: Task 2.5 — status: done
- [x] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — narrate
  the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`,
  instruction text in packaged `rsk_create_instructions.md`/
  `rsk_update_instructions.md`) — depends on: Tasks 3.3, 3.4, 3.5, 3.8,
  3.10 — status: done
- [x] Task 3.14: `rsk/tools/list_rsk.py` — the paged `list_rsk` tool
  (`max_results`/`offset` -> `PagedResult[RskSummary]`, mirroring
  `tsk/tools/list_tsk.py` + feat-13's shared paging contract, with the
  residual-risk fields from Task 2.3) — depends on: Tasks 3.1, 2.3 —
  status: done
- [x] Task 3.15: `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix`
  resources (`rsk/resources/tara.py`, `rsk/resources/risk_matrix.py` — raw
  packaged markdown via `read_packaged_text`, mirroring
  `tsk/resources/tsk_example.py`) + packaged copies `rsk/data/
  rsk_tara.md`/`rsk_risk_matrix.md` from the Phase 1 drafts (Task 1.5),
  with two zone-table cells corrected to match the documented product
  thresholds (see Decisions Made) — depends on: Tasks 1.5, 3.1 — status:
  done
- [x] Task 3.16: `tests/rsk/tools/test_list_rsk.py` (paging contract,
  clamping, skip-on-broken-file, residual fields present and correct) +
  `tests/rsk/resources/test_tara.py`/`test_risk_matrix.py` (registered,
  packaged content resolves from the source tree, `rsk_risk_matrix.md`'s
  documented zone thresholds — and all 25 zone-table cells — parsed out of
  the PACKAGED file and asserted against `level_from_product`) — depends
  on: Tasks 3.14, 3.15 — status: done
- [x] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers)
  AND update `server.py`'s module docstring (AGENTS.md: it is the
  authoritative, currently-maintained registration list) — the 5 resources
  (`specmgr://rsk/schema`, `/example`, `/template`, `/tara`,
  `/risk-matrix`), the 10 tools (`parse_rsk`, `get_rsk`, `list_rsk`,
  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,
  `set_status_rsk`, `delete_rsk` stub, `validate_rsk`), the 2 prompts
  (`create_risk`, `update_risk`), plus the "RSK has no
  `specmgr://rsk/{id}` resource" note in the docstring's existing
  per-domain pattern — depends on: Tasks 3.2-3.16 — status: done
- [x] Task 3.18: `tests/rsk/tools/...`, `tests/rsk/resources/...`,
  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/
  resources/`/`tests/tsk/prompts/` layout (Task 3.16's tests live under the
  same tree; 116 new tests, matching tsk's own coverage shape) — depends
  on: Tasks 3.1-3.17 — status: done

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

**As of 2026-08-25**: Phases 1-3 complete. GitHub issue #15 opened, feature
folder created from `.specmgr/_template/v1/README.md`. Full schema and MCP
surface proposed (see Design Notes and Task List), mirroring `feat-10`
(tsk)'s 4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA
instead of TARRA, cause/trigger/consequence split into separate sections,
assessment values moved from list items to H3 headings with regex `@alias`
constraints, execution pinned to the Orchestrator/Phase-Implementer
pattern, two domain-knowledge resources `specmgr://rsk/tara` +
`specmgr://rsk/risk-matrix` added, `list_rsk` summary lines carry the
residual-risk coordinates, and listing corrected to the paged `list_rsk`
tool per feat-13). Phase 1 (commit 1) delivered: `RskFrontmatter`
(6-value status, `open` default), the `Risk`/`Assessment` body models (5x5
H3-heading assessments, TARA-closed `## Strategy`), the `rsk_reference.md`
round-trip fixture, the mirrored test suite (43 tests, all green — 1349
total), and the two domain-knowledge drafts (`rsk_tara.md`,
`rsk_risk_matrix.md`). Phase 2 (commit 2) delivered: `RskDocument` +
`parse_rsk` (mirroring `TskDocument`/`parse_tsk`, two error channels:
structural `AssertionError` / field-level `pydantic.ValidationError`),
`RskSummary` (a `DocSummary` subclass with the initial/residual zone
levels, TARA word, first scope entry, and residual-risk coordinates, built
by a `from_document` factory), `_util.py::SCHEMA_COMMENT_VERSION`,
`rsk_schema.json` (registered in `specmgr schema`'s `_GENERATORS`), and
the parser/summary test suites (15 new tests, all green — 1364 total; all
`rsk` modules at 100% coverage). Phase 3 (commit 3) delivered: the full
MCP surface mirroring `tsk` — the ten `@mcp.tool()`s (`parse_rsk`,
`get_rsk`, the paged `list_rsk` returning `PagedResult[RskSummary]` via the
`from_document` factory, `get_rsk_example`/`get_rsk_template`,
`create_rsk`/`update_rsk`/`set_status_rsk`/`delete_rsk` stub/
`validate_rsk`), the five `@mcp.resource()`s (`specmgr://rsk/schema`,
`/example`, `/template`, plus the two domain-knowledge resources `/tara`
and `/risk-matrix`), the two `@mcp.prompt()`s (`create_risk`/
`update_risk`), the packaged `rsk/data/` (7 files, incl. the generated
`rsk_schema.json`), `server.py` registration (last-line import + docstring)
and `rsk/__init__.py` sub-package imports, the `pyproject.toml`
package-data entry, the new `specmgr-schema-rsk-package` pre-commit hook
(+ `rsk/models/v1` added to all five existing schema hooks' `files:`
triggers), and the Python-3.13-only CI step for the packaged schema copy —
plus the mirrored test trees (116 new tests, all green — 1480 total; all
`rsk` modules at 100% coverage; the ACC-005 drift guard now covers both
the documented product thresholds and all 25 zone-table cells of the
packaged `rsk_risk_matrix.md`). Also corrected two zone-table cells in the
Phase 1 `rsk_risk_matrix.md` draft (and this plan's own Design Notes
table) that contradicted the documented product thresholds — see Decisions
Made. Next: Phase 4 (Docs, CI wiring & final verification).

### Blockers

None.

### Recent Updates

#### 2026-08-25T20:55:00+02:00 (newest)

- Completed: Phase 3 (MCP Surface), per Task 3.1-3.18 — (3.1)
  `rsk/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`: thin
  risk-specific wrappers over `general.tools._doc_paths` (mirrors
  `tsk/tools/` file-for-file; no base-dir wiring — `doc_base_dir("rsk")`
  resolves generically); (3.2-3.9, 3.14) the ten `@mcp.tool()`s:
  `parse_rsk` (read path -> model-layer `parse_rsk`), `create_rsk`
  (body-only content; MCP builds the entire frontmatter, `status="open"`
  default), `update_rsk` (whole-body replace, preserves
  id/type/status/created/version, bumps `updated`), `set_status_rsk`
  (sole status path, bumps `updated`, body re-persisted verbatim),
  `delete_rsk` (registered stub, `structured_output=False`),
  `validate_rsk` (disk-free/id-free dry run, `full` flag), `get_rsk`
  (id-based read; tool, not resource, per ADR ddfb1109-422d-4507-8dbc-
  dc5e4bec9614), `get_rsk_example`/`get_rsk_template` (packaged data via
  `read_packaged_text`), and the paged `list_rsk`
  (`PagedResult[RskSummary]`, the `RskSummary.from_document(doc,
  ref=path.stem)` construction site from Task 2.3, skip-and-continue on
  `AssertionError`/`pydantic.ValidationError`, feat-13 paging contract);
  (3.10, 3.11, 3.15) the five `@mcp.resource()`s:
  `specmgr://rsk/schema` (packaged `rsk/data/rsk_schema.json` via
  `importlib.resources`, `application/json`, deliberately not importing
  `commands.schema` to avoid leaking the cli extra), `/example` +
  `/template` (raw packaged markdown), and the two domain-knowledge
  resources `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix` (raw
  packaged markdown, `text/markdown`; functions named `tara`/
  `risk_matrix` with `name="rsk_tara"`/`name="rsk_risk_matrix"` — see
  Decisions Made); (3.13) the two `@mcp.prompt()`s `create_risk`/
  `update_risk` (the issue's literal wording, not `rsk`-prefixed),
  instructional text in packaged `rsk_create_instructions.md`/
  `rsk_update_instructions.md` via `string.Template` (`$topic`;
  `$id`/`$instructions`); (3.9, 3.15) `rsk/data/` packaged, 7 files:
  `rsk_example.md` (copy of Phase 1's `rsk_reference.md`),
  `rsk_template.md` (valid, fully-parseable skeleton, deadbeef-style id,
  every section incl. both 5x5 assessments + a TARA word; round-trips
  through `parse_rsk` — tested), `rsk_schema.json` (generated via
  `specmgr schema --type rsk --output-dir
  src/biz/dfch/specmgr/rsk/data` — same generator as `docs/`),
  `rsk_tara.md`/`rsk_risk_matrix.md` (copies of the Phase 1 drafts, zone-
  table cells corrected — see Decisions Made), and the two instructions
  files; (3.12) `pyproject.toml` package-data entry (`data/*.md`,
  `data/*.json`), new `specmgr-schema-rsk-package` pre-commit hook +
  `rsk/models/v1` added to the `files:` trigger of all five existing
  `specmgr-schema*` hooks (feat-10 precedent) + the stale generic-hook
  description fixed ("currently `req` and `uc`" -> the actual five
  registered types), and the Python-3.13.13-pinned CI step "Make sure
  `src/biz/dfch/specmgr/rsk/data/rsk_schema.json` is correct" (placed
  after the tsk step; no redundant `docs/rsk_schema.json` step — the
  full-`specmgr schema` steps already regenerate it, Task 4.3 confirms
  coverage); (3.16, 3.18) `tests/rsk/{tools,resources,prompts}/`
  mirroring `tests/tsk/`'s layout and coverage shape, 116 new tests: 70
  tools (incl. `test_list_rsk.py`'s paging contract/clamping/skip-on-
  broken-file + the residual fields' presence and correctness, and the
  `test_get_rsk_template.py` round-trip), 26 resources (incl.
  `test_tara.py` — exactly the four TARA words documented, cross-checked
  against `Strategy`'s own validator — and `test_risk_matrix.py`, the
  ACC-005 drift guard: the documented product thresholds and all 25 zone-
  table cells are parsed out of the PACKAGED file and asserted against
  `level_from_product`), 20 prompts; (3.17) `server.py`'s last-line
  domain import gained `rsk` (between `req` and `tsk`) and its module
  docstring's registration list gained the 5 resources/10 tools/2
  prompts + the "RSK has no `specmgr://rsk/{id}` resource" note;
  `rsk/__init__.py` now imports `prompts`/`resources`/`tools` for their
  registration side effects (mirrors `tsk/__init__.py`, docstring
  updated). Quality gate: ruff format/check clean (932 files), vulture
  clean, 1480 tests OK (1364 + 116 new; all `rsk` modules 100% covered),
  `specmgr docs` regenerated (26 new `docs/api/` module files +
  `GENERATED.md`/`docs/api/README.md` updated, plus a new
  `PagedResult[RskSummary]` section in the `paged_result` module docs),
  `specmgr mcp-docs` regenerated (`docs/MCP.md` gained the 5 rsk
  resources, 10 rsk tools, and 2 rsk prompts), `specmgr schema` all
  five types `(unchanged)` + the packaged `rsk_schema.json` copy
  `(unchanged)` on the re-run, `specmgr coverage-badge` regenerated
  (`docs/coverage.svg` still 98%, content unchanged)
- Next: Phase 4 (Docs, CI wiring & final verification) — Task 4.1-4.4
  walk-through (docs/mcp-docs/schema regeneration confirmation, CI
  coverage check, final ACC-001..008 pass)
- Notes: see the three new Decisions Made entries below (zone-table cell
  correction in the Phase 1 draft and this plan's own Design Notes table,
  the `tara`/`risk_matrix` resource function naming, and the
  `whitelist.py` `_.from_document` entry removal); also, the vulture
  whitelist needed no new entries — `rsk/tools/__init__.py`'s own
  imports/`__all__` keep the ten tool names out of vulture's findings the
  same way `tsk`'s do (verified: vulture clean)

#### 2026-08-25T09:47:03+02:00

- Completed: Phase 2 (Pydantic Models & Parser), per Task 2.1-2.6 —
  (2.1) `rsk/models/v1/document.py::RskDocument(frontmatter, body)`:
  mirrors `TskDocument`/`ReqDocument`'s own frontmatter+body pairing
  (`RskFrontmatter` + `Risk`); (2.2) `rsk/models/v1/parser.py::parse_rsk`:
  mirrors `parse_tsk`/`parse_req` exactly (python-frontmatter split, own
  `_stringify_metadata` copy, `Risk.from_text(format_text(post.content))`,
  two error channels — structural `AssertionError` / field-level
  `pydantic.ValidationError`, both uncaught); (2.3)
  `rsk/models/v1/summary.py::RskSummary(DocSummary)`: base's
  `id`/`title`/`status`/`ref` first, then `initial_level`/`residual_level`
  (from the assessments' computed `level`), `strategy` (verbatim TARA
  word), `scope` (first `## Scope` entry), and the residual-risk
  coordinates `residual_probability`/`residual_impact` (1..5,
  `ge`/`le`-constrained) / `residual_product` (1..25, the risk product) —
  all derived by a new `from_document(document, ref)` classmethod factory
  (never re-implementing the 5x5 zone mapping), which is also the Phase 3
  `list_rsk` tool's construction site (see Decisions Made); (2.4)
  description audit: no gaps found — Phase 1's body/assessment fields and
  the new `RskSummary` fields carry `Field(description=...)`, while
  `RskDocument`'s `frontmatter`/`body` and `RskFrontmatter`'s
  inherited/base fields are bare exactly like REQ/TSK's own audited state
  (verified against `docs/req_schema.json`/`tsk_schema.json`); (2.5)
  `rsk/models/v1/_util.py::SCHEMA_COMMENT_VERSION = "v1"` (mirrors
  `tsk`'s) + `commands/schema.py`: `generate_rsk_schema()` (injects
  `$schema` + `$comment`, `indent=2, sort_keys=True` + trailing newline)
  and the `"rsk"` `_GENERATORS` entry — `specmgr schema` newly writes
  `docs/rsk_schema.json` (JSON Schema 2020-12, title `RskDocument`), all
  four other `docs/*_schema.json` files byte-identical; (2.6)
  `tests/rsk/models/v1/test_parser.py` (10 tests, mirroring
  `TestParseTsk`'s case shape: minimal doc incl. both assessments'
  `value`/`level`, full `rsk_reference.md` round-trip incl. frontmatter
  date stringification and re-round-trip stability, frontmatter
  defaults-when-absent (`status` -> `open`), invalid status
  (`draft` + unknown word -> `ValidationError`), missing mandatory
  section + wrong assessment order (`AssertionError`),
  `### Probability 6` / `### Probability` (`AssertionError`),
  `## Strategy` = `tolerate` (`ValidationError`), zero-entry `## Scope`
  (`AssertionError`)) + `tests/rsk/models/v1/test_summary.py` (5 tests:
  `DocSummary` subclass/field order, `from_document` on the minimal and
  reference documents, coordinate-bounds rejection). Package exports
  updated (`rsk/models/__init__.py` + `rsk/models/v1/__init__.py`
  docstrings/imports/`__all__`: `RskDocument`, `parse_rsk`, `RskSummary`,
  `SCHEMA_COMMENT_VERSION`); vulture whitelist gained `_.from_document`
  (framework-bound: its only caller is the Phase 3 `list_rsk` tool —
  Phase 1 precedent) and the five `RskSummary`-only field names. Quality
  gate: ruff format/check clean (854 files), vulture clean, 1364 tests OK
  (1349 + 15 new; all `rsk` modules 100% covered), `specmgr docs`
  regenerated (4 new `docs/api/` module files + `GENERATED.md`/
  `docs/api/README.md` updated), `specmgr mcp-docs` no change
  (`docs/MCP.md` untouched — nothing MCP-registered yet),
  `specmgr schema` stable on re-run (exit 0), `specmgr coverage-badge`
  regenerated (`docs/coverage.svg` still 98%, content unchanged)
- Next: Phase 3 (MCP Surface) — `rsk/tools/` (incl. the paged `list_rsk`
  consuming `RskSummary.from_document`), `rsk/resources/` (incl.
  `specmgr://rsk/tara` + `/risk-matrix`), `rsk/prompts/`, `rsk/data/`
  packaging, `server.py` registration
- Notes: see the new Decisions Made entry below (`RskSummary.from_document`
  factory mechanism); also, the frontmatter `updated` date was bumped to
  2026-08-25 (execution crossed midnight since Phase 1's 2026-08-24 entry)

#### 2026-08-24T19:59:00+02:00

- Completed: Phase 1 (Specification), per Task 1.1-1.5 — (1.1)
  `rsk/models/v1/frontmatter.py::RskFrontmatter`: `type=Literal["rsk"]`,
  6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/
  `dropped`, `open` default via redeclared `status` field + own
  `mode="before"` validator (runs before the base's
  `_default_blank_status_to_draft`, verified against Pydantic 2.13.4);
  (1.2) `rsk/models/v1/assessment.py`: `Probability`/`Impact` leaf H3
  sections with regex `@alias` `^Probability [1-5]$`/`^Impact [1-5]$`
  (value in the heading, computed `value: int` per leaf) and
  `Assessment(MarkdownSection2)` with mandatory `probability`/`impact`
  fields and computed `level` from the product zones (1-4 low, 5-9
  medium, 10-14 high, 15-25 very high) via public `level_from_product`;
  `InitialAssessment`/`ResidualAssessment` thin LITERAL-aliased subclasses
  pin each H2 heading and enforce the initial-before-residual order;
  `rsk/models/v1/body.py`: `Risk(MarkdownSection1WithComment)` with the
  full section order — leaf `Cause`/`Trigger`/`Consequence`/`Mitigation`,
  `Scope` (`list[MarkdownListItem]`, min 1), `Strategy` (`value:
  MarkdownParagraph` validated against the TARA 4-value set, mirroring
  `req`'s `Level`/`Priority`), optional `Owner`/`Tags`/`More Information`;
  (1.3) `rsk_reference.md`: complete mdformat-stable reference document
  (frontmatter + body exercising every field; the plan's worked example —
  initial 4x3=12 `high` -> residual 2x3=6 `medium`) reserved as Phase 2's
  parser round-trip fixture; (1.4) `tests/rsk/models/v1/` (43 tests):
  frontmatter status set/defaults, 5x5 heading-value bounds and all four
  zone boundaries (4/5, 9/10, 14/15), missing-value/wrong-H3-order/
  wrong-H2-order rejection, TARA closed set, `Scope` >=1, optional
  sections absent-vs-present, reference-document body round-trip; (1.5)
  domain-knowledge drafts `rsk_tara.md`/`rsk_risk_matrix.md` in this
  feature folder (Phase 3 packages them into `rsk/data/`). Package shape
  mirrors feat-10's Phase 1 (`rsk/__init__.py` docstring-only;
  `rsk/models/` + `rsk/models/v1/` re-export the public names with
  `__all__`); vulture whitelist gained the new Pydantic fields/validator
  (feat-10 precedent). Quality gate: ruff format/check clean, vulture
  clean, 1349 tests OK, `specmgr docs` + `specmgr mcp-docs` +
  `specmgr coverage-badge` regenerated with no drift (new rsk modules at
  100% coverage; `docs/MCP.md`/`docs/coverage.svg` unchanged in content)
- Next: Phase 2 (Pydantic Models & Parser) — `RskDocument`, `parse_rsk`,
  `RskSummary`, `rsk_schema.json` + `specmgr schema` registry entry, and
  `tests/rsk/models/v1/test_parser.py` (round-tripping `rsk_reference.md`)
- Notes: see the three new Decisions Made entries below (Phase-1
  micro-decisions); also, the pre-existing 543KB session transcript in
  this feature folder was left unformatted at branch HEAD (committed in
  the session-transcript commit after the baseline plan commit) — applied
  the project's own `ruff format` to it (2-line, formatting-only diff) so
  the mandatory whole-tree `ruff format --check` gate passes

#### 2026-08-24T15:04:31+02:00

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
- **2026-08-24** (Phase 1): `Assessment` (the shared `MarkdownSection2`
  base, regex `@alias` `^(Initial|Residual) Assessment$`) is instantiated
  on `Risk` through two thin LITERAL-aliased subclasses —
  `InitialAssessment` and `ResidualAssessment` — rather than a single
  shared field type — rationale: with one class whose regex alias accepts
  both H2 headings, a document carrying the two assessment sections in the
  wrong order would parse successfully with the contents silently swapped;
  the LITERAL-pinned subclasses make `match_alias` reject the swapped order
  at parse time (verified), keeping the plan's single `Assessment` class
  as the shared base (fields, computed `level`, direct-construction
  tests).
- **2026-08-24** (Phase 1): `RskFrontmatter` redeclares `status` with its
  own `"open"` default plus a child-class `mode="before"` validator
  (`_default_blank_status_to_open`, via `models/md`'s `default_if_blank`)
  — rationale: the base's `"draft"` default is not part of rsk's closed
  six-value set, so absent/blank `status` must default to `"open"`;
  verified against Pydantic 2.13.4 that child-class before-validators run
  before the base's `_default_blank_status_to_draft`, which then sees
  `"open"` and passes it through — no base-model change needed.
- **2026-08-24** (Phase 1): the product→zone mapping is exposed as a
  public `level_from_product(product: int)` helper in `assessment.py`
  (used by `Assessment.level`, exported in `rsk.models.v1`'s `__all__`) —
  rationale: product 14 is unattainable by any 1..5 probability/impact
  pair (no factors <= 5), so the 14/15 zone boundary the plan requires
  tested can only be exercised through the mapping itself; it also gives
  the ACC-005 documented-thresholds test (Phase 3) a single target.
- **2026-08-25** (Phase 2): `RskSummary` (unlike `TskSummary`/`ReqSummary`,
  which add no fields and are built inline in their domains' listing
  tools) carries a `from_document(document, ref)` classmethod factory —
  rationale: its six risk-specific fields (the zone levels, the TARA word,
  the first scope entry, and the residual-risk coordinates incl. the risk
  product) are all *derived* from the parsed document's computed
  `level`/`value` fields; a model-layer factory keeps that derivation in
  one place (testable in Phase 2, zone-mapping drift surfaces in
  `tests/rsk/models/v1/test_summary.py`), never re-implements the 5x5
  mapping, and leaves the Phase 3 `list_rsk` tool a one-liner
  (`RskSummary.from_document(doc, ref=path.stem)`, mirroring the
  inline-construction shape `list_tsk`/`list_req` use for the base four
  fields). The factory's `ref` parameter (the file path's `stem`) is taken
   as an argument rather than read from the document, matching how the
   other domains' listing tools pass it. The five derived-only field names
   plus `_.from_document` are vulture-whitelisted (their only caller is
   the Phase 3 tool — Phase 1's own precedent for not-yet-consumed model
   members).
- **2026-08-25** (Phase 3): the Phase 1 draft `rsk_risk_matrix.md`'s zone
  table — and this plan's own Design Notes table — carried two cells that
  contradicted the documented product thresholds: (p=5, i=3) and (p=4, i=4)
  (products 15 and 16, both in the 15-25 `very high` band) read `high` —
  corrected to `very high` in the packaged `rsk/data/rsk_risk_matrix.md`,
  the feature-folder original, and this plan's Design Notes table (content
  correction, in place, no renumbering) — rationale: the Task 3.16
  ACC-005 drift guard parses the packaged table and asserts all 25 cells
  against `level_from_product`, which surfaced the discrepancy; the model
  (`level_from_product` and the 1-4/5-9/10-14/15-25 threshold statement)
  was correct all along, so only the prose table was wrong.
- **2026-08-25** (Phase 3): the `specmgr://rsk/tara`/
  `specmgr://rsk/risk-matrix` resource functions are named `tara`/
  `risk_matrix` (matching their Task 3.15 module names
  `rsk/resources/tara.py`/`risk_matrix.py`) with the MCP-registry
  `name=` parameters `rsk_tara`/`rsk_risk_matrix` — rationale: the
  `tsk_example`/`iso25010` convention is function-name == module-name
  (which is what `rsk/resources/__init__.py`'s own `from . import ...`
  references for vulture), whereas `general/resources/version.py`'s
  divergent `version_info` function required a `whitelist.py` entry;
  keeping function == module keeps the two new resources vulture-clean
  with no whitelist change, while the `name=` parameters keep the MCP
  registry names domain-qualified.
- **2026-08-25** (Phase 3): removed the `whitelist.py` `_.from_document`
  entry (added in Phase 2) — rationale: its stated reason ("its only
  caller is a Phase 3 MCP tool (not yet built)") is realized:
  `rsk/tools/list_rsk.py` now calls `RskSummary.from_document` in `src/`,
  so vulture sees the reference directly (verified: vulture clean after
  removal).

### Related PRs / Commits

No PR opened yet. Work happens on branch `feat-15-add-artifact-type-risk`
(from `dev`), one Conventional Commit per phase (see Execution approach).
