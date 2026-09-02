---
created: '2026-08-29 00:00:00.000Z'
id: feat-30-sop
status: done
updated: '2026-08-30 00:00:00.000Z'
version: 1.0.0
---

# Feature: Add artifact type "Standard Operating Procedure" (SOP)

## Plan

### Overview

New `sop` domain: Standard Operating Procedures — structured, step-by-step
operational documents with a RASCI-style responsibility assignment and a
closed approval/effectivity lifecycle. `sop` follows the domain-first
hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and is built on the
generic `models/md` parsing engine with the simple surface used by
GOL/RSK/QA/DEC — no fine-grained ADR-style mutation tools, no renderer
(writes persist the caller's raw validated body byte-for-byte). `sop` is
the **first domain built from scratch entirely on the post-feat-22 generic
mutation tools** (ADR 36905d5b-8057-4294-8665-c7eed5534db0): it has no
`update_sop`/`set_status_sop` tools of its own — it dispatches straight
into the generic `update`/`set_status` tools in `general/tools/` from day
one, per the convention `AGENTS.md` already reserves for future domains.

### Requirements

- REQ-001: Define the `sop` markdown schema — frontmatter (`type="sop"`,
  closed 5-value status set `draft`/`review`/`approved`/`active`/`retired`,
  default `draft`) and body (H1 title, mandatory `## Purpose`, optional
  `## Scope`, optional `## Definitions`, optional `## Roles and Responsibilities` (RASCI composite — see Design Notes), optional `## Safety and Precautions`, mandatory `## Procedure` (>=1 `### Step N: {title}`), optional `## Related Artifacts` (5 cross-reference sub-lists,
  including a `Sops` self-reference), optional `## More Information`,
  optional `## Updates` (ISO8601-timestamped entries, always last)).
- REQ-002: Pydantic models under `sop/models/v1/` (frontmatter, body,
  document, parser, summary), domain-first, mirroring `dec`/`gol`'s exact
  file shapes. No `models/md` engine changes are needed — every field
  (including the "optional heading that MAY be present with zero list
  items" shape used by `Support`/`Consulted`/`Informed`) is already
  supported by the existing engine, empirically verified against the live
  `MarkdownSection3`/`MarkdownListItem` classes before this plan was
  written (see Design Notes).
- REQ-003: Parse/validate `sop` documents from markdown, mirroring
  `parse_dec`/`parse_gol`'s two-error-channel convention (`AssertionError`
  for structural problems, `pydantic.ValidationError` for field-level
  problems).
- REQ-004: 8 MCP tools — **no** `update_sop`/`set_status_sop` (see
  Overview): `create_sop`, `parse_sop`, `list_sop` (paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), `get_sop(id, raw=False)`, `get_sop_example`, `get_sop_template`, `delete_sop` (stub),
  `validate_sop` — plus private `_paths`/`_io`/`_lock`/`_write` helpers.
- REQ-005: MCP resources: `specmgr://sop/schema`, `/example`, `/template`
  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
  reads are `get_sop`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_sop(topic)`/`update_sop(id, instructions=None)` — narrated instruction flows reusing the
  dedup-check-first pattern (`list_sop`) and the `TodoWrite`/`question`-tool
  narration pattern from `gol`/`dec`/`prb`'s prompts. Both use their own
  packaged instructions data file (`sop_create_instructions.md`/
  `sop_update_instructions.md` under `sop/data/`), not an inline string.
- REQ-007: Add `"sop"` to the generic cross-domain mutation tools —
  `_update_sop`/`_set_status_sop` private adapters, `"sop"` dispatch-table
  entries, and `"sop"` added to the `Literal[...]` parameter unions in
  `general/tools/update.py` and `general/tools/set_status.py` (ADR
  36905d5b's "one dispatch entry per generic tool" convention for new
  domains — this is the first domain to exercise that path from its
  initial build rather than via a later conversion, as `dec` needed).
- REQ-008: Packaged example/template/schema/instructions data
  (`sop/data/`) via the existing generic
  `general/tools/_packaged_data.py`, with the matching `pyproject.toml`
  package-data entry, pre-commit hook, and CI step.
- REQ-009: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
  `sop` entry in the doc-type registry, `commands/schema.py`), `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md` and root
  `README.md` updated.
- REQ-010: Full test coverage mirroring `tests/dec/`'s layout, plus new
  test coverage in `tests/general/tools/test_update.py`/
  `test_set_status.py` for the `"sop"` dispatch entries (REQ-007).
- REQ-011: Add a cross-cutting, general MCP resource `specmgr://rasci`
  (`general/resources/rasci.py`, packaged `general/data/general_rasci.md`)
  defining the generic RASCI (Responsible/Accountable/Support/Consulted/
  Informed) responsibility-assignment framework — **not** `sop`-specific,
  mirroring `specmgr://iso25010`'s cross-cutting placement rationale (a
  well-known external framework, not coupled to any one domain's schema),
  rather than `rsk/tara`'s domain-scoped placement (whose content is
  tightly coupled to RSK's own closed vocabulary). Content is limited to
  the five roles' generic definitions — no `sop`-specific heading names or
  cardinality rules. `sop`-domain discoverability is handled via explicit
  cross-references, not duplication: `RolesAndResponsibilities`/
  `Accountable`/`Responsible`/`Support`/`Consulted`/`Informed` class
  docstrings (which flow into `specmgr://sop/schema`'s generated JSON
  field descriptions), `sop/__init__.py`'s module docstring, the
  `create_sop`/`update_sop` packaged instructions (an explicit "read
  `specmgr://rasci` first" step), and `server.py`'s module docstring
  (both the `general` resources paragraph and the `sop` paragraph).

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001/002/003 — packaged example **and** template
  parse via `parse_sop`; structural violations raise `AssertionError`:
  unknown H2; missing `## Purpose` or `## Procedure`; `## Procedure` with
  zero steps; `### Step N` without `: title`; duplicate step numbers;
  `## Roles and Responsibilities` present without `### Accountable` or
  without `### Responsible`; `### Accountable` written as a bullet list
  instead of a single paragraph; `### Responsible` present but empty;
  `## Related Artifacts` sub-list present with zero items; a malformed
  `## Updates` entry heading (wrong timestamp format, missing ` — title`);
  misordering of any top-level section; second H1; non-blank content
  before the H1.
- [ ] ACC-002: Verifies REQ-001/002 — value violations raise
  `pydantic.ValidationError`: `status` outside the 5-value set, `type` !=
  `"sop"`; `Step.number`/`Step.name` computed correctly from the heading;
  `### Support`/`### Consulted`/`### Informed` each independently
  present-with-zero-items vs. present-with-N-items vs. absent entirely
  (three distinct, individually testable states); `Related Artifacts`
  sub-lists (including `Sops`) independently optional; `UpdateEntry`'s
  computed `timestamp`/`title` fields extracted correctly from a
  well-formed heading.
- [ ] ACC-003: Verifies REQ-004 — every listed tool is implemented,
  registered, and callable; `create_sop`→`get_sop`→`list_sop`→`update`
  (generic, `type="sop"`)→`set_status` (generic, `type="sop"`)→
  `validate_sop` round-trip against a temp `SPECMGR_DOCS_DIR`;
  `create_sop` fixes `status="draft"` and writes
  `sop-{id}-{slug}.md`; `delete_sop` raises `NotImplementedError`;
  `get_sop(id, raw=True)` returns the frontmatter-stripped body text
  verbatim; `list_sop` paging (default 25 / cap 100 / `truncated`
  boundary) mirrors every other domain's `list_<d>` tool exactly.
- [ ] ACC-004: Verifies REQ-005 — every listed resource is implemented and
  registered (no `/{id}`, no `/list`); `specmgr://sop/schema` equals fresh
  `generate_sop_schema()` output; example/template resources equal the
  packaged files byte-for-byte.
- [ ] ACC-005: Verifies REQ-006 — both prompts return instruction text
  with `$topic`/`$id`/`$instructions` substituted from packaged data;
  `create_sop`'s narration includes a `list_sop` dedup check first.
- [ ] ACC-006: Verifies REQ-007 — the generic `update`/`set_status` tools
  accept `type="sop"` and correctly dispatch to `_update_sop`/
  `_set_status_sop`; both the whole-body and line-range (`begin`/`end`)
  branches of `update` work for `sop`; `set_status` rejects
  `superseded_by` for `type="sop"` with the same `ValueError` every
  non-adr type gets; new test cases added to
  `tests/general/tools/test_update.py`/`test_set_status.py` (not just
  `tests/sop/`) exercise this.
- [ ] ACC-007: Verifies REQ-008 — packaged data resolves correctly from a
  real, non-editable install (`uv build --wheel` + scratch-venv install),
  mirroring `dec`/`gol`'s ACC-007 verification.
- [ ] ACC-008: Verifies REQ-009 — `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` all report no drift after implementation; `AGENTS.md` and root
  `README.md` reflect the new `sop` domain, including the "dispatch-only,
  no per-domain update/set_status tools" note.
- [ ] ACC-009: Verifies REQ-010 — full unittest suite green; ruff
  format/check and vulture clean; `specmgr unused-code` clean.
- [ ] ACC-010: Verifies REQ-011 — `specmgr://rasci` is implemented,
  registered under `general/resources/`, and returns the packaged
  `general_rasci.md` content verbatim; the content is genuinely generic
  (no `sop`-specific structural rule — heading names, mandatory/optional
  status, cardinality — leaked into it); all four discoverability
  cross-references are present (the six `sop` body-model docstrings,
  `sop/__init__.py`, the create/update instructions, `server.py`'s
  docstring in both the `general` and `sop` paragraphs);
  `tests/general/resources/test_rasci.py` covers real-content assertions,
  fresh-read-per-call, and `FileNotFoundError` on a missing packaged file,
  mirroring `tests/rsk/resources/test_tara.py`'s non-drift-guard tests
  (no drift-guard test needed here, since no Pydantic field independently
  validates against the RASCI role vocabulary).

### Scope

Included:

- `sop/` domain package (models, tools, resources, prompts, data) built on
  the existing `models/md` engine.
- The RASCI `## Roles and Responsibilities` composite (`Accountable`
  single-paragraph + mandatory, `Responsible` mandatory list, `Support`/
  `Consulted`/`Informed` optional lists that MAY be present-but-empty).
- The structured `## Procedure` → `### Step N: {title}` mechanism.
- The `## Related Artifacts` 5-sub-list shape (GOL/DEC's 4 plus a new
  `Sops` self-cross-reference).
- The ISO8601-timestamped `## Updates` entry heading
  (`yyyy-MM-dd HH:mm:ss.fff±HH:mm — {title}`, structurally enforced).
- `"sop"` dispatch entries in the generic `update`/`set_status` tools
  (`general/tools/`) — the first domain to be built dispatch-only from
  day one.
- A new cross-cutting `general/resources/rasci.py` (`specmgr://rasci`)
  resource defining the generic RASCI framework, motivated by but not
  scoped to `sop` — discoverable from `sop` via cross-references only
  (see REQ-011).
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`, root
  `README.md`).
- Tests mirroring `tests/dec/`'s layout and coverage depth, plus new
  dispatch-entry test cases in `tests/general/tools/`.

Explicitly out of scope:

- No `update_sop`/`set_status_sop` per-domain tools — see Overview.
- No `render_sop` / deterministic re-render (raw-body persistence like
  GOL/RSK/QA/DEC).
- No `specmgr://sop/{id}` resource, no `specmgr://sop/list` resource.
- No per-step RACI/RASCI assignment — RASCI is a document-level `## Roles and Responsibilities` section only, not attached to individual
  `### Step N` entries (flagged as possible future work, not built now).
- No hard validator preventing multiple names inside `### Accountable`'s
  single paragraph (e.g. "CEO and CFO jointly") — only the *structural*
  shape (single paragraph, not a bullet list) is enforced.
- Real implementation of `delete_sop` — a stub raising
  `NotImplementedError`, matching every other domain's `delete_*` stub.
- Any changes to the `models/md` engine itself — the engine already
  supports every shape this schema needs (verified empirically before
  writing this plan); if it turns out not to during implementation, stop
  and report rather than patching the engine.
- Any changes to any other existing domain's schema, tools, or data.

### Dependencies

- Depends on: `models/md` engine (feat-5, done), ADR
  ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), ADR
  bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic `MarkdownFrontmatter`
  base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based
  reads), ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool,
  not a resource), ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic
  `update`/`set_status` dispatch tools — `sop` must use these from day
  one, not per-domain tools), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py`/
  `_splice.py` infrastructure.
- Blocks: nothing known.

### Design Notes

**Document structure** (section order is binding — field declaration
order = markdown order):

```markdown
---
id: <uuid>            # specmgr-assigned
type: sop              # Literal["sop"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft           # draft | review | approved | active | retired
version: 1.0.0
---

# {Free-form title}                            H1, @alias REGEX ".+"
## Purpose                                      REQUIRED (leaf)
## Scope                                        OPTIONAL (leaf)
## Definitions                                  OPTIONAL (leaf)
## Roles and Responsibilities                   OPTIONAL (composite, RASCI)
  ### Accountable                               REQUIRED once container present (single MarkdownParagraph)
  ### Responsible                               REQUIRED once container present (bullet list, >=1 item)
  ### Support                                   OPTIONAL (bullet list, MAY be present with 0 items)
  ### Consulted                                 OPTIONAL (bullet list, MAY be present with 0 items)
  ### Informed                                  OPTIONAL (bullet list, MAY be present with 0 items)
## Safety and Precautions                       OPTIONAL (leaf)
## Procedure                                    REQUIRED (composite, >=1 step always)
  ### Step 1: {title}
  ### Step 2: {title}
## Related Artifacts                            OPTIONAL (composite, GOL shape + Sops)
  ### Requirements / ### Decisions / ### Goals /
  ### Acceptance Criteria / ### Sops            OPTIONAL (bullet lists, >=1 if present)
## More Information                             OPTIONAL (leaf)
## Updates                                      OPTIONAL, LAST (TSK/DEC shape, ISO8601 timestamp)
  ### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}
  {entry prose}
```

**Model classes** (all in `sop/models/v1/body.py`, one
`MarkdownSection2`/`MarkdownSection3` subclass per heading; implicit
SPACE_SEPARATED aliases unless noted):

- `Sop(MarkdownSection1)` — `@alias(value=".+", type=AliasType.REGEX)`;
  fields in order: `purpose`, `scope | None`, `definitions | None`,
  `roles_and_responsibilities | None`, `safety_and_precautions | None`,
  `procedure`, `related_artifacts | None`, `more_information | None`,
  `updates | None`; `model_validator(mode="after")` rejecting duplicate
  `Step` numbers (mirrors DEC's `Decision` after-validator; only inspects
  `self.procedure.steps`, always present since `procedure` is mandatory).
- `Purpose` — mandatory leaf (DEC's `Context` precedent: opaque free
  text, no declared nested fields).
- `Scope`, `Definitions`, `MoreInformation` — optional leaves, implicit
  SPACE_SEPARATED aliases.
- `SafetyAndPrecautions(MarkdownSection2)` — `@alias(value="Safety and Precautions", type=AliasType.LITERAL)` (lowercase "and" breaks the
  camel-case SPACE_SEPARATED convention); optional leaf.
- `RolesAndResponsibilities(MarkdownSection2)` — `@alias(value="Roles and Responsibilities", type=AliasType.LITERAL)`; optional container;
  fields: `accountable: Accountable` (mandatory — a plain, non-`Optional`
  field type is sufficient to enforce "heading required once this
  container is present" structurally, via the engine's own
  `process_field` mechanics; no custom validator needed, confirmed
  empirically — see Verification below), `responsible: Responsible`
  (mandatory, same mechanism), `support: Support | None = None`,
  `consulted: Consulted | None = None`, `informed: Informed | None = None`.
- `Accountable(MarkdownSection3)` — `value: MarkdownParagraph` (single,
  mandatory paragraph — DEC's `DecisionOutcome.statement`/GOL's
  `Goal.statement` precedent); exactly one owner, never a bullet list.
- `Responsible(MarkdownSection3)` — `items: list[MarkdownListItem] = Field(min_length=1)`; mandatory, >=1 entry, empty body raises
  `AssertionError` (verified empirically).
- `Support`, `Consulted`, `Informed(MarkdownSection3)` — each `items: list[MarkdownListItem] | None = None`; the heading MAY be present with
  zero list items (parses to `items=None`, verified empirically both when
  followed by a sibling heading and at end-of-section) or with N items.
- `Procedure(MarkdownSection2)` — mandatory (implicit alias "Procedure");
  `steps: list[Step] = Field(min_length=1)` (an H2 with zero steps is a
  structural error).
- `Step(MarkdownSection3)` — `@alias(value=r"^Step \d+: .+$", type=AliasType.REGEX)`; leaf; computed fields `number: int`/`name: str`
  extracted from the heading line (DEC's `Option` precedent, regex
  `^### Step (\d+): (.+)$`, `re.fullmatch`); leading zeros accepted, gaps
  allowed, duplicates rejected (see `Sop`'s after-validator above).
- `RelatedArtifacts(MarkdownSection2)` + `Requirements`/`Decisions`/
  `Goals`/`AcceptanceCriteria`/`Sops(MarkdownSection3)` — GOL/DEC's shape
  copied verbatim for the first four; `Sops` is new, same shape (`items: list[MarkdownListItem] = Field(min_length=1)`), a self-cross-reference
  sub-list (GOL's self-referencing `Goals` sub-list precedent — a `sop`
  document may reference other, related/superseding SOPs). All five
  independently optional on the container.
- `Updates(MarkdownSection2)` — implicit alias "Updates"; `updates: list[UpdateEntry] = Field(min_length=1)`.
- `UpdateEntry(MarkdownSection3)` — `@alias(value=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$", type=AliasType.REGEX)`; `content: MarkdownParagraph` (mandatory lead
  paragraph, TSK/DEC shape); computed fields `timestamp: str`/`title: str` extracted from the heading via
  `^(?P<timestamp>...) — (?P<title>.+)$` (DEC `Option`/RSK precedent).
  Format: ISO8601 date + space + time + milliseconds + explicit UTC
  offset (`+02:00`, `-05:00`) or `Z` for UTC — deliberately **not** the
  same format as frontmatter `created`/`updated` (which stay on the
  shared generic tools' microsecond, no-offset, `T`-separator format;
  this new format is scoped to `## Updates` entry headings only, which
  are hand/LLM-authored body content, not tool-generated). Malformed
  headings raise `AssertionError`.

**Verification performed before writing this plan** (read-only, in-memory,
no files written): live-imported the actual `models.md` engine classes
and confirmed (a) a `MarkdownSection3` subclass with `items: list[MarkdownListItem] | None = None` parses a heading with zero
following content to `items=None`, both when immediately followed by a
sibling heading and at end-of-parent-section; (b) the same shape with
`items: list[MarkdownListItem] = Field(min_length=1)` (mandatory) raises
`AssertionError` on the same empty-body input; (c) a present, populated
list renders and round-trips (subject to the engine's pre-existing,
documented tight-to-loose list normalization, unrelated to this feature).
No `models/md` engine changes are required.

**Independently re-verified 2026-08-30** (read-only, in-memory, no files
written, no repo changes) against the live engine, confirming the above
claims hold and are safe to build on directly — a future agent
implementing Task 1.3 does **not** need to re-run this check:

- A 3-optional-field `RolesAndResponsibilities`-shaped container
  (`support`/`consulted`/`informed`, each `Optional[X]` where
  `X.items: list[MarkdownListItem] | None = None`) parses correctly in
  every combination tested: heading absent entirely (`X is None`);
  heading present with zero items, both mid-section (immediately followed
  by a sibling H3) and at end-of-section (`X is not None`,
  `X.items is None` — the two states are distinguishable); heading
  present with N items (`X.items` populated); and multiple optional H3s
  independently in any of these three states within the same container in
  one document.
- The mandatory-once-container-is-present shape
  (`Responsible.items: list[MarkdownListItem] = Field(min_length=1)`)
  raises `AssertionError` on an empty body, as expected, with no custom
  validator needed.
- No `models/md` engine changes were required to exercise any of the
  above; the shape works with plain `MarkdownSection2`/`MarkdownSection3`
  subclasses exactly as this Design Notes section describes.

**Frontmatter**: `SopFrontmatter(MarkdownFrontmatter)` — `type: Literal["sop"] = "sop"`; closed status set `frozenset({"draft", "review", "approved", "active", "retired"})`, default `"draft"`, GOL/DEC's
error-message pattern. Semantics: `draft` = being written; `review` =
under review by the responsible authority; `approved` = signed off;
`active` = currently in force, staff must follow it; `retired` = no
longer in force, kept for reference. (`approved` and `active` are kept
distinct per explicit user decision — this system does not model an
effective-date/rollout gap, so the transition from `approved` to
`active` is a manual `set_status` call, not automatic.)

**Document/parser/summary**: `SopDocument(BaseModel)` (`frontmatter: SopFrontmatter`, `body: Sop`); `parse_sop(text)` is the 4-line glue
(`frontmatter.loads` → `_stringify_metadata` →
`Sop.from_text(format_text(post.content))`) exactly like `parse_dec`;
`SopSummary(DocSummary)` plain (id/title/status/ref, no extras).

**Error channels** (codebase convention, no new exception types):
structural → engine `AssertionError`; value → `pydantic.ValidationError`.

**Tools** (one module per tool, mirror `gol/tools/`/`dec/tools/`, minus
the two mutation tools per REQ-004): `create_sop` (fresh `uuid4`,
`status="draft"` always, `created`/`updated`=now, `version= CURRENT_SCHEMA_VERSION`, filename `sop-{id}-{slugify(body.text)}.md`);
`parse_sop(path)`; `list_sop(max_results?, offset?)` (paged, inline
`SopSummary`, skip-on-parse-failure); `get_sop(id, raw=False)`;
`get_sop_example()`/`get_sop_template()` (`read_packaged_text`);
`delete_sop(id)` stub (`NotImplementedError`, `structured_output=False`);
`validate_sop(content, full=False)`. Private helpers `_paths.py` (over
`general.tools._doc_paths`, `SOP_TYPE_NAME = "sop"`, `SopNotFoundError`),
`_io.py`, `_lock.py`, `_write.py` — identical shape to GOL/DEC's.

**Generic-tool dispatch** (REQ-007): `general/tools/update.py` gains
`_update_sop` (verbatim-port shape identical to `_update_dec`, using
`sop_lock`/`load_by_id`/`write_sop_file`/`SopNotFoundError`, plus the
range branch) and a `"sop"` entry in `_ADAPTERS`; the `type` parameter's
`Literal[...]` gains `"sop"`. `general/tools/set_status.py` gains
`_set_status_sop` (same shape as `_set_status_dec`, asserting
`superseded_by is None`) and a `"sop"` entry in `_ADAPTERS`; `type`'s
`Literal[...]` gains `"sop"`. Both modules' imports gain the `sop.*`
equivalents of the `dec.*` imports they already have for `dec`.

**Resources**: `specmgr://sop/schema` (JSON from packaged
`sop/data/sop_schema.json`), `specmgr://sop/example`,
`specmgr://sop/template` — identical to GOL/DEC's three; no `/{id}`, no
`/list`. `sop`'s own resource count stays at three — RASCI guidance is
**not** a fourth `sop` resource (see REQ-011): `specmgr://rasci` lives
under `general/resources/` instead, since RASCI (like ISO/IEC 25010) is a
well-known external framework, not coupled to any one domain's schema,
following `specmgr://iso25010`'s cross-cutting placement precedent rather
than `rsk/tara`'s domain-scoped one (whose guidance text is inseparable
from RSK's own `## Strategy`/`## Mitigation` vocabulary). The split is
deliberately non-duplicative: `general/data/general_rasci.md` holds only
the five roles' generic definitions; every `sop`-specific structural rule
(which heading maps to which role, `Accountable`'s single-paragraph
shape, `Support`/`Consulted`/`Informed`'s present-but-possibly-empty
cardinality) stays exclusively in `sop`'s own schema field docstrings
(surfaced via `specmgr://sop/schema`) and packaged instructions — never
copied into `general_rasci.md`. Discoverability from `sop` is by
cross-reference only, at four points: the six `RolesAndResponsibilities`-
family class docstrings in `sop/models/v1/body.py` (Task 1.3),
`create_sop`/`update_sop`'s packaged instructions (Task 3.3),
`sop/__init__.py`'s own module docstring (Task 3.5), and `server.py`'s
module docstring, in both its `general` resources paragraph and its
`sop` paragraph (Task 5.1).

**Prompts**: `create_sop(topic)` and `update_sop(id, instructions=None)`
reading packaged `sop/data/sop_{create,update}_instructions.md` via
`string.Template` (standard "(not given — ask the user before making any
change)" fallback for `instructions`); mirror GOL/DEC. `update_sop`'s
narration must mention the generic `update`/`set_status` tools by name
(`type="sop"`), since `sop` has no per-domain mutation tools of its own.

**Packaged data**: `sop_example.md` — a worked "New Employee IT Account
Provisioning" procedure exercising every section (RASCI with `Support`
deliberately empty to demonstrate that shape, `Consulted`/`Informed`
populated; 5 numbered `Step`s; all 5 `Related Artifacts` sub-lists
including `Sops`; one `## Updates` entry with a well-formed ISO8601
timestamp); must parse. `sop_template.md` — all-sections placeholder
skeleton, `status: draft`, must round-trip through `parse_sop` (RSK/DEC
precedent).

**Cross-cutting wiring**:

- `server.py`: add `sop` to the final import line (`from . import adr, dec, general, gol, prb, qa, req, rsk, sop, tsk, uc`) + module docstring
  (3 resources, 8 tools, 2 prompts, domain summary, explicit note that
  `sop` has no per-domain mutation tools); also list the new cross-cutting
  `specmgr://rasci` resource under `general` and cross-reference it from
  the `sop` paragraph (REQ-011).
- `general/`: new `general/resources/rasci.py` (`specmgr://rasci`) +
  packaged `general/data/general_rasci.md` (REQ-011) — motivated by
  `sop` but not scoped to it; see Design Notes' Resources section for the
  full generic/domain-specific split rationale.
- `commands/schema.py`: `generate_sop_schema()` (mirror
  `generate_dec_schema`) + `_GENERATORS["sop"]`.
- `pyproject.toml`: `"biz.dfch.specmgr.sop" = ["data/*.md", "data/*.json"]` under `[tool.setuptools.package-data]`.
- `.pre-commit-config.yaml`: add `sop/models/v1` to the 9 existing
  `files:` globs (`specmgr-schema` + the 8 per-domain
  `specmgr-schema-*-package` hooks) + new `specmgr-schema-sop-package`
  hook (`--type sop --output-dir src/biz/dfch/specmgr/sop/data`).
- `.github/workflows/ci.yml`: one new step for
  `src/biz/dfch/specmgr/sop/data/sop_schema.json` mirroring the per-type
  packaged-copy steps (the all-types `docs/*_schema.json` step picks
  `sop` up automatically once registered in `_GENERATORS`).
- `AGENTS.md`: `sop/` bullet in the Status section (after `dec/`); add
  `sop` to the "each register `tools`, `resources`, and `prompts`"
  enumeration and to the `delete_*` stub list; explicit note that `sop`
  is the first domain with no per-domain `update_<d>`/`set_status_<d>`
  tools at all, dispatching straight into the generic tools per ADR
  36905d5b; verify no other enumeration goes stale.
- Root `README.md`: add `Standard Operating Procedure (SOP)` to the "At
  this time, we have these artifact:" list, matching the existing entry
  style.
- Regenerate: `docs/MCP.md` (`specmgr mcp-docs`), `docs/GENERATED.md` +
  `docs/api/` (`specmgr docs`), `docs/sop_schema.json` (`specmgr schema`).

**Precedents to copy** (do not re-derive): GOL/DEC = simple surface +
`RelatedArtifacts` shape + frontmatter status pattern + packaged-data/
resource/prompt shapes; TSK = `Updates`/`UpdateEntry` container shape;
DEC's `Option` = computed-fields-from-regex-heading pattern (reused for
`Step` and `UpdateEntry`); DEC Phase 8 (the `dec` per-domain-to-generic
tool conversion, `.specmgr/feat/feat-22-consolidate-mutation-tools/ README.md`) = the exact shape `_update_sop`/`_set_status_sop` must take,
except built directly rather than via a later conversion.

**Commit discipline (binding for every phase)**: each phase ends with one
commit (conventional-commit style, scope `sop`, e.g. `feat(sop): add models and parser`). Include any hook-regenerated `docs/` files in the
same commit (the `specmgr docs`/`mcp-docs` pre-commit hooks trigger on
`src/` changes and regenerate `docs/GENERATED.md`+`docs/api/` by
filesystem scan — from Phase 1 on, `sop` modules will appear there before
`server.py` registers the domain; that is expected and correct, same as
every prior domain's build history).

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model
  (`MarkdownFrontmatter`)
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: No `/{id}` resources for
  id-based reads (tool-only, `get_sop`)
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Paged `list_<domain>` tool
  instead of a `/list` resource — must be followed from the start
- 36905d5b-8057-4294-8665-c7eed5534db0: Generic `update`/`set_status`
  dispatch tools — `sop` has no per-domain mutation tools at all, the
  first domain to be built this way from day one

No new ADR is anticipated for this feature — every schema/tooling
decision either follows an existing ADR's precedent directly or is
scoped enough to log only in this file's own Decisions Made.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end task (tests, full
quality gate, README Progress update).

#### Phase 0: Scaffolding

- [x] Task 0.1: Package skeleton — `sop/__init__.py` (`from . import prompts, resources, tools` + registration docstring), empty
  `sop/models/v1/`, `sop/tools/`, `sop/resources/`, `sop/prompts/`,
  `sop/data/` packages, and `tests/sop/` skeleton mirroring `tests/dec/`
  (`models/v1/`, `tools/`, `prompts/`, `resources/` + `__init__.py`
  files) — depends on: none — status: done
- [ ] Task 0.2: Commit Phase 0 — depends on: Task 0.1 — status:
  not-started

#### Phase 1: Models + parser (`sop/models/v1/`)

- [x] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends
  on: Task 0.1 — status: done
- [x] Task 1.2: `frontmatter.py` — `SopFrontmatter(MarkdownFrontmatter)`:
  `type: Literal["sop"] = "sop"`, closed 5-set status validator — depends
  on: Task 1.1 — status: done
- [x] Task 1.3: `body.py` — all section classes per Design Notes:
  `Sop` (root + duplicate-step-number after-validator), `Purpose`,
  `Scope`, `Definitions`, `MoreInformation` (leaves),
  `SafetyAndPrecautions` (LITERAL alias leaf), `RolesAndResponsibilities`
  - `Accountable` (single `MarkdownParagraph`) + `Responsible` (mandatory
    list) + `Support`/`Consulted`/`Informed` (optional, MAY-be-empty
    lists), `Procedure` + `Step` (REGEX heading, computed `number`/`name`),
    `RelatedArtifacts` + 5 H3 list children (GOL shape + `Sops`),
    `Updates` + `UpdateEntry` (ISO8601 REGEX heading, computed
    `timestamp`/`title`) — the `Support`/`Consulted`/`Informed`
    present-with-zero-items shape is pre-verified live against the engine
    (see Design Notes' 2026-08-30 re-verification); no exploratory
    re-check needed before implementing, proceed directly to writing the
    classes. `RolesAndResponsibilities`, `Accountable`, `Responsible`,
    `Support`, `Consulted`, and `Informed`'s class docstrings must each
    include a one-line pointer ("See the general `specmgr://rasci`
    resource for RASCI role definitions.") — this is the primary
    `sop`-domain discoverability path for REQ-011's new
    `specmgr://rasci` resource, since these docstrings flow directly into
  `specmgr://sop/schema`'s generated JSON field descriptions — depends
  on: Task 1.2 — status: done
- [x] Task 1.4: `document.py` (`SopDocument`), `parser.py` (`parse_sop`
  glue + `_stringify_metadata`), `summary.py` (`SopSummary`),
  `models/v1/__init__.py` + `models/__init__.py` exports — depends on:
  Task 1.3 — status: done
- [x] Task 1.5: Tests `tests/sop/models/v1/` — `test_frontmatter.py`,
  `test_body.py` (alias acceptance/rejection, RASCI mandatory-vs-optional
  matrix incl. the three-way `Support`/`Consulted`/`Informed` states
  (absent / present-empty / present-with-N-items), `Accountable` rejects
  a bullet list, `Responsible` rejects an empty body, `Step` regex incl.
  leading-zero acceptance + title-required rejection + number uniqueness,
  `Procedure` container-with-zero-steps rejection, `Related Artifacts`
  sub-list independence incl. `Sops`, `UpdateEntry` heading regex
  acceptance/rejection matrix, misordering), `test_parser.py` (ACC-001/
  ACC-002 matrix + round-trip) — depends on: Task 1.4 — status:
  done
- [ ] Task 1.6: Phase-end quality gate (ruff format/check, vulture, full
  unittest) + commit; update this README's Progress section — depends
  on: Task 1.5 — status: not-started

#### Phase 2: Tools (`sop/tools/`) + generic-tool dispatch

- [x] Task 2.1: Private helpers `_paths.py` (`SOP_TYPE_NAME="sop"`,
  `SopNotFoundError`, wrappers over `general.tools._doc_paths`),
  `_io.py` (`read_sop`, `load_by_id`), `_lock.py` (`sop_lock`),
  `_write.py` (`write_sop_file`) — mirror GOL/DEC — depends on: Task 1.6
  — status: done
- [x] Task 2.2: The 8 tool modules + `tools/__init__.py` per Design Notes
  (`create_sop` fixes `status="draft"`, filename `sop-{id}-{slug}.md`;
  `delete_sop` stub `structured_output=False`) — depends on: Task 2.1 —
  status: done
- [x] Task 2.3: `general/tools/update.py` — add `_update_sop` adapter
  (verbatim-shape port of `_update_dec`) + `"sop"` in `_ADAPTERS` +
  `"sop"` in the `type` `Literal[...]` + import wiring; same for
  `general/tools/set_status.py` (`_set_status_sop`) — depends on: Task
  2.1 — status: done
- [x] Task 2.4: Tests `tests/sop/tools/` — one module per tool + helper
  tests + `test_integration.py` (ACC-003, using the generic `update`/
  `set_status` tools with `type="sop"`, not per-domain tools); new test
  cases in `tests/general/tools/test_update.py`/`test_set_status.py`
  covering `type="sop"` (ACC-006) — depends on: Task 2.2, Task 2.3 —
  status: done
- [ ] Task 2.5: Phase-end quality gate + commit; update this README's
  Progress section — depends on: Task 2.4 — status: not-started

#### Phase 3: Resources + packaged data + schema

- [x] Task 3.1: `sop/data/sop_example.md` — worked "New Employee IT
  Account Provisioning" procedure exercising every section per Design
  Notes; must parse — depends on: Task 2.5 — status: done
- [x] Task 3.2: `sop/data/sop_template.md` — all-sections placeholder
  skeleton, `status: draft`; must round-trip through `parse_sop` —
  depends on: Task 2.5 — status: done
- [x] Task 3.3: `sop/data/sop_create_instructions.md` +
  `sop_update_instructions.md` (narrated flows, `$topic`/`$id`/
  `$instructions` placeholders; `update` flow explicitly names the
  generic `update`/`set_status` tools with `type="sop"`); both must
  include an explicit step, before filling in
  `## Roles and Responsibilities`, telling the caller to read
  `specmgr://rasci` for the generic role definitions (REQ-011's
  discoverability requirement) — depends on: Task 2.5 — status:
  done
- [x] Task 3.4: `general/data/general_rasci.md` — new packaged data file,
  generic RASCI (Responsible/Accountable/Support/Consulted/Informed)
  guidance: what RASCI is, the five roles' standard definitions, RASCI vs.
  plain RACI. Deliberately **no** `sop`-specific heading names or
  cardinality rules (those stay in `sop`'s own schema/instructions, see
  Task 1.3/Task 3.3) — depends on: Task 2.5 — status: done
- [x] Task 3.5: `general/resources/rasci.py` — new cross-cutting resource
  (REQ-011), mirroring `rsk/resources/tara.py`'s shape exactly:
  `@mcp.resource("specmgr://rasci", name="rasci", title="RASCI
  Responsibility Assignment Guidance", ..., mime_type="text/markdown")`
  returning `read_packaged_text("general", "rasci")` verbatim (raw
  passthrough, not structurally parsed like `iso25010`); register in
  `general/resources/__init__.py` (import/`__all__`/docstring) and
  `general/__init__.py`'s module docstring. Also add a one-line
  cross-reference note to `sop/__init__.py`'s own module docstring
  (`sop` relies on the cross-cutting `specmgr://rasci` resource for
  role definitions, not a domain-local one) — the fourth and last of
  REQ-011's discoverability touchpoints (the other three: Task 1.3's
  body-model docstrings, Task 3.3's packaged instructions, Task 5.1's
  `server.py` docstring) — depends on: Task 3.4 — status: done
- [x] Task 3.6: `commands/schema.py` — `generate_sop_schema()` +
  `_GENERATORS["sop"]` (mirror `generate_dec_schema`); run `specmgr schema --type sop` (writes `docs/sop_schema.json`) and `specmgr schema --type sop --output-dir src/biz/dfch/specmgr/sop/data` (packaged copy)
  — depends on: Task 2.5 — status: done
- [x] Task 3.7: `sop/resources/` — `sop_schema.py` (`specmgr://sop/schema`,
  JSON from packaged copy), `sop_example.py`, `sop_template.py`,
  `__init__.py` — still exactly three `sop` resources, no `rasci.py` here
  (see Task 3.5) — depends on: Task 3.1, Task 3.2, Task 3.6 — status:
  done
- [x] Task 3.8: `tests/general/resources/test_rasci.py` (ACC-010) —
  mirroring `tests/rsk/resources/test_tara.py`'s shape minus the
  drift-guard test (real-content assertions, fresh-read-per-call,
  `FileNotFoundError` on a missing packaged file) — depends on: Task 3.5
  — status: done
- [x] Task 3.9: Tests `tests/sop/resources/` (ACC-004) — depends on:
  Task 3.7 — status: done
- [ ] Task 3.10: Phase-end quality gate + commit; update this README's
  Progress section — depends on: Task 3.8, Task 3.9 — status: not-started

#### Phase 4: Prompts

- [x] Task 4.1: `sop/prompts/` — `create_sop.py` (`create_sop(topic)`),
  `update_sop.py` (`update_sop(id, instructions=None)` with standard
  fallback), `__init__.py` — depends on: Task 3.3 — status: done
- [x] Task 4.2: Tests `tests/sop/prompts/` (ACC-005) — depends on: Task
  4.1 — status: done
- [ ] Task 4.3: Phase-end quality gate + commit; update this README's
  Progress section — depends on: Task 4.2 — status: not-started

#### Phase 5: Cross-cutting registration

- [x] Task 5.1: `server.py` — add `sop` to the final import line
  (`adr, dec, general, gol, prb, qa, req, rsk, sop, tsk, uc`) + module
  docstring (3 resources, 8 tools, 2 prompts, domain summary, no
  per-domain mutation tools note). Also insert `sop` into the docstring's
  existing `ac`-reservation enumeration sentence ("... adr, uc, req, tsk,
  qa, prb, gol, rsk, dec, and later ac" → add `sop` before "and later
  ac") — confirmed via exploration (2026-08-30) to be the one enumeration
  sentence this task would otherwise leave stale. Also (REQ-011): list
  `specmgr://rasci` once under the `general` resources paragraph, and add
  a one-line cross-reference to it in the `sop` paragraph itself ("role
  definitions: see general `specmgr://rasci`") so an agent scanning only
  the `sop` paragraph still finds it — depends on: Task 4.3, Task 3.10 —
  status: done
- [x] Task 5.2: `pyproject.toml` — `"biz.dfch.specmgr.sop" = ["data/*.md", "data/*.json"]` package-data entry — depends on: Task 3.10
  — status: done
- [x] Task 5.3: `.pre-commit-config.yaml` — add `sop/models/v1` to the 9
  existing `files:` globs + new `specmgr-schema-sop-package` hook —
  depends on: Task 3.6 — status: done
- [x] Task 5.4: `.github/workflows/ci.yml` — new packaged-copy drift
  step for `sop/data/sop_schema.json` — depends on: Task 3.6 — status:
  done
- [x] Task 5.5: `AGENTS.md` — `sop/` bullet in Status (after `dec/`);
  `sop` added to the tools/resources/prompts enumeration and the
  `delete_*` stub list; note on `sop`'s dispatch-only tool surface;
  verify no other enumeration goes stale — depends on: Task 5.1 —
  status: done
- [x] Task 5.6: Root `README.md` — add `Standard Operating Procedure (SOP)` to the "At this time, we have these artifact:" list — depends
  on: Task 5.1 — status: done
- [x] Task 5.7: Regenerate `docs/MCP.md` (`specmgr mcp-docs`),
  `docs/GENERATED.md` + `docs/api/` (`specmgr docs`); verify all
  idempotent on a second run (ACC-008) — depends on: Task 5.1, Task 5.2
  — status: done
- [x] Task 5.8: Final quality gate (ruff format/check, vulture, full
  unittest, `specmgr unused-code`) + commit — depends on: Task 5.7 —
  status: done
- [x] Task 5.9: Final verification pass — walk every ACC-001..010 with
  concrete evidence (including a live `create_sop`→`get_sop`→
  `list_sop`→`update`(type=sop)→`set_status`(type=sop)→`validate_sop`
  run, not just unit tests); update this README's Progress section; set
  feature status to `done` — depends on: Task 5.8 — status: done

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what
was originally planned, rather than keeping a second copy of the task
around.

## Progress

### Current Status

**As of 2026-08-31**: Feature complete — all phases done. Every
ACC-001..010 verified with concrete evidence. Phase 5 (cross-cutting
registration) wired `sop` into `server.py` (import line + full module
docstring: 3 resources, 8 tools, 2 prompts, dispatch-only note, REQ-011
`specmgr://rasci` cross-reference), `pyproject.toml` (package-data
entry), `.pre-commit-config.yaml` (9 glob updates + new
`specmgr-schema-sop-package` hook), `.github/workflows/ci.yml` (new
packaged-schema-copy drift step), `AGENTS.md` (`sop/` bullet +
enumerations), and root `README.md` (artifact list). All doc generation
is drift-free and idempotent (`specmgr mcp-docs`/`docs`/`schema`/
`adr-toc` all no-op on second run). Full quality gate green: ruff
format/check, vulture, `specmgr unused-code`, 2259-test unittest suite,
server import. ACC-003 live round-trip
(`create_sop`→`get_sop`→`list_sop`→`update(type="sop")`→
`set_status(type="sop")`→`validate_sop`→`delete_sop`) and ACC-007
non-editable wheel install both pass. Feature status set to `done`.

**As of 2026-08-30**: Phase 4 (prompts) complete. The `sop` domain now
ships its 2 MCP prompts under `sop/prompts/` (`create_sop.py`/
`update_sop.py`/`__init__.py`, mirroring `dec/prompts/` file-for-file --
the Phase-0 empty `prompts/__init__.py` marker was overwritten with the
real side-effect-registration imports). `create_sop(topic)` reads the
packaged `sop/data/sop_create_instructions.md` via `string.Template`
(`$topic` placeholder) and returns narrated instructional text covering
the `list_sop` dedup-check-first step, the `specmgr://rasci` read-first
step before `## Roles and Responsibilities`, the
`specmgr://sop/template`/`/example`/`/schema` starting-point resources,
the `TodoWrite`/`question`-tool interview flow, and the
`create_sop(content)`/`validate_sop(content, full=False)` tool calls --
it never calls those tools itself. `update_sop(id, instructions=None)`
reads `sop/data/sop_update_instructions.md` via `string.Template`
(`$id`/`$instructions` placeholders, standard
"(not given -- ask the user before making any change)" fallback) and
names the GENERIC `update(id, type="sop", content)`/
`set_status(id, type="sop", status)` tools (both whole-body and
line-range via `get_sop(id, raw=True)`), plus `get_sop(id)`/`validate_sop`
and the `specmgr://rasci` read-first step -- never a per-domain
`update_sop(...)`/`set_status_sop(...)` call shape (`sop` is
dispatch-only, ADR 36905d5b). The 2 prompts are NOT yet registered with
the MCP server -- `server.py` does not import `sop` until Phase 5.

Tests: 22 new tests across `tests/sop/prompts/test_create_sop.py` (11)
and `tests/sop/prompts/test_update_sop.py` (11), mirroring
`tests/dec/prompts/`'s shape -- string-content/ordering assertions on
the narrated text (the prompts only return text, never call tools),
plus the packaged-data-file fresh-read-per-call and `FileNotFoundError`
behavioral tests. The full quality gate is green: ruff format/check,
vulture (clean, no whitelist changes -- the prompt functions are
imported by `sop/prompts/__init__.py`, referenced within `src/`),
`specmgr unused-code` (clean), and the 2259-test unittest suite. Task
4.3 (commit) is pending the orchestrator. Next: Phase 5 (cross-cutting
registration).

**As of 2026-08-30**: Phase 3 (resources + packaged data + schema)
complete. The `sop` domain now ships its 3 MCP resources under
`sop/resources/` (`sop_schema.py`/`sop_example.py`/`sop_template.py`,
mirroring `dec/resources/` file-for-file -- `specmgr://sop/schema`
reads the packaged JSON, `specmgr://sop/example` and
`specmgr://sop/template` are raw-markdown passthroughs; no `/{id}`, no
`/list`) and its four packaged data files under `sop/data/`
(`sop_example.md` -- a worked "New Employee IT Account Provisioning"
procedure exercising every section, including a deliberately-empty
`### Support` to demonstrate the present-with-zero-items shape, 5
`### Step N` entries, all 5 `## Related Artifacts` sub-lists incl.
`### Sops`, and one ISO8601-timestamped `## Updates` entry with the
em-dash separator; `sop_template.md` -- an all-sections placeholder
skeleton, `status: draft`, every RASCI sub-list populated so it
round-trips through `parse_sop`; `sop_create_instructions.md`/
`sop_update_instructions.md` -- narrated `string.Template` flows with
the `$topic`/`$id`/`$instructions` placeholders, the `list_sop`
dedup-check-first step, the explicit `specmgr://rasci` read-first step
before `## Roles and Responsibilities`, and the generic
`update`/`set_status` tools named with `type="sop"`). Both
`sop_example.md` and `sop_template.md` parse via `parse_sop`.
`commands/schema.py` gained `generate_sop_schema()` (mirror of
`generate_dec_schema`) and a `"sop"` entry in `_GENERATORS`; both
`docs/sop_schema.json` and the packaged
`sop/data/sop_schema.json` were generated and are byte-identical. The
Phase-0 `sop/data/.gitkeep` was removed (real data files now exist).

REQ-011's cross-cutting `specmgr://rasci` resource is now **live**:
`general/data/general_rasci.md` (generic RASCI role definitions --
deliberately no `sop`-specific headings/cardinality, verified by a
genericness assertion) and `general/resources/rasci.py` (raw-markdown
passthrough mirroring `rsk/resources/tara.py`) are registered via
`general/resources/__init__.py` (which `server.py` already imports), so
`specmgr://rasci` is reachable now even though `server.py` does not yet
import `sop` (Phase 5). The fourth and last REQ-011 discoverability
touchpoint -- the one-line cross-reference in `sop/__init__.py`'s module
docstring -- is in place (the other three: the six body-model
docstrings from Phase 1, the create/update instructions from Task 3.3,
and `server.py`'s docstring in Phase 5). `general/__init__.py`'s
resources enumeration now lists `rasci` alongside `version`/`iso25010`.

Tests: 24 new tests across `tests/general/resources/test_rasci.py`
(ACC-010: real-content assertions, a dedicated genericness assertion,
fresh-read-per-call, `FileNotFoundError`) and `tests/sop/resources/`
(`test_sop_schema.py`/`test_sop_example.py`/`test_sop_template.py`,
ACC-004: schema equals fresh `generate_sop_schema()`, example/template
equal the packaged files byte-for-byte, example parses and exercises
every section incl. the empty `### Support`, template round-trips
through `parse_sop`), plus the two deferred real-content tool tests
(`test_returns_real_packaged_example`/`test_returns_real_packaged_template`
in `tests/sop/tools/test_get_sop_example.py`/`test_get_sop_template.py`,
deferred from Phase 2 now that the packaged data files exist). The full
quality gate is green: ruff format/check, vulture (clean, no whitelist
changes), `specmgr unused-code` (clean), and the 2237-test unittest
suite. Task 3.10 (commit) is pending the orchestrator. Next: Phase 4
(prompts).

**As of 2026-08-30**: Phase 2 (tools + generic-tool dispatch) complete.
The `sop` domain now ships its full 8-tool MCP surface under
`sop/tools/` (`create_sop`, `parse_sop`, `list_sop` (paged from day one),
`get_sop(id, raw=False)`, `get_sop_example`, `get_sop_template`,
`delete_sop` (stub, `structured_output=False`), `validate_sop`) plus the
private `_paths`/`_io`/`_lock`/`_write` helpers, all mirroring `dec/tools/`
file-for-file. `sop` is the first domain built **dispatch-only** from day
one (ADR 36905d5b): it has no per-domain `update_sop`/`set_status_sop`
tools -- whole-body/line-range updates and status changes go through the
generic `update`/`set_status` tools in `general/tools/` with `type="sop"`.
Both generic tools gained a `_update_sop`/`_set_status_sop` adapter (verbatim
shape ports of `_update_dec`/`_set_status_dec`), a `"sop"` entry in their
`_ADAPTERS` dispatch tables, and `"sop"` in their `type: Literal[...]`
unions (`update` is now `Literal[...rsk, dec, sop]`; `set_status` is now
`Literal[...rsk, dec, sop, adr]`). The 62-test `tests/sop/tools/` suite
mirrors `tests/dec/tools/` file-for-file (including the ACC-003
`test_integration.py` round-trip that drives the GENERIC `update`/
`set_status` tools with `type="sop"`, both whole-body and line-range), plus
new `type="sop"` cases added to `tests/general/tools/test_update.py`/
`test_set_status.py` (ACC-006). `get_sop_example`/`get_sop_template` are
mock-tested only this phase (the real packaged data files arrive in Phase 3
Task 3.1/3.2, so their `test_returns_real_packaged_*` tests are deferred to
Phase 3). The full quality gate is green: ruff format/check, vulture (clean,
no whitelist changes -- the Phase-1 `# sop` whitelist section still applies),
`specmgr unused-code` (clean), the 2213-test unittest suite, and the fresh
`sop`-tools/dispatch import smoke test. Task 2.5 (commit) is pending the
orchestrator. Next: Phase 3 (resources + packaged data + schema).

**As of 2026-08-30**: Phase 1 (models + parser) complete. The full `sop`
Pydantic schema now lives under `src/biz/dfch/specmgr/sop/models/v1/`
(`_util.py`, `frontmatter.py`, `body.py`, `document.py`, `parser.py`,
`summary.py` + the two `__init__.py` export modules), mirroring `dec`'s file
shapes exactly. `SopFrontmatter` narrows `type` to `Literal["sop"]` and
`status` to the closed five-value approval/effectivity set
(`draft`/`review`/`approved`/`active`/`retired`); `Sop` carries the binding
section order (Purpose -> Scope -> Definitions -> Roles and Responsibilities
-> Safety and Precautions -> Procedure -> Related Artifacts -> More
Information -> Updates), the RASCI composite (mandatory `Accountable`/
`Responsible`, optional `Support`/`Consulted`/`Informed` with the
present-with-zero-items shape), the regex-aliased `Step`/`UpdateEntry`
computed fields (`number`/`name`, `timestamp`/`title`), the `Sops`
self-cross-reference sub-list, and the duplicate-step-number after-validator.
All six RASCI-family class docstrings carry the `specmgr://rasci`
discoverability pointer (REQ-011). The 144-test `tests/sop/models/v1/` suite
(`test_frontmatter.py`/`test_body.py`/`test_parser.py`) covers the full
ACC-001/ACC-002 matrix. The full quality gate is green: ruff format/check,
vulture (clean after adding a `# sop (feat-30 Phase 1)` whitelist section for
10 Pydantic-field/validator false positives), and the 2151-test unittest
suite. Task 1.6 (commit) is pending the orchestrator. Next: Phase 2 (tools +
generic-tool dispatch).

**As of 2026-08-30**: Phase 0 (scaffolding) complete. The `sop` domain
package skeleton and the matching `tests/sop/` skeleton have been created
under `src/biz/dfch/specmgr/sop/` and `tests/sop/`, mirroring `dec`'s
layout exactly. `sop/__init__.py` carries the AGPL copyright header, a
module docstring describing the SOP domain, and
`from . import prompts, resources, tools`; all sub-package `__init__.py`
files are empty markers pending later phases. The full quality gate (ruff
format/check, vulture, 2007-test unittest suite, fresh `sop` import) is
green. Task 0.2 (commit) is pending the orchestrator. Next: Phase 1
(models + parser).

**As of 2026-08-29**: Planning complete. Every schema/design decision was
resolved interactively before any code was written (see Decisions Made
below), including a live, read-only, in-memory verification against the
actual `models/md` engine confirming the "optional heading that MAY be
present with zero list items" shape (used by `Support`/`Consulted`/
`Informed`) parses correctly with no engine changes needed.

### Blockers

None.

### Recent Updates

#### Update 2026-08-31T10:00:00Z (Phase 5 cross-cutting registration + final verification)

- Completed: Tasks 5.1-5.9 -- cross-cutting registration of the `sop`
  domain and final ACC-001..010 verification walk-through. This was the
  final phase; the feature status is now `done`.
- Task 5.1 (`server.py`): added `sop` to the final import line
  (`from . import adr, dec, general, gol, prb, qa, req, rsk, sop, tsk, uc`)
  and updated the module docstring's every domain enumeration
  consistently: (1) Resources section -- added `specmgr://sop/schema`,
  `specmgr://sop/example`, `specmgr://sop/template` entries (mirroring
  DEC's style) and added `specmgr://rasci` under the `general` resources
  (REQ-011); (2) "no /{id} resource" paragraph -- added the SOP sentence
  mirroring DEC's (no `/{id}`, no `/list`, `list_sop` paged tool from day
  one, ADR ec9f5262); (3) Tools section -- added the SOP tools sentence
  (8 tools: `parse_sop`, `get_sop` with `raw=True`, `list_sop`,
  `get_sop_example`, `get_sop_template`, `create_sop`, `delete_sop` stub,
  `validate_sop`) plus the explicit dispatch-only note (NO per-domain
  `update_sop`/`set_status_sop` tools -- generic `update`/`set_status`
  with `type="sop"`, ADR 36905d5b) and the `specmgr://rasci` cross-
  reference; (4) `update` tool description -- "eight" -> "nine whole-body
  domains" + `sop` added to the literal list; (5) `set_status` tool
  description -- "nine" -> "ten domains" + `sop` added before `adr`; (6)
  Prompts section -- added the SOP prompts sentence (`create_sop`/
  `update_sop`, narrated `TodoWrite` + `question`-tool flow, `list_sop`
  dedup check, `specmgr://rasci` read-first step, generic `update`/
  `set_status` with `type="sop"`); (7) `ac`-reservation enumeration
  sentence -- `sop` added before "and later ac"; (8) "existing imports"
  sentence -- `sop` added (alphabetical); (9) "each register tools,
  resources, and prompts" sentence -- `sop` added.
- Task 5.2 (`pyproject.toml`): added
  `"biz.dfch.specmgr.sop" = ["data/*.md", "data/*.json"]` under
  `[tool.setuptools.package-data]`, alphabetically after `rsk` and before
  `tsk`, mirroring the `dec` entry exactly. `general`'s entry
  (`["data/*.md"]` only) was NOT changed -- it already covers
  `general_rasci.md`.
- Task 5.3 (`.pre-commit-config.yaml`): added `sop/models/v1` to the
  `files:` glob of all 9 existing schema hooks (`specmgr-schema` + 8
  `specmgr-schema-*-package` hooks) via `replaceAll`, and added a new
  `specmgr-schema-sop-package` hook mirroring the `dec` package hook
  (`--type sop --output-dir src/biz/dfch/specmgr/sop/data`). Also
  updated the `specmgr-schema` hook's description to list `sop` among the
  registered types.
- Task 5.4 (`.github/workflows/ci.yml`): added a new
  `Make sure src/biz/dfch/specmgr/sop/data/sop_schema.json is correct`
  step mirroring the `dec` step, placed after it, with the matching
  `::error::` message and `if: matrix.python-version == '3.13'`.
- Task 5.5 (`AGENTS.md`): added the `sop/` bullet in the Status section
  (after `dec/`, before `general/`) describing `sop/tools/` (8 tools,
  dispatch-only via generic `update`/`set_status` with `type="sop"`),
  `sop/resources/` (3 resources, no `/{id}`/`/list`), `sop/prompts/`
  (`create_sop`/`update_sop`), `sop/models/v1/`, the explicit dispatch-
  only note (ADR 36905d5b), and the `specmgr://rasci` cross-reference
  (REQ-011). Updated the `general/` bullet's domain counts (eight -> nine
  whole-body, nine -> ten domains, eight -> nine `get_<d>` tools) and
  added `specmgr://rasci` to its resources list. Added `sop` to the
  `validate_*` list, `delete_*` stub list, "each register" enumeration,
  and the MCP server domain-import enumeration. Verified no other
  enumeration went stale (grepped every `dec` occurrence).
- Task 5.6 (root `README.md`): added `Standard Operating Procedure (SOP)`
  to the "At this time, we have these artifact:" list, alphabetically
  after `Requirement (REQ)` and before `Task List (TSK)`.
- Task 5.7 (doc regeneration + idempotency, ACC-008): ran
  `specmgr mcp-docs`, `specmgr docs`, `specmgr schema`, `specmgr adr-toc`.
  First run changed only `docs/api/biz.dfch.specmgr.server.md` (reflecting
  `server.py`'s updated docstring); `docs/MCP.md` was already up-to-date
  with `sop` entries from prior phase commits (confirmed: 38 `sop`
  occurrences at HEAD, regeneration produced no diff). `docs/GENERATED.md`
  unchanged (no new modules). Second run of all four commands produced no
  further changes -- idempotent.
- Task 5.8 (final quality gate): all green.
  - `ruff format --check`: 1285 files already formatted, exit 0.
  - `ruff check`: All checks passed!, exit 0.
  - `vulture src/ whitelist.py --min-confidence 60`: clean, exit 0.
  - `specmgr unused-code`: No unused code found, exit 0.
  - `python -m unittest discover -s tests -t . -p "test_*.py"`: Ran 2259
    tests in 59.544s, OK.
  - `python -c "import biz.dfch.specmgr.server"`: server imports OK; sop
    registered, exit 0.
- Task 5.9 (ACC-001..010 walk-through): every ACC verified with concrete
  evidence (see the full table in the report back to the orchestrator):
  - ACC-001/002: 144 tests in `tests/sop/models/` (structural
    `AssertionError` + value `pydantic.ValidationError` matrices), OK.
  - ACC-003: live round-trip against a temp `SPECMGR_DOCS_DIR`:
    `create_sop` (id, `status="draft"`, `sop-{id}-{slug}.md` filename) ->
    `get_sop` -> `get_sop(raw=True)` (frontmatter-stripped body) ->
    `list_sop` (1 doc) -> `update(type="sop")` (whole-body, `updated`
    bumped, Scope added) -> `set_status(type="sop", "active")` (status
    changed, `updated` bumped, body unchanged) -> `set_status` rejects
    `superseded_by` for `type="sop"` (`ValueError`) -> `validate_sop`
    (True) -> `delete_sop` (`NotImplementedError`). Plus 64 tests in
    `tests/sop/tools/`, OK.
  - ACC-004: 18 tests in `tests/sop/resources/`, OK. `specmgr://sop/schema`
    == fresh `generate_sop_schema()` (True). Example/template resources ==
    packaged files byte-for-byte (True, True).
  - ACC-005: 22 tests in `tests/sop/prompts/`, OK.
  - ACC-006: 28 tests in `tests/general/tools/test_update` +
    `test_set_status`, OK. `set_status` rejects `superseded_by` for
    `type="sop"` (confirmed in live round-trip).
  - ACC-007: `uv build --wheel` succeeded; wheel contains all 6 sop data
    files + `general_rasci.md`. Scratch-venv non-editable install
    (`uv pip install ... [mcp]`) + `read_packaged_text('sop','example')`/
    `('general','rasci')`/`('sop','template')` all resolved correctly
    from the installed (non-editable) package.
  - ACC-008: no drift + idempotent (Task 5.7 evidence above).
  - ACC-009: full gate green (Task 5.8 evidence above).
  - ACC-010: 4 tests in `tests/general/resources/test_rasci`, OK.
    `specmgr://rasci` returns `general_rasci.md` verbatim (True). Content
    is generic (no sop-specific headings -- grep for Step/Procedure/
    Purpose/SOP/Safety/Roles/Accountable/Responsible/Support/Consulted/
    Informed returned no matches). All four discoverability cross-
    references confirmed via grep: (1) six body-model docstrings in
    `sop/models/v1/body.py` (lines 78/95/117/140/163/187); (2)
    `sop/__init__.py` docstring (line 55); (3) `sop_create_instructions.md`
    (line 81) + `sop_update_instructions.md` (line 38); (4) `server.py`
    docstring in both the general resources paragraph (line 94) and the
    sop paragraph (lines 176/179/229).
- Whitelist: no changes. Vulture and `specmgr unused-code` both clean;
  this phase only touched registration/doc files (no new Python symbols).
- Did NOT commit (the orchestrator owns the commit per the phase
  instructions).

#### Update 2026-08-30T20:00:00Z (Phase 4 prompts)

- Completed: Tasks 4.1-4.2 -- implemented the `sop/prompts/` MCP prompt
  surface and the matching tests. Created `sop/prompts/create_sop.py`
  (`@mcp.prompt(name="create_sop", title="Create a standard operating
  procedure", ...)`, `def create_sop(topic: str) -> str:`, body reads
  `sop/data/sop_create_instructions.md` via `string.Template` with the
  `$topic` placeholder), `sop/prompts/update_sop.py`
  (`@mcp.prompt(name="update_sop", title="Update a standard operating
  procedure", ...)`, `def update_sop(id: str, instructions: str | None =
  None) -> str:` with the standard
  "(not given -- ask the user before making any change)" fallback, body
  reads `sop/data/sop_update_instructions.md` via `string.Template` with
  the `$id`/`$instructions` placeholders), and overwrote the Phase-0
  empty `prompts/__init__.py` marker with the real
  `from .create_sop import create_sop` / `from .update_sop import
  update_sop` + `__all__` + module docstring (mirroring
  `dec/prompts/__init__.py`).
- Both prompts mirror `dec/prompts/` file-for-file, adapted to `sop`'s
  dispatch-only surface: `create_sop`'s docstring notes the narration
  covers `list_sop` (dedup check), `specmgr://sop/template`/`/example`/
  `/schema`, `specmgr://rasci` (read before Roles and Responsibilities),
  `create_sop`, `validate_sop`, and that it never calls those tools
  itself. `update_sop`'s docstring notes that `sop` has NO per-domain
  `update_sop`/`set_status_sop` tools -- the narration names the GENERIC
  `update`/`set_status` tools with `type="sop"`, plus
  `get_sop(id)`/`get_sop(id, raw=True)` and `validate_sop`, and the
  `specmgr://rasci` read-first step.
- Tests: 22 new tests. `tests/sop/prompts/test_create_sop.py` (11):
  `test_returns_substituted_instruction_text`,
  `test_instructions_match_packaged_file`,
  `test_mentions_duplicate_check_tool` (`list_sop` -- ACC-005),
  `test_mentions_todowrite_list`, `test_mentions_question_tool`,
  `test_mentions_sop_sections` (`## Purpose`/`## Procedure`/`## Roles and
  Responsibilities`/`## Updates`),
  `test_mentions_rasci_read_first` (`specmgr://rasci` -- REQ-011),
  `test_mentions_starting_point_resources`
  (`specmgr://sop/template`/`/example`/`/schema`),
  `test_mentions_create_and_validate_tools` (`create_sop(content)`/
  `validate_sop(content, full=False)`),
  `test_instructions_loaded_from_packaged_data_file`,
  `test_raises_file_not_found_when_instructions_missing`.
  `tests/sop/prompts/test_update_sop.py` (11):
  `test_returns_substituted_id`,
  `test_instructions_interpolated_when_given`,
  `test_prompts_for_input_when_instructions_absent`,
  `test_instructions_match_packaged_file`,
  `test_mentions_get_sop_tool_first` (ordering: `get_sop(id)` before
  `update(id, type="sop", content)`),
  `test_mentions_both_generic_mutation_tools`
  (`update(id, type="sop", content)` + `set_status(id, type="sop",
  status)`),
  `test_mentions_range_update_flow` (`get_sop(id, raw=True)`,
  1-based inclusive line range, `begin = end = N+1`, `update(id,
  type="sop", content, begin=..., end=...)`, ordering),
  `test_mentions_rasci_read_first`,
  `test_does_not_narrate_per_domain_mutation_tools` (`update_sop(`/
  `set_status_sop(` must NOT appear),
  `test_instructions_loaded_from_packaged_data_file`,
  `test_raises_file_not_found_when_instructions_missing`. All assertion
  phrases verified against the actual Phase-3 instruction files
  (`sop/data/sop_create_instructions.md`/`sop_update_instructions.md`)
  before writing -- the instructions' exact wording is the source of
  truth.
- Whitelist: no changes. Vulture and `specmgr unused-code` both clean;
  the prompt functions are imported by `sop/prompts/__init__.py`
  (referenced within `src/`), so no new false positives arose.
- Quality gate green: `ruff format --check` (1283 files), `ruff check`
  (all passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
  `specmgr unused-code` (No unused code found), full unittest suite (2259
  tests, OK), and the fresh `from biz.dfch.specmgr.sop.prompts import
  create_sop, update_sop` smoke test confirming: `list_sop` in
  create-output = True, `specmgr://rasci` in create-output = True,
  `type="sop"` in update-output = True, `specmgr://rasci` in update-output
  = True, `$id` not in update-output = True, `update_sop(` not in
  update-output = True.
- The 2 `sop` prompts are NOT yet registered with the MCP server --
  `server.py` does not import `sop` until Phase 5 (Task 5.1). That is
  expected; `specmgr mcp-docs` will not show them in `docs/MCP.md` until
  then.
- Next: Phase 5 (cross-cutting registration).

#### Update 2026-08-30T18:00:00Z (Phase 3 resources + data + schema)

- Completed: Tasks 3.1-3.9 -- implemented the `sop` MCP resources, the
  packaged data files, the `generate_sop_schema()` generator, the
  cross-cutting `specmgr://rasci` resource (REQ-011), and the matching
  tests. Created `sop/data/sop_example.md` (worked "New Employee IT
  Account Provisioning" SOP exercising every section, with a
  deliberately-empty `### Support` for the present-with-zero-items shape,
  5 `### Step N` entries, all 5 `## Related Artifacts` sub-lists incl.
  `### Sops`, one ISO8601-em-dash `## Updates` entry; parses via
  `parse_sop`), `sop/data/sop_template.md` (all-sections placeholder
  skeleton, `status: draft`, all RASCI sub-lists populated so it
  round-trips through `parse_sop`), and
  `sop/data/sop_create_instructions.md`/`sop_update_instructions.md`
  (narrated `string.Template` flows with `$topic`/`$id`/`$instructions`,
  the `list_sop` dedup-check-first step, the explicit `specmgr://rasci`
  read-first step before `## Roles and Responsibilities`, and the
  generic `update`/`set_status` tools named with `type="sop"` -- `sop`
  has no per-domain mutation tools).
- REQ-011 (cross-cutting RASCI): created
  `general/data/general_rasci.md` (generic RASCI role definitions --
  what RASCI is, the five roles' standard definitions, RASCI vs. plain
  RACI; deliberately no `sop`-specific heading names or cardinality
  rules, verified by a dedicated genericness assertion) and
  `general/resources/rasci.py` (`specmgr://rasci`, raw-markdown
  passthrough mirroring `rsk/resources/tara.py`). Registered in
  `general/resources/__init__.py` (import/`__all__`/docstring) and
  `general/__init__.py`'s resources enumeration. Added the one-line
  cross-reference to `sop/__init__.py`'s module docstring (the fourth and
  last REQ-011 discoverability touchpoint). `specmgr://rasci` is now
  **live** via `general` (which `server.py` already imports), even
  though `server.py` does not yet import `sop` (Phase 5).
- Schema: `commands/schema.py` gained `generate_sop_schema()` (mirror of
  `generate_dec_schema`) and a `"sop"` entry in `_GENERATORS` (after
  `"rsk"`, before `"tsk"`, alphabetical), plus the `sop.models.v1`
  imports. Ran `specmgr schema --type sop` (writes `docs/sop_schema.json`)
  and `... --output-dir src/biz/dfch/specmgr/sop/data` (packaged copy);
  the two files are byte-identical (`diff` empty). Removed the Phase-0
  `sop/data/.gitkeep` (real data files now exist).
- Resources: `sop/resources/` now carries `sop_schema.py`
  (`specmgr://sop/schema`, JSON from packaged copy),
  `sop_example.py` (`specmgr://sop/example`), `sop_template.py`
  (`specmgr://sop/template`), and `__init__.py` -- exactly 3 `sop`
  resources, no `rasci.py` here (that lives in `general/resources/`).
  The 3 `sop` resources are NOT yet registered with the MCP server --
  `server.py` does not import `sop` until Phase 5.
- Tests: 24 new tests. `tests/general/resources/test_rasci.py` (ACC-010:
  real-content assertions incl. all five role names + "RACI", a
  dedicated `test_content_is_generic_no_sop_specific_rules` method
  asserting no `sop`-specific structural headings, fresh-read-per-call,
  `FileNotFoundError`; no drift-guard test since no Pydantic field
  validates the RASCI vocabulary). `tests/sop/resources/`
  (`test_sop_schema.py`/`test_sop_example.py`/`test_sop_template.py`,
  ACC-004: schema equals fresh `generate_sop_schema()`, example/template
  equal the packaged files byte-for-byte, example parses and exercises
  every section incl. the empty `### Support`, template round-trips
  through `parse_sop`, fresh-read-per-call, `FileNotFoundError`). Plus
  the two deferred real-content tool tests
  (`test_returns_real_packaged_example`/`test_returns_real_packaged_template`)
  added to `tests/sop/tools/test_get_sop_example.py`/
  `test_get_sop_template.py` (deferred from Phase 2 -- the packaged data
  files now exist).
- Whitelist: no changes. Vulture and `specmgr unused-code` both clean;
  the new resource functions are imported by their `__init__.py`
  (referenced within `src/`), and the Phase-1 `# sop (feat-30 Phase 1)`
  whitelist section still applies.
- Quality gate green: `ruff format --check` (1275 files), `ruff check`
  (all passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
  `specmgr unused-code` (No unused code found), full unittest suite (2237
  tests, OK), example+template parse via `parse_sop` confirmed,
  `docs/sop_schema.json`/`sop/data/sop_schema.json` byte-identical, and
  the `rasci` + 3 `sop` resources import smoke test.
- Next: Phase 4 (prompts).

#### Update 2026-08-30T16:00:00Z (Phase 2 tools + dispatch)

- Completed: Tasks 2.1-2.4 -- implemented the `sop/tools/` MCP tool surface
  and the generic-tool dispatch wiring. Created the 4 private helpers
  (`_paths.py` with `SOP_TYPE_NAME="sop"`/`SopNotFoundError`/base-dir +
  id-lookup wrappers over `general.tools._doc_paths`, `_io.py`
  (`read_sop`/`load_by_id`), `_lock.py` (`sop_lock`),
  `_write.py` (`write_sop_file`)), all mirroring `dec/tools/` file-for-file;
  the 8 tool modules (`create_sop` fixing `status="draft"` and writing
  `sop-{id}-{slug}.md`, `parse_sop`, `list_sop` (paged, inline `SopSummary`,
  skip-on-parse-failure), `get_sop(id, raw=False)`, `get_sop_example`,
  `get_sop_template`, `delete_sop` (stub, `structured_output=False`),
  `validate_sop`); and overwrote the Phase-0 empty `tools/__init__.py` with
  the real side-effect-registration imports. NO `update_sop`/
  `set_status_sop` per-domain tools -- `sop` is dispatch-only (ADR
  36905d5b).
- Dispatch wiring: `general/tools/update.py` gained `_update_sop` (verbatim
  shape port of `_update_dec` incl. the range branch), a `"sop"` entry in
  `_ADAPTERS`, `"sop"` in the `type` Literal, `SopDocument` in the
  `_UpdateDocument` union, and the `sop.*` import block; module/function
  docstrings updated eight->nine whole-body. `general/tools/set_status.py`
  gained `_set_status_sop` (incl. the `assert superseded_by is None` guard),
  a `"sop"` entry in `_ADAPTERS` (after `dec`, before `adr`), `"sop"` in the
  `type` Literal, `SopDocument` in the `_SetStatusDocument` union, and the
  `sop.*` import block; docstrings updated nine->ten domains. Final
  Literals: `update` = `Literal["req","uc","tsk","qa","prb","gol","rsk",
  "dec","sop"]`; `set_status` = `Literal["req","uc","tsk","qa","prb","gol",
  "rsk","dec","sop","adr"]`.
- Tests: 62 new tests across `tests/sop/tools/` (helper tests + one module
  per tool + `test_integration.py`), mirroring `tests/dec/tools/`
  file-for-file. `test_integration.py` (ACC-003) drives the GENERIC
  `update`/`set_status` tools with `type="sop"` (both whole-body and
  line-range `begin`/`end`), confirming `create_sop`->`get_sop`->`list_sop`
  ->`update`->`set_status`->`validate_sop`->`delete_sop` round-trip,
  `status="draft"` fixed on create, `sop-{id}-{slug}.md` filename, `updated`
  bumps, `status` changes persist, body carried verbatim through
  `set_status`, and `set_status` rejects `superseded_by` for `type="sop"`.
  New `type="sop"` cases added to `tests/general/tools/test_update.py`
  (whole-body + range + field-error via duplicate `### Step 1` number ->
  `ValidationError`; `TestUpdateRegistration` enum assertion updated to the
  9-value list) and `tests/general/tools/test_set_status.py` (valid/invalid
  status against SOP's closed five-set, `superseded_by` rejection,
  `SopNotFoundError`) -- ACC-006.
- Deferred to Phase 3: `get_sop_example`/`get_sop_template` real-content
  tests (`test_returns_real_packaged_*`) -- the packaged data files
  (`sop/data/sop_example.md`, `sop/data/sop_template.md`) do not exist yet
  (Phase 3 Task 3.1/3.2). Only the two mock-based methods per tool are
  written this phase (delegation to the shared packaged-data reader +
  `FileNotFoundError` on a missing file), exactly mirroring `dec`'s own
  build history.
- Whitelist: no changes. Vulture and `specmgr unused-code` both clean; the
  Phase-1 `# sop (feat-30 Phase 1)` whitelist section still applies (the
  tools/dispatch deal with `SopDocument`/raw text, not body fields as plain
  attributes).
- Quality gate green: `ruff format --check` (1250 files), `ruff check` (all
  passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
  `specmgr unused-code` (No unused code found), full unittest suite (2213
  tests, OK), and the fresh `from biz.dfch.specmgr.sop import tools` +
  `_ADAPTERS`/`SS` `sop`-membership smoke test (`sop tools import OK`,
  `True`, `True`).
- Next: Phase 3 (resources + packaged data + schema).

#### Update 2026-08-30T03:30:00Z (Phase 1 models + parser)

- Completed: Tasks 1.1-1.5 — implemented the `sop/models/v1/` Pydantic
  schema + parser and the `tests/sop/models/v1/` test suite. Created
  `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`), `frontmatter.py`
  (`SopFrontmatter` with the closed five-value status set), `body.py` (all
  section classes: `Sop` root + duplicate-step-number after-validator,
  `Purpose`/`Scope`/`Definitions`/`MoreInformation`/`SafetyAndPrecautions`
  leaves, the RASCI `RolesAndResponsibilities` composite with mandatory
  `Accountable`/`Responsible` and optional present-with-zero-items
  `Support`/`Consulted`/`Informed`, `Procedure`/`Step` with computed
  `number`/`name`, `RelatedArtifacts` + 5 H3 sub-lists incl. the new `Sops`
  self-cross-reference, `Updates`/`UpdateEntry` with the ISO8601-regex
  heading and computed `timestamp`/`title`), `document.py` (`SopDocument`),
  `parser.py` (`parse_sop` + `_stringify_metadata`), `summary.py`
  (`SopSummary`), and overwrote the Phase-0 empty `models/v1/__init__.py` +
  `models/__init__.py` markers with full copyright/docstring/exports
  mirroring `dec`. The six RASCI-family class docstrings each carry the
  `specmgr://rasci` discoverability pointer (REQ-011).
- Tests: 144 new tests across `test_frontmatter.py` (5-value status set,
  `type` discriminator, defaults), `test_body.py` (alias
  acceptance/rejection for every heading class; RASCI mandatory-vs-optional
  matrix incl. the three-way `Support`/`Consulted`/`Informed` states
  tested mid-section and at end-of-section, alone and combined;
  `Accountable`-rejects-bullet-list; `Responsible`-rejects-empty; `Step`
  regex incl. leading-zero acceptance, title-required rejection, gaps, and
  the duplicate-number `ValidationError`; `Procedure` zero-step rejection;
  `RelatedArtifacts` 5-sub-list independence incl. `Sops`;
  `UpdateEntry` ISO8601 heading acceptance/rejection matrix + computed
  `timestamp`/`title`; misordering; second H1; leading content before H1;
  full reference-document round-trip), and `test_parser.py` (ACC-001/
  ACC-002 matrix through `parse_sop` + round-trip + frontmatter-defaults).
- Whitelist: added `_._validate_step_numbers_unique` to the Pydantic
  validator-method section and a new `# sop (feat-30 Phase 1)` section
  listing 9 names (`accountable`/`responsible`/`support`/`sops`/
  `timestamp`/`purpose`/`definitions`/`roles_and_responsibilities`/
  `safety_and_precautions`) — all Pydantic model fields / `@computed_field`s
  read only via (de)serialization, the exact `dec` feat-21 Phase 1
  precedent; the `sop` tools that will access them come in Phase 2.
- Quality gate green: `ruff format --check` (1219 files), `ruff check`
  (all passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
  full unittest suite (2151 tests, OK), and a fresh
  `from biz.dfch.specmgr.sop.models.v1 import SopDocument, parse_sop, Sop,
  SopFrontmatter` import all pass.
- Empirically re-confirmed the Design Notes' pre-verification: the
  `Support`/`Consulted`/`Informed` present-with-zero-items shape parses to
  `items=None` both mid-section and at end-of-section with no engine
  changes, and the `Responsible` mandatory-list empty body raises
  `AssertionError` — exactly as the 2026-08-30 re-verification claimed.
- Next: Phase 2 (tools + generic-tool dispatch).

#### Update 2026-08-30T02:00:00Z (Phase 0 scaffolding)

- Completed: Task 0.1 — created the `sop` domain package skeleton under
  `src/biz/dfch/specmgr/sop/` and the matching test skeleton under
  `tests/sop/`, both mirroring `dec`'s layout exactly. `sop/__init__.py`
  carries the AGPL copyright header, a module docstring describing the
  SOP domain (Standard Operating Procedures; 3 resources, 8 tools, 2
  prompts; first domain with no per-domain `update_sop`/`set_status_sop`
  tools, dispatching straight into the generic `update`/`set_status` tools
  per ADR 36905d5b), and `from . import prompts, resources, tools` +
  `__all__`. The sub-package `__init__.py` files (`models/`, `models/v1/`,
  `tools/`, `resources/`, `prompts/`) are empty markers pending later
  phases (exports come in Phase 1-4); `sop/data/` exists with a `.gitkeep`
  placeholder pending Phase 3's packaged data files (matching `dec/data/`'s
  no-`__init__.py` convention). All six `tests/sop/**/__init__.py` files
  are empty markers (no `test_*.py` files yet). `server.py` was NOT touched
  (Phase 5 Task 5.1); `specmgr://rasci` cross-reference was NOT added to
  `sop/__init__.py` (Task 3.5).
- Quality gate green: `ruff format --check` (1204 files formatted), `ruff
  check` (all checks passed), `vulture src/ whitelist.py --min-confidence
  60` (clean), full unittest suite (2007 tests, OK), and a fresh
  `from biz.dfch.specmgr import sop` import all pass.
- Note: `sop/data/` uses a `.gitkeep` placeholder (the plan permitted "an
  empty placeholder or just the directory") so the empty directory is
  git-trackable until Phase 3 adds real `.md`/`.json` data files;
  `dec/data/` has no such placeholder because it already ships real data
  files.
- Next: Phase 1 (models + parser).

#### Update 2026-08-30T01:00:00Z (RASCI resource promoted to general)

- Decided and planned: the RASCI role-definitions guidance is now a
  cross-cutting `specmgr://rasci` resource (`general/resources/rasci.py`,
  packaged `general/data/general_rasci.md`) — new REQ-011/ACC-010 —
  rather than a `sop`-scoped `specmgr://sop/rasci` resource as first
  proposed. Rationale: RASCI, like ISO/IEC 25010, is a well-known
  external framework, not coupled to any one domain's schema, so it
  follows `specmgr://iso25010`'s cross-cutting placement rather than
  `rsk/tara`'s domain-scoped one. `sop`'s own resource count is
  unaffected (stays at three: `schema`/`example`/`template`).
- Split content deliberately, non-duplicatively: `general_rasci.md` holds
  only the five roles' generic definitions; every `sop`-specific
  structural rule (heading names, `Accountable`'s single-paragraph
  shape, the present-but-possibly-empty `Support`/`Consulted`/`Informed`
  cardinality) stays exclusively in `sop`'s own schema field docstrings
  and packaged instructions.
- Planned four discoverability touchpoints so an agent working the `sop`
  domain reliably finds the resource despite it living outside `sop/`:
  (1) the six `RolesAndResponsibilities`-family class docstrings in
  `sop/models/v1/body.py` (Task 1.3, flows into `specmgr://sop/schema`'s
  generated field descriptions), (2) `create_sop`/`update_sop`'s packaged
  instructions (Task 3.3, explicit "read `specmgr://rasci` first" step),
  (3) `sop/__init__.py`'s own module docstring (Task 3.5), and (4)
  `server.py`'s module docstring in both its `general` and `sop`
  paragraphs (Task 5.1).
- Renumbered Phase 3's task list to insert the two new tasks (Task 3.4
  `general_rasci.md`, Task 3.5 `general/resources/rasci.py`) and their
  test task (Task 3.8); fixed the three downstream dependency references
  to the old Task 3.4 (`commands/schema.py`, now Task 3.6) in Task 5.2/
  5.3/5.4.

#### Update 2026-08-30T00:00:00Z (pre-implementation plan review)

- Completed: Independent plan-review pass before starting Phase 0 —
  cross-checked every precedent this plan cites (`dec`/`gol` directory
  shapes, `Option` regex-computed-field pattern, `general/tools/update.py`/
  `set_status.py` `_ADAPTERS` dispatch shape, `commands/schema.py`
  `_GENERATORS` pattern, `.pre-commit-config.yaml` hook globs,
  `pyproject.toml` package-data format, `server.py`'s import line) against
  the actual current code — all matched exactly, no discrepancies found
  beyond the two below.
- Completed: Live, in-memory, read-only re-verification (no files written)
  of the `Support`/`Consulted`/`Informed` "present-with-zero-items"
  optional-list shape against the real `models/md` engine, since it has no
  precedent elsewhere in the codebase — every tested combination (heading
  absent / present-empty mid-section / present-empty end-of-section /
  present-with-N-items, plus the mandatory `Responsible` empty-body
  rejection) passed exactly as Design Notes claims. Result recorded
  directly in Design Notes so Task 1.3 does not need to repeat this check.
- Found and fixed: `server.py`'s module docstring already carries an
  `"... and later ac"` domain-enumeration sentence that Task 5.1's original
  wording would not have updated for `sop` — Task 5.1 now explicitly calls
  this out.
- Filed: a new cross-cutting follow-up, `feat-7-various-improvements` Task
  0.30 ("Consolidate 'Recent Updates' and 'Updates' across artifact
  types"), since `sop`'s new ISO8601-enforced `## Updates` heading shape
  is a third divergent variant alongside `tsk`'s `## Recent Updates` and
  `dec`'s `## Updates` — explicitly out of scope for this feature, which
  proceeds with its own designed shape as planned.
- Next: Phase 0 (package scaffolding).

#### Update 2026-08-29T00:00:00Z (planning)

- Completed: Full interactive design session covering frontmatter status
  vocabulary, mandatory-vs-optional body sections, the RASCI `## Roles and Responsibilities` composite (including the `Accountable`
  single-paragraph-not-list constraint and the
  present-but-possibly-empty `Support`/`Consulted`/`Informed` shape,
  verified live against the engine), the `## Related Artifacts` 5th
  `Sops` sub-list, and the ISO8601-timestamped `## Updates` entry
  heading format/enforcement/scope. Worked example document produced and
  iterated with the user (definitions loose-list style, no bold in list
  leads). This README written as the resulting plan.
- Next: Phase 0 (package scaffolding).
- Notes: Precedent modules to copy, not re-derive: `dec/` (whole-domain
  shape, generic-dispatch-only tool surface after its own feat-22
  conversion), `gol/`+`dec/` (`RelatedArtifacts` shape), `tsk/`+`dec/`
  (`Updates`/`UpdateEntry` container shape), `dec/models/v1/body.py`'s
  `Option` (computed-fields-from-regex-heading pattern, reused for `Step`
  and `UpdateEntry`). Do not modify `models/md` or any other domain.

### Decisions Made

- **2026-08-29**: GitHub issue [#30](https://github.com/dfch/biz.dfch.SpecMgr/issues/30)
  filed with this feature's Overview as its description; folder renamed
  from `feat-0-sop` to `feat-30-sop` accordingly (user decision).
- **2026-08-29**: Closed 5-value status set `draft`/`review`/`approved`/
  `active`/`retired`, no dashes in values, default `draft`; `approved`
  and `active` kept as distinct statuses even though this system does
  not model an effective-date/rollout gap (user decision — the
  transition is a manual `set_status` call).
- **2026-08-29**: Only `Purpose` and `Procedure` are mandatory top-level
  sections; every other section is optional (user decision).
- **2026-08-29**: `## Procedure` uses structured `### Step N: {title}`
  subsections (DEC `Option` precedent), not a single free-text/list leaf
  (user decision).
- **2026-08-29**: Section order fixed as `Purpose, Scope, Definitions, Roles and Responsibilities, Safety and Precautions, Procedure, Related Artifacts, More Information, Updates` — Safety and Precautions placed
  immediately before Procedure (read warnings before acting); Updates
  always trailing-last (user decision).
- **2026-08-29**: `## Roles and Responsibilities` uses a RASCI (5-role)
  composite, not a flat "letter: name" list — chosen for consistency
  with this codebase's existing container-with-H3-children pattern
  (`RelatedArtifacts`, `ProsAndCons`), individual addressability, and
  future validation headroom (user decision, after an explicit
  pros/cons comparison of the two shapes).
- **2026-08-29**: `### Accountable` is a single mandatory `MarkdownParagraph`
  (never a bullet list) to structurally discourage multiple owners;
  `### Responsible` is a mandatory bullet list (>=1 item); `### Support`/`### Consulted`/`### Informed` are each optional and MAY be
  present with zero list items (an intentional "considered, currently
  empty" placeholder distinct from omitting the heading entirely) — user
  decision, verified feasible against the live engine before being
  accepted into the schema.
- **2026-08-29**: Both `Accountable` and `Responsible` are mandatory
  once `## Roles and Responsibilities` is present at all (strict-RACI
  "always has an owner and a doer"); `Support`/`Consulted`/`Informed`
  stay independently optional (user decision).
- **2026-08-29**: RASCI heading label is `Support` (not `Supporting`)
  (user decision).
- **2026-08-29**: `## Related Artifacts` copies GOL/DEC's 4 sub-lists
  and adds a 5th, `### Sops`, for cross-referencing related/superseding
  procedures (user decision, GOL's self-referencing `Goals` sub-list
  precedent).
- **2026-08-29**: `## Updates` entry headings use a structurally
  enforced ISO8601 timestamp format (`yyyy-MM-dd HH:mm:ss.fff±HH:mm — {title}`, milliseconds + explicit UTC offset or `Z`), scoped only to
  this section's entry headings — frontmatter `created`/`updated` keep
  the existing shared generic-tools timestamp format, unchanged (user
  decision).
- **2026-08-29**: `sop` is the first domain built with **no**
  per-domain `update_sop`/`set_status_sop` tools at all — it dispatches
  directly into the generic `update`/`set_status` tools from its
  initial build, per ADR 36905d5b (user decision, following the
  convention `AGENTS.md` already reserves for future domains).
- **2026-08-30**: The RASCI role-definitions guidance is a cross-cutting
  `specmgr://rasci` resource under `general/resources/` (REQ-011), not a
  `sop`-scoped `specmgr://sop/rasci` resource — RASCI is treated as a
  well-known external framework analogous to ISO/IEC 25010 (cross-cutting
  precedent: `specmgr://iso25010`), not as domain-coupled guidance like
  `rsk/tara`/`risk-matrix` (whose content is inseparable from RSK's own
  `## Strategy`/`## Mitigation` vocabulary). Content is split
  non-duplicatively — generic role definitions only in
  `general_rasci.md`; every `sop`-specific structural rule stays in
  `sop`'s own schema/instructions — with `sop`-domain discoverability
  handled by four explicit cross-references rather than by moving or
  copying content (user decision, after an explicit pros/cons comparison
  of sop-scoped vs. general placement).

### Related PRs / Commits

- [Issue #30](https://github.com/dfch/biz.dfch.SpecMgr/issues/30): Add
  artifact type "Standard Operating Procedure" (SOP)
- (no commits yet — implementation not started)
